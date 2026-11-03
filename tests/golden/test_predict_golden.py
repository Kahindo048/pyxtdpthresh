"""``predict`` against the frozen Stata 17 run (G.8.4): residuals, fit, AR residuals, regime."""

import json
import warnings

import numpy as np
import pytest
from validation.compare import ATOL, RTOL
from validation.estimation_cases import unpack
from validation.predict_cases import CASES as ALL_CASES
from validation.predict_cases import CONDITION, GOLDEN, KINDS
from validation.variance_cases import frame

from pyxtdpthresh._errors import DataError, PyxdpthreshWarning, SpecificationError
from pyxtdpthresh.models.xtdpthresh.fit import fit_point

pytestmark = pytest.mark.golden

FROZEN = json.loads(GOLDEN.read_text(encoding="utf-8"))["cases"]
CASES = {c.name: c for c in ALL_CASES if c.name in FROZEN}
_FITS: dict[str, tuple] = {}


def estimate(name):
    if name not in _FITS:
        case = CASES[name]
        args = case.full_args()
        y, q = args.pop("y"), args.pop("q")
        x = args.pop("x", ())
        df = frame(case)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", PyxdpthreshWarning)
            _FITS[name] = (fit_point(df, y, x, q=q, id="firm", time="year", **args), df)
    return _FITS[name]


def close(got, want, what):
    got, want = np.asarray(got, dtype=float), np.asarray(want, dtype=float)
    assert got.shape == want.shape, f"{what}: shape {got.shape} != {want.shape}"
    both_nan = np.isnan(got) & np.isnan(want)
    diff = np.abs(got - want)
    ok = both_nan | (diff <= ATOL) | (diff <= RTOL * np.abs(want))
    assert ok.all(), f"{what}: {int((~ok).sum())} rows differ, largest {np.nanmax(diff):.3g}"


@pytest.mark.parametrize("name", list(CASES))
def test_predictions_match_stata(name):
    ref = FROZEN[name]
    fit, df = estimate(name)
    keys, series = unpack(ref["keys"]), unpack(ref["series"])
    assert np.array_equal(df[["firm", "year"]].to_numpy(dtype=float), keys)
    for j, (kind, _) in enumerate(KINDS):
        close(fit.predict(kind, df).to_numpy(), series[:, j], f"predict {kind}")


@pytest.mark.parametrize("name", list(CASES))
def test_where_restricts_the_rows(name):
    ref = FROZEN[name]
    fit, df = estimate(name)
    got = fit.predict("residuals", df, where=CONDITION).to_numpy()
    close(got, unpack(ref["series"])[:, len(KINDS)], "predict residuals if")


def test_xb_plus_residuals_is_the_transformed_dependent_variable():
    fit, df = estimate("fod_td")
    total = fit.predict("xb", df) + fit.predict("residuals", df)
    placed = np.full(len(df), np.nan)
    placed[fit.data.source_row[fit.stack.row]] = fit.stack.dy
    close(total.to_numpy(), placed, "xb + residuals")


def test_unknown_kind_is_refused():
    fit, df = estimate("fd_jump")
    with pytest.raises(SpecificationError) as raised:
        fit.predict("fitted", df)
    assert raised.value.key == "predict_kind" and raised.value.stata_code == 198


def test_changed_keys_are_refused():
    fit, df = estimate("fd_jump")
    changed = df.assign(year=df["year"] + 1)
    with pytest.raises(DataError) as raised:
        fit.predict("residuals", changed)
    assert raised.value.key == "predict_data_changed" and raised.value.stata_code == 459
    # the regime needs only q
    assert fit.predict("regime", changed).notna().any()
