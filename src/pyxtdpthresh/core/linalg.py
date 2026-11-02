"""Linear algebra with the semantics of Stata's Mata.

Mata's ``invsym()`` is a sweep-operator inverse that silently turns a symmetric matrix
that is singular, or not positive semidefinite, into a *generalised* inverse: every pivot
that is too small, or negative, is dropped and its row and column of the result are set to
zero.  ``xtdpthresh`` relies on that behaviour (and guards against it in :func:`syminv`),
so it is reproduced here rather than replaced by :func:`numpy.linalg.inv`.

What was measured on Stata 17 MP (``validation/stata/t_invsym_*.do``, ``la_*`` exports):

* ``invsym`` reads only the upper triangle of its argument and ``cholinv`` only the lower
  one (they differ on a non-symmetric input);
* the sweep pivots on the largest remaining diagonal element, so for a singular matrix the
  dropped variable is not always the last one;
* the pivot is dropped when it is at most ``INVSYM_REL_TOL`` times the *original* diagonal
  element, at most ``INVSYM_ABS_FLOOR``, or negative;
* ``cholinv`` returns missing when the Cholesky factorisation fails or the matrix is
  numerically singular (reciprocal condition number below ``CHOLINV_RCOND_FLOOR``).

For a well-conditioned positive definite matrix no pivot can be dropped in any order, so
a Cholesky factorisation gives the inverse directly; the explicit sweep is only needed
when the smallest eigenvalue cannot be bounded safely away from the tolerance.
"""

from __future__ import annotations

from typing import NamedTuple

import numpy as np
from scipy.linalg import LinAlgError, cho_factor, cho_solve

from pyxtdpthresh._types import BoolArray, FloatArray

#: Relative pivot tolerance of ``invsym``: Stata drops a pivot at 8.8e-10 times the original
#: diagonal element and keeps it at 1.17e-9 times, so 1e-9 is adopted.
INVSYM_REL_TOL = 1e-9
#: Absolute pivot floor of ``invsym`` (bracketed between 10^-19.125 and 10^-19).
INVSYM_ABS_FLOOR = 9e-20
#: ``cholinv`` gives missing below this reciprocal condition number.  Stata inverts a
#: matrix of reciprocal condition number 3.7e-17 and returns missing for badly scaled
#: matrices of 1e-32 and below; the factorisation itself fails from about 1e-17.
CHOLINV_RCOND_FLOOR = 1e-20
#: ``epsilon(1)`` of Mata.
_EPS = float(np.finfo(np.float64).eps)


class SymInv(NamedTuple):
    """Result of :func:`syminv`: admission flag and inverse (NaN when not admitted)."""

    ok: bool
    inv: FloatArray


# ----------------------------------------------------------------------------- invsym
def _lower_sym(a: FloatArray) -> FloatArray:
    """Symmetric matrix built from the lower triangle of ``a`` (what ``cholinv`` reads)."""
    return np.asarray(np.tril(a) + np.tril(a, -1).T, dtype=np.float64)


def _upper_sym(a: FloatArray) -> FloatArray:
    """Symmetric matrix built from the upper triangle of ``a`` (what ``invsym`` reads)."""
    return np.asarray(np.triu(a) + np.triu(a, 1).T, dtype=np.float64)


def _pivot_floor(diag: FloatArray) -> FloatArray:
    """Smallest pivot kept at each position, from the original diagonal."""
    return np.maximum(INVSYM_REL_TOL * np.maximum(diag, 0.0), INVSYM_ABS_FLOOR)


def _sweep(a: FloatArray) -> tuple[FloatArray, BoolArray]:
    """Generalised inverse by pivoted sweep; returns it with the dropped-pivot mask."""
    # Stata: invsym (Mata built-in); order and tolerance measured, see module docstring.
    work = np.array(a, dtype=np.float64, copy=True)
    n = work.shape[0]
    floor = _pivot_floor(np.diag(work))
    dropped = np.zeros(n, dtype=np.bool_)
    pending = np.ones(n, dtype=np.bool_)
    for _ in range(n):
        current = np.where(pending, np.diag(work), -np.inf)
        k = int(np.argmax(current))
        pending[k] = False
        pivot = work[k, k]
        if not pivot > floor[k]:  # also catches NaN
            work[k, :] = 0.0
            work[:, k] = 0.0
            dropped[k] = True
            continue
        row = work[k, :] / pivot
        col = work[:, k].copy()
        col[k] = 0.0
        work -= np.outer(col, row)
        work[k, :] = row
        work[:, k] = -col / pivot
        work[k, k] = 1.0 / pivot
    return (work + work.T) / 2.0, dropped


