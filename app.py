from flask import Flask, request, jsonify, send_from_directory
import anthropic
import os
import json
import smtplib
import requests
import re
import hmac
import hashlib
import threading
from datetime import datetime, timedelta
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

GMAIL_ADDRESS = os.environ.get("GMAIL_EMAIL")
GMAIL_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD")

print(f"[DEBUG] GMAIL_ADDRESS configuré: {bool(GMAIL_ADDRESS)}", flush=True)
print(f"[DEBUG] GMAIL_PASSWORD configuré: {bool(GMAIL_PASSWORD)}", flush=True)

FACEBOOK_PAGE_ACCESS_TOKEN = os.environ.get("FACEBOOK_PAGE_ACCESS_TOKEN")
FACEBOOK_PAGE_ID = os.environ.get("FACEBOOK_PAGE_ID")
FACEBOOK_VERIFY_TOKEN = os.environ.get("FACEBOOK_VERIFY_TOKEN")
FACEBOOK_APP_SECRET = os.environ.get("FACEBOOK_APP_SECRET")

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

@app.route("/privacy")
def privacy():
    return send_from_directory("static", "privacy.html")

@app.route("/terms")
def terms():
    return send_from_directory("static", "terms.html")

@app.route("/delete-data")
def delete_data():
    return send_from_directory("static", "delete-data.html")

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


def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email.strip()))


def escape_prompt_injection(text):
    if not text or not isinstance(text, str):
        return ""
    return text.replace("}", "}}").replace("{", "{{").replace('"', '\\"')


