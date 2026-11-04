# The examples of the help file, in Stata and in Python

Each command is the one printed in the help file of `xtdpthresh` (section *Examples*), run with the default options of Stata (`boot(299)`, `gridci(100)`, `grid(100)`). The Stata column is Stata 17 MP; the Python column is `pyxtdpthresh` on the same data. A value agrees when the absolute deviation is at most 5e-05 or the relative deviation is at most 1e-06.

| Example | Objects compared | Largest deviation | All agree |
|---|---:|---:|:---:|
| Point estimates and diagnostics | 53 | 9.2e-14 | yes |
| Full inference and the test of Hansen's threshold | 70 | 4.9e-09 | yes |
| Instruments from lag 2 | 70 | 2.1e-07 | yes |
| Kink model | 62 | 6.4e-10 | yes |
| Unbalanced panel, first differences | 70 | 3.3e-10 | yes |
| Unbalanced panel, forward orthogonal deviations | 70 | 1.7e-08 | yes |
| External instrument | 53 | 1.0e-07 | yes |
| Postestimation: residuals and regime | 55 | 9.2e-14 | yes |

## Point estimates and diagnostics

`xtdpthresh invest, qx(debt) endogenous(cashflow tobin_q debt) maxlag(3 8) collapse noboot`

**Coefficients**

| Object | Python | Stata | Abs. deviation |
|---|---:|---:|---:|
| `lower:L.invest` | 0.0432692 | 0.0432692 | 3.5e-17 |
| `lower:cashflow` | -0.00689701 | -0.00689701 | 2.0e-15 |
| `lower:tobin_q` | 0.00405169 | 0.00405169 | 1.0e-17 |
| `lower:debt` | -0.124453 | -0.124453 | 1.4e-17 |
| `change:_cons` | -0.392195 | -0.392195 | 1.3e-14 |
| `change:L.invest` | 1.59093 | 1.59093 | 9.8e-15 |
| `change:cashflow` | 0.372871 | 0.372871 | 1.0e-14 |
| `change:tobin_q` | 0.0106853 | 0.0106853 | 1.3e-15 |
| `change:debt` | 0.320758 | 0.320758 | 1.1e-14 |

**Standard errors**

| Object | Python | Stata | Abs. deviation |
|---|---:|---:|---:|
| `lower:L.invest` | 0.237744 | 0.237744 | 1.7e-15 |
| `lower:cashflow` | 0.0751998 | 0.0751998 | 1.0e-15 |
| `lower:tobin_q` | 0.006944 | 0.006944 | 6.0e-17 |
| `lower:debt` | 0.100636 | 0.100636 | 1.7e-15 |
| `change:_cons` | 0.151401 | 0.151401 | 8.7e-15 |
| `change:L.invest` | 0.595637 | 0.595637 | 1.2e-14 |
| `change:cashflow` | 0.252386 | 0.252386 | 2.9e-15 |
| `change:tobin_q` | 0.0438127 | 0.0438127 | 9.0e-16 |
| `change:debt` | 0.171695 | 0.171695 | 6.9e-15 |

**Stored scalars**

| Object | Python | Stata | Abs. deviation |
|---|---:|---:|---:|
| `e(N)` | 6720 | 6720 | 0 |
| `e(N_units)` | 560 | 560 | 0 |
| `e(N_clust)` | 560 | 560 | 0 |
| `e(N_iv)` | 25 | 25 | 0 |
| `e(N_iv_common)` | 0 | 0 | 0 |
| `e(N_iv_dep)` | 0 | 0 | 0 |
| `e(N_switch)` | 271 | 271 | 0 |
| `e(gamma)` | 0.419358 | 0.419358 | 5.6e-17 |
| `e(obj)` | 16.0038 | 16.0038 | 9.2e-14 |
| `e(hansen)` | 16.0038 | 16.0038 | 9.2e-14 |
| `e(hansen_df)` | 15 | 15 | 0 |
| `e(hansen_p)` | 0.381801 | 0.381801 | 4.1e-15 |
| `e(ar1)` | -4.61481 | -4.61481 | 4.4e-15 |
| `e(ar1_p)` | 3.93454e-06 | 3.93454e-06 | 8.6e-20 |
| `e(ar2)` | -0.334267 | -0.334267 | 2.5e-14 |
| `e(ar2_p)` | 0.738178 | 0.738178 | 1.9e-14 |
| `e(ar_joint)` | 1 | 1 | 0 |
| `e(ar1_cond)` | -4.56324 | -4.56324 | 4.1e-14 |
| `e(ar2_cond)` | -0.334948 | -0.334948 | 2.5e-14 |
| `e(q_lo)` | 0 | 0 | 0 |
| `e(q_hi)` | 0.601687 | 0.601687 | 1.1e-16 |
| `e(grid_admitted)` | 99 | 99 | 0 |
| `e(estimator_twostep)` | 1 | 1 | 0 |
| `e(W1_fallback)` | 0 | 0 | 0 |
| `e(joint_vce)` | 1 | 1 | 0 |
| `e(vce_applied)` | 0 | 0 | 0 |
| `e(gamma_bw)` | 0.0973951 | 0.0973951 | 4.6e-16 |
| `e(q_nvals_bw)` | 3283 | 3283 | 0 |
| `e(kink_refined)` | . | . | 0 |
| `e(rseed)` | . | . | 0 |

**Stored matrices (largest deviation over all elements)**

