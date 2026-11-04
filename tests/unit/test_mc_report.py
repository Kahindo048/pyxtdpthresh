"""Coverage report of Monte Carlo experiments (block I.5.3): the figures draw the results."""

import math

import matplotlib
import numpy as np
import pandas as pd
import pytest
from test_montecarlo import synthetic

from pyxtdpthresh._errors import SpecificationError
from pyxtdpthresh.extras.plotting import FIT_KINDS, MONTE_CARLO_KINDS, PLOT_KINDS, plot
from pyxtdpthresh.extras.simulation import (
    DESIGNS,
    coverage_markdown,
    coverage_report,
    coverage_table,
)

matplotlib.use("Agg")

BLUE, ORANGE = "#2a78d6", "#eb6834"


def rows(gammas, segments, hull, slopes, rejects, *, complete=True, linearity=None):
    """The records of an experiment of the design ``gong_seo`` written by hand."""
    out = []
    for i, gamma in enumerate(gammas):
        row = {
            "status": "ok",
            "gamma": gamma,
            "cover_segments": segments[i],
            "cover_hull": hull[i],
            "ci_complete": complete,
            "pval_lin": 0.01,
            "reject_linearity": True if linearity is None else linearity[i],
        }
        for name, values in slopes.items():
            row[f"b:{name}"] = 1.0
            row[f"cover:{name}"] = values[i]
        for shift, flags in rejects.items():
            row[f"reject_{shift}"] = flags[i]
        out.append(row)
    return out


@pytest.fixture(scope="module")
def small():
    """n = 400: 4 replications, the true threshold 0.25 covered by 3 of 4 segments."""
    slopes = {"lower:q": [True, True, True, False], "upper:q": [True, True, True, True]}
    rejects = {"0": [False, False, False, True], "0.1": [False, True, False, True],
               "0.5": [True, True, True, True]}  # fmt: skip
    data = rows(
        [0.2, 0.3, 0.25, 0.6], [True, True, True, False], [True, True, True, True], slopes, rejects
    )
    return synthetic("gong_seo", data, shifts=(0.1, 0.5))


@pytest.fixture(scope="module")
def large():
    """n = 800, everything covered; the power is the highest."""
    slopes = {"lower:q": [True] * 4, "upper:q": [True] * 4}
    rejects = {"0": [False] * 4, "0.1": [True, True, False, True], "0.5": [True] * 4}
    data = rows([0.24, 0.26, 0.25, 0.27], [True] * 4, [True] * 4, slopes, rejects)
    return synthetic("gong_seo", data, shifts=(0.1, 0.5))


@pytest.fixture(scope="module")
def linear():
    slopes = {"lower:q": [True] * 4}
    return synthetic(
        "linear",
        rows([0.0] * 4, [None] * 4, [None] * 4, slopes, {}, linearity=[False, False, True, False]),
    )


def named(small, large):
    return {"n = 400": small, "n = 800": large}


# ---------------------------------------------------------------------------------- dispatch
def test_the_new_kinds_are_registered_and_apart_from_the_fit_kinds():
    assert set(MONTE_CARLO_KINDS) == {"coverage", "power", "distribution"}
    assert set(MONTE_CARLO_KINDS) <= set(PLOT_KINDS)
    assert not set(MONTE_CARLO_KINDS) & set(FIT_KINDS) and "robustness" not in FIT_KINDS


@pytest.mark.parametrize("kind", MONTE_CARLO_KINDS)
def test_an_experiment_a_list_or_a_mapping_can_be_drawn(small, large, kind):
    assert plot(small, kind).axes
    assert plot([small, large], kind).axes
    assert plot(named(small, large), kind).axes


@pytest.mark.parametrize("kind", MONTE_CARLO_KINDS)
def test_a_monte_carlo_graph_refuses_other_results_and_the_reverse(small, kind):
    with pytest.raises(SpecificationError) as caught:
        plot(object(), kind)
    assert caught.value.key == "plot_wrong_result"
    with pytest.raises(SpecificationError) as caught:
        plot(small, "profile")
    assert caught.value.key == "plot_wrong_result"
    with pytest.raises(SpecificationError):
        plot(small, "robustness")


