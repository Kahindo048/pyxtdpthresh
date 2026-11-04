"""Seconds of ``import`` and of the first two fits in a fresh process (J.2.4).

Prints ``import first_fit second_fit``.  Run it once with an empty Numba cache and once with it
filled to measure the compilation.
"""

import sys
import time

t0 = time.perf_counter()
import pyxtdpthresh as pyx  # noqa: E402

t1 = time.perf_counter()
frame = pyx.load_dataset("invest")
small = frame[frame["firm"] <= 60]
options = {"q": "tobin_q", "id": "firm", "time": "year"}
r = pyx.xtdpthresh(small, "invest", ["cashflow"], n_boot=29, grid_ci=30, seed=1, **options)
t2 = time.perf_counter()
r = pyx.xtdpthresh(small, "invest", ["cashflow"], n_boot=29, grid_ci=30, seed=1, **options)
t3 = time.perf_counter()
print(f"{t1 - t0:.2f} {t2 - t1:.2f} {t3 - t2:.2f}", file=sys.stdout)
