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
egen double peer_q = mean(tobin_q), by(year)
display "@@CASE help_maxlag_3_8"
capture noisily xtdpthresh invest , qx(debt) collapse noboot maxlag(3 8) endogenous(cashflow tobin_q debt)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/pc_help_maxlag_3_8_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(kink_refined)"), pyx_sc("e(gamma_stage1)"), pyx_sc("e(refine_iterations)"), pyx_sc("e(refine_added)"), pyx_sc("e(grid_effective)"), pyx_sc("e(N)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_units)")))
    mata: pyx_export("../out/pc_help_maxlag_3_8_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/pc_help_maxlag_3_8_vc.csv", st_matrix("e(V_cond)"))
}

use "../data/invest.dta", clear
xtset firm year
egen double peer_q = mean(tobin_q), by(year)
display "@@CASE help_maxlag_2_10"
capture noisily xtdpthresh invest , qx(debt) collapse noboot maxlag(2 10) endogenous(cashflow tobin_q debt)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/pc_help_maxlag_2_10_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(kink_refined)"), pyx_sc("e(gamma_stage1)"), pyx_sc("e(refine_iterations)"), pyx_sc("e(refine_added)"), pyx_sc("e(grid_effective)"), pyx_sc("e(N)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_units)")))
    mata: pyx_export("../out/pc_help_maxlag_2_10_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/pc_help_maxlag_2_10_vc.csv", st_matrix("e(V_cond)"))
}

use "../data/invest.dta", clear
xtset firm year
egen double peer_q = mean(tobin_q), by(year)
display "@@CASE help_kink"
capture noisily xtdpthresh invest , qx(debt) kink collapse noboot maxlag(3 8) endogenous(cashflow tobin_q debt)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/pc_help_kink_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(kink_refined)"), pyx_sc("e(gamma_stage1)"), pyx_sc("e(refine_iterations)"), pyx_sc("e(refine_added)"), pyx_sc("e(grid_effective)"), pyx_sc("e(N)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_units)")))
    mata: pyx_export("../out/pc_help_kink_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/pc_help_kink_vc.csv", st_matrix("e(V_cond)"))
}

use "../data/invest.dta", clear
xtset firm year
egen double peer_q = mean(tobin_q), by(year)
display "@@CASE help_iv_peer"
capture noisily xtdpthresh invest , qx(debt) collapse noboot maxlag(3 8) endogenous(cashflow tobin_q debt) iv(L2.peer_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/pc_help_iv_peer_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(kink_refined)"), pyx_sc("e(gamma_stage1)"), pyx_sc("e(refine_iterations)"), pyx_sc("e(refine_added)"), pyx_sc("e(grid_effective)"), pyx_sc("e(N)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_units)")))
    mata: pyx_export("../out/pc_help_iv_peer_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/pc_help_iv_peer_vc.csv", st_matrix("e(V_cond)"))
}

use "../data/invest.dta", clear
xtset firm year
egen double peer_q = mean(tobin_q), by(year)
drop if mod(firm + 3*year, 11) == 0
display "@@CASE help_unbalanced_gaps"
capture noisily xtdpthresh invest , qx(debt) collapse noboot maxlag(3 8) endogenous(cashflow tobin_q debt)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/pc_help_unbalanced_gaps_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(kink_refined)"), pyx_sc("e(gamma_stage1)"), pyx_sc("e(refine_iterations)"), pyx_sc("e(refine_added)"), pyx_sc("e(grid_effective)"), pyx_sc("e(N)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_units)")))
    mata: pyx_export("../out/pc_help_unbalanced_gaps_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/pc_help_unbalanced_gaps_vc.csv", st_matrix("e(V_cond)"))
}

use "../data/invest.dta", clear
xtset firm year
egen double peer_q = mean(tobin_q), by(year)
drop if firm <= 10 & year > 1973
drop if firm >= 11 & firm <= 20 & year > 1974
display "@@CASE help_unbalanced_short"
capture noisily xtdpthresh invest , qx(debt) collapse noboot maxlag(3 8) endogenous(cashflow tobin_q debt)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/pc_help_unbalanced_short_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(kink_refined)"), pyx_sc("e(gamma_stage1)"), pyx_sc("e(refine_iterations)"), pyx_sc("e(refine_added)"), pyx_sc("e(grid_effective)"), pyx_sc("e(N)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_units)")))
    mata: pyx_export("../out/pc_help_unbalanced_short_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/pc_help_unbalanced_short_vc.csv", st_matrix("e(V_cond)"))
}

use "../data/invest.dta", clear
xtset firm year
egen double peer_q = mean(tobin_q), by(year)
drop if firm >= 11 & firm <= 40 & mod(year, 2) == 0
display "@@CASE help_unbalanced_alternate"
capture noisily xtdpthresh invest , qx(debt) collapse noboot maxlag(3 8) endogenous(cashflow tobin_q debt)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/pc_help_unbalanced_alternate_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(kink_refined)"), pyx_sc("e(gamma_stage1)"), pyx_sc("e(refine_iterations)"), pyx_sc("e(refine_added)"), pyx_sc("e(grid_effective)"), pyx_sc("e(N)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_units)")))
    mata: pyx_export("../out/pc_help_unbalanced_alternate_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/pc_help_unbalanced_alternate_vc.csv", st_matrix("e(V_cond)"))
}

