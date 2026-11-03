"""Threshold search of ``xtdpthresh`` against Stata (E.5).

The real command is run (point estimate, ``noboot``) on the Hansen panel (100 firms, 1973-1981)
with different grids, trimming, ``minregime``, ``refine``, the kink model and unbalanced panels.
Stata exports ``e(gamma)``, ``e(obj)``, ``e(b)``, ``e(V_cond)`` and the search bookkeeping
(``e(grid_admitted)``, ``e(q_lo)``, ``e(q_hi)``, ``e(kink_refined)``, the first-stage threshold,
the refinement counts); Python must reproduce them.  Invalid requests are compared by return code
and by the Stata message that identifies the rule.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from validation.cases import _MATA_EXPORT, OUT_DIR, STATA_DIR
from validation.compare import read_matrix
from validation.estimation_cases import (
    BASE_ARGS,
    DERIVED_STATA,
    MAX_FIRM,
    MAX_YEAR,
    pack,
)
from validation.estimation_cases import EstCase as _EstCase
from validation.sample_cases import DATA
from validation.spec_cases import parse_log, stata_command

GOLDEN = Path(__file__).resolve().parents[1] / "tests" / "golden" / "search_golden.json"
LOG = STATA_DIR / "_run_search_cases.log"


@dataclass(frozen=True)
class SearchCase(_EstCase):
    """One run; ``key`` is the rule expected from Python when the request is refused."""

    key: str | None = None
    args: dict[str, Any] = field(default_factory=dict)

    def full_args(self) -> dict[str, Any]:
        """Arguments of the call: the base, then the case."""
        return {**BASE_ARGS, "export_gmm": False, "grid": 50, **self.args}


def _case(name: str, data: str = "d0", key: str | None = None, **args: Any) -> SearchCase:
    return SearchCase(name, data, args, key)


_E = {"endogenous": ("tobin_q",)}
CASES: tuple[SearchCase, ...] = (
    _case("default", **_E),
    _case("grid10", grid=10, **_E),
    _case("grid200", grid=200, **_E),
    _case("quantile", grid_type="quantile", **_E),
    _case("quantile_10", grid_type="quantile", grid=10, **_E),
    _case("observed_support", grid_sample="observed", **_E),
    _case("trim20", trim=0.2, **_E),
    _case("trim05", trim=0.05, **_E),
    _case("min_regime", min_regime=60, **_E),
    _case("refine1", refine=1, grid=15, **_E),
    _case("refine3", refine=3, grid=15, **_E),
    _case("refine_quantile", refine=2, grid_type="quantile", grid=12, **_E),
    _case("kink", kink=True, **_E),
    _case("kink_grid10", kink=True, grid=10, **_E),
    _case("kink_trim20", kink=True, trim=0.2, **_E),
    _case("static", static=True, x=("cashflow", "L.tobin_q")),
    _case("collapse", collapse=True, **_E),
    _case("iv", iv=("z1", "z2"), iv_collapse=True, **_E),
    _case("exog_only"),
    _case("nocenter", center=False, **_E),
    _case("unbalanced_gaps", "d1", **_E),
    _case("unbalanced_missing_x", "d2", **_E),
    _case("unbalanced_short_units", "d3", **_E),
    _case("unbalanced_alternate_years", "d4", **_E),
    _case("unbalanced_missing_endog", "d5", **_E),
    _case("unbalanced_refine", "d1", refine=2, grid=15, **_E),
    _case("unbalanced_kink", "d3", kink=True, **_E),
    _case("alternate_years_kink", "d4", kink=True, **_E),
    _case("alternate_years_grid10", "d4", grid=10, **_E),
    _case("e_min_regime_huge", key="minregime_no_split", min_regime=5000, **_E),
)

FRAGMENTS = {"minregime_no_split": "leaves no admissible threshold split"}
_SCALARS = (
    "gamma", "obj", "twostep", "grid_admitted", "q_lo", "q_hi", "kink_refined", "stage1_gamma",
    "refine_iterations", "refine_added", "grid_effective", "n",
)  # fmt: skip


_E_NAME = {"twostep": "estimator_twostep", "stage1_gamma": "gamma_stage1", "n": "N"}
_MATA_SC = """mata:
real scalar pyx_sc(string scalar name)
{
    real matrix v
    v = st_numscalar(name)
    return(rows(v) * cols(v) == 1 ? v : .)
}
end
"""


def render_do(cases: tuple[SearchCase, ...] | None = None) -> str:
    """Do-file that runs every case and exports what Python must reproduce."""
    cases = CASES if cases is None else cases
    out = ["version 17", "set more off", "clear all", _MATA_EXPORT, _MATA_SC]
    for c in cases:
        tag = f"../out/sc2_{c.name}"
        scalars = ", ".join(f'pyx_sc("e({_E_NAME.get(n, n)})")' for n in _SCALARS)
        out += [
            'use "../data/invest.dta", clear',
            "xtset firm year",
            f"keep if firm <= {MAX_FIRM} & year <= {MAX_YEAR}",
            *DERIVED_STATA,
            *DATA[c.data][0],
            f'display "@@CASE {c.name}"',
            f"capture noisily {stata_command(c.full_args())}",
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
    """Write ``validation/stata/search_cases.do``."""
    path = path or STATA_DIR / "search_cases.do"
    path.write_text(render_do(), encoding="ascii", errors="replace", newline="\n")
    return path


def freeze(log: Path = LOG, path: Path = GOLDEN, out_dir: Path = OUT_DIR) -> Path:
    """Freeze the Stata results into ``tests/golden/search_golden.json``."""
    parsed = parse_log(log.read_text(encoding="utf-8", errors="replace"))
    cases: dict[str, dict[str, Any]] = {}
    for c in CASES:
        entry: dict[str, Any] = dict(parsed[c.name])
        if entry["rc"] == 0:
            tag = out_dir / f"sc2_{c.name}"
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
