"""Texts of the tables in English and French (layer 6)."""

from __future__ import annotations

from pyxtdpthresh._types import Lang

LABELS: dict[str, dict[str, str]] = {
    "dep_var": {"en": "Dependent variable", "fr": "Variable dépendante"},
    "lower": {"en": "Lower regime", "fr": "Régime bas"},
    "change": {"en": "Change at the threshold", "fr": "Changement au seuil"},
    "upper": {"en": "Upper regime", "fr": "Régime haut"},
    "n_obs": {"en": "Observations", "fr": "Observations"},
    "n_units": {"en": "Units", "fr": "Unités"},
    "n_instruments": {"en": "Instruments", "fr": "Instruments"},
    "hansen_p": {"en": "Hansen J (p-value)", "fr": "J de Hansen (p)"},
    "ar1_p": {"en": "AR(1) (p-value)", "fr": "AR(1) (p)"},
    "ar2_p": {"en": "AR(2) (p-value)", "fr": "AR(2) (p)"},
    "linearity_p": {"en": "Linearity test (p-value)", "fr": "Test de linéarité (p)"},
    "gamma": {"en": "Threshold γ̂", "fr": "Seuil γ̂"},
    "gamma_ci": {"en": "Threshold {level:g} % interval", "fr": "Seuil, intervalle à {level:g} %"},
    "method": {"en": "Transformation", "fr": "Transformation"},
    "shape": {"en": "Threshold effect", "fr": "Effet de seuil"},
    "estimator": {"en": "Estimator", "fr": "Estimateur"},
    "jump": {"en": "jump", "fr": "saut"},
    "kink": {"en": "kink", "fr": "kink"},
    "two_step": {"en": "two-step", "fr": "deux pas"},
    "one_step": {"en": "one-step", "fr": "un pas"},
    "se": {"en": "Standard errors in parentheses.", "fr": "Écarts-types entre parenthèses."},
    "t": {"en": "t-statistics in parentheses.", "fr": "Statistiques t entre parenthèses."},
    "p": {"en": "p-values in parentheses.", "fr": "p-values entre parenthèses."},
    "ci": {
        "en": "{level:g} % confidence intervals in brackets.",
        "fr": "Intervalles de confiance à {level:g} % entre crochets.",
    },
    "title": {
        "en": "Dynamic panel threshold model",
        "fr": "Modèle dynamique de panel à seuil",
    },
    "threshold_var": {"en": "Threshold variable", "fr": "Variable de seuil"},
    "coef": {"en": "Coef.", "fr": "Coef."},
    "std_err": {"en": "Std. err.", "fr": "Éc.-type"},
    "z": {"en": "z", "fr": "z"},
    "p_z": {"en": "P>|z|", "fr": "P>|z|"},
    "conf_int": {"en": "[{level:g} % conf. interval]", "fr": "[IC à {level:g} %]"},
    "gamma_ci_kinds": {
        "en": "Threshold interval: grid bootstrap (xtdpthresh) or asymptotic (xthenreg).",
        "fr": "Intervalle du seuil : grid bootstrap (xtdpthresh) ou asymptotique (xthenreg).",
    },
}


def label(key: str, lang: Lang, **fields: object) -> str:
    """Text ``key`` in ``lang`` with ``fields`` substituted."""
    return LABELS[key][lang].format(**fields)