# ---------------------------------------------------------------------------------- coverage
def test_the_coverage_graph_draws_the_coverages_with_their_monte_carlo_bars(small, large):
    fig = plot(named(small, large), "coverage")
    left, right = fig.axes[:2]
    assert [t.get_text() for t in left.get_yticklabels()] == ["n = 400", "n = 800"]
    bars = left.containers
    assert len(bars) == 4  # segments and hull of the two experiments
    seg_small, hull_small, seg_large, _ = (c.lines[0].get_xdata()[0] for c in bars)
    assert (seg_small, hull_small, seg_large) == (0.75, 1.0, 1.0)
    # +/- 1.96 Monte Carlo errors: sqrt(.75 * .25 / 4)
    err = bars[0].lines[2][0].get_segments()[0]
    assert err[:, 0] == pytest.approx(
        [0.75 - 1.96 * math.sqrt(0.75 * 0.25 / 4), 0.75 + 1.96 * math.sqrt(0.75 * 0.25 / 4)]
    )
    colours = [matplotlib.colors.to_hex(c.lines[0].get_color()) for c in bars]
    assert colours == [BLUE, ORANGE, BLUE, ORANGE]
    assert list(left.lines[-1].get_xdata()) == [0.95, 0.95]  # the nominal level, drawn last
    assert left.lines[-1].get_linestyle() == ":"


def test_the_slope_panel_shows_each_slope_and_their_mean(small, large):
    fig = plot(named(small, large), "coverage")
    right = fig.axes[1]
    grey, mean = right.collections[0], right.collections[1]
    first = grey.get_offsets()
    assert sorted(first[:, 0]) == [0.75, 1.0] and set(first[:, 1]) == {0.0}
    assert matplotlib.colors.to_hex(mean.get_facecolor()[0]) == BLUE
    assert mean.get_offsets()[0].tolist() == [0.875, 0.0]
    assert right.get_ylim() == fig.axes[0].get_ylim()  # shared rows


def test_the_coverage_axis_leaves_room_for_the_lowest_value_and_the_nominal_level(small, large):
    fig = plot(named(small, large), "coverage")
    low, high = fig.axes[0].get_xlim()
    assert 0.0 <= low <= 0.5 and high == pytest.approx(1.02)
    assert fig.axes[0].get_xlim() == fig.axes[1].get_xlim()


def test_an_experiment_without_a_complete_set_is_named_not_drawn(small):
    empty = synthetic("gong_seo", rows([0.2] * 2, [None] * 2, [None] * 2, {}, {}, complete=False))
    fig = plot({"ok": small, "empty": empty}, "coverage")
    assert any("no complete set" in t.get_text() for t in fig.axes[0].texts)
    fr = plot({"ok": small, "empty": empty}, "coverage", lang="fr")
    assert any("aucun ensemble complet" in t.get_text() for t in fr.axes[0].texts)


def test_the_coverage_graph_speaks_french(small):
    fig = plot(small, "coverage", lang="fr")
    left = fig.axes[0]
    assert left.get_title(loc="left") == "Seuil"
    assert fig.axes[1].get_title(loc="left") == "Pentes"
    assert [t.get_text() for t in left.get_yticklabels()] == ["n = 300, T = 6, saut = 0,2"]
    assert "Couverture" in fig._supxlabel.get_text()
    assert any("nominal 95 %" in t.get_text() for t in left.texts)
    assert any(t.get_text() == "enveloppe" for t in left.texts)


