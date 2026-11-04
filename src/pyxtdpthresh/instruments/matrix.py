"""Cross products with the instrument matrix, dense or sparse according to its fill.

The per-period layout makes ``Z`` mostly zeros (each row uses the block of its own period), so
products with ``Z`` go through a compressed-row copy; a collapsed or small ``Z`` is mostly
non-zero and BLAS on the dense array is faster.  The choice is made once from the fill.
"""

from __future__ import annotations

import numpy as np
from scipy import sparse

from pyxtdpthresh._types import FloatArray, IntArray

#: Fill (share of non-zero entries) below which products use the sparse copy.
SPARSE_FILL = 0.15


class InstrumentMatrix:
    """Instruments of the stacked equations, ``(n, k)``.

    Parameters
    ----------
    z
        Dense instrument matrix.
    """

    def __init__(self, z: FloatArray) -> None:
        self.dense: FloatArray = np.ascontiguousarray(z, dtype=np.float64)
        self.csr = sparse.csr_matrix(self.dense)
        cells = max(self.dense.size, 1)
        self._use_sparse = self.csr.nnz / cells < SPARSE_FILL
        self._csc: sparse.csc_matrix | None = None
        self._csr64: tuple[IntArray, IntArray] | None = None

    @property
    def shape(self) -> tuple[int, int]:
        """Rows and columns."""
        return int(self.dense.shape[0]), int(self.dense.shape[1])

    @property
    def csc(self) -> sparse.csc_matrix:
        """Compressed-column copy with sorted indices (built on first use)."""
        if self._csc is None:
            self._csc = self.csr.tocsc()
            self._csc.sort_indices()
        return self._csc

    @property
    def csr64(self) -> tuple[IntArray, IntArray]:
        """``indptr`` and ``indices`` of the compressed-row copy as ``int64`` (built once)."""
        if self._csr64 is None:
            self._csr64 = (self.csr.indptr.astype(np.int64), self.csr.indices.astype(np.int64))
        return self._csr64

    def gram(self) -> FloatArray:
        """``Z'Z`` as a dense ``(k, k)`` matrix."""
        if self._use_sparse:
            return np.asarray((self.csr.T @ self.csr).toarray())
        return np.asarray(self.dense.T @ self.dense)

    def rmatmul(self, a: FloatArray) -> FloatArray:
        """``Z'a`` for a vector or a matrix ``a`` with ``n`` rows."""
        if self._use_sparse:
            return np.asarray(self.csr.T @ a)
        return np.asarray(self.dense.T @ a)

    def cross_rows(self, first: IntArray, second: IntArray) -> FloatArray:
        """``Z[first]' Z[second]``, the sum of ``z_a z_b'`` over the row pairs ``(a, b)``."""
        if self._use_sparse:
            return np.asarray((self.csr[first].T @ self.csr[second]).toarray())
        return np.asarray(self.dense[first].T @ self.dense[second])
