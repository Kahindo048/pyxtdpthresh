"""Coverage report of Monte Carlo experiments: one table and the three graphs (layer 6).

``coverage_table(results)`` gathers one row per experiment: bias and RMSE of the threshold, its
coverage (accepted segments and hull, with the Monte Carlo error), the share of incomplete
confidence sets, the coverage of the slopes, the rejection rate of the linearity test and of the
shifted thresholds.  ``coverage_report(results, directory)`` writes the table (CSV and Markdown)
and the graphs ``coverage``, ``power`` and ``distribution`` in English and French.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from pathlib import Path

import numpy as np
import pandas as pd

from pyxtdpthresh._types import Lang
from pyxtdpthresh.extras.simulation.montecarlo import MonteCarloResult

#: Columns of the Markdown table, with their headers (English), in order.
MARKDOWN_COLUMNS = {
    "experiment": "experiment",
    "reps": "reps",
    "failed": "failed",
    "gamma_bias": "bias",
    "gamma_rmse": "RMSE",
    "coverage_segments": "coverage (segments)",
    "coverage_hull": "coverage (hull)",
    "incomplete": "incomplete",
    "slopes_coverage_mean": "slopes (mean)",
    "linearity_rate": "linearity",
}

Experiments = MonteCarloResult | Sequence[MonteCarloResult] | Mapping[str, MonteCarloResult]


def _row(name: str, run: MonteCarloResult) -> dict[str, object]:
    estimates = run.estimates()
    names = [p for p in estimates.index if p != "gamma"]
    slopes = estimates.loc[names, "coverage"].to_numpy(float) if names else np.empty(0)
    slopes = slopes[np.isfinite(slopes)]
    coverage = run.threshold_coverage()
    gamma = estimates.loc["gamma"] if "gamma" in estimates.index else None
    linearity = run.linearity()
    row: dict[str, object] = {
        "experiment": name,
        "design": run.design.name,
        "n": run.n,
        "t": run.t,
        "jump": run.design.jump if run.design.has_threshold else math.nan,
        "reps": run.reps,
        "failed": run.n_failed,
        "gamma_bias": float(gamma["bias"]) if gamma is not None else math.nan,
        "gamma_rmse": float(gamma["rmse"]) if gamma is not None else math.nan,
        "gamma_median_bias": float(gamma["median_bias"]) if gamma is not None else math.nan,
        "coverage_segments": float(coverage.loc["segments", "coverage"]),
        "mcse_segments": float(coverage.loc["segments", "mcse"]),
        "coverage_hull": float(coverage.loc["hull", "coverage"]),
        "incomplete": float(coverage.loc["segments", "incomplete"]),
        "slopes_coverage_mean": float(np.mean(slopes)) if slopes.size else math.nan,
        "slopes_coverage_min": float(np.min(slopes)) if slopes.size else math.nan,
        "linearity_rate": float(linearity["rate"]),
        "linearity_kind": linearity["kind"],
    }
    for shift, value in run.power()["rejection"].items():
        row[f"reject_{float(shift):g}"] = float(value)
    return row


def coverage_table(results: Experiments, *, lang: Lang | None = None) -> pd.DataFrame:
    """Return one row per experiment with the statistics a coverage report shows.

    ``results`` is one experiment, a list of them or a ``{name: result}`` mapping; unnamed
    experiments are named after their sample size, periods and jump (in ``lang``).
    """
    from pyxtdpthresh.extras.plotting._mc import named
    from pyxtdpthresh.extras.plotting.style import resolve_lang

    runs = named(results, resolve_lang(lang))
    return pd.DataFrame([_row(name, run) for name, run in runs]).set_index("experiment", drop=False)


def _format(value: object, lang: Lang) -> str:
    if isinstance(value, float | np.floating):
        text = "-" if not math.isfinite(float(value)) else f"{float(value):.3f}"
        return text.replace(".", ",") if lang == "fr" else text
    return str(value)


def coverage_markdown(table: pd.DataFrame, *, lang: Lang = "en") -> str:
    """Return ``table`` as a Markdown table (decimal comma in French)."""
    headers = {
        "en": MARKDOWN_COLUMNS,
        "fr": {
            "experiment": "expérience",
            "reps": "réplications",
            "failed": "échecs",
            "gamma_bias": "biais",
            "gamma_rmse": "REQM",
            "coverage_segments": "couverture (segments)",
            "coverage_hull": "couverture (enveloppe)",
            "incomplete": "incomplets",
            "slopes_coverage_mean": "pentes (moyenne)",
            "linearity_rate": "linéarité",
        },
    }[lang]
    lines = ["| " + " | ".join(headers.values()) + " |", "|" + "---|" * len(headers)]
    for _, row in table.iterrows():
        cells = [_format(row[column], lang) for column in headers]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines) + "\n"


def coverage_report(
    results: Experiments,
    directory: str | Path,
    *,
    langs: Sequence[Lang] = ("en", "fr"),
    stem: str = "coverage",
) -> dict[str, Path]:
    """Write the table (CSV, Markdown) and the three graphs of the experiments in ``directory``.

    Returns the files written, by name (``table``, ``markdown_en``, ``coverage_en``...).
    """
    from pyxtdpthresh.extras.plotting import MONTE_CARLO_KINDS, plot
    from pyxtdpthresh.extras.plotting.style import save_figure

    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    written: dict[str, Path] = {}
    table = coverage_table(results, lang=langs[0])
    written["table"] = target / f"{stem}.csv"
    table.to_csv(written["table"], index=False)
    for lang in langs:
        localized = coverage_table(results, lang=lang)
        markdown = target / f"{stem}_{lang}.md"
        markdown.write_text(coverage_markdown(localized, lang=lang), encoding="utf-8")
        written[f"markdown_{lang}"] = markdown
        for kind in MONTE_CARLO_KINDS:
            figure = plot(results, kind, lang=lang)  # type: ignore[arg-type]
            written[f"{kind}_{lang}"] = save_figure(figure, target / f"{kind}_{lang}.png")[0]
    return written
