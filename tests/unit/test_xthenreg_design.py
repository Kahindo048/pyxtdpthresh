"""Hand-checkable tests of the xthenreg sample and instrument construction."""

import numpy as np
import pandas as pd
import pytest

from pyxtdpthresh._errors import DataError, PyxdpthreshWarning, SpecificationError
from pyxtdpthresh.models.xthenreg.design import (
    build_instruments,
    moment_matrix,
    prepare_data,
)


def panel_frame(n=3, t=5, seed=0):
    rng = np.random.default_rng(seed)
    firm = np.repeat(np.arange(1, n + 1), t)
    year = np.tile(np.arange(2000, 2000 + t), n)
    return pd.DataFrame(
        {
            "firm": firm,
            "year": year,
            "y": rng.standard_normal(n * t),
            "q": rng.standard_normal(n * t),
            "x": rng.standard_normal(n * t),
            "e": rng.standard_normal(n * t),
            "z": rng.standard_normal(n * t),
        }
    )


def test_prepare_data_shapes_and_lag_block():
    df = panel_frame()
    d = prepare_data(df, "y", "q", ["x"], ["e"], id="firm", time="year")
    assert (d.n_units, d.n_periods, d.k_1, d.k_inst) == (3, 5, 3, 0)
    assert d.names == ("x", "e") and (d.n_plain, d.n_endo, d.n_exo) == (1, 1, 0)
    np.testing.assert_array_equal(d.x[0][:, 1:], d.y[:, :-1])
    assert np.isnan(d.x[0][:, 0]).all()
    np.testing.assert_array_equal(d.y[1], df["y"].to_numpy()[5:10])


def test_moment_counts_follow_the_stata_matrix():
    # T = 5, k_1 = 3 (lag y, x, e), e endogenous: rows t = 2..5
    m = moment_matrix(5, 3, n_endo=1, n_exo=0)
    assert m.tolist() == [[1, 0, 1, 0], [1, 1, 1, 1], [1, 2, 1, 2], [1, 3, 1, 3]]
    # exogenous gets two more lags, external instruments one column each
    m2 = moment_matrix(5, 3, n_endo=0, n_exo=1, k_inst=2)
    assert m2[:, 3].tolist() == [2, 3, 4, 5] and m2[:, 4:].tolist() == [[1, 1]] * 4


def test_dynamic_instruments_by_hand():
    df = panel_frame(t=4)
    d = prepare_data(df, "y", "q", ["x"], id="firm", time="year")
    inst = build_instruments(d)
    # equations t = 3, 4: [1, y_1, dx_3] and [1, y_1, y_2, dx_4]
    assert inst.block_sizes.tolist() == [3, 4] and inst.n_moments == 7
    assert inst.equation_index.tolist() == [2, 3]
    z = inst.literal()
    x, y = d.x[1], d.y
    np.testing.assert_allclose(
        z[:, 0], [1, y[0, 0], x[0, 2] - x[0, 1], 1, y[0, 0], y[0, 1], x[0, 3] - x[0, 2]]
    )
    assert inst.z.shape == (3 * 2, 7)
    assert inst.unit_ptr.tolist() == [0, 2, 4, 6]


def test_static_endogenous_and_exogenous_levels_and_external_instruments():
    df = panel_frame(t=4)
    d = prepare_data(df, "y", "q", [], ["e"], ["x"], ["z"], id="firm", time="year")
    inst = build_instruments(d, static=True)
    # equations t = 2, 3, 4; e endogenous: e_1..e_{t-2}; x exogenous: x_1..x_t; plus z_t
    assert inst.block_sizes.tolist() == [1 + 0 + 2 + 1, 1 + 1 + 3 + 1, 1 + 2 + 4 + 1]
    z0 = inst.literal()[:, 0]
    e, x, zz = d.x[1][0], d.x[2][0], d.inst[0][0]
    np.testing.assert_allclose(z0[:4], [1, x[0], x[1], zz[1]])  # t=2: no e level, x_1..x_2, z_2
    np.testing.assert_allclose(z0[4:9], [1, e[0], x[0], x[1], x[2]])  # first five of the t=3 block
    assert z0[9] == zz[2]


def test_columns_of_a_block_are_contiguous_and_the_rest_is_zero():
    d = prepare_data(panel_frame(t=5), "y", "q", ["x"], id="firm", time="year")
    inst = build_instruments(d)
    dense = inst.z.toarray()
    starts, sizes = inst.block_starts, inst.block_sizes
    for p in range(inst.n_equations):
        rows = dense[np.arange(d.n_units) * inst.n_equations + p]
        outside = np.ones(inst.n_moments, bool)
        outside[starts[p] : starts[p] + sizes[p]] = False
        assert not rows[:, outside].any()


def test_units_not_observed_in_every_period_are_dropped():
    df = panel_frame(n=4, t=5)
    df.loc[(df["firm"] == 2) & (df["year"] == 2003), "x"] = np.nan  # unit 2 loses a row
    d = prepare_data(df, "y", "q", ["x"], id="firm", time="year")
    assert d.n_units == 3 and d.n_units_ignored == 1 and d.n_periods == 5
    assert d.unit_labels.tolist() == [1, 3, 4]


def test_where_clause_changes_the_periods():
    d = prepare_data(
        panel_frame(t=6), "y", "q", ["x"], id="firm", time="year", where="year >= 2002"
    )
    assert d.n_periods == 4 and d.times.tolist() == [2002, 2003, 2004, 2005]


def test_errors():
    df = panel_frame()
    unbalanced = df.drop(index=[3])
    with pytest.raises(DataError, match="strongly balanced"):
        prepare_data(unbalanced, "y", "q", ["x"], id="firm", time="year")
    bad = df.copy()
    bad.loc[2, "e"] = np.nan  # a variable outside the sample selection
    with pytest.raises(DataError, match="'e'|e\\b"):
        prepare_data(bad, "y", "q", ["x"], ["e"], id="firm", time="year")
    short = prepare_data(panel_frame(t=2), "y", "q", ["x"], id="firm", time="year")
    with pytest.raises(SpecificationError):
        build_instruments(short)
    build_instruments(short, static=True)  # two periods are enough for the static model
    with pytest.raises(DataError, match="No usable"):
        prepare_data(df, "y", "q", ["x"], id="firm", time="year", where="year > 3000")


def test_non_consecutive_periods_warn():
    df = panel_frame(t=5)
    df = df[df["year"] != 2002]
    with pytest.warns(PyxdpthreshWarning, match="consecutive"):
        prepare_data(df, "y", "q", ["x"], id="firm", time="year")
