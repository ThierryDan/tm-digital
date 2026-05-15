# Configuration du Webhook Facebook Messenger

## 🔧 Configuration Requise

### 1. Variables d'Environnement (.env)

Assurez-vous que votre fichier `.env` contient :

```env
FACEBOOK_PAGE_ACCESS_TOKEN=EAASXrQnL1IABRaW3fL3kLpclpSJ3jDu...
FACEBOOK_PAGE_ID=61589069834991
FACEBOOK_VERIFY_TOKEN=my_secure_verify_token_2024
FACEBOOK_APP_SECRET=votre_app_secret_ici
```

⚠️ **Important** : `FACEBOOK_APP_SECRET` ne doit PAS être "YOUR_APP_SECRET_HERE"

### 2. Obtenir l'App Secret

1. Aller sur https://developers.facebook.com
2. Sélectionner votre App
3. Aller dans Settings → Basic
4. Copier le **App Secret** et le mettre dans `.env`

## 🌐 URL du Webhook

Votre webhook est accessible à :
```
https://tm-digital.onrender.com/webhook
```

## ✅ Configuration Facebook Developer Console

### Étape 1 : Configurer la Webhook

1. Aller dans **Settings → Webhooks**
2. Cliquer sur **Select an object to get started** → **Pages**
3. Remplir les champs :
   - **Callback URL** : `https://tm-digital.onrender.com/webhook`
   - **Verify Token** : `my_secure_verify_token_2024` (doit correspondre à `.env`)
4. Cliquer **Verify and Save**

### Étape 2 : S'abonner aux événements Messages

1. Dans **Settings → Webhooks**
2. Sous votre configuration de webhook, cliquer **Edit**
3. Dans **Webhook Fields**, cocher :
   - ✓ `messages`
   - ✓ `messaging_postbacks`
   - ✓ `message_echoes`

### Étape 3 : Vérifier les Permissions de la Page

1. Aller dans **Messenger Settings**
2. S'assurer que votre **Page Access Token** a les permissions :
   - `messages_read`
   - `messages_manage`
   - `pages_manage_metadata`

### Étape 4 : Ajouter le Page Access Token

1. Aller dans **Messenger → Settings**
2. Cliquer sur **Access Tokens**
3. Générer un nouveau token pour votre page
4. Copier le token et le mettre dans `.env` comme `FACEBOOK_PAGE_ACCESS_TOKEN`

## 🧪 Test du Webhook

### Vérifier la Configuration avec cURL

```bash
curl -X GET "https://tm-digital.onrender.com/webhook?hub.mode=subscribe&hub.verify_token=my_secure_verify_token_2024&hub.challenge=test_challenge"
```

Vous devriez recevoir : `test_challenge`

### Envoyer un Message de Test via Facebook

1. Ouvrir votre page Facebook
2. Envoyer un message à votre page via Messenger
3. Vérifier les logs pour voir si le message est reçu

## 📊 Dépannage

### "Webhook signature validation will fail"

**Symptôme** : Message d'avertissement dans les logs
**Solution** : 
- Vérifier que `FACEBOOK_APP_SECRET` est configuré dans `.env`
- Redémarrer l'application après modification du `.env`

### "Invalid Facebook signature"

**Symptôme** : Les messages reçus sont rejetés avec cette erreur
**Solution** :
- Vérifier que `FACEBOOK_APP_SECRET` est exact (copié depuis Facebook Developer Console)
- Les secrets sont sensibles à la casse

### "Webhook POST received" mais pas de messages traités

**Symptôme** : Les logs montrent la réception du webhook mais pas de traitement de messages
**Solution** :
- Vérifier que vous avez activé les champs `messages` dans la configuration du webhook
- Vérifier que le `Webhook Fields` contient `messages` et `messaging_postbacks`

### "No POST in logs"

**Symptôme** : Aucune requête POST reçue du tout
**Solutions** :
1. Vérifier la **Callback URL** dans Facebook Developer Console (doit être exact)
2. Vérifier que la **Verify Token** correspond à celle dans `.env`
3. Vérifier que les champs `messages` sont activés dans **Webhook Fields**
4. Vérifier les logs de Facebook pour les erreurs de webhook
5. Tester manuellement la vérification du webhook avec cURL

## 📝 Fichiers de Logs Utiles

Les demandes de suppression de données sont enregistrées dans :
- `delete_requests.json`

Les réservations sont enregistrées dans :
- `reservations.json`

Les contacts sont enregistrées dans :
- `contacts.json`

## 🔐 Sécurité

- Ne jamais partager votre `FACEBOOK_APP_SECRET`
- Régulièrement régenérer votre `FACEBOOK_PAGE_ACCESS_TOKEN`
- Utiliser des variables d'environnement et ne pas commiter les secrets dans le code
- Vérifier que votre `.env` est dans `.gitignore`
