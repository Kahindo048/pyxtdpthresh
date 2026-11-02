"""Validation of the xthenreg linearity test (block D.4; files ``lt_*``).

The Stata side runs the **verbatim** body of ``maincode_0719`` (estimation, covariance and
bootstrap) after ``set seed``, and exports the sample sup-Wald statistic, the covariance of the
tested coefficients at every grid point, the supremum of each bootstrap replication and the
p-value.  The bootstrap weights come from Stata's own generator, so the comparison also checks
the reproduction of ``set seed`` / ``invnormal(uniform())`` inside a real command.
"""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import numpy as np

from validation.cases import (
    _MATA_EXPORT,
    OUT_DIR,
    STATA_DIR,
    XTHENREG_CASES,
    XthenregCase,
)
from validation.compare import read_matrix

ADO = Path.home() / "ado" / "plus" / "x" / "xthenreg.ado"
GOLDEN = Path(__file__).resolve().parents[1] / "tests" / "golden" / "linearity_golden.json"
TAG = "lt"
BOOT = 40
GRID = 20
SEED = 2024


def linearity_cases() -> tuple[XthenregCase, ...]:
    """Dynamic and static, jump and kink, with and without external instruments."""
    by_tag = {c.tag: c for c in XTHENREG_CASES}
    out = []
    for src, new in (("c1", "l1"), ("c2", "l2"), ("c3", "l3"), ("c5", "l4"), ("c4", "l5")):
        out.append(replace(by_tag[src], tag=new, grid_num=GRID, boost=BOOT, seed=SEED))
    # specifications whose bootstrap p-value lies strictly between 0 and 1 (the first five
    # reject linearity so strongly that p = 0 whatever the arithmetic)
    common = {"y": "invest", "grid_num": GRID, "boost": BOOT, "seed": SEED, "max_year": 1980}
    out += [
        XthenregCase("p1", q="cashflow", endogenous=("debt",), static=True, **common),
        XthenregCase("p2", q="cashflow", endogenous=("debt",), **common),
        XthenregCase(
            "p3", q="tobin_q", endogenous=("cashflow", "tobin_q"), static=True, kink=True, **common
        ),
        XthenregCase("p4", q="debt", endogenous=("debt",), static=True, kink=True, **common),
    ]
    return tuple(out)


def _body() -> str:
    """Verbatim body of ``maincode_0719`` up to the bootstrap p-value."""
    lines = ADO.read_text(encoding="utf-8", errors="replace").splitlines()
    first = next(i for i, ln in enumerate(lines) if "pan_var = st_global" in ln)
    last = next(i for i, ln in enumerate(lines) if "boots_p = -1" in ln and i > first)
    # keep the closing brace of the else branch
    return "\n".join(lines[first : last + 2])


def _source() -> str:
    lines = ADO.read_text(encoding="utf-8", errors="replace").splitlines()
    start = next(i for i, ln in enumerate(lines) if ln.strip() == "mata:") + 1
    end = max(i for i, ln in enumerate(lines) if ln.strip() == "end")
    return "\n".join(lines[start:end])


_DUMP = r"""
mata:
void dump_linearity(string scalar tag, string scalar vname, real scalar k_endo,
                    real scalar k_exo, real scalar grid_num, real scalar trim_rate,
                    real scalar h_0, real scalar flag_static, real scalar flag_kink,
                    real scalar flag_inst, string scalar inst_list, string scalar touse,
                    real scalar flag_b, real scalar B)
{
__BODY__
    pyx_export("../out/" + tag + "_scal.csv", (N \ T \ boots_p \ sup_wald_ori))
    pyx_export("../out/" + tag + "_wald.csv", wald_rec)
    pyx_export("../out/" + tag + "_covwald.csv", cov_wald_rec)
}
end
"""


def render_do(cases: tuple[XthenregCase, ...] | None = None) -> str:
    """Do-file that runs the bootstrap of every case in Stata and exports it."""
    cases = linearity_cases() if cases is None else cases
    body = "\n".join("    " + ln for ln in _body().splitlines())
    out = ["version 17", "set more off", "clear all", "", _MATA_EXPORT]
    out += ["mata:", _source(), "end", "", _DUMP.replace("__BODY__", body)]
    for c in cases:
        var_all = " ".join([c.y, c.q, *c.x, *c.endogenous, *c.exogenous])
        out += [
            'use "../data/invest.dta", clear',
            "xtset firm year",
            f"keep if year <= {c.max_year}",
            "gen double z1 = cashflow*tobin_q + debt",
            "gen double z2 = ln(1 + tobin_q)",
            "quietly xtset",
            f"gen byte touse = !missing({c.y}, {c.q}, {', '.join(c.x)})"
            if c.x
            else f"gen byte touse = !missing({c.y}, {c.q})",
            f"set seed {c.seed}",
            f'mata: dump_linearity("{TAG}_{c.tag}", "{var_all}", {len(c.endogenous)}, '
            f"{len(c.exogenous)}, {c.grid_num}, {c.trim_rate:g}, 1.5, {int(c.static)}, "
            f'{int(c.kink)}, {int(bool(c.inst))}, "{" ".join(c.inst) if c.inst else "."}", '
            f'"touse", 1, {c.boost})',
            "",
        ]
    out.append("exit, clear")
    return "\n".join(out) + "\n"


def write_do(path: Path | None = None) -> Path:
    """Write ``validation/stata/linearity_cases.do``."""
    path = path or STATA_DIR / "linearity_cases.do"
    path.write_text(render_do(), encoding="ascii", errors="replace", newline="\n")
    return path


KINDS = ("scal", "wald", "covwald")


def stata_results(out_dir: Path = OUT_DIR) -> dict[str, dict[str, np.ndarray]]:
    """Exports of the Stata run, grouped by case."""
    return {
        c.tag: {k: read_matrix(out_dir / f"{TAG}_{c.tag}_{k}.csv") for k in KINDS}
        for c in linearity_cases()
    }


def freeze(out_dir: Path = OUT_DIR, path: Path = GOLDEN) -> Path:
    """Freeze the Stata results into ``tests/golden/linearity_golden.json``."""
    master = {
        "meta": {"stata": "Stata 17.0 MP", "source": "validation/linearity_cases.py"},
        "stata": {
            t: {k: v.tolist() for k, v in o.items()} for t, o in stata_results(out_dir).items()
        },
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(master), encoding="utf-8", newline="\n")
    return path


if __name__ == "__main__":
    import sys

    print(freeze() if "--freeze" in sys.argv else write_do())
