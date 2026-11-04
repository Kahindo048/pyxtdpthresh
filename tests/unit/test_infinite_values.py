"""An infinite value is missing, as in Stata, and the user is told."""

import warnings

import numpy as np
import pytest

import pyxtdpthresh as pyx
from pyxtdpthresh._errors import PyxdpthreshWarning


def estimate(df):
    return pyx.xtdpthresh(
        df, "y", q="q", endogenous=["e1"], x=["x1"], maxlag=(2, 4), collapse=True, id="id",
        time="t", bootstrap=False,
    )  # fmt: skip


@pytest.fixture
def panel():
    return pyx.simulate_panel("gong_seo", n=150, t=6, seed=4).assign(
        x1=lambda d: np.sin(d["id"] + d["t"]), e1=lambda d: np.cos(d["id"] * d["t"])
    )


def test_an_infinite_value_is_treated_as_missing_with_a_warning(panel):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", PyxdpthreshWarning)
        as_nan = estimate(panel.assign(y=panel["y"].where(panel.index != 7, np.nan)))
    bad = panel.assign(y=panel["y"].where(panel.index != 7, np.inf))
    with pytest.warns(PyxdpthreshWarning, match=r"1 infinite value\(s\) in y"):
        as_inf = estimate(bad)
    assert as_inf.gamma == as_nan.gamma
    assert list(as_inf.fit.search.fit.theta) == list(as_nan.fit.search.fit.theta)


def test_the_warning_is_also_in_french_and_names_the_column(panel):
    bad = panel.assign(x1=panel["x1"].where(panel.index != 3, -np.inf))
    with pyx.option_context(lang="fr"), pytest.warns(PyxdpthreshWarning, match="infinie.*x1"):
        estimate(bad)


def test_a_clean_panel_raises_no_warning_about_infinity(panel):
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", PyxdpthreshWarning)
        estimate(panel)
    assert not [w for w in caught if "infini" in str(w.message)]
