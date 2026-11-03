"""Threshold search and final estimate of ``xtdpthresh`` against the frozen Stata 17 run (E.5)."""

import json
import math
import warnings

import numpy as np
import pytest
from validation.compare import ATOL, RTOL
from validation.estimation_cases import frame, unpack
from validation.search_cases import CASES as ALL_CASES
from validation.search_cases import FRAGMENTS, GOLDEN

from pyxtdpthresh._errors import PyxdpthreshError, PyxdpthreshWarning
from pyxtdpthresh.models.xtdpthresh.design import check_specification
from pyxtdpthresh.models.xtdpthresh.sample import prepare_data
from pyxtdpthresh.models.xtdpthresh.search import search_threshold
from pyxtdpthresh.models.xtdpthresh.stack import build_stack

pytestmark = pytest.mark.golden

FROZEN = json.loads(GOLDEN.read_text(encoding="utf-8"))["cases"]
CASES = {c.name: c for c in ALL_CASES if c.name in FROZEN}
OK = [name for name in CASES if FROZEN[name]["rc"] == 0]


def run_python(case):
    """Search result of a case, from the data."""
    df = frame(case)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", PyxdpthreshWarning)
        spec = check_specification(**case.full_args())
        data = prepare_data(df, spec, id="firm", time="year")
    o = spec.options
    stack = build_stack(data)
    return search_threshold(
        stack,
        grid=o.grid,
        grid_type=o.grid_type,
        observed_support=o.grid_sample == "observed",
        trim=o.trim,
        min_regime=o.min_regime,
        refine=o.refine,
        center=o.center,
    )


def close(got, want, what):
    got, want = np.asarray(got, dtype=float), np.asarray(want, dtype=float)
    assert got.shape == want.shape, f"{what}: shape {got.shape} != {want.shape}"
    ok = (np.abs(got - want) <= ATOL) | (np.abs(got - want) <= RTOL * np.abs(want))
    assert ok.all(), f"{what}: largest difference {np.max(np.abs(got - want)):.3g}"


@pytest.mark.parametrize("name", OK)
def test_search_matches_stata(name):
    case, ref = CASES[name], FROZEN[name]
    sc = ref["scalars"]
    assert case.key is None, f"{name}: Stata accepted a request that should be refused"
    result = run_python(case)
    fit = result.fit
    close(fit.gamma, sc["gamma"], "gamma")
    close(fit.theta, unpack(ref["b"]).ravel(), "e(b)")
    close(fit.obj, sc["obj"], "e(obj)")
    close(fit.cov, unpack(ref["vcond"]), "e(V_cond)")
    assert fit.twostep == bool(sc["twostep"])
    assert result.grid_admitted == sc["grid_admitted"]
    assert result.grid_effective == sc["grid_effective"]
    close([result.q_lo, result.q_hi], [sc["q_lo"], sc["q_hi"]], "q bounds")
    close(result.stage1_gamma, sc["stage1_gamma"], "first-stage threshold")
    if case.full_args().get("kink"):
        assert result.kink_refined == bool(sc["kink_refined"])
    stats = result.refine
    assert (stats.iterations if stats else 0) == sc["refine_iterations"]
    assert (stats.added if stats else 0) == sc["refine_added"]


@pytest.mark.parametrize("name", [n for n in CASES if FROZEN[n]["rc"] != 0])
def test_refused_requests_match_stata(name):
    case, ref = CASES[name], FROZEN[name]
    assert case.key is not None
    assert FRAGMENTS[case.key] in ref["text"], f"{name}: Stata said {ref['text']!r}"
    with pytest.raises(PyxdpthreshError) as raised:
        run_python(case)
    assert raised.value.key == case.key
    assert raised.value.stata_code == ref["rc"]


def test_every_case_was_frozen():
    assert set(CASES) == {c.name for c in ALL_CASES}
    assert not any(math.isnan(FROZEN[n]["scalars"]["gamma"]) for n in OK)
