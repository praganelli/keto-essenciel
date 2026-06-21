const admin = require("firebase-admin");
admin.initializeApp({ credential: admin.credential.cert(require("/app/backend/firebase_service_account.json")) });
const db = admin.firestore();
const parrain = process.argv[2];
const code = process.argv[3];
const filleul = process.argv[4];
(async () => {
  const p = await db.collection("premium_emails").doc(parrain).get();
  console.log("premium_emails["+parrain+"] exists:", p.exists);
  if (p.exists) console.log("  data:", JSON.stringify(p.data()));
  const led = await db.collection("referral_parrain_grants").doc(code+"__"+filleul).get();
  console.log("ledger["+code+"__"+filleul+"] exists:", led.exists);
  if (led.exists) console.log("  data:", JSON.stringify(led.data()));
  const f = await db.collection("premium_emails").doc(filleul).get();
  console.log("premium_emails["+filleul+"] (filleul self-grant) exists:", f.exists);
  if (f.exists) console.log("  data:", JSON.stringify(f.data()));
  process.exit(0);
})();
