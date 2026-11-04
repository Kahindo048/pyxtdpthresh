"""Error messages that name the variable, the row, the unit or the period at fault (I.6.4)."""

import numpy as np
import pandas as pd
import pytest

from pyxtdpthresh import _i18n
from pyxtdpthresh._errors import DataError
from pyxtdpthresh.data import checks
from pyxtdpthresh.data.checks import as_period_numbers, balance_summary, unknown_variable
from pyxtdpthresh.data.panel import build_panel
from pyxtdpthresh.models.xthenreg.design import prepare_data


def frame(n_units=4, n_times=5):
    ids = np.repeat(np.arange(1, n_units + 1) * 10, n_times)
    years = np.tile(np.arange(2000, 2000 + n_times), n_units)
    return pd.DataFrame(
        {
            "firm": ids, "year": years, "invest": np.arange(ids.size, dtype=float),
            "tobin_q": ids / 10.0, "debt": ids / 100.0,
        }
    )  # fmt: skip


# ----------------------------------------------------------------------- unknown variable
def test_a_misspelled_variable_gets_a_suggestion_and_the_columns_available():
    with pytest.raises(DataError) as caught:
        build_panel(frame(), ["tobin_Q"], id="firm", time="year")
    text = str(caught.value)
    assert "'tobin_Q'" in text and "Did you mean 'tobin_q'?" in text
    assert "Columns available: firm, year, invest, tobin_q, debt." in text
    assert caught.value.key == "variable_not_found"


def test_the_suggestion_ignores_the_case_and_offers_at_most_three_names():
    error = unknown_variable("DEBT", ["debt", "debts", "debtor", "debtors", "other"])
    text = str(error)
    assert "Did you mean" in text and text.count("'debt") <= 3 + 1  # the name itself is quoted
    assert "'debt'" in text.split("Did you mean")[1]


def test_no_suggestion_is_made_when_nothing_is_close():
    text = str(unknown_variable("zzzz", ["firm", "year"]))
    assert "Did you mean" not in text and "Columns available: firm, year." in text


def test_a_long_list_of_columns_is_cut():
    text = str(unknown_variable("nope", [f"c{i}" for i in range(25)]))
    assert "c9 ..." in text and "c10" not in text


def test_an_unknown_panel_key_names_the_columns_and_the_index_levels():
    indexed = frame().set_index("year")
    with pytest.raises(DataError) as caught:
        build_panel(indexed, ["invest"], id="firms", time="year")
    assert "Did you mean 'firm'?" in str(caught.value) and "year" in str(caught.value)


def test_the_message_is_in_french_when_asked():
    from pyxtdpthresh import _config

    _config.set_options(lang="fr")
    try:
        with pytest.raises(DataError) as caught:
            build_panel(frame(), ["tobin_Q"], id="firm", time="year")
    finally:
        _config.set_options(lang="en")
    text = str(caught.value)
    assert "introuvable" in text and "Vouliez-vous dire « tobin_q »" not in text
    assert "Vouliez-vous dire 'tobin_q' ?" in text and "Colonnes disponibles" in text


# ------------------------------------------------------------------------------ the time
def test_a_non_integer_period_is_named_with_its_row_and_unit():
    df = frame()
    df["year"] = df["year"].astype(float)
    df.loc[7, "year"] = 2001.5
    with pytest.raises(DataError) as caught:
        build_panel(df, ["invest"], id="firm", time="year")
    text = str(caught.value)
    assert "2001.5 at row 7 (firm 20)" in text and "'year'" in text
    assert caught.value.key == "time_not_integer"


def test_a_missing_or_infinite_period_is_named_too():
    values = np.array([2000.0, 2001.0, np.inf, 2003.0])
    with pytest.raises(DataError, match="inf at row 2 .firm 3."):
        as_period_numbers(values, "year", np.array([1, 2, 3, 4]), "firm")
    with pytest.raises(DataError, match="at row 2$|at row 2[^0-9(]"):
        as_period_numbers(values, "year")  # without the units only the row is known


