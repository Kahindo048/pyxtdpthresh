"""Instrument construction and cleaning on small hand-checkable panels."""

import math

import numpy as np
import pytest

from pyxtdpthresh._errors import DataError
from pyxtdpthresh.core.calendar import row_at_shift
from pyxtdpthresh.instruments.builder import (
    ENDOGENOUS,
    EXOGENOUS,
    LAG_Y,
    PREDETERMINED,
    InstrumentSettings,
    build_fd_instruments,
    make_layout,
)
from pyxtdpthresh.instruments.cleaning import (
    clean_instruments,
    dependent_columns,
    drop_cell_constant,
    duplicate_columns,
)
from pyxtdpthresh.kernels.cleaning import independent_columns
from pyxtdpthresh.kernels.reference import cleaning as ref_cleaning


def two_units(t=4):
    """Two complete units of ``t`` periods; unit 0 has y = 10, 20, ... and unit 1 y = 100, 200..."""
    offsets = np.array([0, t, 2 * t], dtype=np.int64)
    time = np.tile(np.arange(1, t + 1), 2).astype(np.int64)
    y = np.concatenate([10.0 * np.arange(1, t + 1), 100.0 * np.arange(1, t + 1)])
    return offsets, time, y


def build(offsets, time, y, x, var_type, inst=None, eq=None, **settings):
    n = time.size
    eq = np.ones(n, bool) if eq is None else eq
    prev = row_at_shift(offsets, time, 1)
    rows = np.flatnonzero((prev >= 0) & eq)
    d = x[rows] - x[prev[rows]]
    return build_fd_instruments(
        offsets=offsets, time=time, eq=eq, y=y, x=x, var_type=np.array(var_type, dtype=np.int64),
        inst=np.zeros((n, 0)) if inst is None else inst, eq_row=rows, eq_time=time[rows],
        d_exog=d[:, np.array(var_type) == EXOGENOUS], settings=InstrumentSettings(**settings),
    )  # fmt: skip


def test_row_at_shift_uses_calendar_and_never_crosses_units():
    offsets = np.array([0, 3, 5], dtype=np.int64)
    time = np.array([1, 2, 4, 3, 4], dtype=np.int64)
    np.testing.assert_array_equal(row_at_shift(offsets, time, 2), [-1, -1, 1, -1, -1])
    np.testing.assert_array_equal(row_at_shift(offsets, time, -1), [1, -1, -1, 4, -1])
    np.testing.assert_array_equal(row_at_shift(offsets, time, 1, np.array([4])), [3])


def test_layout_widths_follow_the_minimum_lags():
    base = dict(n_blocks=3, span=3, k_exog=1, k_endog=0, k_predet=0, k_inst=0)
    full = make_layout(InstrumentSettings(), **base)
    assert (full.lag_lo_y, full.lag_lo_p, full.n_lag_y, full.n_lag_p) == (2, 1, 2, 3)
    assert full.block_width == 1 + 2 + 1 and full.n_cols == 12
    collapsed = make_layout(InstrumentSettings(collapse=True), **base)
    assert collapsed.n_cols == 4
    static = make_layout(InstrumentSettings(static=True), **base)
    assert static.block_width == 2
    capped = make_layout(InstrumentSettings(lag_lo=3, lag_hi=3), **base)
    assert (capped.n_lag_y, capped.n_lag_p) == (1, 1)
    empty = make_layout(InstrumentSettings(lag_lo=5), **base)
    assert (empty.n_lag_y, empty.n_lag_p) == (0, 0)


