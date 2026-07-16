#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Saisie du jour Diabète → carrousel 3 étapes + curseurs (glycémies, pas, eau, sommeil)."""
src = open('/app/keto.html', encoding='utf-8').read()

# ── 1. CSS ──
css_anchor = ".diab-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin:8px 0 4px}"
assert src.count(css_anchor) == 1
css_new = css_anchor + """
      /* ═══ Saisie du jour : carrousel 3 étapes + curseurs ═══ */
      .diab-wiz-tabs{display:flex;gap:6px;margin-bottom:14px}
      .diab-wiz-tab{flex:1;text-align:center;padding:9px 4px;border-radius:10px;font-family:'Plus Jakarta Sans',sans-serif;font-size:11px;font-weight:700;color:var(--muted);background:rgba(0,0,0,.045);cursor:pointer;border:1px solid transparent;transition:all .25s;white-space:nowrap}
      .diab-wiz-tab.on{background:rgba(164,84,60,.1);color:#a4543c;border-color:rgba(164,84,60,.3)}
      .diab-wiz-viewport{overflow:hidden;margin:0 -4px}
      .diab-wiz-track{display:flex;width:300%;transition:transform .38s cubic-bezier(.22,1,.36,1)}
      .diab-wiz-step{width:33.3333%;flex:0 0 33.3333%;padding:2px 4px;box-sizing:border-box}
      .diab-wiz-dotrow{display:flex;justify-content:center;gap:6px;margin-top:14px}
      .diab-wiz-dot{width:7px;height:7px;border-radius:4px;background:rgba(0,0,0,.15);transition:all .3s}
      .diab-wiz-dot.on{background:#a4543c;width:22px}
      .diab-wiz-nav{display:flex;gap:8px;margin-top:12px}
      #diabGlyGrid{display:flex;flex-direction:column;gap:12px}
      .diab-slider-row{display:flex;align-items:center;gap:10px;margin-top:3px}
      .diab-slider-row input[type=range]{flex:1;accent-color:#a4543c;height:28px;min-width:0}
      .diab-slider-row input[type=number]{width:82px;flex:0 0 82px;text-align:center}
      .diab-slide-field{margin-bottom:12px}
      body.dark .diab-wiz-tab{background:rgba(255,255,255,.06)}
      body.dark .diab-wiz-dot{background:rgba(255,255,255,.2)}"""
src = src.replace(css_anchor, css_new)

