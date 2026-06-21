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
const functionsV1 = require("firebase-functions/v1");
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

// Email de REMERCIEMENT — envoyé quand un client vient de passer en Premium
async function sendPremiumThankYouEmail(resend, email) {
  await resend.emails.send({
    from: FROM_EMAIL,
    to: [email],
    subject: "Merci pour votre passage en Premium 🌿",
    html: `
      <div style="font-family:Arial,sans-serif;max-width:520px;margin:auto;color:#2a2114">
        <h1 style="color:#236648">Un grand merci 🙏</h1>
        <p>Merci d'avoir rejoint <strong>Keto Premium — Essenciel O Naturel</strong> !</p>
        <p>Votre accès Premium est dès maintenant activé : tous les <strong>modes alimentaires</strong>,
        le <strong>suivi avancé</strong> et l'ensemble des <strong>recettes</strong> sont débloqués dans l'application.</p>
        <p>Connectez-vous avec l'email de votre paiement pour en profiter immédiatement.
        Nous sommes ravis de vous accompagner vers plus d'énergie et de légèreté.</p>
        <p style="margin-top:24px;color:#8a7659">Belle cétose,<br>Essenciel O Naturel · Naturopathie</p>
      </div>
    `,
  });
}

// Email de BIENVENUE — envoyé à la création d'un nouveau compte (inscription)
async function sendSignupWelcomeEmail(resend, email, firstname) {
  const hello = firstname ? `Bonjour ${firstname},` : "Bonjour,";
  await resend.emails.send({
    from: FROM_EMAIL,
    to: [email],
    subject: "Bienvenue chez Essenciel O Naturel 🌿",
    html: `
      <div style="font-family:Arial,sans-serif;max-width:520px;margin:auto;color:#2a2114">
        <h1 style="color:#236648">Bienvenue 🌿</h1>
        <p>${hello}</p>
        <p>Votre compte vient d'être créé sur <strong>Le Keto par un Naturopathe — Essenciel O Naturel</strong>.
        Nous sommes heureux de vous compter parmi nous !</p>
        <p>Vous pouvez dès à présent renseigner votre profil pour obtenir un
        <strong>programme alimentaire personnalisé</strong>, suivre vos mesures et découvrir nos recettes.</p>
        <p>Pour débloquer tous les modes alimentaires et le suivi avancé, pensez à passer en <strong>Premium</strong>
        directement depuis l'application.</p>
        <p style="margin-top:24px;color:#8a7659">À très vite,<br>Essenciel O Naturel · Naturopathie</p>
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
          await sendPremiumThankYouEmail(resend, email);
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

// ════════════════════ BIENVENUE À L'INSCRIPTION ════════════════════
// Déclencheur Firebase Auth : s'exécute automatiquement à la création
// de tout nouveau compte (email/mot de passe OU Google) et envoie :
//   - un email de bienvenue au nouveau client
//   - une notification à l'administrateur
exports.welcomeOnSignup = functionsV1.auth.user().onCreate(async (user) => {
  const email = (user.email || "").trim().toLowerCase();
  if (!email) return null;

  // Prénom : displayName si dispo, sinon partie locale de l'email
  let firstname = "";
  if (user.displayName) firstname = user.displayName.split(" ")[0];
  else firstname = email.split("@")[0];

  try {
    const resend = new Resend(process.env.RESEND_API_KEY);
    await sendSignupWelcomeEmail(resend, email, firstname);
    await resend.emails.send({
      from: FROM_EMAIL,
      to: [ADMIN_EMAIL],
      subject: "👋 Nouvelle inscription",
      html: `<p>Nouveau compte créé : <strong>${email}</strong>${
        firstname ? " (" + firstname + ")" : ""
      }</p>`,
    });
    logger.info("Welcome email sent to", email);
  } catch (e) {
    logger.error("welcomeOnSignup Resend:", e.message);
  }
  return null;
});


// Email de notification au parrain (un filleul a utilisé son code)
async function sendReferralParrainEmail(resend, parrainEmail, filleulMasked, code, bonusDays) {
  await resend.emails.send({
    from: FROM_EMAIL,
    to: [parrainEmail],
    subject: "🎁 Votre parrainage Keto a été utilisé !",
    html: `
      <div style="font-family:Arial,sans-serif;max-width:520px;margin:auto;color:#2a2114">
        <h1 style="color:#236648">Merci de faire rayonner le keto 🌿</h1>
        <p>Bonne nouvelle : votre code de parrainage <strong>${code}</strong> vient d'être
        utilisé${filleulMasked ? " par <strong>" + filleulMasked + "</strong>" : ""}.</p>
        <p>En remerciement, <strong>${bonusDays} jours de Premium</strong> viennent d'être
        ajoutés à votre compte. Ils s'appliquent automatiquement à l'email de ce compte.</p>
        <p>Continuez à partager votre code : chaque filleul reçoit 3 mois Premium offerts,
        et vous gagnez 1 mois bonus à chaque utilisation.</p>
        <p style="margin-top:24px;color:#8a7659">Belle cétose,<br>Essenciel O Naturel · Naturopathie</p>
      </div>
    `,
  });
}

// ════════════════════ RÉCOMPENSE PARRAIN (parrainage) ════════════════════
// Appelée par l'app quand un filleul applique un code de parrainage.
//   - vérifie le jeton Firebase du filleul
//   - crédite le PARRAIN de N jours Premium (Admin SDK — contourne les règles
//     Firestore qui empêchent le filleul d'écrire le doc d'un autre email)
//   - envoie un email de notification au parrain
//   - idempotent : un même filleul ne crédite qu'une fois par code
exports.referralReward = onRequest({ region: "europe-west1", cors: true }, async (req, res) => {
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
    const filleulEmail = (decoded.email || "").trim().toLowerCase();
    if (!filleulEmail) return res.status(401).json({ error: "no_email" });

    const code = String((req.body && req.body.code) || "")
      .toUpperCase()
      .replace(/[^A-Z0-9]/g, "");
    if (!code) return res.status(400).json({ error: "no_code" });

    const codeRef = db.collection("referral_codes").doc(code);
    const codeSnap = await codeRef.get();
    if (!codeSnap.exists) return res.status(404).json({ error: "code_not_found" });

    const cdata = codeSnap.data() || {};
    if (cdata.active === false) return res.status(400).json({ error: "code_inactive" });
    const ownerEmail = (cdata.owner_email || "").trim().toLowerCase();
    if (!ownerEmail) return res.status(400).json({ error: "no_owner" });
    if (ownerEmail === filleulEmail) return res.status(400).json({ error: "self_referral" });
    const bonusDays = parseInt(cdata.bonus_days_for_owner || 30, 10);

    // Idempotence : un filleul ne crédite qu'une fois ce code
    const ledgerRef = db.collection("referral_parrain_grants").doc(code + "__" + filleulEmail);
    const ledgerSnap = await ledgerRef.get();
    if (ledgerSnap.exists) return res.json({ ok: true, already: true, bonusDays });

    // Créditer le parrain dans premium_emails/{ownerEmail}
    const pRef = db.collection("premium_emails").doc(ownerEmail);
    const pSnap = await pRef.get();
    const now = new Date();
    let base = now;
    let since = now.toISOString();
    let hasActiveSub = false;
    if (pSnap.exists) {
      const pd = pSnap.data() || {};
      since = pd.since || since;
      if (pd.subscriptionId && !pd.expires &&
          (pd.status === "active" || pd.status === "trialing" || pd.active === true)) {
        hasActiveSub = true; // abonnement Stripe en cours, sans date de fin
      }
      if (pd.expires) {
        const cur = new Date(pd.expires);
        if (cur > now) base = cur;
      }
    }
    if (hasActiveSub) {
      // Ne pas imposer d'expiration à un abonné Stripe : on mémorise le bonus
      await pRef.set({
        last_referral_bonus_at: now.toISOString(),
        referral_bonus_pending_days: admin.firestore.FieldValue.increment(bonusDays),
      }, { merge: true });
    } else {
      const newExpires = new Date(base.getTime() + bonusDays * 86400000);
      await pRef.set({
        active: true,
        since: since,
        expires: newExpires.toISOString(),
        source: "referral_owner_bonus",
        last_referral_bonus_at: now.toISOString(),
      }, { merge: true });
    }

    await ledgerRef.set({
      code: code,
      filleul_email: filleulEmail,
      owner_email: ownerEmail,
      bonus_days: bonusDays,
      at: now.toISOString(),
    });

    // Email au parrain
    try {
      const resend = new Resend(process.env.RESEND_API_KEY);
      const parts = filleulEmail.split("@");
      const masked = parts.length === 2 ? (parts[0].slice(0, 2) + "***@" + parts[1]) : "";
      await sendReferralParrainEmail(resend, ownerEmail, masked, code, bonusDays);
    } catch (e) {
      logger.error("referral email:", e.message);
    }

    return res.json({ ok: true, bonusDays: bonusDays });
  } catch (e) {
    logger.error("referralReward:", e.message);
    return res.status(500).json({ error: "server_error", message: e.message });
  }
});
