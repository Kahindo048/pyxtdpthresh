"""Simulated panels of the Seo-Shin design estimated like Stata 17 (I.5 against the frozen run).

Three of the four panels are replications of the Monte Carlo experiment where the threshold
estimate is far from the truth (``gamma`` of 1.5 to 2.6 for a true 0): the criterion really has its
global minimum there, and Stata finds the same point.  The panels are frozen in
``simulated_panels.csv.gz`` so that the test does not depend on the generator.
"""

import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from validation.compare import ATOL, RTOL

from pyxtdpthresh._errors import PyxdpthreshWarning
from pyxtdpthresh.extras.simulation import DESIGNS
from pyxtdpthresh.models.xtdpthresh.fit import fit_point

pytestmark = pytest.mark.golden

HERE = Path(__file__).parent
FROZEN = json.loads((HERE / "simulated_golden.json").read_text(encoding="utf-8"))["cases"]
PANELS = pd.read_csv(HERE / "simulated_panels.csv.gz")


def fit(panel: str):
    frame = PANELS[PANELS["panel"] == int(panel)]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", PyxdpthreshWarning)
        return fit_point(
            frame, "y", id="id", time="t", bootstrap=False, **DESIGNS["seo_shin_jump"].arguments()
        )


@pytest.mark.parametrize("panel", list(FROZEN))
def test_the_threshold_criterion_and_slopes_equal_stata(panel):
    want, got = FROZEN[panel], fit(panel)
    np.testing.assert_allclose(got.search.fit.gamma, want["gamma"], atol=ATOL, rtol=RTOL)
    np.testing.assert_allclose(got.scalars["obj"], want["obj"], atol=ATOL, rtol=RTOL)
    np.testing.assert_allclose(got.search.fit.theta, want["b"], atol=ATOL, rtol=RTOL)
    assert got.scalars["N_iv"] == want["n_iv"]


def test_the_panels_are_balanced_and_the_frozen_threshold_is_far_from_the_truth():
    assert PANELS.groupby("panel").size().tolist() == [2000] * 4
    far = [abs(FROZEN[k]["gamma"] - DESIGNS["seo_shin_jump"].gamma) for k in ("1", "2", "3")]
    assert min(far) > 1.0  # the three panels the experiment flagged are real minima of J
