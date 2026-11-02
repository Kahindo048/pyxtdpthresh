"""Compile every kernel once on tiny inputs, so that the first real call is not delayed."""

from __future__ import annotations

import numpy as np

from pyxtdpthresh.kernels import moments, rng, units


def warmup() -> None:
    """Trigger the compilation (or the load from the on-disk cache) of all kernels.

    The signatures are the ones the estimators use (``float64`` / ``int64`` arrays), so the
    compiled code is reused afterwards.
    """
    z = np.array([[1.0, 0.0], [0.5, 2.0]])
    ptr = np.array([0, 1, 2], dtype=np.int64)
    lev = np.array([0, 1], dtype=np.int64)
    weights = np.ones(2)
    level = np.ones((2, 1))
    q = np.array([0.0, 1.0])
    moments.regime_moments(z, ptr, lev, weights, level, q, np.array([0.5]))
    units.unit_moments(z, np.ones(2), np.array([0, 2], dtype=np.int64))
    rng.next_uint64(rng.seed_state(1), 2)
