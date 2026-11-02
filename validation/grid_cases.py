"""Validation of core.quantiles and core.grids against Stata (block C.3; files ``gr_*``).

The Stata side runs moremata's ``mm_quantile`` and Mata's ``rangen`` as they are, and the
**verbatim** source of ``xdpt2_quantile``, ``xdpt2_rangen`` and ``xdpt2_quantile_grid`` taken
from ``xtdpthresh.ado``.  The data are defined by integer formulas that Mata and NumPy
evaluate identically, so no data file is needed.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from validation.cases import _MATA_EXPORT, OUT_DIR, STATA_DIR
from validation.compare import read_matrix

ADO = Path.home() / "ado" / "plus" / "x" / "xtdpthresh.ado"
GOLDEN = Path(__file__).resolve().parents[1] / "tests" / "golden" / "grid_golden.json"
TAG = "gr"
TRIM = 0.2
GRID_NUM = 100
QGRID_NUM = 30
USER_FLOOR = 30


def _idx(n: int) -> np.ndarray:
    return np.arange(1, n + 1, dtype=np.float64)


#: name -> (Mata expression of the column vector q, Python builder).
CASES = {
    "ties10": ("mod(i*7, 10)", 500, lambda i: np.mod(i * 7, 10)),
    "uni4520": ("mod(i*7919, 10007)/100", 4520, lambda i: np.mod(i * 7919, 10007) / 100),
    "small25": ("mod(i*37, 101)/10", 25, lambda i: np.mod(i * 37, 101) / 10),
    "n300": ("mod(i*104729, 1009)/13", 300, lambda i: np.mod(i * 104729, 1009) / 13),
    "skew1000": (
        "(mod(i*7919, 10007)/10007):*(mod(i*7919, 10007)/10007)*50",
        1000,
        lambda i: (np.mod(i * 7919, 10007) / 10007) * (np.mod(i * 7919, 10007) / 10007) * 50,
    ),
}


def data(name: str) -> np.ndarray:
    """Threshold variable of one case."""
    _, n, build = CASES[name]
    return np.asarray(build(_idx(n)), dtype=np.float64)


def probabilities(n: int) -> np.ndarray:
    """Probabilities that stress the estimators: trim bounds, extremes, exact ranks, odd values."""
    trims = [0.01, 0.05, 0.1, 0.2, 0.3, 0.4, 0.45]
    ps = {0.0, 1.0, 0.5, 0.25, 0.75, 0.123456, 0.999, -0.1, 1.2}
    ps |= {t / 2 for t in trims} | {1 - t / 2 for t in trims}
    ps |= {k / n for k in (1, 2, 7, n // 3, n // 2, n - 1)}  # p * n is (nearly) an integer
    return np.array(sorted(ps), dtype=np.float64)


def _extract_functions() -> str:
    """Verbatim Mata source of the three ``xdpt2_*`` helpers."""
    lines = ADO.read_text(encoding="utf-8", errors="replace").splitlines()

    def block(first: str, until: str) -> str:
        a = next(i for i, ln in enumerate(lines) if ln.startswith(first))
        b = next(i for i, ln in enumerate(lines) if i > a and ln.startswith(until))
        return "\n".join(lines[a:b])

    quantile = block("real scalar xdpt2_quantile(", "// v0.9.32: critical value")
    grid = block("real colvector xdpt2_quantile_grid(", "// Scale-equivariant tolerance")
    return quantile + "\n" + grid


_MATA_RUN = """\
mata:
void run_case(string scalar tag, real colvector q, real colvector p)
{
    real scalar k, lo, hi, mdef, mapp
    real colvector t7, g, adm
    t7 = J(rows(p), 1, .)
    for (k = 1; k <= rows(p); k++) t7[k] = xdpt2_quantile(q, p[k])
    pyx_export("../out/" + tag + "_mm.csv", mm_quantile(q, 1, p))
    pyx_export("../out/" + tag + "_t7.csv", t7)
    lo = xdpt2_quantile(q, __TRIM__ / 2)
    hi = xdpt2_quantile(q, 1 - __TRIM__ / 2)
    pyx_export("../out/" + tag + "_rangen.csv", rangen(lo, hi, __GRID__))
    pyx_export("../out/" + tag + "_rangen_x.csv", xdpt2_rangen(lo, hi, __GRID__))
    pyx_export("../out/" + tag + "_rangen1.csv", rangen(lo, hi, 1))
    pyx_export("../out/" + tag + "_qgrid.csv",
               xdpt2_quantile_grid(q, __TRIM__ / 2, 1 - __TRIM__ / 2, __QGRID__))
    pyx_export("../out/" + tag + "_qgrid1.csv",
               xdpt2_quantile_grid(q, __TRIM__ / 2, 1 - __TRIM__ / 2, 1))
    mdef = min((sum(q :<= lo), sum(q :> hi)))
    if (mdef < 2) mdef = 2
    mapp = (__USER__ > mdef ? __USER__ : mdef)
    pyx_export("../out/" + tag + "_minreg.csv", (mdef \\ mapp))
    g = xdpt2_rangen(lo, hi, __GRID__)
    adm = J(rows(g), 1, .)
    for (k = 1; k <= rows(g); k++) {
        adm[k] = (sum(q :<= g[k]) >= mapp) & (sum(q :> g[k]) >= mapp)
    }
    pyx_export("../out/" + tag + "_adm.csv", adm)
}
end
"""


def render_do() -> str:
    """Do-file that evaluates every case with Stata and exports the results."""
    run = (
        _MATA_RUN.replace("__TRIM__", repr(TRIM))
        .replace("__GRID__", str(GRID_NUM))
        .replace("__QGRID__", str(QGRID_NUM))
        .replace("__USER__", str(USER_FLOOR))
    )
    body = ["version 17", "set more off", "clear all", "", _MATA_EXPORT]
    body += ["mata:", _extract_functions(), "end", "", run, "mata:"]
    for name, (expr, n, _) in CASES.items():
        p = probabilities(n)
        lit = " \\ ".join(f"{v:.17g}" for v in p)
        body.append(f"i = (1::{n}); q = {expr}; p = ({lit})")
        body.append(f'run_case("{TAG}_{name}", q, p)')
    body += ["end", "exit, clear"]
    return "\n".join(body) + "\n"


def write_do(path: Path | None = None) -> Path:
    """Write ``validation/stata/grid_cases.do``."""
    path = path or STATA_DIR / "grid_cases.do"
    path.write_text(render_do(), encoding="ascii", newline="\n")
    return path


KINDS = ("mm", "t7", "rangen", "rangen_x", "rangen1", "qgrid", "qgrid1", "minreg", "adm")


def python_results(name: str) -> dict[str, np.ndarray]:
    """Same objects as the Stata export, computed with the package."""
    from pyxtdpthresh.core import grids, quantiles

    q = data(name)
    p = probabilities(q.size)
    lo = float(quantiles.quantile_type7(q, TRIM / 2))
    hi = float(quantiles.quantile_type7(q, 1 - TRIM / 2))
    default, applied = grids.min_regime_floor(q, lo, hi, USER_FLOOR)
    grid = quantiles.rangen(lo, hi, GRID_NUM)
    return {
        "mm": quantiles.mm_quantile(q, p),
        "t7": quantiles.quantile_type7(q, p),
        "rangen": grid,
        "rangen_x": grid,
        "rangen1": quantiles.rangen(lo, hi, 1),
        "qgrid": grids.quantile_grid(q, TRIM / 2, 1 - TRIM / 2, QGRID_NUM),
        "qgrid1": grids.quantile_grid(q, TRIM / 2, 1 - TRIM / 2, 1),
        "minreg": np.array([default, applied], dtype=np.float64),
        "adm": grids.admissible(grid, q, applied).astype(np.float64),
    }


def stata_results(out_dir: Path = OUT_DIR) -> dict[str, dict[str, np.ndarray]]:
    """Exports of the Stata run, grouped by case."""
    return {
        name: {k: read_matrix(out_dir / f"{TAG}_{name}_{k}.csv") for k in KINDS} for name in CASES
    }


def freeze(out_dir: Path = OUT_DIR, path: Path = GOLDEN) -> Path:
    """Freeze the Stata results into ``tests/golden/grid_golden.json``."""
    master = {
        "meta": {"stata": "Stata 17.0 MP", "source": "validation/grid_cases.py"},
        "stata": {
            n: {k: v.tolist() for k, v in o.items()} for n, o in stata_results(out_dir).items()
        },
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(master, indent=1), encoding="utf-8", newline="\n")
    return path


if __name__ == "__main__":
    import sys

    print(freeze() if "--freeze" in sys.argv else write_do())
