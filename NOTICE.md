# Notice and credits

pyxtdpthresh is released under the MIT License (see `LICENSE`). It is an implementation in Python
of methods that other people designed and of two Stata programs that other people wrote. This
notice says whose work it builds on and what is, and is not, copied from it.

## The programs this package reproduces

**`xthenreg`** — dynamic panel threshold regression with endogeneity.

* Authors: Myung Hwan Seo (Seoul National University), Sueyoul Kim (University of Maryland) and
  Young-Joo Kim (Hongik University).
* Reference: Seo, M. H., S. Kim, and Y.-J. Kim. 2019. Estimation of dynamic panel threshold model
  using Stata. *Stata Journal* 19(3), article st0573. https://doi.org/10.1177/1536867X19874243
* The help file of the program carries a disclaimer (provided "as is", without warranty); it is
  reproduced under "Disclaimer of the original programs" below.

**`xtdpthresh`** (version 0.9.38) — dynamic panel threshold regression for unbalanced panels, with
endogenous regressors and continuity-robust inference.

* Authors: Duy Chinh Nguyen (International University, Vietnam National University Ho Chi Minh
  City) and Nhat Duy Lai (Saigon University, corresponding author).
* Reference: Nguyen, D. C., and N. D. Lai. 2026. xtdpthresh: Dynamic panel threshold regression for
  unbalanced panels, with endogenous regressors and continuity-robust inference. SSRN Working Paper
  6619058. https://ssrn.com/abstract=6619058

## What is taken from them

* **Algorithms and conventions.** The package reproduces what the two programs compute, including
  their conventions (grid, trimming, instruments, weight matrices, variances, bootstrap and the
  random numbers of Stata), so that its results agree with theirs to four decimals. The source
  comments cite the function and line of the Stata program that each routine follows
  (`# Stata: function (file.ado:line)`); `docs/ported_functions.md` lists them.
* **Reference results.** The numbers the package is compared with were produced by running the
  original programs in Stata 17 MP and are stored in `tests/golden/`. Those files hold results
  (numbers), not program text.
* **Not distributed.** The `.ado`, `.mata` and `.sthlp` files of the two programs are not part of
  this package. The comparison tests that rerun them need a Stata installation that has them and are
  not run by users of the package.
* **Wording.** The names of the options and of the stored results follow those of the programs so that
  a Stata user finds the same names; `docs/user_guide.md` gives the correspondence.

## The methods

* Seo, M. H., and Y. Shin. 2016. Dynamic panels with threshold effect and endogeneity. *Journal of
  Econometrics* 195: 169-186.
* Gong, W., and M. H. Seo. 2026. Bootstraps for dynamic panel threshold models. *Journal of
  Econometrics* 253: 106153.
* Hansen, B. E. 1999. Threshold effects in non-dynamic panels: Estimation, testing, and inference.
  *Journal of Econometrics* 93: 345-368.
* Hansen, B. E. 1999. The grid bootstrap and the autoregressive model. *Review of Economics and
  Statistics* 81: 594-607.
* Arellano, M., and S. Bond. 1991. Some tests of specification for panel data. *Review of Economic
  Studies* 58: 277-297.
* Arellano, M., and O. Bover. 1995. Another look at the instrumental variable estimation of
  error-components models. *Journal of Econometrics* 68: 29-51.
* Windmeijer, F. 2005. A finite sample correction for the variance of linear efficient two-step GMM
  estimators. *Journal of Econometrics* 126: 25-51.
* Mammen, E. 1993. Bootstrap and wild bootstrap for high dimensional linear models. *Annals of
  Statistics* 21: 255-285.
* Roodman, D. 2009. How to do xtabond2: An introduction to difference and system GMM in Stata.
  *Stata Journal* 9: 86-136.

`docs/user_guide.pdf` (Appendix A) says, algorithm by algorithm, where the package follows these
papers and where it follows the programs.

## Data

The investment panel bundled with the package (`pyx.load_dataset("invest")`) is the firm panel of
Hansen (1999, *Journal of Econometrics* 93), 565 firms observed from 1973 to 1987, which the author
makes available with his paper and which the help file of `xtdpthresh` uses for its examples.

## Software the package depends on

NumPy, SciPy, pandas, Numba and Matplotlib (BSD-style licences); threadpoolctl (BSD); optionally
python-docx (MIT), openpyxl (MIT) and joblib (BSD). Their licences are those of the projects and are
not changed by this one.

## Disclaimer of the original programs

The help file of `xthenreg` states:

> THIS SOFTWARE IS PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR IMPLIED. THE
> ENTIRE RISK AS TO THE QUALITY AND PERFORMANCE OF THE PROGRAM IS WITH YOU. SHOULD THE PROGRAM PROVE
> DEFECTIVE, YOU ASSUME THE COST OF ALL NECESSARY SERVICING, REPAIR OR CORRECTION. IN NO EVENT WILL
> THE COPYRIGHT HOLDERS OR THEIR EMPLOYERS, OR ANY OTHER PARTY WHO MAY MODIFY AND/OR REDISTRIBUTE THIS
> SOFTWARE, BE LIABLE TO YOU FOR DAMAGES, INCLUDING ANY GENERAL, SPECIAL, INCIDENTAL OR
> CONSEQUENTIAL DAMAGES ARISING OUT OF THE USE OR INABILITY TO USE THE PROGRAM.

This package is independent of the authors of the programs it reproduces; they have not reviewed or
endorsed it, and any difference from their programs is a defect of this package.
