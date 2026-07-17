#!/usr/bin/env python3
"""Réordonne PC : déplace le module 'Activité physique' (ex-index 7) en position 5
(avant 'Perte de poids'). Idempotent."""
src = open('/app/parcours_module.html', encoding='utf-8').read()

M_ACT = '{t:"Activité physique",e:"🏃"'
M_NEW = '{t:"Bouger, récupérer et retrouver son énergie"'
M_STRESS = '{t:"Stress et sommeil"'
M_POIDS = '{t:"Perte de poids"'

if M_NEW in src:
    print('Déjà réordonné (titre déjà renommé)'); exit(0)

i1 = src.index(M_ACT)
i2 = src.index(M_STRESS)
block = src[i1:i2]
# retirer le bloc (avec sa virgule finale incluse dans block)
src = src[:i1] + src[i2:]
# insérer avant Perte de poids
j = src.index(M_POIDS)
src = src[:j] + block + src[j:]
open('/app/parcours_module.html', 'w', encoding='utf-8').write(src)
print('Module Activité physique déplacé en position 6 (index 5)')
