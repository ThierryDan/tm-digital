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

def load_email_config():
    """Charger la configuration email depuis les variables d'environnement"""
    return (
        os.environ.get("GMAIL_EMAIL"),
        os.environ.get("GMAIL_APP_PASSWORD"),
        os.environ.get("ADMIN_EMAIL")
    )

GMAIL_ADDRESS, GMAIL_PASSWORD, ADMIN_EMAIL = load_email_config()

print(f"[DEBUG] GMAIL_ADDRESS (envoi): {bool(GMAIL_ADDRESS)}", flush=True)
print(f"[DEBUG] GMAIL_PASSWORD configuré: {bool(GMAIL_PASSWORD)}", flush=True)
print(f"[DEBUG] ADMIN_EMAIL (réception): {ADMIN_EMAIL if ADMIN_EMAIL else 'Non configuré'}", flush=True)

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


@app.route("/api/chat", methods=["POST"])
def api_chat():
    """API pour le chat widget sur le site"""
    data = request.json
    user_message = data.get("message", "")
    niche = data.get("niche", "tmdigital")

    if not user_message:
        return jsonify({"error": "Message vide"}), 400

    try:
        system_prompt = SYSTEM_PROMPTS.get(niche, SYSTEM_PROMPTS["tmdigital"])

        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )

        reply = response.content[0].text
        return jsonify({"reply": reply})
    except Exception as e:
        print(f"[API-CHAT] Erreur: {e}", flush=True)
        return jsonify({"error": str(e)}), 500


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
        print(f"[EMAIL-CLIENT] Tentative d'envoi au client {data.get('email')}", flush=True)

        if not GMAIL_ADDRESS or not GMAIL_PASSWORD:
            print(f"[EMAIL-CLIENT] ❌ Credentials manquantes", flush=True)
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

        print(f"[EMAIL-CLIENT] Connexion SMTP_SSL:465...", flush=True)
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=15)
        print(f"[EMAIL-CLIENT] ✓ Connexion SSL établie", flush=True)

        print(f"[EMAIL-CLIENT] Authentification...", flush=True)
        server.login(GMAIL_ADDRESS, GMAIL_PASSWORD)
        print(f"[EMAIL-CLIENT] ✓ Authentification réussie", flush=True)

        server.send_message(msg)
        server.quit()
        print(f"[EMAIL-CLIENT] ✓ Email envoyé avec succès", flush=True)
        return True
    except Exception as e:
        print(f"[EMAIL-CLIENT] ❌ Erreur: {e}", flush=True)
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
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=15)
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
        msg["To"] = ADMIN_EMAIL
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
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=15)
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
        print(f"[EMAIL-ADMIN] Envoi à l'admin ({ADMIN_EMAIL})...", flush=True)

        if not GMAIL_ADDRESS or not GMAIL_PASSWORD:
            print(f"[EMAIL-ADMIN] ❌ Credentials manquantes", flush=True)
            return False

        msg = MIMEMultipart()
        msg["From"] = GMAIL_ADDRESS
        msg["To"] = ADMIN_EMAIL
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

        print(f"[EMAIL-ADMIN] Connexion SMTP_SSL:465...", flush=True)
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=15)
        print(f"[EMAIL-ADMIN] ✓ Connexion SSL établie", flush=True)

        print(f"[EMAIL-ADMIN] Authentification...", flush=True)
        server.login(GMAIL_ADDRESS, GMAIL_PASSWORD)
        print(f"[EMAIL-ADMIN] ✓ Authentification réussie", flush=True)

        server.send_message(msg)
        server.quit()
        print(f"[EMAIL-ADMIN] ✓ Email admin envoyé", flush=True)
        return True
    except Exception as e:
        print(f"[EMAIL-ADMIN] ❌ Erreur: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return False


@app.route("/setup-brevo", methods=["POST"])
def setup_brevo():
    """Endpoint pour configurer Brevo (persistant)"""
    data = request.json
    global SENDER_EMAIL, BREVO_API_KEY, ADMIN_EMAIL

    sender_email = data.get("sender_email", "").strip()
    brevo_api_key = data.get("brevo_api_key", "").strip()
    admin_email = data.get("admin_email", "").strip()

    if not all([sender_email, brevo_api_key, admin_email]):
        return jsonify({
            "success": False,
            "error": "Toutes les variables sont obligatoires",
            "required": ["sender_email", "brevo_api_key", "admin_email"]
        }), 400

    # Sauvegarder dans un fichier JSON (persistant)
    config_file = "email_config.json"
    config = {
        "sender_email": sender_email,
        "brevo_api_key": brevo_api_key,
        "admin_email": admin_email
    }

    try:
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        print(f"[SETUP-BREVO] Configuration sauvegardée dans {config_file}", flush=True)
    except IOError as e:
        print(f"[SETUP-BREVO] ❌ Erreur sauvegarde: {e}", flush=True)
        return jsonify({
            "success": False,
            "error": f"Erreur sauvegarde config: {e}"
        }), 500

    # Aussi configurer les variables globales pour la session courante
    SENDER_EMAIL = sender_email
    BREVO_API_KEY = brevo_api_key
    ADMIN_EMAIL = admin_email

    print(f"[SETUP-BREVO] Configuration Brevo mise à jour", flush=True)
    print(f"[SETUP-BREVO] SENDER_EMAIL: {sender_email}", flush=True)
    print(f"[SETUP-BREVO] ADMIN_EMAIL: {admin_email}", flush=True)

    return jsonify({
        "success": True,
        "message": "Configuration Brevo sauvegardée et appliquée",
        "sender_email": sender_email,
        "admin_email": admin_email,
        "api_key_length": len(brevo_api_key),
        "file": config_file
    })


@app.route("/diagnostic", methods=["GET"])
def diagnostic():
    """Endpoint pour diagnostiquer la configuration Gmail SMTP"""
    return jsonify({
        "status": "Configuration Email (Gmail SMTP)",
        "GMAIL_EMAIL": "✓ Configuré" if GMAIL_ADDRESS else "❌ MANQUANT",
        "GMAIL_APP_PASSWORD": "✓ Configuré" if GMAIL_PASSWORD else "❌ MANQUANT",
        "ADMIN_EMAIL": f"✓ {ADMIN_EMAIL}" if ADMIN_EMAIL else "❌ MANQUANT",
        "ready_to_send": bool(GMAIL_ADDRESS and GMAIL_PASSWORD and ADMIN_EMAIL),
        "instructions": "Configure les variables d'environnement GMAIL_EMAIL, GMAIL_APP_PASSWORD, ADMIN_EMAIL"
    })


@app.route("/debug-contacts", methods=["GET"])
def debug_contacts():
    """Voir les derniers contacts et vérifier l'envoi d'email"""
    contacts_file = "contacts.json"
    if not os.path.exists(contacts_file):
        return jsonify({"error": "Aucun fichier contacts"}), 404

    try:
        with open(contacts_file, encoding="utf-8") as f:
            contacts = json.load(f)

        # Tester l'envoi d'email sur le dernier contact
        if contacts:
            last = contacts[-1]
            print(f"\n[DEBUG] Test envoi email pour: {last.get('email')}", flush=True)

            test_response = f"Email de test pour {last.get('nom')}"

            print(f"[DEBUG] Tentative send_email_to_client...", flush=True)
            client_result = send_email_to_client(last, test_response)
            print(f"[DEBUG] Résultat client: {client_result}", flush=True)

            print(f"[DEBUG] Tentative send_email_to_admin...", flush=True)
            admin_result = send_email_to_admin(last, test_response)
            print(f"[DEBUG] Résultat admin: {admin_result}", flush=True)

            return jsonify({
                "contacts_count": len(contacts),
                "last_contact": last,
                "email_test": {
                    "to_client": client_result,
                    "to_admin": admin_result,
                    "gmail_address": bool(GMAIL_ADDRESS),
                    "gmail_password": bool(GMAIL_PASSWORD),
                    "admin_email": ADMIN_EMAIL
                }
            })
        else:
            return jsonify({"error": "Aucun contact"}), 404
    except Exception as e:
        import traceback
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500


@app.route("/test-email", methods=["GET"])
def test_email():
    """Endpoint pour tester l'envoi d'email"""
    print(f"\n[TEST-EMAIL] Test d'envoi d'email lancé", flush=True)
    print(f"[TEST-EMAIL] GMAIL_ADDRESS: {GMAIL_ADDRESS}", flush=True)
    print(f"[TEST-EMAIL] ADMIN_EMAIL: {ADMIN_EMAIL}", flush=True)
    print(f"[TEST-EMAIL] GMAIL_PASSWORD configuré: {bool(GMAIL_PASSWORD)}", flush=True)

    if not GMAIL_ADDRESS or not GMAIL_PASSWORD:
        return jsonify({
            "success": False,
            "error": "Credentials Gmail manquantes",
            "details": f"GMAIL_ADDRESS={bool(GMAIL_ADDRESS)}, GMAIL_PASSWORD={bool(GMAIL_PASSWORD)}"
        }), 400

    try:
        print(f"[TEST-EMAIL] Connexion à smtp.gmail.com:587...", flush=True)
        server = smtplib.SMTP("smtp.gmail.com", 587, timeout=15)
        print(f"[TEST-EMAIL] ✓ Connexion établie", flush=True)

        server.starttls()
        print(f"[TEST-EMAIL] ✓ TLS activé", flush=True)

        print(f"[TEST-EMAIL] Authentification avec {GMAIL_ADDRESS}...", flush=True)
        server.login(GMAIL_ADDRESS, GMAIL_PASSWORD)
        print(f"[TEST-EMAIL] ✓ Authentification réussie", flush=True)

        msg = MIMEMultipart()
        msg["From"] = GMAIL_ADDRESS
        msg["To"] = ADMIN_EMAIL
        msg["Subject"] = "🧪 TEST EMAIL - TM Digital"
        body = f"""Test d'envoi réussi!

GMAIL_ADDRESS (envoi): {GMAIL_ADDRESS}
ADMIN_EMAIL (réception): {ADMIN_EMAIL}
Heure du test: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Si tu reçois ce message, la configuration est correcte!
"""
        msg.attach(MIMEText(body, "plain"))

        server.send_message(msg)
        server.quit()
        print(f"[TEST-EMAIL] ✓ Email test envoyé avec succès", flush=True)

        return jsonify({
            "success": True,
            "message": "Email test envoyé",
            "from": GMAIL_ADDRESS,
            "to": ADMIN_EMAIL
        })
    except smtplib.SMTPAuthenticationError as e:
        error_msg = f"❌ Erreur d'authentification Gmail: {str(e)}"
        print(f"[TEST-EMAIL] {error_msg}", flush=True)
        return jsonify({"success": False, "error": error_msg}), 401
    except smtplib.SMTPException as e:
        error_msg = f"❌ Erreur SMTP: {str(e)}"
        print(f"[TEST-EMAIL] {error_msg}", flush=True)
        return jsonify({"success": False, "error": error_msg}), 500
    except Exception as e:
        error_msg = f"❌ Erreur: {str(e)}"
        print(f"[TEST-EMAIL] {error_msg}", flush=True)
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": error_msg}), 500


@app.route("/contacts", methods=["GET"])
def get_contacts():
    """Endpoint pour voir tous les contacts reçus"""
    contacts_file = "contacts.json"
    if not os.path.exists(contacts_file):
        return jsonify({"contacts": [], "count": 0})

    try:
        with open(contacts_file, encoding="utf-8") as f:
            contacts = json.load(f)
        return jsonify({"contacts": contacts, "count": len(contacts)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


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
    response = None
    try:
        response = generate_response(entry)
        if response:
            print(f"[CONTACT] ✓ Réponse Claude: {response[:80]}...", flush=True)
        else:
            print(f"[CONTACT] ⚠️ Claude retourna None", flush=True)
    except Exception as e:
        print(f"[CONTACT] ⚠️ Erreur Claude (continuant quand même): {e}", flush=True)

    # Envoyer les emails même si Claude échoue
    if response:
        print(f"[CONTACT] Envoi des emails avec réponse Claude...", flush=True)
    else:
        print(f"[CONTACT] Envoi des emails sans réponse Claude (fallback)...", flush=True)
        response = f"Merci {entry.get('nom')} pour votre message.\n\nNous avons bien reçu votre demande et vous répondrons dans les 24 heures ouvrables.\n\nCordialement,\nL'équipe TM Digital"

    client_sent = send_email_to_client(entry, response)
    admin_sent = send_email_to_admin(entry, response)
    print(f"[CONTACT] Emails: client={'✓' if client_sent else '❌'}, admin={'✓' if admin_sent else '❌'}", flush=True)

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
        msg["To"] = ADMIN_EMAIL
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

@app.route("/run-telegram-bot", methods=["POST", "GET"])
def run_telegram_bot_endpoint():
    """Endpoint pour lancer le bot Telegram manuellement"""
    telegram_token = os.environ.get("TELEGRAM_BOT_TOKEN")

    if not telegram_token or telegram_token == "YOUR_BOT_TOKEN_HERE":
        return jsonify({"error": "TELEGRAM_BOT_TOKEN not configured"}), 400

    try:
        print("🤖 Lancement du bot Telegram via endpoint...", flush=True)
        # Lancer le bot dans un thread séparé
        telegram_thread = threading.Thread(target=start_telegram_bot, daemon=True)
        telegram_thread.start()
        return jsonify({"success": True, "message": "Bot Telegram lancé en arrière-plan"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Lancer le bot Telegram automatiquement au démarrage en arrière-plan
def start_telegram_bot_bg():
    """Lancer le bot Telegram en arrière-plan au démarrage"""
    telegram_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if telegram_token and telegram_token != "YOUR_BOT_TOKEN_HERE":
        try:
            print("🤖 Démarrage du bot Telegram en arrière-plan...", flush=True)
            telegram_thread = threading.Thread(target=start_telegram_bot, daemon=True)
            telegram_thread.start()
            print("✓ Bot Telegram lancé", flush=True)
        except Exception as e:
            print(f"⚠️  Erreur démarrage bot Telegram: {e}", flush=True)


if __name__ == "__main__":
    # Lancer le bot Telegram en arrière-plan
    start_telegram_bot_bg()

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
