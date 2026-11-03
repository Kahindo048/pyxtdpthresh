"""Instruments and fixed-threshold GMM of ``xtdpthresh`` against the frozen Stata 17 run (E.3, E.4).

Python rebuilds the instrument matrix and the regressors from the data and reproduces Stata's
``Z`` and ``X`` entry by entry; with Stata's own weight matrix it reproduces ``e(b)``,
``e(obj)`` and ``e(V_cond)``; and when its own second-step weight equals Stata's, the whole
two-step chain agrees too.
"""

import json
import warnings

import numpy as np
import pytest
from validation.compare import ATOL, RTOL
from validation.estimation_cases import CASES as ALL_CASES
from validation.estimation_cases import GOLDEN, frame, unpack

from pyxtdpthresh._errors import PyxdpthreshWarning
from pyxtdpthresh.core.gmm import cluster_omega, sandwich, solve_fixed_weight
from pyxtdpthresh.models.xtdpthresh.design import check_specification
from pyxtdpthresh.models.xtdpthresh.estimator import (
    estimate_at,
    moments_by_unit,
    problem_at,
)
from pyxtdpthresh.models.xtdpthresh.sample import prepare_data
from pyxtdpthresh.models.xtdpthresh.stack import build_stack

pytestmark = pytest.mark.golden

FROZEN = json.loads(GOLDEN.read_text(encoding="utf-8"))["cases"]
CASES = {c.name: c for c in ALL_CASES if c.name in FROZEN}
OK = [name for name in CASES if FROZEN[name]["rc"] == 0]


def build(case):
    """Stack of a case, built from the data."""
    df = frame(case)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", PyxdpthreshWarning)
        spec = check_specification(**case.full_args())
        data = prepare_data(df, spec, id="firm", time="year")
    return spec, build_stack(data)


def assert_close(got, want, what):
    got, want = np.asarray(got, dtype=float), np.asarray(want, dtype=float)
    assert got.shape == want.shape, f"{what}: shape {got.shape} != {want.shape}"
    ok = (np.abs(got - want) <= ATOL) | (np.abs(got - want) <= RTOL * np.abs(want))
    assert ok.all(), f"{what}: largest difference {np.max(np.abs(got - want)):.3g}"


@pytest.mark.parametrize("name", OK)
def test_instruments_and_regressors_match_stata(name):
    ref = FROZEN[name]
    sc = ref["scalars"]
    _, stack = build(CASES[name])
    inst = stack.instruments
    assert stack.n_rows == sc["n"]
    assert stack.n_instruments == sc["n_iv"]
    assert (inst.n_common, inst.n_dependent, inst.dep_near) == (
        sc["n_common"], sc["n_dep"], sc["n_dep_near"],
    )  # fmt: skip
    assert stack.first_weight.fallback == sc["w1_fallback"]
    np.testing.assert_allclose(stack.z.dense, unpack(ref["z"]), rtol=0, atol=1e-9)
    assert_close(stack.regressors(sc["gamma"]), unpack(ref["x"]), "X at the threshold")


@pytest.mark.parametrize("name", OK)
def test_fixed_weight_estimate_matches_stata(name):
    ref = FROZEN[name]
    sc = ref["scalars"]
    spec, stack = build(CASES[name])
    weight = unpack(ref["a"])
    step = problem_at(stack, sc["gamma"])
    fit = solve_fixed_weight(step.zw, stack.zy, weight, stack.n_rows)
    assert fit.ok
    assert_close(fit.theta, unpack(ref["b"]).ravel(), "e(b)")
    assert_close(fit.obj, sc["obj"], "e(obj)")
    resid = step.residual(stack, fit.theta)
    omega = cluster_omega(
        moments_by_unit(stack, resid), stack.n_rows, stack.n_units, spec.options.center
    )
    cov = sandwich(step.zw, weight, omega, stack.n_rows)
    assert cov is not None
    assert_close(cov, unpack(ref["vcond"]), "e(V_cond)")


def chain_cases():
    """Cases where Python's second-step weight at the threshold equals Stata's."""
    hits = []
    for name in OK:
        spec, stack = build(CASES[name])
        fit = estimate_at(stack, FROZEN[name]["scalars"]["gamma"], center=spec.options.center)
        weight = unpack(FROZEN[name]["a"])
        if fit is not None and fit.weight.shape == weight.shape:
            scale = np.max(np.abs(weight))
            if np.max(np.abs(fit.weight - weight)) <= 1e-8 * scale:
                hits.append(name)
    return hits


CHAIN = chain_cases()


@pytest.mark.parametrize("name", CHAIN)
def test_two_step_chain_matches_stata(name):
    ref = FROZEN[name]
    spec, stack = build(CASES[name])
    fit = estimate_at(stack, ref["scalars"]["gamma"], center=spec.options.center)
    assert fit is not None
    assert fit.twostep == bool(ref["scalars"]["twostep"])
    assert_close(fit.theta, unpack(ref["b"]).ravel(), "e(b)")
    assert_close(fit.obj, ref["scalars"]["obj"], "e(obj)")
    assert_close(fit.cov, unpack(ref["vcond"]), "e(V_cond)")


def test_the_two_step_chain_is_checked_on_most_cases():
    assert len(CHAIN) >= 0.6 * len(OK), f"{len(CHAIN)} of {len(OK)} cases reach the chain"


def test_every_case_was_frozen():
    assert set(CASES) == {c.name for c in ALL_CASES}
