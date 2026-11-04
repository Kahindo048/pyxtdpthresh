"""Messages of the ``xtdpthresh`` specification checks (layer 0).

The wording is the package's own, written for the Python call (``grid=5``, ``method="fd"``),
and every message names the offending argument and, where useful, the value received.  Each
check keeps the key and the Stata return code of the rule it ports, so the validation can
verify that the same rule fires in both programs without comparing texts.
"""

from __future__ import annotations

SPEC_MESSAGES: dict[str, dict[str, str]] = {
    # ---------------------------------------------------------------- argument types
    "opt_type_int": {
        "en": "{name} must be an integer (got {value!r}).",
        "fr": "{name} doit être un entier (reçu : {value!r}).",
    },
    "opt_type_number": {
        "en": "{name} must be a number (got {value!r}).",
        "fr": "{name} doit être un nombre (reçu : {value!r}).",
    },
    # ---------------------------------------------------------------- option values
    "opt_vce": {
        "en": 'vce must be "robust" or "windmeijer" (got {value!r}).',
        "fr": 'vce doit valoir "robust" ou "windmeijer" (reçu : {value!r}).',
    },
    "opt_coef_ci_type": {
        "en": 'coef_ci_type must be "symmetric" or "percentile" (got {value!r}).',
        "fr": 'coef_ci_type doit valoir "symmetric" ou "percentile" (reçu : {value!r}).',
    },
    "opt_coef_boot_gs": {
        "en": (
            'coef_boot="gs" is not implemented: the available scheme is a cluster wild '
            "residual bootstrap that accounts for the threshold search, not the Gong-Seo "
            'coefficient bootstrap. Use "twostep", "onestep" or "none".'
        ),
        "fr": (
            'coef_boot="gs" n\'est pas implémenté : le schéma disponible est un bootstrap '
            "sauvage des résidus par grappes qui tient compte de la recherche du seuil, et non "
            'le bootstrap des coefficients de Gong-Seo. Utiliser "twostep", "onestep" ou "none".'
        ),
    },
    "opt_coef_boot": {
        "en": 'coef_boot must be "twostep", "onestep" or "none" (got {value!r}).',
        "fr": 'coef_boot doit valoir "twostep", "onestep" ou "none" (reçu : {value!r}).',
    },
    "note_coef_boot": {
        "en": (
            'coef_boot="{value}" is a legacy compatibility feature; inference by coefficient '
            "bootstrap is outside the supported core."
        ),
        "fr": (
            'coef_boot="{value}" est une fonction de compatibilité héritée ; l\'inférence par '
            "bootstrap des coefficients est hors du noyau pris en charge."
        ),
    },
    "opt_grid_type": {
        "en": 'grid_type must be "uniform" or "quantile" (got {value!r}).',
        "fr": 'grid_type doit valoir "uniform" ou "quantile" (reçu : {value!r}).',
    },
    "opt_min_regime": {
        "en": "min_regime must be a non-negative integer (got {value!r}).",
        "fr": "min_regime doit être un entier positif ou nul (reçu : {value!r}).",
    },
    "opt_bw_scale": {
        "en": "bw_scale must be a positive number (got {value!r}).",
        "fr": "bw_scale doit être un nombre strictement positif (reçu : {value!r}).",
    },
    "opt_refine": {
        "en": "refine must be an integer between 0 and 20 (got {value!r}).",
        "fr": "refine doit être un entier entre 0 et 20 (reçu : {value!r}).",
    },
    "opt_refine_kink": {
        "en": (
            "refine is available for the jump specification only: the kink regressor "
            "(q - gamma) * 1(q > gamma) varies continuously with gamma."
        ),
        "fr": (
            "refine n'est disponible que pour la spécification à saut : le régresseur de kink "
            "(q - gamma) * 1(q > gamma) varie continûment avec gamma."
        ),
    },
    "opt_search_retired": {
        "en": (
            "search_mode, search_max and search_tol were removed in xtdpthresh 0.9.26: the "
            "threshold search is a fixed finite grid chosen with grid, plus the optional refine."
        ),
        "fr": (
            "search_mode, search_max et search_tol ont disparu avec xtdpthresh 0.9.26 : la "
            "recherche du seuil porte sur une grille finie fixe choisie par grid, avec refine "
            "en option."
        ),
    },
    "opt_history": {
        "en": 'history must be "panel" or "sample" (got {value!r}).',
        "fr": 'history doit valoir "panel" ou "sample" (reçu : {value!r}).',
    },
    "opt_history_sample_ts": {
        "en": (
            'history="sample" cannot restrict lag or difference terms ({terms}): they are '
            "computed on the full panel before the sample is selected. Create the lagged "
            'variables as ordinary columns, or use history="panel".'
        ),
        "fr": (
            'history="sample" ne peut pas restreindre les termes décalés ou en différence '
            "({terms}) : ils sont calculés sur le panel complet avant la sélection de "
            "l'échantillon. Créer les variables décalées comme colonnes ordinaires, ou "
            'utiliser history="panel".'
        ),
    },
    "opt_boot_type_exact": {
        "en": (
            'boot_type="exact" was renamed "unit": the unit-resampling scheme follows '
            "Algorithm 1 of Gong and Seo but is not certified as the exact algorithm."
        ),
        "fr": (
            'boot_type="exact" a été renommé "unit" : le rééchantillonnage des unités suit '
            "l'algorithme 1 de Gong et Seo mais n'est pas certifié comme l'algorithme exact."
        ),
    },
    "opt_boot_type": {
        "en": 'boot_type must be "wild" or "unit" (got {value!r}).',
        "fr": 'boot_type doit valoir "wild" ou "unit" (reçu : {value!r}).',
    },
    "opt_boot_type_unit_method": {
        "en": (
            'boot_type="unit" supports method="fd" only: Algorithm 1 of Gong and Seo is '
            "developed for the first-differenced estimator."
        ),
        "fr": (
            'boot_type="unit" ne prend en charge que method="fd" : l\'algorithme 1 de Gong et '
            "Seo est développé pour l'estimateur en différences premières."
        ),
    },
    "opt_boot_type_unit_kink": {
        "en": (
            'boot_type="unit" does not support kink: Algorithm 1 targets the unrestricted '
            "jump estimator."
        ),
        "fr": (
            "boot_type=\"unit\" ne prend pas en charge kink : l'algorithme 1 vise l'estimateur "
            "à saut non restreint."
        ),
    },
    "opt_grid_sample": {
        "en": 'grid_sample must be "effective" or "observed" (got {value!r}).',
        "fr": 'grid_sample doit valoir "effective" ou "observed" (reçu : {value!r}).',
    },
    "opt_lev_maxlag": {
        "en": 'lev_maxlag was retired with method="system"; use maxlag for FD/FOD moments.',
        "fr": (
            'lev_maxlag a disparu avec method="system" ; utiliser maxlag pour les moments FD/FOD.'
        ),
    },
    "opt_iv_maxlag": {
        "en": (
            "iv_maxlag is not supported: external instruments always enter with their "
            "period-t value, so a lag limit never applied to them. Use maxlag, which "
            "limits the GMM-style instruments."
        ),
        "fr": (
            "iv_maxlag n'est pas pris en charge : les instruments externes entrent toujours "
            "avec leur valeur de la période t, donc une limite de retards ne s'appliquait "
            "jamais à eux. Utiliser maxlag, qui limite les instruments de type GMM."
        ),
    },
    "opt_method_system": {
        "en": (
            'method="system" is no longer supported (since xtdpthresh 0.9.25). The supported '
            'estimators are method="fd" and method="fod".'
        ),
        "fr": (
            'method="system" n\'est plus pris en charge (depuis xtdpthresh 0.9.25). Les '
            'estimateurs pris en charge sont method="fd" et method="fod".'
        ),
    },
    "opt_method": {
        "en": 'method must be "fd" or "fod" (got {value!r}).',
        "fr": 'method doit valoir "fd" ou "fod" (reçu : {value!r}).',
    },
    "opt_grid": {
        "en": "grid must be an integer of at least 10 (got {value!r}).",
        "fr": "grid doit être un entier d'au moins 10 (reçu : {value!r}).",
    },
    "opt_grid_ci": {
        "en": "grid_ci must be an integer of at least 10 (got {value!r}).",
        "fr": "grid_ci doit être un entier d'au moins 10 (reçu : {value!r}).",
    },
    "opt_gamma_test": {
        "en": "gamma_test needs the grid bootstrap: use bootstrap=True.",
        "fr": "gamma_test exige le grid bootstrap : utiliser bootstrap=True.",
    },
    "opt_continuity_boot": {
        "en": (
            "continuity_test needs the bootstrap tests: use bootstrap=True and linearity_test=True."
        ),
        "fr": (
            "continuity_test exige les tests par bootstrap : utiliser bootstrap=True et "
            "linearity_test=True."
        ),
    },
    "opt_trim": {
        "en": "trim must lie in [0.01, 0.45] (got {value!r}).",
        "fr": "trim doit appartenir à [0,01 ; 0,45] (reçu : {value!r}).",
    },
    "opt_n_boot": {
        "en": "n_boot must be an integer of at least 10; 99 or more is advised (got {value!r}).",
        "fr": (
            "n_boot doit être un entier d'au moins 10 ; 99 ou plus conseillé (reçu : {value!r})."
        ),
    },
    "opt_seed": {
        "en": "seed must be an integer in [0, 2147483647] (got {value!r}).",
        "fr": "seed doit être un entier dans [0, 2147483647] (reçu : {value!r}).",
    },
    "opt_level": {
        "en": "level must lie between 10 and 99.99 (got {value!r}).",
        "fr": "level doit être compris entre 10 et 99,99 (reçu : {value!r}).",
    },
    "opt_maxlag_count": {
        "en": "maxlag takes one or two integers, (min, max) (got {value!r}).",
        "fr": "maxlag prend un ou deux entiers, (min, max) (reçu : {value!r}).",
    },
    "opt_maxlag_range": {
        "en": "maxlag values must be positive integers (got {value!r}).",
        "fr": (
            "les valeurs de maxlag doivent être des entiers strictement positifs "
            "(reçu : {value!r})."
        ),
    },
    "opt_maxlag_int": {
        "en": "maxlag values must be integers (got {value!r}).",
        "fr": "les valeurs de maxlag doivent être des entiers (reçu : {value!r}).",
    },
    "opt_maxlag_order": {
        "en": "maxlag=(min, max) requires min <= max (got {value!r}).",
        "fr": "maxlag=(min, max) exige min <= max (reçu : {value!r}).",
    },
    # ---------------------------------------------------------------- variable terms
    "term_invalid": {
        "en": (
            "'{term}' is not a valid term: write a variable name, optionally with lag or "
            'difference operators ("L.x", "L2.x", "D.x", "S12.x", "F.x") or use '
            'lag("x", 2).'
        ),
        "fr": (
            "« {term} » n'est pas un terme valide : écrire un nom de variable, avec au besoin "
            'des opérateurs de retard ou de différence ("L.x", "L2.x", "D.x", "S12.x", '
            '"F.x"), ou utiliser lag("x", 2).'
        ),
    },
    "spec_depvar_operator": {
        "en": (
            "The dependent variable y cannot carry a lag or difference operator (got "
            "{term!r}); create the lagged or differenced column first."
        ),
        "fr": (
            "La variable dépendante y ne peut pas porter d'opérateur de retard ou de "
            "différence (reçu : {term!r}) ; créer d'abord la colonne décalée ou différenciée."
        ),
    },
    "spec_depvar_lag_exogenous": {
        "en": (
            "{term} is a lag of the dependent variable and cannot be strictly exogenous: "
            "declare it in predetermined instead of x or exogenous."
        ),
        "fr": (
            "{term} est un retard de la variable dépendante et ne peut pas être strictement "
            "exogène : le déclarer dans predetermined plutôt que dans x ou exogenous."
        ),
    },
    "spec_depvar_current_exogenous": {
        "en": (
            "{term} contains the current or a future value of the dependent variable "
            "{y}: differences, seasonal differences and leads of {y} cannot be regressors."
        ),
        "fr": (
            "{term} contient la valeur courante ou une valeur future de la variable dépendante "
            "{y} : les différences, différences saisonnières et avances de {y} ne peuvent pas "
            "être des régresseurs."
        ),
    },
    "spec_depvar_current_regressor": {
        "en": (
            "{term} contains the current or a future value of the dependent variable "
            "{y} and cannot be a regressor; lags of {y} belong in predetermined."
        ),
        "fr": (
            "{term} contient la valeur courante ou une valeur future de la variable dépendante "
            "{y} et ne peut pas être un régresseur ; les retards de {y} vont dans predetermined."
        ),
    },
    "spec_depvar_current_iv": {
        "en": (
            "{term} contains the current or a future value of the dependent variable "
            "{y} and cannot be an instrument; only lags of {y} may appear in iv."
        ),
        "fr": (
            "{term} contient la valeur courante ou une valeur future de la variable dépendante "
            "{y} et ne peut pas être un instrument ; seuls les retards de {y} peuvent figurer "
            "dans iv."
        ),
    },
    # ---------------------------------------------------------------- roles of the variables
    "spec_overlap_endog_x": {
        "en": "{names} cannot be both in endogenous and in x: give each variable one role.",
        "fr": (
            "{names} ne peut pas figurer à la fois dans endogenous et dans x : "
            "un seul rôle par variable."
        ),
    },
    "spec_overlap_endog_exog": {
        "en": "{names} cannot be both in endogenous and in exogenous: give each variable one role.",
        "fr": (
            "{names} ne peut pas figurer à la fois dans endogenous et dans exogenous : "
            "un seul rôle par variable."
        ),
    },
    "spec_overlap_x_exog": {
        "en": "{names} cannot be both in x and in exogenous: it would enter the model twice.",
        "fr": (
            "{names} ne peut pas figurer à la fois dans x et dans exogenous : "
            "il entrerait deux fois dans le modèle."
        ),
    },
    "spec_overlap_predet_x": {
        "en": "{names} cannot be both in predetermined and in x: give each variable one role.",
        "fr": (
            "{names} ne peut pas figurer à la fois dans predetermined et dans x : "
            "un seul rôle par variable."
        ),
    },
    "spec_overlap_predet_exog": {
        "en": (
            "{names} cannot be both in predetermined and in exogenous: give each variable one role."
        ),
        "fr": (
            "{names} ne peut pas figurer à la fois dans predetermined et dans exogenous : "
            "un seul rôle par variable."
        ),
    },
    "spec_overlap_predet_endog": {
        "en": (
            "{names} cannot be both in predetermined and in endogenous: give each variable one "
            "role."
        ),
        "fr": (
            "{names} ne peut pas figurer à la fois dans predetermined et dans endogenous : "
            "un seul rôle par variable."
        ),
    },
    "spec_iv_declared": {
        "en": (
            "iv cannot contain variables declared endogenous or predetermined ({names}): "
            "that contradicts their declared timing and would create invalid moments."
        ),
        "fr": (
            "iv ne peut pas contenir de variables déclarées endogenous ou predetermined "
            "({names}) : cela contredit leur datation déclarée et créerait des moments invalides."
        ),
    },
    "spec_static_empty": {
        "en": (
            "A static model needs at least one regressor or external instrument: add "
            "regressors or iv, or drop static to use the dynamic model with the lag of "
            "{y}."
        ),
        "fr": (
            "Un modèle statique exige au moins un régresseur ou un instrument externe : "
            "ajouter des régresseurs ou iv, ou retirer static pour le modèle dynamique avec "
            "le retard de {y}."
        ),
    },
    "spec_conttest_kink": {
        "en": "continuity_test is not allowed with kink: the fitted model is the kink model.",
        "fr": "continuity_test n'est pas permis avec kink : le modèle estimé est le modèle kink.",
    },
    "spec_conttest_q": {
        "en": (
            "continuity_test needs {q} as a contemporaneous regressor; otherwise the kink "
            "model is not nested in the estimated jump model."
        ),
        "fr": (
            "continuity_test exige {q} comme régresseur contemporain ; sinon le modèle kink "
            "n'est pas emboîté dans le modèle à saut estimé."
        ),
    },
    "spec_duplicates": {
        "en": (
            "{role} lists {names} more than once after lag expansion: each variable may "
            "appear only once within a list."
        ),
        "fr": (
            "{role} contient {names} plus d'une fois après développement des retards : "
            "chaque variable ne peut figurer qu'une fois dans une liste."
        ),
    },
    "spec_depvar_in_rhs": {
        "en": (
            "The dependent variable {y} cannot appear in x, exogenous, endogenous, "
            "predetermined or iv (the dynamic model adds its lag automatically)."
        ),
        "fr": (
            "La variable dépendante {y} ne peut figurer ni dans x, ni dans exogenous, "
            "endogenous, predetermined ou iv (le modèle dynamique ajoute son retard "
            "automatiquement)."
        ),
    },
    "spec_q_is_depvar": {
        "en": (
            "The threshold variable q cannot be the dependent variable {y}; for a "
            "self-exciting threshold, create the lag first."
        ),
        "fr": (
            "La variable de seuil q ne peut pas être la variable dépendante {y} ; pour un "
            "seuil auto-excité, créer d'abord le retard."
        ),
    },
    "spec_exogenous_lag_of_declared": {
        "en": (
            "{term} is declared strictly exogenous, but it is a lag (or the same date) of "
            "{base}, which is declared endogenous or predetermined: declare {term} in "
            "predetermined or endogenous instead."
        ),
        "fr": (
            "{term} est déclaré strictement exogène, mais c'est un retard (ou la même date) "
            "de {base}, déclaré endogenous ou predetermined : déclarer plutôt {term} dans "
            "predetermined ou endogenous."
        ),
    },
    "spec_auto_lag_y": {
        "en": (
            "The lag of {y} is added automatically in the dynamic model: {term} is "
            "algebraically the same lag, remove it (extra lags such as L2.{y} go in "
            "predetermined)."
        ),
        "fr": (
            "Le retard de {y} est ajouté automatiquement dans le modèle dynamique : {term} "
            "est algébriquement le même retard, le retirer (les retards supplémentaires comme "
            "L2.{y} vont dans predetermined)."
        ),
    },
    "spec_iv_lag_needed": {
        "en": (
            "{term} is not a valid instrument under method {method!r}: it is correlated with "
            "the transformed error; instruments built on {base} need a lag of at least "
            "{need} here."
        ),
        "fr": (
            "{term} n'est pas un instrument valide avec method {method!r} : il est corrélé "
            "avec l'erreur transformée ; les instruments construits sur {base} exigent ici "
            "un retard d'au moins {need}."
        ),
    },
    "warn_kink_no_q": {
        "en": (
            "{q} is not a regressor, so kink estimates the one-sided hinge (q - gamma) * "
            "1(q > gamma); add {q} to x for the standard kink model."
        ),
        "fr": (
            "{q} n'est pas un régresseur : kink estime alors la charnière à un côté "
            "(q - gamma) * 1(q > gamma) ; ajouter {q} à x pour le modèle kink standard."
        ),
    },
    "warn_maxlag_one": {
        "en": (
            "maxlag leaves no lagged-level instruments for the lag of {y} or the endogenous "
            "regressors."
        ),
        "fr": (
            "maxlag ne laisse aucun instrument en niveau retardé pour le retard de {y} ni "
            "pour les régresseurs endogènes."
        ),
    },
    "warn_iv_wide": {
        "en": "About {cols} instrument columns; this will be slow. Consider maxlag or collapse.",
        "fr": "Environ {cols} colonnes d'instruments ; ce sera lent. Envisager maxlag ou collapse.",
    },
    "warn_iv_many": {
        "en": "About {cols} instrument columns; consider maxlag or collapse.",
        "fr": "Environ {cols} colonnes d'instruments ; envisager maxlag ou collapse.",
    },
    "warn_infinite": {
        "en": (
            "{n} infinite value(s) in {name} are treated as missing, as Stata treats a number "
            "that overflows (check for log(0) or a division by zero)."
        ),
        "fr": (
            "{n} valeur(s) infinie(s) dans {name} sont traitées comme manquantes, comme Stata "
            "traite un nombre qui déborde (vérifier un log(0) ou une division par zéro)."
        ),
    },
    "warn_memory": {
        "en": (
            "The fit is expected to use about {gb} GB of memory. maxlag or collapse shrink the "
            "instrument matrix; fewer bootstrap draws (n_boot) shrink the bootstrap."
        ),
        "fr": (
            "L'estimation devrait utiliser environ {gb} Go de mémoire. maxlag ou collapse "
            "réduisent la matrice d'instruments ; moins de tirages (n_boot) réduisent le bootstrap."
        ),
    },
    "warn_memory_high": {
        "en": (
            "The fit is expected to use about {gb} GB of memory and may fail or swap. Use "
            "collapse or maxlag to shrink the instrument matrix, or estimate on a subsample."
        ),
        "fr": (
            "L'estimation devrait utiliser environ {gb} Go de mémoire et risque d'échouer ou "
            "de saturer le disque. Utiliser collapse ou maxlag pour réduire la matrice "
            "d'instruments, ou estimer sur un sous-échantillon."
        ),
    },
    "warn_refine_one_step": {
        "en": "refine was not applied because the estimator fell back to one step.",
        "fr": "refine n'a pas été appliqué car l'estimateur est revenu à un pas.",
    },
    "warn_refine_incomplete": {
        "en": (
            "refine stopped before the neighbourhood of the estimated threshold was fully "
            "searched; increase refine."
        ),
        "fr": (
            "refine s'est arrêté avant que le voisinage du seuil estimé soit entièrement "
            "exploré ; augmenter refine."
        ),
    },
    "predict_kind": {
        "en": "predict kind {kind!r} is not available; choose one of: {options}.",
        "fr": "le type de prédiction {kind!r} n'existe pas ; choisir parmi : {options}.",
    },
    "predict_data_changed": {
        "en": (
            "the data differ from those of the estimation (units or periods do not match); "
            "the stored residuals and fitted values no longer apply. Re-estimate on the "
            "current data."
        ),
        "fr": (
            "les données diffèrent de celles de l'estimation (unités ou périodes différentes) ; "
            "les résidus et valeurs ajustées conservés ne s'appliquent plus. Ré-estimer sur "
            "les données actuelles."
        ),
    },
    "xd_unit_one_step": {
        "en": (
            "boot_type='unit' requires the two-step estimator, but this fit fell back to one step."
        ),
        "fr": (
            "boot_type='unit' exige l'estimateur à deux pas, mais cet ajustement est revenu à "
            "un pas."
        ),
    },
    "warn_wind_not_applied": {
        "en": (
            "the Windmeijer correction could not be applied; the cluster-robust variance is "
            "reported (vce_applied = False)."
        ),
        "fr": (
            "la correction de Windmeijer n'a pas pu être appliquée ; la variance robuste par "
            "clusters est rapportée (vce_applied = False)."
        ),
    },
    "warn_wind_same_threshold": {
        "en": (
            "W2 was built at the first-step threshold, so the Windmeijer standard errors are "
            "approximate (wind_same_threshold = 0)."
        ),
        "fr": (
            "W2 a été construit au seuil de première étape : les écarts-types de Windmeijer sont "
            "approchés (wind_same_threshold = 0)."
        ),
    },
    "warn_joint_unavailable": {
        "en": (
            "the joint variance is not available; the slope standard errors treat the threshold "
            "as known (joint_vce = False)."
        ),
        "fr": (
            "la variance conjointe n'est pas disponible ; les écarts-types des pentes traitent "
            "le seuil comme connu (joint_vce = False)."
        ),
    },
    "warn_q_few_values": {
        "en": (
            "q takes {n} distinct values near the threshold (q_nvals_bw); the joint variance "
            "assumes a continuous q. See cov_cond, ar1_cond and ar2_cond."
        ),
        "fr": (
            "q prend {n} valeurs distinctes près du seuil (q_nvals_bw) ; la variance conjointe "
            "suppose un q continu. Voir cov_cond, ar1_cond et ar2_cond."
        ),
    },
    # ---------------------------------------------------------------- data checks
    "xd_const_unit": {
        "en": (
            "{name} does not vary over time within any unit of the estimation sample: the "
            "{method} transformation removes it, so its coefficient is not identified "
            "(remove it, or model it through the unit effects)."
        ),
        "fr": (
            "{name} ne varie dans le temps pour aucune unité de l'échantillon d'estimation : "
            "la transformation {method} l'élimine, son coefficient n'est donc pas identifié "
            "(le retirer, ou le modéliser par les effets d'unité)."
        ),
    },
    "xd_const_time": {
        "en": (
            "{name} takes the same value for all units in every period: time_effects removes "
            "it, so its coefficient is not identified."
        ),
        "fr": (
            "{name} prend la même valeur pour toutes les unités à chaque période : "
            "time_effects l'élimine, son coefficient n'est donc pas identifié."
        ),
    },
    "xd_q_const_unit": {
        "en": (
            "The threshold variable {q} does not vary over time within any unit: the {method} "
            "transformation removes the regime indicator, so the regime shift is not "
            "identified."
        ),
        "fr": (
            "La variable de seuil {q} ne varie dans le temps pour aucune unité : la "
            "transformation {method} élimine l'indicateur de régime, le changement de régime "
            "n'est donc pas identifié."
        ),
    },
    "xd_q_const_time": {
        "en": (
            "The threshold variable {q} takes the same value for all units in every period: "
            "time_effects removes the regime indicator, so the regime shift is not identified."
        ),
        "fr": (
            "La variable de seuil {q} prend la même valeur pour toutes les unités à chaque "
            "période : time_effects élimine l'indicateur de régime, le changement de régime "
            "n'est donc pas identifié."
        ),
    },
    "xd_q_no_values": {
        "en": "The threshold variable {q} has no usable values in the history sample.",
        "fr": (
            "La variable de seuil {q} n'a aucune valeur utilisable dans l'échantillon d'historique."
        ),
    },
    "xd_q_no_variation": {
        "en": "The threshold variable {q} varies too little: the threshold grid would be empty.",
        "fr": "La variable de seuil {q} varie trop peu : la grille de seuils serait vide.",
    },
    "xd_few_units": {
        "en": "At least 5 units with two usable observations are needed (got {n}).",
        "fr": "Il faut au moins 5 unités avec deux observations utilisables (reçu : {n}).",
    },
    "xd_iv_alloc": {
        "en": (
            "The instrument matrix would be too large before empty columns are removed "
            "(up to {cols} columns and {cells} cells over a span of {span} periods). "
            "Set a tighter maxlag and/or collapse=True."
        ),
        "fr": (
            "La matrice d'instruments serait trop grande avant suppression des colonnes vides "
            "(jusqu'à {cols} colonnes et {cells} cellules sur {span} périodes). "
            "Fixez un maxlag plus serré et/ou collapse=True."
        ),
    },
    "xd_few_rows": {
        "en": "Fewer than 20 usable equations remain after the transformation (got {n}).",
        "fr": "Moins de 20 équations utilisables après la transformation (reçu : {n}).",
    },
    "xd_z_ill": {
        "en": (
            "The instrument matrix is ill-conditioned: some columns are nearly, but not "
            "exactly, linear combinations of others. A smaller instrument set (collapse, "
            "maxlag) can help, as can rescaling nearly equal instruments."
        ),
        "fr": (
            "La matrice d'instruments est mal conditionnée : certaines colonnes sont presque, "
            "sans l'être exactement, des combinaisons linéaires d'autres. Un jeu d'instruments "
            "plus petit (collapse, maxlag) peut aider, de même que le changement d'échelle "
            "d'instruments presque égaux."
        ),
    },
    "xd_td_gone": {
        "en": (
            "{names} is removed by the unit and time effects together: it has the form a_i + g_t "
            "(for example, firm age = year - founding year), which the {method} transformation "
            "and time_effects remove exactly, so its coefficient is not identified. Remove it, "
            "or drop time_effects."
        ),
        "fr": (
            "{names} est supprimé par les effets d'unité et de temps conjoints : il a la forme "
            "a_i + g_t (par exemple l'âge d'une firme = année - année de création), que la "
            "transformation {method} et time_effects suppriment exactement, donc son coefficient "
            "n'est pas identifié. Le retirer, ou abandonner time_effects."
        ),
    },
    "xd_common_few": {
        "en": (
            "{dropped} instrument column(s) that repeat the constant instruments (variables "
            "common to all units in each period) were dropped, leaving {left} instruments for "
            "{params} coefficients; at least {need} are needed. Add instruments (a wider maxlag, "
            "or iv) or remove such variables."
        ),
        "fr": (
            "{dropped} colonne(s) d'instruments qui répètent les constantes (variables communes "
            "à toutes les unités à chaque période) ont été supprimées, laissant {left} "
            "instruments pour {params} coefficients ; il en faut au moins {need}. Ajouter des "
            "instruments (maxlag plus large, ou iv) ou retirer ces variables."
        ),
    },
    "xd_profile_flat": {
        "en": (
            "The GMM criterion is flat over the admitted grid: every candidate threshold gives "
            "the same fit (for example, q takes few values, so all admitted candidates give the "
            "same regime split). The threshold is not identified on this grid."
        ),
        "fr": (
            "Le critère GMM est plat sur la grille admise : tous les seuils candidats donnent le "
            "même ajustement (par exemple q prend peu de valeurs, donc tous les candidats "
            "admis donnent le même partage des régimes). Le seuil n'est pas identifié sur cette "
            "grille."
        ),
    },
    "xd_no_gamma": {
        "en": (
            "Point estimation failed: no threshold admitted a valid GMM solve. Possible causes: "
            "too few units or periods, too many instruments relative to N, weak threshold "
            "identification, or no variation of q on the grid. Remedies: collapse, a tighter "
            "maxlag, a larger trim."
        ),
        "fr": (
            "L'estimation ponctuelle a échoué : aucun seuil n'a permis une résolution GMM valide. "
            "Causes possibles : trop peu d'unités ou de périodes, trop d'instruments par rapport "
            "à N, seuil mal identifié, ou q sans variation sur la grille. Remèdes : collapse, "
            "un maxlag plus serré, un trim plus grand."
        ),
    },
    "xd_variance_failed": {
        "en": "The cluster-robust variance could not be computed at the final estimate.",
        "fr": "La variance robuste par clusters n'a pas pu être calculée à l'estimation finale.",
    },
    "opt_td_boot_type_unit": {
        "en": (
            'boot_type="unit" is not available with time_effects: resampling the units '
            "changes the projection that removes the time effects in every draw, and that "
            'projection is not replayed. Use boot_type="wild", or drop time_effects.'
        ),
        "fr": (
            'boot_type="unit" n\'est pas disponible avec time_effects : le rééchantillonnage '
            "des unités modifie à chaque tirage la projection qui élimine les effets "
            "temporels, et cette projection n'est pas rejouée. Utiliser "
            'boot_type="wild", ou retirer time_effects.'
        ),
    },
    "opt_td_coef_boot": {
        "en": (
            'coef_boot="twostep" is not available with time_effects: the two-step replay '
            "would have to recompute the time-effects projection in every draw. Use "
            '"onestep" or "none".'
        ),
        "fr": (
            'coef_boot="twostep" n\'est pas disponible avec time_effects : le rejeu en deux '
            "étapes devrait recalculer à chaque tirage la projection des effets temporels. "
            'Utiliser "onestep" ou "none".'
        ),
    },
}
