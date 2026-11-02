"""Tests of core.linalg: Mata semantics measured on Stata 17 and general properties."""

import numpy as np
import pytest

from pyxtdpthresh.core import linalg


def spd(n, seed=0, cond=10.0):
    """Random symmetric positive definite matrix with the given condition number."""
    rng = np.random.default_rng(seed)
    q, _ = np.linalg.qr(rng.standard_normal((n, n)))
    eig = np.geomspace(1.0, 1.0 / cond, n)
    return (q * eig) @ q.T


# ------------------------------------------------------------------- invsym
@pytest.mark.parametrize("n", [1, 2, 5, 12])
def test_invsym_equals_inverse_for_spd(n):
    a = spd(n, seed=n)
    np.testing.assert_allclose(linalg.invsym(a), np.linalg.inv(a), rtol=1e-10, atol=1e-12)


def test_invsym_reads_upper_triangle_and_cholinv_the_lower():
    a = spd(4)
    b = a.copy()
    b[3, 0] += 5.0  # lower triangle only
    np.testing.assert_allclose(linalg.invsym(b), linalg.invsym(a), atol=1e-12)
    c = a.copy()
    c[0, 3] += 5.0  # upper triangle only
    np.testing.assert_allclose(linalg.cholinv(c), linalg.cholinv(a), atol=1e-12)


def test_sweep_pivots_on_largest_diagonal_so_dropped_variable_is_not_always_last():
    # x2 = x0 - 2 x1: with the natural order variable 3 would be dropped; Stata drops 1
    x = np.random.default_rng(13).standard_normal((40, 3))
    x = np.column_stack([x, x[:, 0] - 2.0 * x[:, 1]])
    g = x.T @ x
    inv = linalg.invsym(g)
    dropped = [k for k in range(4) if inv[k, k] == 0.0]
    assert dropped == [1]  # same matrix as the Stata case la_gram_sing


# values below were produced by Mata's invsym() on Stata 17 MP (t_invsym_indef.do)
@pytest.mark.parametrize(
    ("a", "expected"),
    [
        ([[1.0, 0.0], [0.0, -1.0]], [[1.0, 0.0], [0.0, 0.0]]),
        ([[1.0, 2.0], [2.0, 1.0]], [[1.0, 0.0], [0.0, 0.0]]),
        ([[-1.0]], [[0.0]]),
        ([[0.0, 1.0], [1.0, 0.0]], [[0.0, 0.0], [0.0, 0.0]]),
        ([[-2.0, 1.0], [1.0, -2.0]], [[0.0, 0.0], [0.0, 0.0]]),
        ([[1.0, 1.0], [1.0, 1.0]], [[1.0, 0.0], [0.0, 0.0]]),
        ([[2.0, 1.0], [1.0, -1.0]], [[0.5, 0.0], [0.0, 0.0]]),
    ],
)
def test_invsym_drops_nonpositive_pivots_like_mata(a, expected):
    np.testing.assert_allclose(linalg.invsym(np.array(a)), np.array(expected), atol=1e-14)


def _pivot_matrix(scale, t, r=0.6):
    return scale * np.array([[1.0, r], [r, r * r + t]])


@pytest.mark.parametrize("scale", [1e-6, 1.0, 1e6])
def test_relative_pivot_tolerance_matches_stata_bracket(scale):
    # Stata keeps the second pivot at t = 10^-9.375 and drops it at t = 10^-9.5 (a_22 = 0.36)
    assert linalg.invsym(_pivot_matrix(scale, 10**-9.375))[1, 1] != 0.0
    assert linalg.invsym(_pivot_matrix(scale, 10**-9.5))[1, 1] == 0.0


@pytest.mark.parametrize(
    ("k", "kept"), [(18.0, True), (18.875, True), (19.0, True), (19.125, False), (22.0, False)]
)
def test_absolute_pivot_floor_matches_stata_bracket(k, kept):
    inv = linalg.invsym(np.array([[10.0**-k]]))
    assert bool(inv[0, 0] != 0.0) is kept


def test_diagonal_with_tiny_second_entry_is_kept():
    # Stata never drops diag(1, 1e-17): the rule is relative to the *original* diagonal
    inv = linalg.invsym(np.diag([1.0, 1e-17]))
    np.testing.assert_allclose(np.diag(inv), [1.0, 1e17])


def test_invsym_dropped_counts_dropped_pivots():
    inv, n_dropped = linalg.invsym_dropped(np.array([[1.0, 1.0], [1.0, 1.0]]))
    assert n_dropped == 1 and inv[1, 1] == 0.0
    assert linalg.invsym_dropped(spd(3))[1] == 0