| Object | Python | Stata | Abs. deviation |
|---|---:|---:|---:|
| `e(b)` | - | - | 1.3e-14 |
| `e(V)` | - | - | 1.4e-14 |
| `e(V_cond)` | - | - | 1.6e-14 |
| `e(b_upper)` | - | - | 1.1e-14 |
| `e(V_upper)` | - | - | 1.5e-14 |


## Full inference and the test of Hansen's threshold

`xtdpthresh invest, qx(debt) endogenous(cashflow tobin_q debt) maxlag(3 8) collapse citest(0.0157) rseed(12345)`

**Coefficients**

| Object | Python | Stata | Abs. deviation |
|---|---:|---:|---:|
| `lower:L.invest` | 0.0432692 | 0.0432692 | 3.5e-17 |
| `lower:cashflow` | -0.00689701 | -0.00689701 | 2.0e-15 |
| `lower:tobin_q` | 0.00405169 | 0.00405169 | 1.0e-17 |
| `lower:debt` | -0.124453 | -0.124453 | 1.4e-17 |
| `change:_cons` | -0.392195 | -0.392195 | 1.3e-14 |
| `change:L.invest` | 1.59093 | 1.59093 | 9.8e-15 |
| `change:cashflow` | 0.372871 | 0.372871 | 1.0e-14 |
| `change:tobin_q` | 0.0106853 | 0.0106853 | 1.3e-15 |
| `change:debt` | 0.320758 | 0.320758 | 1.1e-14 |

**Standard errors**

| Object | Python | Stata | Abs. deviation |
|---|---:|---:|---:|
| `lower:L.invest` | 0.237744 | 0.237744 | 1.7e-15 |
| `lower:cashflow` | 0.0751998 | 0.0751998 | 1.0e-15 |
| `lower:tobin_q` | 0.006944 | 0.006944 | 6.0e-17 |
| `lower:debt` | 0.100636 | 0.100636 | 1.7e-15 |
| `change:_cons` | 0.151401 | 0.151401 | 8.7e-15 |
| `change:L.invest` | 0.595637 | 0.595637 | 1.2e-14 |
| `change:cashflow` | 0.252386 | 0.252386 | 2.9e-15 |
| `change:tobin_q` | 0.0438127 | 0.0438127 | 9.0e-16 |
| `change:debt` | 0.171695 | 0.171695 | 6.9e-15 |

**Stored scalars**

| Object | Python | Stata | Abs. deviation |
|---|---:|---:|---:|
| `e(N)` | 6720 | 6720 | 0 |
| `e(N_units)` | 560 | 560 | 0 |
| `e(N_clust)` | 560 | 560 | 0 |
| `e(N_iv)` | 25 | 25 | 0 |
| `e(N_iv_common)` | 0 | 0 | 0 |
| `e(N_iv_dep)` | 0 | 0 | 0 |
| `e(N_switch)` | 271 | 271 | 0 |
| `e(gamma)` | 0.419358 | 0.419358 | 5.6e-17 |
| `e(obj)` | 16.0038 | 16.0038 | 9.2e-14 |
| `e(gamma_lo)` | 0.0121553 | 0.0121553 | 2.8e-17 |
| `e(gamma_hi)` | 0.522678 | 0.522678 | 1.1e-16 |
| `e(ci_nseg)` | 4 | 4 | 0 |
| `e(ci_empty)` | 0 | 0 | 0 |
| `e(ci_incomplete)` | 0 | 0 | 0 |
| `e(boundary_warn)` | 0 | 0 | 0 |
| `e(level)` | 95 | 95 | 0 |
| `e(pval_lin)` | 0.00666667 | 0.00666667 | 2.6e-18 |
| `e(citest_gamma)` | 0.0157 | 0.0157 | 0 |
| `e(citest_D)` | 8.05033 | 8.05033 | 4.7e-12 |
| `e(citest_crit)` | 9.01553 | 9.01553 | 2.3e-11 |
| `e(citest_accept)` | 1 | 1 | 0 |
| `e(citest_p)` | 0.0666667 | 0.0666667 | 2.8e-17 |
| `e(citest_status)` | 1 | 1 | 0 |
| `e(citest_draws)` | 299 | 299 | 0 |
| `e(hansen)` | 16.0038 | 16.0038 | 9.2e-14 |
| `e(hansen_df)` | 15 | 15 | 0 |
| `e(hansen_p)` | 0.381801 | 0.381801 | 4.1e-15 |
| `e(ar1)` | -4.61481 | -4.61481 | 4.4e-15 |
| `e(ar1_p)` | 3.93454e-06 | 3.93454e-06 | 8.6e-20 |
| `e(ar2)` | -0.334267 | -0.334267 | 2.5e-14 |
| `e(ar2_p)` | 0.738178 | 0.738178 | 1.9e-14 |
| `e(ar_joint)` | 1 | 1 | 0 |
| `e(ar1_cond)` | -4.56324 | -4.56324 | 4.1e-14 |
| `e(ar2_cond)` | -0.334948 | -0.334948 | 2.5e-14 |
| `e(q_lo)` | 0 | 0 | 0 |
| `e(q_hi)` | 0.601687 | 0.601687 | 1.1e-16 |
| `e(grid_admitted)` | 99 | 99 | 0 |
| `e(estimator_twostep)` | 1 | 1 | 0 |
| `e(W1_fallback)` | 0 | 0 | 0 |
| `e(joint_vce)` | 1 | 1 | 0 |
| `e(vce_applied)` | 0 | 0 | 0 |
| `e(gamma_bw)` | 0.0973951 | 0.0973951 | 4.6e-16 |
| `e(q_nvals_bw)` | 3283 | 3283 | 0 |
| `e(kink_refined)` | . | . | 0 |
| `e(rseed)` | 12345 | 12345 | 0 |

