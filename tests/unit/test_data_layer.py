"""Tests of the data layer: keys, balance, lags, selection, reading."""

import numpy as np
import pandas as pd
import pytest

from pyxtdpthresh._errors import DataError
from pyxtdpthresh.data import checks, io, sampling
from pyxtdpthresh.data.panel import build_panel


def long_frame(n_units=4, n_times=5):
    ids = np.repeat(np.arange(1, n_units + 1) * 10, n_times)
    years = np.tile(np.arange(2000, 2000 + n_times), n_units)
    return pd.DataFrame(
        {"firm": ids, "year": years, "y": np.arange(ids.size, dtype=float), "x": ids / 10.0}
    )


# ----------------------------------------------------------------- checks
def test_balance_classification():
    df = long_frame()
    unit, t = np.repeat(np.arange(4), 5), df["year"].to_numpy()
    assert checks.classify_balance(unit, t) == "strongly balanced"
    weak_t = t.copy()
    weak_t[:5] += 1  # same count per unit, different periods
    assert checks.classify_balance(unit, weak_t) == "weakly balanced"
    keep = np.ones(20, bool)
    keep[3] = False
    assert checks.classify_balance(unit[keep], t[keep]) == "unbalanced"


def test_require_strongly_balanced_message_names_the_counts():
    df = long_frame().drop(index=[3, 4])
    p = build_panel(df, ["y"], id="firm", time="year")
    assert p.balance == "unbalanced"
    with pytest.raises(DataError, match="1 of 4"):
        checks.require_strongly_balanced(p.unit_of_row, p.time)


def test_period_numbers():
    assert checks.as_period_numbers(np.array([2000.0, 2001.0]), "year").tolist() == [2000, 2001]
    with pytest.raises(DataError, match="year"):
        checks.as_period_numbers(np.array([2000.5]), "year")
    with pytest.raises(DataError):
        checks.as_period_numbers(np.array(["2000-01-01"], dtype="datetime64[D]"), "date")


# ------------------------------------------------------------ build_panel
def test_build_panel_sorts_and_indexes_units():
    df = long_frame().sample(frac=1.0, random_state=0).reset_index(drop=True)
    p = build_panel(df, ["y", "x"], id="firm", time="year")
    assert p.n_units == 4 and p.n_rows == 20 and p.balance == "strongly balanced"
    assert p.offsets.tolist() == [0, 5, 10, 15, 20]
    assert p.unit_labels.tolist() == [10, 20, 30, 40]
    assert np.all(np.diff(p.time[:5]) == 1)
    # source_row maps back to the shuffled input
    np.testing.assert_array_equal(df["y"].to_numpy()[p.source_row], p.column("y"))


def test_build_panel_keys_from_multiindex():
    df = long_frame().set_index(["firm", "year"])
    p = build_panel(df, ["y"])
    assert p.id_name == "firm" and p.time_name == "year" and p.n_units == 4
    with pytest.raises(DataError):
        build_panel(long_frame().set_index("firm"), ["y"])


def test_duplicates_are_reported_with_examples():
    df = pd.concat([long_frame(), long_frame().iloc[[7]]])
    # the second unit has the identifier 20: the message names it, not its internal code 1
    with pytest.raises(DataError, match=r"\(firm=20, year=2002\)") as err:
        build_panel(df, ["y"], id="firm", time="year")
    assert err.value.stata_code == 451


def test_missing_keys_and_unknown_or_text_columns():
    df = long_frame().astype({"firm": float})
    df.loc[2, "firm"] = np.nan
    with pytest.raises(DataError, match="firm"):
        build_panel(df, ["y"], id="firm", time="year")
    with pytest.raises(DataError, match="'nope'"):
        build_panel(long_frame(), ["nope"], id="firm", time="year")
    text = long_frame().assign(s="a")
    with pytest.raises(DataError, match="'s'"):
        build_panel(text, ["s"], id="firm", time="year")


