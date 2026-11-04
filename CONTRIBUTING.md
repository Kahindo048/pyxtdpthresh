# Contributing

The full design is in `ARCHITECTURE.md` (structure, dependency rules, 20 coding rules) and the work plan in `PLAN.md`. The essentials:

## Set up

```bash
python -m venv .venv && .venv\Scripts\activate
pip install -e ".[dev]"
pre-commit install
```

## Before every commit

```bash
ruff check src tests && ruff format src tests
mypy
lint-imports
pytest -m "not stata"
```

## Rules in one screen

1. **Layers import downward only** (enforced by `lint-imports`). Numba only in `kernels/`; matplotlib, python-docx and openpyxl only in `extras/`, imported lazily.
2. **Exactness first**: `float64`, no `fastmath`, tolerances only in `core/tolerances.py` with their Stata origin.
3. **Ported code carries its provenance**: `# Stata: function (file:line)`; deliberate quirks are marked `# STATA-QUIRK:` with the reason. `python tools/ported_functions.py check` (and `tests/unit/test_provenance.py`) verify that each reference points to a real file, line and function; after a change in the Stata files run `python tools/ported_functions.py manifest`, and `inventory` to refresh `docs/ported_functions.md`.
4. **Every Numba kernel has a NumPy reference version** in `kernels/reference/` and an equivalence test.
5. **Randomness** only through an explicit `numpy.random.Generator`.
6. **Errors** derive from `PyxdpthreshError`; no `print` outside explicit rendering of a result.
7. **Messages** live in `_i18n.py` in French and English.
8. Commits follow the conventional format: `feat:`, `fix:`, `perf:`, `test:`, `docs:`, `refactor:`.

## Validation against Stata

`validation/run_stata.ps1` runs Stata 17 MP in batch **from PowerShell only**. Reference results are frozen in `tests/golden/golden_master.json`, so the test suite runs without Stata (marker `stata` is for local runs).

## Docstrings of the public API

Every name of `pyxtdpthresh.__all__` (and every public method of its classes) has a numpy-style docstring: a summary,
a `Parameters` entry for each parameter, a `Returns` section, and an `Examples` section for the main functions (the
examples are run by `tests/unit/test_public_docstrings.py`, so their output must be exact). `python tools/check_docstrings.py`
lists the gaps.

## Releasing

`python tools/check_install.py` builds the wheel and the sdist, runs `twine check`, verifies what each holds (the
licence and the notice in both, no tests in the wheel), installs the wheel in a new environment and runs the model of the
help file there. Run it before every release (it needs network access for the dependencies).