**Stored matrices (largest deviation over all elements)**

| Object | Python | Stata | Abs. deviation |
|---|---:|---:|---:|
| `e(b)` | - | - | 1.3e-14 |
| `e(V)` | - | - | 1.4e-14 |
| `e(V_cond)` | - | - | 1.6e-14 |
| `e(b_upper)` | - | - | 1.1e-14 |
| `e(V_upper)` | - | - | 1.5e-14 |
| `e(ci_segments)` | - | - | 3.3e-16 |
| `e(ci_grid)` | - | - | 4.9e-09 |


## Instruments from lag 2

`xtdpthresh invest, qx(debt) endogenous(cashflow tobin_q debt) maxlag(2 10) collapse rseed(12345)`

**Coefficients**

| Object | Python | Stata | Abs. deviation |
|---|---:|---:|---:|
| `lower:L.invest` | -2.1711 | -2.1711 | 5.2e-12 |
| `lower:cashflow` | 0.0217219 | 0.0217219 | 5.7e-13 |
| `lower:tobin_q` | 0.049847 | 0.049847 | 4.0e-13 |
| `lower:debt` | -12.8239 | -12.8239 | 1.8e-09 |
| `change:_cons` | -0.305248 | -0.305248 | 4.6e-12 |
| `change:L.invest` | 2.64506 | 2.64506 | 4.4e-12 |
| `change:cashflow` | 0.200734 | 0.200734 | 2.0e-13 |
| `change:tobin_q` | -0.0507295 | -0.0507295 | 5.2e-13 |
| `change:debt` | 12.7722 | 12.7722 | 1.8e-09 |

**Standard errors**

| Object | Python | Stata | Abs. deviation |
|---|---:|---:|---:|
| `lower:L.invest` | 0.627755 | 0.627755 | 8.7e-12 |
| `lower:cashflow` | 0.130162 | 0.130162 | 2.6e-12 |
| `lower:tobin_q` | 0.0238528 | 0.0238528 | 3.6e-13 |
| `lower:debt` | 16.1456 | 16.1456 | 4.8e-09 |
| `change:_cons` | 0.108571 | 0.108571 | 1.0e-13 |
| `change:L.invest` | 0.678775 | 0.678775 | 1.2e-11 |
| `change:cashflow` | 0.162995 | 0.162995 | 2.8e-12 |
| `change:tobin_q` | 0.0290445 | 0.0290445 | 2.3e-13 |
| `change:debt` | 16.1399 | 16.1399 | 5.9e-09 |

**Stored scalars**

| Object | Python | Stata | Abs. deviation |
|---|---:|---:|---:|
| `e(N)` | 7280 | 7280 | 0 |
| `e(N_units)` | 560 | 560 | 0 |
| `e(N_clust)` | 560 | 560 | 0 |
| `e(N_iv)` | 37 | 37 | 0 |
| `e(N_iv_common)` | 0 | 0 | 0 |
| `e(N_iv_dep)` | 0 | 0 | 0 |
| `e(N_switch)` | 144 | 144 | 0 |
| `e(gamma)` | 0.0121323 | 0.0121323 | 1.2e-17 |
| `e(obj)` | 24.083 | 24.083 | 5.7e-10 |
| `e(gamma_lo)` | 0.00606613 | 0.00606613 | 3.5e-18 |
| `e(gamma_hi)` | 0.0545951 | 0.0545951 | 1.4e-17 |
| `e(ci_nseg)` | 1 | 1 | 0 |
| `e(ci_empty)` | 0 | 0 | 0 |
| `e(ci_incomplete)` | 0 | 0 | 0 |
| `e(boundary_warn)` | 1 | 1 | 0 |
| `e(level)` | 95 | 95 | 0 |
| `e(pval_lin)` | 0.00333333 | 0.00333333 | 3.5e-18 |
| `e(citest_gamma)` | . | . | 0 |
| `e(citest_D)` | . | . | 0 |
| `e(citest_crit)` | . | . | 0 |
| `e(citest_accept)` | . | . | 0 |
| `e(citest_p)` | . | . | 0 |
| `e(citest_status)` | . | . | 0 |
| `e(citest_draws)` | . | . | 0 |
| `e(hansen)` | 24.083 | 24.083 | 5.7e-10 |
| `e(hansen_df)` | 27 | 27 | 0 |
| `e(hansen_p)` | 0.62571 | 0.62571 | 3.2e-11 |
| `e(ar1)` | -8.5481 | -8.5481 | 2.9e-10 |
| `e(ar1_p)` | 1.25135e-17 | 1.25135e-17 | 3.2e-26 |
| `e(ar2)` | -2.48147 | -2.48147 | 7.4e-10 |
| `e(ar2_p)` | 0.0130842 | 0.0130842 | 2.7e-11 |
| `e(ar_joint)` | 1 | 1 | 0 |
| `e(ar1_cond)` | -8.87077 | -8.87077 | 9.2e-12 |
| `e(ar2_cond)` | -2.49467 | -2.49467 | 1.0e-09 |
| `e(q_lo)` | 0 | 0 | 0 |
| `e(q_hi)` | 0.600546 | 0.600546 | 4.4e-16 |
| `e(grid_admitted)` | 99 | 99 | 0 |
| `e(estimator_twostep)` | 1 | 1 | 0 |
| `e(W1_fallback)` | 0 | 0 | 0 |
| `e(joint_vce)` | 1 | 1 | 0 |
| `e(vce_applied)` | 0 | 0 | 0 |
| `e(gamma_bw)` | 0.0973951 | 0.0973951 | 4.6e-16 |
| `e(q_nvals_bw)` | 3182 | 3182 | 0 |
| `e(kink_refined)` | . | . | 0 |
| `e(rseed)` | 12345 | 12345 | 0 |

