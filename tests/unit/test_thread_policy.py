"""Thread policy: one thread for the Numba kernels, the ``threads`` option for BLAS."""

import numba
import pytest
from threadpoolctl import threadpool_info

from pyxtdpthresh import option_context
from pyxtdpthresh.kernels import _jit


def test_the_kernels_run_on_one_thread_whatever_the_option():
    for threads in (None, 1, 4):
        with option_context(threads=threads):
            assert _jit.apply_threads() == _jit.KERNEL_THREADS == 1
            assert numba.get_num_threads() == 1


def test_the_option_bounds_the_blas_threads():
    cores = numba.config.NUMBA_NUM_THREADS
    with option_context(threads=None):
        assert _jit.available_threads() == max(1, cores // 2)
    with option_context(threads=1):
        assert _jit.available_threads() == 1
    with option_context(threads=10_000):
        assert _jit.available_threads() == cores  # capped at the cores
    assert _jit.set_threads(2) == min(2, cores)
    assert _jit.set_threads(None) == max(1, cores // 2)


def test_blas_threads_applies_the_limit_and_lifts_it():
    before = [lib["num_threads"] for lib in threadpool_info() if lib["user_api"] == "blas"]
    with option_context(threads=1), _jit.blas_threads() as limit:
        inside = [lib["num_threads"] for lib in threadpool_info() if lib["user_api"] == "blas"]
        assert limit == 1 and set(inside) <= {1}
    after = [lib["num_threads"] for lib in threadpool_info() if lib["user_api"] == "blas"]
    assert after == before


@pytest.mark.parametrize("threads", [0, -1])
def test_a_non_positive_number_of_threads_is_refused(threads):
    with pytest.raises(ValueError):
        option_context(threads=threads).__enter__()