use "../data/invest.dta", clear
xtset firm year
egen double peer_q = mean(tobin_q), by(year)
display "@@CASE help_refine"
capture noisily xtdpthresh invest , qx(debt) collapse noboot refine(5) maxlag(3 8) endogenous(cashflow tobin_q debt)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/pc_help_refine_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(kink_refined)"), pyx_sc("e(gamma_stage1)"), pyx_sc("e(refine_iterations)"), pyx_sc("e(refine_added)"), pyx_sc("e(grid_effective)"), pyx_sc("e(N)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_units)")))
    mata: pyx_export("../out/pc_help_refine_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/pc_help_refine_vc.csv", st_matrix("e(V_cond)"))
}

use "../data/invest.dta", clear
xtset firm year
egen double peer_q = mean(tobin_q), by(year)
display "@@CASE help_quantile_grid"
capture noisily xtdpthresh invest , qx(debt) collapse noboot gridtype(quantile) maxlag(3 8) endogenous(cashflow tobin_q debt)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/pc_help_quantile_grid_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(kink_refined)"), pyx_sc("e(gamma_stage1)"), pyx_sc("e(refine_iterations)"), pyx_sc("e(refine_added)"), pyx_sc("e(grid_effective)"), pyx_sc("e(N)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_units)")))
    mata: pyx_export("../out/pc_help_quantile_grid_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/pc_help_quantile_grid_vc.csv", st_matrix("e(V_cond)"))
}

use "../data/invest.dta", clear
xtset firm year
egen double peer_q = mean(tobin_q), by(year)
display "@@CASE help_grid_200"
capture noisily xtdpthresh invest , qx(debt) collapse noboot grid(200) maxlag(3 8) endogenous(cashflow tobin_q debt)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/pc_help_grid_200_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(kink_refined)"), pyx_sc("e(gamma_stage1)"), pyx_sc("e(refine_iterations)"), pyx_sc("e(refine_added)"), pyx_sc("e(grid_effective)"), pyx_sc("e(N)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_units)")))
    mata: pyx_export("../out/pc_help_grid_200_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/pc_help_grid_200_vc.csv", st_matrix("e(V_cond)"))
}

use "../data/invest.dta", clear
xtset firm year
egen double peer_q = mean(tobin_q), by(year)
display "@@CASE default_instruments"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/pc_default_instruments_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(kink_refined)"), pyx_sc("e(gamma_stage1)"), pyx_sc("e(refine_iterations)"), pyx_sc("e(refine_added)"), pyx_sc("e(grid_effective)"), pyx_sc("e(N)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_units)")))
    mata: pyx_export("../out/pc_default_instruments_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/pc_default_instruments_vc.csv", st_matrix("e(V_cond)"))
}

use "../data/invest.dta", clear
xtset firm year
egen double peer_q = mean(tobin_q), by(year)
display "@@CASE static_default"
capture noisily xtdpthresh invest cashflow L.tobin_q, qx(debt) static noboot
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/pc_static_default_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(kink_refined)"), pyx_sc("e(gamma_stage1)"), pyx_sc("e(refine_iterations)"), pyx_sc("e(refine_added)"), pyx_sc("e(grid_effective)"), pyx_sc("e(N)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_units)")))
    mata: pyx_export("../out/pc_static_default_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/pc_static_default_vc.csv", st_matrix("e(V_cond)"))
}

use "../data/invest.dta", clear
xtset firm year
egen double peer_q = mean(tobin_q), by(year)
display "@@CASE mixed_roles"
capture noisily xtdpthresh invest cashflow, qx(debt) collapse noboot maxlag(2 8) endogenous(debt) predetermined(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/pc_mixed_roles_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(kink_refined)"), pyx_sc("e(gamma_stage1)"), pyx_sc("e(refine_iterations)"), pyx_sc("e(refine_added)"), pyx_sc("e(grid_effective)"), pyx_sc("e(N)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_units)")))
    mata: pyx_export("../out/pc_mixed_roles_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/pc_mixed_roles_vc.csv", st_matrix("e(V_cond)"))
}

use "../data/invest.dta", clear
xtset firm year
egen double peer_q = mean(tobin_q), by(year)
display "@@CASE kink_default_instruments"
capture noisily xtdpthresh invest cashflow, qx(debt) kink noboot endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/pc_kink_default_instruments_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(kink_refined)"), pyx_sc("e(gamma_stage1)"), pyx_sc("e(refine_iterations)"), pyx_sc("e(refine_added)"), pyx_sc("e(grid_effective)"), pyx_sc("e(N)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_units)")))
    mata: pyx_export("../out/pc_kink_default_instruments_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/pc_kink_default_instruments_vc.csv", st_matrix("e(V_cond)"))
}

exit, clear