**Stored matrices (largest deviation over all elements)**

| Object | Python | Stata | Abs. deviation |
|---|---:|---:|---:|
| `e(b)` | - | - | 1.8e-09 |
| `e(V)` | - | - | 2.1e-07 |
| `e(V_cond)` | - | - | 3.0e-08 |
| `e(b_upper)` | - | - | 2.2e-11 |
| `e(V_upper)` | - | - | 2.9e-11 |
| `e(ci_segments)` | - | - | 1.4e-17 |
| `e(ci_grid)` | - | - | 1.2e-08 |


## Kink model

`xtdpthresh invest, qx(debt) endogenous(cashflow tobin_q debt) maxlag(3 8) collapse kink rseed(12345)`

**Coefficients**

| Object | Python | Stata | Abs. deviation |
|---|---:|---:|---:|
| `lower:L.invest` | 0.312495 | 0.312495 | 5.6e-14 |
| `lower:cashflow` | 0.113399 | 0.113399 | 1.5e-14 |
| `lower:tobin_q` | 0.0114419 | 0.0114419 | 7.4e-16 |
| `lower:debt` | 3.5401 | 3.5401 | 2.9e-12 |
| `change:debt` | -3.63735 | -3.63735 | 3.0e-12 |

**Standard errors**

| Object | Python | Stata | Abs. deviation |
|---|---:|---:|---:|
| `lower:L.invest` | 0.0782542 | 0.0782542 | 6.6e-14 |
| `lower:cashflow` | 0.0344134 | 0.0344134 | 9.2e-14 |
| `lower:tobin_q` | 0.00469424 | 0.00469424 | 3.5e-14 |
| `lower:debt` | 3.98297 | 3.98297 | 8.0e-11 |
| `change:debt` | 3.98475 | 3.98475 | 7.4e-11 |

**Stored scalars**

| Object | Python | Stata | Abs. deviation |
|---|---:|---:|---:|
| `e(N)` | 6720 | 6720 | 0 |
| `e(N_units)` | 560 | 560 | 0 |
| `e(N_clust)` | 560 | 560 | 0 |
| `e(N_iv)` | 25 | 25 | 0 |
| `e(N_iv_common)` | 0 | 0 | 0 |
| `e(N_iv_dep)` | 0 | 0 | 0 |
| `e(N_switch)` | 169 | 169 | 0 |
| `e(gamma)` | 0.03206 | 0.03206 | 2.1e-17 |
| `e(obj)` | 52.5416 | 52.5416 | 2.1e-13 |
| `e(gamma_lo)` | 0.0182329 | 0.0182329 | 1.0e-17 |
| `e(gamma_hi)` | 0.10332 | 0.10332 | 1.1e-16 |
| `e(ci_nseg)` | 1 | 1 | 0 |
| `e(ci_empty)` | 0 | 0 | 0 |
| `e(ci_incomplete)` | 0 | 0 | 0 |
| `e(boundary_warn)` | 0 | 0 | 0 |
| `e(level)` | 95 | 95 | 0 |
| `e(pval_lin)` | 0.256667 | 0.256667 | 3.3e-16 |
| `e(citest_gamma)` | . | . | 0 |
| `e(citest_D)` | . | . | 0 |
| `e(citest_crit)` | . | . | 0 |
| `e(citest_accept)` | . | . | 0 |
| `e(citest_p)` | . | . | 0 |
| `e(citest_status)` | . | . | 0 |
| `e(citest_draws)` | . | . | 0 |
| `e(hansen)` | 52.5416 | 52.5416 | 2.1e-13 |
| `e(hansen_df)` | 19 | 19 | 0 |
| `e(hansen_p)` | 5.48745e-05 | 5.48745e-05 | 3.5e-18 |
| `e(ar1)` | -6.37072 | -6.37072 | 2.7e-12 |
| `e(ar1_p)` | 1.88139e-10 | 1.88139e-10 | 3.4e-21 |
| `e(ar2)` | 0.278749 | 0.278749 | 4.5e-13 |
| `e(ar2_p)` | 0.780438 | 0.780438 | 3.5e-13 |
| `e(ar_joint)` | 1 | 1 | 0 |
| `e(ar1_cond)` | -6.37884 | -6.37884 | 4.4e-13 |
| `e(ar2_cond)` | 0.279449 | 0.279449 | 1.6e-13 |
| `e(q_lo)` | 0 | 0 | 0 |
| `e(q_hi)` | 0.601687 | 0.601687 | 1.1e-16 |
| `e(grid_admitted)` | 99 | 99 | 0 |
| `e(estimator_twostep)` | 1 | 1 | 0 |
| `e(W1_fallback)` | 0 | 0 | 0 |
| `e(joint_vce)` | 1 | 1 | 0 |
| `e(vce_applied)` | 0 | 0 | 0 |
| `e(gamma_bw)` | . | . | 0 |
| `e(q_nvals_bw)` | . | . | 0 |
| `e(kink_refined)` | 1 | 1 | 0 |
| `e(rseed)` | 12345 | 12345 | 0 |

