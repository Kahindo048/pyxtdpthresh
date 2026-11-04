"""Common settings of the Numba kernels.

Every kernel is compiled with the same options: on-disk cache (the compilation cost is paid
once per machine), explicit ``float64`` / ``int64`` types in the callers, no ``fastmath``
(four-decimal agreement with Stata matters more than the last few percent of speed) and
NumPy error semantics, so that a division by zero gives ``inf`` or ``nan`` as in Mata
instead of raising.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from contextlib import contextmanager
from typing import Any

import numba
from threadpoolctl import ThreadpoolController

from pyxtdpthresh._config import get_options, set_options

#: Decorator for a serial kernel.
njit: Callable[..., Any] = numba.njit(cache=True, nogil=True, fastmath=False, error_model="numpy")
#: Decorator for a kernel that uses ``prange`` over independent iterations.
pjit: Callable[..., Any] = numba.njit(
    cache=True, nogil=True, fastmath=False, error_model="numpy", parallel=True
)
prange = numba.prange


#: Threads of the Numba kernels.  Their workers keep spinning after a parallel region and take the
#: cores from the BLAS products that follow: measured on the bootstrap, one kernel thread and all
#: the cores for BLAS is 1.5 to 1.9 times faster than the Numba default.  The kernels are short
#: passes over the data; the products are where the time goes.
KERNEL_THREADS = 1


def apply_threads() -> int:
    """Set the Numba threads to :data:`KERNEL_THREADS` and return the number in use."""
    numba.set_num_threads(min(KERNEL_THREADS, int(numba.config.NUMBA_NUM_THREADS)))  # type: ignore[attr-defined]
    return int(numba.get_num_threads())


def available_threads() -> int:
    """Return the threads BLAS may use: the ``threads`` option, else half of the logical cores.

    Half of the logical cores is the number of physical cores on a machine with two threads per
    core.  Measured on the bootstrap in fresh processes, all the logical cores make the first fit
    up to twice as slow as the second (the threads compete with each other), while half of them
    give the same time at the first and the second fit and the best or nearly the best time.
    """
    requested = get_options().threads
    cores: int = numba.config.NUMBA_NUM_THREADS  # type: ignore[attr-defined]
    return max(1, cores // 2) if requested is None else min(requested, cores)


def set_threads(n: int | None) -> int:
    """Set the threads the package may use and return how many that is.

    The number bounds the BLAS products (the Numba kernels run on :data:`KERNEL_THREADS`).
    ``None`` takes half of the logical cores.  The value is stored in the package options, so it
    also applies to computations started later.
    """
    set_options(threads=n)
    return available_threads()


_controller: ThreadpoolController | None = None


@contextmanager
def blas_threads() -> Iterator[int]:
    """Give the BLAS products the threads of the ``threads`` option while a computation runs.

    The limit is lifted when the block ends.
    """
    global _controller
    if _controller is None:  # scanning the loaded libraries is slow: done once
        _controller = ThreadpoolController()
    apply_threads()
    limit = available_threads()
    with _controller.limit(limits=limit, user_api="blas"):
        yield limit