# ------------------------------------------------------------------------------------- power
def test_the_power_graph_draws_the_rejection_rate_against_the_shift(small, large):
    fig = plot(named(small, large), "power")
    ax = fig.axes[0]
    level, first, second = ax.lines[0], ax.lines[1], ax.lines[2]
    assert list(level.get_ydata()) == pytest.approx([0.05, 0.05])
    assert first.get_xdata().tolist() == [0.0, 0.1, 0.5]
    assert first.get_ydata().tolist() == [0.25, 0.5, 1.0]
    assert second.get_ydata().tolist() == [0.0, 0.75, 1.0]
    assert matplotlib.colors.to_hex(first.get_color()) == BLUE
    assert matplotlib.colors.to_hex(second.get_color()) == ORANGE
    assert {"n = 400", "n = 800"} <= {t.get_text() for t in ax.texts}
    assert ax.get_xlabel().startswith("Shift c") and ax.get_ylabel() == "Rejection rate"


def test_names_at_the_end_of_the_lines_never_overlap():
    from pyxtdpthresh.extras.plotting.power import LABEL_GAP, _spread

    ends = [
        (0.5, 0.31, "a", "x"),
        (0.5, 0.335, "b", "x"),
        (0.5, 0.65, "c", "x"),
        (0.5, 0.30, "d", "x"),
    ]
    placed = _spread(ends)
    heights = [y for _, y, _, _ in placed]
    assert [name for _, _, name, _ in placed] == ["d", "a", "b", "c"]
    assert all(b - a >= LABEL_GAP - 1e-12 for a, b in zip(heights, heights[1:], strict=False))
    assert heights[0] == 0.30 and heights[-1] == 0.65  # a name far from the others stays put


def test_the_power_graph_leaves_out_designs_without_a_threshold(small, linear):
    ax = plot({"threshold": small, "linear": linear}, "power").axes[0]
    assert len(ax.lines) == 2  # the level and the one experiment with a threshold
    assert "linear" not in {t.get_text() for t in ax.texts}


def test_the_power_graph_speaks_french(small):
    ax = plot(small, "power", lang="fr").axes[0]
    assert ax.get_ylabel() == "Taux de rejet" and ax.get_xlabel().startswith("Décalage c")
    assert any(t.get_text() == "niveau 0,05" for t in ax.texts)


# ------------------------------------------------------------------------------ distribution
def test_the_distribution_graph_draws_the_quantiles_of_the_estimates(small, large):
    fig = plot(named(small, large), "distribution")
    ax = fig.axes[0]
    gamma = small.ok["gamma"].to_numpy(float)
    low, q1, med, q3, high = np.quantile(gamma, [0.05, 0.25, 0.5, 0.75, 0.95])
    thin, thick, truth = ax.lines[0], ax.lines[1], ax.lines[2]
    assert thin.get_xdata().tolist() == pytest.approx([low, high])
    assert thick.get_xdata().tolist() == pytest.approx([q1, q3])
    assert ax.collections[0].get_offsets()[0].tolist() == pytest.approx([med, 0.0])
    assert truth.get_xdata().tolist() == [0.25, 0.25]
    assert matplotlib.colors.to_hex(truth.get_color()) == ORANGE
    assert [t.get_text() for t in ax.get_yticklabels()] == ["n = 400", "n = 800"]


def test_the_distribution_graph_names_a_design_without_threshold(small, linear):
    ax = plot({"threshold": small, "linear": linear}, "distribution").axes[0]
    assert any(t.get_text() == "no threshold" for t in ax.texts)
    fr = plot({"threshold": small, "linear": linear}, "distribution", lang="fr").axes[0]
    assert any(t.get_text() == "pas de seuil" for t in fr.texts)


def test_unnamed_experiments_are_named_after_their_size_and_jump(small):
    ax = plot(small, "distribution").axes[0]
    assert [t.get_text() for t in ax.get_yticklabels()] == ["n = 300, T = 6, jump = 0.2"]
    fr = plot(small, "distribution", lang="fr").axes[0]
    assert [t.get_text() for t in fr.get_yticklabels()] == ["n = 300, T = 6, saut = 0,2"]