**Stored matrices (largest deviation over all elements)**

| Object | Python | Stata | Abs. deviation |
|---|---:|---:|---:|
| `e(b)` | - | - | 3.0e-12 |
| `e(V)` | - | - | 6.4e-10 |
| `e(V_cond)` | - | - | 2.9e-12 |
| `e(b_upper)` | -0.0972546 | -0.0972546 | 5.5e-14 |
| `e(V_upper)` | 0.000527764 | 0.000527764 | 1.2e-14 |
| `e(ci_segments)` | - | - | 1.1e-16 |
| `e(ci_grid)` | - | - | 1.5e-11 |


## Unbalanced panel, first differences

`xtdpthresh invest, qx(debt) endogenous(cashflow tobin_q debt) maxlag(3 8) collapse method(fd) rseed(12345)`

Data: the sample Stata drew with `set seed 20260418` (15% of the observations dropped, then the firms with fewer than four left).

**Coefficients**

| Object | Python | Stata | Abs. deviation |
|---|---:|---:|---:|
| `lower:L.invest` | -0.0734477 | -0.0734477 | 1.9e-14 |
| `lower:cashflow` | 0.174195 | 0.174195 | 1.4e-16 |
| `lower:tobin_q` | 0.00340867 | 0.00340867 | 3.0e-16 |
| `lower:debt` | 1.3827 | 1.3827 | 2.0e-14 |
| `change:_cons` | 0.156727 | 0.156727 | 1.4e-14 |
| `change:L.invest` | 0.256285 | 0.256285 | 3.3e-14 |
| `change:cashflow` | -0.232268 | -0.232268 | 1.1e-14 |
| `change:tobin_q` | 0.026001 | 0.026001 | 2.9e-15 |
| `change:debt` | -1.5512 | -1.5512 | 3.1e-14 |

**Standard errors**

| Object | Python | Stata | Abs. deviation |
|---|---:|---:|---:|
| `lower:L.invest` | 0.35276 | 0.35276 | 3.3e-16 |
| `lower:cashflow` | 0.148151 | 0.148151 | 4.2e-14 |
| `lower:tobin_q` | 0.013705 | 0.013705 | 3.2e-16 |
| `lower:debt` | 1.1073 | 1.1073 | 6.6e-13 |
| `change:_cons` | 0.333854 | 0.333854 | 1.5e-13 |
| `change:L.invest` | 0.518442 | 0.518442 | 7.4e-14 |
| `change:cashflow` | 0.252392 | 0.252392 | 4.5e-14 |
| `change:tobin_q` | 0.0381106 | 0.0381106 | 8.6e-15 |
| `change:debt` | 1.37549 | 1.37549 | 6.7e-13 |

**Stored scalars**

| Object | Python | Stata | Abs. deviation |
|---|---:|---:|---:|
| `e(N)` | 4063 | 4063 | 0 |
| `e(N_units)` | 558 | 558 | 0 |
| `e(N_clust)` | 558 | 558 | 0 |
| `e(N_iv)` | 25 | 25 | 0 |
| `e(N_iv_common)` | 0 | 0 | 0 |
| `e(N_iv_dep)` | 0 | 0 | 0 |
| `e(N_switch)` | 311 | 311 | 0 |
| `e(gamma)` | 0.192607 | 0.192607 | 5.0e-16 |
| `e(obj)` | 6.27118 | 6.27118 | 1.5e-13 |
| `e(gamma_lo)` | 0.00601898 | 0.00601898 | 3.5e-18 |
| `e(gamma_hi)` | 0.595879 | 0.595879 | 2.2e-16 |
| `e(ci_nseg)` | 1 | 1 | 0 |
| `e(ci_empty)` | 0 | 0 | 0 |
| `e(ci_incomplete)` | 0 | 0 | 0 |
| `e(boundary_warn)` | 3 | 3 | 0 |
| `e(level)` | 95 | 95 | 0 |
| `e(pval_lin)` | 0.543333 | 0.543333 | 3.3e-16 |
| `e(citest_gamma)` | . | . | 0 |
| `e(citest_D)` | . | . | 0 |
| `e(citest_crit)` | . | . | 0 |
| `e(citest_accept)` | . | . | 0 |
| `e(citest_p)` | . | . | 0 |
| `e(citest_status)` | . | . | 0 |
| `e(citest_draws)` | . | . | 0 |
| `e(hansen)` | 6.27118 | 6.27118 | 1.5e-13 |
| `e(hansen_df)` | 15 | 15 | 0 |
| `e(hansen_p)` | 0.974824 | 0.974824 | 2.4e-15 |
| `e(ar1)` | -3.56309 | -3.56309 | 9.3e-14 |
| `e(ar1_p)` | 0.000366521 | 0.000366521 | 1.4e-16 |
| `e(ar2)` | -1.31238 | -1.31238 | 1.6e-13 |
| `e(ar2_p)` | 0.189393 | 0.189393 | 5.3e-14 |
| `e(ar_joint)` | 1 | 1 | 0 |
| `e(ar1_cond)` | -3.94163 | -3.94163 | 2.7e-15 |
| `e(ar2_cond)` | -1.42751 | -1.42751 | 2.1e-14 |
| `e(q_lo)` | 0 | 0 | 0 |
| `e(q_hi)` | 0.595879 | 0.595879 | 2.2e-16 |
| `e(grid_admitted)` | 99 | 99 | 0 |
| `e(estimator_twostep)` | 1 | 1 | 0 |
| `e(W1_fallback)` | 0 | 0 | 0 |
| `e(joint_vce)` | 1 | 1 | 0 |
| `e(vce_applied)` | 0 | 0 | 0 |
| `e(gamma_bw)` | 0.0962312 | 0.0962312 | 1.4e-17 |
| `e(q_nvals_bw)` | 4915 | 4915 | 0 |
| `e(kink_refined)` | . | . | 0 |
| `e(rseed)` | 12345 | 12345 | 0 |