def test_invsym_of_exactly_singular_gram_is_generalised_inverse():
    x = np.random.default_rng(3).standard_normal((20, 3))
    x = np.column_stack([x, x[:, 0] + x[:, 1]])
    g = x.T @ x
    inv, n_dropped = linalg.invsym_dropped(g)
    assert n_dropped == 1
    dropped = [k for k in range(4) if inv[k, k] == 0.0]
    assert len(dropped) == 1
    k = dropped[0]
    assert np.all(inv[k, :] == 0.0) and np.all(inv[:, k] == 0.0)
    keep = [j for j in range(4) if j != k]
    np.testing.assert_allclose(inv[np.ix_(keep, keep)], np.linalg.inv(g[np.ix_(keep, keep)]))
    np.testing.assert_allclose(g @ inv @ g, g, atol=1e-9)  # defining property


def test_invsym_missing_input_gives_missing_output():
    assert np.isnan(linalg.invsym(np.array([[1.0, np.nan], [np.nan, 1.0]]))).all()


def test_empty_matrix():
    assert linalg.invsym(np.zeros((0, 0))).shape == (0, 0)


# ------------------------------------------------------------- invsym_batch
def test_invsym_batch_matches_loop_with_singular_member():
    mats = np.stack([spd(4, s) for s in range(5)])
    mats[2] = np.array(
        [[1, 1, 0, 0], [1, 1, 0, 0], [0, 0, 2, 0], [0, 0, 0, 3]], dtype=float
    )  # singular member forces the fallback path
    out = linalg.invsym_batch(mats)
    for k in range(mats.shape[0]):
        np.testing.assert_allclose(out[k], linalg.invsym(mats[k]), rtol=1e-10, atol=1e-12)


def test_invsym_batch_all_regular_and_higher_dims():
    mats = np.stack([spd(3, s) for s in range(6)]).reshape(2, 3, 3, 3)
    out = linalg.invsym_batch(mats)
    assert out.shape == mats.shape
    np.testing.assert_allclose(out @ mats, np.broadcast_to(np.eye(3), mats.shape), atol=1e-10)


def test_invsym_batch_empty():
    assert linalg.invsym_batch(np.zeros((0, 3, 3))).shape == (0, 3, 3)


# ------------------------------------------------------------------ cholinv
def test_cholinv_spd_and_non_spd():
    a = spd(5)
    np.testing.assert_allclose(linalg.cholinv(a), np.linalg.inv(a), rtol=1e-10)
    assert np.isnan(linalg.cholinv(np.array([[1.0, 2.0], [2.0, 1.0]]))).all()


# ------------------------------------------------------------------- syminv
def test_syminv_admits_spd_and_inverts():
    a = spd(6, cond=1e4) * 7.0
    res = linalg.syminv(a)
    assert res.ok
    np.testing.assert_allclose(res.inv, np.linalg.inv(a), rtol=1e-8)


@pytest.mark.parametrize("scale", [1e-20, 1e-8, 1.0, 1e8, 1e20])
def test_syminv_is_scale_equivariant(scale):
    base = spd(5, cond=50.0)
    res = linalg.syminv(base * scale)
    assert res.ok
    np.testing.assert_allclose(res.inv * scale, np.linalg.inv(base), rtol=1e-9)


def test_syminv_rejects_ill_conditioned_singular_indefinite_and_missing():
    assert not linalg.syminv(spd(4, cond=1e13)).ok
    assert not linalg.syminv(np.array([[1.0, 1.0], [1.0, 1.0]])).ok
    assert not linalg.syminv(np.array([[1.0, 2.0], [2.0, 1.0]])).ok
    assert not linalg.syminv(np.array([[1.0, np.nan], [np.nan, 1.0]])).ok
    assert not linalg.syminv(np.diag([1.0, 0.0])).ok
    assert not linalg.syminv(np.zeros((0, 0))).ok


def test_syminv_rejected_result_is_all_nan():
    res = linalg.syminv(np.diag([1.0, -1.0]))
    assert not res.ok and np.isnan(res.inv).all() and res.inv.shape == (2, 2)


# ------------------------------------------------------------ psd_ok, objtol
def test_psd_ok():
    assert linalg.psd_ok(spd(4))
    assert linalg.psd_ok(np.diag([1.0, 0.0]))  # semidefinite
    assert not linalg.psd_ok(np.array([[1.0, 2.0], [2.0, 1.0]]))  # a contrast has negative variance
    assert not linalg.psd_ok(np.array([[1.0, 0.5], [0.0, 1.0]]))  # not symmetric
    assert not linalg.psd_ok(np.array([[1.0, np.nan], [np.nan, 1.0]]))
    assert not linalg.psd_ok(np.zeros((2, 2)))


def test_objtol_is_scale_equivariant():
    assert linalg.objtol(0.0, 0.0, 1e-12) == 0.0
    assert linalg.objtol(2.0, -5.0, 1e-12) == pytest.approx(5e-12)
    assert linalg.objtol(2e-9, 5e-9, 1e-12) == pytest.approx(5e-21)
