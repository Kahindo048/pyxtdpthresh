"""Validation gate of ``xtdpthresh`` (E.6): point estimates on the full panel against Stata 17.

The examples of the help file and the main instrument and search options, run through the single
entry point :func:`fit_point`.
"""

import json
import warnings

import numpy as np
import pytest
from validation.compare import ATOL, RTOL
from validation.estimation_cases import unpack
from validation.point_cases import CASES as ALL_CASES
from validation.point_cases import GOLDEN, args_of, frame

from pyxtdpthresh._errors import PyxdpthreshWarning
from pyxtdpthresh.models.xtdpthresh.fit import fit_point

pytestmark = pytest.mark.golden

FROZEN = json.loads(GOLDEN.read_text(encoding="utf-8"))["cases"]
CASES = {c.name: c for c in ALL_CASES if c.name in FROZEN}


def close(got, want, what):
    got, want = np.asarray(got, dtype=float), np.asarray(want, dtype=float)
    assert got.shape == want.shape, f"{what}: shape {got.shape} != {want.shape}"
    ok = (np.abs(got - want) <= ATOL) | (np.abs(got - want) <= RTOL * np.abs(want))
    assert ok.all(), f"{what}: largest difference {np.max(np.abs(got - want)):.3g}"


@pytest.mark.parametrize("name", list(CASES))
def test_point_estimates_match_stata(name):
    case, ref = CASES[name], FROZEN[name]
    assert ref["rc"] == 0, ref["text"]
    sc = ref["scalars"]
    args = args_of(case)
    y, q = args.pop("y"), args.pop("q")
    x = args.pop("x", ())
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", PyxdpthreshWarning)
        fit = fit_point(frame(case), y, x, q=q, id="firm", time="year", **args)
    got = fit.search.fit
    close(got.gamma, sc["gamma"], "e(gamma)")
    close(got.theta, unpack(ref["b"]).ravel(), "e(b)")
    close(got.obj, sc["obj"], "e(obj)")
    close(got.cov, unpack(ref["vcond"]), "e(V_cond)")
    assert (fit.n_obs, fit.n_instruments, fit.n_units) == (sc["n"], sc["n_iv"], sc["n_units"])
    assert got.twostep == bool(sc["twostep"])
    assert fit.search.grid_admitted == sc["grid_admitted"]
    assert fit.search.grid_effective == sc["grid_effective"]


def test_every_case_was_frozen():
    assert set(CASES) == {c.name for c in ALL_CASES}
