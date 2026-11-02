"""Validation of the data layer against Stata (block C.1; files ``dp_*``).

Three versions of the investment data are built by the same deterministic rules in Stata and
in pandas: strongly balanced, weakly balanced (every firm loses one, different, year) and
unbalanced with calendar gaps; values of ``cashflow`` are set to missing by a rule.  Stata
exports ``xtset``'s verdict on the balance, ``L.invest`` and ``L2.invest`` row by row, and the
complete-case flag of ``marksample``/``markout``.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from validation.cases import _MATA_EXPORT, OUT_DIR, STATA_DIR, load_invest
from validation.compare import read_matrix

GOLDEN = Path(__file__).resolve().parents[1] / "tests" / "golden" / "data_golden.json"
TAG = "dp"
SCENARIOS = ("full", "weak", "unbal")
BALANCE_CODE = {"strongly balanced": 1.0, "weakly balanced": 2.0, "unbalanced": 3.0}

#: Stata statements (one per scenario) that thin the data out; mirrored by :func:`scenario_frame`.
_STATA_RULES = {
    "full": "* no deletion",
    "weak": "drop if year == `y0' + mod(firm, 15)",
    "unbal": "drop if mod(firm + 3*year, 11) == 0",
}

_DO_BODY = """\
foreach sc in full weak unbal {
    use "../data/invest.dta", clear
    quietly summarize year
    local y0 = r(min)
    if "`sc'" == "weak" drop if year == `y0' + mod(firm, 15)
    if "`sc'" == "unbal" drop if mod(firm + 3*year, 11) == 0
    replace cashflow = . if mod(firm + year, 13) == 0
    xtset firm year
    sort firm year
    local code = 3
    if "`r(balanced)'" == "strongly balanced" local code = 1
    if "`r(balanced)'" == "weakly balanced" local code = 2
    generate double l1 = L.invest
    generate double l2 = L2.invest
    generate double cmp = !missing(invest, cashflow, tobin_q)
    mata: pyx_export("../out/dp_`sc'_balance.csv", `code')
    mata: pyx_export("../out/dp_`sc'_rows.csv", st_data(., ("firm", "year", "l1", "l2", "cmp")))
}
exit, clear
"""


def render_do() -> str:
    """Do-file that builds the three scenarios in Stata and exports the checks."""
    return "\n".join(["version 17", "set more off", "clear all", "", _MATA_EXPORT, _DO_BODY])


def write_do(path: Path | None = None) -> Path:
    """Write ``validation/stata/data_cases.do``."""
    path = path or STATA_DIR / "data_cases.do"
    path.write_text(render_do(), encoding="ascii", newline="\n")
    return path


def scenario_frame(name: str) -> pd.DataFrame:
    """The same thinned-out data as the Stata do-file, built with pandas."""
    df = load_invest(max_year=None, derived=False).copy()
    y0 = int(df["year"].min())
    if name == "weak":
        df = df[df["year"] != y0 + np.mod(df["firm"], 15)]
    elif name == "unbal":
        df = df[np.mod(df["firm"] + 3 * df["year"], 11) != 0]
    df = df.reset_index(drop=True)
    df.loc[np.mod(df["firm"] + df["year"], 13) == 0, "cashflow"] = np.nan
    return df.sample(frac=1.0, random_state=7).reset_index(drop=True)  # shuffled on purpose


def python_results(name: str) -> dict[str, np.ndarray]:
    """Same objects as the Stata export, computed with the package."""
    from pyxtdpthresh.data.panel import build_panel
    from pyxtdpthresh.data.sampling import complete_rows

    df = scenario_frame(name)
    panel = build_panel(df, ["invest", "cashflow", "tobin_q"], id="firm", time="year")
    invest = panel.column("invest")
    rows = np.column_stack(
        [
            np.asarray(panel.unit_labels)[panel.unit_of_row].astype(float),
            panel.time.astype(float),
            panel.lag(invest, 1),
            panel.lag(invest, 2),
            complete_rows(panel.values).astype(float),
        ]
    )
    return {"balance": np.array([[BALANCE_CODE[panel.balance]]]), "rows": rows}


def stata_results(out_dir: Path = OUT_DIR) -> dict[str, dict[str, np.ndarray]]:
    """Exports of the Stata run, grouped by scenario."""
    return {
        sc: {k: read_matrix(out_dir / f"{TAG}_{sc}_{k}.csv") for k in ("balance", "rows")}
        for sc in SCENARIOS
    }


def freeze(out_dir: Path = OUT_DIR, path: Path = GOLDEN) -> Path:
    """Freeze the Stata results into ``tests/golden/data_golden.json``."""
    master = {
        "meta": {"stata": "Stata 17.0 MP", "source": "validation/data_cases.py"},
        "stata": {
            n: {k: v.tolist() for k, v in o.items()} for n, o in stata_results(out_dir).items()
        },
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(master), encoding="utf-8", newline="\n")
    return path


if __name__ == "__main__":
    import sys

    print(freeze() if "--freeze" in sys.argv else write_do())