# ── 2. Markup : remplace toute la carte Saisie du jour ──
start = src.index('<div class="sec-label" style="margin-top:20px">✍️ Saisie du jour</div>')
end_marker = '<div id="diabHistory" style="margin-top:14px"></div>\n      </div></div>'
end = src.index(end_marker) + len(end_marker)
new_markup = """<div class="sec-label" style="margin-top:20px">✍️ Saisie du jour</div>
      <div class="card"><div class="card-body">
        <div class="diab-wiz-tabs" id="diabWizTabs">
          <div class="diab-wiz-tab on" onclick="kpDiabWizGo(0)" data-testid="diab-wiz-tab-0">🩸 Glycémies</div>
          <div class="diab-wiz-tab" onclick="kpDiabWizGo(1)" data-testid="diab-wiz-tab-1">💊 Traitement</div>
          <div class="diab-wiz-tab" onclick="kpDiabWizGo(2)" data-testid="diab-wiz-tab-2">🌿 Hygiène de vie</div>
        </div>
        <div class="diab-wiz-viewport">
          <div class="diab-wiz-track" id="diabWizTrack">
            <!-- ── Étape 1 : Glycémies ── -->
            <div class="diab-wiz-step">
              <div class="suivi-field-label" style="font-size:12px;margin-bottom:8px">🩸 Glycémies (mg/dL)</div>
              <div id="diabGlyGrid"></div>
            </div>
            <!-- ── Étape 2 : Traitement ── -->
            <div class="diab-wiz-step">
              <div class="suivi-field-label" style="font-size:12px;margin-bottom:8px">💊 Traitement</div>
              <div>
                <div class="suivi-field-label">💊 Médicament ?</div>
                <div style="display:flex;gap:8px;margin-top:4px">
                  <button type="button" id="diabMedTglNo" class="btn btn-primary" style="flex:1" onclick="kpDiabTgl('med',false)" data-testid="diab-med-no">Non</button>
                  <button type="button" id="diabMedTglYes" class="btn btn-ghost" style="flex:1" onclick="kpDiabTgl('med',true)" data-testid="diab-med-yes">Oui</button>
                </div>
              </div>
              <div id="diabMedFields" style="display:none;margin-top:10px">
                <div style="margin-bottom:10px"><div class="suivi-field-label">Nom du médicament</div><input type="text" id="diabMeds" placeholder="ex : Metformine" class="form-input suivi-input" data-testid="diab-meds"></div>
                <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px">
                  <div><div class="suivi-field-label">Matin (mg)</div><input type="number" id="diabMedsMatin" min="0" step="any" placeholder="1000" class="form-input suivi-input" data-testid="diab-meds-matin"></div>
                  <div><div class="suivi-field-label">Midi (mg)</div><input type="number" id="diabMedsMidi" min="0" step="any" placeholder="500" class="form-input suivi-input" data-testid="diab-meds-midi"></div>
                  <div><div class="suivi-field-label">Soir (mg)</div><input type="number" id="diabMedsSoir" min="0" step="any" placeholder="1000" class="form-input suivi-input" data-testid="diab-meds-soir"></div>
                </div>
              </div>
              <div style="margin-top:12px">
                <div class="suivi-field-label">💉 Insuline ?</div>
                <div style="display:flex;gap:8px;margin-top:4px">
                  <button type="button" id="diabInsTglNo" class="btn btn-primary" style="flex:1" onclick="kpDiabTgl('ins',false)" data-testid="diab-ins-no">Non</button>
                  <button type="button" id="diabInsTglYes" class="btn btn-ghost" style="flex:1" onclick="kpDiabTgl('ins',true)" data-testid="diab-ins-yes">Oui</button>
                </div>
              </div>
              <div id="diabInsFields" style="display:none;margin-top:10px">
                <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px">
                  <div><div class="suivi-field-label">Matin (UI)</div><input type="number" id="diabInsMatin" min="0" step="0.5" placeholder="12" class="form-input suivi-input" data-testid="diab-ins-matin"></div>
                  <div><div class="suivi-field-label">Midi (UI)</div><input type="number" id="diabInsMidi" min="0" step="0.5" placeholder="8" class="form-input suivi-input" data-testid="diab-ins-midi"></div>
                  <div><div class="suivi-field-label">Soir (UI)</div><input type="number" id="diabInsSoir" min="0" step="0.5" placeholder="10" class="form-input suivi-input" data-testid="diab-ins-soir"></div>
                </div>
              </div>
              <div style="margin-top:12px"><div class="suivi-field-label">Effets secondaires</div><input type="text" id="diabSideFx" placeholder="Aucun / décrivez…" class="form-input suivi-input" data-testid="diab-sidefx"></div>
              <label style="display:flex;align-items:center;gap:8px;margin-top:12px;font-size:13px;cursor:pointer">
                <input type="checkbox" id="diabMissed" data-testid="diab-missed" style="width:17px;height:17px;accent-color:#b05522"> ⚠️ Oubli de traitement aujourd'hui
              </label>
            </div>
            <!-- ── Étape 3 : Hygiène de vie ── -->
            <div class="diab-wiz-step">
              <div class="suivi-field-label" style="font-size:12px;margin-bottom:8px">🌿 Habitudes du jour</div>
              <div class="diab-slide-field"><div class="suivi-field-label">🚶 Pas réalisés</div>
                <div class="diab-slider-row">
                  <input type="range" min="0" max="20000" step="250" value="6000" id="diabStepsS" oninput="kpDiabSlide('diabSteps',this.value)" data-testid="diab-steps-slider">
                  <input type="number" id="diabSteps" min="0" step="100" placeholder="7500" class="form-input suivi-input" oninput="kpDiabSlideSync('diabStepsS',this.value)" data-testid="diab-steps">
                </div>
              </div>
              <div class="diab-slide-field"><div class="suivi-field-label">💧 Eau consommée (L)</div>
                <div class="diab-slider-row">
                  <input type="range" min="0" max="4" step="0.1" value="1.5" id="diabWaterS" oninput="kpDiabSlide('diabWater',this.value)" data-testid="diab-water-slider">
                  <input type="number" id="diabWater" min="0" step="0.1" placeholder="1.8" class="form-input suivi-input" oninput="kpDiabSlideSync('diabWaterS',this.value)" data-testid="diab-water">
                </div>
              </div>
              <div class="diab-slide-field"><div class="suivi-field-label">😴 Sommeil (heures)</div>
                <div class="diab-slider-row">
                  <input type="range" min="0" max="12" step="0.5" value="7" id="diabSleepS" oninput="kpDiabSlide('diabSleep',this.value)" data-testid="diab-sleep-slider">
                  <input type="number" id="diabSleep" min="0" max="16" step="0.5" placeholder="7.5" class="form-input suivi-input" oninput="kpDiabSlideSync('diabSleepS',this.value)" data-testid="diab-sleep">
                </div>
              </div>
              <div style="margin-top:10px">
                <div class="suivi-field-label">Humeur</div>
                <div class="diab-mood-row" id="diabMoodRow"></div>
              </div>
              <label style="display:flex;align-items:center;gap:8px;margin-top:12px;font-size:13px;cursor:pointer">
                <input type="checkbox" id="diabCarbsOk" data-testid="diab-carbs-ok" style="width:17px;height:17px;accent-color:#236648"> ✅ Glucides respectés aujourd'hui (20-30 g nets max)
              </label>
            </div>
          </div>
        </div>
        <div class="diab-wiz-dotrow" id="diabWizDots"><span class="diab-wiz-dot on"></span><span class="diab-wiz-dot"></span><span class="diab-wiz-dot"></span></div>
        <div class="diab-wiz-nav">
          <button class="btn btn-ghost" id="diabWizPrev" onclick="kpDiabWizGo(_diabWizStep-1)" data-testid="diab-wiz-prev" style="flex:1" disabled>← Précédent</button>
          <button class="btn btn-gold" id="diabWizNext" onclick="kpDiabWizGo(_diabWizStep+1)" data-testid="diab-wiz-next" style="flex:1">Suivant →</button>
        </div>
        <button class="btn btn-primary" onclick="kpDiabSave()" data-testid="diab-save" style="width:100%;margin-top:10px">+ Enregistrer ma journée</button>
        <div id="diabHistory" style="margin-top:14px"></div>
      </div></div>"""
