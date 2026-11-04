"""Time of each step of an ``xtdpthresh`` fit on three sizes (J.1.1).

Chains the validated steps of ``models/xtdpthresh/fit.py`` and times each one, then profiles the
whole call with cProfile.  Sizes: Hansen's panel (565 firms, 15 years) and simulated panels of
2 000 and 10 000 units.  Run from the project root:

    PYTHONPATH=.:src python tools/profile_components.py [hansen|2000|10000 ...] [--profile]
"""

from __future__ import annotations

import cProfile
import json
import pstats
import sys
import time
import warnings
from pathlib import Path

import pandas as pd

from pyxtdpthresh.extras.datasets import load_dataset
from pyxtdpthresh.extras.simulation import simulate_panel
from pyxtdpthresh.kernels._jit import blas_threads
from pyxtdpthresh.models.xtdpthresh.bootstrap import run_bootstrap
from pyxtdpthresh.models.xtdpthresh.design import check_specification
from pyxtdpthresh.models.xtdpthresh.diagnostics import hansen_test, serial_tests
from pyxtdpthresh.models.xtdpthresh.fit import fit_point
from pyxtdpthresh.models.xtdpthresh.sample import prepare_data
from pyxtdpthresh.models.xtdpthresh.search import search_threshold, threshold_support
from pyxtdpthresh.models.xtdpthresh.stack import build_stack
from pyxtdpthresh.models.xtdpthresh.variance import final_variance

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "performance"
OPTIONS = {"n_boot": 299, "grid_ci": 100, "seed": 1}


def case(name: str) -> tuple[pd.DataFrame, str, list[str], dict[str, str]]:
    """Return the data, ``y``, ``x`` and the keyword arguments of one size."""
    if name == "hansen":
        return (
            load_dataset("invest"),
            "invest",
            ["cashflow"],
            {"q": "tobin_q", "id": "firm", "time": "year"},
        )
    n = int(name)
    frame = simulate_panel("gong_seo", n, 8, seed=11)
    return frame, "y", [], {"q": "q", "id": "id", "time": "t"}


def timed(steps: dict[str, float], key: str, function, *args, **kwargs):  # type: ignore[no-untyped-def]
    """Run ``function`` and add its time to ``steps[key]``."""
    start = time.perf_counter()
    value = function(*args, **kwargs)
    steps[key] = steps.get(key, 0.0) + time.perf_counter() - start
    return value


def components(name: str) -> dict[str, float]:
    """Seconds spent in each step of one fit (the bootstrap steps are timed together)."""
    frame, y, x, keys = case(name)
    steps: dict[str, float] = {}
    id_, time_ = keys["id"], keys["time"]
    with warnings.catch_warnings(), blas_threads():
        warnings.simplefilter("ignore")
        spec = timed(steps, "specification", check_specification, y=y, x=x, q=keys["q"], **OPTIONS)
        data = timed(steps, "data", prepare_data, frame, spec, id=id_, time=time_)
        stack = timed(steps, "stack (instruments, weights)", build_stack, data)
        opts = spec.options
        result = timed(
            steps, "threshold search (grid, step 2)", search_threshold, stack,
            grid=opts.grid, grid_type=opts.grid_type, observed_support=False, trim=opts.trim,
            min_regime=opts.min_regime, refine=opts.refine, center=opts.center,
        )  # fmt: skip
        support, _ = threshold_support(stack, False)
        fit = result.fit
        variance = timed(
            steps, "variance", final_variance, stack, fit, result.stage1_gamma,
            vce=opts.vce, bw_scale=opts.bw_scale, center=opts.center, support=support,
        )  # fmt: skip
        timed(
            steps,
            "tests (Hansen, AR)",
            hansen_test,
            fit.obj,
            stack.n_instruments,
            fit.theta.size,
            twostep=fit.twostep,
        )
        timed(steps, "tests (Hansen, AR)", serial_tests, data, stack, fit, variance)
        timed(
            steps, "bootstrap (linearity + confidence set)", run_bootstrap, stack, result, support,
            trim=opts.trim, grid_ci=opts.grid_ci, grid_type=opts.grid_type, n_boot=opts.n_boot,
            level=opts.level, seed=opts.seed, linearity=True, continuity=False, citest=None,
            coef_boot="none", coef_symmetric=True, center=opts.center, boot_type="wild",
        )  # fmt: skip
    steps["total"] = sum(steps.values())
    steps["n_units"] = float(stack.n_units)
    steps["n_equations"] = float(stack.n_rows)
    steps["n_instruments"] = float(stack.n_instruments)
    return steps


def profile(name: str) -> str:
    """Return the 25 functions that take the most own time in one fit."""
    frame, y, x, keys = case(name)
    profiler = cProfile.Profile()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        profiler.enable()
        fit_point(frame, y, x, **keys, **OPTIONS)
        profiler.disable()
    stream = pstats.Stats(profiler).sort_stats("tottime")
    import io

    buffer = io.StringIO()
    stream.stream = buffer
    stream.print_stats(25)
    return buffer.getvalue()


def main(names: list[str], with_profile: bool) -> None:
    """Time the steps (and optionally profile) for each size and write ``docs/performance``."""
    OUT.mkdir(parents=True, exist_ok=True)
    # first call compiles the kernels: warm up on a small panel, so the times are the steady ones
    components("200")
    for name in names:
        steps = components(name)
        print(name, json.dumps({k: round(v, 3) for k, v in steps.items()}, indent=1))
        (OUT / f"components_{name}.json").write_text(json.dumps(steps, indent=2), encoding="utf-8")
        if with_profile:
            text = profile(name)
            (OUT / f"cprofile_{name}.txt").write_text(text, encoding="utf-8")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    main(args or ["hansen", "2000", "10000"], "--profile" in sys.argv)
