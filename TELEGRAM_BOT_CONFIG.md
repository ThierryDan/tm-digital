# Configuration du Bot Telegram - TM Digital

## 🤖 Obtenir un Token Telegram

### Étape 1 : Créer un Bot avec BotFather

1. Ouvrir Telegram
2. Chercher **@BotFather** (bot officiel de Telegram)
3. Envoyer le message : `/newbot`
4. Suivre les instructions :
   - Donner un **nom** à votre bot (ex: "TM Digital Bot")
   - Donner un **username** unique (ex: "tm_digital_bot" ou "tm_digital_chatbot")

### Étape 2 : Copier le Token

BotFather vous envoie un message avec :
```
Here is your bot token:
123456789:ABCdefGHIjklMNOpqrSTUvwxYZaBCdeFghi
```

Copier la chaîne complète (après "token:") dans votre `.env` :

```env
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrSTUvwxYZaBCdeFghi
```

---

## 🎯 Configuration du Bot

### Option 1 : Polling (Simple, recommandé pour dev)

Le bot utilise **polling** par défaut, ce qui signifie qu'il demande à Telegram s'il y a des nouveaux messages. C'est plus simple à configurer mais moins efficace en production.

```python
# Dans telegram_bot.py
app.run_polling()
```

### Option 2 : Webhook (Production)

Pour la production sur Render, utilisez les webhooks. C'est plus efficace mais nécessite plus de configuration.

**Note** : Le polling fonctionne aussi sur Render!

---

## 📝 Commandes Disponibles

Les utilisateurs de votre bot peuvent utiliser ces commandes :

```
/start    - Démarrer une conversation
/help     - Afficher l'aide
/clear    - Effacer l'historique
/contact  - Afficher les informations de contact
```

---

## 🧪 Test du Bot

### 1. Localiser votre Bot sur Telegram

1. Ouvrir Telegram
2. Chercher votre bot par username (ex: @tm_digital_bot)
3. Envoyer `/start`

Vous devriez voir le message de bienvenue de TM Digital! 🎉

### 2. Tester une Conversation

- Envoyer un message simple comme "Bonjour"
- Le bot devrait répondre avec l'aide de Claude
- L'historique est conservé pour la conversation

### 3. Vérifier les Logs

Lors du test, vérifier les logs Render :
- Dashboard Render → Logs
- Vous devriez voir :
  ```
  🤖 Démarrage du bot Telegram...
  ✓ Bot Telegram en ligne!
  📨 Message from [nom]: [message]
  ✓ Reply sent to [nom]
  ```

---

## 📊 Configuration Avancée

### Personnaliser les Réponses

Éditer `telegram_bot.py` pour personnaliser :

- Messages de bienvenue (`start()`)
- Messages d'aide (`help_command()`)
- Réponses de contact (`contact_command()`)

### Changer le System Prompt

Par défaut, le bot utilise le prompt "tmdigital". Pour changer :

```python
# Dans telegram_bot.py, fonction handle_message
system=SYSTEM_PROMPTS["tmdigital"]  # Changer "tmdigital" par un autre prompt
```

### Ajouter de Nouvelles Commandes

```python
# Dans telegram_bot.py, dans run_telegram_bot()
async def ma_commande(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Réponse personnalisée")

app.add_handler(CommandHandler("macommande", ma_commande))
```

---

## 🚀 Déploiement sur Render

### 1. Mettre à jour .env

```env
TELEGRAM_BOT_TOKEN=votre_vrai_token_ici
```

### 2. Redéployer

```bash
git add .
git commit -m "Add Telegram bot integration"
git push
```

Render va redéployer automatiquement.

### 3. Vérifier dans les Logs

Les logs doivent afficher :
```
🤖 Bot Telegram lancé en arrière-plan
✓ Bot Telegram en ligne!
```

---

## ⚙️ Dépannage

### "TELEGRAM_BOT_TOKEN not configured"

**Symptôme** : Le bot ne démarre pas
**Solution** :
- Vérifier que `TELEGRAM_BOT_TOKEN` est dans `.env`
- Vérifier qu'il n'est pas "YOUR_BOT_TOKEN_HERE"
- Redémarrer l'application

### Le bot ne répond pas

**Symptôme** : Aucune réponse aux messages
**Solution** :
1. Vérifier que le token est correct
2. Vérifier les logs pour les erreurs
3. S'assurer que le bot a accès à l'API Claude
4. Vérifier que `ANTHROPIC_API_KEY` est configuré

### "ImportError: telegram not found"

**Symptôme** : Erreur d'import
**Solution** :
- Installer les dépendances : `pip install -r requirements.txt`
- Ou installer manuellement : `pip install python-telegram-bot`

### Messages pas reçus

**Symptôme** : Le bot reçoit les messages mais ne répond pas
**Solution** :
1. Vérifier que `ANTHROPIC_API_KEY` est valide
2. Vérifier les limites de quota Claude
3. Vérifier les logs pour les erreurs Claude

---

## 📚 Ressources

- **BotFather** : @BotFather sur Telegram
- **Python Telegram Bot** : https://python-telegram-bot.org/
- **Telegram Bot API** : https://core.telegram.org/bots/api

---

## 🔐 Sécurité

- ✓ Le token ne doit jamais être partagé
- ✓ Utiliser des variables d'environnement
- ✓ Ne pas commiter le `.env` dans Git
- ✓ Changer régulièrement le token si compromis
