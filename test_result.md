#====================================================================================================
# START - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================

# THIS SECTION CONTAINS CRITICAL TESTING INSTRUCTIONS FOR BOTH AGENTS
# BOTH MAIN_AGENT AND TESTING_AGENT MUST PRESERVE THIS ENTIRE BLOCK

# Communication Protocol:
# If the `testing_agent` is available, main agent should delegate all testing tasks to it.
#
# You have access to a file called `test_result.md`. This file contains the complete testing state
# and history, and is the primary means of communication between main and the testing agent.
#
# Main and testing agents must follow this exact format to maintain testing data. 
# The testing data must be entered in yaml format Below is the data structure:
# 
## user_problem_statement: {problem_statement}
## backend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.py"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## frontend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.js"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## metadata:
##   created_by: "main_agent"
##   version: "1.0"
##   test_sequence: 0
##   run_ui: false
##
## test_plan:
##   current_focus:
##     - "Task name 1"
##     - "Task name 2"
##   stuck_tasks:
##     - "Task name with persistent issues"
##   test_all: false
##   test_priority: "high_first"  # or "sequential" or "stuck_first"
##
## agent_communication:
##     -agent: "main"  # or "testing" or "user"
##     -message: "Communication message between agents"

# Protocol Guidelines for Main agent
#
# 1. Update Test Result File Before Testing:
#    - Main agent must always update the `test_result.md` file before calling the testing agent
#    - Add implementation details to the status_history
#    - Set `needs_retesting` to true for tasks that need testing
#    - Update the `test_plan` section to guide testing priorities
#    - Add a message to `agent_communication` explaining what you've done
#
# 2. Incorporate User Feedback:
#    - When a user provides feedback that something is or isn't working, add this information to the relevant task's status_history
#    - Update the working status based on user feedback
#    - If a user reports an issue with a task that was marked as working, increment the stuck_count
#    - Whenever user reports issue in the app, if we have testing agent and task_result.md file so find the appropriate task for that and append in status_history of that task to contain the user concern and problem as well 
#
# 3. Track Stuck Tasks:
#    - Monitor which tasks have high stuck_count values or where you are fixing same issue again and again, analyze that when you read task_result.md
#    - For persistent issues, use websearch tool to find solutions
#    - Pay special attention to tasks in the stuck_tasks list
#    - When you fix an issue with a stuck task, don't reset the stuck_count until the testing agent confirms it's working
#
# 4. Provide Context to Testing Agent:
#    - When calling the testing agent, provide clear instructions about:
#      - Which tasks need testing (reference the test_plan)
#      - Any authentication details or configuration needed
#      - Specific test scenarios to focus on
#      - Any known issues or edge cases to verify
#
# 5. Call the testing agent with specific instructions referring to test_result.md
#
# IMPORTANT: Main agent must ALWAYS update test_result.md BEFORE calling the testing agent, as it relies on this file to understand what to test next.

#====================================================================================================
# END - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================



#====================================================================================================
# Testing Data - Main Agent and testing sub agent both should log testing data below this section
#====================================================================================================
## Test Session — Existing-user login bypasses onboarding picker (June 2026)

