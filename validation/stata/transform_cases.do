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
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
display "@@CASE fod_endog"
capture noisily xtdpthresh invest cashflow, qx(debt) exportgmm noboot method(fod) grid(30) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/tc_fod_endog_sc.csv", (pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_iv_dep_near)"), pyx_sc("e(dep_res)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(N)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(kink_refined)"), pyx_sc("e(gamma_stage1)"), pyx_sc("e(refine_iterations)"), pyx_sc("e(refine_added)"), pyx_sc("e(grid_effective)")))
    mata: pyx_export("../out/tc_fod_endog_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/tc_fod_endog_vc.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/tc_fod_endog_z.csv", xdpt_best_Z_f)
    mata: pyx_export("../out/tc_fod_endog_x.csv", xdpt_best_X_f)
    mata: pyx_export("../out/tc_fod_endog_a.csv", xdpt_best_A)
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
display "@@CASE fod_exog_only"
capture noisily xtdpthresh invest cashflow, qx(debt) exportgmm noboot method(fod) grid(30)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/tc_fod_exog_only_sc.csv", (pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_iv_dep_near)"), pyx_sc("e(dep_res)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(N)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(kink_refined)"), pyx_sc("e(gamma_stage1)"), pyx_sc("e(refine_iterations)"), pyx_sc("e(refine_added)"), pyx_sc("e(grid_effective)")))
    mata: pyx_export("../out/tc_fod_exog_only_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/tc_fod_exog_only_vc.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/tc_fod_exog_only_z.csv", xdpt_best_Z_f)
    mata: pyx_export("../out/tc_fod_exog_only_x.csv", xdpt_best_X_f)
    mata: pyx_export("../out/tc_fod_exog_only_a.csv", xdpt_best_A)
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
display "@@CASE fod_predet"
capture noisily xtdpthresh invest cashflow, qx(debt) exportgmm noboot method(fod) grid(30) predetermined(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/tc_fod_predet_sc.csv", (pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_iv_dep_near)"), pyx_sc("e(dep_res)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(N)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(kink_refined)"), pyx_sc("e(gamma_stage1)"), pyx_sc("e(refine_iterations)"), pyx_sc("e(refine_added)"), pyx_sc("e(grid_effective)")))
    mata: pyx_export("../out/tc_fod_predet_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/tc_fod_predet_vc.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/tc_fod_predet_z.csv", xdpt_best_Z_f)
    mata: pyx_export("../out/tc_fod_predet_x.csv", xdpt_best_X_f)
    mata: pyx_export("../out/tc_fod_predet_a.csv", xdpt_best_A)
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
display "@@CASE fod_static"
capture noisily xtdpthresh invest cashflow L.tobin_q, qx(debt) static exportgmm noboot method(fod) grid(30)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/tc_fod_static_sc.csv", (pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_iv_dep_near)"), pyx_sc("e(dep_res)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(N)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(kink_refined)"), pyx_sc("e(gamma_stage1)"), pyx_sc("e(refine_iterations)"), pyx_sc("e(refine_added)"), pyx_sc("e(grid_effective)")))
    mata: pyx_export("../out/tc_fod_static_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/tc_fod_static_vc.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/tc_fod_static_z.csv", xdpt_best_Z_f)
    mata: pyx_export("../out/tc_fod_static_x.csv", xdpt_best_X_f)
    mata: pyx_export("../out/tc_fod_static_a.csv", xdpt_best_A)
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
display "@@CASE fod_collapse"
capture noisily xtdpthresh invest cashflow, qx(debt) collapse exportgmm noboot method(fod) grid(30) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/tc_fod_collapse_sc.csv", (pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_iv_dep_near)"), pyx_sc("e(dep_res)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(N)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(kink_refined)"), pyx_sc("e(gamma_stage1)"), pyx_sc("e(refine_iterations)"), pyx_sc("e(refine_added)"), pyx_sc("e(grid_effective)")))
    mata: pyx_export("../out/tc_fod_collapse_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/tc_fod_collapse_vc.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/tc_fod_collapse_z.csv", xdpt_best_Z_f)
    mata: pyx_export("../out/tc_fod_collapse_x.csv", xdpt_best_X_f)
    mata: pyx_export("../out/tc_fod_collapse_a.csv", xdpt_best_A)
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
display "@@CASE fod_maxlag"
capture noisily xtdpthresh invest cashflow, qx(debt) exportgmm noboot method(fod) grid(30) maxlag(2 5) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/tc_fod_maxlag_sc.csv", (pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_iv_dep_near)"), pyx_sc("e(dep_res)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(N)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(kink_refined)"), pyx_sc("e(gamma_stage1)"), pyx_sc("e(refine_iterations)"), pyx_sc("e(refine_added)"), pyx_sc("e(grid_effective)")))
    mata: pyx_export("../out/tc_fod_maxlag_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/tc_fod_maxlag_vc.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/tc_fod_maxlag_z.csv", xdpt_best_Z_f)
    mata: pyx_export("../out/tc_fod_maxlag_x.csv", xdpt_best_X_f)
    mata: pyx_export("../out/tc_fod_maxlag_a.csv", xdpt_best_A)
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
display "@@CASE fod_iv"
capture noisily xtdpthresh invest cashflow, qx(debt) exportgmm noboot method(fod) grid(30) endogenous(tobin_q) iv(z1 z2)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/tc_fod_iv_sc.csv", (pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_iv_dep_near)"), pyx_sc("e(dep_res)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(N)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(kink_refined)"), pyx_sc("e(gamma_stage1)"), pyx_sc("e(refine_iterations)"), pyx_sc("e(refine_added)"), pyx_sc("e(grid_effective)")))
    mata: pyx_export("../out/tc_fod_iv_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/tc_fod_iv_vc.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/tc_fod_iv_z.csv", xdpt_best_Z_f)
    mata: pyx_export("../out/tc_fod_iv_x.csv", xdpt_best_X_f)
    mata: pyx_export("../out/tc_fod_iv_a.csv", xdpt_best_A)
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
display "@@CASE fod_kink"
capture noisily xtdpthresh invest cashflow, qx(debt) kink exportgmm noboot method(fod) grid(30) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/tc_fod_kink_sc.csv", (pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_iv_dep_near)"), pyx_sc("e(dep_res)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(N)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(kink_refined)"), pyx_sc("e(gamma_stage1)"), pyx_sc("e(refine_iterations)"), pyx_sc("e(refine_added)"), pyx_sc("e(grid_effective)")))
    mata: pyx_export("../out/tc_fod_kink_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/tc_fod_kink_vc.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/tc_fod_kink_z.csv", xdpt_best_Z_f)
    mata: pyx_export("../out/tc_fod_kink_x.csv", xdpt_best_X_f)
    mata: pyx_export("../out/tc_fod_kink_a.csv", xdpt_best_A)
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
display "@@CASE fod_refine"
capture noisily xtdpthresh invest cashflow, qx(debt) exportgmm noboot method(fod) grid(15) refine(2) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/tc_fod_refine_sc.csv", (pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_iv_dep_near)"), pyx_sc("e(dep_res)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(N)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(kink_refined)"), pyx_sc("e(gamma_stage1)"), pyx_sc("e(refine_iterations)"), pyx_sc("e(refine_added)"), pyx_sc("e(grid_effective)")))
    mata: pyx_export("../out/tc_fod_refine_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/tc_fod_refine_vc.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/tc_fod_refine_z.csv", xdpt_best_Z_f)
    mata: pyx_export("../out/tc_fod_refine_x.csv", xdpt_best_X_f)
    mata: pyx_export("../out/tc_fod_refine_a.csv", xdpt_best_A)
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
display "@@CASE fod_nocenter"
capture noisily xtdpthresh invest cashflow, qx(debt) exportgmm noboot nocenter method(fod) grid(30) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/tc_fod_nocenter_sc.csv", (pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_iv_dep_near)"), pyx_sc("e(dep_res)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(N)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(kink_refined)"), pyx_sc("e(gamma_stage1)"), pyx_sc("e(refine_iterations)"), pyx_sc("e(refine_added)"), pyx_sc("e(grid_effective)")))
    mata: pyx_export("../out/tc_fod_nocenter_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/tc_fod_nocenter_vc.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/tc_fod_nocenter_z.csv", xdpt_best_Z_f)
    mata: pyx_export("../out/tc_fod_nocenter_x.csv", xdpt_best_X_f)
    mata: pyx_export("../out/tc_fod_nocenter_a.csv", xdpt_best_A)
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
drop if mod(firm + 3*year, 11) == 0
display "@@CASE fod_gaps"
capture noisily xtdpthresh invest cashflow, qx(debt) exportgmm noboot method(fod) grid(30) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/tc_fod_gaps_sc.csv", (pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_iv_dep_near)"), pyx_sc("e(dep_res)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(N)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(kink_refined)"), pyx_sc("e(gamma_stage1)"), pyx_sc("e(refine_iterations)"), pyx_sc("e(refine_added)"), pyx_sc("e(grid_effective)")))
    mata: pyx_export("../out/tc_fod_gaps_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/tc_fod_gaps_vc.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/tc_fod_gaps_z.csv", xdpt_best_Z_f)
    mata: pyx_export("../out/tc_fod_gaps_x.csv", xdpt_best_X_f)
    mata: pyx_export("../out/tc_fod_gaps_a.csv", xdpt_best_A)
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
replace cashflow = . if mod(firm*year, 13) == 0
display "@@CASE fod_missing_x"
capture noisily xtdpthresh invest cashflow, qx(debt) exportgmm noboot method(fod) grid(30) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/tc_fod_missing_x_sc.csv", (pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_iv_dep_near)"), pyx_sc("e(dep_res)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(N)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(kink_refined)"), pyx_sc("e(gamma_stage1)"), pyx_sc("e(refine_iterations)"), pyx_sc("e(refine_added)"), pyx_sc("e(grid_effective)")))
    mata: pyx_export("../out/tc_fod_missing_x_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/tc_fod_missing_x_vc.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/tc_fod_missing_x_z.csv", xdpt_best_Z_f)
    mata: pyx_export("../out/tc_fod_missing_x_x.csv", xdpt_best_X_f)
    mata: pyx_export("../out/tc_fod_missing_x_a.csv", xdpt_best_A)
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
drop if firm <= 10 & year > 1973
drop if firm >= 11 & firm <= 20 & year > 1974
display "@@CASE fod_short_units"
capture noisily xtdpthresh invest cashflow, qx(debt) exportgmm noboot method(fod) grid(30) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/tc_fod_short_units_sc.csv", (pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_iv_dep_near)"), pyx_sc("e(dep_res)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(N)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(kink_refined)"), pyx_sc("e(gamma_stage1)"), pyx_sc("e(refine_iterations)"), pyx_sc("e(refine_added)"), pyx_sc("e(grid_effective)")))
    mata: pyx_export("../out/tc_fod_short_units_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/tc_fod_short_units_vc.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/tc_fod_short_units_z.csv", xdpt_best_Z_f)
    mata: pyx_export("../out/tc_fod_short_units_x.csv", xdpt_best_X_f)
    mata: pyx_export("../out/tc_fod_short_units_a.csv", xdpt_best_A)
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
drop if firm >= 11 & firm <= 40 & mod(year, 2) == 0
display "@@CASE fod_alternate_years"
capture noisily xtdpthresh invest cashflow, qx(debt) exportgmm noboot method(fod) grid(30) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/tc_fod_alternate_years_sc.csv", (pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_iv_dep_near)"), pyx_sc("e(dep_res)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(N)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(kink_refined)"), pyx_sc("e(gamma_stage1)"), pyx_sc("e(refine_iterations)"), pyx_sc("e(refine_added)"), pyx_sc("e(grid_effective)")))
    mata: pyx_export("../out/tc_fod_alternate_years_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/tc_fod_alternate_years_vc.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/tc_fod_alternate_years_z.csv", xdpt_best_Z_f)
    mata: pyx_export("../out/tc_fod_alternate_years_x.csv", xdpt_best_X_f)
    mata: pyx_export("../out/tc_fod_alternate_years_a.csv", xdpt_best_A)
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
replace tobin_q = . if firm <= 50 & year == 1975
display "@@CASE fod_missing_endog"
capture noisily xtdpthresh invest cashflow, qx(debt) exportgmm noboot method(fod) grid(30) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/tc_fod_missing_endog_sc.csv", (pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_iv_dep_near)"), pyx_sc("e(dep_res)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(N)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(kink_refined)"), pyx_sc("e(gamma_stage1)"), pyx_sc("e(refine_iterations)"), pyx_sc("e(refine_added)"), pyx_sc("e(grid_effective)")))
    mata: pyx_export("../out/tc_fod_missing_endog_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/tc_fod_missing_endog_vc.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/tc_fod_missing_endog_z.csv", xdpt_best_Z_f)
    mata: pyx_export("../out/tc_fod_missing_endog_x.csv", xdpt_best_X_f)
    mata: pyx_export("../out/tc_fod_missing_endog_a.csv", xdpt_best_A)
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
display "@@CASE fd_td_endog"
capture noisily xtdpthresh invest cashflow, qx(debt) td exportgmm noboot grid(30) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/tc_fd_td_endog_sc.csv", (pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_iv_dep_near)"), pyx_sc("e(dep_res)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(N)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(kink_refined)"), pyx_sc("e(gamma_stage1)"), pyx_sc("e(refine_iterations)"), pyx_sc("e(refine_added)"), pyx_sc("e(grid_effective)")))
    mata: pyx_export("../out/tc_fd_td_endog_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/tc_fd_td_endog_vc.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/tc_fd_td_endog_z.csv", xdpt_best_Z_f)
    mata: pyx_export("../out/tc_fd_td_endog_x.csv", xdpt_best_X_f)
    mata: pyx_export("../out/tc_fd_td_endog_a.csv", xdpt_best_A)
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
display "@@CASE fd_td_exog_only"
capture noisily xtdpthresh invest cashflow, qx(debt) td exportgmm noboot grid(30)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/tc_fd_td_exog_only_sc.csv", (pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_iv_dep_near)"), pyx_sc("e(dep_res)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(N)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(kink_refined)"), pyx_sc("e(gamma_stage1)"), pyx_sc("e(refine_iterations)"), pyx_sc("e(refine_added)"), pyx_sc("e(grid_effective)")))
    mata: pyx_export("../out/tc_fd_td_exog_only_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/tc_fd_td_exog_only_vc.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/tc_fd_td_exog_only_z.csv", xdpt_best_Z_f)
    mata: pyx_export("../out/tc_fd_td_exog_only_x.csv", xdpt_best_X_f)
    mata: pyx_export("../out/tc_fd_td_exog_only_a.csv", xdpt_best_A)
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
display "@@CASE fd_td_collapse"
capture noisily xtdpthresh invest cashflow, qx(debt) td collapse exportgmm noboot grid(30) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/tc_fd_td_collapse_sc.csv", (pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_iv_dep_near)"), pyx_sc("e(dep_res)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(N)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(kink_refined)"), pyx_sc("e(gamma_stage1)"), pyx_sc("e(refine_iterations)"), pyx_sc("e(refine_added)"), pyx_sc("e(grid_effective)")))
    mata: pyx_export("../out/tc_fd_td_collapse_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/tc_fd_td_collapse_vc.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/tc_fd_td_collapse_z.csv", xdpt_best_Z_f)
    mata: pyx_export("../out/tc_fd_td_collapse_x.csv", xdpt_best_X_f)
    mata: pyx_export("../out/tc_fd_td_collapse_a.csv", xdpt_best_A)
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
display "@@CASE fd_td_kink"
capture noisily xtdpthresh invest cashflow, qx(debt) kink td exportgmm noboot grid(30) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/tc_fd_td_kink_sc.csv", (pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_iv_dep_near)"), pyx_sc("e(dep_res)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(N)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(kink_refined)"), pyx_sc("e(gamma_stage1)"), pyx_sc("e(refine_iterations)"), pyx_sc("e(refine_added)"), pyx_sc("e(grid_effective)")))
    mata: pyx_export("../out/tc_fd_td_kink_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/tc_fd_td_kink_vc.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/tc_fd_td_kink_z.csv", xdpt_best_Z_f)
    mata: pyx_export("../out/tc_fd_td_kink_x.csv", xdpt_best_X_f)
    mata: pyx_export("../out/tc_fd_td_kink_a.csv", xdpt_best_A)
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
drop if mod(firm + 3*year, 11) == 0
display "@@CASE fd_td_gaps"
capture noisily xtdpthresh invest cashflow, qx(debt) td exportgmm noboot grid(30) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/tc_fd_td_gaps_sc.csv", (pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_iv_dep_near)"), pyx_sc("e(dep_res)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(N)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(kink_refined)"), pyx_sc("e(gamma_stage1)"), pyx_sc("e(refine_iterations)"), pyx_sc("e(refine_added)"), pyx_sc("e(grid_effective)")))
    mata: pyx_export("../out/tc_fd_td_gaps_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/tc_fd_td_gaps_vc.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/tc_fd_td_gaps_z.csv", xdpt_best_Z_f)
    mata: pyx_export("../out/tc_fd_td_gaps_x.csv", xdpt_best_X_f)
    mata: pyx_export("../out/tc_fd_td_gaps_a.csv", xdpt_best_A)
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
drop if firm <= 10 & year > 1973
drop if firm >= 11 & firm <= 20 & year > 1974
display "@@CASE fd_td_short_units"
capture noisily xtdpthresh invest cashflow, qx(debt) td exportgmm noboot grid(30) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/tc_fd_td_short_units_sc.csv", (pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_iv_dep_near)"), pyx_sc("e(dep_res)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(N)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(kink_refined)"), pyx_sc("e(gamma_stage1)"), pyx_sc("e(refine_iterations)"), pyx_sc("e(refine_added)"), pyx_sc("e(grid_effective)")))
    mata: pyx_export("../out/tc_fd_td_short_units_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/tc_fd_td_short_units_vc.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/tc_fd_td_short_units_z.csv", xdpt_best_Z_f)
    mata: pyx_export("../out/tc_fd_td_short_units_x.csv", xdpt_best_X_f)
    mata: pyx_export("../out/tc_fd_td_short_units_a.csv", xdpt_best_A)
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
drop if firm >= 11 & firm <= 40 & mod(year, 2) == 0
display "@@CASE fd_td_alternate_years"
capture noisily xtdpthresh invest cashflow, qx(debt) td exportgmm noboot grid(30) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/tc_fd_td_alternate_years_sc.csv", (pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_iv_dep_near)"), pyx_sc("e(dep_res)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(N)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(kink_refined)"), pyx_sc("e(gamma_stage1)"), pyx_sc("e(refine_iterations)"), pyx_sc("e(refine_added)"), pyx_sc("e(grid_effective)")))
    mata: pyx_export("../out/tc_fd_td_alternate_years_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/tc_fd_td_alternate_years_vc.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/tc_fd_td_alternate_years_z.csv", xdpt_best_Z_f)
    mata: pyx_export("../out/tc_fd_td_alternate_years_x.csv", xdpt_best_X_f)
    mata: pyx_export("../out/tc_fd_td_alternate_years_a.csv", xdpt_best_A)
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
display "@@CASE fod_td_endog"
capture noisily xtdpthresh invest cashflow, qx(debt) td exportgmm noboot method(fod) grid(30) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/tc_fod_td_endog_sc.csv", (pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_iv_dep_near)"), pyx_sc("e(dep_res)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(N)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(kink_refined)"), pyx_sc("e(gamma_stage1)"), pyx_sc("e(refine_iterations)"), pyx_sc("e(refine_added)"), pyx_sc("e(grid_effective)")))
    mata: pyx_export("../out/tc_fod_td_endog_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/tc_fod_td_endog_vc.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/tc_fod_td_endog_z.csv", xdpt_best_Z_f)
    mata: pyx_export("../out/tc_fod_td_endog_x.csv", xdpt_best_X_f)
    mata: pyx_export("../out/tc_fod_td_endog_a.csv", xdpt_best_A)
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
display "@@CASE fod_td_exog_only"
capture noisily xtdpthresh invest cashflow, qx(debt) td exportgmm noboot method(fod) grid(30)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/tc_fod_td_exog_only_sc.csv", (pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_iv_dep_near)"), pyx_sc("e(dep_res)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(N)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(kink_refined)"), pyx_sc("e(gamma_stage1)"), pyx_sc("e(refine_iterations)"), pyx_sc("e(refine_added)"), pyx_sc("e(grid_effective)")))
    mata: pyx_export("../out/tc_fod_td_exog_only_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/tc_fod_td_exog_only_vc.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/tc_fod_td_exog_only_z.csv", xdpt_best_Z_f)
    mata: pyx_export("../out/tc_fod_td_exog_only_x.csv", xdpt_best_X_f)
    mata: pyx_export("../out/tc_fod_td_exog_only_a.csv", xdpt_best_A)
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
display "@@CASE fod_td_collapse"
capture noisily xtdpthresh invest cashflow, qx(debt) td collapse exportgmm noboot method(fod) grid(30) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/tc_fod_td_collapse_sc.csv", (pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_iv_dep_near)"), pyx_sc("e(dep_res)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(N)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(kink_refined)"), pyx_sc("e(gamma_stage1)"), pyx_sc("e(refine_iterations)"), pyx_sc("e(refine_added)"), pyx_sc("e(grid_effective)")))
    mata: pyx_export("../out/tc_fod_td_collapse_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/tc_fod_td_collapse_vc.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/tc_fod_td_collapse_z.csv", xdpt_best_Z_f)
    mata: pyx_export("../out/tc_fod_td_collapse_x.csv", xdpt_best_X_f)
    mata: pyx_export("../out/tc_fod_td_collapse_a.csv", xdpt_best_A)
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
display "@@CASE fod_td_static"
capture noisily xtdpthresh invest cashflow L.tobin_q, qx(debt) static td exportgmm noboot method(fod) grid(30)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/tc_fod_td_static_sc.csv", (pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_iv_dep_near)"), pyx_sc("e(dep_res)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(N)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(kink_refined)"), pyx_sc("e(gamma_stage1)"), pyx_sc("e(refine_iterations)"), pyx_sc("e(refine_added)"), pyx_sc("e(grid_effective)")))
    mata: pyx_export("../out/tc_fod_td_static_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/tc_fod_td_static_vc.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/tc_fod_td_static_z.csv", xdpt_best_Z_f)
    mata: pyx_export("../out/tc_fod_td_static_x.csv", xdpt_best_X_f)
    mata: pyx_export("../out/tc_fod_td_static_a.csv", xdpt_best_A)
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
drop if mod(firm + 3*year, 11) == 0
display "@@CASE fod_td_gaps"
capture noisily xtdpthresh invest cashflow, qx(debt) td exportgmm noboot method(fod) grid(30) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/tc_fod_td_gaps_sc.csv", (pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_iv_dep_near)"), pyx_sc("e(dep_res)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(N)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(kink_refined)"), pyx_sc("e(gamma_stage1)"), pyx_sc("e(refine_iterations)"), pyx_sc("e(refine_added)"), pyx_sc("e(grid_effective)")))
    mata: pyx_export("../out/tc_fod_td_gaps_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/tc_fod_td_gaps_vc.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/tc_fod_td_gaps_z.csv", xdpt_best_Z_f)
    mata: pyx_export("../out/tc_fod_td_gaps_x.csv", xdpt_best_X_f)
    mata: pyx_export("../out/tc_fod_td_gaps_a.csv", xdpt_best_A)
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
drop if firm <= 10 & year > 1973
drop if firm >= 11 & firm <= 20 & year > 1974
display "@@CASE fod_td_short_units"
capture noisily xtdpthresh invest cashflow, qx(debt) td exportgmm noboot method(fod) grid(30) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/tc_fod_td_short_units_sc.csv", (pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_iv_dep_near)"), pyx_sc("e(dep_res)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(N)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(kink_refined)"), pyx_sc("e(gamma_stage1)"), pyx_sc("e(refine_iterations)"), pyx_sc("e(refine_added)"), pyx_sc("e(grid_effective)")))
    mata: pyx_export("../out/tc_fod_td_short_units_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/tc_fod_td_short_units_vc.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/tc_fod_td_short_units_z.csv", xdpt_best_Z_f)
    mata: pyx_export("../out/tc_fod_td_short_units_x.csv", xdpt_best_X_f)
    mata: pyx_export("../out/tc_fod_td_short_units_a.csv", xdpt_best_A)
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
drop if firm >= 11 & firm <= 40 & mod(year, 2) == 0
display "@@CASE fod_td_alternate_years"
capture noisily xtdpthresh invest cashflow, qx(debt) td exportgmm noboot method(fod) grid(30) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/tc_fod_td_alternate_years_sc.csv", (pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_iv_dep_near)"), pyx_sc("e(dep_res)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(N)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(kink_refined)"), pyx_sc("e(gamma_stage1)"), pyx_sc("e(refine_iterations)"), pyx_sc("e(refine_added)"), pyx_sc("e(grid_effective)")))
    mata: pyx_export("../out/tc_fod_td_alternate_years_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/tc_fod_td_alternate_years_vc.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/tc_fod_td_alternate_years_z.csv", xdpt_best_Z_f)
    mata: pyx_export("../out/tc_fod_td_alternate_years_x.csv", xdpt_best_X_f)
    mata: pyx_export("../out/tc_fod_td_alternate_years_a.csv", xdpt_best_A)
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
display "@@CASE fd_history_panel"
capture noisily xtdpthresh invest cashflow if year >= 1976, qx(debt) exportgmm noboot grid(30) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/tc_fd_history_panel_sc.csv", (pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_iv_dep_near)"), pyx_sc("e(dep_res)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(N)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(kink_refined)"), pyx_sc("e(gamma_stage1)"), pyx_sc("e(refine_iterations)"), pyx_sc("e(refine_added)"), pyx_sc("e(grid_effective)")))
    mata: pyx_export("../out/tc_fd_history_panel_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/tc_fd_history_panel_vc.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/tc_fd_history_panel_z.csv", xdpt_best_Z_f)
    mata: pyx_export("../out/tc_fd_history_panel_x.csv", xdpt_best_X_f)
    mata: pyx_export("../out/tc_fd_history_panel_a.csv", xdpt_best_A)
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
display "@@CASE fd_history_sample"
capture noisily xtdpthresh invest cashflow if year >= 1976, qx(debt) exportgmm noboot grid(30) history(sample) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/tc_fd_history_sample_sc.csv", (pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_iv_dep_near)"), pyx_sc("e(dep_res)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(N)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(kink_refined)"), pyx_sc("e(gamma_stage1)"), pyx_sc("e(refine_iterations)"), pyx_sc("e(refine_added)"), pyx_sc("e(grid_effective)")))
    mata: pyx_export("../out/tc_fd_history_sample_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/tc_fd_history_sample_vc.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/tc_fd_history_sample_z.csv", xdpt_best_Z_f)
    mata: pyx_export("../out/tc_fd_history_sample_x.csv", xdpt_best_X_f)
    mata: pyx_export("../out/tc_fd_history_sample_a.csv", xdpt_best_A)
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
display "@@CASE fod_history_panel"
capture noisily xtdpthresh invest cashflow if year >= 1976, qx(debt) exportgmm noboot method(fod) grid(30) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/tc_fod_history_panel_sc.csv", (pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_iv_dep_near)"), pyx_sc("e(dep_res)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(N)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(kink_refined)"), pyx_sc("e(gamma_stage1)"), pyx_sc("e(refine_iterations)"), pyx_sc("e(refine_added)"), pyx_sc("e(grid_effective)")))
    mata: pyx_export("../out/tc_fod_history_panel_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/tc_fod_history_panel_vc.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/tc_fod_history_panel_z.csv", xdpt_best_Z_f)
    mata: pyx_export("../out/tc_fod_history_panel_x.csv", xdpt_best_X_f)
    mata: pyx_export("../out/tc_fod_history_panel_a.csv", xdpt_best_A)
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
display "@@CASE fod_history_sample"
capture noisily xtdpthresh invest cashflow if year >= 1976, qx(debt) exportgmm noboot method(fod) grid(30) history(sample) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/tc_fod_history_sample_sc.csv", (pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_iv_dep_near)"), pyx_sc("e(dep_res)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(N)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(kink_refined)"), pyx_sc("e(gamma_stage1)"), pyx_sc("e(refine_iterations)"), pyx_sc("e(refine_added)"), pyx_sc("e(grid_effective)")))
    mata: pyx_export("../out/tc_fod_history_sample_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/tc_fod_history_sample_vc.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/tc_fod_history_sample_z.csv", xdpt_best_Z_f)
    mata: pyx_export("../out/tc_fod_history_sample_x.csv", xdpt_best_X_f)
    mata: pyx_export("../out/tc_fod_history_sample_a.csv", xdpt_best_A)
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
drop if mod(firm + 3*year, 11) == 0
display "@@CASE fd_iv_with_gaps"
capture noisily xtdpthresh invest cashflow, qx(debt) exportgmm noboot grid(30) endogenous(tobin_q) iv(z1)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/tc_fd_iv_with_gaps_sc.csv", (pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_iv_dep_near)"), pyx_sc("e(dep_res)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(N)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(kink_refined)"), pyx_sc("e(gamma_stage1)"), pyx_sc("e(refine_iterations)"), pyx_sc("e(refine_added)"), pyx_sc("e(grid_effective)")))
    mata: pyx_export("../out/tc_fd_iv_with_gaps_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/tc_fd_iv_with_gaps_vc.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/tc_fd_iv_with_gaps_z.csv", xdpt_best_Z_f)
    mata: pyx_export("../out/tc_fd_iv_with_gaps_x.csv", xdpt_best_X_f)
    mata: pyx_export("../out/tc_fd_iv_with_gaps_a.csv", xdpt_best_A)
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
drop if mod(firm + 3*year, 11) == 0
display "@@CASE fod_iv_with_gaps"
capture noisily xtdpthresh invest cashflow, qx(debt) exportgmm noboot method(fod) grid(30) endogenous(tobin_q) iv(z1)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/tc_fod_iv_with_gaps_sc.csv", (pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_iv_dep_near)"), pyx_sc("e(dep_res)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(N)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(kink_refined)"), pyx_sc("e(gamma_stage1)"), pyx_sc("e(refine_iterations)"), pyx_sc("e(refine_added)"), pyx_sc("e(grid_effective)")))
    mata: pyx_export("../out/tc_fod_iv_with_gaps_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/tc_fod_iv_with_gaps_vc.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/tc_fod_iv_with_gaps_z.csv", xdpt_best_Z_f)
    mata: pyx_export("../out/tc_fod_iv_with_gaps_x.csv", xdpt_best_X_f)
    mata: pyx_export("../out/tc_fod_iv_with_gaps_a.csv", xdpt_best_A)
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
drop if year == 1981 & firm > 1
display "@@CASE fd_td_single_period"
capture noisily xtdpthresh invest cashflow, qx(debt) td exportgmm noboot grid(30) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/tc_fd_td_single_period_sc.csv", (pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_iv_dep_near)"), pyx_sc("e(dep_res)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(N)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(kink_refined)"), pyx_sc("e(gamma_stage1)"), pyx_sc("e(refine_iterations)"), pyx_sc("e(refine_added)"), pyx_sc("e(grid_effective)")))
    mata: pyx_export("../out/tc_fd_td_single_period_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/tc_fd_td_single_period_vc.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/tc_fd_td_single_period_z.csv", xdpt_best_Z_f)
    mata: pyx_export("../out/tc_fd_td_single_period_x.csv", xdpt_best_X_f)
    mata: pyx_export("../out/tc_fd_td_single_period_a.csv", xdpt_best_A)
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
drop if year == 1975 & firm > 3
drop if year == 1979 & firm > 40
display "@@CASE fd_td_sparse_periods"
capture noisily xtdpthresh invest cashflow, qx(debt) td exportgmm noboot grid(30) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/tc_fd_td_sparse_periods_sc.csv", (pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_iv_dep_near)"), pyx_sc("e(dep_res)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(N)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(kink_refined)"), pyx_sc("e(gamma_stage1)"), pyx_sc("e(refine_iterations)"), pyx_sc("e(refine_added)"), pyx_sc("e(grid_effective)")))
    mata: pyx_export("../out/tc_fd_td_sparse_periods_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/tc_fd_td_sparse_periods_vc.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/tc_fd_td_sparse_periods_z.csv", xdpt_best_Z_f)
    mata: pyx_export("../out/tc_fd_td_sparse_periods_x.csv", xdpt_best_X_f)
    mata: pyx_export("../out/tc_fd_td_sparse_periods_a.csv", xdpt_best_A)
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
drop if year == 1981 & firm > 1
display "@@CASE fod_td_single_period"
capture noisily xtdpthresh invest cashflow, qx(debt) td exportgmm noboot method(fod) grid(30) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/tc_fod_td_single_period_sc.csv", (pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_iv_dep_near)"), pyx_sc("e(dep_res)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(N)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(kink_refined)"), pyx_sc("e(gamma_stage1)"), pyx_sc("e(refine_iterations)"), pyx_sc("e(refine_added)"), pyx_sc("e(grid_effective)")))
    mata: pyx_export("../out/tc_fod_td_single_period_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/tc_fod_td_single_period_vc.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/tc_fod_td_single_period_z.csv", xdpt_best_Z_f)
    mata: pyx_export("../out/tc_fod_td_single_period_x.csv", xdpt_best_X_f)
    mata: pyx_export("../out/tc_fod_td_single_period_a.csv", xdpt_best_A)
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
drop if year == 1975 & firm > 3
drop if year == 1979 & firm > 40
display "@@CASE fod_td_sparse_periods"
capture noisily xtdpthresh invest cashflow, qx(debt) td exportgmm noboot method(fod) grid(30) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/tc_fod_td_sparse_periods_sc.csv", (pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_iv_dep_near)"), pyx_sc("e(dep_res)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(N)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(kink_refined)"), pyx_sc("e(gamma_stage1)"), pyx_sc("e(refine_iterations)"), pyx_sc("e(refine_added)"), pyx_sc("e(grid_effective)")))
    mata: pyx_export("../out/tc_fod_td_sparse_periods_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/tc_fod_td_sparse_periods_vc.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/tc_fod_td_sparse_periods_z.csv", xdpt_best_Z_f)
    mata: pyx_export("../out/tc_fod_td_sparse_periods_x.csv", xdpt_best_X_f)
    mata: pyx_export("../out/tc_fod_td_sparse_periods_a.csv", xdpt_best_A)
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
drop if year == 1975 & firm > 3
drop if year == 1979 & firm > 40
display "@@CASE fod_sparse_periods"
capture noisily xtdpthresh invest cashflow, qx(debt) exportgmm noboot method(fod) grid(30) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/tc_fod_sparse_periods_sc.csv", (pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_iv_dep_near)"), pyx_sc("e(dep_res)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(N)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(kink_refined)"), pyx_sc("e(gamma_stage1)"), pyx_sc("e(refine_iterations)"), pyx_sc("e(refine_added)"), pyx_sc("e(grid_effective)")))
    mata: pyx_export("../out/tc_fod_sparse_periods_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/tc_fod_sparse_periods_vc.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/tc_fod_sparse_periods_z.csv", xdpt_best_Z_f)
    mata: pyx_export("../out/tc_fod_sparse_periods_x.csv", xdpt_best_X_f)
    mata: pyx_export("../out/tc_fod_sparse_periods_a.csv", xdpt_best_A)
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
display "@@CASE fd_td_macro"
capture noisily xtdpthresh invest cashflow macro, qx(debt) td exportgmm noboot grid(30) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/tc_fd_td_macro_sc.csv", (pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_iv_dep_near)"), pyx_sc("e(dep_res)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(N)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(kink_refined)"), pyx_sc("e(gamma_stage1)"), pyx_sc("e(refine_iterations)"), pyx_sc("e(refine_added)"), pyx_sc("e(grid_effective)")))
    mata: pyx_export("../out/tc_fd_td_macro_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/tc_fd_td_macro_vc.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/tc_fd_td_macro_z.csv", xdpt_best_Z_f)
    mata: pyx_export("../out/tc_fd_td_macro_x.csv", xdpt_best_X_f)
    mata: pyx_export("../out/tc_fd_td_macro_a.csv", xdpt_best_A)
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
display "@@CASE fod_td_macro"
capture noisily xtdpthresh invest cashflow macro, qx(debt) td exportgmm noboot method(fod) grid(30) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/tc_fod_td_macro_sc.csv", (pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_iv_dep_near)"), pyx_sc("e(dep_res)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(N)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(kink_refined)"), pyx_sc("e(gamma_stage1)"), pyx_sc("e(refine_iterations)"), pyx_sc("e(refine_added)"), pyx_sc("e(grid_effective)")))
    mata: pyx_export("../out/tc_fod_td_macro_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/tc_fod_td_macro_vc.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/tc_fod_td_macro_z.csv", xdpt_best_Z_f)
    mata: pyx_export("../out/tc_fod_td_macro_x.csv", xdpt_best_X_f)
    mata: pyx_export("../out/tc_fod_td_macro_a.csv", xdpt_best_A)
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
display "@@CASE fd_td_gone"
capture noisily xtdpthresh invest cashflow ageish, qx(debt) td exportgmm noboot grid(30) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/tc_fd_td_gone_sc.csv", (pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_iv_dep_near)"), pyx_sc("e(dep_res)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(N)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(kink_refined)"), pyx_sc("e(gamma_stage1)"), pyx_sc("e(refine_iterations)"), pyx_sc("e(refine_added)"), pyx_sc("e(grid_effective)")))
    mata: pyx_export("../out/tc_fd_td_gone_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/tc_fd_td_gone_vc.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/tc_fd_td_gone_z.csv", xdpt_best_Z_f)
    mata: pyx_export("../out/tc_fd_td_gone_x.csv", xdpt_best_X_f)
    mata: pyx_export("../out/tc_fd_td_gone_a.csv", xdpt_best_A)
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
display "@@CASE fod_td_gone"
capture noisily xtdpthresh invest cashflow ageish, qx(debt) td exportgmm noboot method(fod) grid(30) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/tc_fod_td_gone_sc.csv", (pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_iv_dep_near)"), pyx_sc("e(dep_res)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(N)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(kink_refined)"), pyx_sc("e(gamma_stage1)"), pyx_sc("e(refine_iterations)"), pyx_sc("e(refine_added)"), pyx_sc("e(grid_effective)")))
    mata: pyx_export("../out/tc_fod_td_gone_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/tc_fod_td_gone_vc.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/tc_fod_td_gone_z.csv", xdpt_best_Z_f)
    mata: pyx_export("../out/tc_fod_td_gone_x.csv", xdpt_best_X_f)
    mata: pyx_export("../out/tc_fod_td_gone_a.csv", xdpt_best_A)
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
display "@@CASE fd_age_without_td"
capture noisily xtdpthresh invest cashflow ageish, qx(debt) exportgmm noboot grid(30) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/tc_fd_age_without_td_sc.csv", (pyx_sc("e(N_iv)"), pyx_sc("e(N_iv_common)"), pyx_sc("e(N_iv_dep)"), pyx_sc("e(N_iv_dep_near)"), pyx_sc("e(dep_res)"), pyx_sc("e(W1_fallback)"), pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(N)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(kink_refined)"), pyx_sc("e(gamma_stage1)"), pyx_sc("e(refine_iterations)"), pyx_sc("e(refine_added)"), pyx_sc("e(grid_effective)")))
    mata: pyx_export("../out/tc_fd_age_without_td_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/tc_fd_age_without_td_vc.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/tc_fd_age_without_td_z.csv", xdpt_best_Z_f)
    mata: pyx_export("../out/tc_fd_age_without_td_x.csv", xdpt_best_X_f)
    mata: pyx_export("../out/tc_fd_age_without_td_a.csv", xdpt_best_A)
}

exit, clear
