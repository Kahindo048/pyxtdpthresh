"""FOD, time effects, unbalanced panels and history against the frozen Stata 17 run (F).

Python rebuilds the instrument matrix and the regressors from the data and reproduces Stata's
``Z`` and ``X`` entry by entry, then the search and the final estimate.
"""

import json
import warnings

import numpy as np
import pytest
from validation.compare import ATOL, RTOL
from validation.estimation_cases import unpack
from validation.transform_cases import CASES as ALL_CASES
from validation.transform_cases import FRAGMENTS, GOLDEN, frame

from pyxtdpthresh._errors import DataError, PyxdpthreshWarning
from pyxtdpthresh.core.gmm import solve_fixed_weight
from pyxtdpthresh.models.xtdpthresh.design import check_specification
from pyxtdpthresh.models.xtdpthresh.estimator import problem_at
from pyxtdpthresh.models.xtdpthresh.sample import prepare_data
from pyxtdpthresh.models.xtdpthresh.search import search_threshold
from pyxtdpthresh.models.xtdpthresh.stack import build_stack

pytestmark = pytest.mark.golden

FROZEN = json.loads(GOLDEN.read_text(encoding="utf-8"))["cases"]
CASES = {c.name: c for c in ALL_CASES if c.name in FROZEN}
OK = [name for name in CASES if FROZEN[name]["rc"] == 0]
REFUSED = [name for name in CASES if FROZEN[name]["rc"] != 0]


def build(case):
    """Specification and stack of a case, from the data."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", PyxdpthreshWarning)
        spec = check_specification(**case.full_args())
        data = prepare_data(frame(case), spec, id="firm", time="year", where=case.where)
    return spec, build_stack(data)


def close(got, want, what):
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
    np.testing.assert_allclose(stack.z.dense, unpack(ref["z"]), rtol=0, atol=1e-8)
    close(stack.regressors(sc["gamma"]), unpack(ref["x"]), "X at the threshold")


@pytest.mark.parametrize("name", OK)
def test_fixed_weight_estimate_matches_stata(name):
    ref = FROZEN[name]
    sc = ref["scalars"]
    _, stack = build(CASES[name])
    step = problem_at(stack, sc["gamma"])
    fit = solve_fixed_weight(step.zw, stack.zy, unpack(ref["a"]), stack.n_rows)
    assert fit.ok
    close(fit.theta, unpack(ref["b"]).ravel(), "e(b)")
    close(fit.obj, sc["obj"], "e(obj)")


@pytest.mark.parametrize("name", OK)
def test_search_matches_stata(name):
    case, ref = CASES[name], FROZEN[name]
    sc = ref["scalars"]
    spec, stack = build(case)
    o = spec.options
    result = search_threshold(
        stack,
        grid=o.grid,
        grid_type=o.grid_type,
        observed_support=o.grid_sample == "observed",
        trim=o.trim,
        min_regime=o.min_regime,
        refine=o.refine,
        center=o.center,
    )
    fit = result.fit
    close(fit.gamma, sc["gamma"], "gamma")
    close(fit.theta, unpack(ref["b"]).ravel(), "e(b)")
    close(fit.obj, sc["obj"], "e(obj)")
    close(fit.cov, unpack(ref["vcond"]), "e(V_cond)")
    assert fit.twostep == bool(sc["twostep"])
    assert result.grid_admitted == sc["grid_admitted"]
    assert result.grid_effective == sc["grid_effective"]
    close(result.stage1_gamma, sc["stage1_gamma"], "first-stage threshold")
    if o.kink:
        assert result.kink_refined == bool(sc["kink_refined"])
    assert (result.refine.added if result.refine else 0) == sc["refine_added"]


@pytest.mark.parametrize("name", REFUSED)
def test_refused_requests_match_stata(name):
    case, ref = CASES[name], FROZEN[name]
    assert case.key is not None, f"{name}: Stata refused {ref['text']!r}"
    assert FRAGMENTS[case.key] in ref["text"]
    with pytest.raises(DataError) as raised:
        build(case)
    assert raised.value.key == case.key
    assert raised.value.stata_code == ref["rc"]


def test_every_case_was_frozen():
    assert set(CASES) == {c.name for c in ALL_CASES}
    assert all(ALL_CASES[i].key is None for i, c in enumerate(ALL_CASES) if c.name in OK)
