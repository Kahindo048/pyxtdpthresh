"""Messages of the user tools of ``extras`` (layer 0): plots, tables, diagnostics.

These are the package's own (Stata has no counterpart), so they carry a key and no return code.
"""

from __future__ import annotations

EXTRA_MESSAGES: dict[str, dict[str, str]] = {
    "plot_unknown_kind": {
        "en": "Unknown plot {kind!r}; choose one of: {options}.",
        "fr": "Graphique {kind!r} inconnu ; choisir parmi : {options}.",
    },
    "plot_needs_ci": {
        "en": "plot({kind!r}) needs the grid-bootstrap confidence set of the threshold: "
        "estimate with bootstrap=True.",
        "fr": "plot({kind!r}) exige l'ensemble de confiance du seuil par grid bootstrap : "
        "estimer avec bootstrap=True.",
    },
    "plot_needs_linearity": {
        "en": "plot('linearity') needs the bootstrap linearity test: estimate with "
        "bootstrap=True and linearity_test=True.",
        "fr": "plot('linearity') exige le test de linéarité par bootstrap : estimer avec "
        "bootstrap=True et linearity_test=True.",
    },
    "plot_linearity_undefined": {
        "en": "The linearity test has no statistic to draw (the linear model or the threshold "
        "grid could not be solved).",
        "fr": "Le test de linéarité n'a pas de statistique à tracer (le modèle linéaire ou la "
        "grille de seuils n'a pas pu être résolu).",
    },
    "plot_unknown_variable": {
        "en": "{name!r} is not a regressor of the model; choose one of: {options}.",
        "fr": "{name!r} n'est pas un régresseur du modèle ; choisir parmi : {options}.",
    },
    "plot_no_variable": {
        "en": "plot('effect') needs var=...; choose one of: {options}.",
        "fr": "plot('effect') exige var=... ; choisir parmi : {options}.",
    },
    "plot_format": {
        "en": "Cannot save a figure as {suffix!r}; use .png, .pdf or .svg.",
        "fr": "Impossible d'enregistrer une figure en {suffix!r} ; utiliser .png, .pdf ou .svg.",
    },
    "plot_empty": {
        "en": "Nothing to draw for plot({kind!r}): {reason}.",
        "fr": "Rien à tracer pour plot({kind!r}) : {reason}.",
    },
    "table_unknown_model": {
        "en": "Cannot tabulate a {kind}: no extractor is registered for this result type.",
        "fr": "Impossible de présenter un {kind} : aucun extracteur n'est enregistré pour ce type.",
    },
    "table_no_models": {
        "en": "At least one fitted model is needed to build a table.",
        "fr": "Au moins un modèle estimé est nécessaire pour construire un tableau.",
    },
    "table_statistic": {
        "en": "statistic must be one of {options} (got {value!r}).",
        "fr": "statistic doit valoir l'une de {options} (reçu : {value!r}).",
    },
    "table_names_length": {
        "en": "{what} has {got} entries for {expected} models.",
        "fr": "{what} compte {got} entrées pour {expected} modèles.",
    },
    "table_missing_package": {
        "en": "{package} is needed to write {format} files; install it with: {command}",
        "fr": "{package} est nécessaire pour écrire des fichiers {format} ; l'installer avec : "
        "{command}",
    },
    "table_needs_bootstrap": {
        "en": "This table needs the grid-bootstrap confidence set: estimate with bootstrap=True.",
        "fr": "Ce tableau exige l'ensemble de confiance par grid bootstrap : estimer avec "
        "bootstrap=True.",
    },
    "robust_unknown_setting": {
        "en": "{name!r} is not an option of the estimator; the settings can be: {options}.",
        "fr": "{name!r} n'est pas une option de l'estimateur ; les réglages possibles sont : "
        "{options}.",
    },
    "robust_empty_setting": {
        "en": "The setting {name!r} needs a list of values to try.",
        "fr": "Le réglage {name!r} demande une liste de valeurs à essayer.",
    },
    "robust_stability_use": {
        "en": "use must be 'segments' or 'hull' (got {value!r}).",
        "fr": "use doit valoir 'segments' ou 'hull' (reçu : {value!r}).",
    },
    "plot_wrong_result": {
        "en": "plot({kind!r}) draws a {expected}: pass one.",
        "fr": "plot({kind!r}) trace un objet de type {expected} : en fournir un.",
    },
    "plot_xthenreg": {
        "en": (
            "plot({kind!r}) draws the result of xtdpthresh; the result of xthenreg has no graph "
            "(its table, intervals and summary are available)."
        ),
        "fr": (
            "plot({kind!r}) trace le résultat de xtdpthresh ; le résultat de xthenreg n'a pas "
            "de graphique (son tableau, ses intervalles et son résumé sont disponibles)."
        ),
    },
    "variable_suggest": {
        "en": "Did you mean {suggestions}?",
        "fr": "Vouliez-vous dire {suggestions} ?",
    },
    "variable_available": {
        "en": "Columns available: {columns}.",
        "fr": "Colonnes disponibles : {columns}.",
    },
    "balance_example": {
        "en": "For example {id} {unit} is missing {time} {periods}.",
        "fr": "Par exemple {id} {unit} n'a pas {time} {periods}.",
    },
    "augment_exists": {
        "en": "The column(s) {columns} already exist in the data; pass overwrite=True to replace "
        "them or a prefix to name the new ones differently.",
        "fr": "La ou les colonnes {columns} existent déjà dans les données ; passer overwrite=True "
        "pour les remplacer ou un prefix pour nommer autrement les nouvelles.",
    },
    "dataset_unknown": {
        "en": "Unknown dataset {name!r}; the bundled datasets are: {options}.",
        "fr": "Jeu de données {name!r} inconnu ; les jeux fournis sont : {options}.",
    },
    "sim_unknown_design": {
        "en": "Unknown design {name!r}; choose one of: {options}.",
        "fr": "Design {name!r} inconnu ; choisir parmi : {options}.",
    },
    "sim_unknown_parameter": {
        "en": "Unknown design parameter {name!r}; the parameters are: {options}.",
        "fr": "Paramètre de design {name!r} inconnu ; les paramètres sont : {options}.",
    },
    "sim_bad_size": {
        "en": "{name} must be at least {minimum} (got {value!r}).",
        "fr": "{name} doit valoir au moins {minimum} (reçu : {value!r}).",
    },
    "sim_bad_share": {
        "en": "unbalanced must be a share in [0, 1) (got {value!r}).",
        "fr": "unbalanced doit être une part dans [0, 1) (reçu : {value!r}).",
    },
    "sim_bad_alpha": {
        "en": "alpha must lie in (0, 1) (got {value!r}).",
        "fr": "alpha doit être dans (0, 1) (reçu : {value!r}).",
    },
    "sim_bad_correlation": {
        "en": "rho_eu must lie in (-1, 1) (got {value!r}).",
        "fr": "rho_eu doit être dans (-1, 1) (reçu : {value!r}).",
    },
}