src = src[:start] + new_markup + src[end:]

# ── 3. Générateur glycémies : curseur + champ synchronisés ──
old_gen = """    grid.innerHTML = KP_GLY_FIELDS.map(function(f){
      return '<div><div class="suivi-field-label">'+f[1]+'</div>'
        + '<input type="number" id="diabGly_'+f[0]+'" min="20" max="600" placeholder="mg/dL" class="form-input suivi-input" data-testid="diab-gly-'+f[0]+'"></div>';
    }).join('');"""
assert src.count(old_gen) == 1
new_gen = """    grid.innerHTML = KP_GLY_FIELDS.map(function(f){
      return '<div><div class="suivi-field-label">'+f[1]+'</div>'
        + '<div class="diab-slider-row">'
        + '<input type="range" min="40" max="300" step="1" value="110" id="diabGlyS_'+f[0]+'" oninput="kpDiabSlide(\\'diabGly_'+f[0]+'\\',this.value)" data-testid="diab-gly-slider-'+f[0]+'">'
        + '<input type="number" id="diabGly_'+f[0]+'" min="20" max="600" placeholder="mg/dL" class="form-input suivi-input" oninput="kpDiabSlideSync(\\'diabGlyS_'+f[0]+'\\',this.value)" data-testid="diab-gly-'+f[0]+'">'
        + '</div></div>';
    }).join('');"""
src = src.replace(old_gen, new_gen)

# ── 4. JS : carrousel + synchronisation curseurs ──
js_anchor = "function kpDiabSetMood(v){"
assert src.count(js_anchor) == 1
js_new = """/* ─── Carrousel Saisie du jour (3 étapes) + curseurs synchronisés ─── */
var _diabWizStep = 0;
function kpDiabWizGo(i){
  i = Math.max(0, Math.min(2, i));
  _diabWizStep = i;
  var tr = document.getElementById('diabWizTrack');
  if(tr) tr.style.transform = 'translateX(-' + (i * 33.3333) + '%)';
  var tabs = document.querySelectorAll('#diabWizTabs .diab-wiz-tab');
  Array.prototype.forEach.call(tabs, function(t, k){ t.classList.toggle('on', k === i); });
  var dots = document.querySelectorAll('#diabWizDots .diab-wiz-dot');
  Array.prototype.forEach.call(dots, function(d, k){ d.classList.toggle('on', k === i); });
  var prev = document.getElementById('diabWizPrev'), next = document.getElementById('diabWizNext');
  if(prev) prev.disabled = (i === 0);
  if(next){ next.disabled = (i === 2); next.style.opacity = (i === 2) ? '.4' : ''; }
}
window.kpDiabWizGo = kpDiabWizGo;
function kpDiabSlide(numId, v){ var n = document.getElementById(numId); if(n) n.value = v; }
function kpDiabSlideSync(rangeId, v){ var r = document.getElementById(rangeId); if(r && v !== '' && !isNaN(parseFloat(v))) r.value = v; }
window.kpDiabSlide = kpDiabSlide; window.kpDiabSlideSync = kpDiabSlideSync;
function kpDiabSetMood(v){"""
src = src.replace(js_anchor, js_new)

# ── 5. kpDiabFillForm : synchroniser les curseurs après remplissage ──
fill_anchor = "  var mi=document.getElementById('diabMissed'); if(mi) mi.checked=!!e.missedMeds;"
assert src.count(fill_anchor) == 1
fill_new = """  /* Synchronise les curseurs avec les valeurs remplies */
  try{
    KP_GLY_FIELDS.forEach(function(f){ var n=document.getElementById('diabGly_'+f[0]); if(n&&n.value) kpDiabSlideSync('diabGlyS_'+f[0], n.value); });
    [['diabSteps','diabStepsS'],['diabWater','diabWaterS'],['diabSleep','diabSleepS']].forEach(function(p){
      var n=document.getElementById(p[0]); if(n&&n.value) kpDiabSlideSync(p[1], n.value);
    });
  }catch(e){}
""" + fill_anchor
src = src.replace(fill_anchor, fill_new)

open('/app/keto.html', 'w', encoding='utf-8').write(src)
print('OK: toutes les modifications appliquées')
