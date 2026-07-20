#!/usr/bin/env python3
# Refonte écran de connexion — mockup "Bienvenue !" + nouveau logo keto-Essenciel
import io, base64, sys

PATH = '/app/keto.html'
src = io.open(PATH, encoding='utf-8').read()

logo_b64 = base64.b64encode(open('/tmp/logo_t.webp', 'rb').read()).decode()
LOGO = 'data:image/webp;base64,' + logo_b64


def rep(old, new, label):
    global src
    if old not in src:
        print('MISSING:', label); sys.exit(1)
    if src.count(old) != 1:
        print('NOT UNIQUE:', label, src.count(old)); sys.exit(1)
    src = src.replace(old, new)
    print('OK:', label)


# ── R1 : bloc logo (SVG avocat + brand + tagline + pills) → nouveau logo image ──
start = '    <!-- Logo -->\n    <div class="auth-logo">'
end = '    <!-- Firebase config banner'
i = src.index(start); j = src.index(end)
new_logo = '''    <!-- Logo -->
    <div class="auth-logo">
      <div class="kpl-lang" aria-hidden="true">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="9"/><path d="M3.6 9h16.8M3.6 15h16.8M12 3a15 15 0 0 1 0 18M12 3a15 15 0 0 0 0 18"/></svg>
        Français
        <span class="kpl-lang-chev">⌄</span>
      </div>
      <img class="kpl-logo" src="''' + LOGO + '''" alt="keto-Essenciel — Simple · Naturel · Essentiel" draggable="false">
    </div>

'''
src = src[:i] + new_logo + src[j:]
print('OK: R1 logo')

# ── R2 : formulaire de connexion ──
start = '    <!-- ── CONNEXION ── -->'
end = '    <!-- ── CRÉER UN COMPTE ── -->'
i = src.index(start); j = src.index(end)
new_login = '''    <!-- ── CONNEXION ── -->
    <div id="authLoginForm">
      <div class="kpl-welcome">
        <h1 class="kpl-title">Bienvenue ! <span class="kpl-title-leaf" aria-hidden="true">🌿</span></h1>
        <p class="kpl-subtitle">Connectez-vous pour accéder à<br>votre espace personnel</p>
      </div>

      <div class="kpl-inputs">
        <div class="kpl-row" onclick="var i=this.querySelector('input'); if(i&&event.target!==i)i.focus();">
          <svg class="kpl-ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="3" y="5" width="18" height="14" rx="2.5"/><path d="m4 7 8 6 8-6"/></svg>
          <input type="email" id="loginEmail" placeholder="Adresse e-mail" autocomplete="email" data-testid="login-email">
        </div>
        <div class="kpl-row-sep"></div>
        <div class="kpl-row" onclick="var i=this.querySelector('input'); if(i&&event.target!==i&&!event.target.closest('.kpl-eye'))i.focus();">
          <svg class="kpl-ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="5" y="10.5" width="14" height="9.5" rx="2.5"/><path d="M8 10.5V7.5a4 4 0 0 1 8 0v3"/><circle cx="12" cy="15.2" r="1.3" fill="currentColor" stroke="none"/></svg>
          <input type="password" id="loginPassword" placeholder="Mot de passe" autocomplete="current-password" data-testid="login-password">
          <button type="button" class="kpl-eye" onclick="kpTogglePwd(event)" aria-label="Afficher le mot de passe" data-testid="login-eye">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M2.5 12S6 5.5 12 5.5 21.5 12 21.5 12 18 18.5 12 18.5 2.5 12 2.5 12Z"/><circle cx="12" cy="12" r="3"/></svg>
          </button>
        </div>
      </div>

      <div class="kpl-remember-row">
        <label class="kpl-remember" for="kplRemember">
          <input type="checkbox" id="kplRemember" checked data-testid="login-remember">
          <span>Se souvenir de moi</span>
        </label>
        <a class="kpl-forgot" onclick="openReset()" data-testid="login-forgot">Mot de passe oublié ?</a>
      </div>

      <button class="kpl-btn-login" id="btnLogin" onclick="authLogin()" data-testid="login-submit">
        <span>Se connecter</span>
        <span class="kpl-btn-arrow" aria-hidden="true">→</span>
      </button>

      <div class="kpl-divider"><span>ou</span></div>

      <button class="kpl-btn-google" id="btnGoogle" onclick="authGoogle()" data-testid="login-google">
        <svg viewBox="0 0 48 48"><path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/><path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/><path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/><path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.18 1.48-4.97 2.29-8.16 2.29-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/><path fill="none" d="M0 0h48v48H0z"/></svg>
        Continuer avec Google
      </button>

      <button type="button" class="kpl-signup-card" onclick="authSwitchTab('register')" data-testid="auth-goto-register">
        <span class="kpl-signup-ico">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="11" cy="8" r="3.6"/><path d="M4.5 19.5c0-3.3 2.9-5.5 6.5-5.5 1 0 2 .17 2.8.5"/><circle cx="17.6" cy="17.6" r="3.4" fill="#4e7a36" stroke="none"/><path d="M17.6 16v3.2M16 17.6h3.2" stroke="#fff" stroke-width="1.5"/></svg>
        </span>
        <span class="kpl-signup-txt">
          <span class="kpl-signup-q">Vous n'avez pas encore de compte ?</span>
          <span class="kpl-signup-cta">S'inscrire (Gratuit)</span>
        </span>
        <span class="kpl-signup-arrow" aria-hidden="true">→</span>
      </button>

      <div class="kpl-secure" data-testid="login-secure">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M12 3 5 5.8v5.4c0 4.4 3 8 7 9.8 4-1.8 7-5.4 7-9.8V5.8L12 3Z"/><path d="m9.2 12 2 2 3.6-4"/></svg>
        Vos données sont sécurisées
      </div>
    </div>

'''
src = src[:i] + new_login + src[j:]
print('OK: R2 login form')

