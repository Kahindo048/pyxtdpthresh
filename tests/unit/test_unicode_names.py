"""Variable names with accents work, as in Stata 14 and later (a French-speaking user's data)."""

import warnings

import pytest

import pyxtdpthresh as pyx
from pyxtdpthresh._errors import PyxdpthreshWarning

EXTREME = [137, 391, 407, 488, 538]
RENAMED = {"invest": "investé", "debt": "dette_é", "cashflow": "flux_é"}


def fit(df, y, q, endogenous, **options):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", PyxdpthreshWarning)
        return pyx.xtdpthresh(
            df, y, q=q, endogenous=endogenous, maxlag=(3, 8), collapse=True, id="firm",
            time="year", bootstrap=False, **options,
        )  # fmt: skip


def test_accented_names_give_the_estimate_stata_gives_and_the_same_as_plain_names():
    df = pyx.load_dataset("invest")
    plain = fit(df, "invest", "debt", ["cashflow", "tobin_q"])
    accented = fit(df.rename(columns=RENAMED), "investé", "dette_é", ["flux_é", "tobin_q"])
    # Stata 17 on the same model with these variable names: e(gamma) = 0.10989855, rc = 0
    assert accented.gamma == pytest.approx(0.10989855, abs=5e-5)
    assert accented.gamma == plain.gamma
    assert list(accented.fit.search.fit.theta) == list(plain.fit.search.fit.theta)
    assert "flux_é" in " ".join(accented.names)


def test_operators_apply_to_accented_names():
    df = pyx.load_dataset("invest").rename(columns=RENAMED)
    res = fit(df, "investé", "dette_é", ["tobin_q"], x=["L.flux_é"])
    assert any(name.endswith("L.flux_é") for name in res.names)


def test_a_name_with_a_space_is_still_refused():
    df = pyx.load_dataset("invest").rename(columns={"invest": "investissement é"})
    with pytest.raises(pyx.SpecificationError):
        fit(df, "investissement é", "debt", ["cashflow"])