def _safe_without_drop(diag: FloatArray, trace_inv: FloatArray) -> BoolArray:
    """Flag the matrices in which no pivot can be dropped, whatever the sweep order.

    Every pivot of a positive definite matrix is at least its smallest eigenvalue, which is
    at least ``1 / trace(inverse)``; a factor 10 absorbs rounding in the inverse.
    """
    bound = 1.0 / trace_inv
    return np.asarray(bound > 10.0 * _pivot_floor(np.max(diag, axis=-1)), dtype=np.bool_)


def _invsym(a: FloatArray) -> tuple[FloatArray, int]:
    """Core of :func:`invsym`: the inverse and the number of dropped pivots."""
    sym = _upper_sym(a)
    n = sym.shape[0]
    if n == 0:
        return sym, 0
    if not np.all(np.isfinite(sym)):
        return np.full(sym.shape, np.nan), 0
    try:
        factor = cho_factor(sym, lower=True, check_finite=False)
    except LinAlgError:
        inv, dropped = _sweep(sym)
        return inv, int(dropped.sum())
    inv = cho_solve(factor, np.eye(n), check_finite=False)
    if _safe_without_drop(np.diag(sym), np.trace(inv)):
        return (inv + inv.T) / 2.0, 0
    inv, dropped = _sweep(sym)
    return inv, int(dropped.sum())


def invsym(a: FloatArray) -> FloatArray:
    """Inverse of a symmetric matrix with Mata's ``invsym()`` semantics.

    Parameters
    ----------
    a
        Square matrix; only its upper triangle is read, as in Mata.

    Returns
    -------
    numpy.ndarray
        The inverse when ``a`` is positive definite; otherwise a generalised inverse in
        which the rows and columns of dropped pivots are zero.
    """
    # Stata: invsym (Mata built-in)
    return _invsym(np.asarray(a, dtype=np.float64))[0]


def invsym_dropped(a: FloatArray) -> tuple[FloatArray, int]:
    """:func:`invsym` together with the number of dropped pivots.

    The count equals Mata's ``diag0cnt(invsym(a))``: ``xtdpthresh`` uses it to tell a true
    inverse from a generalised one.
    """
    return _invsym(np.asarray(a, dtype=np.float64))


def invsym_batch(a: FloatArray) -> FloatArray:
    """Apply :func:`invsym` to a stack of symmetric matrices of shape ``(..., p, p)``.

    One batched Cholesky factorisation and one batched solve handle the regular case;
    matrices that fail it, or make the batch factorisation fail, are inverted one by one
    with :func:`invsym`.
    """
    arr = np.asarray(a, dtype=np.float64)
    p = arr.shape[-1]
    flat = arr.reshape(-1, p, p)
    out = np.empty_like(flat)
    if flat.shape[0] == 0 or p == 0:
        return out.reshape(arr.shape)
    sym = np.triu(flat) + np.swapaxes(np.triu(flat, 1), -1, -2)
    todo = np.ones(flat.shape[0], dtype=np.bool_)
    try:
        np.linalg.cholesky(sym)
    except np.linalg.LinAlgError:
        pass  # at least one matrix is not positive definite: handled one by one below
    else:
        inv = np.linalg.solve(sym, np.broadcast_to(np.eye(p), sym.shape))
        inv = (inv + np.swapaxes(inv, -1, -2)) / 2.0
        diag = np.diagonal(sym, axis1=-2, axis2=-1)
        safe = _safe_without_drop(diag, np.trace(inv, axis1=-2, axis2=-1))
        out[safe] = inv[safe]
        todo = ~safe
    for idx in np.flatnonzero(todo):
        out[idx] = _invsym(flat[idx])[0]
    return out.reshape(arr.shape)