### Change implemented
- File: /app/keto.html (also copied to /app/backend/keto_app.html served at /api/app)
- In appBoot() -> launch() (existing-account branch): a LOGGED-IN user (currentUser set) now ALWAYS enters the app directly (switchTab('plan')). The legacy welcome/picker screen ("Créer un nouveau profil / Choisir un profil existant / Récupérer depuis le cloud", id=obWelcomeScreen inside #obOverlay) is NO LONGER shown after login.
- Guests (mode local, no currentUser) with NO local profile still see the welcome screen (onboarding preserved).

### Needs testing (frontend, web)
- Test URL: <EXPO_PUBLIC_BACKEND_URL>/api/app  (standalone HTML app)
- Scenario A (MAIN FIX): Register a brand-new account (email+password) -> complete the 7-step wizard minimally -> then LOG OUT (Profil tab -> Déconnexion) -> LOG IN again with the same credentials. EXPECTED: after login the user lands DIRECTLY on the Plan tab. The welcome/picker screen (obWelcomeScreen) must NOT appear.
- Scenario B (regression): "Continuer sans compte (mode local)" as a fresh guest should STILL show the welcome screen with the 3 options.
- needs_retesting: true

#====================================================================================================
## Test Session — Sidebar redesign + Plan content beautification + 2-col desktop + mobile buttons (June 2026)
#====================================================================================================

user_problem_statement: |
  Standalone HTML app (keto.html, also copied to backend/keto_app.html served at /api/app).
  Recent changes to validate (FRONTEND / WEB only — no backend changes):
  1. Desktop left sidebar redesign: light sage/cream panel, brand block ("Keto Premium / ESSENCIEL O NATUREL / Le keto sans effort, par un naturopathe"), avocado logo badge, "MENU" section label, fine line icons (mask SVG), active tab = green pill + white text + left accent bar, hover micro-animation, "Découvrir Premium" gold CTA, mini-profile card (avatar + name).
  2. Premium/Free status badge under the title in sidebar: shows "Version Gratuite" (green) or "Version Premium" (gold). When user is Premium, the "Découvrir Premium" CTA must be HIDDEN. Updates in real-time via kpRefreshUI() (Firestore listener hook).
  3. On login, app goes directly to Plan tab and scrolls to top (switchTab now scrolls to top on every tab change).
  4. Plan content beautification (desktop): rounded cards + soft shadows + hover lift, sticky action toolbar (.plan-topbar), premium progress card, recipe grid hover zoom, welcome header with today's date (#kpHeroDate), comfortable reading column.
  5. Desktop 2-column Plan layout: #tab-plan is CSS grid (main + 336px right rail #planRail). JS function kpSyncPlanRail() moves "Recette du jour" (#recipeOfDayCard) + Quiz banner (#quizPromoBanner) into the sticky right rail on desktop (>=1024px) and restores them into the main flow on mobile/resize.
  6. Mobile Plan top buttons: .plan-topbar is a 2-column grid -> row1 = "Générer la semaine" + "Courses"; the other smaller buttons (PDF, export, etc.) flow on the lines below. The right rail (#planRail) must be HIDDEN on mobile and recipe/quiz must appear in the normal single-column flow.

frontend:
  - task: "Desktop sidebar redesign + premium status badge + CTA hide when premium"
    implemented: true
    working: "NA"
    file: "/app/keto.html"
    needs_retesting: true
    priority: "high"
  - task: "Login -> Plan tab + scroll to top; tab navigation still works"
    implemented: true
    working: "NA"
    file: "/app/keto.html"
    needs_retesting: true
    priority: "high"
  - task: "Desktop 2-column Plan layout with sticky right rail (Recette du jour + Quiz)"
    implemented: true
    working: "NA"
    file: "/app/keto.html"
    needs_retesting: true
    priority: "high"
  - task: "Mobile Plan top buttons (Générer + Courses on row 1, others below) + rail hidden on mobile"
    implemented: true
    working: "NA"
    file: "/app/keto.html"
    needs_retesting: true
    priority: "high"
  - task: "Generate menu still works (renderPlan/weekGrid) with new structure"
    implemented: true
    working: "NA"
    file: "/app/keto.html"
    needs_retesting: true
    priority: "high"

metadata:
  test_sequence: 1
  run_ui: true

test_plan:
  current_focus:
    - "Desktop 2-column Plan layout with sticky right rail (Recette du jour + Quiz)"
    - "Mobile Plan top buttons (Générer + Courses on row 1, others below) + rail hidden on mobile"
    - "Desktop sidebar redesign + premium status badge + CTA hide when premium"
    - "Login -> Plan tab + scroll to top; tab navigation still works"
    - "Generate menu still works with new structure"
  test_all: false
  test_priority: "high_first"

agent_communication:
    -agent: "main"
    -message: |
      Test URL: <EXPO_PUBLIC_BACKEND_URL>/api/app (standalone HTML, NOT an expo screen).
      Easiest entry: on the auth screen, click "Continuer sans compte (mode local)" OR call window.authGuest() to enter as guest, OR login with demo account (see /app/memory/test_credentials.md: demo.keto.1782045313@gmail.com / DemoKeto2026!).
      DESKTOP tests (viewport width >= 1024, e.g. 1440x950):
        - Left sidebar shows light panel + "Keto Premium" brand + avocado logo + "Version Gratuite" badge under the title + MENU label + 4 tabs with line icons + gold "Découvrir Premium" CTA + mini-profile card. Active tab = green pill with white text + left white accent bar.
        - Click each tab (Plan/Recettes/Suivi/Profil): content switches, page scrolls to top, active tab highlight moves.
        - Plan tab: must be a 2-COLUMN layout. Right rail (#planRail) contains "Recette du jour" card + Quiz banner; main column has progression card, plan card, action toolbar, planning.
        - Force premium to verify badge+CTA: run window.kpState={...window.kpState,premium:true}; refreshHeaderLogout(); -> badge becomes "Version Premium" (gold) AND the "Découvrir Premium" CTA disappears.
        - Click "Générer la semaine" (or run generateMenu()): week plan renders without breaking the 2-column layout; rail still intact.
      MOBILE tests (viewport 390x844):
        - Sidebar is NOT shown; bottom pill nav with emoji icons is shown instead.
        - Plan tab top buttons: "GÉNÉRER LA SEMAINE" and "COURSES" alone on the first row (side by side), other smaller buttons (PDF/export icons) on the rows below.
        - The right rail (#planRail) is hidden; "Recette du jour" and Quiz appear in the normal single-column flow.
      NOTE: This app uses Firebase (client-side) + dynamic JS injection. There are NO backend API changes. Only test FRONTEND/WEB behavior. Ignore Firebase network warnings in guest/local mode.
      needs_retesting: true
