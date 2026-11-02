# pyxtdpthresh

Dynamic panel threshold models in Python: ports of Stata's **`xthenreg`** (Seo, Kim and Kim 2019) and **`xtdpthresh`** (Nguyen and Lai 2026), validated against Stata to four decimals and built for speed (Numba).

> **Status: alpha, under construction.** The package skeleton, tooling and validation harness are in place; the estimators are being ported in the order of the work plan. Nothing is published yet.

## Goals

* **Exactness**: every output is compared with Stata 17 MP; agreement to four decimals.
* **Speed**: threshold search on the whole grid from sufficient statistics (cumulative sums), bootstraps by batched matrix products, Numba kernels.
* **Simple to use**: one function call, readable summaries, publication-ready tables in the style of R's `stargazer`, automatic plots and plain-language diagnostics.

## Installation (development)

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -e ".[dev]"
pytest
```

## Layout

The package follows a layered architecture enforced by `import-linter`: see `ARCHITECTURE.md` (layers 0 to 8, dependency rules and 20 coding rules) and `PLAN.md` for the work plan and progress.

## References

* Seo, M. H., and Shin, Y. (2016). Dynamic panels with threshold effect and endogeneity. *Journal of Econometrics* 195: 169-186.
* Seo, M. H., Kim, S., and Kim, Y.-J. (2019). Estimation of dynamic panel threshold model using Stata. *Stata Journal* 19: 685-697.
* Gong, W., and Seo, M. H. (2026). Bootstraps for dynamic panel threshold models. *Journal of Econometrics* 253: 106153.
* Nguyen, D. C., and Lai, N. D. (2026). xtdpthresh: Dynamic panel threshold regression for unbalanced panels. SSRN 6619058.

## License

MIT. See `LICENSE`.