**Stored matrices (largest deviation over all elements)**

| Object | Python | Stata | Abs. deviation |
|---|---:|---:|---:|
| `e(b)` | - | - | 3.3e-14 |
| `e(V)` | - | - | 1.9e-12 |
| `e(V_cond)` | - | - | 7.4e-14 |
| `e(b_upper)` | - | - | 1.4e-14 |
| `e(V_upper)` | - | - | 5.1e-14 |
| `e(ci_segments)` | - | - | 2.2e-16 |
| `e(ci_grid)` | - | - | 3.3e-10 |


## Unbalanced panel, forward orthogonal deviations

`xtdpthresh invest, qx(debt) endogenous(cashflow tobin_q debt) maxlag(3 8) collapse method(fod) rseed(12345)`

Data: the sample Stata drew with `set seed 20260418` (15% of the observations dropped, then the firms with fewer than four left).

**Coefficients**

| Object | Python | Stata | Abs. deviation |
|---|---:|---:|---:|
| `lower:L.invest` | -0.138161 | -0.138161 | 2.0e-13 |
| `lower:cashflow` | 0.187359 | 0.187359 | 1.2e-12 |
| `lower:tobin_q` | -0.0226153 | -0.0226153 | 2.5e-13 |
| `lower:debt` | -8.9034 | -8.9034 | 3.8e-10 |
| `change:_cons` | -0.0662597 | -0.0662597 | 1.8e-12 |
| `change:L.invest` | 0.491762 | 0.491762 | 1.9e-12 |
| `change:cashflow` | -0.0690119 | -0.0690119 | 7.6e-15 |
| `change:tobin_q` | 0.0469446 | 0.0469446 | 1.7e-13 |
| `change:debt` | 8.84481 | 8.84481 | 3.7e-10 |

**Standard errors**

| Object | Python | Stata | Abs. deviation |
|---|---:|---:|---:|
| `lower:L.invest` | 0.735332 | 0.735332 | 6.1e-13 |
| `lower:cashflow` | 0.155159 | 0.155159 | 4.3e-13 |
| `lower:tobin_q` | 0.0238435 | 0.0238435 | 5.6e-14 |
| `lower:debt` | 11.1273 | 11.1273 | 5.4e-10 |
| `change:_cons` | 0.112442 | 0.112442 | 7.5e-13 |
| `change:L.invest` | 0.7896 | 0.7896 | 1.8e-12 |
| `change:cashflow` | 0.177541 | 0.177541 | 2.0e-13 |
| `change:tobin_q` | 0.0323833 | 0.0323833 | 1.2e-14 |
| `change:debt` | 11.1233 | 11.1233 | 7.5e-10 |

**Stored scalars**

| Object | Python | Stata | Abs. deviation |
|---|---:|---:|---:|
| `e(N)` | 4616 | 4616 | 0 |
| `e(N_units)` | 559 | 559 | 0 |
| `e(N_clust)` | 559 | 559 | 0 |
| `e(N_iv)` | 25 | 25 | 0 |
| `e(N_iv_common)` | 0 | 0 | 0 |
| `e(N_iv_dep)` | 0 | 0 | 0 |
| `e(N_switch)` | 123 | 123 | 0 |
| `e(gamma)` | 0.0181774 | 0.0181774 | 4.9e-17 |
| `e(obj)` | 8.90871 | 8.90871 | 3.9e-11 |
| `e(gamma_lo)` | 0.0181774 | 0.0181774 | 4.9e-17 |
| `e(gamma_hi)` | 0.599853 | 0.599853 | 4.4e-16 |
| `e(ci_nseg)` | 11 | 11 | 0 |
| `e(ci_empty)` | 0 | 0 | 0 |
| `e(ci_incomplete)` | 0 | 0 | 0 |
| `e(boundary_warn)` | 2 | 2 | 0 |
| `e(level)` | 95 | 95 | 0 |
| `e(pval_lin)` | 0.283333 | 0.283333 | 3.3e-16 |
| `e(citest_gamma)` | . | . | 0 |
| `e(citest_D)` | . | . | 0 |
| `e(citest_crit)` | . | . | 0 |
| `e(citest_accept)` | . | . | 0 |
| `e(citest_p)` | . | . | 0 |
| `e(citest_status)` | . | . | 0 |
| `e(citest_draws)` | . | . | 0 |
| `e(hansen)` | 8.90871 | 8.90871 | 3.9e-11 |
| `e(hansen_df)` | 15 | 15 | 0 |
| `e(hansen_p)` | 0.882242 | 0.882242 | 2.0e-12 |
| `e(ar1)` | -4.15547 | -4.15547 | 9.2e-11 |
| `e(ar1_p)` | 3.24619e-05 | 3.24619e-05 | 1.3e-14 |
| `e(ar2)` | 0.403822 | 0.403822 | 3.6e-12 |
| `e(ar2_p)` | 0.686343 | 0.686343 | 2.6e-12 |
| `e(ar_joint)` | 1 | 1 | 0 |
| `e(ar1_cond)` | -4.23226 | -4.23226 | 3.6e-11 |
| `e(ar2_cond)` | 0.404264 | 0.404264 | 1.4e-11 |
| `e(q_lo)` | 0 | 0 | 0 |
| `e(q_hi)` | 0.599853 | 0.599853 | 4.4e-16 |
| `e(grid_admitted)` | 99 | 99 | 0 |
| `e(estimator_twostep)` | 1 | 1 | 0 |
| `e(W1_fallback)` | 0 | 0 | 0 |
| `e(joint_vce)` | 1 | 1 | 0 |
| `e(vce_applied)` | 0 | 0 | 0 |
| `e(gamma_bw)` | 0.0961967 | 0.0961967 | 5.6e-17 |
| `e(q_nvals_bw)` | 2782 | 2782 | 0 |
| `e(kink_refined)` | . | . | 0 |
| `e(rseed)` | 12345 | 12345 | 0 |

