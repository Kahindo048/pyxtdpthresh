"""Point estimates of ``xtdpthresh`` on the full Hansen panel against Stata (E.6 gate).

The examples of the help file (``maxlag(3 8) collapse noboot``, ``maxlag(2 10)``, kink, external
instrument) and the main instrument and search options are run on the 565 firms, 1973-1987.
Python must reproduce ``e(b)``, ``e(gamma)``, ``e(obj)``, ``e(N)``, ``e(N_iv)``, ``e(N_units)``
and ``e(V_cond)`` to four decimals.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from validation.cases import _MATA_EXPORT, OUT_DIR, STATA_DIR, load_invest
from validation.compare import read_matrix
from validation.estimation_cases import BASE_ARGS, pack
from validation.sample_cases import DATA
from validation.search_cases import _E_NAME, _MATA_SC, SearchCase
from validation.spec_cases import parse_log, stata_command

GOLDEN = Path(__file__).resolve().parents[1] / "tests" / "golden" / "point_golden.json"
LOG = STATA_DIR / "_run_point_cases.log"
HELP = {
    "x": (),
    "endogenous": ("cashflow", "tobin_q", "debt"),
    "maxlag": (3, 8),
    "collapse": True,
}
_SCALARS = (
    "gamma", "obj", "twostep", "grid_admitted", "q_lo", "q_hi", "kink_refined", "stage1_gamma",
    "refine_iterations", "refine_added", "grid_effective", "n", "n_iv", "n_units",
)  # fmt: skip
_E_NAME2 = {**_E_NAME, "n_iv": "N_iv", "n_units": "N_units"}


def _case(name: str, data: str = "d0", **args: Any) -> SearchCase:
    return SearchCase(name, data, args, None)


CASES: tuple[SearchCase, ...] = (
    _case("help_maxlag_3_8", **HELP),
    _case("help_maxlag_2_10", **{**HELP, "maxlag": (2, 10)}),
    _case("help_kink", **HELP, kink=True),
    _case("help_iv_peer", **HELP, iv=("L2.peer_q",)),
    _case("help_unbalanced_gaps", "d1", **HELP),
    _case("help_unbalanced_short", "d3", **HELP),
    _case("help_unbalanced_alternate", "d4", **HELP),
    _case("help_refine", **HELP, refine=5),
    _case("help_quantile_grid", **HELP, grid_type="quantile"),
    _case("help_grid_200", **HELP, grid=200),
    _case("default_instruments", x=("cashflow",), endogenous=("tobin_q",)),
    _case("static_default", static=True, x=("cashflow", "L.tobin_q")),
    _case(
        "mixed_roles",
        x=("cashflow",),
        predetermined=("tobin_q",),
        endogenous=("debt",),
        maxlag=(2, 8),
        collapse=True,
    ),  # fmt: skip
    _case("kink_default_instruments", kink=True, x=("cashflow",), endogenous=("tobin_q",)),
)


def args_of(case: SearchCase) -> dict[str, Any]:
    """Arguments of the call: the base without the 100-firm restriction, then the case."""
    base = {k: v for k, v in BASE_ARGS.items() if k != "grid"}  # default grid of 100 points
    return {**base, "export_gmm": False, **case.args}


def frame(case: SearchCase) -> pd.DataFrame:
    """The full panel after the distortion, with ``peer_q`` as Stata's ``egen`` builds it."""
    df = load_invest(max_year=None, derived=False)
    df = df.assign(peer_q=df.groupby("year")["tobin_q"].transform("mean"))
    return DATA[case.data][1](df).reset_index(drop=True)


def render_do(cases: tuple[SearchCase, ...] | None = None) -> str:
    """Do-file that runs every case and exports what Python must reproduce."""
    cases = CASES if cases is None else cases
    out = ["version 17", "set more off", "clear all", _MATA_EXPORT, _MATA_SC]
    for c in cases:
        tag = f"../out/pc_{c.name}"
        scalars = ", ".join(f'pyx_sc("e({_E_NAME2.get(n, n)})")' for n in _SCALARS)
        out += [
            'use "../data/invest.dta", clear',
            "xtset firm year",
            "egen double peer_q = mean(tobin_q), by(year)",
            *DATA[c.data][0],
            f'display "@@CASE {c.name}"',
            f"capture noisily {stata_command(args_of(c))}",
            'display "@@RC " _rc',
            "if _rc == 0 {",
            f'    mata: pyx_export("{tag}_sc.csv", ({scalars}))',
            f'    mata: pyx_export("{tag}_b.csv", st_matrix("e(b)"))',
            f'    mata: pyx_export("{tag}_vc.csv", st_matrix("e(V_cond)"))',
            "}",
            "",
        ]
    out.append("exit, clear")
    return "\n".join(out) + "\n"


def write_do(path: Path | None = None) -> Path:
    """Write ``validation/stata/point_cases.do``."""
    path = path or STATA_DIR / "point_cases.do"
    path.write_text(render_do(), encoding="ascii", errors="replace", newline="\n")
    return path


def freeze(log: Path = LOG, path: Path = GOLDEN, out_dir: Path = OUT_DIR) -> Path:
    """Freeze the Stata results into ``tests/golden/point_golden.json``."""
    parsed = parse_log(log.read_text(encoding="utf-8", errors="replace"))
    cases: dict[str, dict[str, Any]] = {}
    for c in CASES:
        entry: dict[str, Any] = dict(parsed[c.name])
        if entry["rc"] == 0:
            tag = out_dir / f"pc_{c.name}"
            values = read_matrix(Path(f"{tag}_sc.csv")).ravel()
            entry["scalars"] = dict(zip(_SCALARS, (float(v) for v in values), strict=True))
            entry["b"] = pack(read_matrix(Path(f"{tag}_b.csv")))
            entry["vcond"] = pack(read_matrix(Path(f"{tag}_vc.csv")))
        cases[c.name] = entry
    master = {"meta": {"stata": "Stata 17.0 MP", "xtdpthresh": "0.9.38"}, "cases": cases}
    path.write_text(json.dumps(master), encoding="utf-8", newline="\n")
    return path


if __name__ == "__main__":
    import sys

    print(freeze() if "--freeze" in sys.argv else write_do())
