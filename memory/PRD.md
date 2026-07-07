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

## Update (July 2026) — Générateur de contenu : visuels de post complets
- Le générateur Facebook produit désormais des VISUELS DE POST COMPLETS (et non plus de simples photos) : bandeau titre pinceau vert, carte message, logo KETO-ESSENCIEL + slogan recréés par l'IA, photo culinaire, bandeau bas avec 4 icônes bénéfices + hashtags — dans le style de la marque, généré à partir du texte du jour.
- Backend (server.py): generate-day renvoie en plus `title`, `visual_text`, `benefits[4]`. Nouvelle fonction `build_infographic_prompt(day, kind)`. generate-image reçoit l'objet `day` (fallback Firestore) et compose l'infographie (carré 1024x1024 + story 1024x1536) via gpt-image-1.5.
- Frontend (keto.html): kpContentGenImage/retry passent l'objet `day` complet.
- Limite connue: le texte est peint par l'IA → petites fautes possibles sur mots longs (ex: SATIÉTÉ→SATITÉ). Trade-off d'une génération 100% auto.
- 502 fix confirmé (génération jour par jour, ~27s/jour) via logs réels (multiples generate-day 200 OK).

## Update (Juillet 2026) — Recherche/filtres recettes + Essai Premium 7 jours
- Bibliothèque: nouvel onglet « 🔍 Toutes » (recherche transversale ~474 recettes) + puces de filtres combinables (≤5g / ≤10g glucides, ≤15 min, Facile, 🌱 Végétal) + compteur de résultats live + état vide. Cartes enrichies de data-carb/data-time/data-diff/data-vegan (renderLibrary). Logique: ensureRecipeTools/toggleLibFilter/filterRecipes (~L14348).
- Essai Premium GRATUIT 7 jours (sans carte, 1x/compte, connexion requise): CTA dans la fenêtre Premium (#kpTrialCta, data-testid premium-trial-btn) au-dessus des offres. Activation réelle via Firestore premium_emails {active,since,expires+7j,source:'trial',plan:'trial',trialUsed:true} → kpStartTrial (~L18360). L'ancienne bannière "Essai Premium" (Phase 4) qui ne faisait qu'un faux compte à rebours localStorage a été re-branchée: startPremiumTrial() ouvre désormais la vraie fenêtre d'essai (~L21879).
## Update (June 2026, fork) — Menu du jour en slide-over + Favoris dans Recettes
- "Ouvrir le menu du jour" (Plan mobile) s'ouvre désormais en panneau glissant depuis la droite (CSS `body.day-sheet-open #day-panel`, backdrop `#daySheetBackdrop`, bouton fermer `#daySheetClose`; JS `setDayView`/`closeDaySheet`). Vérifié via screenshot (day-sheet-open=true).
- Section "⭐ Mes favoris" déplacée hors des Réglages vers le haut de l'onglet Recettes (#tab-library, #recipeFavSection + #favList, `renderFavoritesList()`). Doublon d'ID `favList` retiré de `buildModesSection()` (Réglages). Vérifié via screenshot (favoris rendus dans Recettes).

## Filtres recettes
- Testé (testing_agent iteration_6): filtres 6/6 PASS (≤5g→366, ≤10g→474, ≤15min→393, vegan→40, facile→437, recherche combinée OK, état vide OK); CTA essai visible + message invité OK. Écriture Firestore de l'essai (utilisateur connecté) non testable en fork (compte Firebase absent).
