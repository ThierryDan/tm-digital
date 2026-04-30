from flask import Flask, request, jsonify, send_from_directory
import anthropic
import os
import json
import smtplib
from datetime import datetime
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv()

app = Flask(__name__, static_folder="static")

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

SYSTEM_PROMPTS = {
    "restaurant": open("prompts/restaurant.txt", encoding="utf-8").read(),
    "immobilier": open("prompts/immobilier.txt", encoding="utf-8").read(),
}

GMAIL_ADDRESS = os.environ.get("GMAIL_ADDRESS")
GMAIL_PASSWORD = os.environ.get("GMAIL_PASSWORD")

# ── Pages ──────────────────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory("static", "index.html")

@app.route("/services")
def services():
    return send_from_directory("static", "services.html")

@app.route("/demo")
def demo():
    return send_from_directory("static", "demo.html")

@app.route("/contact")
def contact_page():
    return send_from_directory("static", "contact.html")

# ── API ────────────────────────────────────────────────────────

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "")
    niche = data.get("niche", "restaurant")
    history = data.get("history", [])

    if not user_message:
        return jsonify({"error": "Message vide"}), 400

    system_prompt = SYSTEM_PROMPTS.get(niche, SYSTEM_PROMPTS["restaurant"])
    messages = history + [{"role": "user", "content": user_message}]

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=system_prompt,
        messages=messages,
    )

    reply = response.content[0].text

    return jsonify({
        "reply": reply,
        "history": messages + [{"role": "assistant", "content": reply}]
    })


def generate_response(data):
    prompt = f"""Tu es un assistant professionnel pour TMdigital, une agence spécialisée dans les chatbots IA sur mesure.

Un prospect vient de soumettre une demande de contact. Génère une réponse personnalisée, chaleureuse et professionnelle en français.

INFOS DU PROSPECT:
- Nom: {data.get('nom')}
- Email: {data.get('email')}
- Secteur: {data.get('secteur')}
- Budget envisagé: {data.get('budget', 'Non spécifié')}
- Message: {data.get('message')}

Instructions:
1. Commence par remercier le prospect
2. Montre que tu as bien compris son besoin (mentionne son secteur/activité)
3. Explique brièvement comment TMdigital peut l'aider
4. Propose une prochaine étape (appel gratuit de 30 min)
5. Sois chaleureux mais professionnel
6. Signe avec le nom d'une personne (par exemple: "Marc" ou "Isabelle")

Réponds directement sans préambule."""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
    except Exception as e:
        print(f"Erreur Claude API: {e}")
        return None


def send_email_to_client(data, response):
    try:
        msg = MIMEMultipart()
        msg["From"] = GMAIL_ADDRESS
        msg["To"] = data.get('email')
        msg["Subject"] = "TMdigital — Merci pour votre demande 🎯"

        body = f"""{response}

---

À bientôt,
L'équipe TMdigital
+32 465 74 10 25
https://tmdigital.be
"""
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_ADDRESS, GMAIL_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Erreur envoi email client: {e}")
        return False


def send_email_to_admin(data, response):
    try:
        msg = MIMEMultipart()
        msg["From"] = GMAIL_ADDRESS
        msg["To"] = GMAIL_ADDRESS
        msg["Subject"] = f"NOUVEAU CONTACT: {data.get('nom')} — {data.get('secteur')}"

        body = f"""
NOUVEAU MESSAGE DE CONTACT:

NOM: {data.get('nom')}
EMAIL: {data.get('email')}
ENTREPRISE: {data.get('entreprise', 'Non fourni')}
SECTEUR: {data.get('secteur')}
BUDGET: {data.get('budget', 'Non spécifié')}

MESSAGE DU CLIENT:
{data.get('message')}

---

RÉPONSE ENVOYÉE AU CLIENT:
{response}

---
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_ADDRESS, GMAIL_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Erreur envoi email admin: {e}")
        return False


@app.route("/contact", methods=["POST"])
def contact_submit():
    data = request.json
    required = ["nom", "email", "message", "secteur"]
    if not all(data.get(k, "").strip() for k in required):
        return jsonify({"error": "Champs obligatoires manquants"}), 400

    entry = {
        "date": datetime.now().isoformat(),
        "nom": data.get("nom", "").strip(),
        "email": data.get("email", "").strip(),
        "entreprise": data.get("entreprise", "").strip(),
        "secteur": data.get("secteur", "").strip(),
        "budget": data.get("budget", "").strip(),
        "message": data.get("message", "").strip(),
    }

    contacts_file = "contacts.json"
    contacts = []
    if os.path.exists(contacts_file):
        try:
            with open(contacts_file, encoding="utf-8") as f:
                contacts = json.load(f)
        except (json.JSONDecodeError, IOError):
            contacts = []

    contacts.append(entry)
    with open(contacts_file, "w", encoding="utf-8") as f:
        json.dump(contacts, f, ensure_ascii=False, indent=2)

    response = generate_response(entry)
    if response:
        send_email_to_client(entry, response)
        send_email_to_admin(entry, response)

    return jsonify({"success": True})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
