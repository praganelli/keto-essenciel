# 🌿 Webhook Premium Stripe — Firebase Cloud Function
## Guide de déploiement (Keto · Essenciel O Naturel)

Ce dossier contient une **fonction Firebase** qui, à chaque abonnement Stripe :
1. vérifie la signature du webhook (sécurité),
2. écrit le statut Premium dans Firestore (`premium_emails`),
3. envoie un email de confirmation (Resend).

> ⚠️ La synchro avec votre app fonctionne car cette fonction écrit dans **le même
> projet Firebase** que l'application (`testprojet-721cb`).

---

## 🧩 Prérequis (à installer une fois)

1. **Node.js 20** → https://nodejs.org (téléchargez la version LTS, installez-la).
2. **Firebase CLI** → ouvrez un terminal et tapez :
   ```
   npm install -g firebase-tools
   ```
3. **Connexion** à votre compte Firebase :
   ```
   firebase login
   ```

---

## 💳 Activer le plan Blaze (obligatoire pour les fonctions)

Les Cloud Functions nécessitent le plan **Blaze** (paiement à l'usage).
👉 Il reste **gratuit** sous les quotas (très largement suffisant pour un webhook).
- Console Firebase → votre projet `testprojet-721cb` → en bas à gauche **« Upgrade »** → choisissez **Blaze**.
- Vous pouvez définir un **budget d'alerte** (ex. 1 €) pour être tranquille.

---

## 🔐 Configurer les 3 secrets

Dans un terminal, **placez-vous dans ce dossier** (`firebase-functions`) puis lancez
ces 3 commandes (collez la valeur demandée à chaque fois) :

```
firebase functions:secrets:set STRIPE_SECRET_KEY
firebase functions:secrets:set STRIPE_WEBHOOK_SECRET
firebase functions:secrets:set RESEND_API_KEY
```

Valeurs à coller :
- `STRIPE_SECRET_KEY`   → votre clé secrète Stripe (`sk_live_...`)
- `STRIPE_WEBHOOK_SECRET` → le secret de signature du webhook (`whsec_...`)
- `RESEND_API_KEY`      → votre clé Resend (`re_...`)

---

## 🚀 Déployer

Toujours dans le dossier `firebase-functions` :

```
cd functions
npm install
cd ..
firebase deploy --only functions
```

À la fin, Firebase affiche **l'URL de votre fonction**, du type :
```
https://europe-west1-testprojet-721cb.cloudfunctions.net/stripeWebhook
```
📋 **Copiez cette URL.**

---

## 🔗 Configurer le webhook dans Stripe

1. Dashboard Stripe (mode **Live**) → **Développeurs → Webhooks**.
2. Modifiez votre endpoint existant (ou créez-en un) et **collez l'URL** ci-dessus.
3. Événements à écouter :
   - `checkout.session.completed`
   - `customer.subscription.deleted`
   - (optionnel) `customer.subscription.created`
4. Le **secret de signature** (`whsec_...`) doit correspondre à celui que vous avez
   mis dans `STRIPE_WEBHOOK_SECRET`. Si Stripe en génère un nouveau, refaites la
   commande `firebase functions:secrets:set STRIPE_WEBHOOK_SECRET` puis redéployez.

---

## 📧 Emails vers vos clients (important)

Tant que le domaine n'est pas vérifié, les emails ne partent qu'à l'adresse du
propriétaire du compte Resend. Pour écrire à **tous vos clients** :
1. resend.com → **Domains → Add Domain** → `essencielonaturel.fr`
2. Ajoutez les enregistrements DNS demandés chez votre hébergeur.
3. Dans `functions/index.js`, remplacez la ligne :
   ```js
   const FROM_EMAIL = "Essenciel O Naturel <onboarding@resend.dev>";
   ```
   par :
   ```js
   const FROM_EMAIL = "Essenciel O Naturel <infos@essencielonaturel.fr>";
   ```
4. Redéployez : `firebase deploy --only functions`

---

## ✅ Tester

Faites un paiement test (ou utilisez l'outil **« Send test webhook »** de Stripe sur
votre endpoint). Vérifiez dans la **console Firestore** que le document
`premium_emails/{votre-email}` est créé avec `active: true`.
Dans l'app, reconnectez-vous : vous passez en Premium automatiquement. 🎉

---

Besoin d'aide ? Redonnez-moi l'URL de la fonction après déploiement et je vérifie
la configuration avec vous.
