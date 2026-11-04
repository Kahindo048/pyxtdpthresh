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

import delimited using "../out/stress_s000.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s000"
capture noisily xtdpthresh y x1 x2, qx(q) method(fd) grid(50) boot(29) rseed(75272) gridci(20) maxlag(3 5)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s000_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s000_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s000_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s000_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s000_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s000_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s000_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s000_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s001.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s001"
capture noisily xtdpthresh y x1, qx(q) kink td collapse noboot method(fd) grid(20) boot(29) rseed(892285) gridci(20) maxlag(3 5) endogenous(e1 e2)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s001_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s001_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s001_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s001_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s001_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s001_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s001_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s001_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s002.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s002"
capture noisily xtdpthresh y x1, qx(q) method(fod) grid(20) boot(29) rseed(332524) gridci(20) maxlag(3 5) endogenous(e1)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s002_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s002_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s002_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s002_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s002_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s002_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s002_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s002_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s003.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s003"
capture noisily xtdpthresh y , qx(q) collapse method(fod) grid(20) boot(29) rseed(100987) gridci(20) endogenous(e1)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s003_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s003_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s003_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s003_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s003_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s003_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s003_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s003_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s004.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s004"
capture noisily xtdpthresh y x1, qx(q) noboot method(fod) grid(50) boot(29) rseed(425802) gridci(20) maxlag(2 6) endogenous(e1 e2)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s004_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s004_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s004_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s004_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s004_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s004_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s004_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s004_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s005.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s005"
capture noisily xtdpthresh y x1 x2, qx(q) kink noboot method(fd) grid(100) boot(29) rseed(583603) gridci(20) endogenous(e1)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s005_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s005_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s005_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s005_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s005_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s005_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s005_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s005_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s006.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s006"
capture noisily xtdpthresh y x1, qx(q) noboot method(fd) grid(100) boot(29) rseed(339648) gridci(20) endogenous(e1)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s006_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s006_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s006_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s006_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s006_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s006_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s006_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s006_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s007.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s007"
capture noisily xtdpthresh y , qx(q) collapse method(fd) grid(100) boot(29) rseed(137744) gridci(20) endogenous(e1 e2)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s007_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s007_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s007_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s007_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s007_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s007_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s007_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s007_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s008.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s008"
capture noisily xtdpthresh y x1 x2, qx(q) method(fd) grid(100) boot(29) rseed(726322) gridci(20) maxlag(2 6) endogenous(e1 e2)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s008_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s008_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s008_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s008_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s008_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s008_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s008_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s008_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s009.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s009"
capture noisily xtdpthresh y , qx(q) kink method(fd) grid(100) boot(29) rseed(819178) gridci(20) maxlag(2 6) endogenous(e1 e2)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s009_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s009_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s009_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s009_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s009_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s009_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s009_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s009_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s010.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s010"
capture noisily xtdpthresh y , qx(q) collapse noboot method(fod) grid(20) boot(29) rseed(830162) gridci(20) maxlag(2 6) endogenous(e1 e2)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s010_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s010_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s010_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s010_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s010_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s010_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s010_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s010_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s011.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s011"
capture noisily xtdpthresh y x1 x2, qx(q) noboot method(fd) grid(100) boot(29) rseed(740091) gridci(20) maxlag(3 5) endogenous(e1)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s011_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s011_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s011_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s011_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s011_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s011_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s011_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s011_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s012.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s012"
capture noisily xtdpthresh y x1 x2, qx(q) method(fod) grid(50) boot(29) rseed(731615) gridci(20) maxlag(2 4)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s012_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s012_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s012_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s012_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s012_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s012_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s012_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s012_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s013.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s013"
capture noisily xtdpthresh y x1, qx(q) method(fod) grid(50) boot(29) rseed(625707) gridci(20) maxlag(2 4)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s013_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s013_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s013_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s013_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s013_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s013_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s013_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s013_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s014.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s014"
capture noisily xtdpthresh y x1 x2, qx(q) kink method(fd) grid(20) boot(29) rseed(860977) gridci(20) endogenous(e1)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s014_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s014_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s014_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s014_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s014_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s014_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s014_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s014_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s015.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s015"
capture noisily xtdpthresh y x1 x2, qx(q) noboot method(fod) grid(100) boot(29) rseed(572513) gridci(20) maxlag(2 4) endogenous(e1 e2)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s015_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s015_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s015_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s015_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s015_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s015_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s015_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s015_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s016.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s016"
capture noisily xtdpthresh y x1 x2, qx(q) collapse method(fd) grid(20) boot(29) rseed(644616) gridci(20) maxlag(3 5)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s016_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s016_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s016_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s016_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s016_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s016_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s016_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s016_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s017.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s017"
capture noisily xtdpthresh y , qx(q) noboot method(fod) grid(50) boot(29) rseed(304924) gridci(20) maxlag(3 5) endogenous(e1 e2)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s017_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s017_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s017_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s017_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s017_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s017_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s017_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s017_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s018.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s018"
capture noisily xtdpthresh y , qx(q) collapse method(fod) grid(50) boot(29) rseed(286521) gridci(20) maxlag(2 6) endogenous(e1)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s018_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s018_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s018_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s018_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s018_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s018_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s018_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s018_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s019.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s019"
capture noisily xtdpthresh y x1, qx(q) kink td method(fd) grid(100) boot(29) rseed(525379) gridci(20) maxlag(2 4)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s019_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s019_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s019_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s019_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s019_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s019_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s019_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s019_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s020.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s020"
capture noisily xtdpthresh y , qx(q) td collapse noboot method(fd) grid(50) boot(29) rseed(686477) gridci(20)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s020_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s020_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s020_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s020_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s020_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s020_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s020_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s020_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s021.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s021"
capture noisily xtdpthresh y x1, qx(q) noboot method(fd) grid(100) boot(29) rseed(818279) gridci(20) maxlag(2 4) endogenous(e1 e2)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s021_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s021_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s021_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s021_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s021_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s021_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s021_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s021_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s022.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s022"
capture noisily xtdpthresh y , qx(q) collapse noboot method(fd) grid(50) boot(29) rseed(485574) gridci(20) maxlag(2 6) endogenous(e1 e2)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s022_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s022_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s022_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s022_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s022_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s022_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s022_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s022_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s023.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s023"
capture noisily xtdpthresh y , qx(q) collapse noboot method(fd) grid(100) boot(29) rseed(105405) gridci(20) maxlag(2 4) endogenous(e1)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s023_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s023_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s023_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s023_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s023_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s023_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s023_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s023_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s024.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s024"
capture noisily xtdpthresh y , qx(q) noboot method(fd) grid(20) boot(29) rseed(575701) gridci(20) endogenous(e1 e2)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s024_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s024_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s024_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s024_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s024_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s024_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s024_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s024_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s025.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s025"
capture noisily xtdpthresh y , qx(q) noboot method(fod) grid(50) boot(29) rseed(882994) gridci(20) maxlag(2 6) endogenous(e1)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s025_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s025_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s025_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s025_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s025_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s025_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s025_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s025_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s026.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s026"
capture noisily xtdpthresh y x1 x2, qx(q) method(fd) grid(100) boot(29) rseed(390483) gridci(20) maxlag(2 4)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s026_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s026_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s026_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s026_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s026_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s026_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s026_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s026_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s027.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s027"
capture noisily xtdpthresh y x1, qx(q) noboot method(fd) grid(20) boot(29) rseed(202682) gridci(20)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s027_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s027_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s027_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s027_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s027_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s027_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s027_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s027_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s028.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s028"
capture noisily xtdpthresh y , qx(q) td collapse method(fod) grid(100) boot(29) rseed(327492) gridci(20) maxlag(3 5) endogenous(e1 e2)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s028_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s028_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s028_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s028_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s028_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s028_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s028_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s028_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s029.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s029"
capture noisily xtdpthresh y x1 x2, qx(q) method(fd) grid(20) boot(29) rseed(155950) gridci(20) maxlag(2 4) endogenous(e1)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s029_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s029_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s029_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s029_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s029_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s029_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s029_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s029_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s030.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s030"
capture noisily xtdpthresh y , qx(q) method(fd) grid(20) boot(29) rseed(827990) gridci(20) maxlag(3 5) endogenous(e1)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s030_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s030_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s030_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s030_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s030_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s030_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s030_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s030_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s031.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s031"
capture noisily xtdpthresh y x1 x2, qx(q) collapse noboot method(fod) grid(100) boot(29) rseed(711216) gridci(20) maxlag(3 5)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s031_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s031_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s031_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s031_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s031_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s031_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s031_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s031_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s032.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s032"
capture noisily xtdpthresh y , qx(q) method(fd) grid(50) boot(29) rseed(965849) gridci(20) endogenous(e1)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s032_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s032_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s032_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s032_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s032_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s032_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s032_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s032_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s033.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s033"
capture noisily xtdpthresh y x1 x2, qx(q) noboot method(fd) grid(20) boot(29) rseed(27348) gridci(20) maxlag(2 4) endogenous(e1)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s033_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s033_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s033_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s033_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s033_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s033_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s033_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s033_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s034.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s034"
capture noisily xtdpthresh y x1 x2, qx(q) noboot method(fd) grid(100) boot(29) rseed(473434) gridci(20) maxlag(2 4) endogenous(e1 e2)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s034_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s034_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s034_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s034_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s034_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s034_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s034_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s034_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s035.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s035"
capture noisily xtdpthresh y , qx(q) kink method(fd) grid(50) boot(29) rseed(112676) gridci(20) maxlag(3 5) endogenous(e1 e2)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s035_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s035_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s035_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s035_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s035_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s035_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s035_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s035_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s036.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s036"
capture noisily xtdpthresh y x1, qx(q) td method(fd) grid(100) boot(29) rseed(147939) gridci(20) maxlag(2 6) endogenous(e1 e2)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s036_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s036_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s036_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s036_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s036_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s036_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s036_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s036_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s037.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s037"
capture noisily xtdpthresh y x1 x2, qx(q) td noboot method(fd) grid(50) boot(29) rseed(566920) gridci(20) endogenous(e1 e2)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s037_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s037_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s037_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s037_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s037_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s037_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s037_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s037_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s038.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s038"
capture noisily xtdpthresh y x1 x2, qx(q) method(fod) grid(50) boot(29) rseed(182275) gridci(20) maxlag(3 5)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s038_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s038_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s038_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s038_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s038_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s038_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s038_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s038_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s039.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s039"
capture noisily xtdpthresh y , qx(q) td collapse method(fod) grid(100) boot(29) rseed(979463) gridci(20) maxlag(3 5)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s039_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s039_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s039_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s039_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s039_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s039_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s039_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s039_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s040.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s040"
capture noisily xtdpthresh y x1 x2, qx(q) noboot method(fod) grid(50) boot(29) rseed(92643) gridci(20) maxlag(3 5) endogenous(e1 e2)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s040_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s040_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s040_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s040_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s040_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s040_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s040_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s040_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s041.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s041"
capture noisily xtdpthresh y x1, qx(q) noboot method(fod) grid(20) boot(29) rseed(240889) gridci(20)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s041_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s041_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s041_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s041_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s041_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s041_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s041_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s041_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s042.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s042"
capture noisily xtdpthresh y x1 x2, qx(q) kink method(fd) grid(20) boot(29) rseed(39401) gridci(20) endogenous(e1 e2)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s042_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s042_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s042_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s042_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s042_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s042_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s042_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s042_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s043.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s043"
capture noisily xtdpthresh y x1 x2, qx(q) td method(fod) grid(50) boot(29) rseed(614385) gridci(20) maxlag(3 5) endogenous(e1 e2)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s043_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s043_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s043_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s043_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s043_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s043_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s043_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s043_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s044.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s044"
capture noisily xtdpthresh y , qx(q) noboot method(fd) grid(20) boot(29) rseed(609) gridci(20) maxlag(3 5) endogenous(e1 e2)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s044_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s044_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s044_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s044_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s044_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s044_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s044_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s044_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s045.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s045"
capture noisily xtdpthresh y x1 x2, qx(q) td noboot method(fod) grid(50) boot(29) rseed(824706) gridci(20) endogenous(e1 e2)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s045_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s045_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s045_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s045_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s045_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s045_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s045_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s045_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s046.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s046"
capture noisily xtdpthresh y x1 x2, qx(q) collapse method(fd) grid(20) boot(29) rseed(62838) gridci(20) maxlag(3 5) endogenous(e1)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s046_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s046_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s046_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s046_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s046_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s046_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s046_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s046_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s047.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s047"
capture noisily xtdpthresh y x1, qx(q) kink td method(fd) grid(50) boot(29) rseed(381753) gridci(20) endogenous(e1)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s047_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s047_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s047_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s047_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s047_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s047_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s047_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s047_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s048.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s048"
capture noisily xtdpthresh y x1 x2, qx(q) td noboot method(fod) grid(100) boot(29) rseed(234878) gridci(20) maxlag(2 6)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s048_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s048_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s048_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s048_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s048_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s048_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s048_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s048_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s049.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s049"
capture noisily xtdpthresh y , qx(q) noboot method(fod) grid(20) boot(29) rseed(731212) gridci(20) maxlag(2 6) endogenous(e1 e2)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s049_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s049_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s049_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s049_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s049_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s049_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s049_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s049_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s050.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s050"
capture noisily xtdpthresh y , qx(q) noboot method(fod) grid(100) boot(29) rseed(302020) gridci(20)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s050_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s050_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s050_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s050_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s050_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s050_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s050_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s050_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s051.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s051"
capture noisily xtdpthresh y , qx(q) kink collapse noboot method(fd) grid(20) boot(29) rseed(93760) gridci(20) maxlag(2 6) endogenous(e1 e2)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s051_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s051_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s051_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s051_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s051_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s051_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s051_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s051_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s052.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s052"
capture noisily xtdpthresh y x1, qx(q) collapse noboot method(fod) grid(100) boot(29) rseed(69355) gridci(20) maxlag(3 5) endogenous(e1 e2)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s052_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s052_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s052_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s052_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s052_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s052_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s052_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s052_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s053.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s053"
capture noisily xtdpthresh y x1 x2, qx(q) collapse noboot method(fd) grid(20) boot(29) rseed(42626) gridci(20) maxlag(3 5) endogenous(e1 e2)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s053_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s053_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s053_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s053_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s053_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s053_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s053_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s053_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s054.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s054"
capture noisily xtdpthresh y x1 x2, qx(q) td noboot method(fod) grid(100) boot(29) rseed(414527) gridci(20) maxlag(2 4)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s054_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s054_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s054_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s054_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s054_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s054_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s054_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s054_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s055.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s055"
capture noisily xtdpthresh y , qx(q) td noboot method(fod) grid(20) boot(29) rseed(616036) gridci(20) endogenous(e1)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s055_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s055_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s055_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s055_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s055_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s055_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s055_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s055_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s056.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s056"
capture noisily xtdpthresh y x1, qx(q) method(fod) grid(50) boot(29) rseed(981566) gridci(20) maxlag(2 4) endogenous(e1)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s056_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s056_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s056_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s056_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s056_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s056_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s056_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s056_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s057.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s057"
capture noisily xtdpthresh y x1 x2, qx(q) collapse noboot method(fd) grid(20) boot(29) rseed(246396) gridci(20) maxlag(2 4) endogenous(e1 e2)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s057_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s057_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s057_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s057_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s057_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s057_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s057_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s057_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s058.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s058"
capture noisily xtdpthresh y , qx(q) noboot method(fod) grid(20) boot(29) rseed(248283) gridci(20)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s058_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s058_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s058_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s058_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s058_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s058_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s058_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s058_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s059.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s059"
capture noisily xtdpthresh y x1 x2, qx(q) collapse noboot method(fod) grid(20) boot(29) rseed(389619) gridci(20) maxlag(3 5)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s059_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s059_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s059_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s059_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s059_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s059_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s059_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s059_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s060.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s060"
capture noisily xtdpthresh y , qx(q) collapse noboot method(fod) grid(20) boot(29) rseed(486960) gridci(20) maxlag(2 4)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s060_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s060_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s060_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s060_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s060_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s060_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s060_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s060_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s061.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s061"
capture noisily xtdpthresh y x1 x2, qx(q) kink td collapse method(fd) grid(100) boot(29) rseed(619954) gridci(20) maxlag(3 5) endogenous(e1)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s061_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s061_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s061_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s061_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s061_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s061_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s061_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s061_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s062.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s062"
capture noisily xtdpthresh y x1, qx(q) kink td collapse noboot method(fd) grid(50) boot(29) rseed(332757) gridci(20) maxlag(3 5) endogenous(e1)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s062_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s062_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s062_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s062_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s062_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s062_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s062_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s062_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s063.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s063"
capture noisily xtdpthresh y x1, qx(q) noboot method(fod) grid(50) boot(29) rseed(531293) gridci(20) maxlag(3 5) endogenous(e1)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s063_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s063_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s063_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s063_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s063_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s063_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s063_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s063_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s064.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s064"
capture noisily xtdpthresh y x1 x2, qx(q) collapse noboot method(fd) grid(100) boot(29) rseed(562144) gridci(20) maxlag(3 5) endogenous(e1)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s064_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s064_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s064_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s064_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s064_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s064_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s064_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s064_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s065.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s065"
capture noisily xtdpthresh y , qx(q) td method(fod) grid(20) boot(29) rseed(560303) gridci(20) maxlag(2 6) endogenous(e1)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s065_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s065_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s065_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s065_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s065_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s065_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s065_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s065_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s066.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s066"
capture noisily xtdpthresh y , qx(q) kink method(fd) grid(100) boot(29) rseed(600896) gridci(20) maxlag(3 5)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s066_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s066_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s066_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s066_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s066_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s066_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s066_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s066_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s067.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s067"
capture noisily xtdpthresh y , qx(q) collapse noboot method(fd) grid(20) boot(29) rseed(401573) gridci(20) endogenous(e1)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s067_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s067_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s067_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s067_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s067_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s067_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s067_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s067_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s068.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s068"
capture noisily xtdpthresh y x1, qx(q) kink method(fd) grid(20) boot(29) rseed(879282) gridci(20) maxlag(3 5) endogenous(e1)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s068_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s068_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s068_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s068_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s068_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s068_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s068_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s068_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s069.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s069"
capture noisily xtdpthresh y x1 x2, qx(q) collapse noboot method(fod) grid(50) boot(29) rseed(659856) gridci(20) maxlag(2 4) endogenous(e1 e2)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s069_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s069_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s069_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s069_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s069_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s069_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s069_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s069_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s070.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s070"
capture noisily xtdpthresh y x1, qx(q) noboot method(fd) grid(50) boot(29) rseed(808490) gridci(20) maxlag(3 5) endogenous(e1 e2)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s070_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s070_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s070_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s070_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s070_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s070_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s070_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s070_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s071.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s071"
capture noisily xtdpthresh y , qx(q) collapse noboot method(fod) grid(20) boot(29) rseed(769786) gridci(20) maxlag(3 5)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s071_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s071_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s071_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s071_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s071_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s071_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s071_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s071_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s072.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s072"
capture noisily xtdpthresh y x1 x2, qx(q) collapse method(fd) grid(20) boot(29) rseed(773486) gridci(20)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s072_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s072_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s072_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s072_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s072_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s072_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s072_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s072_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s073.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s073"
capture noisily xtdpthresh y , qx(q) td collapse noboot method(fd) grid(50) boot(29) rseed(440305) gridci(20) maxlag(2 6) endogenous(e1 e2)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s073_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s073_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s073_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s073_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s073_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s073_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s073_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s073_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s074.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s074"
capture noisily xtdpthresh y , qx(q) kink td noboot method(fd) grid(50) boot(29) rseed(925228) gridci(20) maxlag(3 5) endogenous(e1 e2)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s074_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s074_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s074_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s074_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s074_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s074_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s074_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s074_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s075.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s075"
capture noisily xtdpthresh y x1 x2, qx(q) method(fod) grid(50) boot(29) rseed(479802) gridci(20) maxlag(2 4) endogenous(e1 e2)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s075_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s075_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s075_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s075_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s075_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s075_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s075_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s075_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s076.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s076"
capture noisily xtdpthresh y x1 x2, qx(q) noboot method(fd) grid(50) boot(29) rseed(709844) gridci(20) maxlag(2 6) endogenous(e1 e2)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s076_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s076_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s076_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s076_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s076_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s076_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s076_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s076_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s077.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s077"
capture noisily xtdpthresh y x1 x2, qx(q) kink collapse noboot method(fd) grid(50) boot(29) rseed(257110) gridci(20) maxlag(2 4) endogenous(e1)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s077_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s077_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s077_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s077_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s077_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s077_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s077_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s077_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s078.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s078"
capture noisily xtdpthresh y x1 x2, qx(q) td collapse method(fod) grid(50) boot(29) rseed(435643) gridci(20) maxlag(2 4)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s078_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s078_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s078_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s078_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s078_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s078_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s078_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s078_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s079.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s079"
capture noisily xtdpthresh y x1 x2, qx(q) method(fd) grid(50) boot(29) rseed(475394) gridci(20)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s079_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s079_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s079_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s079_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s079_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s079_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s079_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s079_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s080.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s080"
capture noisily xtdpthresh y , qx(q) method(fod) grid(100) boot(29) rseed(921985) gridci(20) maxlag(2 4)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s080_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s080_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s080_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s080_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s080_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s080_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s080_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s080_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s081.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s081"
capture noisily xtdpthresh y x1, qx(q) noboot method(fd) grid(100) boot(29) rseed(225202) gridci(20)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s081_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s081_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s081_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s081_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s081_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s081_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s081_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s081_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s082.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s082"
capture noisily xtdpthresh y x1, qx(q) collapse noboot method(fd) grid(20) boot(29) rseed(583635) gridci(20) maxlag(3 5) endogenous(e1 e2)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s082_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s082_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s082_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s082_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s082_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s082_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s082_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s082_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s083.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s083"
capture noisily xtdpthresh y x1 x2, qx(q) kink td collapse noboot method(fd) grid(50) boot(29) rseed(663408) gridci(20) maxlag(2 6) endogenous(e1)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s083_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s083_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s083_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s083_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s083_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s083_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s083_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s083_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s084.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s084"
capture noisily xtdpthresh y , qx(q) method(fd) grid(50) boot(29) rseed(614583) gridci(20) maxlag(2 6)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s084_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s084_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s084_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s084_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s084_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s084_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s084_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s084_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s085.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s085"
capture noisily xtdpthresh y x1 x2, qx(q) collapse method(fod) grid(100) boot(29) rseed(352313) gridci(20) maxlag(2 6)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s085_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s085_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s085_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s085_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s085_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s085_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s085_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s085_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s086.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s086"
capture noisily xtdpthresh y , qx(q) collapse noboot method(fd) grid(100) boot(29) rseed(735539) gridci(20) maxlag(2 4) endogenous(e1)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s086_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s086_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s086_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s086_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s086_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s086_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s086_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s086_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s087.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s087"
capture noisily xtdpthresh y , qx(q) td collapse noboot method(fod) grid(100) boot(29) rseed(873927) gridci(20) maxlag(2 6) endogenous(e1 e2)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s087_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s087_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s087_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s087_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s087_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s087_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s087_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s087_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s088.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s088"
capture noisily xtdpthresh y x1 x2, qx(q) noboot method(fod) grid(20) boot(29) rseed(447309) gridci(20) maxlag(2 4)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s088_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s088_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s088_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s088_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s088_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s088_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s088_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s088_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s089.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s089"
capture noisily xtdpthresh y , qx(q) noboot method(fd) grid(50) boot(29) rseed(484364) gridci(20) maxlag(2 4) endogenous(e1)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s089_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s089_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s089_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s089_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s089_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s089_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s089_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s089_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s090.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s090"
capture noisily xtdpthresh y x1 x2, qx(q) noboot method(fod) grid(50) boot(29) rseed(715316) gridci(20) maxlag(3 5)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s090_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s090_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s090_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s090_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s090_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s090_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s090_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s090_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s091.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s091"
capture noisily xtdpthresh y x1, qx(q) td collapse noboot method(fd) grid(20) boot(29) rseed(265909) gridci(20) maxlag(2 6)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s091_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s091_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s091_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s091_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s091_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s091_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s091_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s091_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s092.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s092"
capture noisily xtdpthresh y x1, qx(q) kink collapse method(fd) grid(50) boot(29) rseed(314887) gridci(20) endogenous(e1)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s092_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s092_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s092_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s092_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s092_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s092_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s092_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s092_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s093.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s093"
capture noisily xtdpthresh y x1, qx(q) collapse noboot method(fod) grid(100) boot(29) rseed(22632) gridci(20) maxlag(2 6)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s093_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s093_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s093_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s093_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s093_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s093_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s093_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s093_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s094.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s094"
capture noisily xtdpthresh y , qx(q) method(fd) grid(20) boot(29) rseed(405440) gridci(20) endogenous(e1)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s094_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s094_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s094_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s094_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s094_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s094_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s094_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s094_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s095.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s095"
capture noisily xtdpthresh y x1, qx(q) method(fd) grid(20) boot(29) rseed(615656) gridci(20) maxlag(2 6) endogenous(e1)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s095_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s095_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s095_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s095_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s095_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s095_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s095_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s095_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s096.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s096"
capture noisily xtdpthresh y x1 x2, qx(q) noboot method(fod) grid(100) boot(29) rseed(551000) gridci(20) maxlag(2 4)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s096_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s096_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s096_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s096_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s096_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s096_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s096_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s096_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s097.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s097"
capture noisily xtdpthresh y x1 x2, qx(q) kink collapse noboot method(fd) grid(20) boot(29) rseed(762724) gridci(20) maxlag(2 6)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s097_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s097_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s097_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s097_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s097_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s097_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s097_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s097_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s098.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s098"
capture noisily xtdpthresh y , qx(q) collapse noboot method(fd) grid(50) boot(29) rseed(221282) gridci(20) maxlag(2 6)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s098_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s098_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s098_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s098_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s098_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s098_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s098_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s098_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s099.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s099"
capture noisily xtdpthresh y x1, qx(q) kink noboot method(fd) grid(100) boot(29) rseed(491471) gridci(20) maxlag(2 4) endogenous(e1 e2)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s099_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s099_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s099_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s099_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s099_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s099_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s099_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s099_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s100.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s100"
capture noisily xtdpthresh y , qx(q) td collapse noboot method(fd) grid(50) boot(29) rseed(226822) gridci(20) maxlag(2 4) endogenous(e1 e2)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s100_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s100_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s100_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s100_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s100_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s100_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s100_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s100_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s101.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s101"
capture noisily xtdpthresh y , qx(q) collapse method(fod) grid(100) boot(29) rseed(879436) gridci(20) maxlag(2 4) endogenous(e1 e2)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s101_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s101_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s101_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s101_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s101_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s101_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s101_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s101_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s102.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s102"
capture noisily xtdpthresh y , qx(q) collapse noboot method(fod) grid(20) boot(29) rseed(166295) gridci(20) maxlag(2 4) endogenous(e1)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s102_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s102_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s102_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s102_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s102_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s102_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s102_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s102_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s103.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s103"
capture noisily xtdpthresh y , qx(q) td noboot method(fd) grid(20) boot(29) rseed(792932) gridci(20)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s103_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s103_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s103_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s103_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s103_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s103_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s103_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s103_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s104.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s104"
capture noisily xtdpthresh y x1 x2, qx(q) td collapse noboot method(fod) grid(100) boot(29) rseed(357798) gridci(20) maxlag(3 5) endogenous(e1 e2)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s104_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s104_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s104_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s104_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s104_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s104_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s104_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s104_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s105.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s105"
capture noisily xtdpthresh y , qx(q) method(fd) grid(50) boot(29) rseed(251825) gridci(20) maxlag(2 4) endogenous(e1 e2)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s105_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s105_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s105_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s105_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s105_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s105_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s105_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s105_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s106.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s106"
capture noisily xtdpthresh y x1 x2, qx(q) method(fod) grid(100) boot(29) rseed(320764) gridci(20) maxlag(2 6) endogenous(e1)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s106_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s106_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s106_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s106_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s106_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s106_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s106_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s106_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s107.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s107"
capture noisily xtdpthresh y , qx(q) noboot method(fod) grid(20) boot(29) rseed(214836) gridci(20)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s107_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s107_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s107_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s107_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s107_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s107_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s107_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s107_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s108.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s108"
capture noisily xtdpthresh y x1 x2, qx(q) noboot method(fd) grid(50) boot(29) rseed(354190) gridci(20) endogenous(e1 e2)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s108_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s108_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s108_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s108_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s108_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s108_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s108_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s108_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s109.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s109"
capture noisily xtdpthresh y , qx(q) td noboot method(fd) grid(100) boot(29) rseed(271814) gridci(20) endogenous(e1)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s109_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s109_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s109_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s109_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s109_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s109_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s109_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s109_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s110.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s110"
capture noisily xtdpthresh y x1, qx(q) method(fod) grid(50) boot(29) rseed(357803) gridci(20) endogenous(e1)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s110_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s110_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s110_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s110_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s110_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s110_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s110_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s110_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s111.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s111"
capture noisily xtdpthresh y x1, qx(q) td collapse method(fod) grid(100) boot(29) rseed(865992) gridci(20) maxlag(2 4) endogenous(e1)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s111_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s111_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s111_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s111_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s111_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s111_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s111_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s111_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s112.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s112"
capture noisily xtdpthresh y x1, qx(q) collapse noboot method(fd) grid(20) boot(29) rseed(154628) gridci(20) maxlag(2 6)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s112_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s112_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s112_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s112_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s112_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s112_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s112_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s112_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s113.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s113"
capture noisily xtdpthresh y x1 x2, qx(q) collapse noboot method(fod) grid(100) boot(29) rseed(638986) gridci(20) maxlag(2 4)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s113_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s113_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s113_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s113_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s113_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s113_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s113_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s113_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s114.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s114"
capture noisily xtdpthresh y x1, qx(q) collapse method(fod) grid(100) boot(29) rseed(97359) gridci(20) maxlag(2 4) endogenous(e1 e2)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s114_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s114_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s114_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s114_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s114_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s114_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s114_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s114_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s115.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s115"
capture noisily xtdpthresh y , qx(q) collapse noboot method(fod) grid(100) boot(29) rseed(772217) gridci(20) maxlag(3 5) endogenous(e1 e2)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s115_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s115_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s115_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s115_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s115_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s115_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s115_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s115_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s116.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s116"
capture noisily xtdpthresh y x1, qx(q) td collapse noboot method(fod) grid(50) boot(29) rseed(341981) gridci(20) maxlag(2 6) endogenous(e1 e2)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s116_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s116_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s116_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s116_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s116_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s116_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s116_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s116_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s117.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s117"
capture noisily xtdpthresh y , qx(q) collapse noboot method(fd) grid(50) boot(29) rseed(610754) gridci(20) maxlag(3 5) endogenous(e1)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s117_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s117_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s117_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s117_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s117_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s117_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s117_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s117_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s118.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s118"
capture noisily xtdpthresh y x1 x2, qx(q) noboot method(fd) grid(20) boot(29) rseed(642327) gridci(20) maxlag(3 5) endogenous(e1)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s118_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s118_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s118_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s118_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s118_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s118_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s118_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s118_ci_grid.csv", st_matrix("e(ci_grid)"))
}

import delimited using "../out/stress_s119.csv", clear case(preserve) asdouble
xtset id t
display "@@CASE s119"
capture noisily xtdpthresh y , qx(q) kink td method(fd) grid(20) boot(29) rseed(242269) gridci(20) maxlag(2 4) endogenous(e1 e2)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/st_s119_sc.csv", (pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_switch)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(level)"), pyx_sc("e(pval_lin)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_p)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_draws)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(joint_vce)"), pyx_sc("e(vce_applied)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(kink_refined)"), pyx_sc("e(rseed)")))
    mata: pyx_export("../out/st_s119_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/st_s119_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/st_s119_V_cond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/st_s119_b_upper.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/st_s119_V_upper.csv", st_matrix("e(V_upper)"))
    mata: pyx_export("../out/st_s119_ci_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/st_s119_ci_grid.csv", st_matrix("e(ci_grid)"))
}

exit, clear
