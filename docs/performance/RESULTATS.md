# Profil par composante (J.1.1)

`tools/profile_components.py` — bootstrap wild, B = 299, grid_ci = 100, grille de 100, noyaux déjà
compilés, une seule exécution par taille (mesure indicative, non répétée).

| Composante (s)                           | Hansen 565 | N = 2 000 | N = 10 000 |
|------------------------------------------|-----------:|----------:|-----------:|
| Données                                  |       0,01 |      0,01 |       0,04 |
| Pile (instruments, poids)                |       0,13 |      0,07 |       0,40 |
| Recherche du seuil (grille, étape 2)     |       0,21 |      0,19 |       0,31 |
| Variance                                 |       0,01 |      0,01 |       0,03 |
| Tests (Hansen, AR)                       |       0,02 |      0,02 |       0,08 |
| Bootstrap (linéarité + ensemble de conf.)|       4,53 |      1,48 |       3,87 |
| **Total**                                |   **4,90** |  **1,78** |   **4,74** |
| Équations / instruments                  | 7 345 / 117 | 12 000 / 27 | 60 000 / 27 |

Le bootstrap pèse 80 à 92 % du temps. Dans le profil (`cprofile_*.txt`) :

* Hansen (117 instruments) : `criterion` (forme quadratique `n·m'Qm`, BLAS) 2,6 s de temps propre sur
  5,3 s, puis `einsum` 0,57 s et `make_family` 0,22 s.
* N = 10 000 (27 instruments) : `sample_moments` 0,84 s (moments par tirage), `transform_levels`
  0,45 s, `rmatmul` 0,36 s, `unit_moments` 0,21 s, conversions `astype` 0,24 s.
* Le bootstrap par unités (Gong-Seo, algorithme 1) n'est pas dans ce tableau : mesuré à part,
  environ 0,4 s par tirage, soit environ 80 fois le wild.
