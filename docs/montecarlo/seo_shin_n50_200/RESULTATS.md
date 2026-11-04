# Designs de Seo et Shin (2016, section 6) avec le paquet

Expérience : `tools/monte_carlo_seo_shin.py --reps 300 --tag seo_shin_n50_200` (graine 2026).
Designs `seo_shin_jump` (équation (16), Tong 1990) et `seo_shin_cont` (équation (17), Chan et Tsay
1998), T = 10, n = 50, 100, 200, **300 réplications** par cellule (le papier : 1000), 199 tirages
de bootstrap wild, grille de 100 points, 44 instruments (36 niveaux retardés de y + une constante
par équation). Aucune réplication n'a échoué. Le papier compare FD-GMM et moyennage de matrices de
poids aléatoires ; le paquet n'implémente que le FD-GMM, comparé ici à la colonne « FD-GMM ».

## Ce que le paquet donne

| | n | médiane − vérité | écart-type robuste (IQR/1,349) | écart-type papier | part des réplications à plus de 0,5 de γ₀ |
|---|---|---|---|---|---|
| Saut (16), γ₀ = 0 | 50 | 0,018 | 0,677 | 0,247 | 0,417 |
| | 100 | 0,004 | 0,108 | 0,294 | 0,140 |
| | 200 | 0,002 | 0,072 | 0,255 | 0,090 |
| Continu (17), γ₀ = 0,8 | 50 | −0,042 | 0,673 | 0,272 | 0,453 |
| | 100 | −0,155 | 0,648 | 0,274 | 0,463 |
| | 200 | −0,097 | 0,593 | 0,279 | 0,367 |

- Dans le design à saut, la **médiane est sur la vérité** et le cœur de la distribution est plus
  serré que dans le papier à n ≥ 100 (écart-type robuste 0,07 à 0,11 contre 0,26 à 0,29).
- En revanche une part de réplications (9 % à n = 200, 42 % à n = 50) tombe loin de la vérité, ce
  qui donne des écarts-types, MSE et couvertures très supérieurs aux tableaux 1, 2, 3 et 7 :
  à n = 200, écart-type de γ̂ 0,448 contre 0,255 ; de δ₁ 1,53 contre 0,42 ; MSE de δ₁ 2,3 contre 0,17.
- Le design continu est mal identifié (le saut est nul au seuil) : médiane de γ̂ en dessous de 0,8
  et dispersion forte à tout n, ce que le papier note aussi (« le design continu donne des MSE
  plus élevés »), mais dans une bien moindre mesure.
- Couverture de l'enveloppe de l'ensemble de confiance bootstrap de γ₀ : saut 0,993 / 0,817 / 0,813
  (n = 50, 100, 200) ; continu 0,997 / 0,877 / 0,943. Le papier (tableau 7, IC asymptotique, h = 1,
  FD-GMM) : 0,960 / 0,978 / 0,979 et 0,811 / 0,898 / 0,900. **Les deux méthodes d'intervalle
  diffèrent** : la comparaison n'est qu'indicative.

## Ces valeurs extrêmes sont celles de Stata

Trois des réplications à γ̂ éloigné (3, 20 et 32 : γ̂ = 2,595 ; 1,793 ; 1,506 pour γ₀ = 0) et une
réplication normale ont été exportées en `.dta` et estimées par Stata 17 MP
(`xtdpthresh y, qx(q) noboot`). Stata et Python donnent les mêmes γ̂, critère J et coefficients,
à 4,5 × 10⁻⁹ près. Dans ces trois panels, le critère est **réellement plus bas** au γ̂ éloigné qu'à
la vraie valeur (J = 25,9 contre 29,7 ; 33,8 contre 42,5 ; 51,0 contre 57,5), et une grille de 400
points ou `refine` ne changent pas la conclusion. Le test golden
`tests/golden/test_simulated_golden.py` fige ces quatre panels et les résultats de Stata.

L'écart de dispersion avec le papier n'est donc pas un défaut de la transcription de l'estimateur.
Causes possibles, **non testées** : (a) le papier n'a pas les 8 instruments constants de l'estimateur
de Stata (36 instruments contre 44) ; (b) la recherche sur la grille ou le critère à deux pas du
papier diffère de celui de `xtdpthresh` ; (c) pour un modèle auto-excité (q = y₋₁), le bootstrap
du paquet traite q comme donné alors qu'il dépend de y, ce qui peut expliquer la sous-couverture à
n = 100 et 200.
