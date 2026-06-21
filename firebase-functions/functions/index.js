/**
 * Keto Premium — Webhook Stripe + Résiliation (Firebase Cloud Functions, 2e gén.)
 *
 * stripeWebhook :
 *   - checkout.session.completed     -> active Premium + stocke détails abonnement + email
 *   - customer.subscription.updated  -> met à jour dates / type / résiliation prévue
 *   - customer.subscription.deleted  -> désactive Premium
 *
 * cancelSubscription (appelée par l'app) :
 *   - vérifie le jeton Firebase de l'utilisateur
 *   - résilie l'abonnement Stripe À LA FIN DE LA PÉRIODE PAYÉE (cancel_at_period_end)
 *
 * Les clés sont lues depuis functions/.env.
 */

const { onRequest } = require("firebase-functions/v2/https");
const logger = require("firebase-functions/logger");
const admin = require("firebase-admin");
const Stripe = require("stripe");
const { Resend } = require("resend");

admin.initializeApp();
const db = admin.firestore();

const PREMIUM_COLLECTION = "premium_emails";
// Après vérification du domaine dans Resend, remplacez par :
//   "Essenciel O Naturel <infos@essencielonaturel.fr>"
const FROM_EMAIL = "Essenciel O Naturel <onboarding@resend.dev>";
const ADMIN_EMAIL = "infos@essencielonaturel.fr";

function stripeClient() {
  return new Stripe(process.env.STRIPE_SECRET_KEY);
}

// Détails utiles d'un abonnement Stripe -> objet Firestore
function subData(sub) {
  const item = sub.items && sub.items.data && sub.items.data[0];
  const interval =
    item && item.price && item.price.recurring ? item.price.recurring.interval : null; // 'month' | 'year'
  return {
    subscriptionId: sub.id,
    customerId: typeof sub.customer === "string" ? sub.customer : (sub.customer && sub.customer.id),
    interval: interval,
    currentPeriodEnd: sub.current_period_end
      ? new Date(sub.current_period_end * 1000).toISOString()
      : null,
    cancelAtPeriodEnd: !!sub.cancel_at_period_end,
    status: sub.status,
  };
}

async function writeDoc(email, data) {
  const key = (email || "").trim().toLowerCase();
  if (!key) return null;
  await db.collection(PREMIUM_COLLECTION).doc(key).set(data, { merge: true });
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

// ════════════════════ WEBHOOK STRIPE ════════════════════
exports.stripeWebhook = onRequest({ region: "europe-west1" }, async (req, res) => {
  const stripe = stripeClient();

  let event;
  try {
    event = stripe.webhooks.constructEvent(
      req.rawBody,
      req.headers["stripe-signature"],
      process.env.STRIPE_WEBHOOK_SECRET
    );
  } catch (err) {
    logger.error("Signature invalide:", err.message);
    return res.status(400).send(`Webhook Error: ${err.message}`);
  }

  try {
    const obj = event.data.object;

    if (event.type === "checkout.session.completed") {
      const email =
        (obj.customer_details && obj.customer_details.email) || obj.customer_email;
      if (email) {
        let extra = {};
        if (obj.subscription) {
          try {
            const sub = await stripe.subscriptions.retrieve(obj.subscription);
            extra = subData(sub);
          } catch (e) {
            logger.error("retrieve sub:", e.message);
          }
        }
        await writeDoc(email, Object.assign(
          { active: true, source: "stripe", since: new Date().toISOString(), expires: null },
          extra
        ));
        try {
          const resend = new Resend(process.env.RESEND_API_KEY);
          await sendWelcomeEmail(resend, email);
          await resend.emails.send({
            from: FROM_EMAIL,
            to: [ADMIN_EMAIL],
            subject: "🎉 Nouvel abonné Premium",
            html: `<p>Nouvel abonnement Keto Premium : <strong>${email}</strong></p>`,
          });
        } catch (e) {
          logger.error("Resend:", e.message);
        }
      }
    } else if (event.type === "customer.subscription.updated") {
      const sub = obj;
      const cust = await stripe.customers.retrieve(sub.customer);
      if (cust && cust.email) {
        const active = sub.status === "active" || sub.status === "trialing";
        await writeDoc(cust.email, Object.assign({ active: active, source: "stripe" }, subData(sub)));
      }
    } else if (event.type === "customer.subscription.created") {
      const sub = obj;
      const cust = await stripe.customers.retrieve(sub.customer);
      if (cust && cust.email) {
        await writeDoc(cust.email, Object.assign({ active: true, source: "stripe" }, subData(sub)));
      }
    } else if (event.type === "customer.subscription.deleted") {
      const cust = await stripe.customers.retrieve(obj.customer);
      if (cust && cust.email) {
        await writeDoc(cust.email, { active: false, cancelAtPeriodEnd: false, status: "canceled" });
      }
    }
  } catch (e) {
    logger.error("Erreur de traitement:", e.message);
  }

  return res.json({ received: true });
});

// ════════════════════ RÉSILIATION (appelée par l'app) ════════════════════
exports.cancelSubscription = onRequest({ region: "europe-west1", cors: true }, async (req, res) => {
  try {
    if (req.method !== "POST") return res.status(405).json({ error: "method_not_allowed" });

    const authH = req.headers.authorization || "";
    const m = authH.match(/^Bearer (.+)$/);
    if (!m) return res.status(401).json({ error: "no_token" });

    let decoded;
    try {
      decoded = await admin.auth().verifyIdToken(m[1]);
    } catch (e) {
      return res.status(401).json({ error: "invalid_token" });
    }
    const email = (decoded.email || "").trim().toLowerCase();
    if (!email) return res.status(401).json({ error: "no_email" });

    const doc = await db.collection(PREMIUM_COLLECTION).doc(email).get();
    const data = doc.exists ? doc.data() : null;
    if (!data || !data.subscriptionId) return res.status(404).json({ error: "no_subscription" });

    const stripe = stripeClient();
    const sub = await stripe.subscriptions.update(data.subscriptionId, {
      cancel_at_period_end: true,
    });

    const periodEnd = sub.current_period_end
      ? new Date(sub.current_period_end * 1000).toISOString()
      : data.currentPeriodEnd || null;

    await writeDoc(email, {
      cancelAtPeriodEnd: true,
      currentPeriodEnd: periodEnd,
      status: sub.status,
    });

    return res.json({ ok: true, cancelAtPeriodEnd: true, currentPeriodEnd: periodEnd });
  } catch (e) {
    logger.error("cancelSubscription:", e.message);
    return res.status(500).json({ error: "server_error", message: e.message });
  }
});
