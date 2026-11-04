# pyxtdpthresh

Dynamic panel threshold models in Python. The package ports two Stata commands,
**`xtdpthresh`** (Nguyen and Lai 2026) and **`xthenreg`** (Seo, Kim and Kim 2019), checks every
output against Stata 17 MP, and adds what Stata does not have: a result object that prints, exports
and plots itself, plain-language diagnostics, a robustness check, and a simulation toolkit.

> **Status: alpha (0.0.1).** The estimators, inference and tools below are implemented and tested.
> Install it from PyPI with `pip install pyxtdpthresh`.

## Install

```bash
pip install pyxtdpthresh                               # or: pip install .  from a checkout
pip install "pyxtdpthresh[export]"                     # Word and Excel tables (python-docx, openpyxl)
python -c "import pyxtdpthresh; pyxtdpthresh.warmup()" # once: compiles the Numba kernels (a few seconds)
```

Python 3.10 or later. The kernels are compiled by Numba the first time they are used and cached on
disk; `warmup()` pays that cost once, ahead of time (without it the first fit takes several
seconds more).

## Quick start

The model of Seo and Shin (2016, section 7): investment on its lag, cash flow, Tobin's q and
leverage, all slopes changing at a leverage threshold, with the three regressors endogenous. This is
the main example of the help file of `xtdpthresh`.

```python
import pyxtdpthresh as pyx

df = pyx.load_dataset("invest")  # Hansen (1999): 565 firms, 1973-1987
df = df[~df["firm"].isin([137, 391, 407, 488, 538])]  # the five extreme firms of Seo and Shin

res = pyx.xtdpthresh(
    df,
    "invest",
    q="debt",
    endogenous=["cashflow", "tobin_q", "debt"],
    maxlag=(3, 8),
    collapse=True,
    id="firm",
    time="year",
    seed=12345,
)
print(res)  # estimates by regime, threshold and its interval, tests
res.to_latex("table.tex")  # also to_html, to_markdown, to_word, to_excel, to_csv
res.plot("regimes", path="regimes.png")
print(res.diagnose())  # what deserves attention, in plain language
```

On this panel the call takes about two seconds and prints a report like those of `pyxtabond2` and
`pyxthreg` (abridged here):

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
...
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
...

                                Diagnostic Tests
================================================================================
Diagnostic Test                              Statistic                   P-value
--------------------------------------------------------------------------------
Arellano-Bond AR(1)                          z = -4.61            Pr > z = 0.000
Arellano-Bond AR(2)                          z = -0.33            Pr > z = 0.738
Hansen test of overid.                chi2(15) = 16.00         Pr > chi2 = 0.382
================================================================================
```

The linearity test rejects, while the confidence set of the threshold is wide and made of four
separate intervals; `res.diagnose()` says so and recommends reporting the segments, not only their
hull.

## What is in the package

| | |
|---|---|
| **Estimators** | `xtdpthresh(...)`: first differences or forward orthogonal deviations, unbalanced panels, endogenous, predetermined and exogenous regressors, external instruments, time effects, jump or kink. `xthenreg(...)`: the balanced-panel estimator of Seo, Kim and Kim with its sup-Wald linearity test. |
| **Inference** | Grid-bootstrap confidence set of the threshold (wild or unit resampling, with all its segments), bootstrap linearity and continuity tests, a test of a given threshold (`gamma_test`), coefficient bootstrap, Windmeijer-corrected and joint variances, Hansen and AR(1)/AR(2) tests. |
| **The result** | `res.params`, `res.se`, `res.cov`, `res.gamma`, `res.gamma_ci`, `res.scalars` (the names of Stata's `e()`), `res.summary()`, `res.predict(...)`, `res.augment(df)`, `res.to_json()`. |
| **Tables** | `res.to_latex()` and friends; `pyx.compare([a, b])` puts models side by side, `xthenreg` against `xtdpthresh`, FD against FOD, jump against kink. |
| **Plots** | `res.plot(kind)` with `profile`, `ci`, `linearity`, `coef`, `regimes`, `effect`, `switch`, `instruments`, `residuals`; figures in English or French. |
| **Diagnosis** | `res.diagnose()`, `res.settings_log()` (the settings really used: sample, instruments kept and removed, grid, seed). |
| **Robustness** | `pyx.robustness(df, ...)` re-estimates over grids, trimmings, instrument sets, FD/FOD and jump/kink and reports how stable the threshold is. |
| **Simulation** | `pyx.simulate_panel(design, n, t)` for the designs of Gong and Seo (2026) and Seo and Shin (2016); `pyx.monte_carlo(...)` for bias, coverage, size and power, in parallel and reproducible. |
| **Data** | `pyx.load_dataset("invest")`, `pyx.from_stata("file.dta")` (reads the `xtset` variables of the file). |

Messages, reports and figures are available in English and French (`pyx.set_options(lang="fr")`).

## Validation

The aim is that every output equals what Stata 17 MP gives, to four decimals (absolute difference
at most 5e-5, or relative difference at most 1e-6). The check is automated and runs without Stata:

* the results of the real Stata commands are frozen in `tests/golden/` (one file per component:
  data, design, instruments, search, variance, bootstrap, linearity, tests, prediction, simulated
  panels) and the package is compared with them case by case;
* the random numbers of Stata (`set seed`, `uniform()`, `invnormal()`) are reproduced, so that a
  seeded bootstrap draws the same weights as Stata;
* hostile inputs (minimal panels, a constant, binary or rare threshold variable, an empty regime,
  duplicated regressors, fewer units than instruments, a null outcome) return the same Stata return
  code as the command in 19 of 19 cases, and the same estimates where both succeed;
* the eight examples of the help file of `xtdpthresh` are run in both programs with the default
  options, object by object (`docs/help_examples.md`).

Appendix B of `docs/user_guide.pdf` gives the largest deviation from Stata by block, by object and by
case (its LaTeX is written by `python -m validation.report`; `--record` first re-runs the golden tests
to record the deviations).

`pytest` runs about 2100 tests; line and branch coverage is 91.5 %. `docs/ported_functions.md` lists
the Stata functions that are ported and where; every ported function cites its Stata source
(`# Stata: function (file.ado:line)`) and a test checks the citations.