**Stored matrices (largest deviation over all elements)**

| Object | Python | Stata | Abs. deviation |
|---|---:|---:|---:|
| `e(b)` | - | - | 3.8e-10 |
| `e(V)` | - | - | 1.7e-08 |
| `e(V_cond)` | - | - | 8.8e-09 |
| `e(b_upper)` | - | - | 2.1e-12 |
| `e(V_upper)` | - | - | 1.2e-11 |
| `e(ci_segments)` | - | - | 5.0e-16 |
| `e(ci_grid)` | - | - | 3.3e-10 |


## External instrument

`xtdpthresh invest, qx(debt) endogenous(cashflow tobin_q debt) iv(L2.peer_q) maxlag(3 8) collapse noboot`

**Coefficients**

| Object | Python | Stata | Abs. deviation |
|---|---:|---:|---:|
| `lower:L.invest` | -1.0113 | -1.0113 | 7.4e-12 |
| `lower:cashflow` | -0.0400901 | -0.0400901 | 6.9e-12 |
| `lower:tobin_q` | 0.0388101 | 0.0388101 | 1.3e-12 |
| `lower:debt` | -21.6807 | -21.6807 | 1.2e-09 |
| `change:_cons` | -0.175634 | -0.175634 | 8.4e-12 |
| `change:L.invest` | 1.14331 | 1.14331 | 4.6e-12 |
| `change:cashflow` | 0.0584189 | 0.0584189 | 7.9e-12 |
| `change:tobin_q` | -0.019527 | -0.019527 | 1.3e-12 |
| `change:debt` | 21.5136 | 21.5136 | 1.2e-09 |

**Standard errors**

| Object | Python | Stata | Abs. deviation |
|---|---:|---:|---:|
| `lower:L.invest` | 0.6019 | 0.6019 | 1.9e-12 |
| `lower:cashflow` | 0.158711 | 0.158711 | 1.9e-12 |
| `lower:tobin_q` | 0.030362 | 0.030362 | 1.0e-12 |
| `lower:debt` | 16.1906 | 16.1906 | 2.3e-09 |
| `change:_cons` | 0.144324 | 0.144324 | 1.0e-11 |
| `change:L.invest` | 0.677452 | 0.677452 | 2.5e-12 |
| `change:cashflow` | 0.193044 | 0.193044 | 1.2e-12 |
| `change:tobin_q` | 0.0351659 | 0.0351659 | 9.9e-13 |
| `change:debt` | 16.1998 | 16.1998 | 3.1e-09 |

**Stored scalars**

| Object | Python | Stata | Abs. deviation |
|---|---:|---:|---:|
| `e(N)` | 7280 | 7280 | 0 |
| `e(N_units)` | 560 | 560 | 0 |
| `e(N_clust)` | 560 | 560 | 0 |
| `e(N_iv)` | 26 | 26 | 0 |
| `e(N_iv_common)` | 0 | 0 | 0 |
| `e(N_iv_dep)` | 0 | 0 | 0 |
| `e(N_switch)` | 152 | 152 | 0 |
| `e(gamma)` | 0.0181984 | 0.0181984 | 3.1e-17 |
| `e(obj)` | 9.15452 | 9.15452 | 4.1e-10 |
| `e(hansen)` | 9.15452 | 9.15452 | 4.1e-10 |
| `e(hansen_df)` | 16 | 16 | 0 |
| `e(hansen_p)` | 0.906914 | 0.906914 | 1.7e-11 |
| `e(ar1)` | -3.61425 | -3.61425 | 5.6e-11 |
| `e(ar1_p)` | 0.00030122 | 0.00030122 | 6.5e-14 |
| `e(ar2)` | -1.92109 | -1.92109 | 7.8e-10 |
| `e(ar2_p)` | 0.0547203 | 0.0547203 | 9.8e-11 |
| `e(ar_joint)` | 1 | 1 | 0 |
| `e(ar1_cond)` | -3.69278 | -3.69278 | 2.3e-10 |
| `e(ar2_cond)` | -1.94962 | -1.94962 | 1.7e-09 |
| `e(q_lo)` | 0 | 0 | 0 |
| `e(q_hi)` | 0.600546 | 0.600546 | 4.4e-16 |
| `e(grid_admitted)` | 99 | 99 | 0 |
| `e(estimator_twostep)` | 1 | 1 | 0 |
| `e(W1_fallback)` | 0 | 0 | 0 |
| `e(joint_vce)` | 1 | 1 | 0 |
| `e(vce_applied)` | 0 | 0 | 0 |
| `e(gamma_bw)` | 0.0973951 | 0.0973951 | 4.6e-16 |
| `e(q_nvals_bw)` | 3291 | 3291 | 0 |
| `e(kink_refined)` | . | . | 0 |
| `e(rseed)` | . | . | 0 |

