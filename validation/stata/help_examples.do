version 17
set more off
clear all
mata:
void pyx_export(string scalar fname, real matrix M)
{
    real scalar fh, i, j
    string scalar line
    if (fileexists(fname)) unlink(fname)
    fh = fopen(fname, "w")
    for (i = 1; i <= rows(M); i++) {
        line = strofreal(M[i,1], "%21.15g")
        for (j = 2; j <= cols(M); j++) line = line + "," + strofreal(M[i,j], "%21.15g")
        fput(fh, line)
    }
    fclose(fh)
}
end

mata:
real scalar pyx_sc(string scalar name)
{
    real matrix v
    v = st_numscalar(name)
    return(rows(v) * cols(v) == 1 ? v : .)
}
end

use "../data/invest.dta", clear
xtset firm year
drop if inlist(firm, 137, 391, 407, 488, 538)
display "@@CASE point"
capture noisily xtdpthresh invest, qx(debt) endogenous(cashflow tobin_q debt) maxlag(3 8) collapse noboot
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/he_point_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/he_point_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/he_point_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/he_point_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/he_point_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/he_point_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/he_point_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/he_point_ci_grid.csv", st_matrix("e(ci_grid)"))
}

display "@@CASE inference"
capture noisily xtdpthresh invest, qx(debt) endogenous(cashflow tobin_q debt) maxlag(3 8) collapse citest(0.0157) rseed(12345)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/he_inference_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/he_inference_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/he_inference_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/he_inference_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/he_inference_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/he_inference_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/he_inference_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/he_inference_ci_grid.csv", st_matrix("e(ci_grid)"))
}

display "@@CASE lag2"
capture noisily xtdpthresh invest, qx(debt) endogenous(cashflow tobin_q debt) maxlag(2 10) collapse rseed(12345)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/he_lag2_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/he_lag2_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/he_lag2_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/he_lag2_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/he_lag2_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/he_lag2_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/he_lag2_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/he_lag2_ci_grid.csv", st_matrix("e(ci_grid)"))
}

display "@@CASE kink"
capture noisily xtdpthresh invest, qx(debt) endogenous(cashflow tobin_q debt) maxlag(3 8) collapse kink rseed(12345)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/he_kink_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/he_kink_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/he_kink_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/he_kink_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/he_kink_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/he_kink_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/he_kink_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/he_kink_ci_grid.csv", st_matrix("e(ci_grid)"))
}

preserve
set seed 20260418
drop if runiform() < 0.15
bysort firm: drop if _N < 4
display "@@CASE unbalanced_fd"
capture noisily xtdpthresh invest, qx(debt) endogenous(cashflow tobin_q debt) maxlag(3 8) collapse method(fd) rseed(12345)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/he_unbalanced_fd_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/he_unbalanced_fd_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/he_unbalanced_fd_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/he_unbalanced_fd_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/he_unbalanced_fd_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/he_unbalanced_fd_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/he_unbalanced_fd_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/he_unbalanced_fd_ci_grid.csv", st_matrix("e(ci_grid)"))
}
export delimited firm year invest tobin_q cashflow debt using "../out/he_sample.csv", replace
restore

preserve
set seed 20260418
drop if runiform() < 0.15
bysort firm: drop if _N < 4
display "@@CASE unbalanced_fod"
capture noisily xtdpthresh invest, qx(debt) endogenous(cashflow tobin_q debt) maxlag(3 8) collapse method(fod) rseed(12345)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/he_unbalanced_fod_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/he_unbalanced_fod_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/he_unbalanced_fod_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/he_unbalanced_fod_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/he_unbalanced_fod_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/he_unbalanced_fod_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/he_unbalanced_fod_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/he_unbalanced_fod_ci_grid.csv", st_matrix("e(ci_grid)"))
}

restore

egen double peer_q = mean(tobin_q), by(year)
display "@@CASE external_iv"
capture noisily xtdpthresh invest, qx(debt) endogenous(cashflow tobin_q debt) iv(L2.peer_q) maxlag(3 8) collapse noboot
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/he_external_iv_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/he_external_iv_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/he_external_iv_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/he_external_iv_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/he_external_iv_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/he_external_iv_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/he_external_iv_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/he_external_iv_ci_grid.csv", st_matrix("e(ci_grid)"))
}

display "@@CASE predict"
capture noisily xtdpthresh invest, qx(debt) endogenous(cashflow tobin_q debt) maxlag(3 8) collapse noboot
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/he_predict_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/he_predict_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/he_predict_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/he_predict_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/he_predict_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/he_predict_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/he_predict_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/he_predict_ci_grid.csv", st_matrix("e(ci_grid)"))
    predict double ehat, residuals
    predict byte upper, regime
    export delimited firm year ehat upper using "../out/he_predict_predict.csv", replace
    drop ehat upper
}

exit, clear
