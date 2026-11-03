"""Help-file example of the unbalanced panel (F.6.1): the sample Stata drew, and both methods.

Stata drops 15% of the observations at random (``set seed 20260418``) and the firms with fewer
than four observations left, then runs ``xtdpthresh`` with ``method(fd)`` and ``method(fod)``.
The random sample is exported so that Python estimates on exactly the same rows.
"""

from __future__ import annotations

import gzip
import json
from pathlib import Path
from typing import Any

import pandas as pd

from validation.cases import _MATA_EXPORT, OUT_DIR, STATA_DIR
from validation.compare import read_matrix
from validation.estimation_cases import pack
from validation.search_cases import _E_NAME, _MATA_SC

ROOT = Path(__file__).resolve().parents[1] / "tests" / "golden"
GOLDEN = ROOT / "help_unbalanced_golden.json"
SAMPLE = ROOT / "help_unbalanced_sample.csv.gz"
LOG = STATA_DIR / "_run_help_unbalanced.log"
ARGS: dict[str, Any] = {
    "y": "invest",
    "x": (),
    "q": "debt",
    "endogenous": ("cashflow", "tobin_q", "debt"),
    "maxlag": (3, 8),
    "collapse": True,
    "bootstrap": False,
}
METHODS = ("fd", "fod")
_SCALARS = (
    "gamma", "obj", "twostep", "grid_admitted", "n", "n_iv", "n_units", "grid_effective",
    "stage1_gamma",
)  # fmt: skip
_NAMES = {**_E_NAME, "n_iv": "N_iv", "n_units": "N_units", "n": "N"}


def render_do() -> str:
    """Do-file: draw the sample, export it, and run both methods."""
    command = (
        "xtdpthresh invest, qx(debt) endogenous(cashflow tobin_q debt) maxlag(3 8) collapse "
        "noboot method({m})"
    )
    scalars = ", ".join(f'pyx_sc("e({_NAMES.get(n, n)})")' for n in _SCALARS)
    out = [
        "version 17",
        "set more off",
        "clear all",
        _MATA_EXPORT,
        _MATA_SC,
        'use "../data/invest.dta", clear',
        "xtset firm year",
        "set seed 20260418",
        "drop if runiform() < 0.15",
        "bysort firm: drop if _N < 4",
        'export delimited firm year invest tobin_q cashflow debt using "../out/hu_sample.csv", '
        "replace",
    ]
    for method in METHODS:
        tag = f"../out/hu_{method}"
        out += [
            f'display "@@CASE {method}"',
            f"capture noisily {command.format(m=method)}",
            'display "@@RC " _rc',
            "if _rc == 0 {",
            f'    mata: pyx_export("{tag}_sc.csv", ({scalars}))',
            f'    mata: pyx_export("{tag}_b.csv", st_matrix("e(b)"))',
            f'    mata: pyx_export("{tag}_vc.csv", st_matrix("e(V_cond)"))',
            "}",
        ]
    out.append("exit, clear")
    return "\n".join(out) + "\n"


def write_do(path: Path | None = None) -> Path:
    """Write ``validation/stata/help_unbalanced.do``."""
    path = path or STATA_DIR / "help_unbalanced.do"
    path.write_text(render_do(), encoding="ascii", errors="replace", newline="\n")
    return path


def freeze() -> Path:
    """Freeze the sample and the Stata results."""
    from validation.spec_cases import parse_log

    parsed = parse_log(LOG.read_text(encoding="utf-8", errors="replace"))
    frame = pd.read_csv(OUT_DIR / "hu_sample.csv")
    with gzip.open(SAMPLE, "wt", encoding="utf-8", newline="\n") as handle:
        frame.to_csv(handle, index=False)
    cases: dict[str, dict[str, Any]] = {}
    for method in METHODS:
        entry: dict[str, Any] = dict(parsed[method])
        if entry["rc"] == 0:
            tag = OUT_DIR / f"hu_{method}"
            values = read_matrix(Path(f"{tag}_sc.csv")).ravel()
            entry["scalars"] = dict(zip(_SCALARS, (float(v) for v in values), strict=True))
            entry["b"] = pack(read_matrix(Path(f"{tag}_b.csv")))
            entry["vcond"] = pack(read_matrix(Path(f"{tag}_vc.csv")))
        cases[method] = entry
    GOLDEN.write_text(
        json.dumps({"meta": {"stata": "Stata 17.0 MP", "xtdpthresh": "0.9.38"}, "cases": cases}),
        encoding="utf-8",
        newline="\n",
    )
    return GOLDEN


def sample() -> pd.DataFrame:
    """The panel Stata drew."""
    return pd.read_csv(SAMPLE)


if __name__ == "__main__":
    import sys

    print(freeze() if "--freeze" in sys.argv else write_do())