def test_several_designs_are_told_apart_in_the_names(small, linear):
    ax = plot([small, linear], "distribution").axes[0]
    labels = [t.get_text() for t in ax.get_yticklabels()]
    assert labels[0].startswith("gong_seo: ") and labels[1].startswith("linear: ")


# ----------------------------------------------------------------------------------- the table
def test_the_table_has_one_row_per_experiment_with_the_statistics(small, large, linear):
    table = coverage_table({"n = 400": small, "n = 800": large, "linear": linear})
    assert list(table.index) == ["n = 400", "n = 800", "linear"]
    row = table.loc["n = 400"]
    assert row["reps"] == 4 and row["failed"] == 0 and row["design"] == "gong_seo"
    gamma = np.array([0.2, 0.3, 0.25, 0.6])
    assert row["gamma_bias"] == pytest.approx(np.mean(gamma - 0.25))
    assert row["gamma_rmse"] == pytest.approx(math.sqrt(np.mean((gamma - 0.25) ** 2)))
    assert row["gamma_median_bias"] == pytest.approx(np.median(gamma - 0.25))
    assert row["coverage_segments"] == 0.75 and row["coverage_hull"] == 1.0
    assert row["mcse_segments"] == pytest.approx(math.sqrt(0.75 * 0.25 / 4))
    assert row["slopes_coverage_mean"] == pytest.approx(0.875)
    assert row["slopes_coverage_min"] == 0.75
    assert row["incomplete"] == 0.0 and row["linearity_rate"] == 1.0
    assert (row["reject_0"], row["reject_0.1"], row["reject_0.5"]) == (0.25, 0.5, 1.0)
    assert table.loc["linear", "linearity_kind"] == "size"
    assert table.loc["linear", "linearity_rate"] == 0.25
    assert math.isnan(table.loc["linear", "gamma_rmse"]) and math.isnan(table.loc["linear", "jump"])


def test_markdown_is_a_table_with_a_decimal_comma_in_french(small, large):
    table = coverage_table(named(small, large))
    english = coverage_markdown(table).splitlines()
    assert english[0].startswith("| experiment | reps | failed | bias | RMSE | coverage (segments)")
    assert english[1] == "|" + "---|" * 10
    assert english[2].startswith("| n = 400 | 4 | 0 |") and "0.750" in english[2]
    french = coverage_markdown(table, lang="fr").splitlines()
    assert french[0].startswith("| expérience | réplications | échecs | biais | REQM |")
    assert "0,750" in french[2] and "0.750" not in french[2]
    assert "-" in coverage_markdown(coverage_table({"x": synthetic("linear", [{"status": "ok"}])}))


def test_the_report_writes_the_table_and_the_graphs_in_both_languages(small, large, tmp_path):
    written = coverage_report(named(small, large), tmp_path / "report")
    expected = {"table", "markdown_en", "markdown_fr"} | {
        f"{kind}_{lang}" for kind in MONTE_CARLO_KINDS for lang in ("en", "fr")
    }
    assert set(written) == expected
    for path in written.values():
        assert path.exists() and path.stat().st_size > 200
    table = pd.read_csv(written["table"])
    assert table["experiment"].tolist() == ["n = 400", "n = 800"]
    assert written["coverage_fr"].name == "coverage_fr.png"
    assert "couverture" in written["markdown_fr"].read_text(encoding="utf-8")


def test_the_report_names_unnamed_experiments_in_each_language(small, tmp_path):
    written = coverage_report([small], tmp_path, langs=("fr",), stem="mc")
    assert set(written) == {"table", "markdown_fr", "coverage_fr", "power_fr", "distribution_fr"}
    assert written["table"].name == "mc.csv"
    assert "saut = 0,2" in written["markdown_fr"].read_text(encoding="utf-8")


def test_the_default_design_is_discontinuous_with_the_jump_the_names_report():
    assert DESIGNS["gong_seo"].gamma == 0.25
    assert DESIGNS["gong_seo"].jump == pytest.approx(-0.3 + 2.0 * 0.25)
