"""Compile every kernel once on tiny inputs, so that the first real call is not delayed."""

from __future__ import annotations

import numpy as np

from pyxtdpthresh.kernels import cleaning, moments, profile, rng, sweep, syminv, transforms, units


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
    profile.profile_rows(np.array([[1.0, np.nan]]), q)
    syminv.syminv_many(np.eye(2)[None])
    rng.next_uint64(rng.seed_state(1), 2)
    sweep.sweep(np.eye(2), np.full(2, 1e-9))
    cleaning.independent_columns(np.eye(2), 1e-13)
    transforms.fod_triplets(np.array([0, 3], dtype=np.int64), np.ones(3, dtype=bool))
