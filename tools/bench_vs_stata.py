"""Time of ``xtdpthresh`` in Stata and in Python on three sizes (J.3.1).

Three steps, because Stata runs only from PowerShell:

    python tools/bench_vs_stata.py prepare    # panels (.dta) and the do-file that times Stata
    powershell validation/run_stata.ps1 -Do validation/stata/perf_stata.do -TimeoutSec 3600
    python tools/bench_vs_stata.py compare    # times Python, reads Stata's, writes the table

The same model on both sides: ``y`` on its lag with the threshold variable ``q``, first
differences, wild bootstrap with ``B = 299`` and ``grid_ci = 100``, one seed.  Each size is timed
without bootstrap (search, variance, tests) and with it; the bootstrap cost is the difference.
The sizes are Hansen's panel (565 x 15) and simulated panels of 2 000 and 10 000 units (T = 8).
"""

from __future__ import annotations

import json
import statistics
import sys
import time
import warnings
from pathlib import Path

import pandas as pd

from pyxtdpthresh.extras.datasets import load_dataset
from pyxtdpthresh.extras.simulation import simulate_panel
from pyxtdpthresh.models.xtdpthresh.fit import fit_point

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "validation" / "data"
STATA = ROOT / "validation" / "stata"
OUT = ROOT / "docs" / "performance"
SIZES = {
    "hansen": ("invest.dta", "invest", "cashflow", "tobin_q", "firm", "year"),
    "2000": ("perf_2000.dta", "y", "", "q", "id", "t"),
    "10000": ("perf_10000.dta", "y", "", "q", "id", "t"),
}
BOOT, GRID_CI, SEED = 299, 100, 20260611
REPS = {"hansen": 5, "2000": 5, "10000": 3}
CSV = STATA / "perf_stata.csv"
PAIRS = STATA / "perf_pairs.csv"


def panel(name: str) -> pd.DataFrame:
    """Return the data of one size."""
    if name == "hansen":
        return load_dataset("invest")
    return simulate_panel("gong_seo", int(name), 8, seed=11)


def stata_command(name: str, bootstrap: bool) -> str:
    """Return the Stata command of one size, with or without the bootstrap."""
    _, y, x, q, _, _ = SIZES[name]
    tail = f"boot({BOOT}) gridci({GRID_CI}) rseed({SEED})" if bootstrap else "noboot"
    return f"xtdpthresh {y} {x}, qx({q}) {tail}".replace("  ", " ")


def prepare() -> None:
    """Write the simulated panels as ``.dta`` and the do-file that times Stata."""
    for name in ("2000", "10000"):
        panel(name).to_stata(DATA / SIZES[name][0], write_index=False, version=118)
    lines = [
        "version 17", "set more off", "clear all",
        f'file open fh using "{CSV.as_posix()}", write text replace',
        'file write fh "size,bootstrap,rep,seconds" _n',
    ]  # fmt: skip
    for name, (file, *_, ident, period) in SIZES.items():
        for bootstrap in (False, True):
            lines += [
                f"forvalues r = 1/{REPS[name]} {{",
                f'    use "../data/{file}", clear',
                f"    xtset {ident} {period}",
                "    timer clear 1", "    timer on 1",
                f"    quietly {stata_command(name, bootstrap)}",
                "    timer off 1", "    quietly timer list 1",
                f'    file write fh "{name},{int(bootstrap)},`r\',`=r(t1)\'" _n',
                "}",
            ]  # fmt: skip
    lines += ["file close fh", "exit, clear"]
    (STATA / "perf_stata.do").write_text("\n".join(lines) + "\n", encoding="ascii", newline="\n")
    print("written", STATA / "perf_stata.do")


def python_times(name: str, bootstrap: bool) -> list[float]:
    """Return the seconds of ``REPS`` repetitions of the Python fit."""
    file, y, x, q, ident, period = SIZES[name]
    frame = panel(name)
    options = (
        {"n_boot": BOOT, "grid_ci": GRID_CI, "seed": SEED} if bootstrap else {"bootstrap": False}
    )
    columns = [x] if x else []
    times = []
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        fit_point(frame, y, columns, q=q, id=ident, time=period, **options)  # warm-up
        for _ in range(REPS[name]):
            start = time.perf_counter()
            fit_point(frame, y, columns, q=q, id=ident, time=period, **options)
            times.append(time.perf_counter() - start)
    return times


def compare() -> None:
    """Time Python, read the times of Stata and write the comparison."""
    stata = pd.read_csv(CSV)
    rows = []
    for name in SIZES:
        median = {}
        for bootstrap in (False, True):
            s = stata[(stata["size"].astype(str) == name) & (stata["bootstrap"] == int(bootstrap))]
            py = python_times(name, bootstrap)
            median[bootstrap] = (
                statistics.median(s["seconds"]), statistics.median(py),
                (float(s["seconds"].min()), float(s["seconds"].max())), (min(py), max(py)),
            )  # fmt: skip
        (s0, p0, *_), (s1, p1, *_) = median[False], median[True]
        rows.append({
            "size": name,
            "stata_noboot": s0, "python_noboot": p0, "ratio_noboot": s0 / p0,
            "stata_boot_cost": s1 - s0, "python_boot_cost": p1 - p0,
            "ratio_boot": (s1 - s0) / (p1 - p0), "stata_total": s1, "python_total": p1,
            "ratio_total": s1 / p1,
            "stata_range": median[True][2], "python_range": median[True][3],
        })  # fmt: skip
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "stata_comparison.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print(pd.DataFrame(rows).drop(columns=["stata_range", "python_range"]).round(3).to_string())


def pair_do(name: str) -> None:
    """Write the do-file that times ONE Stata fit of a size and appends it to ``perf_pairs.csv``."""
    file, *_, ident, period = SIZES[name]
    lines = [
        "version 17", "set more off", "clear all",
        f'use "../data/{file}", clear', f"xtset {ident} {period}",
        "timer clear 1", "timer on 1", f"quietly {stata_command(name, True)}", "timer off 1",
        "quietly timer list 1",
        f'file open fh using "{PAIRS.as_posix()}", write text append',
        f"file write fh \"stata,{name},`=r(t1)'\" _n", "file close fh", "exit, clear",
    ]  # fmt: skip
    text = "\n".join(lines) + "\n"
    (STATA / f"perf_pair_{name}.do").write_text(text, encoding="ascii", newline="\n")


def pair_python(name: str) -> None:
    """Time ONE Python fit of a size (after a warm-up) and append it to ``perf_pairs.csv``."""
    frame, (_, y, x, q, ident, period) = panel(name), SIZES[name]
    columns = [x] if x else []
    options = {"n_boot": BOOT, "grid_ci": GRID_CI, "seed": SEED}
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        small = frame[frame[ident] <= frame[ident].unique()[40]]
        fit_point(small, y, columns, q=q, id=ident, time=period, **options)  # warm-up
        start = time.perf_counter()
        fit_point(frame, y, columns, q=q, id=ident, time=period, **options)
        seconds = time.perf_counter() - start
    with PAIRS.open("a", encoding="ascii") as handle:
        handle.write(f"python,{name},{seconds}\n")


if __name__ == "__main__":
    command, *rest = sys.argv[1:]
    {"prepare": prepare, "compare": compare, "pair-do": pair_do, "pair-python": pair_python}[
        command
    ](*rest)
