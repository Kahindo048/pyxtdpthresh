"""Reading ``xtset`` from a ``.dta`` (I.6.1): the files below were saved by Stata 17 MP.

``tests/unit/data`` is made by ``validation/stata/make_xtset_files.do`` from the first 30 firms of
Hansen's panel: ``xtset_firm_year`` (xtset firm year), ``xtset_renamed`` (other variable names),
``xtset_delta2`` (delta(2), odd years), ``tsset_only`` (tsset year, one firm) and ``xtset_none``
(saved without xtset).
"""

import struct
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from pyxtdpthresh._errors import PyxdpthreshWarning
from pyxtdpthresh.data import io
from pyxtdpthresh.data.io import XtsetInfo, _characteristics, _stata_delta, stata_xtset
from pyxtdpthresh.models.xtdpthresh.fit import fit_point

DATA = Path(__file__).parent / "data"


# ------------------------------------------------------------------------- the real files
def test_xtset_variables_and_delta_are_read_from_a_stata_file():
    assert stata_xtset(DATA / "xtset_firm_year.dta") == XtsetInfo("firm", "year", 1.0)
    assert stata_xtset(DATA / "xtset_renamed.dta") == XtsetInfo("company", "period", 1.0)
    assert stata_xtset(DATA / "xtset_delta2.dta") == XtsetInfo("firm", "year", 2.0)


def test_a_file_without_a_panel_variable_gives_no_panel():
    assert stata_xtset(DATA / "xtset_none.dta") == XtsetInfo()
    only_time = stata_xtset(DATA / "tsset_only.dta")
    assert only_time.panel is None and only_time.time == "year" and only_time.delta == 1.0


def test_from_stata_puts_the_panel_and_time_in_the_index():
    frame = io.from_stata(DATA / "xtset_firm_year.dta")
    assert frame.index.names == ["firm", "year"]
    assert frame.shape == (30 * 15, 4) and list(frame.columns) == [
        "invest", "tobin_q", "cashflow", "debt",
    ]  # fmt: skip
    assert frame.attrs["id"] == "firm" and frame.attrs["time"] == "year"
    assert frame.attrs["delta"] == 1.0
    renamed = io.from_stata(DATA / "xtset_renamed.dta")
    assert renamed.index.names == ["company", "period"]


def test_from_stata_keeps_the_columns_when_asked_and_records_the_names():
    frame = io.from_stata(DATA / "xtset_firm_year.dta", set_index=False)
    assert isinstance(frame.index, pd.RangeIndex) and {"firm", "year"} <= set(frame.columns)
    assert frame.attrs["id"] == "firm" and frame.attrs["time"] == "year"


def test_the_time_unit_of_a_delta_two_panel_is_recorded():
    frame = io.from_stata(DATA / "xtset_delta2.dta")
    assert frame.attrs["delta"] == 2.0
    assert sorted(frame.index.get_level_values("year").unique()) == list(range(1973, 1988, 2))


def test_names_are_never_guessed_from_the_columns():
    """The file has ``firm`` and ``year`` columns but no xtset: nothing is set."""
    frame = io.from_stata(DATA / "xtset_none.dta")
    assert isinstance(frame.index, pd.RangeIndex) and {"firm", "year"} <= set(frame.columns)
    assert frame.attrs["id"] is None and frame.attrs["time"] is None
    assert frame.attrs["delta"] is None
    lone = io.from_stata(DATA / "tsset_only.dta")  # a time variable alone is not a panel
    assert lone.attrs["id"] is None and isinstance(lone.index, pd.RangeIndex)


def test_a_file_written_by_pandas_is_read_without_xtset(tmp_path):
    frame = pd.DataFrame({"a": [1.0, 2.0], "firm": [1, 2]})
    frame.to_stata(tmp_path / "plain.dta", write_index=False)
    out = io.from_stata(tmp_path / "plain.dta")
    assert out.shape == (2, 2) and out.attrs["id"] is None


def test_the_estimator_takes_the_panel_from_the_index_of_a_stata_file():
    kwargs = {"bootstrap": False, "grid": 20, "collapse": True, "maxlag": (2, 5)}
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", PyxdpthreshWarning)
        framed = io.from_stata(DATA / "xtset_firm_year.dta")
        auto = fit_point(framed, "invest", ("cashflow",), q="debt", **kwargs)
        plain = io.from_stata(DATA / "xtset_none.dta")
        explicit = fit_point(
            plain, "invest", ("cashflow",), q="debt", id="firm", time="year", **kwargs
        )
    assert auto.search.fit.gamma == explicit.search.fit.gamma
    np.testing.assert_array_equal(auto.search.fit.theta, explicit.search.fit.theta)


# ---------------------------------------------------------------------- what Stata does not make
def entry(variable, name, text, width, order="<"):
    body = (
        variable.encode().ljust(width, b"\0") + name.encode().ljust(width, b"\0")
        + text.encode() + b"\0"
    )  # fmt: skip
    return b"<ch>" + struct.pack(f"{order}I", len(body)) + body + b"</ch>"


@pytest.mark.parametrize(("release", "width"), [(117, 33), (118, 129), (119, 129)])
@pytest.mark.parametrize("order", ["<", ">"])
def test_characteristics_are_parsed_in_each_release_and_byte_order(release, width, order):
    section = b"<characteristics>" + b"".join(
        [
            entry("_dta", "_TSpanel", "id", width, order),
            entry("x", "note1", "a note", width, order),
            entry("_dta", "_TStvar", "t", width, order),
        ]
    ) + b"</characteristics>"  # fmt: skip
    found = _characteristics(section, release, order)
    assert found[("_dta", "_TSpanel")] == "id" and found[("_dta", "_TStvar")] == "t"
    assert found[("x", "note1")] == "a note"


@pytest.mark.parametrize(
    ("text", "value"),
    [
        ("+1.0000000000000X+000", 1.0),
        ("+1.0000000000000X+001", 2.0),
        ("+1.0000000000000X-001", 0.5),
        ("+1.8000000000000X+002", 6.0),
        ("+1.0000000000000X+00a", 1024.0),
        ("-1.0000000000000X+000", -1.0),
    ],
)
def test_the_hexadecimal_time_unit_of_stata_is_decoded(text, value):
    assert _stata_delta(text) == value


def test_an_unreadable_time_unit_is_none():
    assert _stata_delta("one") is None and _stata_delta("") is None


def test_files_that_cannot_be_parsed_give_an_empty_result(tmp_path):
    (tmp_path / "junk.dta").write_bytes(b"not a stata file")
    (tmp_path / "old.dta").write_bytes(b"\x73\x01\x01\x00" + b"\0" * 200)  # a release 115 header
    for name in ("junk.dta", "old.dta", "missing.dta"):
        assert stata_xtset(tmp_path / name) == XtsetInfo()
    broken = b"<stata_dta><header><release>118</release><byteorder>LSF</byteorder></header><map>"
    (tmp_path / "short.dta").write_bytes(broken + b"\0" * 20)
    assert stata_xtset(tmp_path / "short.dta") == XtsetInfo()