# ── R3 : lien retour connexion en tête du formulaire d'inscription ──
rep('''    <div id="authRegisterForm" style="display:none">
      <!-- Stepper indicator -->''',
    '''    <div id="authRegisterForm" style="display:none">
      <button type="button" class="kpl-back-login" onclick="authSwitchTab('login')" data-testid="auth-goto-login">← J'ai déjà un compte — me connecter</button>
      <!-- Stepper indicator -->''',
    'R3 back-to-login')

# ── R4 : footer simplifié (invité conservé, discret) ──
start = '''    <!-- Mode invité -->
    <button class="auth-guest-btn" onclick="authGuest()">Continuer sans compte (mode local)</button>'''
end_marker = '''    <div class="auth-footer auth-coordinates" data-testid="auth-coordinates">
      <div class="auth-coord-brand">🌿 Essenciel <em>O Naturel</em></div>
      <div class="auth-coord-tag">Naturopathie · Phytothérapie · Keto</div>
      <div>
        <a class="auth-coord-link auth-coord-row" href="mailto:infos@essencielonaturel.fr" data-testid="auth-coord-mail">infos@essencielonaturel.fr</a>
        <span class="auth-coord-row auth-coord-loc">Lunéville, France</span>
      </div>
      <div class="auth-coord-mini">Vos données restent privées et sécurisées</div>
    </div>'''
rep(start + '\n\n' + end_marker,
    '''    <!-- Mode invité -->
    <button class="auth-guest-btn kpl-guest" onclick="authGuest()">Continuer sans compte (mode local)</button>

    <div class="auth-footer auth-coordinates kpl-foot" data-testid="auth-coordinates">
      <a class="auth-coord-link" href="mailto:infos@essencielonaturel.fr" data-testid="auth-coord-mail">🌿 Essenciel O Naturel · infos@essencielonaturel.fr</a>
    </div>''',
    'R4 footer')

