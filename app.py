from flask import Flask, request, jsonify, send_from_directory
import anthropic
import os
import json
import smtplib
import requests
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
    "tmdigital": open("prompts/tmdigital.txt", encoding="utf-8").read(),
}

GMAIL_ADDRESS = os.environ.get("GMAIL_ADDRESS")
GMAIL_PASSWORD = os.environ.get("GMAIL_PASSWORD")

FACEBOOK_PAGE_ACCESS_TOKEN = os.environ.get("FACEBOOK_PAGE_ACCESS_TOKEN")
FACEBOOK_PAGE_ID = os.environ.get("FACEBOOK_PAGE_ID")
FACEBOOK_VERIFY_TOKEN = os.environ.get("FACEBOOK_VERIFY_TOKEN")

RESERVATION_PROMPT = """Tu es le gérant d'un restaurant (Le Moderne) en ligne avec un client.

Le client veut faire une réservation. Tu dois collecter ces infos de manière naturelle et conversationnelle:
1. Son NOM (s'il ne l'a pas donné)
2. La DATE (format: JJ/MM/YYYY)
3. L'HEURE (format: HH:MM)
4. Le NOMBRE DE PERSONNES

Une fois que tu as TOUTES ces 4 infos, réponds avec le message JSON suivant (et rien d'autre):
```json
{"reservation_complete": true, "nom": "...", "date": "JJ/MM/YYYY", "heure": "HH:MM", "personnes": "N"}
```

Si une info manque, demande-la de manière naturelle et chaleureuse."""

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


def send_reservation_email_client(reservation):
    try:
        msg = MIMEMultipart()
        msg["From"] = GMAIL_ADDRESS
        msg["To"] = reservation.get('email')
        msg["Subject"] = f"Confirmation de réservation — Le Moderne 🍽️"

        body = f"""Salut {reservation.get('nom')},

Super! Votre réservation est confirmée! 🎉

📅 DATE: {reservation.get('date')}
⏰ HEURE: {reservation.get('heure')}
👥 NOMBRE DE PERSONNES: {reservation.get('personnes')}
🏪 RESTAURANT: Le Moderne

À bientôt,
L'équipe du Moderne
+32 465 74 10 25
"""
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_ADDRESS, GMAIL_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Erreur envoi email réservation client: {e}")
        return False


def send_reservation_email_admin(reservation):
    try:
        msg = MIMEMultipart()
        msg["From"] = GMAIL_ADDRESS
        msg["To"] = GMAIL_ADDRESS
        msg["Subject"] = f"🔔 NOUVELLE RÉSERVATION: {reservation.get('nom')}"

        body = f"""
NOUVELLE RÉSERVATION REÇUE:

CLIENT: {reservation.get('nom')}
EMAIL: {reservation.get('email')}
TÉLÉPHONE: {reservation.get('telephone', 'Non fourni')}

📅 DATE: {reservation.get('date')}
⏰ HEURE: {reservation.get('heure')}
👥 PERSONNES: {reservation.get('personnes')}

---
Date de réception: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_ADDRESS, GMAIL_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Erreur envoi email réservation admin: {e}")
        return False


def send_facebook_message(recipient_id, message_text):
    try:
        url = f"https://graph.instagram.com/v18.0/me/messages"
        payload = {
            "recipient": {"id": recipient_id},
            "message": {"text": message_text}
        }
        headers = {"Content-Type": "application/json"}
        params = {"access_token": FACEBOOK_PAGE_ACCESS_TOKEN}

        response = requests.post(url, json=payload, headers=headers, params=params)
        return response.status_code == 200
    except Exception as e:
        print(f"Erreur envoi message Facebook: {e}")
        return False


def get_facebook_response(user_id, user_message):
    try:
        history = [{
            "role": "user",
            "content": user_message
        }]

        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=SYSTEM_PROMPTS["tmdigital"],
            messages=history,
        )

        reply = response.content[0].text

        if "contact_request" in reply.lower():
            try:
                json_str = reply[reply.find("{"):reply.rfind("}")+1]
                contact_data = json.loads(json_str)
                print(f"Contact request: {contact_data}")
            except:
                pass

        return reply
    except Exception as e:
        print(f"Erreur Claude API Facebook: {e}")
        return "Désolé, j'ai une erreur technique. Peux-tu réessayer?"


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


@app.route("/reservation", methods=["POST"])
def reservation_submit():
    data = request.json
    required = ["nom", "email", "date", "heure", "personnes"]
    if not all(data.get(k, "").strip() for k in required):
        return jsonify({"error": "Données de réservation incomplètes"}), 400

    reservation = {
        "date_reservation": datetime.now().isoformat(),
        "nom": data.get("nom", "").strip(),
        "email": data.get("email", "").strip(),
        "telephone": data.get("telephone", "").strip(),
        "date": data.get("date", "").strip(),
        "heure": data.get("heure", "").strip(),
        "personnes": data.get("personnes", "").strip(),
    }

    reservations_file = "reservations.json"
    reservations = []
    if os.path.exists(reservations_file):
        try:
            with open(reservations_file, encoding="utf-8") as f:
                reservations = json.load(f)
        except (json.JSONDecodeError, IOError):
            reservations = []

    reservations.append(reservation)
    with open(reservations_file, "w", encoding="utf-8") as f:
        json.dump(reservations, f, ensure_ascii=False, indent=2)

    send_reservation_email_client(reservation)
    send_reservation_email_admin(reservation)

    return jsonify({"success": True, "message": "Réservation confirmée!"})


# ── Facebook Webhook ────────────────────────────────────────

@app.route("/webhook", methods=["GET"])
def webhook_verify():
    verify_token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if verify_token == FACEBOOK_VERIFY_TOKEN:
        return challenge
    return "Invalid verify token", 403


@app.route("/webhook", methods=["POST"])
def webhook_handle():
    data = request.json

    if data.get("object") != "page":
        return "ok", 200

    entry = data.get("entry", [{}])[0]
    messaging = entry.get("messaging", [])

    for msg in messaging:
        sender_id = msg.get("sender", {}).get("id")
        recipient_id = msg.get("recipient", {}).get("id")
        message_data = msg.get("message", {})
        user_message = message_data.get("text")

        if sender_id and user_message:
            reply = get_facebook_response(sender_id, user_message)
            send_facebook_message(sender_id, reply)

    return "ok", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
