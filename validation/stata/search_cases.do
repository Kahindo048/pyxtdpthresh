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
display "@@CASE default"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(50) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/sc2_default_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(kink_refined)"), pyx_sc("e(gamma_stage1)"), pyx_sc("e(refine_iterations)"), pyx_sc("e(refine_added)"), pyx_sc("e(grid_effective)"), pyx_sc("e(N)")))
    mata: pyx_export("../out/sc2_default_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/sc2_default_vc.csv", st_matrix("e(V_cond)"))
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
display "@@CASE grid10"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(10) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/sc2_grid10_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(kink_refined)"), pyx_sc("e(gamma_stage1)"), pyx_sc("e(refine_iterations)"), pyx_sc("e(refine_added)"), pyx_sc("e(grid_effective)"), pyx_sc("e(N)")))
    mata: pyx_export("../out/sc2_grid10_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/sc2_grid10_vc.csv", st_matrix("e(V_cond)"))
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
display "@@CASE grid200"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(200) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/sc2_grid200_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(kink_refined)"), pyx_sc("e(gamma_stage1)"), pyx_sc("e(refine_iterations)"), pyx_sc("e(refine_added)"), pyx_sc("e(grid_effective)"), pyx_sc("e(N)")))
    mata: pyx_export("../out/sc2_grid200_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/sc2_grid200_vc.csv", st_matrix("e(V_cond)"))
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
display "@@CASE quantile"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(50) gridtype(quantile) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/sc2_quantile_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(kink_refined)"), pyx_sc("e(gamma_stage1)"), pyx_sc("e(refine_iterations)"), pyx_sc("e(refine_added)"), pyx_sc("e(grid_effective)"), pyx_sc("e(N)")))
    mata: pyx_export("../out/sc2_quantile_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/sc2_quantile_vc.csv", st_matrix("e(V_cond)"))
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
display "@@CASE quantile_10"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(10) gridtype(quantile) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/sc2_quantile_10_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(kink_refined)"), pyx_sc("e(gamma_stage1)"), pyx_sc("e(refine_iterations)"), pyx_sc("e(refine_added)"), pyx_sc("e(grid_effective)"), pyx_sc("e(N)")))
    mata: pyx_export("../out/sc2_quantile_10_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/sc2_quantile_10_vc.csv", st_matrix("e(V_cond)"))
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
display "@@CASE observed_support"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(50) gridsample(observed) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/sc2_observed_support_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(kink_refined)"), pyx_sc("e(gamma_stage1)"), pyx_sc("e(refine_iterations)"), pyx_sc("e(refine_added)"), pyx_sc("e(grid_effective)"), pyx_sc("e(N)")))
    mata: pyx_export("../out/sc2_observed_support_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/sc2_observed_support_vc.csv", st_matrix("e(V_cond)"))
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
display "@@CASE trim20"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(50) trim(0.2) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/sc2_trim20_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(kink_refined)"), pyx_sc("e(gamma_stage1)"), pyx_sc("e(refine_iterations)"), pyx_sc("e(refine_added)"), pyx_sc("e(grid_effective)"), pyx_sc("e(N)")))
    mata: pyx_export("../out/sc2_trim20_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/sc2_trim20_vc.csv", st_matrix("e(V_cond)"))
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
display "@@CASE trim05"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(50) trim(0.05) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/sc2_trim05_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(kink_refined)"), pyx_sc("e(gamma_stage1)"), pyx_sc("e(refine_iterations)"), pyx_sc("e(refine_added)"), pyx_sc("e(grid_effective)"), pyx_sc("e(N)")))
    mata: pyx_export("../out/sc2_trim05_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/sc2_trim05_vc.csv", st_matrix("e(V_cond)"))
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
display "@@CASE min_regime"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(50) minregime(60) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/sc2_min_regime_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(kink_refined)"), pyx_sc("e(gamma_stage1)"), pyx_sc("e(refine_iterations)"), pyx_sc("e(refine_added)"), pyx_sc("e(grid_effective)"), pyx_sc("e(N)")))
    mata: pyx_export("../out/sc2_min_regime_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/sc2_min_regime_vc.csv", st_matrix("e(V_cond)"))
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
display "@@CASE refine1"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(15) refine(1) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/sc2_refine1_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(kink_refined)"), pyx_sc("e(gamma_stage1)"), pyx_sc("e(refine_iterations)"), pyx_sc("e(refine_added)"), pyx_sc("e(grid_effective)"), pyx_sc("e(N)")))
    mata: pyx_export("../out/sc2_refine1_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/sc2_refine1_vc.csv", st_matrix("e(V_cond)"))
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
display "@@CASE refine3"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(15) refine(3) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/sc2_refine3_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(kink_refined)"), pyx_sc("e(gamma_stage1)"), pyx_sc("e(refine_iterations)"), pyx_sc("e(refine_added)"), pyx_sc("e(grid_effective)"), pyx_sc("e(N)")))
    mata: pyx_export("../out/sc2_refine3_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/sc2_refine3_vc.csv", st_matrix("e(V_cond)"))
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
display "@@CASE refine_quantile"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(12) gridtype(quantile) refine(2) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/sc2_refine_quantile_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(kink_refined)"), pyx_sc("e(gamma_stage1)"), pyx_sc("e(refine_iterations)"), pyx_sc("e(refine_added)"), pyx_sc("e(grid_effective)"), pyx_sc("e(N)")))
    mata: pyx_export("../out/sc2_refine_quantile_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/sc2_refine_quantile_vc.csv", st_matrix("e(V_cond)"))
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
display "@@CASE kink"
capture noisily xtdpthresh invest cashflow, qx(debt) kink noboot grid(50) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/sc2_kink_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(kink_refined)"), pyx_sc("e(gamma_stage1)"), pyx_sc("e(refine_iterations)"), pyx_sc("e(refine_added)"), pyx_sc("e(grid_effective)"), pyx_sc("e(N)")))
    mata: pyx_export("../out/sc2_kink_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/sc2_kink_vc.csv", st_matrix("e(V_cond)"))
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
display "@@CASE kink_grid10"
capture noisily xtdpthresh invest cashflow, qx(debt) kink noboot grid(10) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/sc2_kink_grid10_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(kink_refined)"), pyx_sc("e(gamma_stage1)"), pyx_sc("e(refine_iterations)"), pyx_sc("e(refine_added)"), pyx_sc("e(grid_effective)"), pyx_sc("e(N)")))
    mata: pyx_export("../out/sc2_kink_grid10_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/sc2_kink_grid10_vc.csv", st_matrix("e(V_cond)"))
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
display "@@CASE kink_trim20"
capture noisily xtdpthresh invest cashflow, qx(debt) kink noboot grid(50) trim(0.2) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/sc2_kink_trim20_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(kink_refined)"), pyx_sc("e(gamma_stage1)"), pyx_sc("e(refine_iterations)"), pyx_sc("e(refine_added)"), pyx_sc("e(grid_effective)"), pyx_sc("e(N)")))
    mata: pyx_export("../out/sc2_kink_trim20_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/sc2_kink_trim20_vc.csv", st_matrix("e(V_cond)"))
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
display "@@CASE static"
capture noisily xtdpthresh invest cashflow L.tobin_q, qx(debt) static noboot grid(50)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/sc2_static_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(kink_refined)"), pyx_sc("e(gamma_stage1)"), pyx_sc("e(refine_iterations)"), pyx_sc("e(refine_added)"), pyx_sc("e(grid_effective)"), pyx_sc("e(N)")))
    mata: pyx_export("../out/sc2_static_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/sc2_static_vc.csv", st_matrix("e(V_cond)"))
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
display "@@CASE collapse"
capture noisily xtdpthresh invest cashflow, qx(debt) collapse noboot grid(50) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/sc2_collapse_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(kink_refined)"), pyx_sc("e(gamma_stage1)"), pyx_sc("e(refine_iterations)"), pyx_sc("e(refine_added)"), pyx_sc("e(grid_effective)"), pyx_sc("e(N)")))
    mata: pyx_export("../out/sc2_collapse_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/sc2_collapse_vc.csv", st_matrix("e(V_cond)"))
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
display "@@CASE iv"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(50) endogenous(tobin_q) iv(z1 z2, collapse)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/sc2_iv_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(kink_refined)"), pyx_sc("e(gamma_stage1)"), pyx_sc("e(refine_iterations)"), pyx_sc("e(refine_added)"), pyx_sc("e(grid_effective)"), pyx_sc("e(N)")))
    mata: pyx_export("../out/sc2_iv_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/sc2_iv_vc.csv", st_matrix("e(V_cond)"))
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
display "@@CASE exog_only"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(50)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/sc2_exog_only_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(kink_refined)"), pyx_sc("e(gamma_stage1)"), pyx_sc("e(refine_iterations)"), pyx_sc("e(refine_added)"), pyx_sc("e(grid_effective)"), pyx_sc("e(N)")))
    mata: pyx_export("../out/sc2_exog_only_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/sc2_exog_only_vc.csv", st_matrix("e(V_cond)"))
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
display "@@CASE nocenter"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot nocenter grid(50) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/sc2_nocenter_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(kink_refined)"), pyx_sc("e(gamma_stage1)"), pyx_sc("e(refine_iterations)"), pyx_sc("e(refine_added)"), pyx_sc("e(grid_effective)"), pyx_sc("e(N)")))
    mata: pyx_export("../out/sc2_nocenter_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/sc2_nocenter_vc.csv", st_matrix("e(V_cond)"))
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
drop if mod(firm + 3*year, 11) == 0
display "@@CASE unbalanced_gaps"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(50) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/sc2_unbalanced_gaps_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(kink_refined)"), pyx_sc("e(gamma_stage1)"), pyx_sc("e(refine_iterations)"), pyx_sc("e(refine_added)"), pyx_sc("e(grid_effective)"), pyx_sc("e(N)")))
    mata: pyx_export("../out/sc2_unbalanced_gaps_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/sc2_unbalanced_gaps_vc.csv", st_matrix("e(V_cond)"))
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
replace cashflow = . if mod(firm*year, 13) == 0
display "@@CASE unbalanced_missing_x"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(50) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/sc2_unbalanced_missing_x_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(kink_refined)"), pyx_sc("e(gamma_stage1)"), pyx_sc("e(refine_iterations)"), pyx_sc("e(refine_added)"), pyx_sc("e(grid_effective)"), pyx_sc("e(N)")))
    mata: pyx_export("../out/sc2_unbalanced_missing_x_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/sc2_unbalanced_missing_x_vc.csv", st_matrix("e(V_cond)"))
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
drop if firm <= 10 & year > 1973
drop if firm >= 11 & firm <= 20 & year > 1974
display "@@CASE unbalanced_short_units"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(50) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/sc2_unbalanced_short_units_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(kink_refined)"), pyx_sc("e(gamma_stage1)"), pyx_sc("e(refine_iterations)"), pyx_sc("e(refine_added)"), pyx_sc("e(grid_effective)"), pyx_sc("e(N)")))
    mata: pyx_export("../out/sc2_unbalanced_short_units_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/sc2_unbalanced_short_units_vc.csv", st_matrix("e(V_cond)"))
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
drop if firm >= 11 & firm <= 40 & mod(year, 2) == 0
display "@@CASE unbalanced_alternate_years"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(50) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/sc2_unbalanced_alternate_years_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(kink_refined)"), pyx_sc("e(gamma_stage1)"), pyx_sc("e(refine_iterations)"), pyx_sc("e(refine_added)"), pyx_sc("e(grid_effective)"), pyx_sc("e(N)")))
    mata: pyx_export("../out/sc2_unbalanced_alternate_years_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/sc2_unbalanced_alternate_years_vc.csv", st_matrix("e(V_cond)"))
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
replace tobin_q = . if firm <= 50 & year == 1975
display "@@CASE unbalanced_missing_endog"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(50) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/sc2_unbalanced_missing_endog_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(kink_refined)"), pyx_sc("e(gamma_stage1)"), pyx_sc("e(refine_iterations)"), pyx_sc("e(refine_added)"), pyx_sc("e(grid_effective)"), pyx_sc("e(N)")))
    mata: pyx_export("../out/sc2_unbalanced_missing_endog_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/sc2_unbalanced_missing_endog_vc.csv", st_matrix("e(V_cond)"))
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
drop if mod(firm + 3*year, 11) == 0
display "@@CASE unbalanced_refine"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(15) refine(2) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/sc2_unbalanced_refine_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(kink_refined)"), pyx_sc("e(gamma_stage1)"), pyx_sc("e(refine_iterations)"), pyx_sc("e(refine_added)"), pyx_sc("e(grid_effective)"), pyx_sc("e(N)")))
    mata: pyx_export("../out/sc2_unbalanced_refine_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/sc2_unbalanced_refine_vc.csv", st_matrix("e(V_cond)"))
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
drop if firm <= 10 & year > 1973
drop if firm >= 11 & firm <= 20 & year > 1974
display "@@CASE unbalanced_kink"
capture noisily xtdpthresh invest cashflow, qx(debt) kink noboot grid(50) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/sc2_unbalanced_kink_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(kink_refined)"), pyx_sc("e(gamma_stage1)"), pyx_sc("e(refine_iterations)"), pyx_sc("e(refine_added)"), pyx_sc("e(grid_effective)"), pyx_sc("e(N)")))
    mata: pyx_export("../out/sc2_unbalanced_kink_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/sc2_unbalanced_kink_vc.csv", st_matrix("e(V_cond)"))
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
drop if firm >= 11 & firm <= 40 & mod(year, 2) == 0
display "@@CASE alternate_years_kink"
capture noisily xtdpthresh invest cashflow, qx(debt) kink noboot grid(50) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/sc2_alternate_years_kink_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(kink_refined)"), pyx_sc("e(gamma_stage1)"), pyx_sc("e(refine_iterations)"), pyx_sc("e(refine_added)"), pyx_sc("e(grid_effective)"), pyx_sc("e(N)")))
    mata: pyx_export("../out/sc2_alternate_years_kink_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/sc2_alternate_years_kink_vc.csv", st_matrix("e(V_cond)"))
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
drop if firm >= 11 & firm <= 40 & mod(year, 2) == 0
display "@@CASE alternate_years_grid10"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(10) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/sc2_alternate_years_grid10_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(kink_refined)"), pyx_sc("e(gamma_stage1)"), pyx_sc("e(refine_iterations)"), pyx_sc("e(refine_added)"), pyx_sc("e(grid_effective)"), pyx_sc("e(N)")))
    mata: pyx_export("../out/sc2_alternate_years_grid10_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/sc2_alternate_years_grid10_vc.csv", st_matrix("e(V_cond)"))
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
display "@@CASE e_min_regime_huge"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(50) minregime(5000) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/sc2_e_min_regime_huge_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(q_lo)"), pyx_sc("e(q_hi)"), pyx_sc("e(kink_refined)"), pyx_sc("e(gamma_stage1)"), pyx_sc("e(refine_iterations)"), pyx_sc("e(refine_added)"), pyx_sc("e(grid_effective)"), pyx_sc("e(N)")))
    mata: pyx_export("../out/sc2_e_min_regime_huge_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/sc2_e_min_regime_huge_vc.csv", st_matrix("e(V_cond)"))
}

exit, clear
