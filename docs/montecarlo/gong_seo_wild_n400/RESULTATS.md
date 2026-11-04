# Couverture de l'IC du seuil : design de Gong et Seo (section 5, tableau 1)

Expérience : `tools/monte_carlo_gong_seo.py --reps 200 --tag gong_seo_wild_n400` (graine 2026).
Design `gong_seo` (équation (12)), n = 400, T = 6, 200 réplications par cellule, 500 tirages de
bootstrap **wild** (défaut du paquet), grille de 100 points, instruments non regroupés. Aucune
réplication n'a échoué. Le papier utilise 2000 réplications et le bootstrap par unités.

## Couverture de γ₀ (nominal 95 %)

| Saut δ₁ + δ₃γ | 0 | 0,1 | 0,2 | 0,5 | 1 |
|---|---|---|---|---|---|
| Paquet, enveloppe de l'ensemble accepté | 0,995 | 1,000 | 1,000 | 0,995 | 0,995 |
| Papier, Grid-B (tableau 1, n = 400) | 0,992 | 0,995 | 0,993 | 0,988 | 0,966 |
| Paquet, union des segments (lecture stricte) | 0,935 | 0,930 | 0,925 | 0,930 | 0,930 |

L'IC du papier est un intervalle : la comparaison pertinente est l'enveloppe. L'erreur de Monte
Carlo à 200 réplications vaut 0,005 à 0,007 pour une couverture de 0,99 ; quatre cellules sur cinq
sont à moins de 1,2 erreur type du papier, la cellule « saut = 1 » est à 2,3 erreurs types (plus
conservatrice que le papier).

## Rejet de γ₀ + c par l'enveloppe (puissance, tableau 2 du papier, n = 400)

| c | saut | 0 | 0,1 | 0,2 | 0,5 | 1 |
|---|---|---|---|---|---|---|
| 0,10 | Paquet | 0,005 | 0,000 | 0,000 | 0,015 | 0,060 |
|  | Papier | 0,015 | 0,015 | 0,015 | 0,027 | 0,096 |
| 0,25 | Paquet | 0,010 | 0,020 | 0,020 | 0,040 | 0,130 |
|  | Papier | 0,020 | 0,030 | 0,042 | 0,100 | 0,281 |
| 0,50 | Paquet | 0,050 | 0,065 | 0,080 | 0,130 | 0,255 |
|  | Papier | 0,102 | 0,137 | 0,172 | 0,314 | 0,581 |

**Écart non expliqué** : à couverture comparable, nos intervalles sont plus larges que ceux du
papier, donc moins puissants (jusqu'à deux fois moins pour c = 0,25 et 0,5). Causes possibles, non
testées : bootstrap wild au lieu du bootstrap par unités de l'algorithme 1 ; 4 constantes
d'instruments de plus (28 au lieu de 24) ; grille et élagage de q. Le test demande le bootstrap par
unités, aujourd'hui 80 fois plus lent que le wild (bloc J).

## Taille du test de linéarité

Design `linear`, n = 400, T = 6, 200 réplications, 299 tirages : taux de rejet à 5 % de **0,055**
(erreur de Monte Carlo 0,016). Sous le design à seuil, le test rejette dans 100 % des réplications
pour chacun des sauts.

## Pentes

Couverture moyenne des intervalles asymptotiques sur les cinq cellules : 0,95 à 0,96. Sous le
modèle linéaire, les changements (`change:_cons`, `change:L.y`) ne sont pas identifiés : couvertures
de 0,78 et 0,87, ce qui n'a pas de sens à interpréter.