def generate_response(data):
    nom = escape_prompt_injection(data.get('nom', ''))
    email = escape_prompt_injection(data.get('email', ''))
    secteur = escape_prompt_injection(data.get('secteur', ''))
    budget = escape_prompt_injection(data.get('budget', 'Non spécifié'))
    message = escape_prompt_injection(data.get('message', ''))

    prompt = f"""Tu es un assistant professionnel pour TMdigital, une agence spécialisée dans les chatbots IA sur mesure.

Un prospect vient de soumettre une demande de contact. Génère une réponse personnalisée, chaleureuse et professionnelle en français.

INFOS DU PROSPECT:
- Nom: {nom}
- Email: {email}
- Secteur: {secteur}
- Budget envisagé: {budget}
- Message: {message}

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
        print(f"[EMAIL] Tentative d'envoi au client {data.get('email')}", flush=True)

        if not GMAIL_ADDRESS or not GMAIL_PASSWORD:
            print(f"[EMAIL] ❌ Credentials manquantes: ADDRESS={bool(GMAIL_ADDRESS)}, PASSWORD={bool(GMAIL_PASSWORD)}", flush=True)
            return False

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

        print(f"[EMAIL] Connexion à smtp.gmail.com:587 (TLS)...", flush=True)
        server = smtplib.SMTP("smtp.gmail.com", 587, timeout=15)
        print(f"[EMAIL] ✓ Connexion établie", flush=True)

        server.starttls()
        print(f"[EMAIL] ✓ TLS activé", flush=True)

        print(f"[EMAIL] Authentification avec {GMAIL_ADDRESS}...", flush=True)
        server.login(GMAIL_ADDRESS, GMAIL_PASSWORD)
        print(f"[EMAIL] ✓ Authentification réussie", flush=True)

        server.send_message(msg)
        server.quit()
        print(f"[EMAIL] ✓ Email envoyé avec succès à {data.get('email')}", flush=True)
        return True
    except smtplib.SMTPAuthenticationError as e:
        print(f"[EMAIL] ❌ Erreur d'authentification: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return False
    except smtplib.SMTPException as e:
        print(f"[EMAIL] ❌ Erreur SMTP: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"[EMAIL] ❌ Erreur générale: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return False


def send_reservation_email_client(reservation):
    try:
        print(f"[RESERVATION-CLIENT] Envoi confirmation à {reservation.get('email')}", flush=True)

        if not GMAIL_ADDRESS or not GMAIL_PASSWORD:
            print(f"[RESERVATION-CLIENT] ❌ Credentials manquantes", flush=True)
            return False

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

        print(f"[RESERVATION-CLIENT] Connexion SMTP:587...", flush=True)
        server = smtplib.SMTP("smtp.gmail.com", 587, timeout=15)
        server.starttls()
        server.login(GMAIL_ADDRESS, GMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"[RESERVATION-CLIENT] ✓ Email envoyé", flush=True)
        return True
    except smtplib.SMTPAuthenticationError as e:
        print(f"[RESERVATION-CLIENT] ❌ Erreur d'authentification: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"[RESERVATION-CLIENT] ❌ Erreur: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return False


def send_reservation_email_admin(reservation):
    try:
        print(f"[RESERVATION-ADMIN] Envoi notification au propriétaire", flush=True)

        if not GMAIL_ADDRESS or not GMAIL_PASSWORD:
            print(f"[RESERVATION-ADMIN] ❌ Credentials manquantes", flush=True)
            return False

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

        print(f"[RESERVATION-ADMIN] Connexion SMTP:587...", flush=True)
        server = smtplib.SMTP("smtp.gmail.com", 587, timeout=15)
        server.starttls()
        server.login(GMAIL_ADDRESS, GMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"[RESERVATION-ADMIN] ✓ Email admin envoyé", flush=True)
        return True
    except smtplib.SMTPAuthenticationError as e:
        print(f"[RESERVATION-ADMIN] ❌ Erreur d'authentification: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"[RESERVATION-ADMIN] ❌ Erreur: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return False


def send_facebook_message(recipient_id, message_text):
    try:
        url = f"https://graph.facebook.com/v18.0/me/messages"
        payload = {
            "recipient": {"id": recipient_id},
            "message": {"text": message_text}
        }
        headers = {"Content-Type": "application/json"}
        params = {"access_token": FACEBOOK_PAGE_ACCESS_TOKEN}

        response = requests.post(url, json=payload, headers=headers, params=params)
        print(f"Facebook API response: {response.status_code}")
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
        print(f"[EMAIL-ADMIN] Envoi au propriétaire ({GMAIL_ADDRESS})...", flush=True)

        if not GMAIL_ADDRESS or not GMAIL_PASSWORD:
            print(f"[EMAIL-ADMIN] ❌ Credentials manquantes", flush=True)
            return False

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

        print(f"[EMAIL-ADMIN] Connexion SMTP:587...", flush=True)
        server = smtplib.SMTP("smtp.gmail.com", 587, timeout=15)
        server.starttls()
        server.login(GMAIL_ADDRESS, GMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"[EMAIL-ADMIN] ✓ Email admin envoyé", flush=True)
        return True
    except smtplib.SMTPAuthenticationError as e:
        print(f"[EMAIL-ADMIN] ❌ Erreur d'authentification: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"[EMAIL-ADMIN] ❌ Erreur: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return False


@app.route("/contact", methods=["POST"])
def contact_submit():
    print(f"\n[CONTACT] Nouvelle demande de contact reçue", flush=True)
    data = request.json
    print(f"[CONTACT] Données: nom={data.get('nom')}, email={data.get('email')}, secteur={data.get('secteur')}", flush=True)

    required = ["nom", "email", "message", "secteur"]
    if not all(data.get(k, "").strip() for k in required):
        print(f"[CONTACT] ❌ Champs manquants", flush=True)
        return jsonify({"error": "Champs obligatoires manquants"}), 400

    if not is_valid_email(data.get("email", "")):
        print(f"[CONTACT] ❌ Email invalide: {data.get('email')}", flush=True)
        return jsonify({"error": "Email invalide"}), 400

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

    print(f"[CONTACT] Génération de réponse Claude...", flush=True)
    response = generate_response(entry)

    if response:
        print(f"[CONTACT] ✓ Réponse Claude générée, envoi des emails...", flush=True)
        client_sent = send_email_to_client(entry, response)
        admin_sent = send_email_to_admin(entry, response)
        print(f"[CONTACT] Email client: {'✓' if client_sent else '❌'}, Email admin: {'✓' if admin_sent else '❌'}", flush=True)
    else:
        print(f"[CONTACT] ❌ Échec génération réponse Claude", flush=True)

    print(f"[CONTACT] Fin du traitement\n", flush=True)
    return jsonify({"success": True})


@app.route("/reservation", methods=["POST"])
def reservation_submit():
    data = request.json
    required = ["nom", "email", "date", "heure", "personnes"]
    if not all(data.get(k, "").strip() for k in required):
        return jsonify({"error": "Données de réservation incomplètes"}), 400

    if not is_valid_email(data.get("email", "")):
        return jsonify({"error": "Email invalide"}), 400

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


@app.route("/delete-data-request", methods=["POST"])
def delete_data_request():
    data = request.json
    required = ["email", "fullname"]
    if not all(data.get(k, "").strip() for k in required):
        return jsonify({"error": "Email et Nom obligatoires"}), 400

    if not is_valid_email(data.get("email", "")):
        return jsonify({"error": "Email invalide"}), 400

    delete_request = {
        "date_request": datetime.now().isoformat(),
        "email": data.get("email", "").strip(),
        "fullname": data.get("fullname", "").strip(),
        "reason": data.get("reason", "").strip(),
    }

    delete_requests_file = "delete_requests.json"
    delete_requests = []
    if os.path.exists(delete_requests_file):
        try:
            with open(delete_requests_file, encoding="utf-8") as f:
                delete_requests = json.load(f)
        except (json.JSONDecodeError, IOError):
            delete_requests = []

    delete_requests.append(delete_request)
    with open(delete_requests_file, "w", encoding="utf-8") as f:
        json.dump(delete_requests, f, ensure_ascii=False, indent=2)

    try:
        msg = MIMEMultipart()
        msg["From"] = GMAIL_ADDRESS
        msg["To"] = GMAIL_ADDRESS
        msg["Subject"] = f"🔔 DEMANDE DE SUPPRESSION DE DONNÉES: {data.get('fullname')}"

        body = f"""
