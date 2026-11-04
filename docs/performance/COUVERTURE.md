# Coverage and packaging measurements (K.1.5, K.4.4)

Measured with `pytest --cov` (line and branch) on the full suite (2114 tests), then with `python -m
build` and a clean-environment install of the wheel.

## Coverage

Total: **91.5 %** (94.1 % of lines). Target of the plan: 85 % on the estimation modules.

| Package | Statements | Coverage |
|---|---:|---:|
| core | 359 | 97.0 % |
| data | 404 | 95.3 % |
| instruments | 335 | 95.5 % |
| inference | 184 | 96.9 % |
| models | 2520 | 94.4 % |
| extras | 2516 | 96.9 % |
| results, api, transforms, root | 410 | 98–100 % |
| kernels | 668 | 54.4 % |

The low figure of `kernels` is a measurement artefact: `coverage` cannot trace code compiled by Numba, so
the bodies of the jitted kernels count as never executed, although the equivalence tests run them (against
their NumPy references, with and without `NUMBA_DISABLE_JIT=1`). Outside the compiled bodies the lowest
estimation modules are `models/xtdpthresh/variance.py` (80 %) and `bootstrap.py` (91 %).

## Packaging

* `python -m build` produces `pyxtdpthresh-0.0.1-py3-none-any.whl` (392 kB, 138 files) and the sdist (335 kB).
  The wheel holds `py.typed` and `invest.csv`; no caches, tests or validation files.
* **Gaps to fix before publishing:** the wheel carries no `LICENSE` file (`license-files = []`), and the
  sdist contains neither `LICENSE`, `tests/`, `docs/` nor `CHANGELOG.md` (no `MANIFEST.in`); the `License ::`
  classifier is deprecated in favour of an SPDX expression (setuptools warning).
* Clean install (new virtual environment, wheel only, run from another directory with `python -I`):
  numpy 2.5.4, scipy 1.18.1, pandas 3.1.0, numba 0.68.1, matplotlib 3.11.2 were resolved; `import pyxtdpthresh`
  loads none of numba, pandas or matplotlib; the bundled data set loads; `xtdpthresh` returns the same
  estimates as the development environment (0.3911, 0.0833, 0.0766, -0.3736, -0.0928); `to_latex` and `plot`
  work; `to_word` without `python-docx` raises a clear error naming `pip install pyxtdpthresh[export]`.
* First fit in a clean install: 7.8 s (the Numba cache is empty: compilation). `pyxtdpthresh.warmup()` pays
  that cost once, ahead of time (see `PREMIER_APPEL.md`).