# ----------------------------------------------------------------------------- cholinv
def cholinv(a: FloatArray) -> FloatArray:
    """Inverse of a symmetric positive definite matrix (Mata ``cholinv()``).

    Only the lower triangle is read.  Returns a matrix of NaN, as Mata returns missing,
    when the matrix is not positive definite or is numerically singular.
    """
    # Stata: cholinv (Mata built-in); singularity threshold measured, see module docstring.
    arr = np.asarray(a, dtype=np.float64)
    if arr.shape[0] == 0:
        return np.zeros((0, 0), dtype=np.float64)
    sym = _lower_sym(arr)
    missing = np.full(arr.shape, np.nan)
    if not np.all(np.isfinite(sym)):
        return missing
    try:
        factor = cho_factor(sym, lower=True, check_finite=False)
    except LinAlgError:
        return missing
    inv = np.asarray(cho_solve(factor, np.eye(arr.shape[0]), check_finite=False))
    rcond = 1.0 / (np.linalg.norm(sym, 1) * np.linalg.norm(inv, 1))
    if not rcond >= CHOLINV_RCOND_FLOOR:
        return missing
    return np.asarray((inv + inv.T) / 2.0, dtype=np.float64)


# ----------------------------------------------------------------------------- syminv
def syminv(a: FloatArray) -> SymInv:
    """Scale-equivariant inverse with an admission check (``xdpt2_syminv``).

    The matrix is equilibrated by its diagonal, must be positive definite with a 2-norm
    condition number of at most ``1e12``, and the inverse is rejected when a pivot is
    dropped or when ``C @ inv(C)`` is further from the identity than
    ``max(1e-8, 10 n eps cond)``.

    Returns
    -------
    SymInv
        ``ok`` is False, and ``inv`` is NaN, when the matrix is not admitted.
    """
    # Stata: xdpt2_syminv (xtdpthresh.ado:2516)
    arr = np.asarray(a, dtype=np.float64)
    rejected = SymInv(False, np.full(arr.shape, np.nan))
    if arr.ndim != 2 or arr.shape[0] == 0 or arr.shape[0] != arr.shape[1]:
        return rejected
    if not np.all(np.isfinite(arr)):
        return rejected

    diag = np.diag(arr)
    if np.any(diag <= 0.0):
        return rejected
    scale = np.sqrt(diag)
    equil = arr / np.outer(scale, scale)
    equil = (equil + equil.T) / 2.0
    # Stata: cholesky(C) returns missing unless C is positive definite
    try:
        np.linalg.cholesky(equil)
    except np.linalg.LinAlgError:
        return rejected
    cond = float(np.linalg.cond(equil))
    if not np.isfinite(cond) or cond > 1e12:
        return rejected

    inv_eq, n_dropped = _invsym(equil)
    if n_dropped > 0 or not np.all(np.isfinite(inv_eq)):
        return rejected
    tol = max(1e-8, 10.0 * equil.shape[0] * _EPS * cond)
    if np.max(np.abs(equil @ inv_eq - np.eye(equil.shape[0]))) > tol:
        return rejected
    inv = inv_eq / np.outer(scale, scale)
    if not np.all(np.isfinite(inv)):
        return rejected
    return SymInv(True, inv)


# ------------------------------------------------------------------- psd_ok and objtol
def psd_ok(v: FloatArray) -> bool:
    """Check that ``v`` is finite, symmetric and positive semidefinite up to a tolerance.

    Mirrors ``xdpt2_psd_ok``: symmetric within ``1e-8`` of the largest entry, smallest
    eigenvalue at least ``-1e-10`` times the largest eigenvalue in absolute value.
    """
    # Stata: xdpt2_psd_ok (xtdpthresh.ado:2554)
    arr = np.asarray(v, dtype=np.float64)
    if arr.ndim != 2 or arr.shape[0] == 0 or arr.shape[0] != arr.shape[1]:
        return False
    if not np.all(np.isfinite(arr)):
        return False
    if np.max(np.abs(arr - arr.T)) > 1e-8 * np.max(np.abs(arr)):
        return False
    eigenvalues = np.linalg.eigvalsh((arr + arr.T) / 2.0)
    largest = float(np.max(np.abs(eigenvalues)))
    if not np.isfinite(largest) or largest <= 0.0:
        return False
    return bool(np.min(eigenvalues) >= -1e-10 * largest)


def objtol(a: float, b: float, rel: float) -> float:
    """Scale-equivariant tolerance to compare two objective values (``xdpt2_objtol``).

    ``rel * max(|a|, |b|)``, and zero when both are zero, so that tie decisions do not
    depend on the units of the outcome.
    """
    # Stata: xdpt2_objtol (xtdpthresh.ado:2497)
    scale = max(abs(a), abs(b))
    return 0.0 if scale == 0.0 else rel * scale
