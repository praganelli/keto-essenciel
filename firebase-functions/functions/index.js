/**
 * Keto Premium — Webhook Stripe (Firebase Cloud Function, 2e génération)
 *
 * À chaque abonnement Stripe :
 *   1. Vérifie la signature du webhook (sécurité)
 *   2. Écrit le statut Premium dans Firestore (collection "premium_emails")
 *   3. Envoie un email de confirmation via Resend
 *
 * Événements gérés :
 *   - checkout.session.completed      -> active le Premium + email
 *   - customer.subscription.created   -> active le Premium
 *   - customer.subscription.deleted   -> désactive le Premium
 */

const { onRequest } = require("firebase-functions/v2/https");
const { defineSecret } = require("firebase-functions/params");
const logger = require("firebase-functions/logger");
const admin = require("firebase-admin");
const Stripe = require("stripe");
const { Resend } = require("resend");

admin.initializeApp();
const db = admin.firestore();

// Secrets (configurés via "firebase functions:secrets:set ...")
const STRIPE_SECRET_KEY = defineSecret("STRIPE_SECRET_KEY");
const STRIPE_WEBHOOK_SECRET = defineSecret("STRIPE_WEBHOOK_SECRET");
const RESEND_API_KEY = defineSecret("RESEND_API_KEY");

// ─── Configuration ───
const PREMIUM_COLLECTION = "premium_emails";
// Tant que le domaine n'est pas vérifié dans Resend, gardez onboarding@resend.dev
// (les emails ne partiront qu'au propriétaire du compte Resend).
// Après vérification du domaine essencielonaturel.fr, remplacez par :
//   "Essenciel O Naturel <infos@essencielonaturel.fr>"
const FROM_EMAIL = "Essenciel O Naturel <onboarding@resend.dev>";
const ADMIN_EMAIL = "infos@essencielonaturel.fr";

async function setPremium(email, active, source) {
  const key = (email || "").trim().toLowerCase();
  if (!key) return null;
  const data = active
    ? { active: true, source: source || "stripe", since: new Date().toISOString(), expires: null }
    : { active: false };
  await db.collection(PREMIUM_COLLECTION).doc(key).set(data, { merge: true });
  logger.info(`Premium ${active ? "activé" : "désactivé"} pour ${key}`);
  return key;
}

async function sendWelcomeEmail(resend, email) {
  await resend.emails.send({
    from: FROM_EMAIL,
    to: [email],
    subject: "Bienvenue dans Keto Premium 🌿",
    html: `
      <div style="font-family:Arial,sans-serif;max-width:520px;margin:auto;color:#2a2114">
        <h1 style="color:#236648">Bienvenue dans Keto Premium</h1>
        <p>Merci pour votre abonnement à <strong>Keto Premium — Essenciel O Naturel</strong>.</p>
        <p>Votre accès Premium est désormais activé : modes alimentaires, suivi avancé
        et toutes les recettes sont débloqués dans l'application.</p>
        <p>Connectez-vous avec l'email de votre paiement pour en profiter immédiatement.</p>
        <p style="margin-top:24px;color:#8a7659">Belle cétose,<br>Essenciel O Naturel · Naturopathie</p>
      </div>
    `,
  });
}

exports.stripeWebhook = onRequest(
  {
    region: "europe-west1",
    secrets: [STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET, RESEND_API_KEY],
  },
  async (req, res) => {
    const stripe = new Stripe(STRIPE_SECRET_KEY.value());

    // 1) Vérification de la signature avec le corps BRUT (req.rawBody)
    let event;
    try {
      event = stripe.webhooks.constructEvent(
        req.rawBody,
        req.headers["stripe-signature"],
        STRIPE_WEBHOOK_SECRET.value()
      );
    } catch (err) {
      logger.error("Signature invalide:", err.message);
      return res.status(400).send(`Webhook Error: ${err.message}`);
    }

    // 2) Traitement de l'événement
    try {
      const obj = event.data.object;

      if (event.type === "checkout.session.completed") {
        const email =
          (obj.customer_details && obj.customer_details.email) || obj.customer_email;
        if (email) {
          await setPremium(email, true, "stripe");
          try {
            const resend = new Resend(RESEND_API_KEY.value());
            await sendWelcomeEmail(resend, email);
            await resend.emails.send({
              from: FROM_EMAIL,
              to: [ADMIN_EMAIL],
              subject: "🎉 Nouvel abonné Premium",
              html: `<p>Nouvel abonnement Keto Premium : <strong>${email}</strong></p>`,
            });
          } catch (e) {
            logger.error("Erreur email Resend:", e.message);
          }
        }
      } else if (event.type === "customer.subscription.created") {
        const cust = await stripe.customers.retrieve(obj.customer);
        if (cust && cust.email) await setPremium(cust.email, true, "stripe");
      } else if (event.type === "customer.subscription.deleted") {
        const cust = await stripe.customers.retrieve(obj.customer);
        if (cust && cust.email) await setPremium(cust.email, false, "stripe");
      }
    } catch (e) {
      logger.error("Erreur de traitement:", e.message);
      // On répond quand même 200 pour éviter les ré-essais infinis de Stripe
    }

    return res.json({ received: true });
  }
);
