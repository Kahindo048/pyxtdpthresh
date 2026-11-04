"""Gallery of the graphs of block I.1 on Hansen's investment panel (565 firms).

Writes every graph in English and French (PNG) under ``docs/galerie/``, for the jump model of
the help example and for its kink version.  Run from the project root:

    PYTHONPATH=. python tools/galerie.py [output_directory]
"""

from __future__ import annotations

import sys
import warnings
from pathlib import Path

from validation.bootstrap_cases import CASES
from validation.variance_cases import frame

from pyxtdpthresh._errors import PyxdpthreshWarning
from pyxtdpthresh.extras.plotting import FIT_KINDS, plot
from pyxtdpthresh.models.xtdpthresh.fit import fit_point

ROOT = Path(__file__).resolve().parents[1]
SEED_CASES = {"jump": "full_help", "kink": "full_help_kink"}


def estimate(name: str):  # type: ignore[no-untyped-def]
    """Fit the full-panel case ``name`` of the validation suite (the help example)."""
    case = next(c for c in CASES if c.name == name)
    args = case.full_args()
    y, q, x = args.pop("y"), args.pop("q"), args.pop("x", ())
    args.update(n_boot=299, grid_ci=100)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", PyxdpthreshWarning)
        return fit_point(frame(case), y, x, q=q, id="firm", time="year", **args)


def main(out: Path) -> None:
    """Write the gallery."""
    out.mkdir(parents=True, exist_ok=True)
    for model, name in SEED_CASES.items():
        fit = estimate(name)
        first = next(iter(fit.names)).partition(":")[2]
        for kind in FIT_KINDS:
            options = {"var": fit.spec.q if model == "kink" else first} if kind == "effect" else {}
            for lang in ("en", "fr"):
                plot(fit, kind, lang=lang, path=out / f"{model}_{kind}_{lang}.png", **options)  # type: ignore[arg-type]
        print(model, "gamma =", round(fit.search.fit.gamma, 4), "-", len(FIT_KINDS), "graphs")


def robust(out: Path) -> None:
    """Write the robustness graph of the help example (default settings) in English and French."""
    from pyxtdpthresh.extras.robustness import robustness

    case = next(c for c in CASES if c.name == "full_help")
    args = case.full_args()
    y, q, x = args.pop("y"), args.pop("q"), args.pop("x", ())
    args.update(n_boot=299, grid_ci=100)
    result = robustness(frame(case), y, x, q=q, id="firm", time="year", **args)
    for lang in ("en", "fr"):
        result.plot(lang=lang, path=out / f"robustesse_{lang}.png")
    result.table.to_csv(out / "robustesse.csv")
    print("robustness stability index:", round(result.stability(), 3))


def tables(out: Path) -> None:
    """Write the tables of the help example (FD, FOD, kink, ``xthenreg``) in every format."""
    from validation.cases import load_invest

    from pyxtdpthresh.extras.reporting import ThresholdStargazer, diagnose, summary, to_json
    from pyxtdpthresh.models.xthenreg.design import prepare_data
    from pyxtdpthresh.models.xthenreg.estimate import estimate as xthenreg_estimate

    fits = [estimate(name) for name in ("full_help", "full_help_fod", "full_help_kink")]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        data = prepare_data(
            load_invest(max_year=1980), "invest", "debt", (), ("cashflow", "tobin_q", "debt"),
            id="firm", time="year",
        )  # fmt: skip
        henreg = xthenreg_estimate(data, grid_num=50)
    names = ["xtdpthresh FD", "xtdpthresh FOD", "xtdpthresh kink", "xthenreg"]
    for lang in ("en", "fr"):
        table = ThresholdStargazer(
            [*fits, henreg], names, lang=lang, title="Dynamic threshold models", label="tab:dpt"
        )  # fmt: skip
        stem = out / f"tableau_{lang}"
        table.to_latex(stem.with_suffix(".tex"))
        table.to_html(stem.with_suffix(".html"))
        table.to_markdown(stem.with_suffix(".md"))
        table.to_text(stem.with_suffix(".txt"))
        table.to_csv(stem.with_suffix(".csv"))
        table.to_word(stem.with_suffix(".docx"))
        table.to_excel(stem.with_suffix(".xlsx"))
    (out / "resume_fd.txt").write_text(summary(fits[0]), encoding="utf-8")
    for lang in ("en", "fr"):
        parts = [f"== {n} ==\n{diagnose(f, lang)}" for n, f in zip(names, fits, strict=False)]
        report = "\n".join(parts)
        (out / f"diagnostic_{lang}.txt").write_text(report, encoding="utf-8")
    to_json(fits[0], out / "resultat_fd.json")
    from pyxtdpthresh.extras.reporting import settings_log

    for lang in ("en", "fr"):
        (out / f"journal_{lang}.txt").write_text(str(settings_log(fits[0], lang)), encoding="utf-8")
    print("tables written to", out)


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "docs" / "galerie"
    main(target)
    tables(target)
    robust(target)
