"""``predict`` of ``xtdpthresh`` against Stata (G.8.4).

After the estimation of some cases of :mod:`validation.variance_cases`, Stata predicts the
residuals, the fit, the AR residuals and the regime, and the last one again with an ``if``.  The
series are exported with the keys; Python must reproduce them row by row.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from validation.cases import OUT_DIR, STATA_DIR
from validation.estimation_cases import DERIVED_STATA, MAX_FIRM, MAX_YEAR, pack
from validation.sample_cases import DATA
from validation.spec_cases import parse_log, stata_command
from validation.transform_cases import DATA2, EXTRA_STATA
from validation.variance_cases import CASES as VARIANCE_CASES
from validation.variance_cases import QDISC_STATA, VarCase

GOLDEN = Path(__file__).resolve().parents[1] / "tests" / "golden" / "predict_golden.json"
LOG = STATA_DIR / "_run_predict_cases.log"
NAMES = (
    "fd_jump", "fod_jump", "fd_kink", "fod_kink", "fd_td", "fod_td", "fod_gaps_wind",
    "fd_short_wind", "fod_alternate_wind", "fod_short", "full_help_fod",
)  # fmt: skip
CASES: tuple[VarCase, ...] = tuple(c for c in VARIANCE_CASES if c.name in NAMES)
#: Python ``kind`` and Stata option, in the column order of the export.
KINDS = (
    ("residuals", "residuals"),
    ("xb", "xb"),
    ("ar_residuals", "arresiduals"),
    ("regime", "regime"),
)
CONDITION = "year >= 1977"


def render_do(cases: tuple[VarCase, ...] | None = None) -> str:
    """Do-file that estimates every case, predicts and exports the series."""
    cases = CASES if cases is None else cases
    out = ["version 17", "set more off", "clear all"]
    for c in cases:
        if c.panel == "full":
            prep = ["egen double peer_q = mean(tobin_q), by(year)", *DATA[c.data][0]]
        else:
            prep = [
                f"keep if firm <= {MAX_FIRM} & year <= {MAX_YEAR}",
                *DERIVED_STATA,
                *EXTRA_STATA,
                QDISC_STATA,
                *DATA2[c.data][0],
            ]
        predictions = [f"predict double p_{k}, {opt}" for k, opt in KINDS]
        columns = " ".join(f"p_{k}" for k, _ in KINDS)
        out += [
            'use "../data/invest.dta", clear',
            "xtset firm year",
            *prep,
            f'display "@@CASE {c.name}"',
            f"capture noisily {stata_command(c.full_args())}",
            'display "@@RC " _rc',
            "if _rc == 0 {",
            *[f"    {line}" for line in predictions],
            "    predict double p_if, residuals",
            f"    replace p_if = . if !({CONDITION})",
            f'    export delimited firm year {columns} p_if using "../out/pr_{c.name}.csv", replace',
            "}",
            "",
        ]
    out.append("exit, clear")
    return "\n".join(out) + "\n"


def write_do(path: Path | None = None) -> Path:
    """Write ``validation/stata/predict_cases.do``."""
    path = path or STATA_DIR / "predict_cases.do"
    path.write_text(render_do(), encoding="ascii", errors="replace", newline="\n")
    return path


def freeze(log: Path = LOG, path: Path = GOLDEN, out_dir: Path = OUT_DIR) -> Path:
    """Freeze the Stata series into ``tests/golden/predict_golden.json``."""
    parsed = parse_log(log.read_text(encoding="utf-8", errors="replace"))
    cases: dict[str, dict[str, Any]] = {}
    for c in CASES:
        entry: dict[str, Any] = dict(parsed[c.name])
        if entry["rc"] == 0:
            table = pd.read_csv(out_dir / f"pr_{c.name}.csv")
            entry["keys"] = pack(table[["firm", "year"]].to_numpy(dtype=float))
            columns = [f"p_{k}" for k, _ in KINDS] + ["p_if"]
            entry["series"] = pack(table[columns].to_numpy(dtype=float))
        cases[c.name] = entry
    master = {"meta": {"stata": "Stata 17.0 MP", "xtdpthresh": "0.9.38"}, "cases": cases}
    path.write_text(json.dumps(master), encoding="utf-8", newline="\n")
    return path


def selected(frame: pd.DataFrame) -> np.ndarray:
    """Rows kept by :data:`CONDITION`."""
    return (frame["year"] >= 1977).to_numpy()


if __name__ == "__main__":
    import sys

    print(freeze() if "--freeze" in sys.argv else write_do())
