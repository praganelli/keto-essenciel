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
