# Exploration de l'écart avec Seo et Shin (2016) : ce qui l'explique et ce qui ne l'explique pas

Outil : `tools/explore_seo_shin.py` (rejoue **les mêmes panels**, mêmes graines, avec une variante de
l'estimation ; rien n'est modifié dans le paquet). Design `seo_shin_jump`, T = 10, 300 réplications
(120 pour les essais à `grid_ci=400`). Référence : `docs/montecarlo/seo_shin_n50_200/RESULTATS.md`.

## 1. Les instruments constants : écartés

Le papier utilise 36 instruments (niveaux retardés de y) ; le paquet en ajoute une constante par
équation (44). Sans les constantes (36, colonnes du bloc annulées dans le script) :

| n = 200 | σ(γ̂) | MSE(γ̂) | part de γ̂ à plus de 0,5 | σ(β̂) | MSE(δ̂₁) | couverture (enveloppe) |
|---|---|---|---|---|---|---|
| Avec constantes (44) | 0,448 | 0,205 | 0,09 | 0,277 | 2,33 | 0,813 |
| Sans constantes (36) | 0,597 | 0,372 | 0,14 | 0,521 | 3,73 | 0,877 |
| Papier (FD-GMM) | 0,255 | 0,066 | | 0,261 | 0,174 | |

À n = 100 le résultat est le même (pas d'amélioration systématique). Les constantes n'expliquent pas
la dispersion.

## 2. La queue lourde vient de l'endogénéité du seuil

Avec un seuil **exogène** (`seo_shin_exogenous`, q uniforme sur [−1, 1], indépendante des erreurs),
l'estimateur de γ est très précis (écart-type 0,02 à n = 200) et aucune réplication n'est éloignée
(0 sur 300). Dans le design auto-excité (q = y₋₁, endogène) on retrouve la queue : 9 % des
réplications à plus de 0,5 du vrai seuil à n = 200. C'est la situation que traite le FD-GMM, et le
papier note lui-même que ses MSE sont élevés pour δ₁ et δ₂.

## 3. La sous-couverture vient surtout de la grille de l'ensemble de confiance

Couverture de γ₀ par l'enveloppe, `grid_ci` = 100 puis 400 :

| n = 200 | grid_ci = 100 | grid_ci = 400 |
|---|---|---|
| Seuil exogène | 0,783 | 0,933 |
| Auto-excité, saut | 0,813 | 0,900 |

Quand γ̂ est très précis (écart-type 0,02, pas de la grille 0,02 pour q ∈ [−1, 1]), la vraie valeur
tombe entre deux points de la grille et l'ensemble accepté peut l'exclure. L'hypothèse « le
bootstrap traite q comme donné alors qu'il dépend de y » **n'est pas étayée** : le seuil exogène,
pour lequel elle ne joue pas, sous-couvre autant que le seuil auto-excité.

Règle de `diagnose` ajoutée (`ci_grid_coarse`) : un ensemble de confiance de moins de 2 pas de sa
grille est signalé. Mesurée sur les 300 réplications du seuil exogène à n = 200 (65 échecs de
couverture), elle signale 37 réplications dont 20 manquent la vraie valeur (54 %, contre 22 % en
moyenne) et repère 31 % des échecs ; à 4 pas elle en repère 60 % avec 42 % de signalements
exacts. Beaucoup d'échecs sont de simples écarts d'échantillonnage sans lien avec la grille.
C'est un signe à lire, pas un détecteur ; aucune des trois estimations réelles de Hansen ne la
déclenche.

## 4. La fenêtre de recherche rapproche les chiffres, sans les reproduire

Le papier dit que la fenêtre de γ est entre « les dixième ou quinzième percentiles » de q et ne
précise pas celle de sa simulation. À n = 200, `bootstrap=False`, en élargissant le `trim` :

| trim | σ(γ̂) | MSE(γ̂) | σ(β̂) | MSE(β̂) | MSE(δ̂₁) | MSE(δ̂₂) |
|---|---|---|---|---|---|---|
| 0,10 (défaut) | 0,448 | 0,205 | 0,277 | 0,078 | 2,33 | 0,352 |
| 0,15 | 0,400 | 0,162 | 0,278 | 0,078 | 0,96 | 0,244 |
| 0,25 | 0,355 | 0,127 | 0,261 | 0,069 | 0,70 | 0,203 |
| 0,35 | 0,293 | 0,086 | 0,258 | 0,069 | 0,70 | 0,209 |
| Papier | 0,255 | 0,066 | 0,261 | 0,068 | 0,174 | 0,536 |

Une fenêtre étroite retire les minima lointains et rapproche γ et β du papier. Elle ne reproduit
pas δ₁ (nettement plus dispersé ici) ni δ₂ (plus précis ici). On ne peut donc pas affirmer que la
fenêtre explique l'écart : la simulation du papier ne la donne pas.

## Conclusion

| Hypothèse | Verdict |
|---|---|
| Instruments constants | écartée |
| Queue lourde due à q endogène | confirmée |
| Bootstrap avec q = y₋₁ | non étayée |
| Grille de l'ensemble de confiance trop grossière | confirmée pour la couverture |
| Fenêtre de recherche | explique en partie γ et β, pas δ₁ ni δ₂ ; indéterminée |

Il reste un écart sur δ₁ et δ₂ que je ne sais pas expliquer sans la procédure exacte du papier
(fenêtre, moyennage de matrices de poids aléatoires, valeurs initiales de y).