# ── R5 : styles kpl (insérés après la fin d'authScreen → gagnent la cascade) ──
rep('<!-- ══ fin authScreen ══ -->',
    '''<!-- ══ fin authScreen ══ -->
<style id="kplAuthStyles">
/* ═══ CONNEXION v3 — mockup "Bienvenue !" ═══ */
#authScreen .auth-tabs{display:none !important}
#authScreen{background:#f7f5ec !important}
#authScreen .auth-card{
  background:
    radial-gradient(46% 22% at 100% 0%, rgba(163,190,140,.26) 0%, transparent 72%),
    radial-gradient(40% 18% at 0% 26%, rgba(163,190,140,.16) 0%, transparent 70%),
    radial-gradient(52% 20% at 62% 100%, rgba(163,190,140,.22) 0%, transparent 72%),
    #f8f6ee !important;
}
@media (max-width:980px){
  #authScreen .auth-card{ min-height:100dvh; }
}
/* Pastille langue */
.kpl-lang{
  position:absolute; top:calc(12px + env(safe-area-inset-top)); right:16px;
  display:inline-flex; align-items:center; gap:7px;
  background:#fff; border:1px solid rgba(30,42,30,.08); border-radius:99px;
  padding:8px 14px; z-index:6;
  font-family:'Plus Jakarta Sans',sans-serif; font-size:13px; font-weight:600; color:#2c342c;
  box-shadow:0 6px 18px -10px rgba(30,42,30,.25);
  user-select:none; cursor:default;
}
.kpl-lang svg{width:17px;height:17px;color:#4e7a36}
.kpl-lang-chev{font-size:12px;color:#8a9086;margin-top:-4px}
/* Logo */
#authScreen .auth-card .auth-logo{ text-align:center !important; margin-top:calc(30px + env(safe-area-inset-top)) !important; margin-bottom:6px !important; position:relative; }
.kpl-logo{ width:clamp(210px, 52vw, 285px); max-width:100%; height:auto; display:block; margin:0 auto; filter:drop-shadow(0 8px 22px rgba(46,74,34,.14)); }
@media (min-width:981px){ #authScreen .auth-card .auth-logo{ margin-top:5vh !important; } .kpl-lang{ position:absolute; } }
/* Bienvenue */
.kpl-welcome{ text-align:center; margin:14px 0 20px; }
.kpl-title{ font-family:'Plus Jakarta Sans',sans-serif; font-size:31px; font-weight:800; letter-spacing:-.02em; color:#3f7d3a; margin:0 0 8px; }
.kpl-title-leaf{ font-size:24px; }
.kpl-subtitle{ font-family:'Plus Jakarta Sans',sans-serif; font-size:15.5px; line-height:1.45; color:#5c645a; margin:0; }
/* Carte inputs */
.kpl-inputs{
  background:#fff; border:1px solid rgba(30,42,30,.05); border-radius:22px;
  padding:4px 18px; box-shadow:0 14px 34px -20px rgba(30,42,30,.28);
}
.kpl-row{ display:flex; align-items:center; gap:13px; padding:17px 2px; cursor:text; }
.kpl-row-sep{ height:1px; background:rgba(30,42,30,.07); margin:0 2px; }
.kpl-ico{ width:22px; height:22px; color:#4e7a36; flex-shrink:0; }
.kpl-row input{
  flex:1; min-width:0; border:none; outline:none; background:transparent;
  font-family:'Plus Jakarta Sans',sans-serif; font-size:16px; color:#232b22;
  padding:0; box-shadow:none;
}
.kpl-row input::placeholder{ color:#8a9086; font-weight:500; }
.kpl-eye{ background:none; border:none; padding:4px; cursor:pointer; color:#4e7a36; display:flex; }
.kpl-eye svg{ width:22px; height:22px; }
.kpl-eye.kpl-eye-on{ color:#2e5424; }
/* Se souvenir / oublié */
.kpl-remember-row{ display:flex; align-items:center; justify-content:space-between; gap:10px; margin:15px 2px 18px; flex-wrap:wrap; }
.kpl-remember{ display:inline-flex; align-items:center; gap:9px; font-family:'Plus Jakarta Sans',sans-serif; font-size:14px; font-weight:600; color:#2c342c; cursor:pointer; }
.kpl-remember input{ width:19px; height:19px; accent-color:#4e7a36; cursor:pointer; margin:0; }
.kpl-forgot{ font-family:'Plus Jakarta Sans',sans-serif; font-size:14px; font-weight:700; color:#3f7d3a; cursor:pointer; text-decoration:none; }
.kpl-forgot:hover{ text-decoration:underline; }
/* Bouton Se connecter */
.kpl-btn-login{
  position:relative; width:100%; border:none; cursor:pointer;
  background:linear-gradient(135deg,#5b8a40,#436c2c);
  color:#fff; border-radius:99px; padding:17px 52px;
  font-family:'Plus Jakarta Sans',sans-serif; font-size:17px; font-weight:700; letter-spacing:.01em;
  box-shadow:0 14px 26px -12px rgba(67,108,44,.55), inset 0 1px 0 rgba(255,255,255,.18);
  display:flex; align-items:center; justify-content:center;
  transition:transform .2s ease, filter .2s ease;
}
.kpl-btn-login:hover{ filter:brightness(1.06); transform:translateY(-1px); }
.kpl-btn-login:active{ transform:scale(.98); }
.kpl-btn-login:disabled{ opacity:.6; cursor:not-allowed; }
.kpl-btn-arrow{ position:absolute; right:22px; top:50%; transform:translateY(-50%); font-size:19px; }
.kpl-btn-login .auth-spinner{ width:20px; height:20px; border:2px solid rgba(255,255,255,.35); border-top-color:#fff; border-radius:50%; animation:spin .7s linear infinite; }
/* Divider */
.kpl-divider{ display:flex; align-items:center; gap:14px; margin:16px 0; color:#6b7266; font-family:'Plus Jakarta Sans',sans-serif; font-size:13.5px; font-weight:600; }
.kpl-divider::before,.kpl-divider::after{ content:''; flex:1; height:1px; background:rgba(30,42,30,.13); }
/* Google */
.kpl-btn-google{
  width:100%; border:1px solid rgba(30,42,30,.06); cursor:pointer;
  background:#fff; color:#232b22; border-radius:99px; padding:15px;
  font-family:'Plus Jakarta Sans',sans-serif; font-size:15.5px; font-weight:700;
  box-shadow:0 10px 24px -18px rgba(30,42,30,.35);
  display:flex; align-items:center; justify-content:center; gap:11px;
  transition:transform .2s ease, box-shadow .2s ease;
}
.kpl-btn-google:hover{ transform:translateY(-1px); box-shadow:0 14px 28px -16px rgba(30,42,30,.4); }
.kpl-btn-google svg{ width:20px; height:20px; flex-shrink:0; }
/* Carte inscription */
.kpl-signup-card{
  width:100%; margin-top:18px; border:none; cursor:pointer; text-align:left;
  background:#e9efdb; border-radius:20px; padding:16px 18px;
  display:flex; align-items:center; gap:14px;
  transition:transform .2s ease, filter .2s ease;
}
.kpl-signup-card:hover{ filter:brightness(1.02); transform:translateY(-1px); }
.kpl-signup-ico{ width:46px; height:46px; border-radius:50%; background:#fff; display:flex; align-items:center; justify-content:center; flex-shrink:0; box-shadow:0 6px 14px -8px rgba(30,42,30,.3); }
.kpl-signup-ico svg{ width:25px; height:25px; color:#3c5a2c; }
.kpl-signup-txt{ flex:1; min-width:0; display:flex; flex-direction:column; gap:3px; }
.kpl-signup-q{ font-family:'Plus Jakarta Sans',sans-serif; font-size:13.5px; font-weight:600; color:#3a423a; }
.kpl-signup-cta{ font-family:'Plus Jakarta Sans',sans-serif; font-size:18px; font-weight:800; color:#3f7d3a; letter-spacing:-.01em; }
.kpl-signup-arrow{ font-size:20px; color:#3f7d3a; font-weight:700; }
/* Sécurité */
.kpl-secure{ display:flex; align-items:center; justify-content:center; gap:8px; margin-top:16px; font-family:'Plus Jakarta Sans',sans-serif; font-size:13.5px; font-weight:600; color:#5c645a; }
.kpl-secure svg{ width:17px; height:17px; color:#4e7a36; }
/* Invité + footer discrets */
#authScreen .auth-guest-btn.kpl-guest{ font-size:12px !important; padding:8px !important; margin-top:2px !important; margin-bottom:2px !important; }
#authScreen .auth-footer.kpl-foot{ border-top:none !important; margin-top:0 !important; padding:4px 20px 14px !important; text-align:center !important; background:none !important; }
#authScreen .auth-footer.kpl-foot .auth-coord-link{ font-family:'Plus Jakarta Sans',sans-serif; font-size:11px; color:#8a9086; text-decoration:none; }
/* Retour connexion (inscription) */
.kpl-back-login{ background:none; border:none; cursor:pointer; padding:0 0 14px; font-family:'Plus Jakarta Sans',sans-serif; font-size:13.5px; font-weight:700; color:#3f7d3a; text-align:left; }
.kpl-back-login:hover{ text-decoration:underline; }
/* Reset overlay clair */
#authScreen .auth-reset-overlay{ background:rgba(248,246,238,.98) !important; backdrop-filter:blur(8px); border-radius:0 !important; }
#authScreen .auth-reset-title{ color:#2c342c !important; }
#authScreen .auth-reset-sub{ color:#6b7266 !important; }
@media (max-width:980px){
  #authScreen .auth-card .auth-logo{ margin-top:calc(48px + env(safe-area-inset-top)) !important; }
  .kpl-title{ font-size:29px; }
}
</style>''',
    'R5 styles')