## Speed

The bootstrap, which is most of the time, is evaluated for all draws and candidate thresholds by
batched matrix products from sufficient statistics, and the small kernels are compiled by Numba.
Wild bootstrap with 299 draws and a grid of 100 candidate thresholds, Python against Stata 17 MP on
the same machine, measured one run after the other (`docs/performance/STATA.md`):

| Panel | Stata | pyxtdpthresh | Ratio |
|---|---:|---:|---:|
| Hansen, 565 firms x 15 years, 117 instruments | 37 s | 3.3 s | 11.6x |
| 2,000 firms x 8 years | 19 s | 1.0 s | 18x |
| 10,000 firms x 8 years | 80 s | 2.7 s | 29x |

With many instruments the time is in one matrix product that already runs close to the speed of the
machine, so the ratio is smaller; the unit-resampling bootstrap of Gong and Seo was measured about 13 times
faster than Stata's (150 firms, 99 draws; not a paired measurement). Times on a given machine vary by up to a factor of two from one moment to the
next, which is why the comparison is paired. `pyx.set_options(threads=n)` bounds the BLAS threads
(default: half of the logical cores).

## Reproducibility

Without `seed=`, a seed is drawn and recorded: `res.seed` replays the run exactly, and it is in
`res.settings_log()` and `res.to_json()`.

## Limits worth knowing

* One threshold and two regimes, as in the theory the commands rely on.
* The default bootstrap is the wild bootstrap of the command; the unit-resampling bootstrap
  (`boot_type="unit"`) needs the two-step estimator.
* In Monte Carlo experiments built on the designs of Gong and Seo (2026) the coverage of the
  threshold agrees with the paper, but the rejection rate of shifted thresholds (power) is lower
  than their Table 2; the cause is not established (`docs/montecarlo/`). With the self-exciting
  designs of Seo and Shin (2016) the dispersion of the estimated threshold is larger than in their
  tables; the extreme estimates are identical to Stata's, so they come from the estimator.
* Memory grows with the number of equations times the number of raw instrument columns; a note is
  issued before a fit that is expected to need more than 2 GB (a warning above 8 GB).

## Documentation

* `docs/` has the performance and Monte Carlo reports, the list of ported Stata functions and the
  gallery of figures (`docs/galerie/`); `examples/` has runnable scripts.
* `docs/user_guide.md` is the user guide: every option with its Stata name, and how to read the
  output. `docs/user_guide.pdf` is the same guide in PDF, with the methodological note (the algebra, the
  algorithms, the conventions of Stata that are reproduced, the validation journal) as Appendix A and the validation against Stata 17 as Appendix B; it is
  built from `docs/user_guide.md`, `docs/methodological_note.tex` and `docs/validation_appendix.tex` by
  `tools/build_guide_pdf.py`.
* `ARCHITECTURE.md` and `CONTRIBUTING.md` describe the layers, the coding rules and the checks.

## References

* Seo, M. H., and Shin, Y. (2016). Dynamic panels with threshold effect and endogeneity. *Journal of Econometrics* 195: 169-186.
* Seo, M. H., Kim, S., and Kim, Y.-J. (2019). Estimation of dynamic panel threshold model using Stata. *Stata Journal* 19: 685-697.
* Gong, W., and Seo, M. H. (2026). Bootstraps for dynamic panel threshold models. *Journal of Econometrics* 253: 106153.
* Nguyen, D. C., and Lai, N. D. (2026). xtdpthresh: Dynamic panel threshold regression for unbalanced panels. SSRN 6619058.
* Hansen, B. E. (1999). Threshold effects in non-dynamic panels. *Journal of Econometrics* 93: 345-368 (the investment panel).

## License

MIT. See `LICENSE`. The package reproduces the programs `xthenreg` (Seo, Kim and Kim 2019) and
`xtdpthresh` (Nguyen and Lai 2026); `NOTICE.md` says whose work it builds on, what is taken from the
programs (their algorithms and conventions, not their code) and quotes their disclaimer.
