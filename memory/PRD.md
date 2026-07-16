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
- Testé (testing_agent iteration_6): filtres 6/6 PASS

## Renommage marque + version + menu du jour (fork, juin 2026)
- Marque "Keto Premium" → "Keto - Essenciel" partout ; badge version "v1.1" en haut ; onglet Plan par défaut = jour actuel.

## Admin recettes + Onglet Renforcement musculaire (fork, juin 2026)
- Module isolé ajouté en fin de body (script dédié) pour ne pas déstabiliser le fichier monolithique.
- ADMIN (infos@essencielonaturel.fr) : nouvelles cartes dans l'onglet Admin (via hook window.kpAdminExtras appelé après kpBindAdminPanel) :
  - « 🍽 Ajouter une recette » : photo (upload compressé ~700px base64), nom, catégorie, emoji, temps, difficulté, kcal, macros, description, ingrédients (format « qty | nom | emoji | type » par ligne), épices, étapes, astuce. Sauvegarde Firestore `custom_recipes` + fusion dans le pool correspondant (BFAST/MAIN/STARTER/DESSERT/SAUCE/SNACK/PAIN) → visible dans Recettes ET menus générés. Liste + suppression.
  - « 💪 Renforcement musculaire » : ajout programme/conseil (titre, niveau, contenu multi-lignes) → Firestore `muscle_content`. Liste + suppression.
- Recettes perso chargées au démarrage (waitFb → kpLoadCustomRecipes) et fusionnées. Photo affichée dans le modal recette (openRecipe patché) + cartes du menu du jour (dmc).
- ONGLET « 💪 Muscu » (bottom nav, visible par tous) : gate Premium — non-premium → upsell « Débloquer avec Premium » ; premium → programmes d'entraînement + conseils nutrition keto (contenu de départ fixe STARTER_PROGS/STARTER_TIPS + contenus Admin dynamiques). renderMuscle() branché dans switchTab.
- DÉPENDANCE À VÉRIFIER : règles Firestore doivent autoriser lecture publique + écriture admin sur `custom_recipes` et `muscle_content` (sinon chargement/sauvegarde échouent silencieusement — erreurs catchées, pas de crash).

## Barre d'onglets mobile : pleine largeur + zéro latence (fork, juin 2026)
- BUG: la barre d'onglets flottait (insets ~4px + gap ~6px au bas, coins arrondis) et le changement d'onglet paraissait lent (cascade de cartes ~1s).
- Fix largeur/position: override mobile `.bottom-nav{padding:0;left/right/bottom:0}` + `.bottom-nav .bottom-nav-inner{width:100%;max-width:none;margin:0;border-radius:0;padding:9px 10px max(9px,safe-area)}`. Vérifié testing_agent: left 0/right 390/bottom 844/gap 0/radius 0.
- Fix latence: kpAnimateCards stagger i*55→Math.min(i,6)*20 (≤120ms), appel via requestAnimationFrame (au lieu de setTimeout 30), .kp-card-in .34s→.26s, .tab-slide .22s→.16s. Vérifié: latences switchTab 2–60ms, aucune régression, 0 erreur JS.

## Impression menu/liste en popup interne (fork, juin 2026)
- Les 3 fonctions d'impression (exportPDF menu, printShopping liste, exportWeightPDF poids) utilisaient `window.open('','_blank')` → sur mobile/PWA ça ouvrait un onglet et le retour rechargeait l'app (→ écran connexion / perte session invité).
- Nouveau: popup INTERNE `#kpPrintOverlay` (overlay `.recipe-overlay`, z-index 1300, portalé body) affichant l'aperçu formaté dans une `<iframe srcdoc>`, avec boutons « Fermer » (kpClosePrint) et « Imprimer » (kpDoPrint → iframe.print()). Aucun nouvel onglet, l'utilisateur reste dans l'app. Fallback window.open conservé si l'iframe indisponible.
- Nettoyage marque restante dans les templates d'impression: "Keto Premium V9" → "Keto - Essenciel".
- Vérifié: liste + menu ouvrent la popup, « Fermer » revient au Plan sans déconnexion (authVisible=none).

## Régénération auto au changement de mode (fork, juin 2026)
- `applyDietMode(modeId)` : après recalcul des cibles, régénère IMMÉDIATEMENT la semaine via `generateMenu()` (wrappé par withFilteredRecipes → filtre selon le mode), puis `switchTab('plan')` + `setDayView('week')` pour montrer le résultat. Flag `window._suppressMenuToast` pour éviter le double toast (garde uniquement « Mode X — nouveau menu généré ✅»). Gating Premium existant conservé (non-premium → modal Premium). Vérifié en Premium : standard(viande) → vegetarien → menu régénéré (tofu/tempeh), tab=plan, dietMode=vegetarien.

## Refonte contenu « Menu du jour » (fork, juin 2026)
- BUGFIX: le modal recette (openRecipe) s'ouvrait SOUS le bottom sheet (z-index 200 < 901). Corrigé: `.recipe-overlay` z-index→1300 + portage sur document.body à l'ouverture (openRecipe). Vérifié (rectTop:0/bottom:844 plein écran au-dessus du sheet).
- Contenu de la fiche (bottom sheet) refait en Option A + résumé d'ingrédients : cartes repas compactes `.dmc` (pastille emoji, badge, titre Fraunces italique, description 2 lignes, pastilles macros kcal/lip/prot/gluc, temps, chips « Ingrédients » = noms uniquement, boutons « Voir la recette » → openRecipe + « Changer » → swapMeal). Détails complets (étapes/assaisonnements/notes) uniquement dans la fiche recette. Nouvelles fonctions dmcBfast/dmcMain/dmcCourse + _dmcMealCard ; renderDayPanel appelle ces builders (les anciens build* restent inutilisés). En-tête + anneaux macros conservés. Vérifié via screenshot (3 cartes, titres + chips ingrédients OK, pas d'erreur JS).

