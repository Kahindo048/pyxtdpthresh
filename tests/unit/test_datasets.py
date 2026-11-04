"""Bundled datasets (I.6.3): the file is Hansen's panel exactly as Stata holds it."""

import warnings
from importlib import resources

import numpy as np
import pandas as pd
import pytest

from pyxtdpthresh._errors import PyxdpthreshWarning, SpecificationError
from pyxtdpthresh.extras.datasets import DATASETS, list_datasets, load_dataset
from pyxtdpthresh.models.xtdpthresh.fit import fit_point

DTA = "validation/data/invest.dta"


def test_the_panel_has_the_shape_of_hansens_data():
    frame = load_dataset("invest")
    assert frame.shape == (565 * 15, 6)
    assert list(frame.columns) == ["firm", "year", "invest", "tobin_q", "cashflow", "debt"]
    assert frame["firm"].nunique() == 565 and sorted(frame["year"].unique()) == list(
        range(1973, 1988)
    )
    assert frame.groupby("firm").size().eq(15).all()  # balanced
    assert not frame.isna().any().any()


def test_the_values_equal_the_stata_file_exactly():
    stata = pd.read_stata(DTA, convert_categoricals=False)
    frame = load_dataset()  # the default is invest
    for column in ("invest", "tobin_q", "cashflow", "debt"):
        np.testing.assert_array_equal(frame[column].to_numpy(), stata[column].to_numpy())
    np.testing.assert_array_equal(frame["firm"].to_numpy(), stata["firm"].to_numpy())
    np.testing.assert_array_equal(frame["year"].to_numpy(), stata["year"].to_numpy())


def test_the_variable_labels_are_those_of_the_stata_file():
    labels = pd.io.stata.StataReader(DTA).variable_labels()
    assert load_dataset().attrs["variable_labels"] == labels
    assert load_dataset().attrs["id"] == "firm" and load_dataset().attrs["time"] == "year"
    assert "565 firms" in load_dataset().attrs["description"]


def test_the_dataset_is_listed_and_documented():
    assert set(list_datasets()) == set(DATASETS) == {"invest"}
    assert "Hansen (1999" in list_datasets()["invest"]


def test_the_attributes_are_not_shared_between_loads():
    first = load_dataset()
    first.attrs["variable_labels"]["debt"] = "changed"
    assert load_dataset().attrs["variable_labels"]["debt"].startswith("Long-term debt")


def test_an_unknown_dataset_is_refused_with_its_key_in_both_languages():
    with pytest.raises(SpecificationError) as caught:
        load_dataset("nope")
    assert caught.value.key == "dataset_unknown" and "invest" in str(caught.value)
    from pyxtdpthresh._i18n import message

    assert "inconnu" in message("dataset_unknown", name="x", options="invest", lang="fr")


def test_the_file_is_inside_the_package_data():
    file = resources.files("pyxtdpthresh.extras.datasets").joinpath("invest.csv")
    assert file.is_file() and file.stat().st_size > 100_000  # type: ignore[attr-defined]


def test_the_bundled_panel_is_ready_for_the_estimator():
    frame = load_dataset()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", PyxdpthreshWarning)
        fit = fit_point(
            frame, "invest", ("cashflow",), q="debt", id=frame.attrs["id"],
            time=frame.attrs["time"], bootstrap=False, grid=30, collapse=True, maxlag=(2, 5),
        )  # fmt: skip
    assert fit.scalars["N_units"] == 565 and np.isfinite(fit.search.fit.gamma)
