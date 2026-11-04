"""``augment`` (I.6.2): the series of ``predict`` as columns of the data, nothing else."""

import warnings

import numpy as np
import pandas as pd
import pytest
from test_search import simulate

from pyxtdpthresh._errors import PyxdpthreshWarning, SpecificationError
from pyxtdpthresh.extras.augment import DEFAULT_KINDS, augment
from pyxtdpthresh.models.xtdpthresh.fit import fit_point

OPTIONS = {"collapse": True, "grid": 25, "n_boot": 49, "seed": 3, "bootstrap": False}


@pytest.fixture(scope="module")
def frame():
    return simulate(n=120, t=7, seed=4)


@pytest.fixture(scope="module")
def fit(frame):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", PyxdpthreshWarning)
        return fit_point(frame, "y", ("x",), q="q", id="id", time="t", **OPTIONS)


def same(a, b):
    np.testing.assert_array_equal(np.asarray(a, float), np.asarray(b, float))


def test_each_column_is_the_predict_series_of_the_same_name(fit, frame):
    out = augment(fit, frame)
    assert list(out.columns) == [*frame.columns, *DEFAULT_KINDS]
    for kind in DEFAULT_KINDS:
        same(out[kind], fit.predict(kind, frame))
        assert out[kind].name == kind
    assert out.index.equals(frame.index) and len(out) == len(frame)


def test_the_original_columns_are_untouched_and_the_input_is_not_modified(fit, frame):
    before = frame.copy()
    out = augment(fit, frame)
    pd.testing.assert_frame_equal(frame, before)  # no column added in place
    pd.testing.assert_frame_equal(out[list(frame.columns)], frame)
    assert out is not frame


def test_the_regime_is_one_above_the_threshold_and_missing_for_a_missing_q(fit, frame):
    gamma = fit.search.fit.gamma
    out = augment(fit, frame, kinds=["regime"])
    same(out["regime"], (frame["q"] > gamma).astype(float))
    gappy = frame.copy()
    gappy.loc[5, "q"] = np.nan
    assert np.isnan(augment(fit, gappy, kinds=["regime"]).loc[5, "regime"])


def test_the_residuals_are_missing_where_no_equation_exists(fit, frame):
    out = augment(fit, frame, kinds=["residuals", "xb"])
    first_period = frame["t"] == frame["t"].min()
    assert out.loc[first_period, "residuals"].isna().all()  # first differences need a lag
    assert out["residuals"].notna().sum() == fit.scalars["N"]
    assert out["xb"].notna().sum() == fit.scalars["N"]


def test_the_ar_residuals_can_be_asked_for_and_the_order_follows_the_request(fit, frame):
    out = augment(fit, frame, kinds=("regime", "ar_residuals"))
    assert list(out.columns)[-2:] == ["regime", "ar_residuals"]
    same(out["ar_residuals"], fit.predict("ar_residuals", frame))


def test_a_single_name_is_accepted_as_a_list_of_one(fit, frame):
    assert list(augment(fit, frame, kinds="xb").columns)[-1:] == ["xb"]


def test_a_prefix_names_the_new_columns(fit, frame):
    out = augment(fit, frame, prefix="m1_")
    assert [c for c in out.columns if c not in frame.columns] == [
        "m1_residuals", "m1_xb", "m1_regime",
    ]  # fmt: skip
    twice = augment(fit, out, prefix="m2_")  # a second model next to the first
    assert {"m1_residuals", "m2_residuals"} <= set(twice.columns)


def test_an_existing_column_is_an_error_unless_it_is_to_be_replaced(fit, frame):
    once = augment(fit, frame)
    with pytest.raises(SpecificationError) as caught:
        augment(fit, once)
    assert caught.value.key == "augment_exists" and "residuals" in str(caught.value)
    replaced = augment(fit, once.assign(residuals=0.0), overwrite=True)
    same(replaced["residuals"], fit.predict("residuals", frame))
    assert list(replaced.columns).count("residuals") == 1


def test_a_nothing_is_added_when_a_name_is_wrong(fit, frame):
    with pytest.raises(SpecificationError) as caught:
        augment(fit, frame, kinds=["residuals", "fitted"])
    assert caught.value.key == "predict_kind" and "fitted" in str(caught.value)


def test_the_frame_must_be_the_one_the_model_was_estimated_on(fit, frame):
    from pyxtdpthresh._errors import DataError

    for shorter in (frame.iloc[:-30], frame.iloc[:5]):  # fewer rows than the fit used
        with pytest.raises(DataError) as caught:
            augment(fit, shorter, kinds=["residuals"])
        assert caught.value.key == "predict_data_changed" and caught.value.stata_code == 459
    reordered = frame.assign(t=frame["t"].iloc[::-1].to_numpy())  # same size, other periods
    with pytest.raises(DataError) as caught:
        augment(fit, reordered, kinds=["xb"])
    assert caught.value.key == "predict_data_changed"


def test_it_works_on_an_indexed_panel_and_keeps_the_index():
    data = simulate(n=100, t=7, seed=6).set_index(["id", "t"])
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", PyxdpthreshWarning)
        model = fit_point(data, "y", ("x",), q="q", **OPTIONS)
    out = augment(model, data)
    assert out.index.names == ["id", "t"] and out.index.equals(data.index)
    same(out["xb"], model.predict("xb", data))
