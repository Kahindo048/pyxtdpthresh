"""Kernel of the smallest value of the criterion profile (J.2: unit bootstrap)."""

import os
import subprocess
import sys
import tempfile
import textwrap

import numpy as np
import pytest

from pyxtdpthresh.inference.bootstrap.objective import is_degenerate, usable_minimum
from pyxtdpthresh.kernels.profile import profile_rows
from pyxtdpthresh.kernels.reference import profile as reference


def table(seed, rows=60, cols=40):
    """Random profiles with ties, missing values, empty rows and rows of zeros."""
    rng = np.random.default_rng(seed)
    values = rng.normal(size=(rows, cols)) ** 2
    values[rng.random((rows, cols)) < 0.2] = np.nan
    values[::7, 3] = values[::7, 9] = 0.5  # exact ties
    values[1::11, 5] = values[1::11, 12] * (1 + 1e-14)  # ties within the tolerance
    values[2] = np.nan  # no finite value
    values[3] = 0.0  # all zero
    values[4] = 2.0  # flat
    values[5] = np.nan
    values[5, 7] = 1.0  # one value
    values[6, :] = np.where(np.arange(cols) % 2 == 0, np.inf, values[6, :])
    return values, np.sort(rng.normal(size=cols))[rng.permutation(cols)]


@pytest.mark.parametrize("seed", range(8))
def test_the_kernel_equals_the_numpy_reference(seed):
    values, gammas = table(seed)
    got, expected = profile_rows(values, gammas), reference.profile_rows(values, gammas)
    for a, b in zip(got, expected, strict=True):
        np.testing.assert_array_equal(a, b)  # nan equal to nan


def test_edge_rows():
    values, gammas = table(0)
    best, count, high = profile_rows(values, gammas)
    assert best[2] == -1 and count[2] == 0 and np.isnan(high[2])
    assert count[5] == 1 and best[5] == 7 and high[5] == 1.0
    assert count[3] == values.shape[1] and best[3] == int(
        np.argmin(gammas)
    )  # all ties: smallest gamma
    assert count[6] == np.isfinite(values[6]).sum()  # infinite values do not count


def test_ties_within_the_tolerance_go_to_the_smaller_threshold():
    best, count, high = profile_rows(
        np.array([[3.0, 1.0, 1.0 + 1e-14, 2.0, np.nan]]), np.array([0.1, 0.5, 0.2, 0.3, 0.4])
    )
    assert (best[0], count[0], high[0]) == (2, 4, 3.0)


def test_the_shape_is_checked():
    with pytest.raises(ValueError):
        profile_rows(np.ones((3, 4)), np.ones(5))
    with pytest.raises(ValueError):
        profile_rows(np.ones(4), np.ones(4))


@pytest.mark.parametrize("seed", range(4))
def test_usable_minimum_is_the_row_by_row_rule(seed):
    values, gammas = table(seed)
    best, low, usable = usable_minimum(values, gammas)
    ref_best, ref_count, ref_high = reference.profile_rows(values, gammas)
    for r in range(values.shape[0]):
        want = ref_best[r] >= 0 and not is_degenerate(
            float(values[r, ref_best[r]]), float(ref_high[r]), int(ref_count[r])
        )
        assert bool(usable[r]) == want
        assert best[r] == ref_best[r]
        if ref_best[r] >= 0:
            assert low[r] == values[r, ref_best[r]]


def test_the_kernel_agrees_with_jit_disabled():
    code = textwrap.dedent(
        """
        import sys
        import numpy as np
        sys.path.insert(0, ".")
        from tests.unit.test_profile_kernel import table
        from pyxtdpthresh.kernels.profile import profile_rows
        values, gammas = table(5)
        best, count, high = profile_rows(values, gammas)
        np.savez(sys.argv[1], best=best, count=count, high=high)
        """
    )
    values, gammas = table(5)
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "out.npz")
        env = {**os.environ, "NUMBA_DISABLE_JIT": "1"}
        subprocess.run([sys.executable, "-c", code, path], check=True, env=env)
        with np.load(path) as saved:
            for name, a in zip(
                ("best", "count", "high"), profile_rows(values, gammas), strict=True
            ):
                np.testing.assert_array_equal(saved[name], a)
