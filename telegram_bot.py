import os
import asyncio
import anthropic
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

SYSTEM_PROMPTS = {
    "tmdigital": open("prompts/tmdigital.txt", encoding="utf-8").read(),
}

# Historique de conversation par utilisateur
user_conversations = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Commande /start"""
    user_id = update.effective_user.id
    user_conversations[user_id] = []

    message = """👋 Bienvenue sur TM Digital!

Je suis un assistant IA spécialisé dans les chatbots IA sur mesure.

📝 Comment puis-je vous aider?
- Vous avez des questions sur nos services?
- Vous voulez en savoir plus sur nos solutions?
- Vous envisagez un projet chatbot?

Tapez simplement votre message et je vous répondrai! 🚀"""

    await update.message.reply_text(message)
    print(f"✓ User {user_id} started conversation")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Commande /help"""
    help_text = """📚 Commandes disponibles:
/start - Démarrer une conversation
/help - Afficher l'aide
/clear - Effacer l'historique de conversation
/contact - Informations de contact

Vous pouvez aussi simplement envoyer un message pour discuter avec notre assistant IA! 💬"""

    await update.message.reply_text(help_text)

async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Commande /clear - Effacer l'historique"""
    user_id = update.effective_user.id
    user_conversations[user_id] = []
    await update.message.reply_text("✓ Historique de conversation effacé!")
    print(f"✓ Conversation cleared for user {user_id}")

async def contact_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Commande /contact"""
    contact_text = """📞 Contactez-nous:

📧 Email: contact@tmdigital.be
☎️  Téléphone: +32 465 74 10 25
🌐 Site: https://tm-digital.onrender.com
📱 Messenger: https://www.facebook.com/tmdigital

Visitez notre formulaire de contact pour une demande spécifique! 👉 https://tm-digital.onrender.com/contact"""

    await update.message.reply_text(contact_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Traiter les messages utilisateur"""
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name or "Utilisateur"
    user_message = update.message.text

    # Initialiser l'historique si nécessaire
    if user_id not in user_conversations:
        user_conversations[user_id] = []

    print(f"📨 Message from {user_name} ({user_id}): {user_message[:50]}")

    # Ajouter le message utilisateur à l'historique
    user_conversations[user_id].append({
        "role": "user",
        "content": user_message
    })

    # Afficher le statut "en train de taper..."
    await update.message.chat.send_action("typing")

    try:
        # Appeler l'API Claude
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=SYSTEM_PROMPTS["tmdigital"],
            messages=user_conversations[user_id],
        )

        reply = response.content[0].text

        # Ajouter la réponse à l'historique
        user_conversations[user_id].append({
            "role": "assistant",
            "content": reply
        })

        # Envoyer la réponse (découper si trop long)
        if len(reply) > 4096:
            # Telegram limite à 4096 caractères par message
            for i in range(0, len(reply), 4096):
                await update.message.reply_text(reply[i:i+4096])
        else:
            await update.message.reply_text(reply)

        print(f"✓ Reply sent to {user_name}")

    except Exception as e:
        error_msg = f"❌ Erreur: {str(e)}"
        print(error_msg)
        await update.message.reply_text("Désolé, j'ai rencontré une erreur technique. Veuillez réessayer.")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Gérer les erreurs"""
    print(f"Update {update} caused error {context.error}")

async def main():
    """Fonction principale asynchrone"""
    try:
        if not TELEGRAM_BOT_TOKEN or TELEGRAM_BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
            print("⚠️  WARNING: TELEGRAM_BOT_TOKEN not configured", flush=True)
            return

        print("🤖 Démarrage du bot Telegram...", flush=True)

        app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        print("✓ Application créée", flush=True)

        # Ajouter les gestionnaires de commandes
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("help", help_command))
        app.add_handler(CommandHandler("clear", clear_command))
        app.add_handler(CommandHandler("contact", contact_command))
        print("✓ Commandes ajoutées", flush=True)

        # Ajouter le gestionnaire de messages
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        print("✓ Gestionnaires ajoutés", flush=True)

        # Gestionnaire d'erreurs
        app.add_error_handler(error_handler)

        # Démarrer le bot avec polling (sans signal handlers car on est dans un thread)
        print("✓ Bot Telegram en ligne! Écoute les messages...", flush=True)
        await app.run_polling(stop_signals=())
    except Exception as e:
        print(f"❌ Erreur dans main(): {e}", flush=True)
        import traceback
        traceback.print_exc()

def run_telegram_bot():
    """Lancer le bot Telegram dans son propre event loop"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(main())
    finally:
        loop.close()

if __name__ == "__main__":
    run_telegram_bot()