## Optimisation fluidité + corrections (fork, juin 2026)
- Test frontend complet (testing_agent iteration_8) : AUCUNE erreur JS. Tous les changements récents validés (bottom sheet + 3 modes de fermeture, renommage, badge v1.1, Réglages sous Info perso, macros correctes, jour actuel par défaut).
- Fluidité globale (CSS reset) : `-webkit-tap-highlight-color:transparent` (plus de flash gris au tap), `text-size-adjust:100%`, `-webkit-font-smoothing:antialiased`, momentum scroll, support `prefers-reduced-motion`.
- Perf : negative-cache 60s sur la lecture Firestore LPEV → supprime les appels réseau répétés + le spam de warnings « Missing or insufficient permissions » en mode invité (warnings attendus, non bloquants).
- Layout : anti-débordement horizontal sur les cartes accordéon Profil (Activité/Repas/Composition) — `overflow-x:hidden` + `minmax(0,1fr)` sur les grilles + labels d'activité réduits. Page sans scroll horizontal (docSW=viewport).
- Non modifié (comportements intentionnels signalés par le testeur) : auto-ouverture du Bilan Keto en invité, bannière collante « Essai Premium » — à ajuster sur demande.
- Panneau "Menu du jour" (mobile) : animation slide améliorée (ressort cubic-bezier .16,1,.3,1, fond flouté 4px, panneau arrondi, bouton fermeture animé, contenu en fade-in).
- Écran Profil (mobile) : entrée "Réglages" déplacée SOUS la carte "Informations personnelles".
- Carte "Vos macros" : fix débordement texte (result-macros grid minmax(0,1fr), rm-val/rm-lab nowrap+ellipsis, letter-spacing réduit).
- BUG corrigé : `calcMacros` faisait `tdee + p.goal` (concat texte si goal en string → 24680 kcal). Corrigé en `Number(p.goal||0)` + `Number(p.activity||1)`. Vérifié (target 1711 kcal correct).
- Geste swipe : le panneau « Menu du jour » est désormais un BOTTOM SHEET iOS 26 (remonte du bas, coins arrondis, poignée de glissement, fond flouté 6px, ressort). Fermeture par glisser vers le bas, tap sur la poignée ou tap à l'extérieur. IMPORTANT: le sheet est PORTALÉ sur document.body à l'ouverture (portalDaySheet/unportalDaySheet) car #tab-plan.tab-slide a un `transform` qui cassait le position:fixed. Vérifié via screenshots (rectTop:68/bottom:844 épinglé viewport ; swipe down → open=false).
- Marque "Keto Premium" → "Keto - Essenciel" partout (titre, auth, splash, onboarding, aide, manifeste PWA, notifications, parrainage, footers PDF, statut abonnement, toasts).
- Badge version "Keto - Essenciel · v1.1" ajouté en haut de l'écran (header, sous le titre) via `.app-version-badge`.
- Onglet Plan : le jour affiché par défaut est désormais le JOUR ACTUEL (`TODAY_IDX=(getDay()+6)%7`, `activeDay=TODAY_IDX`). Le hero affiche le badge "📍 Aujourd'hui". Vérifié via screenshot (Mardi + tag Aujourd'hui + badge v1.1). (≤5g→366, ≤10g→474, ≤15min→393, vegan→40, facile→437, recherche combinée OK, état vide OK); CTA essai visible + message invité OK. Écriture Firestore de l'essai (utilisateur connecté) non testable en fork (compte Firebase absent).

## Admin : édition/suppression/restauration de TOUTES les recettes (fork, juin 2026)
- Barre d'actions ADMIN (✏️ Modifier / 🗑 Supprimer) injectée en bas du modal recette (openRecipe) — visible uniquement si window.isAdmin(). Fonctionne pour les recettes perso ET les recettes « en dur ».
- Édition: overlay #kpRecipeEditOverlay (mêmes champs que l'ajout, pré-remplis). kpAdminEditRecipe(id) → kpAdminSaveRecipeEdit(). Recette perso → update custom_recipes/{docId}; recette en dur → set recipe_overrides/{id}. Application immédiate en mémoire + renderLibrary.
- Suppression: kpAdminDeleteRecipeById(id) avec CONFIRMATION. Perso → delete custom_recipes/{docId}; en dur → set recipe_deletions/{id} (pierre tombale). Splice en mémoire.
- Restauration: carte « 🗑 Recettes supprimées » dans l'onglet Admin (kpAdminLoadDeletions/kpAdminRestoreRecipe) → delete tombstone + location.reload().
- Chargement au démarrage (déjà présent): kpLoadCustomRecipes applique recipe_overrides puis recipe_deletions.
- firestore.rules: 2 nouvelles collections recipe_overrides + recipe_deletions (lecture publique, écriture admin infos@essencielonaturel.fr). → UTILISATEUR DOIT RECOLLER firestore.rules dans la console Firebase.
- Corrigé: résidu « ml> » supprimé en fin de keto.html. Fichier synchronisé vers backend/keto_app.html.
- Vérifié (screenshot/DOM): openRecipe OK, barre admin présente, éditeur ouvert pré-rempli (Saumon citron-aneth), 0 erreur JS. NON testable en sandbox: écritures Firestore réelles (nécessitent login admin + connexion Firestore) → à valider par l'utilisateur en prod.

## Refonte onglet Musculation + Tests physiques (fork, juin 2026)
- Onglet Musculation (renderMuscle) entièrement redesigné : hero dégradé vert, navigation segmentée 3 vues (🏋️ Programmes / 🥩 Nutrition / 📊 Tests physiques) via kpMuscleSwitch, cartes premium (styles injectés #mxStyles, classes mx-*). Cache contenu Admin window._muscleDyn (invalidé à l'ajout/suppression muscle_content).
- NOUVEAU : vue « Tests physiques » (source : PPTX utilisateur « Testez vos capacités physiques »). 8 tests : Cooper, Ruffier-Dickson, Souplesse, Équilibre unipodal, Suspension (grip), Maintien traction, Pompes, Redressements assis. Chaque carte = intro + étapes numérotées + barème.
- 2 calculateurs INTERACTIFS : Cooper → VO₂max = (d-504.9)/44.73 + catégorie (kpCooperCalc). Ruffier-Dickson → indice = ((F1-70)+(F2-F0))/10 + interprétation (kpRuffierCalc). Vérifiés : 2600m→46.8 Très bon ; F0=70,F1=120,F2=85→6.5 faible.
- Vérifié via screenshots (Premium forcé) : hero + 3 onglets + switch OK, 8 cartes tests, calculateurs corrects, 0 erreur JS.

## Journal des tests + suppression tagline (fork, juin 2026)
- Journal de progression dans la vue « Tests physiques » (Muscu) : chaque carte de test a un champ « 📔 Enregistrer mon résultat » + bouton 💾 (kpTestSave). Cooper & Ruffier auto-remplissent le champ après calcul. Carte « Mon journal des tests » en tête listant par test la dernière valeur, la variation vs précédent (progrès/baisse, ruffier = plus bas = mieux via TEST_LOWER), l'historique daté + suppression (kpTestDelete).
- Stockage localStorage scoping par utilisateur (kp_test_journal_u-<uid> / guest) + miroir best-effort Firestore users/{uid}/ketoTests/data.
- Vérifié : tagline masquée, Cooper autofill 46.8, 2 entrées enregistrées et affichées, 0 erreur JS.
- Tagline d'en-tête « Bonjour ! Plan · Bibliothèque · Suivi · Profil » SUPPRIMÉE (.tagline{display:none}).

## CTA « Passez Premium » sidebar desktop plus visible (fork, juin 2026)
- Le bouton doré .bnav-premium-cta était trop pâle et se fondait dans le fond crème. Refait : dégradé doré plus profond (#e9b73f→#a86f16), texte + flèche BLANCS avec ombre, bordure dorée + halo (box-shadow ring 3px), padding augmenté. Vérifié via screenshot desktop 1440 : bouton bien lisible et contrasté.

## CTA Premium repositionné en HAUT de la sidebar desktop (fork, juin 2026)
- Suite retour utilisateur (« toujours pareil / mets-le ailleurs ») : le bouton .bnav-premium-cta est DÉPLACÉ tout en haut de la sidebar (order:-1, sous .bnav-brand order:-2, avant le label MENU + onglets). margin auto retirée du CTA et reportée sur .bnav-profile-card (margin-top:auto) pour garder profil/réglages ancrés en bas. Vérifié desktop 1440 : CTA en haut (top~228), au-dessus des onglets.

## Fix troncature CTA Premium sidebar desktop (fork, juin 2026)
- Cause : .bottom-nav-inner (sidebar desktop) height:100% sans overflow → sur petits écrans le contenu dépassait et les items étaient rognés (flex-shrink). Fix : overflow-y:auto + scrollbar fine + `.bottom-nav-inner>*{flex:0 0 auto}` (aucun écrasement) + padding top 34→22. CTA reste en haut (order:-1), toujours entièrement visible. Vérifié 1280x700 : CTA fullyVisible true, sidebar scrollable.

## Variété générateur + Préparation détaillée IA (fork, juin 2026)
- GÉNÉRATEUR (generateMenu ligne ~12606) : pickRecipe prenait toujours scored[0] (±0.25 aléatoire) → toujours les mêmes recettes. Corrigé : pioche AU HASARD parmi les ~60% meilleurs candidats (min 8) → toute la bibliothèque tourne. Vérifié : 3 générations toutes différentes, 7 déjeuners distincts/semaine, pools bfast 92/main 253/starter 12/dessert 20. NB: snacks & pains ne sont PAS dans la structure repas (petit-déj/déj/dîner + entrée/dessert) car le menu référence des index par tableau de catégorie ; ajouter un créneau collation/pain = refonte à part.
- PRÉPARATION DÉTAILLÉE IA : nouveau endpoint POST /api/recipe/detailed-steps (public, OpenAI gpt-5.5, JSON steps[]+tip). Bouton « ✨ Générer une préparation détaillée » sous les étapes du modal recette (kpDetailSteps/kpRenderDetailSteps), cache localStorage (kp_detail_steps_<id>) + auto-chargement à la réouverture. 
- IMPORTANT PROXY : l'endpoint renvoie TOUJOURS HTTP 200 avec {ok:false,error} en cas d'erreur OpenAI (un 5xx serait remplacé par une page HTML par le proxy Cloudflare → le front ne pourrait pas lire le JSON). Messages d'erreur FR clairs (quota/rate/no key). Clé OpenAI serveur actuellement en insufficient_quota → l'utilisateur doit fournir une clé avec crédit (même clé que le Générateur de contenu).

## Badge unifié marque + version + statut (fork, juin 2026)
- Fusion des 2 badges de l'en-tête mobile (.app-version-badge « Keto - Essenciel · v1.1 » + .plan-status-mobile « Version Gratuite ») en UN seul badge élégant .brand-badge (lignes ~7702) : 🥑 + « Keto Essenciel » + chip « v1.1 » + séparateur + segment statut (ids conservés planStatusMobile/planStatusMobileTxt pour compat JS ligne 14485). Segment statut vert en Gratuit, dégradé doré en Premium (.bb-status.is-premium). Vérifié mobile 390px, 0 erreur JS.

## Fix débordement badge unifié (fork, juin 2026)
- .brand-badge débordait sur écrans étroits (325px sur vw 320). Corrigé : flex-wrap:wrap + justify-content:center + max-width:calc(100% - 28px) + row-gap, white-space nowrap déplacé sur les segments internes (.bb-name/.bb-ver/.bb-status). Vérifié 320px (wrap, pas de débordement) et 390px (1 ligne).

## Bannière quiz masquée après complétion (fork, juin 2026)
- Avant : la bannière #quizPromoBanner ne disparaissait que si score 100% (kp_quiz_perfect). Désormais : à la fin du quiz (renderQuizResult, quel que soit le score) on set kp_quiz_done='1' + display:none. Logique d'affichage au chargement masque si kp_quiz_done/kp_quiz_perfect/kp_quiz_score présent. Vérifié : bannière flex→none après 15 réponses, reste none au reload.

## Optimisation performance iOS (surchauffe/latence) (fork, juin 2026)
- Diagnostic : orbs blur(100-120px) déjà masqués (body.kp-v13). Vrais coûts GPU mobiles repeints à chaque frame de scroll : (1) backdrop-filter (128 usages, surtout blur(30px)+saturate(200%) sur menu bas + header FIXES, saturate = très coûteux iOS), (2) body::before/::after = grain plein écran en mix-blend-mode:multiply (blend de tout le viewport), (3) setInterval 1200ms (kpUpdateProfileIdentity) + 1500ms (observer scan).
- Fix (bloc <style id="kp-perf-mobile"> avant </body>, scoped @media (pointer:coarse) = tactile only, desktop intact) : `*{backdrop-filter:none}` puis flou léger RÉACTIVÉ uniquement sur .bottom-nav-inner (blur 10px + fond opaque light/dark), header, et overlays (.recipe-overlay/.kp-modal-overlay/.prefs-overlay/.subst-overlay/.day-sheet*/.quiz-overlay/.kp-cprofile-overlay blur 8px). body::before/after → mix-blend-mode:normal + opacity .04. Timers throttlés 1200→3000ms et 1500→3000ms.
- Desktop non affecté (pointer:coarse ne matche pas). App charge sans erreur. NON mesurable en sandbox (pas d'iPhone) → à valider par l'utilisateur sur son appareil.

## Tests physiques en carrousel horizontal (fork, juin 2026)
- Vue « Tests physiques » (Muscu) : les 8 tests passent d'une pile verticale à un CARROUSEL horizontal. .mx-carousel (flex + overflow-x:auto + scroll-snap-type:x mandatory), chaque test = .mx-slide flex:0 0 100%. Navigation : swipe natif + flèches ‹/› (kpCarouselStep) + points cliquables (kpCarouselGo) + compteur « Test x/8 » (#mxCounter). Dots/compteur/flèches mis à jour au scroll via kpBindCarousel/kpCarouselUpdate (flèche prev cachée au 1er, next au dernier). Le journal reste au-dessus. Vérifié : 8 slides, go(2)→Test 3/8 dot actif 2, 0 erreur.

## Fix "The string did not match the expected pattern" sur Préparation détaillée (fork, juin 2026)
- Cause : /api/download livre le HTML en téléchargement (index.html). Ouvert en local (file://) ou hébergé ailleurs (Firebase), l'appel relatif /api/recipe/detailed-steps ne trouve plus le backend → Safari renvoie "The string did not match the expected pattern" (fetch échoue). Dans la preview servie par le backend, l'appel relatif marchait.
- Fix : backend injecte window.__KP_API_BASE__ = URL absolue (déduite des en-têtes x-forwarded-proto/host) dans /api/app ET /api/download (HTMLResponse + injection avant </head>, helper _serve_html_with_base / _api_base_from_request). Frontend kpDetailSteps utilise apiBase + '/api/...'. CORS déjà en '*'. Vérifié : base injectée = https://body-metrics-bug..., endpoint OK (~15s) renvoie {ok:true,steps:[...]} étapes détaillées FR. La clé OpenAI a de nouveau du crédit.
- ACTION UTILISATEUR : re-télécharger l'app via /api/download pour récupérer la version avec l'URL backend injectée. NB: l'URL backend injectée est celle de la session courante (change à chaque fork) → pour une prod stable il faudra un backend déployé permanent.

## Section Gainage dans Muscu (fork, juin 2026)
- Nouvel onglet 'gainage' dans le segmented control Muscu (4 onglets : Progr./Nutrition/Gainage/Tests). GAINAGE_EXOS (10 exercices : Planche, Planche bras tendus, Gainage latéral, latéral genoux, lever de jambe, Bird Dog, Dead Bug, Planche dynamique, Mountain Climber lent, Hollow Hold) + GAINAGE_PROGRAMS (Débutant 5min, Interm. 10min). Chaque carte exo : icône, badge niveau (vert/orange/rouge via lvlColor), muscles 🎯 (mx-chip), position numérotée, conseil 💡, erreurs à éviter ⚠️ (mx-warn), durée/reps ⏱ (mx-dur). Filtre par niveau (kpGainageFilter, window.kpGainageLvl) Tous/Débutant/Interm/Avancé. gainageExoCard/gainageProgCard. Vérifié : 4 segs, 12 cartes, filtre Avancé→Hollow Hold seul, 0 erreur.

## Fin de la déconnexion auto en arrière-plan / persistance session (fork, juin 2026)
- Cause du "déconnecté à chaque changement d'app" sur iOS Safari : IIFE autoLogoutOnInactive (ligne ~14593) faisait authInstance.signOut() sur visibilitychange(hidden) + pagehide. SUPPRIMÉE.
- Ajout : authInstance.setPersistence(firebase.auth.Auth.Persistence.LOCAL) après init auth (garantit la survie de session au background/reload d'onglet). 

## Refonte onglet Muscu : Quiz onboarding + Gainage carrousel + suppression Nutrition (fork, juin 2026)
- SEGMENTS Muscu réduits de 4 à 3 : Progr. / Gainage / Tests. La section « Nutrition » (bouton nutri + rendu tips) a été SUPPRIMÉE de renderMuscle/renderMuscleBody (STARTER_TIPS/tipCard restent définis mais inutilisés).
- QUIZ FORME & SANTÉ (12 questions) : auto-déclenché à la 1ère visite de l'onglet Muscu (Premium requis). MUSCU_Q (âge, fréquence, condition, planche, douleurs dos/genoux/épaules, cœur/tension, grossesse, équilibre, objectif, temps/séance). kpMuscuRecommend mappe les réponses → niveau (Débutant/Interm/Avancé) + précautions + exercices filtrés (exclut Hollow Hold si cardio/grossesse, planches bras tendus si épaules, etc.) + conseils sport. Overlay #muscuQuizOverlay (kpOpenMuscuQuiz/kpMuscuAnswer/kpMuscuSubmit).
- PERSISTANCE : localStorage scoping par user (muKey='kp_muscu_'+uid/guest, {done,profile,ans}) + miroir Firestore users/{uid}/ketoMuscu/data (muStore). Au 1er render, muFbLoad récupère depuis Firestore si local vide (autres appareils) → quiz affiché une seule fois. Auto-trigger re-vérifie done au moment du setTimeout (anti-doublon).
- PROGRAMME PERSONNALISÉ affiché en tête de la vue Gainage (muscuRecoCard : niveau, précautions ⚠️, exercices recommandés, sport conseillé, bouton « ↻ Refaire le questionnaire »). Si quiz non fait → carte CTA « 📝 Faire le questionnaire ».
- GAINAGE EN CARROUSEL : les 10 exercices (GAINAGE_EXOS) passent d'une liste verticale à un carrousel horizontal (#mxCarousel data-label="Exercice", flèches ‹/›, dots, compteur « Exercice x/10 »). Réutilise l'infra kpBindCarousel/kpCarouselStep/kpCarouselGo (kpCarouselUpdate lit data-label pour le libellé du compteur, générique Test/Exercice). Filtre par niveau conservé (re-render du carrousel). Programmes guidés conservés au-dessus.
- Vérifié via screenshot (Premium forcé) : quiz auto-ouvert 12 Q, submit → niveau Intermédiaire, précautions dos/genoux, 10 slides carrousel, nav ‹/› (Exercice 1→3/10), 3 segments (Nutrition absente), 0 erreur JS. keto.html synchronisé vers backend/keto_app.html.

## Muscu v2 : quiz wizard pas-à-pas + Diabète type 2 + programme perso détaillé (fork, juin 2026)
- QUIZ REFAIT en assistant pas-à-pas (une question par écran) : overlay .mq-modal (header dégradé vert, barre de progression #mqBar, compteur « Question x sur 13 », cartes d'options .mq-opt avec pastille radio, footer Précédent/Suivant, anim mqIn). Auto-avance à la sélection (kpMuscuAnswer→kpMuscuNext 240ms), navigation kpMuscuPrev/kpMuscuNext, validation kpMuscuSubmit. Pré-remplissage depuis muLoad().ans si « Refaire ».
- NOUVELLE pathologie « DIABÈTE de type 2 » (Non / Pré-diabète / Oui traité) ajoutée aux 12 → 13 questions. kpMuscuRecommend REFACTORISÉ en clés (MUSCU_Q a un `key` par question : age/freq/cond/plank/back/knee/shoulder/cardio/diabetes/preg/balance/goal/time) pour éviter les bugs d'index. Diabète → caution (marche 10-15 min après repas, encas, hypo) + conseil sport (150 min/sem + marche post-repas).
- PROGRAMME PERSONNALISÉ redesigné (muscuRecoCard + muscuRecoExoCard) : carte .mrx-card (en-tête dégradé « Sur-mesure / Niveau X / N exercices », blocs « Vos points de vigilance », « Vos exercices — le mouvement détaillé » = chaque exo avec icône, description, étapes numérotées « Comment faire », astuce 💡, erreurs ⚠️, durée ⏱, puis « Activité sportive conseillée », bouton Refaire).
- SÉPARATION nette dans la vue Gainage : « 🎯 Mon programme personnalisé » → diviseur .mrx-divider → « 🔥 Programmes guidés » → diviseur → « 💪 Bibliothèque d'exercices » (carrousel filtrable).
- Vérifié via screenshot : wizard Q1/13 propre, submit avec diabetes=Oui → Niveau Intermédiaire, 8 exos, 23 étapes détaillées, caution Diabète affichée, programmes guidés + carrousel présents, 0 erreur JS.

## FIX « Firebase indisponible » sur édition/suppression/ajout recette (fork, juin 2026)
- ROOT CAUSE (confirmée en live) : une seule app Firebase existe et elle est NOMMÉE (`keto-app`, via firebase.initializeApp(cfg, appName) réutilisée par authInitFirebase). Il n'y a AUCUNE app par défaut. Or kpFs() faisait `firebase.firestore()` (app par défaut) → throw « No Firebase App '[DEFAULT]' » → kpFs renvoyait null → toast « Firebase indisponible » sur kpAdminSaveRecipeEdit/kpAdminDeleteRecipeById/kpAdminSaveRecipe (et chargement silencieusement KO pour custom_recipes/muscle_content).
- FIX : kpFs() (module admin, ~L24610) préfère désormais l'app AUTHENTIFIÉE : `authFirebase.firestore()` → sinon `firebase.apps[0].firestore()` → sinon `firebase.firestore()`. Bénéfice double : (1) plus d'erreur d'app par défaut, (2) les écritures portent le token auth de l'admin (indispensable pour passer les règles Firestore qui exigent request.auth.token.email == admin). Vérifié en live : kpFs() résout vers l'app 'keto-app'. Le flux write complet nécessite un login admin (non testable en sandbox) mais la cause du blocage est levée.

## Muscu : onglet « 🎯 Perso » dédié + exercices personnalisés en slider (fork, juin 2026)
- NOUVEAU segment « 🎯 Perso » dans le control Muscu (Progr. / Perso / Gainage / Tests). renderMuscleBody a une branche `view==='perso'` : affiche muscuRecoCard(profil) si quiz fait, sinon une carte CTA « Faire le questionnaire ». Le programme personnalisé a été RETIRÉ de la vue Gainage (qui ne contient plus que Programmes guidés + Bibliothèque d'exercices). kpMuscuSubmit atterrit désormais sur `perso`.
- EXERCICES personnalisés en SLIDER : dans muscuRecoCard, les exercices recommandés passent d'une pile verticale à un carrousel horizontal (#mxCarousel data-label="Exercice", flèches ‹/›, dots, compteur « Exercice x/N ») — chaque slide = carte muscuRecoExoCard détaillée (étapes, astuce, erreurs, durée). kpBindCarousel appelé après rendu. CSS : `.mx-slide .mrx-exo{margin-bottom:0}`.
- Vérifié via screenshot : onglet Perso actif, 8 slides « Exercice 1/8 », cartes détaillées, vigilance Diabète, Niveau Intermédiaire, 0 erreur JS.

## Muscu : programmes guidés en sliders (1 slide/exercice) + carrousel multi-instances (fork, juin 2026)
- REFACTO carrousel en MULTI-INSTANCES : nouveaux helpers génériques kpCarIndex/kpCarUpdate(id)/kpCarGo(id,i)/kpCarStep(id,dir)/kpBindCar(id) + builder buildCarousel(id,label,slides[]). Sélecteurs par attributs data-counter/data-dots/data-prev/data-next="{id}" (plus d'IDs globaux uniques mxCarousel/mxDots…). Migrés : Tests (id mxTests), Bibliothèque gainage (mxGain), Perso (mxPerso). Chaque instance est indépendante (vérifié : step sur mxProg0 n'affecte pas mxProg1).
- PROGRAMMES GUIDÉS (GAINAGE_PROGRAMS) : chaque programme est désormais un SLIDER avec une slide par étape (id mxProg{i}). gainageProgCard(p,idx) → buildCarousel. progStepSlide mappe le nom de l'étape à l'exercice GAINAGE_EXOS (PROG_MAP + findGainageByLabel) et affiche le mouvement détaillé (icône, « Comment faire » étapes numérotées, astuce 💡, durée ⏱). Les étapes « Repos » = slide dédiée ⏸️. En-tête programme montre « durée · N exercices ».
- Vérifié via screenshot : Débutant 11 étapes / Interm. 9 étapes en sliders indépendants, mouvement détaillé par slide, dots+flèches+compteur « Étape x/N », Perso+Tests sans régression, 0 erreur JS.
- Comme la déconnexion n'est plus automatique, le bouton manuel #profileLogoutZone est RÉAFFICHÉ : renderProfileIdentity met display='' (au lieu de 'none'), et retrait de .profile-logout-zone de la règle @media(max-width:1023px){display:none!important} (ligne 625). Les entrées nav #nt-logout/.bnav-logout/#headerLogoutBtn restent masquées sur mobile (déconnexion via Profil). Vérifié : bg simulé = pas de logout, bouton "Se déconnecter" visible dans Profil, 0 erreur.

## Fork juin/juillet 2026 — Corrections + Générateur de contenu v2 + Emails + Admin Inscrits
- RÈGLES FIRESTORE : blocs manquants ajoutés dans /app/firestore.rules (recipe_overrides, recipe_deletions, generated_content — read public/admin, write admin). Endpoint GET /api/download-rules pour télécharger le fichier. L'utilisateur doit publier les règles dans la console Firebase (fait, confirmé OK).
- SUPPRESSIONS RECETTES : les recettes PERSO (custom_recipes) sont désormais archivées dans recipe_deletions (doc 'c_'+docId, {custom:true, data:kpStripRuntime(r)}) avant suppression → restaurables via kpAdminRestoreRecipe (re-add dans custom_recipes). Badge Perso/Origine dans la liste admin « Recettes supprimées ».
- BUG « Voir la recette ≠ menu » : 30 IDS EN DOUBLE entre le bloc vegan MAIN_RECIPES (1100-1129) et un bloc BFAST (1100-1129). Renuméroté MAIN vegan → 1400-1429 (BFAST conservé car findRecipe/overrides résolvaient vers BFAST). Vérifié : 0 doublon, 980 repas testés sans mismatch.
- LÉGUME D'ACCOMPAGNEMENT : si le plat principal (déjeuner/dîner) n'a aucun ingrédient type 'veg' → generateMenu ajoute d.lunchVeg/dinnerVeg depuis KETO_VEG_SIDES (12 légumes keto, rotation, {name,emoji,qty,shop}). Affiché : encart vert + CHIP dans les ingrédients de la carte (dmcMain/_dmcMealCard), ligne « Légume ajouté » dans la fiche recette (openRecipeFromMenu → window._kpMenuVeg dans openRecipe), ajouté à la liste de courses. Exception dietMode==='carnivore'. Backfill à la volée dans dmcMain pour les anciens menus (undefined → calcule + save). swapMeal recalcule.
- GÉNÉRATEUR CONTENU FACEBOOK v2 (style essenciel-content-wiz.lovable.app) : hero (« Ta semaine Facebook, générée en beauté »), grille de 7 cartes jour (KP_CW_THEMES : Lundi Mythe Kéto / Mardi Choix impossible / Mercredi Astuce Naturo / Jeudi Question à la communauté / Vendredi La recette commentée / Samedi La mission Kéto / Dimanche Inspiration & bien-être — alignés backend CONTENT_THEMES). Par jour : « Générer cette journée », « Régénérer le texte du post » (conserve les visuels via merge Firestore), « Générer le carré », « Générer la story ». Génération semaine = boucle kpContentGenerateDay + visuels si case « Visuels auto ».
- HISTORIQUE CONTENU : section « Historique des semaines générées » (client Firestore generated_content), « Voir » = consultation LECTURE SEULE avec bandeau « Archive · lecture seule » + bouton retour semaine en cours, suppression par semaine, « Vider l'historique » (batch delete). ANTI-RÉPÉTITION backend : generate-day lit les semaines passées et injecte les sujets déjà traités dans le prompt (à ne pas répéter).
- PROMPT VISUEL recalé sur la charte exacte des exemples client : crème #F7F2E8, vert forêt #1E3D2A, VERT ANIS #A9C83C (accents manuscrits/badge/doodles), photo lumineuse fondue, pilule calendrier jour-thème, titre serif condensé, note papier scotchée avec question manuscrite, ligne bénéfice soulignée. 7 COMPOSITIONS distinctes par thème (mythe démonté, duel VS, éditoriale, conversation, recette gourmande, polaroid mission, citation sereine). PEU de texte imposé. Testé en réel (gpt-image-1.5, clé OpenAI user) : rendu conforme.
- LOGIN MOBILE v2 : sans image, tient sur 1 écran (100dvh, espacements clamp/dvh, vérifié 667px et 844px = 0 scroll), en-tête compact, onglets pill iOS, champs arrondis focus vert, bouton dégradé. FIX : #authScreen{padding:0} dans la media query ~L6130 (l'ancien padding:14px créait 28px de scroll). Le CSS v2 est à ~L4248 (bloc « CONNEXION MOBILE v2 »).
- EMAILS (Resend, backend FastAPI — la Cloud Function welcomeOnSignup n'a jamais été déployée) : POST /api/notify (token Firebase user ; kind='signup' → send_welcome_email + notify_admin_new_signup ; kind='premium' → send_premium_email + notify_admin_new_subscriber(source)). Hooks frontend : authOnSuccess (isNewUser) → kpNotifyServer(user,'signup',…) ; activation code promo → kpNotifyServer(user,'premium',{source:'code promo X'}). Stripe webhook envoyait déjà les emails premium. SIGNATURE complète (EMAIL_SIGNATURE_HTML : Essenciel O Naturel — Marie-Cécile, site, email, Lunéville) ajoutée à la fin des emails. Testés réellement (reçus par l'admin).
- ADMIN « 🧑‍🤝‍🧑 INSCRITS » : GET /api/admin/users (_verify_admin) → firebase_auth.list_users() + croisement premium_emails → {email,name,created,last_login,provider,premium}. Panneau admin avec stats (total/7j/premium/Google-Email), recherche, badges. 17 inscrits au moment du test. NB : un bouton toolbar avait disparu lors d'une édition — re-vérifié présent dans keto.html ET backend/keto_app.html.
- MDP OUBLIÉ : fonctionne (sendPasswordResetEmail) — email arrivait en spam ; message amélioré (mention spams + cas Google).
- PENDING/BACKLOG : ~456 photos recettes IA (P2), Dark mode (P2), catégorie Pains Cétogènes DÉJÀ en place (PAIN_RECIPES ids 1300-1309 + onglet bibliothèque 🍞) — à confirmer avec l'utilisateur. KP_CONTENT_BASE et kpNotifyServer contiennent l'URL preview en dur pour l'usage hors emergentagent.com (à mettre à jour si fork/déploiement).

## Emails corrigés + Préparations détaillées pour TOUTES les recettes (fork, juillet 2026)
- SIGNATURE EMAIL corrigée : Patrice Raganelli (PAS Marie-Cécile), tél 06 58 83 86 41, 47 rue de la République 54300 Lunéville (EMAIL_SIGNATURE_HTML dans server.py, appendée à welcome + premium).
- PRÉPARATIONS DÉTAILLÉES : /api/recipe/detailed-steps accepte 'id' + CACHE GLOBAL Firestore 'recipe_details/{id}' (lecture avant OpenAI, écriture après). Frontend : openRecipe AUTO-charge la préparation détaillée (localStorage → sinon serveur, bouton masqué). BATCH /app/backend/batch_details.py exécuté : 474/474 recettes générées (gpt via OPENAI_TEXT_MODEL), 0 erreur → toutes les fiches affichent instantanément 6-10 étapes détaillées + astuce chef. Endpoint POST /api/recipe/dump (dump JSON → /tmp/recipes_dump.json) utilisé pour extraire les recettes du navigateur.
- Testé par testing_agent (iteration_9.json) : 7/7 backend, auto-génération UI vérifiée, cache <1s.

## Cadre nutritionnel complet appliqué au générateur de menus + recettes IA (fork, juillet 2026)
- CADRE FOURNI PAR L'UTILISATEUR intégré partout : glucides 20-30 g nets/j ; protéines 1,2-1,5 g/kg de poids (profile.weight, fallback 75 kg) sans excès ; poissons gras 2-3x/sem ; œufs 1-2/j max (interprété : max 1 repas à base d'œufs/j) ; légumes pauvres en glucides UNIQUEMENT en rotation ; graisses de qualité (olive/avocat/beurre/ghee/crème/olives) ; fruits limités aux BAIES 50-80 g max/j ; fruits à coque avec modération + OPTION D'EXCLUSION.
- MODULE QC ÉTENDU (keto.html, IIFE ~L15850-16450) : nouvelles constantes KPQ_BERRIES/KPQ_BAD_FRUITS/KPQ_HIGHCARB_VEG/KPQ_NUTS + kpqStripFalse (anti faux-positifs : noix de coco/st-jacques/muscade, tomates cerises, poireau, fleur d'oranger). Helpers : kpqDayProt, kpqProtRange, kpqIsEggMeal, kpqBerryGrams, kpqBadFruits, kpqHighCarbVeg, kpqHasNuts, kpNoNuts, kpqCleanCand, kpqHasProtType.
- ORDRE DES PASSES kpQualityFix (CRITIQUE, ne pas réordonner sans re-tester) : per-day (14j → prot qualité → carbs ≤30 → boostVeg → œufs → fruits → légumes interdits → noix → prot g/kg) → kpqFixFish() → passes FINALES : kpqFixEggs, kpqFixProt, kpqFixFish (re-check), plaisir (mkPlaisirPred protège protéines/œufs/fruits), boostVeg, kpqFixColors() (déplacé EN DERNIER car les swaps réinitialisent les accompagnements), boostVeg. Chaque fix a un RETRY sans contrainte 14 jours (prevIds=[]) si échec.
- kpqSwapIn filtre désormais TOUS les candidats : exclusion fruits à coque (si préférence), compatibilité dietMode via filterRecipesForMode([r],mode).
- EXCLUSION « Fruits à coque » : chip dans Réglages (buildExcludeGrid + EMOJI 🥜), filtre les pools BFAST/MAIN dans withFilteredRecipes (qui tourne maintenant AUSSI en mode standard si noNuts), + swap des entrées/desserts contenant des noix dans le QC, + critère dédié dans le rapport.
- RAPPORT kpWeekQuality : 14 critères (15 si noNuts) — ajoutés : protéines g/kg (moyenne/j), œufs modération, fruits=baies ≤80g, légumes pauvres en glucides only, fruits à coque exclus. Label huiles enrichi (crème).
- BACKEND server.py : constante KETO_FRAMEWORK (cadre complet en français) injectée dans les prompts systèmes : /api/recipe/detailed-steps + BRAND_VOICE des 2 endpoints contenu FB (generate-text, generate-day).
- TESTÉ : 20/20 générations consécutives = TOUS critères validés (evaluate dans page réelle). SYNC OBLIGATOIRE : cp /app/keto.html /app/backend/keto_app.html après chaque édition (c'est keto_app.html qui est servi).

## Emoji optionnel admin + préparations EN DUR + popup desktop + cible protéines (fork, juillet 2026)
- CIBLE PROTÉINES sur la fiche du jour : renderDayPanel affiche sous la tuile protéines « 🎯 cible X–Y g (1,2–1,5 g/kg · Zkg) » (vars _pw/protLo/protHi/protOk, couleur verte si dans la plage ±12g, ambre sinon).
- ADMIN INGRÉDIENTS : parseIng accepte désormais « quantité | nom » seul — emoji ET type optionnels dans n'importe quel ordre (détection type par mot-clé prot/fat/veg via kpGuessIngType, emoji deviné via kpGuessIngEmoji, fallback 🥄). Labels/placeholder des 2 formulaires (ajout #arIng + édition #erIng) mis à jour.
- PRÉPARATIONS DÉTAILLÉES EN DUR : script embarqué <script id="kpRecipeDetailsData"> → window.KP_RECIPE_DETAILS (474 entrées, ~860KB, fichier total 2.86MB). Consulté en PRIORITÉ par openRecipe (wrapper) et kpDetailSteps → 0 appel réseau pour les recettes intégrées ; fallback localStorage puis /api/recipe/detailed-steps conservé pour les recettes perso. Script de dump : /app/backend/dump_details.py (Firestore recipe_details → /tmp/recipe_details.json). ⚠️ INSERTION : le bloc doit être inséré avant le DERNIER </body> (il existe un '</body>' dans une string JS plus haut — bug corrigé via rindex).
- POPUP DESKTOP « menu du jour » : ≥1024px, setDayView('day') porte #daySheet dans <body> + body.day-modal-open → modale centrée (880px max, backdrop flouté, ✕ en haut à droite via .day-sheet-handle-wrap::after, anim dayModalIn). Fermeture : ✕, clic backdrop, touche Échap (listener keydown). Mobile <1024px inchangé (bottom-sheet). CSS bloc « POPUP centré (desktop) » après le bloc mobile ~L610.
- COMPTE DEMO RECRÉÉ : demo.keto.qa2026@gmail.com / DemoKeto2026! (l'ancien demo.keto.1782045313 est INVALIDE) — mis à jour dans /app/memory/test_credentials.md.
- Testé par testing_agent (iteration_10.json) : backend 8/8, frontend 10/10, aucun bug.

## Email fin d'essai + Tableau de bord Diabète + anti-cache (fork, juillet 2026)
- EMAIL FIN D'ESSAI (server.py) : send_trial_ended_email (relance premium, CTA vers KP_APP_URL, signature Patrice) + check_expired_trials() — scan premium_emails where plan=='trial', skip si trialEndEmailSent/source!='trial'/pas d'expires ; à expiration : envoie email, set {active:false, trialEndEmailSent:true, trialEndEmailAt}. Boucle asyncio @startup toutes les 6 h + endpoint manuel POST /api/admin/check-trials. TESTÉ : 1 vrai essai expiré relancé (sylvie.neimard@gmail.com), idempotent (2e appel = 0).
- ANTI-CACHE : _serve_html_with_base renvoie Cache-Control no-cache/no-store — corrige le « popup desktop ne fonctionne pas » (ancienne version en cache navigateur ; le popup a été VÉRIFIÉ fonctionnel en conditions réelles avec login + clic réel).
- ⚠️ INCIDENT server.py : une édition a dupliqué la fin du fichier (le tail depuis le prompt detailed-steps) → réparé par troncature ligne 1126 puis réinjection des fonctions trial. TOUJOURS vérifier `python3 -c "import ast; ast.parse(...)"` après édition de server.py.
- TABLEAU DE BORD DIABÈTE (keto.html) : section #diabeteSection dans l'onglet Suivi, visible UNIQUEMENT si profile.dietMode==='diabete' (kpDiabRender appelé par renderSuivi + applyDietMode). Composants :
  • 8 tuiles : glycémie actuelle, moyenne 7j, temps dans la cible (70-180 mg/dL), poids (weightLog), pas, eau, sommeil, humeur.
  • SCORE MÉTABOLIQUE /100 (kpDiabScore) : glycémie cible 30 (prorata mesures dans cible) + glucides 20 (checkbox carbsOk) + activité 15 (pas/8000) + sommeil 15 (7-9h=15, 6-10h=10, >0=5) + hydratation 10 (eau/2L) + humeur 10 (mood/5). Anneau SVG + barres de décomposition.
  • GRAPHIQUE canvas #diabChart : barres = score quotidien (vert/ambre/rouge), ligne terracotta = glycémie moyenne (axe droit 0-250), toggle Semaine/Mois (kpDiabSetRange).
  • SAISIE DU JOUR : 8 glycémies (jeun, post-pdj, av/post déj, av/post dîner, coucher, nocturne facultatif), traitement (médicaments, dose insuline UI, heure injection, oubli checkbox, effets secondaires), habitudes (pas, eau L, sommeil h, humeur 5 emojis kpDiabSetMood), glucides respectés. FUSION par jour (saisie progressive matin→soir, kpDiabSave merge sur date du jour).
  • Historique 7 journées avec score coloré + suppression (kpDiabDelete).
  • Stockage localStorage kp_diabete_v1__profileId + SYNC CLOUD (data.diabete dans syncProfileToCloud/FromCloud).
- TESTÉ via evaluate + screenshots desktop 1920 et mobile 390 : score 97/100 correct, tuiles, graphes 7j/30j, formulaire pré-rempli. NB : l'onglet Suivi entier est gaté Premium (overlay kp-suivi-overlay-wrap) — le mode diabète étant Premium, cohérent.
- ⚠️ TOOL GLITCH observé : sur keto.html (2.9MB), une édition « successful » peut ne pas persister — TOUJOURS vérifier par grep après une grosse insertion.

## Ascenseurs onglet Suivi (fork, juillet 2026)
- Classe .suivi-scroll (max-height:320px, overflow-y:auto, scrollbar fine thématisée + dark mode) appliquée à : #weightHistory, #wellnessHistory, #measuresHistory, #macroComplianceBody. Le tableau de bord Diabète (#diabeteSection) N'A PAS d'ascenseur (affichage complet, demande explicite). Section diabète toujours conditionnée à profile.dietMode==='diabete'.
- Testé : historique 31 poids → conteneur 320px scrollable (scrollHeight 1798), diabète masqué en mode standard.

## Accordéons onglet Suivi (fork, juillet 2026)
- kpInitSuiviAccordions() (appelé en fin de renderSuivi, idempotent via data-acc) : transforme en accordéons repliés par défaut les sections #macroComplianceSection, #wellnessSection, #measuresSection, #exportSection (id ajouté). Le .sec-label devient l'en-tête cliquable (chevron ::after animé), le contenu est déplacé dans .suivi-acc-body > .suivi-acc-inner (animation grid-template-rows 0fr→1fr).
- EXCLUS des accordéons (demande explicite) : tableau de bord Diabète (#diabeteSection) et toutes les sections perte de poids (Enregistrer mon poids, Courbe, Historique).
- Testé : 4 accordéons fermés par défaut, ouverture au clic (h 0→234px), diabète non-accordéon et affiché entier.

## Refonte visuelle onglet Suivi v2 (fork, juillet 2026)
- Bloc <style> « SUIVI v2 » scopé #tab-suivi en tête de l'onglet : héro de progression .sv-hero (dégradé vert sapin, poids serif 52px, chips ▼/▲ delta total + 7j, méta IMC/pesées/départ, feuille 🌿 en filigrane), titres de sections en petites capitales dorées avec filet dégradé (::after, seulement pour :not(.suivi-acc)), cartes 20px unifiées avec ombres douces, tuiles stats hover-lift serif, accordéons transformés en cartes-boutons (pastille chevron ronde verte), inputs focus ring vert, dark mode complet.
- JS kpRenderSuiviHero() (appelé en fin de renderSuivi) : calcule delta total, tendance 7j (pesée la plus récente ≥7j), IMC via profile.height ; état vide élégant « Commencez votre suivi 🌱 ».
- ⚠️ RÉCURRENCE TOOL GLITCH : 2e fois qu'une édition « successful » sur keto.html ne persiste pas (JS hero perdu, réappliqué). TOUJOURS grep après édition + resync cp vers backend/keto_app.html.

## Gating Premium du Suivi Diabète (fork, juillet 2026)
- #diabeteSection = classe suivi-premium-section + pill « Premium » dans le titre + contenu enveloppé dans .suivi-premium-wrap > .suivi-premium-content + .suivi-premium-overlay (🔒 Suivi Diabète Premium, CTA openPremiumModal('diabete')).
- 'diabeteSection' ajouté à la liste kpApplyPremiumGate (toggle .locked → flou + overlay). Double protection : mode diabète déjà premium-only + onglet Suivi entier gaté.
- ⚠️ 3e occurrence du TOOL GLITCH sur keto.html : l'édit d'ouverture (wrap) n'a pas persisté alors que la fermeture oui → DOM mal imbriqué (overlay hors section). Réappliqué + vérifié par evaluate (wrap:true, overlay display:flex, flou visible).

## Optimisation mobile onglet Suivi (fork, juillet 2026)
- Bloc @media(max-width:767px) dans le style « SUIVI v2 » : héro compact (42px), titres sections 10px/flex-wrap, cartes padding 16/14, score métabolique en colonne centrée (anneau + barres pleine largeur), tuiles diabète 2 colonnes fixes (19px), diab-grid 2 colonnes, champ Humeur en pleine largeur via :has(.diab-mood-row) + boutons emoji compacts (fin du débordement), accordéons 14px, bouton principal pleine largeur ≥46px, #diabChart 170px.
- Vérifié par screenshots 390px : héro, score, saisie, historique, accordéons tous lisibles.

## Corrections & ajouts (fork, juin/juillet 2026 — session courante)
- BUG texte de recettes en bas de page CORRIGÉ : keto.html contenait 2 fragments orphelins de payload recettes APRÈS le premier </html> (lignes ~27420 et ~27425, restes d'écritures partielles) + 2 blocs </script></body></html> dupliqués → rendus comme texte brut en bas de page. Fichier tronqué au premier </html> (27418 lignes). Payload KP_RECIPE_DETAILS principal validé (JSON OK, 474 recettes).
- Accordéon Suivi Diabète : #diabeteSection est désormais un accordéon (classe suivi-acc-diab, fermé par défaut). En-tête .sv-group-head cliquable (chevron ::after terracotta animé), .suivi-premium-wrap déplacé dans .suivi-acc-body > .suivi-acc-inner (même mécanique grid 0fr→1fr). Init dans kpInitSuiviAccordions (idempotent via data-acc).
- Règle d'affichage stricte Suivi Diabète : kpApplyPremiumGate force diabeteSection.style.display selon kpDiabIsActive() UNIQUEMENT (dietMode==='diabete'). Le Premium seul n'affiche JAMAIS la section. Vérifié par evaluate : display none en mode standard même avec isPremium()=true.
- Écran de connexion : ajout bloc .auth-focus sous la tagline — « Spécialement conçue pour » + 3 pastilles responsive (⚖️ Perte de poids · 🩸 Diabète · ⚡ Épilepsie), CSS @media ≤480px + dark mode. Vérifié par screenshot mobile 390px.
- ⚠️ 4e occurrence TOOL GLITCH keto.html : l'édit JS accordéon diabète « successful » n'a pas persisté (CSS oui) → réappliqué + grep + resync cp /app/keto.html → /app/backend/keto_app.html + restart backend.

## Questionnaire Diabète + Profil utilisateur (fork, session courante)
- Nouveau bloc #diabQuizOverlay (réutilise les classes .quiz-* du Bilan Keto) + IIFE juste avant le script kpRecipeDetailsData dans keto.html.
- 13 questions (Q10 = multi-sélection complications, « Aucune » exclusive). Réponses stockées profile.diabQuiz={answers,score,profil,complications,date} + save() + syncProfileToCloud.
- Lancement AUTO : applyDietMode('diabete') → setTimeout 600ms → openDiabQuiz() (skip si profile.diabQuiz.profil déjà présent ; openDiabQuiz(true) pour refaire). NB : peut apparaître avec ~1-2s de délai car generateMenu() bloque le thread.
- Calcul du profil (points de risque par option, complications plafonnées à 4, max ≈26) : 🔴 Prioritaire (score≥14 OU HbA1c>8% OU ≥2 complications, + encart suivi médical), 🟠 Métabolique Fragile (≥9), 🟡 À Optimiser (≥4), 🟢 Équilibré (<4). Exposé via window.KP_DIAB_PROFILES {emoji,name,color,bg,desc,advice,tips}.
- Écran résultat : emoji + nom du profil + description + 3 conseils personnalisés + encart médical (Prioritaire) + boutons ↺ Refaire / C'est parti.
- Tableau de bord Diabète (kpDiabRender → diabScoreWrap) : chip profil coloré + conseil (advice) + lien « Refaire le questionnaire » ; si non complété → CTA pointillé « 📋 Faire le questionnaire Diabète ».
- Testé par evaluate : flux 13 questions, multi Q10 [0,2], score 20 → Prioritaire, sauvegarde OK, chip 🟡 rendu OK, ouverture auto après applyDietMode OK (screenshot).

## Activation Premium instantanée + verrou Diabète renforcé (fork, session courante)
- kpRefreshUI enrichi (étape 2b) : appelle désormais aussi kpApplyPremiumGate + refreshTrialBanner + kpUpdateTrialCta + renderSuivi (si onglet suivi actif). Comme kpRefreshUI est déclenché par le listener Firestore temps réel (onSnapshot premium_emails), le watcher 5 min, l'essai et les codes promo → TOUTE activation/révocation Premium se propage instantanément à l'UI (sections Suivi déverrouillées, bannière essai masquée, teaser Premium retiré).
- kpStartTrial + kpRedeemPromoCode : activation OPTIMISTE immédiate après écriture Firestore réussie (kpState.premium=true + kpSaveCache + kpRefreshUI) sans attendre le round-trip kpCheckPremium (900/800ms), qui reste en confirmation.
- Verrou Suivi Diabète confirmé : kpApplyPremiumGate (appelé maintenant à chaque changement premium) force display selon kpDiabIsActive() uniquement. Testé par evaluate : premium ON + mode standard → diabète display:none ; mode diabète → block ; révocation → reverrouillage instantané.

## Gestion du poids GRATUITE dans l'onglet Suivi (fork, session courante)
- kpUpdateSuiviLock modifié : en version gratuite, le cadre #svGroupPoids (saisie poids + stats + courbe + historique) reste visible et fonctionnel (logWeight n'a aucun gate premium). Tout le reste (héro, conseil, bien-être, mesures, macros 30j, diabète, export) est masqué, avec le teaser Premium affiché APRÈS le cadre poids (copy mise à jour : « Allez plus loin dans votre suivi » listant les fonctionnalités Premium restantes). Les balises STYLE/SCRIPT enfants de #tab-suivi ne sont plus touchées.
- Testé par evaluate : gratuit → poids visible/bien-être caché/teaser présent ; premium → tout restauré/teaser retiré.

## Refonte saisie Diabète + Glycémie express enrichie (fork, session courante)
- KP_GLY_FIELDS réduit : retrait de postPdj/postDej/postDin (« 2h après petit-déj/déjeuner/dîner »). Restent : jeun, avDej, avDin, coucher, nuit. Pré-sélection horaire de la glycémie express adaptée (h<10 jeun, <14 avDej, <20 avDin, sinon coucher).
- Traitement (Saisie du jour) : diabMeds = nom du médicament + doses par moment diabMedsMatin/Midi/Soir (mg) ; insuline par moment diabInsMatin/Midi/Soir (UI). Champs diabInsulin/diabInjTime SUPPRIMÉS. Schéma entrée : {meds, medsDose:{matin,midi,soir}, insulin:{matin,midi,soir}} avec fusion par moment (Object.assign) dans kpDiabSave ; kpDiabFillForm adapté ; historique affiche totaux 💉 UI et 💊 nom + mg (rétro-compat insulinDose lue).
- Glycémie express (FAB 🩸) : ajout toggles « 💊 Médicament pris ? Oui/Non » (si oui → nom + valeur mg) et « 💉 Insuline ? Oui/Non » (si oui → valeur UI) via kpGlyQuickTgl. kpGlyQuickSave affecte les doses au créneau matin(<12h)/midi(<17h)/soir selon l'heure ; glycémie devenue optionnelle si méd/insuline renseigné ; reset des toggles à l'ouverture.
- applyDietMode : appel kpApplyPremiumGate ajouté après kpDiabRender (ceinture-bretelles disparition Suivi Diabète). Testé E2E par evaluate : champs OK, save {medsDose:{matin:1000},insulin:{soir:10}}, quick save fusion OK, changement de mode → display none + log purgé.
- ⚠️ TOOL GLITCH x2 encore (markup Glycémie express + kpDiabFillForm « successful » non persistés) → réappliqués (2e via python replace). TOUJOURS grep après chaque édition de keto.html.

## 🔴 DEUX CAUSES RACINES MAJEURES corrigées (fork, session courante)
1. TEXTE ORPHELIN EN BAS DE PAGE (récurrent) — CAUSE : l'outil d'édition fait des écritures IN-PLACE SANS TRONCATURE sur keto.html (fichier géant, ligne payload 878 Ko). Chaque édition qui RACCOURCIT le fichier laisse les derniers octets de l'ancienne version (fin du payload recettes + </script></body></html> dupliqués) → rendus comme texte brut en bas de page. FIX : script /app/fix_tail.py (tronque tout après le 1er </html> suivant le payload KP_RECIPE_DETAILS). ⚠️ RÈGLE OBLIGATOIRE : après CHAQUE édition de keto.html → `python3 /app/fix_tail.py && cp /app/keto.html /app/backend/keto_app.html && sudo supervisorctl restart backend`.
2. SUIVI DIABÈTE VISIBLE HORS MODE DIABÈTE (récurrent, signalé 3x par l'utilisateur) — CAUSE : kpUpdateSuiviLock (appelé à chaque confirmation Premium, dont CHAQUE chargement de page premium via kpRefreshUI) restaure TOUS les enfants de #tab-suivi avec style.removeProperty('display') → efface le display:none inline de #diabeteSection → section révélée même en mode standard. Reproduit via parcours réel (clic tuiles pmd-diabete/pmd-standard + transition free→premium). FIX : après la boucle de restauration, ré-application de la règle : diabeteSection.style.display selon kpDiabIsActive() uniquement (« RÈGLE ABSOLUE » dans le code). Testé : diabète→block, standard→none, transition free→premium→none.
- NB : le clic direct Playwright sur les tuiles échoue (overlays quiz/profil après login) → utiliser element.click() via evaluate + fermer .kp-cprofile-overlay et .quiz-overlay.open après login.

## Switches Traitement + Historique complet + Accès rapide Diabète (fork, session courante)
- Traitement (Saisie du jour) : switch Oui/Non « 💊 Médicament ? » (diabMedTglYes/No → #diabMedFields : nom + Matin/Midi/Soir mg) et « 💉 Insuline ? » (diabInsTglYes/No → #diabInsFields : Matin/Midi/Soir UI). kpDiabTgl(kind,val) global (état window._diabMedOn/_diabInsOn). kpDiabSave n'enregistre ces champs QUE si switch Oui (fusion du jour conserve l'existant). kpDiabFillForm ré-active automatiquement les switches si données présentes.
- Historique : kpDiabRenderHistory affiche le traitement détaillé par moment (💊 Nom — Matin X mg · Soir Y mg · 💉 Midi Z UI, rétro-compat insulinDose) + bouton « Voir tout l'historique (N) ↓ / Réduire ↑ » (kpDiabHistToggle, window._diabHistAll) au-delà de 7 journées.
- Accès rapide : carte « 🩸 Suivi Diabète » sur l'écran Plan (#planDiabQuickHost après planPremiumStatusHost, rendue par kpRenderDiabQuickCard dans renderPlan/kpDiabRender/kpGlyQuickSave). Affiche chip profil quiz + dernière glycémie + score/100 + boutons « Tableau de bord → » (kpOpenDiabDashboard : switchTab suivi + acc-open + scroll) et « 🩸 Glycémie » (kpGlyQuickOpen). Visible UNIQUEMENT si kpDiabIsActive().
- Testé par evaluate : switches, save conditionnel, fusion, auto-réactivation, historique détaillé, carte plan + disparition hors mode diabète.

## 💡 Conseil du jour personnalisé + Rappel glycémie (fork, session courante)
- kpDiabDailyAdvice() : moteur de conseils basé sur la glycémie, priorités : 1) hypo <70 aujourd'hui → alerte ; 2) série ≥2 jours 100% dans la cible (70-180) → « Félicitations ! Vous êtes dans votre cible depuis N jours » ; 3) jeun en hausse 3 jours consécutifs (>130) → dîner plus tôt + marche ; 4) valeurs du jour élevées (jeun>130 → 2 œufs/avocat au petit-déj ; avDej/avDin>150 → marche ; coucher/nuit>160 → dîner plus léger) ; 5) semaine ≥80% TIR → encouragement ; 6) aucune saisie → invitation ; 7) rotation quotidienne de 6 conseils naturopathiques (seed = jour epoch).
- kpDiabAdviceHTML() : carte dorée « 💡 CONSEIL DU JOUR » affichée dans le tableau de bord Diabète (fin de diabScoreWrap) ET dans la carte accès rapide du Plan.
- Rappel discret (kpRenderDiabQuickCard) : si glycémie attendue non saisie → bandeau ambre « ⏰ Pensez à saisir votre glycémie à jeun du matin » (h≥7 sans jeun ; 12-19h sans avDej ; ≥19h sans avDin).
- Testé : 5 cas du moteur validés + rappel + rendu sur Plan et dashboard.

## Quiz Diabète : Q4 & Q6 multi-sélection (fork, session courante)
- Q4 « Prenez-vous un traitement ? » et Q6 « Quel est votre objectif principal ? » → multi:true + sous-titre « Plusieurs réponses possibles ». Option exclusive générique via propriété none:index (Q4 none:0 « Aucun », Q10 none:6 « Aucune »). compCount (règle ≥2 complications → Prioritaire) désormais limité à la question marquée comp:true (Q10) pour ne pas compter les traitements/objectifs.
- Testé E2E : Q4 2 sélections + exclusivité Aucun, Q6 2 sélections, parcours complet → Profil À Optimiser score 7, complications 0.

## Pré-remplissage Traitement depuis Q4 du quiz (fork, session courante)
- kpDiabPrefillFromQuiz() (appelée dans kpDiabRender après kpDiabFillForm) : lit profile.diabQuiz.answers[3] (Q4 traitement, tableau multi OU nombre legacy). Comprimés(1)/Comprimés+insuline(3)/GLP-1(4) → switch Médicament ON ; Insuline(2)/(3) → switch Insuline ON ; Aucun(0) → rien. N'active que si le switch n'est pas déjà ON (jamais de désactivation forcée).
- Testé : [1,2]→2 switches ON+champs visibles ; [0]→OFF ; legacy 3→2 ON.

## Popup de confirmation quitter le mode Diabète (fork, session courante)
- applyDietMode : si dietMode courant='diabete' et cible≠diabete et !window._kpDiabSwitchOk → kpShowDiabSwitchConfirm(cible) + return (mode inchangé, données intactes).
- Popup #diabSwitchConfirm (z-index 100001) : « Quitter le mode Diabète ? » + avertissement suppression définitive (glycémies, traitements, journées, questionnaire). Boutons : « Non, je reste en mode Diabète » (kpDiabSwitchCancel → ferme + re-render grille) / « Oui, je continue — supprimer l'historique » (kpDiabSwitchConfirmYes → _kpDiabSwitchOk=true → applyDietMode → purge existante).
- ⚠️ TOOL GLITCH encore (gros bloc « successful » non persisté + 2643 octets orphelins) → réappliqué via python replace + node --check + fix_tail. RÈGLE : pour tout ajout >20 lignes dans keto.html, préférer python replace et TOUJOURS grep + fix_tail après.
- Testé E2E : popup, Non (données conservées), Oui (purge + section masquée).

## Saisie du jour Diabète → carrousel 3 étapes + curseurs (fork, session courante)
- Carrousel horizontal (choix utilisateur confirmé) : Étape 1 🩸 Glycémies → Étape 2 💊 Traitement → Étape 3 🌿 Hygiène de vie. Onglets cliquables (#diabWizTabs), points de progression (#diabWizDots), nav Précédent/Suivant (kpDiabWizGo, translateX sur .diab-wiz-track width:300%), bouton « + Enregistrer ma journée » toujours visible (fusion partielle par étape OK).
- Curseurs + champ clavier synchronisés (choix : tout sauf doses) : glycémies (40-300, généré dans kpDiabBuildForm : diabGlyS_*), pas (0-20000), eau (0-4 L), sommeil (0-12 h) via kpDiabSlide/kpDiabSlideSync. Sémantique « non saisi » préservée : le curseur ne remplit le champ QUE sur interaction. kpDiabFillForm resynchronise les curseurs. Doses médicament/insuline restent au clavier.
- 🔧 2 bugs layout corrigés : (1) .diab-wiz-tab flex sans min-width:0 + nowrap → débordement horizontal page ; (2) .suivi-acc-body display:grid sans grid-template-columns:minmax(0,1fr) → la colonne s'élargissait au min-content du track 300% (carte plus large que l'écran, champs numériques hors écran). Fix : minmax(0,1fr) + min-width:0 sur .suivi-acc-inner.
- Script /app/apply_wizard.py conservé (référence). Testé : E2E evaluate (sync bidirectionnelle, save multi-étapes, refill) + captures visuelles connectées 390px des 3 étapes.

## Popup « Saisie du jour » Diabète (fork, session courante)
- La carte Saisie du jour du tableau de bord ne contient plus que : bouton « ✍️ Saisie du jour » (kpDiabEntryOpen) + #diabHistory.
- Le carrousel 3 étapes + curseurs est déplacé dans #diabEntryOverlay (popup fixed z-index 100000, re-parenté sur body à l'ouverture, fermeture par ×, clic fond, ou après enregistrement).
- kpDiabEntryReset() : vide tous les champs (glycémies, nom/doses méd, insuline, effets, pas, eau, sommeil), curseurs remis aux défauts (gly 110 / pas 6000 / eau 1.5 / sommeil 7), switches sur Non, checkboxes décochées, humeur effacée. Appelé à l'OUVERTURE (toujours des valeurs vierges) et après kpDiabSave (qui ferme aussi le popup). La fusion par jour dans kpDiabSave permet plusieurs saisies/jour.
- Scripts /app/apply_entry_popup.py (référence). Testé E2E : ouverture à zéro, save (jeun 135/steps 8000), fermeture auto, réouverture à zéro + capture visuelle du popup.

## Bouton « Ajouter ma journée » sur carte Plan + vérif desktop (fork, session courante)
- Carte Suivi Diabète (Plan) : « Tableau de bord → » remplacé par « ✍️ Ajouter ma journée » (kpDiabEntryOpen). kpDiabEntryOpen appelle désormais kpDiabBuildForm() (construit la grille glycémies si le tableau de bord Suivi n'a jamais été rendu — cas ouverture directe depuis le Plan). kpOpenDiabDashboard conservé (non utilisé sur la carte).
- ⚠️ TOOL GLITCH récurrent : édition bouton « successful » non persistée → réappliquée via python. BILAN de session : ~6 éditions perdues, TOUJOURS grep après search_replace sur keto.html, python replace pour tout bloc critique.
- Écran noir desktop signalé par l'utilisateur : NON REPRODUIT sur preview (testé 1920x800 : landing, login, app connectée, carte diabète, popup saisie — tous OK, aucun overlay fantôme). Hypothèses : rechargement pendant restart backend, ou version publiée/hébergée obsolète. À re-vérifier avec l'utilisateur (quelle page/action exacte).

## Bouton « Saisir ma journée » + diagnostic écran noir (fork, session courante)
- Carte Plan Diabète : « Ajouter ma journée » → « ✍️ Saisir ma journée ». Texte adapté au bouton : une règle .btn avec letter-spacing .22em !important + uppercase écrasait les styles inline → contré avec inline !important (font-size:11px, letter-spacing:.05em, gap:5px, padding 5px). Vérifié : scrollWidth<=clientWidth sur les 2 boutons à 390px.
- ÉCRAN NOIR DESKTOP élucidé : la capture utilisateur montre le MODE SOMBRE actif (toggle 🌙 #themeToggle, localStorage 'keto-dark'='1', body.dark). Le dark mode existe (152 règles body.dark) mais est INCOMPLET sur desktop : fond quasi noir, certaines cartes restent claires, texte « Recette du jour » illisible. = Tâche P2 « Finaliser le Mode sombre ». Pas d'auto-activation système (uniquement via toggle). AUSSI : le pod a redémarré en cours de session (502 temporaire) — peut causer un écran noir/blanc passager.

## Onglet « Parcours » — Formation Diabète 12 modules (fork, juin 2026)
- Nouveau module isolé `<script id="kpParcoursModule">` injecté avant le payload recettes via /app/apply_parcours.py (source : /app/parcours_module.html, idempotent via marqueurs KP-PARCOURS-START/END). AUCUNE modification du HTML existant : l'onglet #tab-parcours, le bouton nav #nt-parcours, le CSS et le wrapper switchTab sont créés dynamiquement en JS.
- Contenu : 12 modules / 59 chapitres (curriculum complet fourni par l'utilisateur), chaque chapitre = 2-4 pages de contenu FR + quiz 2-3 questions + missions (ch.1 : bilan de départ). Design fidèle à l'image de référence : héro teal avec anneau de progression (conic-gradient), cartes chapitres numérotées ✓/🔒, quiz A/B/C avec feedback vert/rouge + explication, écran Félicitations sombre (score, +50 pts, progression module).
- Déverrouillage séquentiel : chapitre n+1 après chapitre n ; module n+1 quand module n = 100 %. Toast 🔒 sinon.
- Progression sauvegardée dans profile.diabParcours {done:{'mi-ci':{s,ts}}, pts} → save() (localStorage) + syncProfileToCloud() (Firestore users/{uid}/ketoProfile/data) — +50 pts une seule fois par chapitre.
- Remplacement Compléments : pcNavSync (interval 1,5 s) → si kpDiabIsActive() : #nt-parcours visible, #nt-lpev + #lpevPlanCard masqués (setProperty !important pour contrer le CSS !important existant) ; sinon inverse + retour auto sur Plan si on quitte le mode diabète pendant que Parcours est ouvert.
- Testé E2E (compte démo, viewport 390px) : nav flex/none OK, home (héro + 11 cartes + stats 0/59), verrouillage chapitre 3 bloqué, lecture 3 pages, quiz 2/2, congrats +50 pts, done['0-0'] persisté, chapitre 2 déverrouillé. fix_tail OK (aucun octet orphelin), backend synchronisé.