def test_a_text_period_is_reported_with_its_first_value():
    with pytest.raises(DataError, match="'2000-01' at row 0"):
        as_period_numbers(np.array(["2000-01", "2000-02"], dtype=object), "date")


def test_the_french_time_message_has_the_row():
    text = _i18n.message(
        "time_not_integer", "fr", name="year", example=1.5, row=3, unit=" (firm 2)"
    )
    assert "à la ligne 3 (firm 2)" in text


# --------------------------------------------------------------------------- duplicates
def test_a_duplicate_names_the_identifier_and_the_period_as_they_are_in_the_data():
    df = pd.concat([frame(), frame().iloc[[7, 13]]])
    with pytest.raises(DataError) as caught:
        build_panel(df, ["invest"], id="firm", time="year")
    text = str(caught.value)
    assert "(firm=20, year=2002)" in text and "(firm=30, year=2003)" in text
    assert caught.value.stata_code == 451


def test_string_identifiers_are_named_as_they_are():
    df = frame().assign(
        firm=lambda d: d["firm"].map({10: "Acme", 20: "Bolt", 30: "Cog", 40: "Dyn"})
    )
    df = pd.concat([df, df.iloc[[7]]])
    with pytest.raises(DataError, match=r"\(firm=Bolt, year=2002\)"):
        build_panel(df, ["invest"], id="firm", time="year")


# ----------------------------------------------------------------------------- balance
def test_an_unbalanced_panel_names_the_first_incomplete_unit_and_its_missing_periods():
    df = frame().drop(index=[6, 7])  # unit 20 loses 2001 and 2002
    with pytest.raises(DataError) as caught:
        prepare_data(df, "invest", "debt", ["tobin_q"], (), id="firm", time="year")
    text = str(caught.value)
    assert "strongly balanced" in text and "1 of 4 unit(s)" in text
    assert "For example firm 20 is missing year (2001, 2002)." in text


def test_a_long_list_of_missing_periods_is_cut():
    df = frame(n_units=3, n_times=12)
    df = df[~((df["firm"] == 10) & (df["year"] > 2002))]  # unit 10 lacks 2003..2011
    summary = balance_summary(
        pd.factorize(df["firm"])[0], df["year"].to_numpy(), df["firm"].unique(), ("firm", "year")
    )
    assert "(2003, 2004, 2005, 2006, 2007, ...)" in summary.example


def test_a_balanced_panel_has_no_example_and_the_summary_keeps_its_counts():
    df = frame()
    summary = balance_summary(np.repeat(np.arange(4), 5), df["year"].to_numpy())
    assert summary.kind == "strongly balanced" and summary.example == ""
    assert (summary.n_units, summary.n_times, summary.n_incomplete) == (4, 5, 0)


def test_the_example_falls_back_on_the_unit_code_without_labels():
    df = frame().drop(index=[0])
    unit = np.repeat(np.arange(4), 5)[df.index.to_numpy()]
    summary = balance_summary(unit, df["year"].to_numpy())
    assert "unit 0 is missing time (2000)" in summary.example


def test_the_french_balance_example():
    text = _i18n.message("balance_example", "fr", id="firm", unit=20, time="year", periods="(2001)")
    assert text == "Par exemple firm 20 n'a pas year (2001)."


def test_the_old_entry_points_still_accept_the_old_arguments():
    unit = np.repeat(np.arange(4), 5)
    time = np.tile(np.arange(2000, 2005), 4)
    assert checks.classify_balance(unit, time) == "strongly balanced"
    checks.require_strongly_balanced(unit, time)
    checks.check_unique_pairs(unit, time, "firm", "year")  # no labels: the codes are shown
    with pytest.raises(DataError, match=r"\(firm=0, year=2000\)"):
        checks.check_unique_pairs(np.append(unit, 0), np.append(time, 2000), "firm", "year")