NOUVELLE DEMANDE DE SUPPRESSION DE DONNÉES:

NOM: {data.get('fullname')}
EMAIL: {data.get('email')}
RAISON: {data.get('reason', 'Non spécifiée')}

---
Date de réception: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
À traiter avant: {(datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')}
"""
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_ADDRESS, GMAIL_PASSWORD)
            server.send_message(msg)
    except Exception as e:
        print(f"Erreur envoi email suppression: {e}")

    return jsonify({"success": True, "message": "Demande reçue. Traitement dans 30 jours."})


# ── Facebook Webhook ────────────────────────────────────────

def verify_facebook_signature(request_body, signature):
    if not FACEBOOK_APP_SECRET or FACEBOOK_APP_SECRET == "YOUR_APP_SECRET_HERE":
        print("⚠️  WARNING: FACEBOOK_APP_SECRET not configured - webhook signature validation will fail!")
        print("Please set FACEBOOK_APP_SECRET in .env with your app's secret from Facebook Developer Console")
        return False

    expected_sig = hmac.new(
        FACEBOOK_APP_SECRET.encode(),
        request_body,
        hashlib.sha256
    ).hexdigest()

    is_valid = hmac.compare_digest(signature, expected_sig)
    if not is_valid:
        print(f"❌ Invalid Facebook signature. Expected: {expected_sig[:16]}..., Got: {signature[:16]}...")
    else:
        print("✓ Valid Facebook signature")
    return is_valid


@app.route("/webhook", methods=["GET"])
def webhook_verify():
    verify_token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if verify_token == FACEBOOK_VERIFY_TOKEN:
        print("✓ Webhook verification successful")
        return challenge
    print(f"❌ Invalid verify token. Expected: {FACEBOOK_VERIFY_TOKEN}, Got: {verify_token}")
    return "Invalid verify token", 403


@app.route("/webhook", methods=["POST"])
def webhook_handle():
    print(f"📨 Webhook POST received from {request.remote_addr}")

    signature = request.headers.get("X-Hub-Signature-256", "").split("sha256=")[-1]

    if not signature:
        print("⚠️  No signature found in request headers")
        return "No signature", 403

    if not verify_facebook_signature(request.get_data(), signature):
        print("Invalid Facebook signature")
        return "Invalid signature", 403

    try:
        data = request.json

        if data.get("object") != "page":
            print(f"⚠️  Webhook for object '{data.get('object')}', ignoring (expecting 'page')")
            return "ok", 200

        entry = data.get("entry", [{}])[0]
        messaging = entry.get("messaging", [])
        print(f"📋 Processing {len(messaging)} messages")

        for msg in messaging:
            sender_id = msg.get("sender", {}).get("id")
            recipient_id = msg.get("recipient", {}).get("id")
            message_data = msg.get("message", {})
            user_message = message_data.get("text")

            print(f"Message from {sender_id}: {user_message[:50] if user_message else 'No text'}")

            if sender_id and user_message:
                reply = get_facebook_response(sender_id, user_message)
                success = send_facebook_message(sender_id, reply)
                print(f"Reply sent: {success}")
            else:
                print(f"⚠️  Skipped message - sender_id: {sender_id}, has text: {bool(user_message)}")

    except Exception as e:
        print(f"❌ Erreur webhook Facebook: {e}")
        import traceback
        traceback.print_exc()

    return "ok", 200


def start_telegram_bot():
    """Lancer le bot Telegram dans un thread séparé"""
    try:
        from telegram_bot import run_telegram_bot
        print("🤖 Démarrage du bot Telegram en thread...", flush=True)
        run_telegram_bot()
    except ImportError as e:
        print(f"⚠️  Erreur import telegram_bot: {e}", flush=True)
    except Exception as e:
        print(f"❌ Erreur démarrage bot Telegram: {e}", flush=True)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    telegram_bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")

    # Démarrer le bot Telegram dans un thread si le token est configuré
    if telegram_bot_token and telegram_bot_token != "YOUR_BOT_TOKEN_HERE":
        telegram_thread = threading.Thread(target=start_telegram_bot, daemon=True)
        telegram_thread.start()
        print("🤖 Bot Telegram lancé en arrière-plan", flush=True)
    else:
        print("⚠️  TELEGRAM_BOT_TOKEN not configured, Telegram integration disabled", flush=True)

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
