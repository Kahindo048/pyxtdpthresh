"""Reference timings of the real ``xthenreg`` command in Stata (B.3.2) and of the package (D.5.5).

Four scenarios on the Hansen panel, dynamic jump model with three endogenous regressors and a
grid of 100 points: ``T = 8`` and ``T = 15``, each without bootstrap and with 20 bootstrap replications (Stata is too slow to time 399 several times).
Each scenario is repeated; the spread of the repetitions gives the margin of the comparison.
The command is timed as a whole, so the bootstrap cost is the difference between the two runs
of a panel.
"""

from __future__ import annotations

import json
import statistics
import time
import warnings
from dataclasses import dataclass, replace
from pathlib import Path

import numpy as np

from validation.cases import _MATA_EXPORT, OUT_DIR, STATA_DIR, XthenregCase

RESULT = Path(__file__).resolve().parents[1] / "tests" / "benchmarks" / "stata_reference.json"
_ENDO = ("cashflow", "tobin_q", "debt")
_EXPORT = (
    'mata: pyx_export("../out/bench_stata.csv", '
    'st_matrix("pyxbench")[2..rows(st_matrix("pyxbench")), .])'
)
BOOT = 20  # replications timed in Stata (the cost is linear in B)
_BASE = XthenregCase("bn", "invest", "debt", endogenous=_ENDO, grid_num=100, seed=2024)


@dataclass(frozen=True)
class Scenario:
    """One timed configuration."""

    name: str
    case: XthenregCase
    reps: int


def scenarios() -> tuple[Scenario, ...]:
    """The four timed configurations."""
    t8, t15 = replace(_BASE, max_year=1980), replace(_BASE, max_year=None)
    return (
        Scenario("T8_noboot", t8, 5),
        Scenario("T8_boot20", replace(t8, boost=BOOT), 3),
        Scenario("T15_noboot", t15, 5),
        Scenario("T15_boot20", replace(t15, boost=BOOT), 3),
    )


def render_do() -> str:
    """Do-file that times every scenario and exports ``(scenario, rep, seconds)``."""
    out = ["version 17", "set more off", "clear all", _MATA_EXPORT, "matrix pyxbench = J(1, 3, .)"]
    for s_idx, s in enumerate(scenarios(), start=1):
        c = s.case
        year = f"keep if year <= {c.max_year}" if c.max_year is not None else "* all years"
        out += [
            f"forvalues r = 1/{s.reps} {{",
            '    use "../data/invest.dta", clear',
            "    xtset firm year",
            f"    {year}",
            f"    set seed {c.seed}",
            "    timer clear 1",
            "    timer on 1",
            f"    quietly {c.stata_command()}",
            "    timer off 1",
            "    quietly timer list 1",
            "    local sec = r(t1)",
            f"    matrix pyxbench = (pyxbench \\ ({s_idx}, `r', `sec'))",
            f"    {_EXPORT}",
            "}",
        ]
    out.append("exit, clear")
    return "\n".join(out) + "\n"


def write_do(path: Path | None = None) -> Path:
    """Write ``validation/stata/bench_cases.do``."""
    path = path or STATA_DIR / "bench_cases.do"
    path.write_text(render_do(), encoding="ascii", newline="\n")
    return path


def stata_times(out_dir: Path = OUT_DIR) -> dict[str, list[float]]:
    """Seconds of each repetition, by scenario."""
    rows = np.loadtxt(out_dir / "bench_stata.csv", delimiter=",", ndmin=2)
    names = [s.name for s in scenarios()]
    return {n: rows[rows[:, 0] == i, 2].tolist() for i, n in enumerate(names, start=1)}


def python_times() -> dict[str, list[float]]:
    """Seconds of each repetition of the package (data preparation included)."""
    from validation.runner import estimate_case

    warnings.simplefilter("ignore")
    estimate_case(replace(_BASE, max_year=1980, boost=8))  # compile and warm the caches
    times: dict[str, list[float]] = {}
    for s in scenarios():
        runs = []
        for _ in range(s.reps):
            start = time.perf_counter()
            estimate_case(s.case)
            runs.append(time.perf_counter() - start)
        times[s.name] = runs
    return times


def summarise(stata: dict[str, list[float]], python: dict[str, list[float]]) -> dict[str, dict]:
    """Median and range per scenario; the speed-up range pairs the extremes (the margin)."""
    table = {}
    for name in stata:
        s, p = stata[name], python[name]
        table[name] = {
            "stata_median": statistics.median(s),
            "stata_range": [min(s), max(s)],
            "python_median": statistics.median(p),
            "python_range": [min(p), max(p)],
            "speedup_median": statistics.median(s) / statistics.median(p),
            "speedup_range": [min(s) / max(p), max(s) / min(p)],
        }
    return table


def python_times_399() -> dict[str, list[float]]:
    """Package timings with 399 replications (3 repetitions each)."""
    from validation.runner import estimate_case

    out: dict[str, list[float]] = {}
    for name, year in (("T8", 1980), ("T15", None)):
        runs = []
        for _ in range(3):
            start = time.perf_counter()
            estimate_case(replace(_BASE, max_year=year, boost=399))
            runs.append(time.perf_counter() - start)
        out[name] = runs
    return out


def _extrapolate(base: float, boot: float, target: int = 399) -> float:
    """Time at ``target`` replications from the times at B = 0 and B = ``BOOT``."""
    return base + target / BOOT * (boot - base)


def stata_399(stata: dict[str, list[float]]) -> dict[str, dict]:
    """Stata time with 399 replications, extrapolated linearly from B = 0 and B = 20."""
    out = {}
    for name in ("T8", "T15"):
        base, boot = stata[f"{name}_noboot"], stata[f"{name}_boot20"]
        out[name] = {
            "median": _extrapolate(statistics.median(base), statistics.median(boot)),
            "range": [
                _extrapolate(min(base), min(boot)),
                _extrapolate(max(base), max(boot)),
            ],
            "per_replication": (statistics.median(boot) - statistics.median(base)) / BOOT,
        }
    return out


if __name__ == "__main__":
    import sys

    if "--run" in sys.argv:
        stata = stata_times()
        result = summarise(stata, python_times())
        py399, st399 = python_times_399(), stata_399(stata)
        result["boot399"] = {
            n: {
                "stata_extrapolated": st399[n],
                "python_median": statistics.median(py399[n]),
                "python_range": [min(py399[n]), max(py399[n])],
                "speedup_median": st399[n]["median"] / statistics.median(py399[n]),
                "speedup_range": [
                    st399[n]["range"][0] / max(py399[n]),
                    st399[n]["range"][1] / min(py399[n]),
                ],
            }
            for n in st399
        }
        RESULT.parent.mkdir(parents=True, exist_ok=True)
        RESULT.write_text(json.dumps(result, indent=1), encoding="utf-8", newline="\n")
        print(json.dumps(result, indent=1))
    else:
        print(write_do())
