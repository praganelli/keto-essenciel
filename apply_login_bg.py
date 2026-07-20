#!/usr/bin/env python3
# Fond feuillage/avocats flou + brins de feuillage sur l'écran de connexion
import io, base64, sys

PATH = '/app/keto.html'
src = io.open(PATH, encoding='utf-8').read()
BG = 'data:image/webp;base64,' + base64.b64encode(open('/tmp/login_bg.webp', 'rb').read()).decode()


def rep(old, new, label):
    global src
    if src.count(old) != 1:
        print('FAIL:', label, src.count(old)); sys.exit(1)
    src = src.replace(old, new)
    print('OK:', label)


# 1) Fond photo + voile crème (remplace le fond uni + blobs)
rep('''#authScreen .auth-tabs{display:none !important}
#authScreen{background:#f7f5ec !important}
#authScreen .auth-card{
  background:
    radial-gradient(46% 22% at 100% 0%, rgba(163,190,140,.26) 0%, transparent 72%),
    radial-gradient(40% 18% at 0% 26%, rgba(163,190,140,.16) 0%, transparent 70%),
    radial-gradient(52% 20% at 62% 100%, rgba(163,190,140,.22) 0%, transparent 72%),
    #f8f6ee !important;
}''',
    '''#authScreen .auth-tabs{display:none !important}
#authScreen{
  background:url("''' + BG + '''") center/cover no-repeat fixed #eef0e4 !important;
}
#authScreen::after{ background:none !important; }
#authScreen .auth-card{
  background:linear-gradient(180deg,
    rgba(249,247,240,.93) 0%,
    rgba(249,247,240,.87) 30%,
    rgba(248,246,238,.80) 62%,
    rgba(248,246,238,.62) 100%) !important;
}''',
    'fond photo')

# 2) Brins de feuillage décoratifs (markup, dans la carte)
rep('''  <!-- ═══ CÔTÉ FORMULAIRE (la carte d'auth) ═══ -->
  <div class="auth-card">
''',
    '''  <!-- ═══ CÔTÉ FORMULAIRE (la carte d'auth) ═══ -->
  <div class="auth-card">

    <!-- Feuillage décoratif (mockup) -->
    <svg class="kpl-sprig kpl-sprig-1" viewBox="0 0 120 90" aria-hidden="true">
      <g fill="#b3c896" opacity=".85">
        <path d="M38 62 C22 50 18 30 30 14 C48 22 56 44 46 60 C44 63 41 64 38 62Z"/>
        <path d="M52 70 C48 52 58 34 78 28 C86 46 76 66 60 72 C57 73 53 73 52 70Z" opacity=".75"/>
      </g>
      <path d="M40 60 C50 70 70 76 96 74" stroke="#a3bb82" stroke-width="2.4" fill="none" stroke-linecap="round" opacity=".8"/>
    </svg>
    <svg class="kpl-sprig kpl-sprig-2" viewBox="0 0 100 100" aria-hidden="true">
      <path d="M50 88 C30 72 26 44 42 22 C66 34 74 64 58 84 C56 87 53 89 50 88Z" fill="#b3c896" opacity=".8"/>
      <path d="M48 84 C46 62 50 42 60 28" stroke="#96ad74" stroke-width="2" fill="none" stroke-linecap="round" opacity=".7"/>
    </svg>
''',
    'sprigs markup')

# 3) CSS des brins
rep('''/* Pastille langue */''',
    '''/* Brins de feuillage décoratifs */
.kpl-sprig{ position:fixed; pointer-events:none; z-index:1; }
.kpl-sprig-1{ width:110px; height:82px; right:-14px; top:33%; transform:rotate(8deg); }
.kpl-sprig-2{ width:84px; height:84px; right:6px; bottom:calc(10px + env(safe-area-inset-bottom)); transform:rotate(-14deg); }
@media (min-width:981px){
  .kpl-sprig-1{ right:8px; top:30%; }
  .kpl-sprig-2{ right:22px; bottom:18px; }
}
/* Pastille langue */''',
    'sprigs css')

io.open(PATH, 'w', encoding='utf-8').write(src)
print('DONE', len(src))
