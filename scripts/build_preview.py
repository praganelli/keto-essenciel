import io
SRC="/app/keto.html"
OUT="/app/backend/keto_preview.html"

LEAF = ("data:image/svg+xml;utf8,"
        "<svg xmlns='http://www.w3.org/2000/svg' width='140' height='140' viewBox='0 0 140 140'>"
        "<g fill='none' stroke='%23ffffff' stroke-width='1.1' opacity='0.7'>"
        "<path d='M34 22 q22 20 0 44 q-22 -24 0 -44z'/>"
        "<path d='M98 74 q19 17 0 38 q-19 -21 0 -38z'/>"
        "<path d='M70 110 q14 12 0 28 q-14 -16 0 -28z'/>"
        "</g></svg>")

CSS = """
<style id="kp-desktop-AC">
/* ═══════════════ EXPÉRIENCE DESKTOP — Concept A + C (min-width:1024px) ═══════════════ */
@media (min-width:1024px){
  /* Décor de fond éditorial plein écran (vert sauge profond) */
  body{
    background:
      radial-gradient(1100px 560px at 82% -8%, rgba(150,182,150,.30), transparent 60%),
      radial-gradient(900px 520px at -5% 105%, rgba(94,124,97,.26), transparent 55%),
      linear-gradient(157deg, #1d3022 0%, #294029 44%, #36523a 72%, #41613f 100%) !important;
    background-attachment:fixed !important;
  }
  /* on retire le voile crème mobile pour laisser respirer le fond sombre */
  body::after{ display:none !important; }
  /* texture botanique subtile */
  body::before{
    content:''; position:fixed; inset:0; z-index:0; pointer-events:none; opacity:.09;
    background-image:url("__LEAF__"); background-size:240px; background-repeat:repeat;
  }

  /* L'app posée dans un cadre centré flottant (effet application premium) */
  .app{
    max-width:1200px !important;
    margin:112px auto 64px !important;
    padding:10px 44px 72px !important;
    background:rgba(252,246,231,.97);
    border:1px solid rgba(255,255,255,.55);
    border-radius:30px;
    box-shadow:0 50px 130px -34px rgba(0,0,0,.6), 0 1px 0 rgba(255,255,255,.6) inset;
  }
  body.dark .app{ background:rgba(17,27,20,.97); border-color:rgba(255,255,255,.08); }

  /* Navigation déplacée EN HAUT — barre flottante glassmorphe */
  .bottom-nav{ top:22px !important; bottom:auto !important; padding-top:0 !important; padding-bottom:0 !important; }
  .bottom-nav-inner{ margin:0 auto; box-shadow:0 18px 50px -16px rgba(0,0,0,.45); }

  /* En-tête plus imposant et éditorial */
  header{ padding:30px 0 24px !important; }
  header h1{ font-size:48px !important; line-height:1.02 !important; }
  header .tagline{ font-size:15px !important; }

  /* Concept C — grilles adaptatives : bibliothèque 4 colonnes */
  .lib-grid{ grid-template-columns:repeat(4, 1fr) !important; gap:20px !important; }
  /* plus de respiration pour le planning de la semaine */
  .week-grid{ gap:12px !important; }
}
@media (min-width:1440px){
  .app{ max-width:1340px !important; padding-left:56px !important; padding-right:56px !important; }
  .lib-grid{ grid-template-columns:repeat(5, 1fr) !important; }
  header h1{ font-size:54px !important; }
}
</style>
""".replace("__LEAF__", LEAF)

html = open(SRC, encoding="utf-8").read()
# Inject just before </head> so it wins the cascade
assert "</head>" in html
html = html.replace("</head>", CSS + "\n</head>", 1)
open(OUT, "w", encoding="utf-8").write(html)
print("preview built:", OUT, "size", len(html))