**Stored matrices (largest deviation over all elements)**

| Object | Python | Stata | Abs. deviation |
|---|---:|---:|---:|
| `e(b)` | - | - | 1.2e-09 |
| `e(V)` | - | - | 1.0e-07 |
| `e(V_cond)` | - | - | 2.6e-08 |
| `e(b_upper)` | - | - | 1.7e-11 |
| `e(V_upper)` | - | - | 2.2e-11 |


## Postestimation: residuals and regime

`xtdpthresh invest, qx(debt) endogenous(cashflow tobin_q debt) maxlag(3 8) collapse noboot`

**Coefficients**

| Object | Python | Stata | Abs. deviation |
|---|---:|---:|---:|
| `lower:L.invest` | 0.0432692 | 0.0432692 | 3.5e-17 |
| `lower:cashflow` | -0.00689701 | -0.00689701 | 2.0e-15 |
| `lower:tobin_q` | 0.00405169 | 0.00405169 | 1.0e-17 |
| `lower:debt` | -0.124453 | -0.124453 | 1.4e-17 |
| `change:_cons` | -0.392195 | -0.392195 | 1.3e-14 |
| `change:L.invest` | 1.59093 | 1.59093 | 9.8e-15 |
| `change:cashflow` | 0.372871 | 0.372871 | 1.0e-14 |
| `change:tobin_q` | 0.0106853 | 0.0106853 | 1.3e-15 |
| `change:debt` | 0.320758 | 0.320758 | 1.1e-14 |

**Standard errors**

| Object | Python | Stata | Abs. deviation |
|---|---:|---:|---:|
| `lower:L.invest` | 0.237744 | 0.237744 | 1.7e-15 |
| `lower:cashflow` | 0.0751998 | 0.0751998 | 1.0e-15 |
| `lower:tobin_q` | 0.006944 | 0.006944 | 6.0e-17 |
| `lower:debt` | 0.100636 | 0.100636 | 1.7e-15 |
| `change:_cons` | 0.151401 | 0.151401 | 8.7e-15 |
| `change:L.invest` | 0.595637 | 0.595637 | 1.2e-14 |
| `change:cashflow` | 0.252386 | 0.252386 | 2.9e-15 |
| `change:tobin_q` | 0.0438127 | 0.0438127 | 9.0e-16 |
| `change:debt` | 0.171695 | 0.171695 | 6.9e-15 |

**Stored scalars**

| Object | Python | Stata | Abs. deviation |
|---|---:|---:|---:|
| `e(N)` | 6720 | 6720 | 0 |
| `e(N_units)` | 560 | 560 | 0 |
| `e(N_clust)` | 560 | 560 | 0 |
| `e(N_iv)` | 25 | 25 | 0 |
| `e(N_iv_common)` | 0 | 0 | 0 |
| `e(N_iv_dep)` | 0 | 0 | 0 |
| `e(N_switch)` | 271 | 271 | 0 |
| `e(gamma)` | 0.419358 | 0.419358 | 5.6e-17 |
| `e(obj)` | 16.0038 | 16.0038 | 9.2e-14 |
| `e(hansen)` | 16.0038 | 16.0038 | 9.2e-14 |
| `e(hansen_df)` | 15 | 15 | 0 |
| `e(hansen_p)` | 0.381801 | 0.381801 | 4.1e-15 |
| `e(ar1)` | -4.61481 | -4.61481 | 4.4e-15 |
| `e(ar1_p)` | 3.93454e-06 | 3.93454e-06 | 8.6e-20 |
| `e(ar2)` | -0.334267 | -0.334267 | 2.5e-14 |
| `e(ar2_p)` | 0.738178 | 0.738178 | 1.9e-14 |
| `e(ar_joint)` | 1 | 1 | 0 |
| `e(ar1_cond)` | -4.56324 | -4.56324 | 4.1e-14 |
| `e(ar2_cond)` | -0.334948 | -0.334948 | 2.5e-14 |
| `e(q_lo)` | 0 | 0 | 0 |
| `e(q_hi)` | 0.601687 | 0.601687 | 1.1e-16 |
| `e(grid_admitted)` | 99 | 99 | 0 |
| `e(estimator_twostep)` | 1 | 1 | 0 |
| `e(W1_fallback)` | 0 | 0 | 0 |
| `e(joint_vce)` | 1 | 1 | 0 |
| `e(vce_applied)` | 0 | 0 | 0 |
| `e(gamma_bw)` | 0.0973951 | 0.0973951 | 4.6e-16 |
| `e(q_nvals_bw)` | 3283 | 3283 | 0 |
| `e(kink_refined)` | . | . | 0 |
| `e(rseed)` | . | . | 0 |

**Stored matrices (largest deviation over all elements)**

| Object | Python | Stata | Abs. deviation |
|---|---:|---:|---:|
| `e(b)` | - | - | 1.3e-14 |
| `e(V)` | - | - | 1.4e-14 |
| `e(V_cond)` | - | - | 1.6e-14 |
| `e(b_upper)` | - | - | 1.1e-14 |
| `e(V_upper)` | - | - | 1.5e-14 |

**predict**

| Object | Python | Stata | Abs. deviation |
|---|---:|---:|---:|
| `predict, residuals` | - | - | 2.7e-14 |
| `predict, regime` | - | - | 0 |

