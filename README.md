# 🤖 Chatbot IA sur mesure — Restaurant & Immobilier

## Structure du projet
```
chatbot/
├── app.py                  ← Backend Python (Flask + API Claude)
├── requirements.txt        ← Dépendances Python
├── prompts/
│   ├── restaurant.txt      ← System prompt Restaurant (à personnaliser)
│   └── immobilier.txt      ← System prompt Immobilier (à personnaliser)
└── static/
    └── index.html          ← Interface de chat (frontend)
```

---

## 🚀 Lancer en local (test sur ton PC)

### 1. Installer Python
Télécharge Python 3.11+ sur https://python.org

### 2. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 3. Ajouter ta clé API Claude
Sur Windows (PowerShell) :
```powershell
$env:ANTHROPIC_API_KEY = "sk-ant-XXXXXXXXXXXXXXXX"
```
Sur Mac/Linux :
```bash
export ANTHROPIC_API_KEY="sk-ant-XXXXXXXXXXXXXXXX"
```
Obtiens ta clé sur : https://console.anthropic.com

### 4. Lancer le serveur
```bash
python app.py
```

### 5. Ouvrir dans le navigateur
Aller sur : http://localhost:5000

---

## ✏️ Personnaliser pour un client

1. Ouvre `prompts/restaurant.txt` ou `prompts/immobilier.txt`
2. Remplace tous les `[CROCHETS]` par les vraies infos du client
3. Relance le serveur → le bot est mis à jour

---

## ☁️ Déployer en ligne (Render — gratuit)

### 1. Crée un compte sur https://render.com

### 2. Crée un repo GitHub avec ces fichiers

### 3. Sur Render :
- New → Web Service
- Connecte ton repo GitHub
- **Build Command** : `pip install -r requirements.txt`
- **Start Command** : `gunicorn app:app`
- **Environment Variables** : ajoute `ANTHROPIC_API_KEY` = ta clé

### 4. Ajoute gunicorn au requirements.txt :
```
flask==3.0.3
anthropic==0.40.0
gunicorn==22.0.0
```

### 5. Deploy → tu as une URL publique en 5 minutes !

---

## 💡 Intégrer sur le site d'un client

Ajoute ce code dans le HTML du site client pour afficher
le chat en bas à droite (widget flottant) :

```html
<!-- Chatbot IA -->
<iframe 
  src="https://TON-URL-RENDER.onrender.com"
  style="position:fixed;bottom:20px;right:20px;width:400px;height:580px;
         border:none;border-radius:16px;box-shadow:0 8px 32px rgba(0,0,0,0.15);z-index:9999"
></iframe>
```

---

## 💶 Modèle de prix suggéré
- Installation : 800 € (personnalisation + déploiement + formation)
- Maintenance : 150–200 €/mois (hébergement + mises à jour)