def test_string_ids_and_nullable_dtypes():
    df = long_frame().assign(firm=lambda d: "f" + d["firm"].astype(str))
    df["y"] = df["y"].astype("Float64")
    df.loc[0, "y"] = pd.NA
    p = build_panel(df, ["y"], id="firm", time="year")
    assert p.unit_labels.tolist() == ["f10", "f20", "f30", "f40"]
    assert np.isnan(p.column("y")[0])


def test_arrays_are_read_only():
    p = build_panel(long_frame(), ["y"], id="firm", time="year")
    with pytest.raises(ValueError):
        p.values[0, 0] = 1.0


# ---------------------------------------------------------- lag and select
def test_lag_looks_up_the_period_not_the_previous_row():
    df = long_frame().drop(index=[2])  # firm 10 has no 2002: years 2000, 2001, 2003, 2004
    p = build_panel(df, ["y"], id="firm", time="year")
    y = p.column("y")
    l1, l2 = p.lag(y, 1), p.lag(y, 2)
    assert np.isnan(l1[:4]).tolist() == [True, False, True, False]
    assert l1[1] == y[0] and l1[3] == y[2]  # 2004 looks at 2003
    assert np.isnan(l2[:4]).tolist() == [True, True, False, True]
    assert l2[2] == y[1]  # 2003 looks at 2001, skipping the gap


def test_lag_across_units_never_leaks():
    p = build_panel(long_frame(), ["y"], id="firm", time="year")
    lag = p.lag(p.column("y"), 1)
    assert np.isnan(lag[p.offsets[:-1]]).all()  # first period of every unit is missing


def test_select_drops_empty_units_and_keeps_offsets_consistent():
    p = build_panel(long_frame(), ["y"], id="firm", time="year")
    mask = np.ones(p.n_rows, bool)
    mask[5:10] = False  # whole unit 20
    mask[0] = False
    q = p.select(mask)
    assert q.unit_labels.tolist() == [10, 30, 40] and q.offsets.tolist() == [0, 4, 9, 14]
    assert q.n_rows == 14 and q.source_row[0] == 1


def test_with_columns_appends_derived_variable():
    p = build_panel(long_frame(), ["y"], id="firm", time="year")
    q = p.with_columns({"ly": p.lag(p.column("y"))})
    assert q.names == ("y", "ly") and np.isnan(q.column("ly")[0])


# --------------------------------------------------------------- sampling
def test_where_accepts_mask_series_and_expression():
    df = long_frame()
    for where in (df["year"] > 2002, (df["year"] > 2002).to_numpy(), "year > 2002"):
        p = build_panel(df, ["y"], id="firm", time="year", where=where)
        assert p.n_rows == 8 and p.time.min() == 2003
    assert p.balance == "strongly balanced"  # balance is judged on all rows, like xtset


def test_where_errors():
    df = long_frame()
    with pytest.raises(DataError):
        build_panel(df, ["y"], id="firm", time="year", where=np.arange(20))
    with pytest.raises(DataError, match="No usable"):
        build_panel(df, ["y"], id="firm", time="year", where="year > 3000")


def test_complete_rows():
    a = np.array([[1.0, 2.0], [np.nan, 1.0], [3.0, np.inf]])
    assert sampling.complete_rows(a).tolist() == [True, False, False]
    assert sampling.complete_rows(np.array([1.0, np.nan])).tolist() == [True, False]


# --------------------------------------------------------------------- io
def test_read_table_formats(tmp_path):
    df = long_frame()
    df.to_csv(tmp_path / "d.csv", index=False)
    df.to_stata(tmp_path / "d.dta", write_index=False)
    for name in ("d.csv", "d.dta"):
        out = io.read_table(tmp_path / name)
        assert list(out.columns) == list(df.columns) and len(out) == len(df)
    assert io.from_stata(tmp_path / "d.dta").shape == df.shape
    with pytest.raises(DataError, match=".xlsx"):
        io.read_table(tmp_path / "d.xlsx")