def test_default_instruments_of_a_dynamic_model_with_one_exogenous_regressor():
    offsets, time, y = two_units()
    x = np.column_stack([np.zeros(8), np.arange(8.0) ** 2])  # L.y placeholder and exogenous
    raw = build(offsets, time, y, x, [LAG_Y, EXOGENOUS])
    # equations at t = 2, 3, 4 of both units; blocks of width 4: const, y_{t-2}, y_{t-3}, dx
    assert raw.z.shape == (6, 12) and raw.keep.all()
    first = raw.z[0]  # unit 0, t = 2: no y lag exists; constant and dx only
    np.testing.assert_array_equal(first[:4], [1.0, 0.0, 0.0, 1.0])
    second = raw.z[1]  # unit 0, t = 3: y_1 = 10 at lag 2, block 1
    np.testing.assert_array_equal(second[4:8], [1.0, 10.0, 0.0, 3.0])
    third = raw.z[2]  # unit 0, t = 4: y_2 = 20, y_1 = 10 in block 2
    np.testing.assert_array_equal(third[8:], [1.0, 20.0, 10.0, 5.0])
    assert np.count_nonzero(raw.z[2, :8]) == 0
    np.testing.assert_array_equal(raw.col_block, np.repeat([0, 1, 2], 4))


def test_collapse_shares_one_block_and_iv_collapse_only_the_external_columns():
    offsets, time, y = two_units()
    x = np.column_stack([np.zeros(8), np.arange(8.0) ** 2])
    inst = np.arange(1.0, 9.0)[:, None]
    shared = build(
        offsets, time, y, x, [LAG_Y, EXOGENOUS], inst=inst, collapse=True, iv_collapse=True
    )
    assert shared.z.shape == (6, 4 + 1)
    np.testing.assert_array_equal(shared.z[2, :4], [1.0, 20.0, 10.0, 5.0])
    assert shared.z[2, 4] == inst[3, 0]  # external instrument dated t, row 3 of the panel
    own = build(offsets, time, y, x, [LAG_Y, EXOGENOUS], inst=inst, iv_collapse=False)
    assert own.z.shape == (6, 12 + 3)
    assert own.z[2, 12 + 2] == inst[3, 0]  # third period block of the external instrument


def test_endogenous_and_predetermined_variables_start_at_their_minimum_lag():
    offsets, time, y = two_units(5)
    x = np.column_stack([np.zeros(10), np.arange(10.0) + 1, np.arange(10.0) + 101])
    raw = build(offsets, time, y, x, [LAG_Y, ENDOGENOUS, PREDETERMINED], static=False)
    layout = raw.layout
    assert (
        layout.block_width == 1 + 3 + 1 * 3 + 1 * 4
    )  # const, y lags 2..4, endog 2..4, predet 1..4
    # unit 0 at t = 5: endogenous lags 2..4 are x[2,1], x[1,1], x[0,1] -> 3, 2, 1
    row = raw.z[np.flatnonzero(raw.keep)[3]]
    block = row[3 * layout.block_width : 4 * layout.block_width]
    np.testing.assert_array_equal(block[4:7], [3.0, 2.0, 1.0])
    np.testing.assert_array_equal(block[7:], [104.0, 103.0, 102.0, 101.0])


def test_equation_without_any_instrument_is_dropped_and_the_constant_alone_does_not_count():
    offsets, time, y = two_units(3)
    x = np.zeros((6, 1))
    raw = build(offsets, time, y, x, [LAG_Y])  # no exogenous regressor: only y lags
    # t = 2 has no lag-2 observation; only t = 3 has one
    assert raw.keep.tolist() == [False, True, False, True]
    assert (raw.z[:, :].sum(axis=1) > 0).all()


def test_history_rows_are_instrument_sources_but_not_equations():
    offsets, time, y = two_units(4)
    eq = np.array([False, False, True, True, False, False, True, True])
    x = np.zeros((8, 1))
    raw = build(offsets, time, y, x, [LAG_Y], eq=eq)
    # equations t = 3 and t = 4; the first uses the history level y_1 = 10 as lag-2 instrument
    assert raw.keep.all() and raw.layout.n_blocks == 2
    np.testing.assert_array_equal(raw.z[0, :3], [1.0, 10.0, 0.0])
    np.testing.assert_array_equal(raw.z[1, 3:], [1.0, 20.0, 10.0])


def test_projected_allocation_gate():
    offsets, time, y = two_units()
    x = np.zeros((8, 1))
    big = np.ones((8, 5001))
    with pytest.raises(DataError) as raised:
        build(offsets, time, y, x, [LAG_Y], inst=big, collapse=False)
    assert raised.value.key == "xd_iv_alloc" and raised.value.stata_code == 498


