"""Help example of the unbalanced panel (F.6.1): the exact sample Stata drew, both methods."""

import json
import warnings

import numpy as np
import pytest
from validation.compare import ATOL, RTOL
from validation.estimation_cases import unpack
from validation.help_unbalanced import ARGS, GOLDEN, METHODS, sample

from pyxtdpthresh._errors import PyxdpthreshWarning
from pyxtdpthresh.models.xtdpthresh.fit import fit_point

pytestmark = pytest.mark.golden

FROZEN = json.loads(GOLDEN.read_text(encoding="utf-8"))["cases"]


def close(got, want, what):
    got, want = np.asarray(got, dtype=float), np.asarray(want, dtype=float)
    assert got.shape == want.shape, f"{what}: shape {got.shape} != {want.shape}"
    ok = (np.abs(got - want) <= ATOL) | (np.abs(got - want) <= RTOL * np.abs(want))
    assert ok.all(), f"{what}: largest difference {np.max(np.abs(got - want)):.3g}"


@pytest.mark.parametrize("method", METHODS)
def test_unbalanced_help_example_matches_stata(method):
    ref = FROZEN[method]
    assert ref["rc"] == 0
    sc = ref["scalars"]
    args = dict(ARGS)
    y, q, x = args.pop("y"), args.pop("q"), args.pop("x")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", PyxdpthreshWarning)
        fit = fit_point(sample(), y, x, q=q, id="firm", time="year", method=method, **args)
    got = fit.search.fit
    close(got.gamma, sc["gamma"], "e(gamma)")
    close(got.theta, unpack(ref["b"]).ravel(), "e(b)")
    close(got.obj, sc["obj"], "e(obj)")
    close(got.cov, unpack(ref["vcond"]), "e(V_cond)")
    assert (fit.n_obs, fit.n_instruments, fit.n_units) == (sc["n"], sc["n_iv"], sc["n_units"])
    assert got.twostep == bool(sc["twostep"])
