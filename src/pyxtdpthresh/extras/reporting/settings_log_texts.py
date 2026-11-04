"""Texts of the journal of effective settings, in English and French (layer 6)."""

from __future__ import annotations

#: Title of each section.
SECTIONS: dict[str, dict[str, str]] = {
    "sample": {"en": "Sample", "fr": "Échantillon"},
    "model": {"en": "Model", "fr": "Modèle"},
    "instruments": {"en": "Instruments and weights", "fr": "Instruments et pondération"},
    "search": {"en": "Threshold search", "fr": "Recherche du seuil"},
    "inference": {"en": "Inference", "fr": "Inférence"},
    "software": {"en": "Software", "fr": "Logiciel"},
}

#: Label of each entry, by stable key.
LABELS: dict[str, dict[str, str]] = {
    "n_units": {"en": "units with equations", "fr": "unités avec équations"},
    "n_equations": {"en": "equations (stacked rows)", "fr": "équations (lignes empilées)"},
    "n_units_dropped": {
        "en": "units dropped (fewer than two equation rows)",
        "fr": "unités écartées (moins de deux lignes d'équation)",
    },
    "history": {"en": "history used for lags and instruments", "fr": "historique des retards"},
    "method": {"en": "transformation", "fr": "transformation"},
    "shape": {"en": "threshold effect", "fr": "effet de seuil"},
    "dynamics": {"en": "dynamics", "fr": "dynamique"},
    "time_effects": {"en": "time effects (td)", "fr": "effets temporels (td)"},
    "threshold_variable": {"en": "threshold variable", "fr": "variable de seuil"},
    "x": {"en": "strictly exogenous regressors", "fr": "régresseurs strictement exogènes"},
    "exogenous": {
        "en": "exogenous (instrumented in levels)",
        "fr": "exogènes (instruments en niveaux)",
    },
    "endogenous": {"en": "endogenous regressors", "fr": "régresseurs endogènes"},
    "predetermined": {"en": "predetermined regressors", "fr": "régresseurs prédéterminés"},
    "iv": {"en": "external instruments", "fr": "instruments externes"},
    "n_instruments": {"en": "instruments kept", "fr": "instruments conservés"},
    "collapse": {"en": "collapsed instruments", "fr": "instruments regroupés"},
    "iv_collapse": {"en": "collapsed external instruments", "fr": "instruments externes regroupés"},
    "maxlag": {"en": "instrument lags", "fr": "retards des instruments"},
    "removed_common": {
        "en": "columns removed: common to all units",
        "fr": "colonnes retirées : communes à toutes les unités",
    },
    "removed_zero": {"en": "columns removed: empty", "fr": "colonnes retirées : vides"},
    "removed_duplicate": {
        "en": "columns removed: duplicates",
        "fr": "colonnes retirées : doublons",
    },
    "removed_dependent": {
        "en": "columns removed: linear combinations",
        "fr": "colonnes retirées : combinaisons linéaires",
    },
    "dependent_residual": {
        "en": "largest residual of a removed combination",
        "fr": "plus grand résidu d'une combinaison retirée",
    },
    "first_weight": {"en": "first-step weight", "fr": "poids de première étape"},
    "estimator": {"en": "estimator", "fr": "estimateur"},
    "grid_type": {"en": "grid of thresholds", "fr": "grille de seuils"},
    "grid_requested": {"en": "grid points requested", "fr": "points de grille demandés"},
    "grid_effective": {"en": "grid points evaluated", "fr": "points de grille évalués"},
    "grid_admitted": {"en": "grid points admitted", "fr": "points de grille admis"},
    "q_range": {"en": "range searched", "fr": "intervalle exploré"},
    "trim": {"en": "trimming of the threshold variable", "fr": "élagage de la variable de seuil"},
    "min_regime": {"en": "smallest regime allowed", "fr": "plus petit régime admis"},
    "kink_refined": {"en": "kink estimate refined", "fr": "estimation du kink affinée"},
    "vce": {"en": "variance estimator", "fr": "estimateur de variance"},
    "joint_vce": {
        "en": "variance joint with the threshold",
        "fr": "variance conjointe avec le seuil",
    },
    "bandwidth": {"en": "kernel bandwidth of the threshold", "fr": "fenêtre du noyau du seuil"},
    "level": {"en": "confidence level (%)", "fr": "niveau de confiance (%)"},
    "bootstrap": {"en": "bootstrap run", "fr": "bootstrap exécuté"},
    "boot_type": {"en": "bootstrap type", "fr": "type de bootstrap"},
    "n_boot": {"en": "bootstrap draws", "fr": "tirages de bootstrap"},
    "seed": {"en": "bootstrap seed", "fr": "graine du bootstrap"},
    "grid_ci": {"en": "points of the confidence-set grid", "fr": "points de la grille de l'IC"},
    "ci_unresolved": {
        "en": "confidence-set points unresolved",
        "fr": "points de l'ensemble de confiance non résolus",
    },
    "package": {"en": "package", "fr": "paquet"},
    "reference": {"en": "reproduces", "fr": "reproduit"},
}

#: Words used in the values.
WORDS: dict[str, dict[str, str]] = {
    "yes": {"en": "yes", "fr": "oui"},
    "no": {"en": "no", "fr": "non"},
    "none": {"en": "none", "fr": "aucun"},
    "fd": {"en": "first differences", "fr": "différences premières"},
    "fod": {"en": "forward orthogonal deviations", "fr": "déviations orthogonales vers l'avant"},
    "jump": {"en": "jump", "fr": "saut"},
    "kink": {"en": "kink (continuous)", "fr": "kink (continu)"},
    "dynamic": {"en": "dynamic (lagged y added)", "fr": "dynamique (retard de y ajouté)"},
    "static": {"en": "static", "fr": "statique"},
    "panel": {"en": "whole panel", "fr": "panel entier"},
    "sample": {"en": "estimation sample only", "fr": "échantillon d'estimation seulement"},
    "twostep": {"en": "two-step GMM", "fr": "GMM en deux étapes"},
    "onestep": {"en": "one-step GMM (fallback)", "fr": "GMM en une étape (repli)"},
    "weight_0": {
        "en": "MA(1) (first differences) or (Z'Z)^-1 (deviations)",
        "fr": "MA(1) (différences) ou (Z'Z)^-1 (déviations)",
    },
    "weight_1": {"en": "(Z'Z)^-1 substituted", "fr": "(Z'Z)^-1 substitué"},
    "weight_2": {"en": "identity substituted", "fr": "identité substituée"},
    "uniform": {"en": "uniform", "fr": "uniforme"},
    "quantile": {"en": "quantiles", "fr": "quantiles"},
    "wild": {"en": "wild", "fr": "wild"},
    "unit": {"en": "units resampled", "fr": "rééchantillonnage des unités"},
    "unlimited": {"en": "unlimited", "fr": "illimité"},
    "to": {"en": "to", "fr": "à"},
    "unset": {
        "en": "not set: the draws come from an unrecorded random stream, "
        "the run cannot be repeated",
        "fr": "non fixée : les tirages viennent d'un flux aléatoire non enregistré, "
        "l'exécution n'est pas reproductible",
    },
    "not_run": {"en": "not run", "fr": "non exécuté"},
    "header": {"en": "Settings journal", "fr": "Journal des réglages"},
}
