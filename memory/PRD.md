# Keto Premium — PRD

## Problem statement (original, FR)
Application keto/naturopathie (HTML standalone autonome, embarquée dans une app Expo via WebView).
Bugs signalés :
1. Mesures corporelles & bien-être (onglet Suivi) : les valeurs saisies se retrouvaient sur tous les profils et clients.
2. Plan / petit-déjeuner : retirer le légume de "l'assiette complète" du petit-déjeuner.

## Architecture
- Frontend Expo (expo-router). `app/index.tsx` charge l'app keto via WebView (web = iframe) depuis `${EXPO_PUBLIC_BACKEND_URL}/api/app`.
- Backend FastAPI sert le fichier `backend/keto_app.html` sur `GET /api/app`.
- L'app keto = PWA HTML autonome (`/app/keto.html` = source de référence, copiée dans `backend/keto_app.html`).
- Stockage : localStorage côté HTML ; profils multi-utilisateurs + sync Firebase optionnelle.

## Fixes implémentés (2026-06-20)
- **Isolation Suivi par compte/profil** : `_kpActiveProfileId()` préfixe désormais la clé de stockage avec `u-<currentUser.uid>` quand l'utilisateur est connecté, combiné à l'id du profil local. Empêche le partage des mesures/bien-être entre comptes (clients) et profils. `renderSuivi()` rafraîchit aussi bien-être + mesures au changement de profil/compte.
- **Petit-déjeuner sans légume** : `balanceHtml()` n'affiche plus l'item "Légume" pour le slot `breakfast` (assiette complète = protéine + lipides), pill/ribbon adaptés, grille passée en 2 colonnes (`kp-balance-grid--two`). Le légume du petit-déj n'est plus ajouté à la liste de courses (`addBalanceToShopping`).

## Backlog / Next
- P1 : Migration optionnelle des anciennes données Suivi vers les nouvelles clés (actuellement data corrompue partagée laissée orpheline).
- P2 : Synchroniser mesures/bien-être vers le cloud (actuellement local uniquement).

## Update (June 2026) — UI polish + Premium webhook backend
- Profile tab: replaced activity/goal dropdowns with intensity bar + 2x2 goal cards; moved "Appliquer ces macros" button into Activité panel with a change-reminder hint.
- Mobile fixes: Parrainez/Essenciel single column before logout; fixed Essenciel footer being clipped (flex:0 0 auto on mobile); login screen scroll-down indicator.
- Toast messages: fixed invisible text (dark color on light glass) + variant styles (success/info/premium/error).
- Card entrance animations (1a) + animated macro distribution rings (2b) in day panel.
- NEW Premium backend (server.py): Stripe webhook /api/stripe/webhook (signature-verified via STRIPE_WEBHOOK_SECRET) -> writes premium_emails/{email} in Firestore (project testprojet-721cb) {active,source:'stripe',since,expires:null} + Resend confirmation email. /api/premium-status?email= for checks. Firebase Admin via backend/firebase_service_account.json. Keys in backend/.env (STRIPE_SECRET_KEY live, RESEND_API_KEY, STRIPE_WEBHOOK_SECRET).
- Frontend reads premium directly from Firestore (kpCheckPremium, collection premium_emails) -> auto-upgrades within ~5 min or on login.
- PENDING user actions: publish project for stable webhook URL (then update Stripe endpoint URL, keep same whsec_); verify essencielonaturel.fr domain in Resend then switch PREMIUM_FROM_EMAIL to infos@essencielonaturel.fr (currently onboarding@resend.dev -> only sends to account owner).
