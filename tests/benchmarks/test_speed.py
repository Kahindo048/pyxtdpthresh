"""Guard against slowdowns (J.3.3).

The speed of this machine changes by a factor of two from one hour to the next (the same Stata
do-file took 80 s and then 36 s), so a time in seconds cannot be compared with an old one.  Two
kinds of check are used instead:

* each workload is timed in units of a fixed calibration computation run in the same process
  (a few matrix products), and compared with the units recorded in ``baseline.json`` with a wide
  margin: a slowdown of the package by more than ``TOLERANCE`` fails, the speed of the machine
  does not;
* the kernels are compared with their NumPy references in the same run, a ratio that does not
  depend on the machine at all.

Run with ``pytest -m bench``; record a new baseline after an intended change with
``PYX_BENCH_RECORD=1 pytest -m bench``.
"""

import json
import os
import time
import warnings
from pathlib import Path

import numpy as np
import pytest

from pyxtdpthresh import load_dataset
from pyxtdpthresh.kernels.profile import profile_rows
from pyxtdpthresh.kernels.reference import profile as reference_profile
from pyxtdpthresh.kernels.reference.syminv import syminv_many as reference_syminv
from pyxtdpthresh.kernels.syminv import syminv_many
from pyxtdpthresh.models.xtdpthresh.fit import fit_point

pytestmark = pytest.mark.bench

BASELINE = Path(__file__).with_name("baseline.json")
#: A workload may take this many times its recorded units before the guard fails.
TOLERANCE = 1.6
#: Smallest ratio reference-over-kernel time the kernels must keep.  Measured on one kernel
#: thread (the package setting): 1.3 to 1.9 for ``syminv`` (it was 7 with eight threads), 100 for
#: ``profile``.  The guard is that a kernel does not become slower than its NumPy reference.
MIN_SPEEDUP = {"syminv": 1.1, "profile": 10.0}


def calibration() -> float:
    """Seconds of a fixed computation (matrix products and a Python loop), best of seven."""
    a = np.random.default_rng(0).normal(size=(400, 400))
    best = np.inf
    for _ in range(7):
        start = time.perf_counter()
        for _ in range(30):
            a @ a
        total = 0
        for i in range(300_000):
            total += i
        best = min(best, time.perf_counter() - start)
    return float(best)


def check(name: str, seconds: float) -> None:
    """Compare the time of workload ``name`` with its recorded units of calibration."""
    units = seconds / calibration()
    recorded = json.loads(BASELINE.read_text()) if BASELINE.exists() else {}
    if os.environ.get("PYX_BENCH_RECORD"):
        recorded[name] = round(units, 3)
        BASELINE.write_text(json.dumps(recorded, indent=2, sort_keys=True) + "\n")
        return
    if name not in recorded:
        pytest.skip(f"no baseline for {name}: record one with PYX_BENCH_RECORD=1")
    assert units <= TOLERANCE * recorded[name], (
        f"{name} takes {units:.2f} calibration units, the baseline is {recorded[name]:.2f} "
        f"(limit {TOLERANCE * recorded[name]:.2f})"
    )


@pytest.fixture(scope="module")
def hansen():
    return load_dataset("invest")


@pytest.fixture(scope="module")
def firms150(hansen):
    return hansen[hansen["firm"] <= 150]


def fit(frame, **options):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return fit_point(
            frame, "invest", ["cashflow"], q="tobin_q", id="firm", time="year", seed=1, **options
        )


def timed(benchmark, function, rounds=3):
    benchmark.pedantic(function, rounds=rounds, warmup_rounds=1, iterations=1)
    return float(benchmark.stats["median"])


# ---------------------------------------------------------------------------- workloads
def test_point_estimate_on_hansen(benchmark, hansen):
    check("point_hansen", timed(benchmark, lambda: fit(hansen, bootstrap=False), rounds=5))


def test_wild_bootstrap_on_150_firms(benchmark, firms150):
    run = lambda: fit(firms150, collapse=True, n_boot=99, grid_ci=40)  # noqa: E731
    check("wild_150", timed(benchmark, run))


def test_unit_bootstrap_on_150_firms(benchmark, firms150):
    run = lambda: fit(firms150, collapse=True, boot_type="unit", n_boot=99, grid_ci=40)  # noqa: E731
    check("unit_150", timed(benchmark, run, rounds=2))


def test_wild_bootstrap_on_hansen(benchmark, hansen):
    run = lambda: fit(hansen, n_boot=299, grid_ci=100)  # noqa: E731
    check("wild_hansen", timed(benchmark, run, rounds=2))


# ------------------------------------------------------------------ kernels over references
def best_of(function, rounds=3):
    times = []
    for _ in range(rounds):
        start = time.perf_counter()
        function()
        times.append(time.perf_counter() - start)
    return min(times)


def test_the_syminv_kernel_stays_faster_than_numpy():
    rng = np.random.default_rng(0)
    x = rng.normal(size=(20_000, 5, 5))
    matrices = x @ x.transpose(0, 2, 1) + 0.1 * np.eye(5)
    syminv_many(matrices[:10])  # compiled
    kernel, numpy = (
        best_of(lambda: syminv_many(matrices)),
        best_of(lambda: reference_syminv(matrices)),
    )
    assert numpy / kernel >= MIN_SPEEDUP["syminv"], f"kernel {kernel:.3f}s, numpy {numpy:.3f}s"


def test_the_profile_kernel_stays_faster_than_the_python_loop():
    rng = np.random.default_rng(1)
    values = rng.normal(size=(300, 100)) ** 2
    gammas = rng.normal(size=100)
    profile_rows(values[:2], gammas)  # compiled
    kernel = best_of(lambda: profile_rows(values, gammas))
    python = best_of(lambda: reference_profile.profile_rows(values, gammas))
    assert python / kernel >= MIN_SPEEDUP["profile"], f"kernel {kernel:.4f}s, python {python:.4f}s"
