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
- Comme la déconnexion n'est plus automatique, le bouton manuel #profileLogoutZone est RÉAFFICHÉ : renderProfileIdentity met display='' (au lieu de 'none'), et retrait de .profile-logout-zone de la règle @media(max-width:1023px){display:none!important} (ligne 625). Les entrées nav #nt-logout/.bnav-logout/#headerLogoutBtn restent masquées sur mobile (déconnexion via Profil). Vérifié : bg simulé = pas de logout, bouton "Se déconnecter" visible dans Profil, 0 erreur.
