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

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
display "@@CASE endog"
capture noisily xtdpthresh invest cashflow, qx(debt) exportgmm noboot grid(10) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/ec_endog_sc.csv", (st_numscalar("e(N_iv)"), st_numscalar("e(N_iv_common)"), st_numscalar("e(N_iv_dep)"), st_numscalar("e(N_iv_dep_near)"), st_numscalar("e(iv_dep_res)"), st_numscalar("e(W1_fallback)"), st_numscalar("e(gamma)"), st_numscalar("e(obj)"), st_numscalar("e(estimator_twostep)"), st_numscalar("e(N)")))
    mata: pyx_export("../out/ec_endog_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/ec_endog_vc.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/ec_endog_z.csv", xdpt_best_Z_f)
    mata: pyx_export("../out/ec_endog_x.csv", xdpt_best_X_f)
    mata: pyx_export("../out/ec_endog_a.csv", xdpt_best_A)
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
display "@@CASE exog_only"
capture noisily xtdpthresh invest cashflow, qx(debt) exportgmm noboot grid(10)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/ec_exog_only_sc.csv", (st_numscalar("e(N_iv)"), st_numscalar("e(N_iv_common)"), st_numscalar("e(N_iv_dep)"), st_numscalar("e(N_iv_dep_near)"), st_numscalar("e(iv_dep_res)"), st_numscalar("e(W1_fallback)"), st_numscalar("e(gamma)"), st_numscalar("e(obj)"), st_numscalar("e(estimator_twostep)"), st_numscalar("e(N)")))
    mata: pyx_export("../out/ec_exog_only_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/ec_exog_only_vc.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/ec_exog_only_z.csv", xdpt_best_Z_f)
    mata: pyx_export("../out/ec_exog_only_x.csv", xdpt_best_X_f)
    mata: pyx_export("../out/ec_exog_only_a.csv", xdpt_best_A)
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
display "@@CASE predet"
capture noisily xtdpthresh invest cashflow, qx(debt) exportgmm noboot grid(10) predetermined(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/ec_predet_sc.csv", (st_numscalar("e(N_iv)"), st_numscalar("e(N_iv_common)"), st_numscalar("e(N_iv_dep)"), st_numscalar("e(N_iv_dep_near)"), st_numscalar("e(iv_dep_res)"), st_numscalar("e(W1_fallback)"), st_numscalar("e(gamma)"), st_numscalar("e(obj)"), st_numscalar("e(estimator_twostep)"), st_numscalar("e(N)")))
    mata: pyx_export("../out/ec_predet_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/ec_predet_vc.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/ec_predet_z.csv", xdpt_best_Z_f)
    mata: pyx_export("../out/ec_predet_x.csv", xdpt_best_X_f)
    mata: pyx_export("../out/ec_predet_a.csv", xdpt_best_A)
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
display "@@CASE endog_predet"
capture noisily xtdpthresh invest , qx(debt) exportgmm noboot grid(10) endogenous(tobin_q) predetermined(cashflow)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/ec_endog_predet_sc.csv", (st_numscalar("e(N_iv)"), st_numscalar("e(N_iv_common)"), st_numscalar("e(N_iv_dep)"), st_numscalar("e(N_iv_dep_near)"), st_numscalar("e(iv_dep_res)"), st_numscalar("e(W1_fallback)"), st_numscalar("e(gamma)"), st_numscalar("e(obj)"), st_numscalar("e(estimator_twostep)"), st_numscalar("e(N)")))
    mata: pyx_export("../out/ec_endog_predet_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/ec_endog_predet_vc.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/ec_endog_predet_z.csv", xdpt_best_Z_f)
    mata: pyx_export("../out/ec_endog_predet_x.csv", xdpt_best_X_f)
    mata: pyx_export("../out/ec_endog_predet_a.csv", xdpt_best_A)
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
display "@@CASE exogenous_option"
capture noisily xtdpthresh invest , qx(debt) exportgmm noboot grid(10) exogenous(cashflow tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/ec_exogenous_option_sc.csv", (st_numscalar("e(N_iv)"), st_numscalar("e(N_iv_common)"), st_numscalar("e(N_iv_dep)"), st_numscalar("e(N_iv_dep_near)"), st_numscalar("e(iv_dep_res)"), st_numscalar("e(W1_fallback)"), st_numscalar("e(gamma)"), st_numscalar("e(obj)"), st_numscalar("e(estimator_twostep)"), st_numscalar("e(N)")))
    mata: pyx_export("../out/ec_exogenous_option_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/ec_exogenous_option_vc.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/ec_exogenous_option_z.csv", xdpt_best_Z_f)
    mata: pyx_export("../out/ec_exogenous_option_x.csv", xdpt_best_X_f)
    mata: pyx_export("../out/ec_exogenous_option_a.csv", xdpt_best_A)
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
display "@@CASE static"
capture noisily xtdpthresh invest cashflow L.tobin_q, qx(debt) static exportgmm noboot grid(10)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/ec_static_sc.csv", (st_numscalar("e(N_iv)"), st_numscalar("e(N_iv_common)"), st_numscalar("e(N_iv_dep)"), st_numscalar("e(N_iv_dep_near)"), st_numscalar("e(iv_dep_res)"), st_numscalar("e(W1_fallback)"), st_numscalar("e(gamma)"), st_numscalar("e(obj)"), st_numscalar("e(estimator_twostep)"), st_numscalar("e(N)")))
    mata: pyx_export("../out/ec_static_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/ec_static_vc.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/ec_static_z.csv", xdpt_best_Z_f)
    mata: pyx_export("../out/ec_static_x.csv", xdpt_best_X_f)
    mata: pyx_export("../out/ec_static_a.csv", xdpt_best_A)
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
display "@@CASE static_endog"
capture noisily xtdpthresh invest cashflow, qx(debt) static exportgmm noboot grid(10) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/ec_static_endog_sc.csv", (st_numscalar("e(N_iv)"), st_numscalar("e(N_iv_common)"), st_numscalar("e(N_iv_dep)"), st_numscalar("e(N_iv_dep_near)"), st_numscalar("e(iv_dep_res)"), st_numscalar("e(W1_fallback)"), st_numscalar("e(gamma)"), st_numscalar("e(obj)"), st_numscalar("e(estimator_twostep)"), st_numscalar("e(N)")))
    mata: pyx_export("../out/ec_static_endog_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/ec_static_endog_vc.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/ec_static_endog_z.csv", xdpt_best_Z_f)
    mata: pyx_export("../out/ec_static_endog_x.csv", xdpt_best_X_f)
    mata: pyx_export("../out/ec_static_endog_a.csv", xdpt_best_A)
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
display "@@CASE collapse"
capture noisily xtdpthresh invest cashflow, qx(debt) collapse exportgmm noboot grid(10) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/ec_collapse_sc.csv", (st_numscalar("e(N_iv)"), st_numscalar("e(N_iv_common)"), st_numscalar("e(N_iv_dep)"), st_numscalar("e(N_iv_dep_near)"), st_numscalar("e(iv_dep_res)"), st_numscalar("e(W1_fallback)"), st_numscalar("e(gamma)"), st_numscalar("e(obj)"), st_numscalar("e(estimator_twostep)"), st_numscalar("e(N)")))
    mata: pyx_export("../out/ec_collapse_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/ec_collapse_vc.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/ec_collapse_z.csv", xdpt_best_Z_f)
    mata: pyx_export("../out/ec_collapse_x.csv", xdpt_best_X_f)
    mata: pyx_export("../out/ec_collapse_a.csv", xdpt_best_A)
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
display "@@CASE maxlag_collapse"
capture noisily xtdpthresh invest cashflow, qx(debt) collapse exportgmm noboot grid(10) maxlag(3 6) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/ec_maxlag_collapse_sc.csv", (st_numscalar("e(N_iv)"), st_numscalar("e(N_iv_common)"), st_numscalar("e(N_iv_dep)"), st_numscalar("e(N_iv_dep_near)"), st_numscalar("e(iv_dep_res)"), st_numscalar("e(W1_fallback)"), st_numscalar("e(gamma)"), st_numscalar("e(obj)"), st_numscalar("e(estimator_twostep)"), st_numscalar("e(N)")))
    mata: pyx_export("../out/ec_maxlag_collapse_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/ec_maxlag_collapse_vc.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/ec_maxlag_collapse_z.csv", xdpt_best_Z_f)
    mata: pyx_export("../out/ec_maxlag_collapse_x.csv", xdpt_best_X_f)
    mata: pyx_export("../out/ec_maxlag_collapse_a.csv", xdpt_best_A)
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
display "@@CASE maxlag_2_5"
capture noisily xtdpthresh invest cashflow, qx(debt) exportgmm noboot grid(10) maxlag(2 5) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/ec_maxlag_2_5_sc.csv", (st_numscalar("e(N_iv)"), st_numscalar("e(N_iv_common)"), st_numscalar("e(N_iv_dep)"), st_numscalar("e(N_iv_dep_near)"), st_numscalar("e(iv_dep_res)"), st_numscalar("e(W1_fallback)"), st_numscalar("e(gamma)"), st_numscalar("e(obj)"), st_numscalar("e(estimator_twostep)"), st_numscalar("e(N)")))
    mata: pyx_export("../out/ec_maxlag_2_5_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/ec_maxlag_2_5_vc.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/ec_maxlag_2_5_z.csv", xdpt_best_Z_f)
    mata: pyx_export("../out/ec_maxlag_2_5_x.csv", xdpt_best_X_f)
    mata: pyx_export("../out/ec_maxlag_2_5_a.csv", xdpt_best_A)
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
display "@@CASE maxlag_1_2"
capture noisily xtdpthresh invest , qx(debt) exportgmm noboot grid(10) maxlag(1 2) endogenous(tobin_q) predetermined(cashflow)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/ec_maxlag_1_2_sc.csv", (st_numscalar("e(N_iv)"), st_numscalar("e(N_iv_common)"), st_numscalar("e(N_iv_dep)"), st_numscalar("e(N_iv_dep_near)"), st_numscalar("e(iv_dep_res)"), st_numscalar("e(W1_fallback)"), st_numscalar("e(gamma)"), st_numscalar("e(obj)"), st_numscalar("e(estimator_twostep)"), st_numscalar("e(N)")))
    mata: pyx_export("../out/ec_maxlag_1_2_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/ec_maxlag_1_2_vc.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/ec_maxlag_1_2_z.csv", xdpt_best_Z_f)
    mata: pyx_export("../out/ec_maxlag_1_2_x.csv", xdpt_best_X_f)
    mata: pyx_export("../out/ec_maxlag_1_2_a.csv", xdpt_best_A)
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
display "@@CASE maxlag_4_4"
capture noisily xtdpthresh invest cashflow, qx(debt) exportgmm noboot grid(10) maxlag(4 4) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/ec_maxlag_4_4_sc.csv", (st_numscalar("e(N_iv)"), st_numscalar("e(N_iv_common)"), st_numscalar("e(N_iv_dep)"), st_numscalar("e(N_iv_dep_near)"), st_numscalar("e(iv_dep_res)"), st_numscalar("e(W1_fallback)"), st_numscalar("e(gamma)"), st_numscalar("e(obj)"), st_numscalar("e(estimator_twostep)"), st_numscalar("e(N)")))
    mata: pyx_export("../out/ec_maxlag_4_4_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/ec_maxlag_4_4_vc.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/ec_maxlag_4_4_z.csv", xdpt_best_Z_f)
    mata: pyx_export("../out/ec_maxlag_4_4_x.csv", xdpt_best_X_f)
    mata: pyx_export("../out/ec_maxlag_4_4_a.csv", xdpt_best_A)
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
display "@@CASE iv_one"
capture noisily xtdpthresh invest cashflow, qx(debt) exportgmm noboot grid(10) iv(z1)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/ec_iv_one_sc.csv", (st_numscalar("e(N_iv)"), st_numscalar("e(N_iv_common)"), st_numscalar("e(N_iv_dep)"), st_numscalar("e(N_iv_dep_near)"), st_numscalar("e(iv_dep_res)"), st_numscalar("e(W1_fallback)"), st_numscalar("e(gamma)"), st_numscalar("e(obj)"), st_numscalar("e(estimator_twostep)"), st_numscalar("e(N)")))
    mata: pyx_export("../out/ec_iv_one_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/ec_iv_one_vc.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/ec_iv_one_z.csv", xdpt_best_Z_f)
    mata: pyx_export("../out/ec_iv_one_x.csv", xdpt_best_X_f)
    mata: pyx_export("../out/ec_iv_one_a.csv", xdpt_best_A)
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
display "@@CASE iv_two_collapse"
capture noisily xtdpthresh invest cashflow, qx(debt) exportgmm noboot grid(10) endogenous(tobin_q) iv(z1 z2, collapse)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/ec_iv_two_collapse_sc.csv", (st_numscalar("e(N_iv)"), st_numscalar("e(N_iv_common)"), st_numscalar("e(N_iv_dep)"), st_numscalar("e(N_iv_dep_near)"), st_numscalar("e(iv_dep_res)"), st_numscalar("e(W1_fallback)"), st_numscalar("e(gamma)"), st_numscalar("e(obj)"), st_numscalar("e(estimator_twostep)"), st_numscalar("e(N)")))
    mata: pyx_export("../out/ec_iv_two_collapse_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/ec_iv_two_collapse_vc.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/ec_iv_two_collapse_z.csv", xdpt_best_Z_f)
    mata: pyx_export("../out/ec_iv_two_collapse_x.csv", xdpt_best_X_f)
    mata: pyx_export("../out/ec_iv_two_collapse_a.csv", xdpt_best_A)
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
display "@@CASE iv_two"
capture noisily xtdpthresh invest cashflow, qx(debt) exportgmm noboot grid(10) endogenous(tobin_q) iv(z1 z2)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/ec_iv_two_sc.csv", (st_numscalar("e(N_iv)"), st_numscalar("e(N_iv_common)"), st_numscalar("e(N_iv_dep)"), st_numscalar("e(N_iv_dep_near)"), st_numscalar("e(iv_dep_res)"), st_numscalar("e(W1_fallback)"), st_numscalar("e(gamma)"), st_numscalar("e(obj)"), st_numscalar("e(estimator_twostep)"), st_numscalar("e(N)")))
    mata: pyx_export("../out/ec_iv_two_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/ec_iv_two_vc.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/ec_iv_two_z.csv", xdpt_best_Z_f)
    mata: pyx_export("../out/ec_iv_two_x.csv", xdpt_best_X_f)
    mata: pyx_export("../out/ec_iv_two_a.csv", xdpt_best_A)
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
display "@@CASE iv_with_collapse"
capture noisily xtdpthresh invest cashflow, qx(debt) collapse exportgmm noboot grid(10) iv(z1)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/ec_iv_with_collapse_sc.csv", (st_numscalar("e(N_iv)"), st_numscalar("e(N_iv_common)"), st_numscalar("e(N_iv_dep)"), st_numscalar("e(N_iv_dep_near)"), st_numscalar("e(iv_dep_res)"), st_numscalar("e(W1_fallback)"), st_numscalar("e(gamma)"), st_numscalar("e(obj)"), st_numscalar("e(estimator_twostep)"), st_numscalar("e(N)")))
    mata: pyx_export("../out/ec_iv_with_collapse_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/ec_iv_with_collapse_vc.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/ec_iv_with_collapse_z.csv", xdpt_best_Z_f)
    mata: pyx_export("../out/ec_iv_with_collapse_x.csv", xdpt_best_X_f)
    mata: pyx_export("../out/ec_iv_with_collapse_a.csv", xdpt_best_A)
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
display "@@CASE kink"
capture noisily xtdpthresh invest cashflow, qx(debt) kink exportgmm noboot grid(10) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/ec_kink_sc.csv", (st_numscalar("e(N_iv)"), st_numscalar("e(N_iv_common)"), st_numscalar("e(N_iv_dep)"), st_numscalar("e(N_iv_dep_near)"), st_numscalar("e(iv_dep_res)"), st_numscalar("e(W1_fallback)"), st_numscalar("e(gamma)"), st_numscalar("e(obj)"), st_numscalar("e(estimator_twostep)"), st_numscalar("e(N)")))
    mata: pyx_export("../out/ec_kink_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/ec_kink_vc.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/ec_kink_z.csv", xdpt_best_Z_f)
    mata: pyx_export("../out/ec_kink_x.csv", xdpt_best_X_f)
    mata: pyx_export("../out/ec_kink_a.csv", xdpt_best_A)
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
display "@@CASE nocenter"
capture noisily xtdpthresh invest cashflow, qx(debt) exportgmm noboot nocenter grid(10) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/ec_nocenter_sc.csv", (st_numscalar("e(N_iv)"), st_numscalar("e(N_iv_common)"), st_numscalar("e(N_iv_dep)"), st_numscalar("e(N_iv_dep_near)"), st_numscalar("e(iv_dep_res)"), st_numscalar("e(W1_fallback)"), st_numscalar("e(gamma)"), st_numscalar("e(obj)"), st_numscalar("e(estimator_twostep)"), st_numscalar("e(N)")))
    mata: pyx_export("../out/ec_nocenter_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/ec_nocenter_vc.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/ec_nocenter_z.csv", xdpt_best_Z_f)
    mata: pyx_export("../out/ec_nocenter_x.csv", xdpt_best_X_f)
    mata: pyx_export("../out/ec_nocenter_a.csv", xdpt_best_A)
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
capture noisily xtdpthresh invest cashflow, qx(debt) exportgmm noboot grid(10) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/ec_unbalanced_gaps_sc.csv", (st_numscalar("e(N_iv)"), st_numscalar("e(N_iv_common)"), st_numscalar("e(N_iv_dep)"), st_numscalar("e(N_iv_dep_near)"), st_numscalar("e(iv_dep_res)"), st_numscalar("e(W1_fallback)"), st_numscalar("e(gamma)"), st_numscalar("e(obj)"), st_numscalar("e(estimator_twostep)"), st_numscalar("e(N)")))
    mata: pyx_export("../out/ec_unbalanced_gaps_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/ec_unbalanced_gaps_vc.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/ec_unbalanced_gaps_z.csv", xdpt_best_Z_f)
    mata: pyx_export("../out/ec_unbalanced_gaps_x.csv", xdpt_best_X_f)
    mata: pyx_export("../out/ec_unbalanced_gaps_a.csv", xdpt_best_A)
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
capture noisily xtdpthresh invest cashflow, qx(debt) exportgmm noboot grid(10) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/ec_unbalanced_missing_x_sc.csv", (st_numscalar("e(N_iv)"), st_numscalar("e(N_iv_common)"), st_numscalar("e(N_iv_dep)"), st_numscalar("e(N_iv_dep_near)"), st_numscalar("e(iv_dep_res)"), st_numscalar("e(W1_fallback)"), st_numscalar("e(gamma)"), st_numscalar("e(obj)"), st_numscalar("e(estimator_twostep)"), st_numscalar("e(N)")))
    mata: pyx_export("../out/ec_unbalanced_missing_x_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/ec_unbalanced_missing_x_vc.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/ec_unbalanced_missing_x_z.csv", xdpt_best_Z_f)
    mata: pyx_export("../out/ec_unbalanced_missing_x_x.csv", xdpt_best_X_f)
    mata: pyx_export("../out/ec_unbalanced_missing_x_a.csv", xdpt_best_A)
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
capture noisily xtdpthresh invest cashflow, qx(debt) exportgmm noboot grid(10) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/ec_unbalanced_short_units_sc.csv", (st_numscalar("e(N_iv)"), st_numscalar("e(N_iv_common)"), st_numscalar("e(N_iv_dep)"), st_numscalar("e(N_iv_dep_near)"), st_numscalar("e(iv_dep_res)"), st_numscalar("e(W1_fallback)"), st_numscalar("e(gamma)"), st_numscalar("e(obj)"), st_numscalar("e(estimator_twostep)"), st_numscalar("e(N)")))
    mata: pyx_export("../out/ec_unbalanced_short_units_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/ec_unbalanced_short_units_vc.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/ec_unbalanced_short_units_z.csv", xdpt_best_Z_f)
    mata: pyx_export("../out/ec_unbalanced_short_units_x.csv", xdpt_best_X_f)
    mata: pyx_export("../out/ec_unbalanced_short_units_a.csv", xdpt_best_A)
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
capture noisily xtdpthresh invest cashflow, qx(debt) exportgmm noboot grid(10) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/ec_unbalanced_alternate_years_sc.csv", (st_numscalar("e(N_iv)"), st_numscalar("e(N_iv_common)"), st_numscalar("e(N_iv_dep)"), st_numscalar("e(N_iv_dep_near)"), st_numscalar("e(iv_dep_res)"), st_numscalar("e(W1_fallback)"), st_numscalar("e(gamma)"), st_numscalar("e(obj)"), st_numscalar("e(estimator_twostep)"), st_numscalar("e(N)")))
    mata: pyx_export("../out/ec_unbalanced_alternate_years_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/ec_unbalanced_alternate_years_vc.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/ec_unbalanced_alternate_years_z.csv", xdpt_best_Z_f)
    mata: pyx_export("../out/ec_unbalanced_alternate_years_x.csv", xdpt_best_X_f)
    mata: pyx_export("../out/ec_unbalanced_alternate_years_a.csv", xdpt_best_A)
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
capture noisily xtdpthresh invest cashflow, qx(debt) exportgmm noboot grid(10) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/ec_unbalanced_missing_endog_sc.csv", (st_numscalar("e(N_iv)"), st_numscalar("e(N_iv_common)"), st_numscalar("e(N_iv_dep)"), st_numscalar("e(N_iv_dep_near)"), st_numscalar("e(iv_dep_res)"), st_numscalar("e(W1_fallback)"), st_numscalar("e(gamma)"), st_numscalar("e(obj)"), st_numscalar("e(estimator_twostep)"), st_numscalar("e(N)")))
    mata: pyx_export("../out/ec_unbalanced_missing_endog_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/ec_unbalanced_missing_endog_vc.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/ec_unbalanced_missing_endog_z.csv", xdpt_best_Z_f)
    mata: pyx_export("../out/ec_unbalanced_missing_endog_x.csv", xdpt_best_X_f)
    mata: pyx_export("../out/ec_unbalanced_missing_endog_a.csv", xdpt_best_A)
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
display "@@CASE common_variable"
capture noisily xtdpthresh invest cashflow macro, qx(debt) exportgmm noboot grid(10)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/ec_common_variable_sc.csv", (st_numscalar("e(N_iv)"), st_numscalar("e(N_iv_common)"), st_numscalar("e(N_iv_dep)"), st_numscalar("e(N_iv_dep_near)"), st_numscalar("e(iv_dep_res)"), st_numscalar("e(W1_fallback)"), st_numscalar("e(gamma)"), st_numscalar("e(obj)"), st_numscalar("e(estimator_twostep)"), st_numscalar("e(N)")))
    mata: pyx_export("../out/ec_common_variable_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/ec_common_variable_vc.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/ec_common_variable_z.csv", xdpt_best_Z_f)
    mata: pyx_export("../out/ec_common_variable_x.csv", xdpt_best_X_f)
    mata: pyx_export("../out/ec_common_variable_a.csv", xdpt_best_A)
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
display "@@CASE common_variable_collapse"
capture noisily xtdpthresh invest cashflow macro, qx(debt) collapse exportgmm noboot grid(10)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/ec_common_variable_collapse_sc.csv", (st_numscalar("e(N_iv)"), st_numscalar("e(N_iv_common)"), st_numscalar("e(N_iv_dep)"), st_numscalar("e(N_iv_dep_near)"), st_numscalar("e(iv_dep_res)"), st_numscalar("e(W1_fallback)"), st_numscalar("e(gamma)"), st_numscalar("e(obj)"), st_numscalar("e(estimator_twostep)"), st_numscalar("e(N)")))
    mata: pyx_export("../out/ec_common_variable_collapse_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/ec_common_variable_collapse_vc.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/ec_common_variable_collapse_z.csv", xdpt_best_Z_f)
    mata: pyx_export("../out/ec_common_variable_collapse_x.csv", xdpt_best_X_f)
    mata: pyx_export("../out/ec_common_variable_collapse_a.csv", xdpt_best_A)
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
display "@@CASE duplicate_endog_lag"
capture noisily xtdpthresh invest cashflow, qx(debt) exportgmm noboot grid(10) endogenous(tobin_q L.tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/ec_duplicate_endog_lag_sc.csv", (st_numscalar("e(N_iv)"), st_numscalar("e(N_iv_common)"), st_numscalar("e(N_iv_dep)"), st_numscalar("e(N_iv_dep_near)"), st_numscalar("e(iv_dep_res)"), st_numscalar("e(W1_fallback)"), st_numscalar("e(gamma)"), st_numscalar("e(obj)"), st_numscalar("e(estimator_twostep)"), st_numscalar("e(N)")))
    mata: pyx_export("../out/ec_duplicate_endog_lag_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/ec_duplicate_endog_lag_vc.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/ec_duplicate_endog_lag_z.csv", xdpt_best_Z_f)
    mata: pyx_export("../out/ec_duplicate_endog_lag_x.csv", xdpt_best_X_f)
    mata: pyx_export("../out/ec_duplicate_endog_lag_a.csv", xdpt_best_A)
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
display "@@CASE duplicate_predetermined_ylag"
capture noisily xtdpthresh invest cashflow, qx(debt) exportgmm noboot grid(10) predetermined(L2.invest L3.invest)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/ec_duplicate_predetermined_ylag_sc.csv", (st_numscalar("e(N_iv)"), st_numscalar("e(N_iv_common)"), st_numscalar("e(N_iv_dep)"), st_numscalar("e(N_iv_dep_near)"), st_numscalar("e(iv_dep_res)"), st_numscalar("e(W1_fallback)"), st_numscalar("e(gamma)"), st_numscalar("e(obj)"), st_numscalar("e(estimator_twostep)"), st_numscalar("e(N)")))
    mata: pyx_export("../out/ec_duplicate_predetermined_ylag_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/ec_duplicate_predetermined_ylag_vc.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/ec_duplicate_predetermined_ylag_z.csv", xdpt_best_Z_f)
    mata: pyx_export("../out/ec_duplicate_predetermined_ylag_x.csv", xdpt_best_X_f)
    mata: pyx_export("../out/ec_duplicate_predetermined_ylag_a.csv", xdpt_best_A)
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
display "@@CASE dependent_iv"
capture noisily xtdpthresh invest cashflow, qx(debt) exportgmm noboot grid(10) endogenous(tobin_q) iv(ysum)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/ec_dependent_iv_sc.csv", (st_numscalar("e(N_iv)"), st_numscalar("e(N_iv_common)"), st_numscalar("e(N_iv_dep)"), st_numscalar("e(N_iv_dep_near)"), st_numscalar("e(iv_dep_res)"), st_numscalar("e(W1_fallback)"), st_numscalar("e(gamma)"), st_numscalar("e(obj)"), st_numscalar("e(estimator_twostep)"), st_numscalar("e(N)")))
    mata: pyx_export("../out/ec_dependent_iv_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/ec_dependent_iv_vc.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/ec_dependent_iv_z.csv", xdpt_best_Z_f)
    mata: pyx_export("../out/ec_dependent_iv_x.csv", xdpt_best_X_f)
    mata: pyx_export("../out/ec_dependent_iv_a.csv", xdpt_best_A)
}

exit, clear
