"""NumPy reference of :func:`pyxtdpthresh.kernels.syminv.syminv_many`.

It is also the path of the matrices too large for the kernel.
"""

from __future__ import annotations

import numpy as np

from pyxtdpthresh._types import BoolArray, FloatArray

_EPS = float(np.finfo(np.float64).eps)


def syminv_many(a: FloatArray) -> tuple[BoolArray, FloatArray]:
    """Admission and inverse of many symmetric matrices at once, ``(G, p, p)``.

    The decision is that of :func:`syminv` (positive definite after equilibration, condition at
    most ``1e12``, inverse checked against the identity), reached with eigenvalues and one batched
    inverse instead of a sweep per matrix.  The two can differ only for a matrix whose condition
    number sits at the limit.

    Returns
    -------
    ok, inverse
        Admission mask ``(G,)`` and the inverses (``nan`` where not admitted).
    """
    arr = np.asarray(a, dtype=np.float64)
    size = arr.shape[1]
    inverse = np.full(arr.shape, np.nan)
    ok = np.all(np.isfinite(arr), axis=(1, 2))
    diag = np.diagonal(arr, axis1=1, axis2=2)
    ok &= np.all(diag > 0.0, axis=1)
    if not ok.any():
        return ok, inverse
    index = np.flatnonzero(ok)
    scale = np.sqrt(diag[index])
    equil = arr[index] / (scale[:, :, None] * scale[:, None, :])
    equil = (equil + np.swapaxes(equil, 1, 2)) / 2.0
    eigenvalues = np.linalg.eigvalsh(equil)
    good = eigenvalues[:, 0] > 0.0
    cond = np.where(good, eigenvalues[:, -1] / np.where(good, eigenvalues[:, 0], 1.0), np.inf)
    good &= cond <= 1e12
    if good.any():
        sel = np.flatnonzero(good)
        inv_eq = np.linalg.inv(equil[sel])
        eye = np.eye(size)
        err = np.max(np.abs(np.matmul(equil[sel], inv_eq) - eye), axis=(1, 2))
        passed = err <= np.maximum(1e-8, 10.0 * size * _EPS * cond[sel])
        full = inv_eq / (scale[sel][:, :, None] * scale[sel][:, None, :])
        passed &= np.all(np.isfinite(full), axis=(1, 2))
        inverse[index[sel[passed]]] = full[passed]
        good[sel[~passed]] = False
    ok[index] = good
    return ok, inverse
