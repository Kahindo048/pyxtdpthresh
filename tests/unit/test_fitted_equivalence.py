"""The shortcuts of the bootstrap loop (J.2.3) equal the direct computations they replace."""

import numpy as np
import pytest

from pyxtdpthresh import load_dataset
from pyxtdpthresh.kernels.units import unit_moments, unit_moments_arrays
from pyxtdpthresh.models.xtdpthresh.estimator import moments_by_unit
from pyxtdpthresh.models.xtdpthresh.fit import fit_point

CASES = {
    "fd": {},
    "fod": {"method": "fod"},
    "time_effects": {"time_effects": True},
    "kink": {"kink": True},
    "collapse": {"collapse": True},
    "fod_time_effects": {"method": "fod", "time_effects": True},
}


@pytest.fixture(scope="module")
def frame():
    df = load_dataset("invest")
    return df[df["firm"] <= df["firm"].unique()[80]].reset_index(drop=True)


@pytest.fixture(scope="module", params=list(CASES))
def fit(request, frame):
    x = ["cashflow", "tobin_q"] if request.param == "kink" else ["cashflow"]
    return fit_point(
        frame, "invest", x, q="tobin_q", id="firm", time="year", bootstrap=False,
        **CASES[request.param],
    )  # fmt: skip


def candidates(fit):
    """Return the estimated threshold and two others inside the support."""
    low, high = np.quantile(fit.stack.q_values, [0.25, 0.75])
    return [fit.search.fit.gamma, low, high]


def test_the_fitted_values_equal_the_regressors_times_theta(fit):
    theta = fit.search.fit.theta
    for gamma in candidates(fit):
        direct = fit.stack.regressors(gamma) @ theta
        np.testing.assert_allclose(fit.stack.fitted(gamma, theta), direct, rtol=1e-12, atol=1e-13)


def test_the_moments_of_the_fit_equal_the_cached_moments_times_theta(fit):
    """``Z'F/n`` is ``(Z'X(gamma)/n) theta``: the bootstrap reads it from the candidate cache."""
    stack, theta = fit.stack, fit.search.fit.theta
    for gamma in candidates(fit):
        direct = stack.z.rmatmul(stack.regressors(gamma) @ theta) / stack.n_rows
        cached = stack.moments(np.array([gamma]))[0] @ theta
        np.testing.assert_allclose(cached, direct, rtol=1e-10, atol=1e-12)


def test_the_unit_moments_do_not_depend_on_how_the_index_arrays_are_given(fit):
    stack = fit.stack
    resid = stack.dy - stack.fitted(fit.search.fit.gamma, fit.search.fit.theta)
    reference = unit_moments(stack.z.csr, resid, stack.unit_ptr)
    csr = stack.z.csr
    indptr, indices = stack.z.csr64
    again = unit_moments_arrays(indptr, indices, csr.data, csr.shape, resid, stack.unit_ptr)
    np.testing.assert_array_equal(again, reference)
    np.testing.assert_array_equal(moments_by_unit(stack, resid), reference)


def test_the_int64_index_arrays_are_built_once(fit):
    first = fit.stack.z.csr64
    assert fit.stack.z.csr64 is first
    assert first[0].dtype == np.int64 and first[1].dtype == np.int64
