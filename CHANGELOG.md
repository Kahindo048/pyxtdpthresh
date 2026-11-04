# Changelog

All notable changes are recorded here. The project follows [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.0.1] - 2026-11-04

First release.

### Changed
- `print(result)` and `result.summary()` now give a report in the layout of `pyxtabond2` and `pyxthreg`, 80 columns wide: title and two-column header (sample, model, options, date and time), threshold with its interval, threshold-effect test with the bootstrap critical values at 10, 5 and 1 percent, slopes by regime with stars, and the Arellano-Bond and Hansen tests. In English and French. The numbers are unchanged; `summary(model, when=)` sets the date printed.

### Fixed
- Column names with accents or other Unicode letters (`"investissé"`) are accepted, as in Stata 14 and later.
- An infinite value in a variable is treated as missing, as Stata does, and now gives a warning that names the column and the count; it used to be dropped silently.

### Added
- Stress tests: 120 random panels and calls run in Stata and in the package (`validation/stress.py`, `validation/stress_cases.py`, golden test): 97 agree on every object, 21 are refused by both with the same return code, 2 degenerate ones are decided by rounding noise; plus invariance, repeatability and input-container checks without Stata.
- `xthenreg(..., h_0=)`, the bandwidth multiplier of the Stata option `h_0()`; checked against Stata 17 with `h_0(3)` and `h_0(0.7)` (cases c7 and c8).
- The exceptions and the warning are public: `pyx.PyxdpthreshError`, `SpecificationError`, `DataError`, `NumericalError`, `PyxdpthreshWarning`.
- `pyx.plot` accepts the result objects, and refuses the result of `xthenreg` with a clear message (`SpecificationError`, key `plot_xthenreg`) instead of an `AttributeError`.
- Estimators `xtdpthresh` and `xthenreg` with result classes (`XtdpthreshResult`, `XthenregResult`): summary, tables (LaTeX, HTML, Markdown, Word, Excel), plots, diagnostics, settings log, prediction.
- Grid-bootstrap confidence set of the threshold (wild and unit resampling), linearity, continuity and threshold tests, coefficient bootstrap.
- Robustness check, simulation designs of Gong-Seo (2026) and Seo-Shin (2016), parallel reproducible `monte_carlo`, bundled Hansen (1999) panel, `from_stata`.
- `warmup()`, the `threads` option (BLAS threads; the Numba kernels run on one thread), a memory warning before very large fits, speed guards (`pytest -m bench`).
- Provenance checker (`tools/ported_functions.py`), `docs/ported_functions.md`, edge cases validated against Stata 17 (19 of 19 same return code).
- The user guide in PDF and LaTeX (`docs/user_guide.pdf`, `docs/user_guide.tex`, built by `tools/build_guide_pdf.py`) with the methodological note as Appendix A (`docs/methodological_note.tex`): algebra, cumulative-sum algorithm, variances, bootstrap, comparison with Algorithm 1 of Gong and Seo, the conventions of Stata that are reproduced, the validation journal and the map of the Stata functions.
- The eight examples of the help file of `xtdpthresh`, run in Stata 17 and in Python with the default options, side by side in `docs/help_examples.md` (`validation/help_examples.py`, golden test): every object agrees, largest deviation 2.1e-7.
- Continuous integration (`.github/workflows/ci.yml`): lint, types, layers, provenance and docstring checks; the tests without Stata on Ubuntu and Windows (Python 3.10 and 3.12); the build of the wheel and the sdist and a clean install.
- Docstrings of the public API: every parameter and return value described, and an `Examples` section run by the tests for the main functions; `tools/check_docstrings.py` audits them.
- `NOTICE.md` (credits: the authors of `xthenreg` and `xtdpthresh`, the papers, the bundled data, the disclaimer of the original programs) and a fuller `CITATION.cff`.
- Packaging: the licence and the notice are in the wheel and the sdist (they were left out before), SPDX license expression, `MANIFEST.in`, `tools/check_install.py` (build, `twine check`, clean-environment install and run).
- The validation against Stata 17 as Appendix B of the user guide (`docs/validation_appendix.tex`): the largest deviation from Stata 17 by block, by object and by case over every comparison of the golden tests, with the one declared looser tolerance (a matrix of condition number 10^13) listed apart. `python -m validation.report`; the golden tests record their deviations when `PYX_RECORD_DEVIATIONS` is set.
- Provenance citations for 19 more Stata functions (86 of the 101 are cited).
- Runnable examples in `examples/` and a user guide, `docs/user_guide.md` (every option with its Stata name, how to read the output); the code of the README and of the guide is run by the tests.
- Package skeleton in `src/` layout with the layered architecture and import-linter contracts.
- Layer-0 modules: global options, exception hierarchy with Stata return codes, French/English message catalogue, type aliases.
- Tooling: ruff, mypy (strict on the computational layers), pytest markers, coverage, pre-commit.
- Stata validation harness (`validation/`): PowerShell runner for Stata 17 MP.