# ----------------------------------------------------------------------------- cleaning
def test_columns_that_are_multiples_of_the_period_constants_are_zeroed():
    times = np.repeat([1, 2, 3], 4)
    unit = np.tile(np.arange(4), 3)
    const = np.zeros((12, 3))
    const[times == 1, 0] = 1.0  # indicator of period 1
    const[times == 2, 1] = 1.0  # indicator of period 2
    macro = np.where(times == 1, 5.0, 0.0)  # a common value in period 1 only: 5 * indicator(1)
    z = np.column_stack([const[:, 0], const[:, 1], macro, unit.astype(float)])
    out, dropped = drop_cell_constant(z, times)
    assert dropped == 1
    assert not out[:, 2].any() and out[:, 3].any() and out[:, 0].any()


def test_a_column_nonzero_in_a_singleton_period_is_never_dropped():
    times = np.array([1, 1, 2])
    z = np.array([[1.0, 1.0], [1.0, 1.0], [0.0, 3.0]])
    out, dropped = drop_cell_constant(z, times)
    assert dropped == 0 and np.array_equal(out, z)


def test_all_ones_direction_spans_a_common_trend_after_the_constants():
    times = np.repeat([1, 2], 3)
    ones = np.ones(6)
    z = np.column_stack([ones, 7.0 * ones])  # collapsed constant and a constant multiple
    out, dropped = drop_cell_constant(z, times)
    assert dropped == 1 and not out[:, 1].any()


def test_exact_duplicates_keep_the_first_occurrence_and_unequal_columns_stay():
    rng = np.random.default_rng(1)
    a, b = rng.normal(size=(2, 30))
    z = np.column_stack([a, b, a, b + 1e-12, a, b])
    np.testing.assert_array_equal(duplicate_columns(z), [True, True, False, True, False, False])


def test_dependent_columns_are_dropped_in_column_order():
    rng = np.random.default_rng(2)
    a, b = rng.normal(size=(2, 40))
    z = np.column_stack([a, b, a + 2.0 * b, rng.normal(size=40)])
    np.testing.assert_array_equal(dependent_columns(z), [True, True, False, True])
    independent = rng.normal(size=(40, 5))
    assert dependent_columns(independent).all()


def test_clean_instruments_counts_each_removal_and_reports_the_residual_of_dependent_columns():
    rng = np.random.default_rng(3)
    a, b = rng.normal(size=(2, 40))
    times = np.repeat([1, 2, 3, 4], 10)
    z = np.column_stack([a, np.zeros(40), b, a, a - b, rng.normal(size=40)])
    cleaned = clean_instruments(z, times)
    assert (cleaned.n_zero, cleaned.n_duplicate, cleaned.n_dependent) == (1, 1, 1)
    np.testing.assert_array_equal(cleaned.columns, [0, 2, 5])
    assert cleaned.dep_near == 0 and cleaned.dep_res < 1e-10
    assert math.isnan(clean_instruments(z[:, [0, 2, 5]], times).dep_res)


def test_a_nearly_dependent_column_is_reported_as_near():
    rng = np.random.default_rng(4)
    a, b = rng.normal(size=(2, 400))
    z = np.column_stack([a, b, a + b + 1e-7 * rng.normal(size=400)])
    cleaned = clean_instruments(z, np.repeat([1, 2], 200))
    assert cleaned.n_dependent == 1 and cleaned.dep_near == 1


@pytest.mark.parametrize("seed", range(6))
def test_independence_kernel_equals_the_reference(seed):
    rng = np.random.default_rng(seed)
    base = rng.normal(size=(30, 6))
    z = np.column_stack([base, base[:, :3] @ rng.normal(size=(3, 4)), rng.normal(size=(30, 3))])
    gram = z.T @ z
    scale = np.sqrt(np.diag(gram))
    gram = gram / np.outer(scale, scale)
    np.testing.assert_array_equal(
        independent_columns(gram, 1e-13), ref_cleaning.independent_columns(gram, 1e-13)
    )
