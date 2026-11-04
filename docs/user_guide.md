# pyxtdpthresh user guide

This guide explains every argument of the two estimators, how each one corresponds to the Stata
option it ports, and how to read what comes back. It assumes you know what a dynamic panel
threshold model is; the equations and the algorithms are in the methodological note, Appendix A of the PDF edition of this guide (`user_guide.pdf`, built from `docs/methodological_note.tex`); the comparison with Stata 17, number by number, is Appendix B. The Stata
help files (`xtdpthresh.sthlp`, `xthenreg.sthlp`) remain the reference for the commands; this
guide says where the Python package differs from them.

**Contents**

1. [Before you start](#1-before-you-start)
2. [Calling `xtdpthresh`](#2-calling-xtdpthresh)
3. [Options of `xtdpthresh`](#3-options-of-xtdpthresh)
4. [Choosing your settings](#4-choosing-your-settings)
5. [Calling `xthenreg`](#5-calling-xthenreg)
6. [Reading the output](#6-reading-the-output)
7. [Working with a result](#7-working-with-a-result)
8. [Reproducibility, speed and memory](#8-reproducibility-speed-and-memory)
9. [Simulation and Monte Carlo](#9-simulation-and-monte-carlo)
10. [Errors and warnings](#10-errors-and-warnings)
11. [What differs from Stata](#11-what-differs-from-stata)

The code blocks of this guide run top to bottom as one script (`tests/integration/test_examples.py`
runs them), so a block may use the names defined in the blocks before it. A block whose first line
is `# not run by the tests` is shown for illustration only.

---

## 1. Before you start

**Data.** Both estimators take a pandas `DataFrame` in long form, one row per (unit, period). Name
the unit and time columns with `id=` and `time=`, or give the frame a two-level `MultiIndex`
(unit, time) and leave both out. `pyx.from_stata("file.dta")` reads a `.dta` file and uses the
`xtset` variables Stata recorded in it; a file saved without `xtset` is returned as it is and you
pass `id=` and `time=` yourself (the names are never guessed).

`xtdpthresh` accepts unbalanced panels. `xthenreg` needs a strongly balanced panel (every unit
observed in every period) and stops with an error otherwise, as the Stata command does.

**Names and missing values.** Column names may contain accents and other Unicode letters
(`"investissé"`, `"dette_é"`), as in Stata 14 and later; a name with a space is refused. A `NaN`,
a missing nullable value and an infinity (`±inf`, for example after a `log(0)`) are all missing,
as Stata has no infinity; an infinity gives a warning that names the column and the count.

**Time-series operators.** Variable names in every role may carry Stata's operators as text:
`"L.x"`, `"L2.x"`, `"D.x"`, `"S12.x"`, `"L(1/2).x"`. They are computed on the calendar, as in
Stata: `L.x` is the value of the *period* before, so a gap in a unit's dates gives a missing value.
The dependent variable may not carry an operator. The rules of the help file apply: each variable
sits in only one role, a lag of the dependent variable is declared `predetermined`, and
differences and leads of the dependent variable are refused.

**The example used below.** Hansen's (1999) firm investment panel, 565 firms observed from 1973 to
1987, with the five extreme firms removed as in Seo and Shin (2016).

```python
import pyxtdpthresh as pyx

df = pyx.load_dataset("invest")
df = df[~df["firm"].isin([137, 391, 407, 488, 538])]

# The model of Seo and Shin (2016, section 7): all four slopes change at a leverage threshold,
# cash flow, Tobin's q and leverage are endogenous, instruments are lags 3 to 8, collapsed.
MODEL = dict(
    q="debt",
    endogenous=["cashflow", "tobin_q", "debt"],
    maxlag=(3, 8),
    collapse=True,
    id="firm",
    time="year",
)
```

**Other ways in.** The unit and time columns can be the two levels of the index; `pyx.list_datasets()`
names the bundled data (`"invest"` today); `pyx.from_stata` reads a `.dta` file.

```python
indexed = df.set_index(["firm", "year"])
no_names = {k: v for k, v in MODEL.items() if k not in ("id", "time")}
same = pyx.xtdpthresh(indexed, "invest", bootstrap=False, **no_names)
print(round(same.gamma, 4))

print(pyx.list_datasets())  # name -> description

# A .dta saved without xtset gives a plain frame: the names are never guessed.
df[["firm", "year", "invest", "debt"]].to_stata("panel.dta", write_index=False)
raw = pyx.from_stata("panel.dta")
print(raw.attrs["id"], raw.attrs["time"])  # None None: pass id= and time= yourself
```

A file saved after `xtset` (or `xtset …, delta()`) gives a frame whose index levels are the panel
and time variables Stata recorded, with their names in `attrs["id"]`, `attrs["time"]` and the time
unit in `attrs["delta"]`; `id=` and `time=` can then be left out. Stata value labels are not applied.

---

## 2. Calling `xtdpthresh`

```text
res = pyx.xtdpthresh(data, y, x=(), *, q, id=None, time=None, where=None, grid_values=None, **options)
```

| Argument | Stata | Meaning |
|---|---|---|
| `data` | the data in memory | long `DataFrame` |
| `y` | `depvar` | dependent variable (a plain column name) |
| `x` | `indepvars` | strictly exogenous regressors, a name or a list |
| `q` | `qx(varname)` | threshold variable, **required** |
| `endogenous` | `endogenous(varlist)` | regressors correlated with the current error |
| `predetermined` | `predetermined(varlist)` | regressors uncorrelated with current and later errors |
| `exogenous` | `exogenous(varlist)` | more strictly exogenous regressors, treated like `x` |
| `iv` | `iv(varlist)` | external instruments, entered with their period-t values |
| `id`, `time` | `xtset id time` | unit and time columns (or index level names) |
| `where` | `if` | condition selecting the equations (see below) |
| `grid_values` | (none) | candidate thresholds to use instead of the grid built from `grid` |
| `**options` | the other options | Section 3 |

`endogenous`, `predetermined`, `exogenous` and `iv` are keyword arguments given as a name or a
list of names. Anything else the call receives is an option of Section 3; an unknown name raises a
`TypeError` (`… got an unexpected keyword argument 'gridd'`).

The model is `y = x'β + (1, x')δ · 1(q > γ) + η + ε`. In the dynamic model (the default) the lag of
`y` is added to `x` automatically; `static=True` removes it. The slopes are `β` below the threshold
and `β + δ₂` above it; `δ₁` is the shift of the intercept.

**How the roles are instrumented.** With `method="fd"`, an endogenous regressor is instrumented by
its levels from t-2, a predetermined one from t-1, a strictly exogenous one by its own transformed
value; with `method="fod"` the dates are t-1 and t. `maxlag` and `collapse` shape these sets, `iv`
adds external ones.

**`where` and `in`.** `where` is a string evaluated with `DataFrame.eval` (`"year >= 1980"`,
`"firm != 12"`) or a boolean array of the length of the frame. Two differences from Stata's `if`: a
missing value in the condition counts as *false* (Stata counts it as true; the rows with a missing
variable are removed afterwards anyway), and there is no `in`; select rows of the frame instead.
By default (`history="panel"`) the condition restricts the *equations*, and observations outside it
remain available as instruments.

```python
# Point estimates only: the bootstrap is the slow part, bootstrap=False skips it.
fast = pyx.xtdpthresh(df, "invest", bootstrap=False, **MODEL)
print(round(fast.gamma, 4), fast.n_obs, fast.n_units, fast.n_instruments)

# Equations from 1980 on; the earlier observations still serve as instruments.
late = pyx.xtdpthresh(df, "invest", where="year >= 1980", bootstrap=False, **MODEL)
print(late.n_obs)

# Your own candidate thresholds, instead of the grid built from `grid`.
import numpy as np

own = pyx.xtdpthresh(
    df, "invest", grid_values=np.linspace(0.05, 0.55, 11), bootstrap=False, **MODEL
)
print(round(own.gamma, 4))
```

A complete call, with inference, a seed, and the test of the threshold estimated by Hansen (1999),
0.0157 (this is the second example of the Stata help file):

```python
res = pyx.xtdpthresh(df, "invest", gamma_test=0.0157, seed=12345, **MODEL)
print(res)
```

**External instruments.** `iv` takes names (with operators) of variables that are not regressors:

```python
df["peer_q"] = df.groupby("year")["tobin_q"].transform("mean")  # yearly mean of Tobin's q
withiv = pyx.xtdpthresh(df, "invest", iv=["L2.peer_q"], bootstrap=False, **MODEL)
print(withiv.n_instruments)
```

A variable that takes the same value for every unit in a period (such as `peer_q`) is identified
through the period constants: without `collapse`, its own columns repeat the constants and are
dropped, and `res.scalars["N_iv_common"]` counts them.

---

## 3. Options of `xtdpthresh`

Python names are in `snake_case`; the Stata name is given for each. Defaults are those of the Stata
command. Every rule of the Stata command is checked in the same order and raises
`SpecificationError` (Section 10) carrying Stata's return code.

### Model

| Python | Stata | Default | Notes |
|---|---|---|---|
| `kink` | `kink` | `False` | Continuous effect at the threshold instead of a jump. Put `q` in `x`, `endogenous` or `predetermined` so that it has a slope below γ; otherwise a warning says the model is a one-sided hinge. |
| `static` | `static` | `False` | No automatic lag of `y`. Accepted by the Stata command; the help file of version 0.9.38 does not describe it. |
| `time_effects` | `td` | `False` | Partial common time effects out of the equations (dummies are not entered by hand). |
| `history` | `history(panel\|sample)` | `"panel"` | With `"sample"`, `where` also bounds the lag history; then no operated term (`L.x`) may be used. Build the lags as columns first. |

### Instruments

| Python | Stata | Default | Notes |
|---|---|---|---|
| `maxlag` | `maxlag(# [#])` | all lags | An integer `L` uses lags 1 to `L` for predetermined variables and 2 to `L` for endogenous variables and `y`; a pair `(a, b)` uses `a` to `b` with the same minimums. `None` means no limit. Without it the number of instruments grows with the square of T. |
| `collapse` | `collapse` | `False` | One instrument column per lag instead of one per lag and period (Roodman 2009). Fewer instruments, possibly weaker identification of γ. |
| `iv_collapse` | `iv(…, collapse)` | `False` | Collapse only the external instruments. `collapse=True` implies it. |

### Transformation and threshold search

| Python | Stata | Default | Notes |
|---|---|---|---|
| `method` | `method(fd\|fod)` | `"fd"` | First differences, or forward orthogonal deviations. FOD discards fewer equations when the panel has interior gaps (an interior gap removes three FD equations and two FOD equations). |
| `grid` | `grid(#)` | `100` | Points of the threshold search, at least 10. Uniform grids of 100, 199 and 397 points are nested, so a finer grid checks the sensitivity of γ̂. |
| `grid_type` | `gridtype(uniform\|quantile)` | `"uniform"` | Equally spaced in `q`, or at its empirical quantiles; used for the estimation grid and the confidence-set grid. |
| `trim` | `trim(#)` | `0.10` | Total trimming rate of `q`, split between the tails; 0.10 restricts the grid to the 5th–95th percentiles. Between 0.01 and 0.45. (`xthenreg` uses 0.4.) |
| `grid_sample` | `gridsample(effective\|observed)` | `"effective"` | Which values of `q` define the trimming bounds and the regime counts of `min_regime`: those that enter the transformed equations, or those in the retained rows. |
| `min_regime` | `minregime(#)` | `0` | Raise the minimum number of observations in each regime. The default, and the least allowed, is the size of the smaller trimmed tail. |
| `refine` | `refine(#)` | `0` | Rounds (0–20) of local refinement after the grid search: the observed values of `q` next to γ̂ become candidates. The confidence set and tests use the initial grid only. Not allowed with `kink`, whose γ̂ is refined continuously. |
| `grid_values` | (none) | `None` | An argument of the call, not an option: an explicit array of candidates. |

### Inference

| Python | Stata | Default | Notes |
|---|---|---|---|
| `bootstrap` | `noboot` (negated) | `True` | `False` skips the confidence set and the linearity test. Point estimates, Hansen and AR tests remain. |
| `n_boot` | `boot(#)` | `299` | Bootstrap replications, at least 10. With B draws the smallest possible p-value is 1/(B + 1). |
| `grid_ci` | `gridci(#)` | `100` | Candidate thresholds of the confidence-set grid, at least 10. |
| `boot_type` | `boottype(wild\|unit)` | `"wild"` | Scheme of the confidence set and of `gamma_test`. `"unit"` resamples whole units, follows Algorithm 1 of Gong and Seo (2026), needs `method="fd"` without `kink` or `time_effects`, and is much slower. The linearity test always uses the wild scheme. |
| `seed` | `rseed(#)` | drawn | Integer in 0 … 2³¹-1. When the bootstrap is on and `seed` is omitted, a seed is drawn and recorded: `res.seed` replays the run. Separate seeds are derived for the confidence set, the linearity test and `gamma_test`, so changing one leaves the draws of the others unchanged. |
| `linearity_test` | `notest` (negated) | `True` | `False` skips the bootstrap linearity test. |
| `gamma_test` | `citest(#)` | `None` | Also run the bootstrap test of H₀: γ = #, with a value of `q`. Needs the bootstrap. It is evaluated after the other components with its own seed, so asking for it changes nothing else. The result is in `res.scalars["citest_p"]` and `["citest_accept"]`. |
| `continuity_test` | `conttest` | `False` | Bootstrap test of continuity (is the kink model enough?), result in `res.scalars["pval_cont"]`. Needs the bootstrap and the linearity test, no `kink`, and `q` as a contemporaneous regressor. Accepted by the command; not described in the 0.9.38 help file. |
| `vce` | `vce(robust\|windmeijer)` | `"robust"` | Cluster-robust two-step sandwich, or a Windmeijer-type correction. The variance includes the estimation error of γ̂; the one conditional on γ̂ is `res.fit.variance.cond` (`e(V_cond)`). |
| `bw_scale` | `bwscale(#)` | `1.5` | Scale of the kernel bandwidth `h = # · 1.06 · s_q · n^(-1/5)` of the jump model's joint variance. Only the reported variance and the AR statistics that include γ̂ depend on it. |
| `center` | `nocenter` (negated) | `True` | `False` uses the uncentered moment covariance, as `xtabond2` does. |
| `level` | `level(#)` | `95` | Confidence level, between 10 and 99.99. |
| `coef_boot` | `coefboot(twostep\|onestep\|none)` | `"none"` | Legacy coefficient bootstrap that searches the threshold again in each draw. A note says so; the intervals are in `res.fit.bootstrap.coefficient.interval` (`e(b_bootci)`) and the printed tables keep the analytic ones. `"twostep"` is refused with `time_effects`. |
| `coef_ci_type` | `coefcitype(symmetric\|percentile)` | `"symmetric"` | Kind of interval of that bootstrap. |

### Reporting

| Python | Stata | Default | Notes |
|---|---|---|---|
| `warn` | `nowarn` (negated) | `True` | `False` silences nonfatal warnings and most notes. Notes on dropped instrument columns and a missing Hansen J, and the warnings for an incomplete or empty confidence set, are always shown. |
| `verbose` | `verbose` | `False` | Accepted, **no effect** in Python. The per-candidate table of the confidence set is `res.ci_table()`. |
| `export_gmm` | `exportgmm` | `False` | Accepted, **no effect** in Python. |

### Combinations the commands refuse

* `n_boot < 10` or `grid_ci < 10` with the bootstrap on; `grid < 10`.
* `gamma_test` without the bootstrap; `continuity_test` without the bootstrap and the linearity test.
* `refine > 0` with `kink`.
* `boot_type="unit"` with `method="fod"` or with `kink` (checked when the bootstrap is on), and with
  `time_effects`.
* `coef_boot="twostep"` with `time_effects`.
* A `maxlag` pair with the low end above the high end.
* `history="sample"` with a lagged or differenced term.

### Retired options

These existed in earlier versions of the Stata command and are refused with an explanation:
`method="system"`, `boot_type="exact"`, `coef_boot="gs"`, and the arguments `search_mode`,
`search_max`, `search_tol`, `lev_maxlag` and `iv_maxlag`.

### The options in use

Each option below is used once, on the model of Section 1. Point estimates first (`bootstrap=False`
is instant), then the options of the bootstrap with a light one (99 draws, 40 candidates).

```python
def fit(**changes):
    """Point estimates of the model of Section 1, with some options changed."""
    return pyx.xtdpthresh(df, "invest", **{**MODEL, "bootstrap": False, **changes})


def show(label, r):
    print(
        f"{label:26s} gamma={r.gamma:.4f}  equations={r.n_obs}  instruments={r.n_instruments}"
        f"  Hansen p={r.scalars['hansen_p']:.3f}"
    )


# Model
show("static (lags 2-8)", fit(static=True, maxlag=(2, 8)))  # no automatic L.invest
show("time effects (td)", fit(time_effects=True))
show("kink", fit(kink=True))
show("history='sample', 1976+", fit(history="sample", where="year >= 1976"))

# Instruments
show("maxlag (3, 5)", fit(maxlag=(3, 5)))
show("no collapse, lags 3-5", fit(collapse=False, maxlag=(3, 5)))
show(
    "external, iv_collapse",
    fit(iv=["L2.cashflow"], iv_collapse=True, collapse=False, maxlag=(3, 5)),
)

# Transformation, search, variance
show("fod", fit(method="fod"))
show("trim 0.20", fit(trim=0.20))
show("quantile grid", fit(grid_type="quantile"))
show("grid_sample='observed'", fit(grid_sample="observed"))
show("min_regime 500", fit(min_regime=500))
show("refine 3", fit(refine=3))
show("windmeijer", fit(vce="windmeijer"))
show("uncentered covariance", fit(center=False))
show("bw_scale 3", fit(bw_scale=3))
show("warn=False", fit(warn=False))
```

```python
infer = dict(n_boot=99, grid_ci=40, seed=1)  # a light bootstrap, for illustration


def full(**changes):
    return pyx.xtdpthresh(df, "invest", **{**MODEL, **infer, **changes})


print(full().gamma_ci, full(level=90).gamma_ci)  # 95 % and 90 % sets (hulls)
print(full(linearity_test=False).scalars["pval_lin"])  # nan: the test was skipped
print(full(continuity_test=True).scalars["pval_cont"])  # bootstrap test of continuity

# Unit resampling (Algorithm 1 of Gong and Seo); slower, so fewer draws here.
unit = pyx.xtdpthresh(
    df, "invest", **{**MODEL, "n_boot": 49, "grid_ci": 20, "seed": 1, "boot_type": "unit"}
)
print(unit.gamma_ci, unit.scalars["ci_nseg"])

# Legacy coefficient bootstrap: a note is issued; the intervals are kept on the fit.
legacy = full(coef_boot="onestep", coef_ci_type="percentile")
print(legacy.fit.bootstrap.coefficient.interval.shape)  # (2, 9): lower and upper, e(b_bootci)
```

`verbose` and `export_gmm` are accepted and do nothing (Section 11).

---

## 4. Choosing your settings

No setting is right in general: the data and the question decide. This section says what each
choice does according to the help file of the command, and shows on the Hansen panel how far the
answer can move. The numbers are one panel and one model. They illustrate sensitivity; they are not
rules.

### Instruments: the choice that matters most

Without `collapse` and `maxlag`, the number of instruments grows with the square of the number of
periods. Many instruments relative to the number of units makes the Hansen test unreliable
(Roodman 2009) and, with the default centered covariance, tends to make it over-reject (help file).
`collapse` and `maxlag` shrink the set, at the price of weaker identification of γ.

```python
import pandas as pd

settings = {
    "collapsed, lags 3-8": {},
    "collapsed, lags 2-10": {"maxlag": (2, 10)},
    "collapsed, lags 3-5": {"maxlag": (3, 5)},
    "not collapsed, lags 3-5": {"collapse": False, "maxlag": (3, 5)},
    "not collapsed, all lags": {"collapse": False, "maxlag": None},
}
rows = {}
for label, changes in settings.items():
    r = fit(**changes)
    rows[label] = {
        "gamma": r.gamma,
        "instruments": r.n_instruments,
        "hansen_p": r.scalars["hansen_p"],
        "ar2_p": r.scalars["ar2_p"],
    }
print(pd.DataFrame(rows).T.round(4))
```

On this panel (560 units) the table reads:

| Setting | γ̂ | Instruments | Hansen p | AR(2) p |
|---|---:|---:|---:|---:|
| collapsed, lags 3-8 | 0.4194 | 25 | 0.382 | 0.738 |
| collapsed, lags 2-10 | 0.0121 | 37 | 0.626 | 0.013 |
| collapsed, lags 3-5 | 0.5895 | 13 | 0.972 | 0.476 |
| not collapsed, lags 3-5 | 0.1216 | 144 | 0.000 | 0.939 |
| not collapsed, all lags | 0.1092 | 377 | 0.000 | 0.922 |

The threshold estimate moves from 0.01 to 0.59 with the instrument set. Two readings are grounded
in the help file. The lag-2 window rejects AR(2) (p = 0.013), which "casts doubt on the lag-2
instruments or on the specification" (third example of the help file). The uncollapsed sets have
144 and 377 instruments for 560 units and a Hansen p-value of 0.000, which the help file warns is
unreliable in that situation: it is not by itself evidence against the model, but the instability of
γ̂ is a fact to report. `pyx.robustness()` (Section 7) runs this kind of variation for you.

A workable order: start from a collapsed set with a lag window justified by the timing of the
variables; check AR(2) and Hansen; move the window and the collapsing; report what moves.

### First differences or forward orthogonal deviations

`method="fd"` is the transformation of Seo and Shin (2016) and of `xthenreg`; `method="fod"` removes
the unit effect by forward orthogonal deviations. With interior gaps, FOD discards fewer equations
(an interior gap removes three FD equations and two FOD equations). Asymptotic theory exists for FD;
for FOD the authors of the command report Monte Carlo evidence only (Nguyen and Lai 2026). On this
balanced panel both give γ̂ = 0.4194 (AR(2) p-values 0.738 and 0.944). On an unbalanced panel,
estimate both and put them side by side with `pyx.compare` (example 3 does exactly that);
`diagnose()` also points it out when FD is used on an unbalanced panel.

### Jump or kink

The default allows a discontinuity at γ. `kink=True` imposes continuity; `q` should then be a
regressor, or the model is a one-sided hinge and a warning says so. If the function is continuous,
the unrestricted estimator of γ converges at rate n^(1/4) to a non-normal limit, whereas the kink
estimator is asymptotically normal (Gong and Seo 2026), so the choice affects inference, not only the
fit. `continuity_test=True` tests the kink model against the jump model. On the Hansen panel the kink
model gives γ̂ = 0.032 and a Hansen p-value of 0.000, against 0.4194 and 0.382 for the jump model.

### Threshold search

The defaults are a uniform grid of 100 points between the 5th and 95th percentile of `q`. Uniform
grids of 100, 199 and 397 points are nested, so `grid=199` or `grid=397` is the natural check that
γ̂ does not depend on the grid. `grid_type="quantile"` puts points where the data are;
`refine` adds the observed values of `q` next to γ̂; `trim` moves the ends; `min_regime` demands more
observations in each regime. On the Hansen panel these choices keep γ̂ between 0.414 and 0.421
(trim 0.20: 0.4144; quantile grid: 0.4210; observed support: 0.4137; refine 3: 0.4150).

### Bootstrap

`n_boot=299` and `grid_ci=100` are the defaults. The smallest possible p-value is 1/(`n_boot` + 1),
so a very small `n_boot` cannot show a small p-value. For exploring, `n_boot=99, grid_ci=40` is much
faster; use the defaults, or more, for what you report. `boot_type="unit"` follows the algorithm with a
proof (Gong and Seo 2026) but is much slower. Always fix a `seed` for results you publish (a seed is
recorded anyway).

### Variance

`vce="robust"` and `vce="windmeijer"` give the same estimates and thresholds; only the variance of
the slopes and the AR statistics that include γ̂ change. `center=False` reproduces `xtabond2`'s
uncentered covariance (and its Hansen statistic).

### Before you report

1. Keep `res.seed` and `res.settings_log()`, or `res.to_json()`.
2. Check the grid (`grid=199`) and one other instrument set.
3. Run `pyx.robustness()` and report how stable the threshold is.
4. Report the segments of the confidence set, not only its hull.
5. Report Hansen and AR(2) as diagnostics, with the number of instruments next to the number of units.

---

## 5. Calling `xthenreg`

```text
res = pyx.xthenreg(data, y, x=(), *, q, endogenous=(), exogenous=(), inst=(),
                   id=None, time=None, where=None, static=False, kink=False,
                   grid_num=100, trim_rate=0.4, h_0=1.5, boot_reps=0, seed=None, draws=None,
                   engine="fast")
```

`xthenreg` implements the first-difference estimator of Seo, Kim and Kim (2019) for strongly
balanced panels, with the sup-Wald linearity test of Seo and Shin (2016).

| Python | Stata | Default | Notes |
|---|---|---|---|
| `y`, `x` | `depvar`, `indepvars` | | In Stata the threshold variable is the **second word** of the variable list, `xthenreg y q x1`; here it is the separate argument `q`, so `xthenreg y q x1` is `xthenreg(df, "y", ["x1"], q="q")`. |
| `endogenous` | `endogenous(varlist)` | none | Excluded from `x`, as in Stata. |
| `exogenous` | `exogenous(varlist)` | none | Additional exogenous regressors. Accepted by the command; not described in its help file. |
| `inst` | `inst(varlist)` | none | Additional instruments. |
| `static` | `static` | `False` | No automatic lag of `y`. |
| `kink` | `kink` | `False` | Kink model. |
| `grid_num` | `grid_num(integer)` | `100` | Points of the grid. |
| `trim_rate` | `trim_rate(real)` | `0.4` | Total trimmed share of `q`. |
| `boot_reps` | `boost(integer)` | `0` | Replications of the bootstrap linearity test; `0` skips it. |
| `seed` | (set by `set seed`) | drawn | Seed of the bootstrap weights; recorded in `res.seed`. |
| `draws` | (none) | `None` | Standard normal weights `(boot_reps, N)` to use instead of the generator. |
| `engine` | (none) | `"fast"` | `"fast"` or `"literal"` moment computation; both give the same numbers, `"literal"` follows the Mata code line by line. |
| `h_0` | `h_0(real)` | `1.5` | Multiplier of the kernel bandwidth `h = h_0 · 1.06 · N^(-1/5) · sd(q)` of the covariance (jump model only; the kink model has no bandwidth). Checked against Stata with `h_0(3)` and `h_0(0.7)`. |

```python
sk = pyx.xthenreg(
    df, "invest", ["cashflow", "tobin_q"], q="debt", id="firm", time="year", boot_reps=49, seed=3
)
print(sk.names)
print(round(sk.gamma, 4), round(sk.scalars["sup_wald"], 2), sk.scalars["boots_p"])
print(sk.ci.round(3))  # e(CI): lower and upper limits of every coefficient, γ last
print(pyx.compare([sk, full()], model_names=["xthenreg", "xtdpthresh"]).to_text())
```

**Coefficient names** are those of the command. `Lag_y_b` is the slope of `L.y` below the
threshold and `x_b` that of a regressor; `cons_d`, `Lag_y_d` and `x_d` are the changes above it
(`_d` for δ; `cons_d` is the intercept shift); `r` is the threshold. With `kink=True` the names are
`Lag_y_b`, `x_b`, `kink_slope` and `r`; with `static=True` there is no `Lag_y_*`. The table of the
result shows them in the same three blocks (lower, change, upper) as `xtdpthresh`.

**Inference.** `xthenreg` reports an asymptotic interval for every coefficient, the threshold
included (`res.ci`, `e(CI)`), not a bootstrap confidence set. Its linearity test is the sup-Wald
statistic of Seo and Shin (2016) (`scalars["sup_wald"]`) with a bootstrap p-value `boots_p` that is
`-1` when the test was not run (`boot_reps=0`) and can be exactly `0` when no replication reaches the
sample statistic. `scalars` also holds `N` (units), `T`, `grid`, `trim`, `bs` (replications), `gamma`,
`L` (number of moment conditions) and `bandwidth` (kernel bandwidth of the covariance).

**What the result has.** Estimates, `se`, `cov`, `ci`, `gamma`, `seed`, `scalars`, `summary()`, and all
the table and export methods (`to_latex`, `to_html`, …, `compare`). Graphs, `diagnose()`,
`settings_log()`, `predict`, `augment` and `ci_table()` belong to `xtdpthresh` results only;
`pyx.plot` called on an `xthenreg` result raises a `SpecificationError` (key `plot_xthenreg`) that
says so.

**Against `xtdpthresh`.** Same moment conditions and weight matrices under `method="fd"`, so the same
estimates on the same grid; but the default trimming is 0.4 instead of 0.10, the threshold variable
is given differently (see the table above), `xthenreg` needs a strongly balanced panel and
has neither `fod`, `td`, `maxlag`, `collapse` nor `iv`, and strictly exogenous regressors are
instrumented by their levels where `xtdpthresh` uses their transformed values.

---

## 6. Reading the output

### The printed result

`print(res)` (or just `res` in a notebook) prints a report in the layout of `pyxtabond2` and
`pyxthreg`, 80 columns wide: the header (sample, model, options), the threshold with its confidence
interval, the threshold-effect test with its bootstrap critical values, the slopes of the three
regimes, and the diagnostic tests:

```
                        PyXtdpthresh Estimation Results
================================================================================
Dep. Variable:                  invest    Threshold var.:                   debt
Model:            Dyn. panel threshold    Threshold effect:                 jump
Method:                       Two-Step    Transformation:                     FD
Date:                 Wed, 04 Nov 2026    Group Variable:                   firm
Time:                         10:12:31    Time variable:                    year
No. Observations:                 6720    Lag Limits:                     (3, 8)
No. Groups:                        560    Collapse:                          Yes
Obs per group:                   12.00    Time effects:                       No
No. Instruments:                    25    Bootstrap B / seed:        299 / 12345
Covariance Type: Robust (joint, gamma)    Grid points:                       100
================================================================================

                       Threshold Estimates (Level = 95%)
================================================================================
Model                          Threshold            Lower CI            Upper CI
--------------------------------------------------------------------------------
Th-1                              0.4194              0.0122              0.5227
================================================================================

                   Threshold Effect Test (Bootstrap, B = 299)
================================================================================
Test                     Statistic     Prob      Crit10       Crit5        Crit1
--------------------------------------------------------------------------------
Linearity                   0.0087   0.0067      0.0052      0.0061       0.0085
================================================================================

                      Dynamic Panel Threshold Coefficients
================================================================================
                          coef  std err       z   P>|z|    [0.025    0.975]
--------------------------------------------------------------------------------
Lower regime  (debt <= 0.4194)
  L.invest              0.0433   0.2377   0.182  0.8556   -0.4227    0.5092
  cashflow             -0.0069   0.0752  -0.092  0.9269   -0.1543    0.1405
  tobin_q               0.0041   0.0069   0.583  0.5596   -0.0096    0.0177
  debt                 -0.1245   0.1006  -1.237  0.2162   -0.3217    0.0728
Change at the threshold
  _cons                -0.3922   0.1514  -2.590  0.0096   -0.6889   -0.0955 ***
  L.invest              1.5909   0.5956   2.671  0.0076    0.4235    2.7584 ***
  cashflow              0.3729   0.2524   1.477  0.1396   -0.1218    0.8675
  tobin_q               0.0107   0.0438   0.244  0.8073   -0.0752    0.0966
  debt                  0.3208   0.1717   1.868  0.0617   -0.0158    0.6573 *
Upper regime  (debt > 0.4194)
  L.invest              1.6342   0.5335   3.063  0.0022    0.5885    2.6799 ***
  cashflow              0.3660   0.2033   1.800  0.0718   -0.0325    0.7645 *
  tobin_q               0.0147   0.0426   0.346  0.7297   -0.0689    0.0983
  debt                  0.1963   0.1654   1.187  0.2353   -0.1279    0.5205
================================================================================
Significance: * p<0.10, ** p<0.05, *** p<0.01

                                Diagnostic Tests
================================================================================
Diagnostic Test                              Statistic                   P-value
--------------------------------------------------------------------------------
Arellano-Bond AR(1)                          z = -4.61            Pr > z = 0.000
Arellano-Bond AR(2)                          z = -0.33            Pr > z = 0.738
Hansen test of overid.                chi2(15) = 16.00         Pr > chi2 = 0.382
================================================================================
```

Reading it:

- **Header.** Two columns, as in `pyxtabond2`. `No. Observations` is the number of stacked equations
  (`e(N)`), `No. Groups` the units that contribute equations, `Lag Limits` the `maxlag` range (`.`
  is no upper limit), `Bootstrap B / seed` the number of draws and the seed (the one drawn when none
  was given, so the run can be repeated). The date and time are those of the estimation: printing the
  result again gives the same text.
- **Threshold Estimates.** The estimate and the confidence set of the threshold (grid bootstrap;
  its hull, see `res.ci_table()` for the segments) at the level of the estimation, `-` without bootstrap.
- **Threshold Effect Test.** The statistic and the bootstrap p-value of the linearity test (and of the
  continuity test when requested). `Crit10`, `Crit5` and `Crit1` are the bootstrap critical values at
  10, 5 and 1 percent: the `k`-th largest draw with `k = floor(size x (B + 1))`, so a statistic above
  `Crit5` has a p-value of at most 0.05. A size with too few draws shows `-`. For `xthenreg` the
  statistic is the sup-Wald and the critical values come from the supremum of each replication.
- **Coefficients.** Lower regime, change at the threshold and upper regime (the upper slopes with
  their own standard error). The interval is the normal one at `res.summary(level=...)`; stars mark
  p < 0.10, 0.05 and 0.01.
- **Diagnostic Tests.** Arellano-Bond AR(1) and AR(2) (first-difference residuals, joint with the
  threshold) and the Hansen test, as `z`/`chi2` and p-value. `xthenreg` has none of them and shows `-`.

`res.summary(lang="fr")` prints the same report in French. The numbers are those of `e()` and of
the validated objects; the critical values are not Stata objects (they are derived from the
bootstrap draws) and are shown for reading only.

Under `kink` the
change block holds only the change in the slope of `q`, and the upper block only the slope of `q`
above the threshold (`res.upper` is `None` when `q` is not a regressor).

### Numbers as objects

```python
print(res.params)  # Series indexed 'lower:cashflow', 'change:_cons', ... (e(b))
print(res.se)  # standard errors from the reported variance (sqrt of the diagonal of e(V))
print(res.cov.shape)  # e(V)
print(res.upper)  # upper-regime slopes and standard errors (e(b_upper), e(V_upper))
print(res.gamma, res.gamma_ci)
print(res.to_dataframe())  # estimate, se, z, p and the interval, indexed by (block, variable)
```

`res.gamma_ci` is the **hull** of the confidence set: the smallest and largest accepted candidate.
When the set has several segments (`res.scalars["ci_nseg"] > 1`), the range between them contains
rejected values, so look at `res.ci_table()` or `res.plot("ci")` and report the segments.

### `res.scalars`

A dictionary with the names of Stata's `e()` (`nan` when a value does not exist for the fit):

| Group | Names |
|---|---|
| Sample | `N` (equations), `N_units`, `N_clust`, `N_switch` (units whose regime changes within their equations at γ̂) |
| Instruments | `N_iv`, `N_iv_common`, `N_iv_dep`, `N_iv_dep_near`, `iv_dep_res` (columns dropped as common to all units or numerically dependent, and the largest residual of a dropped one) |
| Estimator | `gamma`, `obj` (criterion), `estimator_twostep` (0 = one-step fallback), `W1_fallback`, `level`, `joint_vce`, `vce_applied`, `wind_same_threshold`, `gamma_bw`, `q_nvals_bw`, `kink_refined` |
| Grid | `q_lo`, `q_hi` (trimming bounds), `grid_admitted` |
| Hansen | `hansen`, `hansen_df`, `hansen_p` |
| Serial correlation | `ar1`, `ar1_p`, `ar2`, `ar2_p`, `ar_joint`, `ar1_cond`, `ar2_cond`; `ar1_b0`, `ar1_T1`, `ar1_TT`, `ar2_b0`, `ar2_T1`, `ar2_TT` are the pieces of the statistics, kept for checking against Stata |
| Confidence set | `gamma_lo`, `gamma_hi`, `ci_nseg`, `ci_empty`, `ci_incomplete`, `ci_unresolved`, `boundary_warn` |
| Tests | `pval_lin`, `boot_linearity_valid`, `pval_cont`, `boot_continuity_valid`, `citest_gamma`, `citest_D`, `citest_crit`, `citest_accept`, `citest_p`, `citest_status`, `citest_draws`, `rseed` |

The tables behind the confidence set and the regimes:

```python
print(res.ci_table().head())  # gamma, statistic, critical, accepted, n_valid, status
print(res.regime_table())  # observations, units, share and the mean of each variable by regime
```

In `ci_table()` the `status` is 1 for a resolved test, 2 for accepted with a zero statistic, 3 for a
candidate that is not admissible, and 4 to 6 for unresolved ones. Statuses 3 to 6 are not
rejections.

### A reading order that works

1. **The sample.** `n_units`, `n_obs` and `n_instruments` (or `res.settings_log()`): were units
   dropped, and is the number of instruments small next to the number of units? Many instruments
   relative to units makes the Hansen test unreliable (Roodman 2009).
2. **The threshold.** γ̂ is a grid point (a point between grid points under `kink` or `refine`). It
   has no standard error; inference rests on the confidence set. Check the number of segments,
   `boundary_warn` (a bound at the edge of the confidence-set grid: 1 lower, 2 upper, 3 both),
   `ci_incomplete` (no interval is reported if some candidates are unresolved) and `ci_empty`.
3. **Linearity.** The test of H₀: δ = 0. A rejection says a threshold effect exists; it does not say
   where the threshold is. The p-value is (1 + R)/(1 + B).
4. **Hansen J.** A diagnostic, with `N_iv - k - 1` degrees of freedom. Its chi-square reference
   presumes regular identification, which fails near a continuous threshold. A large p-value does
   not show that the instruments are valid. With `center=False` it equals the statistic of
   `xtabond2` for the same instruments.
5. **AR(1) and AR(2).** AR(1) is expected to reject. A rejection of AR(2) indicates serial
   correlation in the errors, which invalidates the lagged instruments: reconsider `maxlag` or the
   specification (the second example of the Stata help file shows this with `maxlag(2 10)`).
6. **The fallbacks.** `estimator_twostep == 0`, `W1_fallback`, `vce_applied == 0` mean the command
   fell back to a simpler computation; `diagnose()` and the printed notes say which.
7. **Discrete `q`.** In the jump model, the joint variance and the AR statistics with γ̂ assume that
   `q` has a continuous density at the threshold. `q_nvals_bw` below 10 triggers a warning; the
   conditional statistics `ar1_cond` and `ar2_cond` do not use that assumption.

### `diagnose()` and `settings_log()`

`res.diagnose()` lists, in plain language, what deserves attention, each finding with a
recommendation and a level (warning or notice). It checks: the number of instruments against the
number of units; a Hansen test that rejects or sits suspiciously close to one, and an AR(2) test
that rejects; a threshold at an edge of the search grid; the confidence set (empty, incomplete,
touching the edge of its grid, several segments, very wide, or so narrow that the grid is too
coarse); a flat criterion profile or a distant rival threshold that fits almost as well; a small
regime or a threshold variable with few distinct values; first differences on an unbalanced panel;
the one-step and first-weight fallbacks; and the result of the continuity test when it was run. In
English or French: `res.diagnose(lang="fr")`.

`res.settings_log()` is the journal of what the estimation *really* used: the sample (units with
equations, dropped units), the model, the instruments kept and removed, the first-step weight, the
grid (requested, evaluated, admitted, range, smallest regime allowed), the variance estimator, the
bootstrap (type, draws, seed, points of the grid) and the package version. Keep it with the results.

```python
print(res.diagnose())
print(res.settings_log())
```

### Two diagnoses, read

*Serial correlation.* The same model with instruments from lag 2 (the third example of the Stata
help file):

```python
ar2 = full(maxlag=(2, 10))
print(ar2.diagnose())
```

```text
Diagnostic report: 1 warning(s), 1 notice(s)

[warning] The AR(2) test rejects the absence of second-order serial correlation in the differenced residuals (p = 0.013): lagged levels may not be valid instruments.
    Recommendation: Start the instruments one lag deeper (for example maxlag=(3, 8)) or add dynamics.
[notice] The confidence set of the threshold reaches the lower edge of the candidates: it is cut by the grid, not by the data.
    Recommendation: Widen the grid (lower trim) before reading the interval.
```

The warning is the one to act on: the instruments are suspect, so the estimate (γ̂ = 0.0121, near the
lower end of the grid) should not be reported as it stands. The notice says the confidence set
touches the edge of the candidates: it is cut by the grid, so do not read its end as a bound.

*Too many instruments.* The same model on the first 79 firms, without `collapse` and with every lag:

```python
small = pyx.xtdpthresh(
    df[df["firm"] < 80], "invest", **{**MODEL, **infer, "collapse": False, "maxlag": None}
)
print(small.n_units, small.n_instruments, small.scalars["estimator_twostep"])
print(small.diagnose())
```

```text
79 377 0.0
Diagnostic report: 2 warning(s), 3 notice(s)

[warning] 377 instruments for 79 units: with more instruments than units the Hansen test loses its power and the weight matrix is poorly estimated.
    Recommendation: Reduce the instruments: collapse=True or limit the lags with maxlag=(2, 4).
[warning] The estimate stays at one step: the second-step weight could not be used.
    Recommendation: Reduce the instruments (collapse=True or limit the lags with maxlag=(2, 4)); the Hansen test is not available at one step.
[notice] The confidence set of the threshold reaches the lower and upper edge of the candidates: it is cut by the grid, not by the data.
    Recommendation: Widen the grid (lower trim) before reading the interval.
[notice] The confidence set covers 100 % of the search grid: the threshold is weakly identified.
    Recommendation: Treat the threshold with caution; more units, a longer panel or a more variable debt would help.
[notice] The criterion profile is flat: 100 % of the thresholds are within 3.8 of the minimum.
    Recommendation: The estimated threshold is not sharply determined; compare it with the confidence set and plot(fit, 'profile').
```

Here the cause is upstream of everything else: with more instruments than units the second-step
weight could not be used, the command falls back to one step (`estimator_twostep` is 0, and there
is no Hansen test), and the confidence set is the whole grid. The five findings share one remedy, fewer
instruments.

---

## 7. Working with a result

**Predictions and residuals.** `res.predict(kind, frame)` returns a Series for the estimation data;
`kind` is `"residuals"`, `"xb"`, `"ar_residuals"` (the first-difference residuals used by the AR
tests; they equal `"residuals"` under FD) or `"regime"` (1 when `q > γ̂`, missing where `q` is). They
are the series computed during the estimation, not recomputed. They are the counterparts of
Stata's `predict, residuals | arresiduals | xb | regime`.

`res.augment(frame, kinds=…, prefix="", overwrite=False)` returns a copy of the frame with those
series as columns (default `kinds`: residuals, xb, regime), named after the series with `prefix` in
front. A column that already has the name is an error (`augment_exists`) unless `overwrite=True`.

```python
aug = res.augment(df, kinds=("residuals", "regime"))
print(aug["regime"].mean())
both = res.augment(df, prefix="m1_", overwrite=True)
print([c for c in both.columns if c.startswith("m1_")])
```

**Tables.** `res.to_latex(path)`, `to_html`, `to_markdown`, `to_text`, `to_csv`, `to_word` and
`to_excel` (the last two need `pip install "pyxtdpthresh[export]"`) write the academic table and
return its text. `res.table(**options)` returns the table object, and `pyx.compare([a, b, …],
model_names=[…])` puts several models side by side (`xthenreg` against `xtdpthresh`, FD against FOD,
jump against kink). The options, shared by all of them:

| Option | Effect |
|---|---|
| `statistic` | under each estimate: `"se"` (default), `"t"`, `"p"` or `"ci"` (interval at `level`) |
| `digits`, `star_levels`, `level` | decimals (3), significance levels (0.1, 0.05, 0.01), level of the intervals |
| `model_names`, `column_labels` | column names, and a group label above them |
| `covariate_labels`, `dep_var_label` | new names for variables (`{"cashflow": "Cash flow"}`; a `"block:variable"` key names one regime) and for the dependent variable |
| `keep`, `omit`, `order` | regular expressions selecting, dropping and ordering rows (against the name or `block:variable`) |
| `add_lines`, `notes` | extra lines under the coefficients (`[("Firm effects", ["Yes", "Yes"])]`) and notes |
| `title`, `label`, `font_size`, `single_row` | caption, LaTeX label, LaTeX size command, one line per estimate |
| `omit_stat` | diagnostic lines to drop (`"n_obs"`, `"hansen_p"`, …) |
| `lang` | `"en"` or `"fr"` for labels and the decimal sign |
| `full_output=True` | (of `res.table` and `res.to_*`) one more line per scalar of `e()` |

```python
fod = pyx.xtdpthresh(df, "invest", method="fod", bootstrap=False, **MODEL)
kink = pyx.xtdpthresh(df, "invest", kink=True, bootstrap=False, **MODEL)
table = pyx.compare([fast, fod, kink], model_names=["FD jump", "FOD jump", "FD kink"])
print(table.to_text())

custom = res.table(
    statistic="ci",
    digits=2,
    keep=["cashflow", "debt"],
    covariate_labels={"cashflow": "Cash flow"},
    add_lines=[("Firm effects", ["Yes"])],
    title="Investment",
)
print(custom.to_text())
res.to_latex("table.tex", full_output=True)
```

**Plots.** `res.plot(kind, path=None, lang=None, **options)` returns a matplotlib `Figure` and writes
it to `path` (`.png`, `.pdf` or `.svg`) when given. They are `xtdpthresh` results' methods (Section 5).

| `kind` | Draws | Options |
|---|---|---|
| `profile` | the GMM criterion over the grid of thresholds | |
| `ci` | the grid-bootstrap statistic against its critical value, accepted set shaded | |
| `linearity` | the bootstrap distribution of the linearity test | |
| `coef` | slopes of both regimes and their change, with intervals | `variables`, `free_scale` |
| `regimes` | the distribution of `q` and the share in each regime | `bins` (30), `trim` (0.01 cut from each tail) |
| `effect` | the effect of one regressor according to the regime | `var`, `trim` |
| `switch` | the share of the upper regime by period, and the units that change regime | |
| `instruments` | instrument columns by period against the number of units | |
| `residuals` | transformed residuals by period and the AR(1) and AR(2) tests | |

`ci` and `linearity` need the bootstrap. `robustness` takes a `RobustnessResult`; `coverage`,
`power` and `distribution` take Monte Carlo results (one, a list, or a `{name: result}` mapping)
through `pyx.plot(result, kind)`. Figures follow the style of the article and come in English or
French (`lang="fr"`).

```python
fig = res.plot("profile", path="profile.png")
res.plot("effect", var="cashflow", path="effect.png")
res.plot("regimes", bins=20, lang="fr", path="regimes_fr.png")
```

**Robustness.** `pyx.robustness(df, y, x, q=…, settings=…, product=False, **options)` re-estimates
the model on a set of settings and gathers the threshold with its confidence set, the slopes, the
linearity p-value and the diagnostics of each run. `settings` maps an option to the values to try
(default: `grid` 50/100/200, `trim` 0.05/0.10/0.15, `collapse`, `method`, `kink`); the options of the
call are the reference. By default one option changes at a time; `product=True` runs every
combination. All runs share one bootstrap seed, so the settings, not the draws, explain the
differences.

```python
rob = pyx.robustness(df, "invest", n_boot=99, grid_ci=40, seed=1, **MODEL)
print(rob.table[["gamma", "gamma_lo", "gamma_hi", "ci_nseg", "in_reference_ci"]])
print(rob.stability())  # share of the other runs whose threshold stays in the reference set

own = pyx.robustness(
    df,
    "invest",
    n_boot=49,
    grid_ci=20,
    seed=1,
    settings={"trim": [0.05, 0.15], "method": ["fod"]},
    product=True,
    **MODEL,
)
print(own.table.index.tolist())  # reference, then the combinations
rob.plot(path="robustness.png")
print(rob.coefficients().head())  # every slope of every run, with its standard error
```

`rob.table` has one row per run; `stability(use="segments")` counts a run as stable when its threshold
lies in an accepted segment of the reference set (`use="hull"` uses the hull). A run that fails is
kept in the table with its message and does not stop the analysis; only a failure of the reference
does. `rob.stargazer()` returns the table of all the runs side by side.

**Records.** `res.to_json(path)` writes a reproducible record of the fit with seven keys: `model`,
`specification` (variables), `options` (every option, as used), `scalars`, `ci_grid` (the inversion
table), `coefficients` and `environment` (versions of the package, Python, numpy, scipy, pandas and
the platform). `res.fit` holds everything the estimator computed, as frozen containers.

```python
import json

record = json.loads(res.to_json())
print(list(record), record["options"]["seed"])
```

---

## 8. Reproducibility, speed and memory

**Seeds.** Everything random in `xtdpthresh` comes from `seed`. The Stata generator is reproduced
(`set seed`, `uniform()`, `invnormal()`), so a seeded bootstrap draws the same weights as Stata. A
seed that is omitted is drawn and recorded in `res.seed`, `res.settings_log()` and `res.to_json()`.

**Global options.**

```python
# not run by the tests
pyx.set_options(lang="fr")  # messages, reports, figures in French
pyx.set_options(threads=4)  # threads of the matrix products (default: half the logical cores)
pyx.set_options(progress=True)  # progress line during long bootstraps, on standard error
with pyx.option_context(lang="fr"):
    ...  # temporary change
```

`set_options` returns the previous options. Numba kernels run on one thread, which is faster than
letting them compete with the matrix products.

**First call.** The Numba kernels are compiled the first time they are used and cached on disk.
`pyx.warmup()` pays that cost ahead of time (a few seconds, once per environment).

**Where the time goes.** The bootstrap is 80–92 % of a full run. For a quick look at a
specification, estimate with `bootstrap=False`; increase `n_boot` and `grid_ci` for the final run.
With many instruments the cost is in one matrix product that already runs close to the speed of
the machine; `collapse` and `maxlag` shrink it.

**Memory.** Memory grows with the number of equations times the number of raw instrument columns. A
note is issued before a fit expected to need more than 2 GB, and a warning above 8 GB; `collapse`,
`maxlag` and fewer draws reduce it.

---

## 9. Simulation and Monte Carlo

`pyx.simulate_panel(design, n, t, seed=…)` draws a panel from a named design and returns it in
long form (`id`, `t`, `y`, `q`, …), ready for the estimators; `pyx.monte_carlo(design, n, t, …)`
replicates the estimation and summarises bias, coverage, size and power.

| Design | Source | What it is |
|---|---|---|
| `gong_seo` | Gong and Seo (2026), §5 | `q` is an AR(1) correlated with the errors, predetermined |
| `gong_seo_endog` | Gong and Seo (2026) | the same with `q` weakly endogenous |
| `linear` | Gong and Seo (2026) | no threshold effect: the design for the **size** of the linearity test |
| `seo_shin_jump`, `seo_shin_cont` | Seo and Shin (2016), §6 | self-exciting, `q = y(t-1)`; discontinuous (eq. 16) and continuous (eq. 17) |
| `seo_shin_jump_common`, `seo_shin_cont_common` | Seo and Shin (2016), §6.1 | intercept fixed across regimes |
| `seo_shin_exogenous`, `seo_shin_exogenous_common` | Seo and Shin (2016), App. A.4 | `q ~ U[-1, 1]`, independent of the errors |

**`simulate_panel(design, n, t, *, seed, burn=50, unbalanced=0.0, min_obs=3, **changes)`** returns
a frame with the columns `id`, `t` (1 to `t`), `y` and `q`; the panel is a function of `seed`
alone. `burn` periods are simulated and discarded first, so that `q` and `y` are close to their
stationary behaviour. `unbalanced` is the share of observations dropped at random (the remaining
values do not change), and a unit left with fewer than `min_obs` observations is removed.
`**changes` override any parameter of the design (`gamma`, `sigma`, `rho`, `rho_eu`, `beta_y`,
`delta0`, …) and `jump=` sets the jump of the regression function at the threshold (`0` is a kink).
`resolve_design(name, **changes)` returns the resulting `Design`: its `truth` holds the true
coefficients (named like the estimates, plus `gamma`) and `arguments()` the call that estimates it
(the roles of the variables and `collapse`).

**`monte_carlo(design, n, t, *, reps=200, seed, workers, alpha=0.05, shifts=(0.10, 0.25, 0.50),
simulation=None, **options)`** replicates the estimation. `simulation` is a dictionary of generator
parameters (`jump`, `unbalanced`, `burn`, any parameter of the design); `options` are `xtdpthresh`
options (`n_boot`, `grid`, `grid_ci`, `level`, …) and override the design's arguments; `alpha` is
the level of the linearity test; `shifts` are the `c` of the alternatives `γ + c` whose rejection
rate is reported. The result keeps one row per replication (`to_dataframe()`, with `status` and
`error` for the replications that failed) and answers:

| Method | Returns |
|---|---|
| `estimates()` | bias, RMSE and coverage of the threshold and of every slope, by parameter |
| `threshold_coverage()` | coverage of the true threshold by the confidence set (segments) and by its hull, and the share of incomplete sets |
| `linearity()` | rejection rate of the linearity test: the power with a threshold effect, the size under design `linear` |
| `power()` | rejection rate of `γ = γ₀ + c`, `c = 0` included (the size of the threshold test) |
| `summary()` | a short text report |

```python
panel = pyx.simulate_panel("gong_seo", 200, 6, seed=3)
print(panel.head(3))

from pyxtdpthresh.extras.simulation import resolve_design

design = resolve_design("gong_seo", gamma=0.5, jump=0.2)
gaps = pyx.simulate_panel(design, 100, 6, seed=3, burn=20, unbalanced=0.15, min_obs=3)
print(len(gaps), gaps["id"].nunique(), design.truth["gamma"], round(design.jump, 2))
gap_fit = pyx.xtdpthresh(gaps, "y", id="id", time="t", bootstrap=False, **design.arguments())
print(round(gap_fit.gamma, 3), gap_fit.n_obs)

mc = pyx.monte_carlo("gong_seo", 100, 5, reps=4, seed=11, workers=1, n_boot=49, grid_ci=20)
print(mc.threshold_coverage())  # coverage of the true threshold by the set and by its hull
print(mc.linearity())  # rejection rate: the power here, the size under design "linear"
print(mc.power())  # rejection rate of gamma + c, c = 0 included

mc2 = pyx.monte_carlo(
    "gong_seo",
    100,
    5,
    reps=4,
    seed=11,
    workers=1,
    n_boot=49,
    grid_ci=20,
    alpha=0.10,
    shifts=(0.2, 0.4),
    simulation={"jump": 0.5, "unbalanced": 0.1},
)
print(mc2.power())
print(mc2.estimates().round(3))
```

The coverage and power figures of four replications mean nothing; the tables in `docs/montecarlo/` use
hundreds. The calls are the same.

The experiment is a function of `seed` alone, whatever `workers` is. `workers=None` uses
`min(cpu_count, reps)` processes of one thread each; `workers=1` runs in the calling process.

**On Windows, where worker processes are started by spawning, a script that runs replications in
several processes must be a real file with the usual guard:**

```python
# not run by the tests
import pyxtdpthresh as pyx

if __name__ == "__main__":
    mc = pyx.monte_carlo("gong_seo", 400, 6, reps=200, seed=1, workers=4)
    print(mc.summary())
```

The worker processes re-import the main file; without the guard each one would start its own
experiment, and a script read from standard input (`python -`) has no file to re-import: the
replications fail. `examples/04_monte_carlo.py` is a complete case.

The bundled results of larger experiments, and what they say about the agreement with the papers
(coverage agrees; the power to reject shifted thresholds is lower than Table 2 of Gong and Seo,
cause not established), are in `docs/montecarlo/`.

---

## 10. Errors and warnings

**Exceptions** all derive from `PyxdpthreshError`:

| Class | Raised when |
|---|---|
| `SpecificationError` (also a `ValueError`) | the call breaks a rule of the Stata command; `.stata_code` is Stata's return code (198 for most option errors) and `.key` names the rule |
| `DataError` (also a `ValueError`) | the data cannot be used: repeated (unit, time) pairs, missing keys, no usable observation, an unbalanced panel for `xthenreg`, a point estimation that finds no valid solution |
| `NumericalError` | a computation fails numerically |

All of them derive from `pyx.PyxdpthreshError` and are importable from the package
(`pyx.SpecificationError`, `pyx.DataError`, `pyx.NumericalError`). `SpecificationError` and
`DataError` are also `ValueError`s.

```python
try:
    pyx.xtdpthresh(df, "invest", grid=5, bootstrap=False, **MODEL)
except pyx.SpecificationError as error:
    print(error.stata_code, error.key)  # 198 opt_grid
    print(error)
```

The return codes match the command's. On 19 hostile inputs (minimal panels, a constant, binary or
rare threshold variable, an empty regime, duplicated regressors, fewer units than instruments, a
null outcome) the package returns the same code as Stata in all 19.

**"No threshold admitted a valid GMM solve"** (a `DataError`) means that at every candidate
threshold the estimator could not be computed. The usual causes are too few units or periods, more
instruments than the data can support, a threshold variable with too little variation, or a regime
that is too small. Remedies: `collapse=True`, a tighter `maxlag`, a larger `trim`.

**Warnings** are `pyx.PyxdpthreshWarning` (a `UserWarning`), so the `warnings` module controls them,
and `warn=False` silences most of them at the source. They cover: many instrument columns, memory,
a kink with `q` not among the regressors, `refine` not applied after a one-step fallback, a Windmeijer correction that could not be applied,
and the legacy `coef_boot`.

---

## 11. What differs from Stata

| Stata | Python |
|---|---|
| `xtset firm year` | `id="firm", time="year"`, or a `MultiIndex`, or `from_stata` |
| `if` / `in` | `where=`; no `in` |
| `e(b)`, `e(V)`, `e(N)`, … | `res.params`, `res.cov`, `res.scalars["N"]`, … |
| `ereturn list, all` (hidden results) | `res.scalars` includes the hidden ones that are kept for checking |
| `predict, residuals \| arresiduals \| xb \| regime` | `res.predict("residuals" \| "ar_residuals" \| "xb" \| "regime", frame)` |
| `estimates store` / `esttab` | the result objects, `pyx.compare([...])` and the `to_*` methods |
| `set level` | `level=` of the call (95 by default) |
| `rseed(#)`, not restored after the command | `seed=`; no global state is changed |
| `verbose`, `exportgmm` | accepted with no effect |
| `xthenreg … h_0()` | `xthenreg(…, h_0=)` |
| a missing value in `if` counts as true | counts as false |
| Mata matrices left in memory | frozen containers under `res.fit` |

What the package adds: the result classes with tables, plots and a JSON record; `diagnose()` and
`settings_log()`; `robustness()`; the simulation toolkit; bundled data; English and French
messages. What it does not change: the estimators, the bootstrap draws, the tests and their
conventions, which are checked against Stata 17 MP to four decimals.
