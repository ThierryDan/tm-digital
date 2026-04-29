# 🚀 Guide de déploiement TMdigital sur Render

## Prérequis

- Compte GitHub avec le code du projet
- Compte Render (gratuit sur https://render.com)
- Clé API Anthropic
- Identifiants Gmail (email + mot de passe d'application)

## Étapes de déploiement

### 1. Préparer le repo GitHub

```bash
# Initialiser git (si pas déjà fait)
git init
git add .
git commit -m "Initial commit: TMdigital chatbot website"
git remote add origin https://github.com/ton-username/tmdigital.git
git push -u origin main
```

### 2. Sur Render.com

#### Option A: Déploiement rapide via Procfile

1. Va sur https://dashboard.render.com
2. Clique **"New"** → **"Web Service"**
3. Connecte ton repo GitHub
4. Configure:
   - **Name:** `tmdigital`
   - **Environment:** `Python 3.11`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Plan:** Free (gratuit)

#### Option B: Via render.yaml (recommandé)

1. Render détecte automatiquement `render.yaml`
2. Clique **"Deploy"**

### 3. Variables d'environnement

Dans Render dashboard, ajoute les **Environment Variables**:

```
ANTHROPIC_API_KEY = sk-ant-XXXXXXXXXXXXX
GMAIL_ADDRESS = thierrym369@gmail.com
GMAIL_PASSWORD = xqst xlyc rekx eapo
```

⚠️ **Sécurité:** Ces variables sont chiffrées dans Render

### 4. Déploiement automatique

- Chaque push sur `main` redéploie automatiquement
- Logs visibles en temps réel sur Render dashboard

## URL publique

Après déploiement:
- Site: `https://tmdigital.onrender.com`
- API Chat: `https://tmdigital.onrender.com/chat`
- API Contact: `https://tmdigital.onrender.com/contact`

## Dépannage

### Erreur "Module not found"
→ Vérifier `requirements.txt` contient toutes les dépendances

### Erreur Gmail SMTP
→ Vérifier les credentials dans Environment Variables

### Site slow/timeout
→ Plan Free Render a une limite. Upgrade vers "Starter" si nécessaire

## Mise à jour du code

```bash
git add .
git commit -m "Fix: amélioration X"
git push origin main
```

Render redéploiera automatiquement! 🎉

## Coûts

- **Plan Free:** Gratuit, peut "sleep" après 15 min d'inactivité
- **Plan Starter:** $7/mois, performance garantie

## Support

- Render docs: https://render.com/docs
- Issues: GitHub Issues
- Email: support@tmdigital.be