# ── R6 : authSetLoading — restaurer la flèche du bouton ──
rep("    if(btnId==='btnLogin') btn.innerHTML = '<span>Se connecter</span>';",
    "    if(btnId==='btnLogin') btn.innerHTML = '<span>Se connecter</span><span class=\"kpl-btn-arrow\" aria-hidden=\"true\">→</span>';",
    'R6 setLoading')

# ── R7 : persistance selon « Se souvenir de moi » ──
rep("""  authSetLoading('btnLogin', true);
  authInstance.signInWithEmailAndPassword(email, pwd)""",
    """  authSetLoading('btnLogin', true);
  // « Se souvenir de moi » : persistance LOCAL (coché) ou SESSION (décoché)
  try{
    var _rm = document.getElementById('kplRemember');
    if(_rm && authInstance.setPersistence && firebase.auth && firebase.auth.Auth && firebase.auth.Auth.Persistence){
      authInstance.setPersistence(_rm.checked ? firebase.auth.Auth.Persistence.LOCAL : firebase.auth.Auth.Persistence.SESSION).catch(function(){});
    }
  }catch(e){}
  authInstance.signInWithEmailAndPassword(email, pwd)""",
    'R7 remember-me')

# ── R8 : bascule œil mot de passe ──
rep("""function authGuest(){
  authClearMsg();""",
    """function kpTogglePwd(ev){
  try{ ev.preventDefault(); ev.stopPropagation(); }catch(e){}
  var inp = document.getElementById('loginPassword'); if(!inp) return;
  var show = inp.type === 'password';
  inp.type = show ? 'text' : 'password';
  var btn = ev.currentTarget || (ev.target && ev.target.closest('.kpl-eye'));
  if(btn) btn.classList.toggle('kpl-eye-on', show);
}
window.kpTogglePwd = kpTogglePwd;

function authGuest(){
  authClearMsg();""",
    'R8 kpTogglePwd')

io.open(PATH, 'w', encoding='utf-8').write(src)
print('DONE — written', len(src), 'chars')
