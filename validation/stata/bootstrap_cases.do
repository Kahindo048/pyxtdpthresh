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
gen double qdisc = floor(debt/0.25 + 0.5)*0.25
display "@@CASE fd_jump"
capture noisily xtdpthresh invest cashflow, qx(debt) grid(30) boot(99) rseed(20260611) gridci(40) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/bc_fd_jump_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(ci_unresolved)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(pval_lin)"), pyx_sc("e(boot_linearity_valid)"), pyx_sc("e(rseed)"), pyx_sc("e(pval_cont)"), pyx_sc("e(boot_continuity_valid)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_draws)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_p)"), pyx_sc("e(boot_coef_B)"), pyx_sc("e(boot_coef_attempted)"), pyx_sc("e(boot_coef_failed)"), pyx_sc("e(boot_coef_twostep)"), pyx_sc("e(boot_grid_stage1)"), pyx_sc("e(boot_grid_stage2)")))
    mata: pyx_export("../out/bc_fd_jump_grid.csv", st_matrix("e(ci_grid)"))
    mata: pyx_export("../out/bc_fd_jump_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/bc_fd_jump_bootci.csv", st_matrix("e(b_bootci)"))
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
gen double qdisc = floor(debt/0.25 + 0.5)*0.25
display "@@CASE fd_kink"
capture noisily xtdpthresh invest cashflow, qx(debt) kink grid(30) boot(99) rseed(20260611) gridci(40) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/bc_fd_kink_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(ci_unresolved)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(pval_lin)"), pyx_sc("e(boot_linearity_valid)"), pyx_sc("e(rseed)"), pyx_sc("e(pval_cont)"), pyx_sc("e(boot_continuity_valid)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_draws)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_p)"), pyx_sc("e(boot_coef_B)"), pyx_sc("e(boot_coef_attempted)"), pyx_sc("e(boot_coef_failed)"), pyx_sc("e(boot_coef_twostep)"), pyx_sc("e(boot_grid_stage1)"), pyx_sc("e(boot_grid_stage2)")))
    mata: pyx_export("../out/bc_fd_kink_grid.csv", st_matrix("e(ci_grid)"))
    mata: pyx_export("../out/bc_fd_kink_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/bc_fd_kink_bootci.csv", st_matrix("e(b_bootci)"))
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
gen double qdisc = floor(debt/0.25 + 0.5)*0.25
display "@@CASE fod_jump"
capture noisily xtdpthresh invest cashflow, qx(debt) method(fod) grid(30) boot(99) rseed(20260611) gridci(40) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/bc_fod_jump_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(ci_unresolved)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(pval_lin)"), pyx_sc("e(boot_linearity_valid)"), pyx_sc("e(rseed)"), pyx_sc("e(pval_cont)"), pyx_sc("e(boot_continuity_valid)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_draws)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_p)"), pyx_sc("e(boot_coef_B)"), pyx_sc("e(boot_coef_attempted)"), pyx_sc("e(boot_coef_failed)"), pyx_sc("e(boot_coef_twostep)"), pyx_sc("e(boot_grid_stage1)"), pyx_sc("e(boot_grid_stage2)")))
    mata: pyx_export("../out/bc_fod_jump_grid.csv", st_matrix("e(ci_grid)"))
    mata: pyx_export("../out/bc_fod_jump_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/bc_fod_jump_bootci.csv", st_matrix("e(b_bootci)"))
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
gen double qdisc = floor(debt/0.25 + 0.5)*0.25
display "@@CASE fod_kink"
capture noisily xtdpthresh invest cashflow, qx(debt) kink method(fod) grid(30) boot(99) rseed(20260611) gridci(40) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/bc_fod_kink_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(ci_unresolved)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(pval_lin)"), pyx_sc("e(boot_linearity_valid)"), pyx_sc("e(rseed)"), pyx_sc("e(pval_cont)"), pyx_sc("e(boot_continuity_valid)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_draws)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_p)"), pyx_sc("e(boot_coef_B)"), pyx_sc("e(boot_coef_attempted)"), pyx_sc("e(boot_coef_failed)"), pyx_sc("e(boot_coef_twostep)"), pyx_sc("e(boot_grid_stage1)"), pyx_sc("e(boot_grid_stage2)")))
    mata: pyx_export("../out/bc_fod_kink_grid.csv", st_matrix("e(ci_grid)"))
    mata: pyx_export("../out/bc_fod_kink_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/bc_fod_kink_bootci.csv", st_matrix("e(b_bootci)"))
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
gen double qdisc = floor(debt/0.25 + 0.5)*0.25
display "@@CASE fd_td"
capture noisily xtdpthresh invest cashflow, qx(debt) td grid(30) boot(99) rseed(20260611) gridci(40) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/bc_fd_td_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(ci_unresolved)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(pval_lin)"), pyx_sc("e(boot_linearity_valid)"), pyx_sc("e(rseed)"), pyx_sc("e(pval_cont)"), pyx_sc("e(boot_continuity_valid)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_draws)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_p)"), pyx_sc("e(boot_coef_B)"), pyx_sc("e(boot_coef_attempted)"), pyx_sc("e(boot_coef_failed)"), pyx_sc("e(boot_coef_twostep)"), pyx_sc("e(boot_grid_stage1)"), pyx_sc("e(boot_grid_stage2)")))
    mata: pyx_export("../out/bc_fd_td_grid.csv", st_matrix("e(ci_grid)"))
    mata: pyx_export("../out/bc_fd_td_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/bc_fd_td_bootci.csv", st_matrix("e(b_bootci)"))
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
gen double qdisc = floor(debt/0.25 + 0.5)*0.25
display "@@CASE fod_td"
capture noisily xtdpthresh invest cashflow, qx(debt) td method(fod) grid(30) boot(99) rseed(20260611) gridci(40) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/bc_fod_td_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(ci_unresolved)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(pval_lin)"), pyx_sc("e(boot_linearity_valid)"), pyx_sc("e(rseed)"), pyx_sc("e(pval_cont)"), pyx_sc("e(boot_continuity_valid)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_draws)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_p)"), pyx_sc("e(boot_coef_B)"), pyx_sc("e(boot_coef_attempted)"), pyx_sc("e(boot_coef_failed)"), pyx_sc("e(boot_coef_twostep)"), pyx_sc("e(boot_grid_stage1)"), pyx_sc("e(boot_grid_stage2)")))
    mata: pyx_export("../out/bc_fod_td_grid.csv", st_matrix("e(ci_grid)"))
    mata: pyx_export("../out/bc_fod_td_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/bc_fod_td_bootci.csv", st_matrix("e(b_bootci)"))
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
gen double qdisc = floor(debt/0.25 + 0.5)*0.25
display "@@CASE fd_static"
capture noisily xtdpthresh invest cashflow L.tobin_q, qx(debt) static grid(30) boot(99) rseed(20260611) gridci(40)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/bc_fd_static_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(ci_unresolved)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(pval_lin)"), pyx_sc("e(boot_linearity_valid)"), pyx_sc("e(rseed)"), pyx_sc("e(pval_cont)"), pyx_sc("e(boot_continuity_valid)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_draws)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_p)"), pyx_sc("e(boot_coef_B)"), pyx_sc("e(boot_coef_attempted)"), pyx_sc("e(boot_coef_failed)"), pyx_sc("e(boot_coef_twostep)"), pyx_sc("e(boot_grid_stage1)"), pyx_sc("e(boot_grid_stage2)")))
    mata: pyx_export("../out/bc_fd_static_grid.csv", st_matrix("e(ci_grid)"))
    mata: pyx_export("../out/bc_fd_static_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/bc_fd_static_bootci.csv", st_matrix("e(b_bootci)"))
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
gen double qdisc = floor(debt/0.25 + 0.5)*0.25
display "@@CASE fd_exog_only"
capture noisily xtdpthresh invest cashflow, qx(debt) grid(30) boot(99) rseed(20260611) gridci(40)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/bc_fd_exog_only_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(ci_unresolved)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(pval_lin)"), pyx_sc("e(boot_linearity_valid)"), pyx_sc("e(rseed)"), pyx_sc("e(pval_cont)"), pyx_sc("e(boot_continuity_valid)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_draws)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_p)"), pyx_sc("e(boot_coef_B)"), pyx_sc("e(boot_coef_attempted)"), pyx_sc("e(boot_coef_failed)"), pyx_sc("e(boot_coef_twostep)"), pyx_sc("e(boot_grid_stage1)"), pyx_sc("e(boot_grid_stage2)")))
    mata: pyx_export("../out/bc_fd_exog_only_grid.csv", st_matrix("e(ci_grid)"))
    mata: pyx_export("../out/bc_fd_exog_only_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/bc_fd_exog_only_bootci.csv", st_matrix("e(b_bootci)"))
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
gen double qdisc = floor(debt/0.25 + 0.5)*0.25
display "@@CASE fd_collapse"
capture noisily xtdpthresh invest cashflow, qx(debt) collapse grid(30) boot(99) rseed(20260611) gridci(40) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/bc_fd_collapse_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(ci_unresolved)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(pval_lin)"), pyx_sc("e(boot_linearity_valid)"), pyx_sc("e(rseed)"), pyx_sc("e(pval_cont)"), pyx_sc("e(boot_continuity_valid)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_draws)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_p)"), pyx_sc("e(boot_coef_B)"), pyx_sc("e(boot_coef_attempted)"), pyx_sc("e(boot_coef_failed)"), pyx_sc("e(boot_coef_twostep)"), pyx_sc("e(boot_grid_stage1)"), pyx_sc("e(boot_grid_stage2)")))
    mata: pyx_export("../out/bc_fd_collapse_grid.csv", st_matrix("e(ci_grid)"))
    mata: pyx_export("../out/bc_fd_collapse_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/bc_fd_collapse_bootci.csv", st_matrix("e(b_bootci)"))
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
gen double qdisc = floor(debt/0.25 + 0.5)*0.25
display "@@CASE fd_iv"
capture noisily xtdpthresh invest cashflow, qx(debt) grid(30) boot(99) rseed(20260611) gridci(40) endogenous(tobin_q) iv(z1 z2)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/bc_fd_iv_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(ci_unresolved)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(pval_lin)"), pyx_sc("e(boot_linearity_valid)"), pyx_sc("e(rseed)"), pyx_sc("e(pval_cont)"), pyx_sc("e(boot_continuity_valid)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_draws)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_p)"), pyx_sc("e(boot_coef_B)"), pyx_sc("e(boot_coef_attempted)"), pyx_sc("e(boot_coef_failed)"), pyx_sc("e(boot_coef_twostep)"), pyx_sc("e(boot_grid_stage1)"), pyx_sc("e(boot_grid_stage2)")))
    mata: pyx_export("../out/bc_fd_iv_grid.csv", st_matrix("e(ci_grid)"))
    mata: pyx_export("../out/bc_fd_iv_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/bc_fd_iv_bootci.csv", st_matrix("e(b_bootci)"))
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
gen double qdisc = floor(debt/0.25 + 0.5)*0.25
drop if mod(firm + 3*year, 11) == 0
display "@@CASE fd_gaps"
capture noisily xtdpthresh invest cashflow, qx(debt) grid(30) boot(99) rseed(20260611) gridci(40) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/bc_fd_gaps_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(ci_unresolved)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(pval_lin)"), pyx_sc("e(boot_linearity_valid)"), pyx_sc("e(rseed)"), pyx_sc("e(pval_cont)"), pyx_sc("e(boot_continuity_valid)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_draws)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_p)"), pyx_sc("e(boot_coef_B)"), pyx_sc("e(boot_coef_attempted)"), pyx_sc("e(boot_coef_failed)"), pyx_sc("e(boot_coef_twostep)"), pyx_sc("e(boot_grid_stage1)"), pyx_sc("e(boot_grid_stage2)")))
    mata: pyx_export("../out/bc_fd_gaps_grid.csv", st_matrix("e(ci_grid)"))
    mata: pyx_export("../out/bc_fd_gaps_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/bc_fd_gaps_bootci.csv", st_matrix("e(b_bootci)"))
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
gen double qdisc = floor(debt/0.25 + 0.5)*0.25
drop if firm <= 10 & year > 1973
drop if firm >= 11 & firm <= 20 & year > 1974
display "@@CASE fd_short"
capture noisily xtdpthresh invest cashflow, qx(debt) grid(30) boot(99) rseed(20260611) gridci(40) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/bc_fd_short_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(ci_unresolved)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(pval_lin)"), pyx_sc("e(boot_linearity_valid)"), pyx_sc("e(rseed)"), pyx_sc("e(pval_cont)"), pyx_sc("e(boot_continuity_valid)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_draws)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_p)"), pyx_sc("e(boot_coef_B)"), pyx_sc("e(boot_coef_attempted)"), pyx_sc("e(boot_coef_failed)"), pyx_sc("e(boot_coef_twostep)"), pyx_sc("e(boot_grid_stage1)"), pyx_sc("e(boot_grid_stage2)")))
    mata: pyx_export("../out/bc_fd_short_grid.csv", st_matrix("e(ci_grid)"))
    mata: pyx_export("../out/bc_fd_short_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/bc_fd_short_bootci.csv", st_matrix("e(b_bootci)"))
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
gen double qdisc = floor(debt/0.25 + 0.5)*0.25
drop if firm >= 11 & firm <= 40 & mod(year, 2) == 0
display "@@CASE fd_one_step"
capture noisily xtdpthresh invest cashflow, qx(debt) grid(30) boot(99) rseed(20260611) gridci(40) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/bc_fd_one_step_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(ci_unresolved)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(pval_lin)"), pyx_sc("e(boot_linearity_valid)"), pyx_sc("e(rseed)"), pyx_sc("e(pval_cont)"), pyx_sc("e(boot_continuity_valid)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_draws)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_p)"), pyx_sc("e(boot_coef_B)"), pyx_sc("e(boot_coef_attempted)"), pyx_sc("e(boot_coef_failed)"), pyx_sc("e(boot_coef_twostep)"), pyx_sc("e(boot_grid_stage1)"), pyx_sc("e(boot_grid_stage2)")))
    mata: pyx_export("../out/bc_fd_one_step_grid.csv", st_matrix("e(ci_grid)"))
    mata: pyx_export("../out/bc_fd_one_step_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/bc_fd_one_step_bootci.csv", st_matrix("e(b_bootci)"))
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
gen double qdisc = floor(debt/0.25 + 0.5)*0.25
drop if firm >= 11 & firm <= 40 & mod(year, 2) == 0
display "@@CASE fod_one_step"
capture noisily xtdpthresh invest cashflow, qx(debt) method(fod) grid(30) boot(99) rseed(20260611) gridci(40) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/bc_fod_one_step_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(ci_unresolved)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(pval_lin)"), pyx_sc("e(boot_linearity_valid)"), pyx_sc("e(rseed)"), pyx_sc("e(pval_cont)"), pyx_sc("e(boot_continuity_valid)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_draws)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_p)"), pyx_sc("e(boot_coef_B)"), pyx_sc("e(boot_coef_attempted)"), pyx_sc("e(boot_coef_failed)"), pyx_sc("e(boot_coef_twostep)"), pyx_sc("e(boot_grid_stage1)"), pyx_sc("e(boot_grid_stage2)")))
    mata: pyx_export("../out/bc_fod_one_step_grid.csv", st_matrix("e(ci_grid)"))
    mata: pyx_export("../out/bc_fod_one_step_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/bc_fod_one_step_bootci.csv", st_matrix("e(b_bootci)"))
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
gen double qdisc = floor(debt/0.25 + 0.5)*0.25
display "@@CASE fd_refine"
capture noisily xtdpthresh invest cashflow, qx(debt) grid(15) refine(2) boot(99) rseed(20260611) gridci(40) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/bc_fd_refine_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(ci_unresolved)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(pval_lin)"), pyx_sc("e(boot_linearity_valid)"), pyx_sc("e(rseed)"), pyx_sc("e(pval_cont)"), pyx_sc("e(boot_continuity_valid)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_draws)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_p)"), pyx_sc("e(boot_coef_B)"), pyx_sc("e(boot_coef_attempted)"), pyx_sc("e(boot_coef_failed)"), pyx_sc("e(boot_coef_twostep)"), pyx_sc("e(boot_grid_stage1)"), pyx_sc("e(boot_grid_stage2)")))
    mata: pyx_export("../out/bc_fd_refine_grid.csv", st_matrix("e(ci_grid)"))
    mata: pyx_export("../out/bc_fd_refine_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/bc_fd_refine_bootci.csv", st_matrix("e(b_bootci)"))
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
gen double qdisc = floor(debt/0.25 + 0.5)*0.25
display "@@CASE fd_quantile_grid"
capture noisily xtdpthresh invest cashflow, qx(debt) grid(30) gridtype(quantile) boot(99) rseed(20260611) gridci(40) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/bc_fd_quantile_grid_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(ci_unresolved)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(pval_lin)"), pyx_sc("e(boot_linearity_valid)"), pyx_sc("e(rseed)"), pyx_sc("e(pval_cont)"), pyx_sc("e(boot_continuity_valid)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_draws)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_p)"), pyx_sc("e(boot_coef_B)"), pyx_sc("e(boot_coef_attempted)"), pyx_sc("e(boot_coef_failed)"), pyx_sc("e(boot_coef_twostep)"), pyx_sc("e(boot_grid_stage1)"), pyx_sc("e(boot_grid_stage2)")))
    mata: pyx_export("../out/bc_fd_quantile_grid_grid.csv", st_matrix("e(ci_grid)"))
    mata: pyx_export("../out/bc_fd_quantile_grid_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/bc_fd_quantile_grid_bootci.csv", st_matrix("e(b_bootci)"))
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
gen double qdisc = floor(debt/0.25 + 0.5)*0.25
display "@@CASE fd_level_90"
capture noisily xtdpthresh invest cashflow, qx(debt) grid(30) boot(99) rseed(20260611) gridci(40) level(90) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/bc_fd_level_90_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(ci_unresolved)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(pval_lin)"), pyx_sc("e(boot_linearity_valid)"), pyx_sc("e(rseed)"), pyx_sc("e(pval_cont)"), pyx_sc("e(boot_continuity_valid)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_draws)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_p)"), pyx_sc("e(boot_coef_B)"), pyx_sc("e(boot_coef_attempted)"), pyx_sc("e(boot_coef_failed)"), pyx_sc("e(boot_coef_twostep)"), pyx_sc("e(boot_grid_stage1)"), pyx_sc("e(boot_grid_stage2)")))
    mata: pyx_export("../out/bc_fd_level_90_grid.csv", st_matrix("e(ci_grid)"))
    mata: pyx_export("../out/bc_fd_level_90_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/bc_fd_level_90_bootci.csv", st_matrix("e(b_bootci)"))
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
gen double qdisc = floor(debt/0.25 + 0.5)*0.25
display "@@CASE fd_no_linearity_test"
capture noisily xtdpthresh invest cashflow, qx(debt) notest grid(30) boot(99) rseed(20260611) gridci(40) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/bc_fd_no_linearity_test_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(ci_unresolved)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(pval_lin)"), pyx_sc("e(boot_linearity_valid)"), pyx_sc("e(rseed)"), pyx_sc("e(pval_cont)"), pyx_sc("e(boot_continuity_valid)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_draws)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_p)"), pyx_sc("e(boot_coef_B)"), pyx_sc("e(boot_coef_attempted)"), pyx_sc("e(boot_coef_failed)"), pyx_sc("e(boot_coef_twostep)"), pyx_sc("e(boot_grid_stage1)"), pyx_sc("e(boot_grid_stage2)")))
    mata: pyx_export("../out/bc_fd_no_linearity_test_grid.csv", st_matrix("e(ci_grid)"))
    mata: pyx_export("../out/bc_fd_no_linearity_test_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/bc_fd_no_linearity_test_bootci.csv", st_matrix("e(b_bootci)"))
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
gen double qdisc = floor(debt/0.25 + 0.5)*0.25
display "@@CASE fd_small_boot"
capture noisily xtdpthresh invest cashflow, qx(debt) grid(30) boot(19) rseed(20260611) gridci(40) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/bc_fd_small_boot_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(ci_unresolved)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(pval_lin)"), pyx_sc("e(boot_linearity_valid)"), pyx_sc("e(rseed)"), pyx_sc("e(pval_cont)"), pyx_sc("e(boot_continuity_valid)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_draws)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_p)"), pyx_sc("e(boot_coef_B)"), pyx_sc("e(boot_coef_attempted)"), pyx_sc("e(boot_coef_failed)"), pyx_sc("e(boot_coef_twostep)"), pyx_sc("e(boot_grid_stage1)"), pyx_sc("e(boot_grid_stage2)")))
    mata: pyx_export("../out/bc_fd_small_boot_grid.csv", st_matrix("e(ci_grid)"))
    mata: pyx_export("../out/bc_fd_small_boot_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/bc_fd_small_boot_bootci.csv", st_matrix("e(b_bootci)"))
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
gen double qdisc = floor(debt/0.25 + 0.5)*0.25
display "@@CASE cont_fd"
capture noisily xtdpthresh invest cashflow debt, qx(debt) conttest grid(30) boot(99) rseed(20260611) gridci(40) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/bc_cont_fd_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(ci_unresolved)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(pval_lin)"), pyx_sc("e(boot_linearity_valid)"), pyx_sc("e(rseed)"), pyx_sc("e(pval_cont)"), pyx_sc("e(boot_continuity_valid)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_draws)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_p)"), pyx_sc("e(boot_coef_B)"), pyx_sc("e(boot_coef_attempted)"), pyx_sc("e(boot_coef_failed)"), pyx_sc("e(boot_coef_twostep)"), pyx_sc("e(boot_grid_stage1)"), pyx_sc("e(boot_grid_stage2)")))
    mata: pyx_export("../out/bc_cont_fd_grid.csv", st_matrix("e(ci_grid)"))
    mata: pyx_export("../out/bc_cont_fd_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/bc_cont_fd_bootci.csv", st_matrix("e(b_bootci)"))
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
gen double qdisc = floor(debt/0.25 + 0.5)*0.25
display "@@CASE cont_fod"
capture noisily xtdpthresh invest cashflow debt, qx(debt) conttest method(fod) grid(30) boot(99) rseed(20260611) gridci(40) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/bc_cont_fod_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(ci_unresolved)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(pval_lin)"), pyx_sc("e(boot_linearity_valid)"), pyx_sc("e(rseed)"), pyx_sc("e(pval_cont)"), pyx_sc("e(boot_continuity_valid)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_draws)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_p)"), pyx_sc("e(boot_coef_B)"), pyx_sc("e(boot_coef_attempted)"), pyx_sc("e(boot_coef_failed)"), pyx_sc("e(boot_coef_twostep)"), pyx_sc("e(boot_grid_stage1)"), pyx_sc("e(boot_grid_stage2)")))
    mata: pyx_export("../out/bc_cont_fod_grid.csv", st_matrix("e(ci_grid)"))
    mata: pyx_export("../out/bc_cont_fod_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/bc_cont_fod_bootci.csv", st_matrix("e(b_bootci)"))
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
gen double qdisc = floor(debt/0.25 + 0.5)*0.25
display "@@CASE cont_fd_td"
capture noisily xtdpthresh invest cashflow debt, qx(debt) td conttest grid(30) boot(99) rseed(20260611) gridci(40) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/bc_cont_fd_td_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(ci_unresolved)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(pval_lin)"), pyx_sc("e(boot_linearity_valid)"), pyx_sc("e(rseed)"), pyx_sc("e(pval_cont)"), pyx_sc("e(boot_continuity_valid)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_draws)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_p)"), pyx_sc("e(boot_coef_B)"), pyx_sc("e(boot_coef_attempted)"), pyx_sc("e(boot_coef_failed)"), pyx_sc("e(boot_coef_twostep)"), pyx_sc("e(boot_grid_stage1)"), pyx_sc("e(boot_grid_stage2)")))
    mata: pyx_export("../out/bc_cont_fd_td_grid.csv", st_matrix("e(ci_grid)"))
    mata: pyx_export("../out/bc_cont_fd_td_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/bc_cont_fd_td_bootci.csv", st_matrix("e(b_bootci)"))
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
gen double qdisc = floor(debt/0.25 + 0.5)*0.25
display "@@CASE cont_fd_static"
capture noisily xtdpthresh invest cashflow L.tobin_q debt, qx(debt) static conttest grid(30) boot(99) rseed(20260611) gridci(40)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/bc_cont_fd_static_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(ci_unresolved)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(pval_lin)"), pyx_sc("e(boot_linearity_valid)"), pyx_sc("e(rseed)"), pyx_sc("e(pval_cont)"), pyx_sc("e(boot_continuity_valid)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_draws)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_p)"), pyx_sc("e(boot_coef_B)"), pyx_sc("e(boot_coef_attempted)"), pyx_sc("e(boot_coef_failed)"), pyx_sc("e(boot_coef_twostep)"), pyx_sc("e(boot_grid_stage1)"), pyx_sc("e(boot_grid_stage2)")))
    mata: pyx_export("../out/bc_cont_fd_static_grid.csv", st_matrix("e(ci_grid)"))
    mata: pyx_export("../out/bc_cont_fd_static_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/bc_cont_fd_static_bootci.csv", st_matrix("e(b_bootci)"))
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
gen double qdisc = floor(debt/0.25 + 0.5)*0.25
drop if firm >= 11 & firm <= 40 & mod(year, 2) == 0
display "@@CASE cont_fd_one_step"
capture noisily xtdpthresh invest cashflow debt, qx(debt) conttest grid(30) boot(99) rseed(20260611) gridci(40) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/bc_cont_fd_one_step_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(ci_unresolved)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(pval_lin)"), pyx_sc("e(boot_linearity_valid)"), pyx_sc("e(rseed)"), pyx_sc("e(pval_cont)"), pyx_sc("e(boot_continuity_valid)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_draws)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_p)"), pyx_sc("e(boot_coef_B)"), pyx_sc("e(boot_coef_attempted)"), pyx_sc("e(boot_coef_failed)"), pyx_sc("e(boot_coef_twostep)"), pyx_sc("e(boot_grid_stage1)"), pyx_sc("e(boot_grid_stage2)")))
    mata: pyx_export("../out/bc_cont_fd_one_step_grid.csv", st_matrix("e(ci_grid)"))
    mata: pyx_export("../out/bc_cont_fd_one_step_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/bc_cont_fd_one_step_bootci.csv", st_matrix("e(b_bootci)"))
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
gen double qdisc = floor(debt/0.25 + 0.5)*0.25
drop if mod(firm + 3*year, 11) == 0
display "@@CASE cont_fd_gaps"
capture noisily xtdpthresh invest cashflow debt, qx(debt) conttest grid(30) boot(99) rseed(20260611) gridci(40) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/bc_cont_fd_gaps_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(ci_unresolved)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(pval_lin)"), pyx_sc("e(boot_linearity_valid)"), pyx_sc("e(rseed)"), pyx_sc("e(pval_cont)"), pyx_sc("e(boot_continuity_valid)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_draws)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_p)"), pyx_sc("e(boot_coef_B)"), pyx_sc("e(boot_coef_attempted)"), pyx_sc("e(boot_coef_failed)"), pyx_sc("e(boot_coef_twostep)"), pyx_sc("e(boot_grid_stage1)"), pyx_sc("e(boot_grid_stage2)")))
    mata: pyx_export("../out/bc_cont_fd_gaps_grid.csv", st_matrix("e(ci_grid)"))
    mata: pyx_export("../out/bc_cont_fd_gaps_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/bc_cont_fd_gaps_bootci.csv", st_matrix("e(b_bootci)"))
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
gen double qdisc = floor(debt/0.25 + 0.5)*0.25
display "@@CASE cont_fd_collapse"
capture noisily xtdpthresh invest cashflow debt, qx(debt) collapse conttest grid(30) boot(99) rseed(20260611) gridci(40) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/bc_cont_fd_collapse_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(ci_unresolved)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(pval_lin)"), pyx_sc("e(boot_linearity_valid)"), pyx_sc("e(rseed)"), pyx_sc("e(pval_cont)"), pyx_sc("e(boot_continuity_valid)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_draws)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_p)"), pyx_sc("e(boot_coef_B)"), pyx_sc("e(boot_coef_attempted)"), pyx_sc("e(boot_coef_failed)"), pyx_sc("e(boot_coef_twostep)"), pyx_sc("e(boot_grid_stage1)"), pyx_sc("e(boot_grid_stage2)")))
    mata: pyx_export("../out/bc_cont_fd_collapse_grid.csv", st_matrix("e(ci_grid)"))
    mata: pyx_export("../out/bc_cont_fd_collapse_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/bc_cont_fd_collapse_bootci.csv", st_matrix("e(b_bootci)"))
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
gen double qdisc = floor(debt/0.25 + 0.5)*0.25
display "@@CASE cont_without_q"
capture noisily xtdpthresh invest cashflow, qx(debt) conttest grid(30) boot(99) rseed(20260611) gridci(40) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/bc_cont_without_q_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(ci_unresolved)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(pval_lin)"), pyx_sc("e(boot_linearity_valid)"), pyx_sc("e(rseed)"), pyx_sc("e(pval_cont)"), pyx_sc("e(boot_continuity_valid)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_draws)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_p)"), pyx_sc("e(boot_coef_B)"), pyx_sc("e(boot_coef_attempted)"), pyx_sc("e(boot_coef_failed)"), pyx_sc("e(boot_coef_twostep)"), pyx_sc("e(boot_grid_stage1)"), pyx_sc("e(boot_grid_stage2)")))
    mata: pyx_export("../out/bc_cont_without_q_grid.csv", st_matrix("e(ci_grid)"))
    mata: pyx_export("../out/bc_cont_without_q_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/bc_cont_without_q_bootci.csv", st_matrix("e(b_bootci)"))
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
gen double qdisc = floor(debt/0.25 + 0.5)*0.25
display "@@CASE citest_inside"
capture noisily xtdpthresh invest cashflow, qx(debt) grid(30) boot(99) rseed(20260611) gridci(40) citest(0.2) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/bc_citest_inside_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(ci_unresolved)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(pval_lin)"), pyx_sc("e(boot_linearity_valid)"), pyx_sc("e(rseed)"), pyx_sc("e(pval_cont)"), pyx_sc("e(boot_continuity_valid)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_draws)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_p)"), pyx_sc("e(boot_coef_B)"), pyx_sc("e(boot_coef_attempted)"), pyx_sc("e(boot_coef_failed)"), pyx_sc("e(boot_coef_twostep)"), pyx_sc("e(boot_grid_stage1)"), pyx_sc("e(boot_grid_stage2)")))
    mata: pyx_export("../out/bc_citest_inside_grid.csv", st_matrix("e(ci_grid)"))
    mata: pyx_export("../out/bc_citest_inside_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/bc_citest_inside_bootci.csv", st_matrix("e(b_bootci)"))
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
gen double qdisc = floor(debt/0.25 + 0.5)*0.25
display "@@CASE citest_outside"
capture noisily xtdpthresh invest cashflow, qx(debt) grid(30) boot(99) rseed(20260611) gridci(40) citest(0.45) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/bc_citest_outside_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(ci_unresolved)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(pval_lin)"), pyx_sc("e(boot_linearity_valid)"), pyx_sc("e(rseed)"), pyx_sc("e(pval_cont)"), pyx_sc("e(boot_continuity_valid)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_draws)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_p)"), pyx_sc("e(boot_coef_B)"), pyx_sc("e(boot_coef_attempted)"), pyx_sc("e(boot_coef_failed)"), pyx_sc("e(boot_coef_twostep)"), pyx_sc("e(boot_grid_stage1)"), pyx_sc("e(boot_grid_stage2)")))
    mata: pyx_export("../out/bc_citest_outside_grid.csv", st_matrix("e(ci_grid)"))
    mata: pyx_export("../out/bc_citest_outside_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/bc_citest_outside_bootci.csv", st_matrix("e(b_bootci)"))
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
gen double qdisc = floor(debt/0.25 + 0.5)*0.25
display "@@CASE citest_kink"
capture noisily xtdpthresh invest cashflow, qx(debt) kink grid(30) boot(99) rseed(20260611) gridci(40) citest(0.2) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/bc_citest_kink_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(ci_unresolved)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(pval_lin)"), pyx_sc("e(boot_linearity_valid)"), pyx_sc("e(rseed)"), pyx_sc("e(pval_cont)"), pyx_sc("e(boot_continuity_valid)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_draws)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_p)"), pyx_sc("e(boot_coef_B)"), pyx_sc("e(boot_coef_attempted)"), pyx_sc("e(boot_coef_failed)"), pyx_sc("e(boot_coef_twostep)"), pyx_sc("e(boot_grid_stage1)"), pyx_sc("e(boot_grid_stage2)")))
    mata: pyx_export("../out/bc_citest_kink_grid.csv", st_matrix("e(ci_grid)"))
    mata: pyx_export("../out/bc_citest_kink_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/bc_citest_kink_bootci.csv", st_matrix("e(b_bootci)"))
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
gen double qdisc = floor(debt/0.25 + 0.5)*0.25
display "@@CASE citest_fod"
capture noisily xtdpthresh invest cashflow, qx(debt) method(fod) grid(30) boot(99) rseed(20260611) gridci(40) citest(0.2) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/bc_citest_fod_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(ci_unresolved)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(pval_lin)"), pyx_sc("e(boot_linearity_valid)"), pyx_sc("e(rseed)"), pyx_sc("e(pval_cont)"), pyx_sc("e(boot_continuity_valid)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_draws)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_p)"), pyx_sc("e(boot_coef_B)"), pyx_sc("e(boot_coef_attempted)"), pyx_sc("e(boot_coef_failed)"), pyx_sc("e(boot_coef_twostep)"), pyx_sc("e(boot_grid_stage1)"), pyx_sc("e(boot_grid_stage2)")))
    mata: pyx_export("../out/bc_citest_fod_grid.csv", st_matrix("e(ci_grid)"))
    mata: pyx_export("../out/bc_citest_fod_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/bc_citest_fod_bootci.csv", st_matrix("e(b_bootci)"))
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
gen double qdisc = floor(debt/0.25 + 0.5)*0.25
drop if firm >= 11 & firm <= 40 & mod(year, 2) == 0
display "@@CASE citest_one_step"
capture noisily xtdpthresh invest cashflow, qx(debt) grid(30) boot(99) rseed(20260611) gridci(40) citest(0.2) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/bc_citest_one_step_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(ci_unresolved)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(pval_lin)"), pyx_sc("e(boot_linearity_valid)"), pyx_sc("e(rseed)"), pyx_sc("e(pval_cont)"), pyx_sc("e(boot_continuity_valid)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_draws)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_p)"), pyx_sc("e(boot_coef_B)"), pyx_sc("e(boot_coef_attempted)"), pyx_sc("e(boot_coef_failed)"), pyx_sc("e(boot_coef_twostep)"), pyx_sc("e(boot_grid_stage1)"), pyx_sc("e(boot_grid_stage2)")))
    mata: pyx_export("../out/bc_citest_one_step_grid.csv", st_matrix("e(ci_grid)"))
    mata: pyx_export("../out/bc_citest_one_step_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/bc_citest_one_step_bootci.csv", st_matrix("e(b_bootci)"))
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
gen double qdisc = floor(debt/0.25 + 0.5)*0.25
display "@@CASE citest_with_tests"
capture noisily xtdpthresh invest cashflow debt, qx(debt) conttest grid(30) boot(99) rseed(20260611) gridci(40) citest(0.3) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/bc_citest_with_tests_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(ci_unresolved)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(pval_lin)"), pyx_sc("e(boot_linearity_valid)"), pyx_sc("e(rseed)"), pyx_sc("e(pval_cont)"), pyx_sc("e(boot_continuity_valid)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_draws)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_p)"), pyx_sc("e(boot_coef_B)"), pyx_sc("e(boot_coef_attempted)"), pyx_sc("e(boot_coef_failed)"), pyx_sc("e(boot_coef_twostep)"), pyx_sc("e(boot_grid_stage1)"), pyx_sc("e(boot_grid_stage2)")))
    mata: pyx_export("../out/bc_citest_with_tests_grid.csv", st_matrix("e(ci_grid)"))
    mata: pyx_export("../out/bc_citest_with_tests_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/bc_citest_with_tests_bootci.csv", st_matrix("e(b_bootci)"))
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
gen double qdisc = floor(debt/0.25 + 0.5)*0.25
display "@@CASE citest_unseeded_subset"
capture noisily xtdpthresh invest cashflow, qx(debt) grid(30) boot(99) rseed(20260611) gridci(40) citest(0.0) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/bc_citest_unseeded_subset_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(ci_unresolved)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(pval_lin)"), pyx_sc("e(boot_linearity_valid)"), pyx_sc("e(rseed)"), pyx_sc("e(pval_cont)"), pyx_sc("e(boot_continuity_valid)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_draws)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_p)"), pyx_sc("e(boot_coef_B)"), pyx_sc("e(boot_coef_attempted)"), pyx_sc("e(boot_coef_failed)"), pyx_sc("e(boot_coef_twostep)"), pyx_sc("e(boot_grid_stage1)"), pyx_sc("e(boot_grid_stage2)")))
    mata: pyx_export("../out/bc_citest_unseeded_subset_grid.csv", st_matrix("e(ci_grid)"))
    mata: pyx_export("../out/bc_citest_unseeded_subset_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/bc_citest_unseeded_subset_bootci.csv", st_matrix("e(b_bootci)"))
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
gen double qdisc = floor(debt/0.25 + 0.5)*0.25
display "@@CASE coef_twostep"
capture noisily xtdpthresh invest cashflow, qx(debt) grid(30) boot(99) rseed(20260611) gridci(40) coefboot(twostep) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/bc_coef_twostep_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(ci_unresolved)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(pval_lin)"), pyx_sc("e(boot_linearity_valid)"), pyx_sc("e(rseed)"), pyx_sc("e(pval_cont)"), pyx_sc("e(boot_continuity_valid)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_draws)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_p)"), pyx_sc("e(boot_coef_B)"), pyx_sc("e(boot_coef_attempted)"), pyx_sc("e(boot_coef_failed)"), pyx_sc("e(boot_coef_twostep)"), pyx_sc("e(boot_grid_stage1)"), pyx_sc("e(boot_grid_stage2)")))
    mata: pyx_export("../out/bc_coef_twostep_grid.csv", st_matrix("e(ci_grid)"))
    mata: pyx_export("../out/bc_coef_twostep_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/bc_coef_twostep_bootci.csv", st_matrix("e(b_bootci)"))
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
gen double qdisc = floor(debt/0.25 + 0.5)*0.25
display "@@CASE coef_onestep"
capture noisily xtdpthresh invest cashflow, qx(debt) grid(30) boot(99) rseed(20260611) gridci(40) coefboot(onestep) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/bc_coef_onestep_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(ci_unresolved)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(pval_lin)"), pyx_sc("e(boot_linearity_valid)"), pyx_sc("e(rseed)"), pyx_sc("e(pval_cont)"), pyx_sc("e(boot_continuity_valid)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_draws)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_p)"), pyx_sc("e(boot_coef_B)"), pyx_sc("e(boot_coef_attempted)"), pyx_sc("e(boot_coef_failed)"), pyx_sc("e(boot_coef_twostep)"), pyx_sc("e(boot_grid_stage1)"), pyx_sc("e(boot_grid_stage2)")))
    mata: pyx_export("../out/bc_coef_onestep_grid.csv", st_matrix("e(ci_grid)"))
    mata: pyx_export("../out/bc_coef_onestep_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/bc_coef_onestep_bootci.csv", st_matrix("e(b_bootci)"))
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
gen double qdisc = floor(debt/0.25 + 0.5)*0.25
display "@@CASE coef_twostep_percentile"
capture noisily xtdpthresh invest cashflow, qx(debt) grid(30) boot(99) rseed(20260611) gridci(40) coefboot(twostep) coefcitype(percentile) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/bc_coef_twostep_percentile_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(ci_unresolved)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(pval_lin)"), pyx_sc("e(boot_linearity_valid)"), pyx_sc("e(rseed)"), pyx_sc("e(pval_cont)"), pyx_sc("e(boot_continuity_valid)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_draws)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_p)"), pyx_sc("e(boot_coef_B)"), pyx_sc("e(boot_coef_attempted)"), pyx_sc("e(boot_coef_failed)"), pyx_sc("e(boot_coef_twostep)"), pyx_sc("e(boot_grid_stage1)"), pyx_sc("e(boot_grid_stage2)")))
    mata: pyx_export("../out/bc_coef_twostep_percentile_grid.csv", st_matrix("e(ci_grid)"))
    mata: pyx_export("../out/bc_coef_twostep_percentile_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/bc_coef_twostep_percentile_bootci.csv", st_matrix("e(b_bootci)"))
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
gen double qdisc = floor(debt/0.25 + 0.5)*0.25
display "@@CASE coef_onestep_percentile"
capture noisily xtdpthresh invest cashflow, qx(debt) grid(30) boot(99) rseed(20260611) gridci(40) coefboot(onestep) coefcitype(percentile) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/bc_coef_onestep_percentile_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(ci_unresolved)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(pval_lin)"), pyx_sc("e(boot_linearity_valid)"), pyx_sc("e(rseed)"), pyx_sc("e(pval_cont)"), pyx_sc("e(boot_continuity_valid)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_draws)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_p)"), pyx_sc("e(boot_coef_B)"), pyx_sc("e(boot_coef_attempted)"), pyx_sc("e(boot_coef_failed)"), pyx_sc("e(boot_coef_twostep)"), pyx_sc("e(boot_grid_stage1)"), pyx_sc("e(boot_grid_stage2)")))
    mata: pyx_export("../out/bc_coef_onestep_percentile_grid.csv", st_matrix("e(ci_grid)"))
    mata: pyx_export("../out/bc_coef_onestep_percentile_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/bc_coef_onestep_percentile_bootci.csv", st_matrix("e(b_bootci)"))
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
gen double qdisc = floor(debt/0.25 + 0.5)*0.25
display "@@CASE coef_twostep_kink"
capture noisily xtdpthresh invest cashflow, qx(debt) kink grid(30) boot(99) rseed(20260611) gridci(40) coefboot(twostep) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/bc_coef_twostep_kink_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(ci_unresolved)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(pval_lin)"), pyx_sc("e(boot_linearity_valid)"), pyx_sc("e(rseed)"), pyx_sc("e(pval_cont)"), pyx_sc("e(boot_continuity_valid)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_draws)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_p)"), pyx_sc("e(boot_coef_B)"), pyx_sc("e(boot_coef_attempted)"), pyx_sc("e(boot_coef_failed)"), pyx_sc("e(boot_coef_twostep)"), pyx_sc("e(boot_grid_stage1)"), pyx_sc("e(boot_grid_stage2)")))
    mata: pyx_export("../out/bc_coef_twostep_kink_grid.csv", st_matrix("e(ci_grid)"))
    mata: pyx_export("../out/bc_coef_twostep_kink_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/bc_coef_twostep_kink_bootci.csv", st_matrix("e(b_bootci)"))
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
gen double qdisc = floor(debt/0.25 + 0.5)*0.25
display "@@CASE coef_twostep_fod"
capture noisily xtdpthresh invest cashflow, qx(debt) method(fod) grid(30) boot(99) rseed(20260611) gridci(40) coefboot(twostep) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/bc_coef_twostep_fod_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(ci_unresolved)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(pval_lin)"), pyx_sc("e(boot_linearity_valid)"), pyx_sc("e(rseed)"), pyx_sc("e(pval_cont)"), pyx_sc("e(boot_continuity_valid)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_draws)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_p)"), pyx_sc("e(boot_coef_B)"), pyx_sc("e(boot_coef_attempted)"), pyx_sc("e(boot_coef_failed)"), pyx_sc("e(boot_coef_twostep)"), pyx_sc("e(boot_grid_stage1)"), pyx_sc("e(boot_grid_stage2)")))
    mata: pyx_export("../out/bc_coef_twostep_fod_grid.csv", st_matrix("e(ci_grid)"))
    mata: pyx_export("../out/bc_coef_twostep_fod_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/bc_coef_twostep_fod_bootci.csv", st_matrix("e(b_bootci)"))
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
gen double qdisc = floor(debt/0.25 + 0.5)*0.25
display "@@CASE coef_onestep_td"
capture noisily xtdpthresh invest cashflow, qx(debt) td grid(30) boot(99) rseed(20260611) gridci(40) coefboot(onestep) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/bc_coef_onestep_td_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(ci_unresolved)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(pval_lin)"), pyx_sc("e(boot_linearity_valid)"), pyx_sc("e(rseed)"), pyx_sc("e(pval_cont)"), pyx_sc("e(boot_continuity_valid)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_draws)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_p)"), pyx_sc("e(boot_coef_B)"), pyx_sc("e(boot_coef_attempted)"), pyx_sc("e(boot_coef_failed)"), pyx_sc("e(boot_coef_twostep)"), pyx_sc("e(boot_grid_stage1)"), pyx_sc("e(boot_grid_stage2)")))
    mata: pyx_export("../out/bc_coef_onestep_td_grid.csv", st_matrix("e(ci_grid)"))
    mata: pyx_export("../out/bc_coef_onestep_td_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/bc_coef_onestep_td_bootci.csv", st_matrix("e(b_bootci)"))
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
gen double qdisc = floor(debt/0.25 + 0.5)*0.25
drop if firm >= 11 & firm <= 40 & mod(year, 2) == 0
display "@@CASE coef_twostep_one_step_fit"
capture noisily xtdpthresh invest cashflow, qx(debt) grid(30) boot(99) rseed(20260611) gridci(40) coefboot(twostep) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/bc_coef_twostep_one_step_fit_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(ci_unresolved)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(pval_lin)"), pyx_sc("e(boot_linearity_valid)"), pyx_sc("e(rseed)"), pyx_sc("e(pval_cont)"), pyx_sc("e(boot_continuity_valid)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_draws)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_p)"), pyx_sc("e(boot_coef_B)"), pyx_sc("e(boot_coef_attempted)"), pyx_sc("e(boot_coef_failed)"), pyx_sc("e(boot_coef_twostep)"), pyx_sc("e(boot_grid_stage1)"), pyx_sc("e(boot_grid_stage2)")))
    mata: pyx_export("../out/bc_coef_twostep_one_step_fit_grid.csv", st_matrix("e(ci_grid)"))
    mata: pyx_export("../out/bc_coef_twostep_one_step_fit_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/bc_coef_twostep_one_step_fit_bootci.csv", st_matrix("e(b_bootci)"))
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
gen double qdisc = floor(debt/0.25 + 0.5)*0.25
display "@@CASE coef_twostep_refine"
capture noisily xtdpthresh invest cashflow, qx(debt) grid(15) refine(2) boot(99) rseed(20260611) gridci(40) coefboot(twostep) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/bc_coef_twostep_refine_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(ci_unresolved)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(pval_lin)"), pyx_sc("e(boot_linearity_valid)"), pyx_sc("e(rseed)"), pyx_sc("e(pval_cont)"), pyx_sc("e(boot_continuity_valid)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_draws)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_p)"), pyx_sc("e(boot_coef_B)"), pyx_sc("e(boot_coef_attempted)"), pyx_sc("e(boot_coef_failed)"), pyx_sc("e(boot_coef_twostep)"), pyx_sc("e(boot_grid_stage1)"), pyx_sc("e(boot_grid_stage2)")))
    mata: pyx_export("../out/bc_coef_twostep_refine_grid.csv", st_matrix("e(ci_grid)"))
    mata: pyx_export("../out/bc_coef_twostep_refine_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/bc_coef_twostep_refine_bootci.csv", st_matrix("e(b_bootci)"))
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
gen double qdisc = floor(debt/0.25 + 0.5)*0.25
display "@@CASE coef_twostep_collapse"
capture noisily xtdpthresh invest cashflow, qx(debt) collapse grid(30) boot(99) rseed(20260611) gridci(40) coefboot(twostep) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/bc_coef_twostep_collapse_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(ci_unresolved)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(pval_lin)"), pyx_sc("e(boot_linearity_valid)"), pyx_sc("e(rseed)"), pyx_sc("e(pval_cont)"), pyx_sc("e(boot_continuity_valid)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_draws)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_p)"), pyx_sc("e(boot_coef_B)"), pyx_sc("e(boot_coef_attempted)"), pyx_sc("e(boot_coef_failed)"), pyx_sc("e(boot_coef_twostep)"), pyx_sc("e(boot_grid_stage1)"), pyx_sc("e(boot_grid_stage2)")))
    mata: pyx_export("../out/bc_coef_twostep_collapse_grid.csv", st_matrix("e(ci_grid)"))
    mata: pyx_export("../out/bc_coef_twostep_collapse_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/bc_coef_twostep_collapse_bootci.csv", st_matrix("e(b_bootci)"))
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
gen double qdisc = floor(debt/0.25 + 0.5)*0.25
display "@@CASE coef_twostep_td"
capture noisily xtdpthresh invest cashflow, qx(debt) td grid(30) boot(99) rseed(20260611) gridci(40) coefboot(twostep) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/bc_coef_twostep_td_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(ci_unresolved)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(pval_lin)"), pyx_sc("e(boot_linearity_valid)"), pyx_sc("e(rseed)"), pyx_sc("e(pval_cont)"), pyx_sc("e(boot_continuity_valid)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_draws)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_p)"), pyx_sc("e(boot_coef_B)"), pyx_sc("e(boot_coef_attempted)"), pyx_sc("e(boot_coef_failed)"), pyx_sc("e(boot_coef_twostep)"), pyx_sc("e(boot_grid_stage1)"), pyx_sc("e(boot_grid_stage2)")))
    mata: pyx_export("../out/bc_coef_twostep_td_grid.csv", st_matrix("e(ci_grid)"))
    mata: pyx_export("../out/bc_coef_twostep_td_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/bc_coef_twostep_td_bootci.csv", st_matrix("e(b_bootci)"))
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
gen double qdisc = floor(debt/0.25 + 0.5)*0.25
display "@@CASE unit_fd"
capture noisily xtdpthresh invest cashflow, qx(debt) grid(30) boot(99) boottype(unit) rseed(20260611) gridci(40) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/bc_unit_fd_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(ci_unresolved)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(pval_lin)"), pyx_sc("e(boot_linearity_valid)"), pyx_sc("e(rseed)"), pyx_sc("e(pval_cont)"), pyx_sc("e(boot_continuity_valid)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_draws)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_p)"), pyx_sc("e(boot_coef_B)"), pyx_sc("e(boot_coef_attempted)"), pyx_sc("e(boot_coef_failed)"), pyx_sc("e(boot_coef_twostep)"), pyx_sc("e(boot_grid_stage1)"), pyx_sc("e(boot_grid_stage2)")))
    mata: pyx_export("../out/bc_unit_fd_grid.csv", st_matrix("e(ci_grid)"))
    mata: pyx_export("../out/bc_unit_fd_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/bc_unit_fd_bootci.csv", st_matrix("e(b_bootci)"))
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
gen double qdisc = floor(debt/0.25 + 0.5)*0.25
drop if mod(firm + 3*year, 11) == 0
display "@@CASE unit_gaps"
capture noisily xtdpthresh invest cashflow, qx(debt) grid(30) boot(99) boottype(unit) rseed(20260611) gridci(40) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/bc_unit_gaps_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(ci_unresolved)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(pval_lin)"), pyx_sc("e(boot_linearity_valid)"), pyx_sc("e(rseed)"), pyx_sc("e(pval_cont)"), pyx_sc("e(boot_continuity_valid)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_draws)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_p)"), pyx_sc("e(boot_coef_B)"), pyx_sc("e(boot_coef_attempted)"), pyx_sc("e(boot_coef_failed)"), pyx_sc("e(boot_coef_twostep)"), pyx_sc("e(boot_grid_stage1)"), pyx_sc("e(boot_grid_stage2)")))
    mata: pyx_export("../out/bc_unit_gaps_grid.csv", st_matrix("e(ci_grid)"))
    mata: pyx_export("../out/bc_unit_gaps_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/bc_unit_gaps_bootci.csv", st_matrix("e(b_bootci)"))
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
gen double qdisc = floor(debt/0.25 + 0.5)*0.25
display "@@CASE unit_collapse"
capture noisily xtdpthresh invest cashflow, qx(debt) collapse grid(30) boot(99) boottype(unit) rseed(20260611) gridci(40) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/bc_unit_collapse_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(ci_unresolved)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(pval_lin)"), pyx_sc("e(boot_linearity_valid)"), pyx_sc("e(rseed)"), pyx_sc("e(pval_cont)"), pyx_sc("e(boot_continuity_valid)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_draws)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_p)"), pyx_sc("e(boot_coef_B)"), pyx_sc("e(boot_coef_attempted)"), pyx_sc("e(boot_coef_failed)"), pyx_sc("e(boot_coef_twostep)"), pyx_sc("e(boot_grid_stage1)"), pyx_sc("e(boot_grid_stage2)")))
    mata: pyx_export("../out/bc_unit_collapse_grid.csv", st_matrix("e(ci_grid)"))
    mata: pyx_export("../out/bc_unit_collapse_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/bc_unit_collapse_bootci.csv", st_matrix("e(b_bootci)"))
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
gen double qdisc = floor(debt/0.25 + 0.5)*0.25
display "@@CASE unit_nocenter"
capture noisily xtdpthresh invest cashflow, qx(debt) nocenter grid(30) boot(99) boottype(unit) rseed(20260611) gridci(40) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/bc_unit_nocenter_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(ci_unresolved)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(pval_lin)"), pyx_sc("e(boot_linearity_valid)"), pyx_sc("e(rseed)"), pyx_sc("e(pval_cont)"), pyx_sc("e(boot_continuity_valid)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_draws)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_p)"), pyx_sc("e(boot_coef_B)"), pyx_sc("e(boot_coef_attempted)"), pyx_sc("e(boot_coef_failed)"), pyx_sc("e(boot_coef_twostep)"), pyx_sc("e(boot_grid_stage1)"), pyx_sc("e(boot_grid_stage2)")))
    mata: pyx_export("../out/bc_unit_nocenter_grid.csv", st_matrix("e(ci_grid)"))
    mata: pyx_export("../out/bc_unit_nocenter_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/bc_unit_nocenter_bootci.csv", st_matrix("e(b_bootci)"))
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
gen double qdisc = floor(debt/0.25 + 0.5)*0.25
display "@@CASE unit_static"
capture noisily xtdpthresh invest cashflow L.tobin_q, qx(debt) static grid(30) boot(99) boottype(unit) rseed(20260611) gridci(40)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/bc_unit_static_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(ci_unresolved)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(pval_lin)"), pyx_sc("e(boot_linearity_valid)"), pyx_sc("e(rseed)"), pyx_sc("e(pval_cont)"), pyx_sc("e(boot_continuity_valid)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_draws)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_p)"), pyx_sc("e(boot_coef_B)"), pyx_sc("e(boot_coef_attempted)"), pyx_sc("e(boot_coef_failed)"), pyx_sc("e(boot_coef_twostep)"), pyx_sc("e(boot_grid_stage1)"), pyx_sc("e(boot_grid_stage2)")))
    mata: pyx_export("../out/bc_unit_static_grid.csv", st_matrix("e(ci_grid)"))
    mata: pyx_export("../out/bc_unit_static_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/bc_unit_static_bootci.csv", st_matrix("e(b_bootci)"))
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
gen double qdisc = floor(debt/0.25 + 0.5)*0.25
display "@@CASE unit_exog_only"
capture noisily xtdpthresh invest cashflow, qx(debt) grid(30) boot(99) boottype(unit) rseed(20260611) gridci(40)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/bc_unit_exog_only_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(ci_unresolved)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(pval_lin)"), pyx_sc("e(boot_linearity_valid)"), pyx_sc("e(rseed)"), pyx_sc("e(pval_cont)"), pyx_sc("e(boot_continuity_valid)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_draws)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_p)"), pyx_sc("e(boot_coef_B)"), pyx_sc("e(boot_coef_attempted)"), pyx_sc("e(boot_coef_failed)"), pyx_sc("e(boot_coef_twostep)"), pyx_sc("e(boot_grid_stage1)"), pyx_sc("e(boot_grid_stage2)")))
    mata: pyx_export("../out/bc_unit_exog_only_grid.csv", st_matrix("e(ci_grid)"))
    mata: pyx_export("../out/bc_unit_exog_only_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/bc_unit_exog_only_bootci.csv", st_matrix("e(b_bootci)"))
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
gen double qdisc = floor(debt/0.25 + 0.5)*0.25
display "@@CASE unit_citest"
capture noisily xtdpthresh invest cashflow, qx(debt) grid(30) boot(99) boottype(unit) rseed(20260611) gridci(40) citest(0.2) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/bc_unit_citest_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(ci_unresolved)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(pval_lin)"), pyx_sc("e(boot_linearity_valid)"), pyx_sc("e(rseed)"), pyx_sc("e(pval_cont)"), pyx_sc("e(boot_continuity_valid)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_draws)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_p)"), pyx_sc("e(boot_coef_B)"), pyx_sc("e(boot_coef_attempted)"), pyx_sc("e(boot_coef_failed)"), pyx_sc("e(boot_coef_twostep)"), pyx_sc("e(boot_grid_stage1)"), pyx_sc("e(boot_grid_stage2)")))
    mata: pyx_export("../out/bc_unit_citest_grid.csv", st_matrix("e(ci_grid)"))
    mata: pyx_export("../out/bc_unit_citest_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/bc_unit_citest_bootci.csv", st_matrix("e(b_bootci)"))
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
gen double qdisc = floor(debt/0.25 + 0.5)*0.25
display "@@CASE unit_quantile_grid"
capture noisily xtdpthresh invest cashflow, qx(debt) grid(30) gridtype(quantile) boot(99) boottype(unit) rseed(20260611) gridci(40) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/bc_unit_quantile_grid_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(ci_unresolved)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(pval_lin)"), pyx_sc("e(boot_linearity_valid)"), pyx_sc("e(rseed)"), pyx_sc("e(pval_cont)"), pyx_sc("e(boot_continuity_valid)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_draws)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_p)"), pyx_sc("e(boot_coef_B)"), pyx_sc("e(boot_coef_attempted)"), pyx_sc("e(boot_coef_failed)"), pyx_sc("e(boot_coef_twostep)"), pyx_sc("e(boot_grid_stage1)"), pyx_sc("e(boot_grid_stage2)")))
    mata: pyx_export("../out/bc_unit_quantile_grid_grid.csv", st_matrix("e(ci_grid)"))
    mata: pyx_export("../out/bc_unit_quantile_grid_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/bc_unit_quantile_grid_bootci.csv", st_matrix("e(b_bootci)"))
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
gen double qdisc = floor(debt/0.25 + 0.5)*0.25
display "@@CASE unit_kink"
capture noisily xtdpthresh invest cashflow, qx(debt) kink grid(30) boot(99) boottype(unit) rseed(20260611) gridci(40) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/bc_unit_kink_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(ci_unresolved)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(pval_lin)"), pyx_sc("e(boot_linearity_valid)"), pyx_sc("e(rseed)"), pyx_sc("e(pval_cont)"), pyx_sc("e(boot_continuity_valid)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_draws)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_p)"), pyx_sc("e(boot_coef_B)"), pyx_sc("e(boot_coef_attempted)"), pyx_sc("e(boot_coef_failed)"), pyx_sc("e(boot_coef_twostep)"), pyx_sc("e(boot_grid_stage1)"), pyx_sc("e(boot_grid_stage2)")))
    mata: pyx_export("../out/bc_unit_kink_grid.csv", st_matrix("e(ci_grid)"))
    mata: pyx_export("../out/bc_unit_kink_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/bc_unit_kink_bootci.csv", st_matrix("e(b_bootci)"))
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
gen double qdisc = floor(debt/0.25 + 0.5)*0.25
display "@@CASE unit_fod"
capture noisily xtdpthresh invest cashflow, qx(debt) method(fod) grid(30) boot(99) boottype(unit) rseed(20260611) gridci(40) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/bc_unit_fod_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(ci_unresolved)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(pval_lin)"), pyx_sc("e(boot_linearity_valid)"), pyx_sc("e(rseed)"), pyx_sc("e(pval_cont)"), pyx_sc("e(boot_continuity_valid)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_draws)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_p)"), pyx_sc("e(boot_coef_B)"), pyx_sc("e(boot_coef_attempted)"), pyx_sc("e(boot_coef_failed)"), pyx_sc("e(boot_coef_twostep)"), pyx_sc("e(boot_grid_stage1)"), pyx_sc("e(boot_grid_stage2)")))
    mata: pyx_export("../out/bc_unit_fod_grid.csv", st_matrix("e(ci_grid)"))
    mata: pyx_export("../out/bc_unit_fod_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/bc_unit_fod_bootci.csv", st_matrix("e(b_bootci)"))
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
gen double qdisc = floor(debt/0.25 + 0.5)*0.25
display "@@CASE unit_td"
capture noisily xtdpthresh invest cashflow, qx(debt) td grid(30) boot(99) boottype(unit) rseed(20260611) gridci(40) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/bc_unit_td_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(ci_unresolved)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(pval_lin)"), pyx_sc("e(boot_linearity_valid)"), pyx_sc("e(rseed)"), pyx_sc("e(pval_cont)"), pyx_sc("e(boot_continuity_valid)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_draws)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_p)"), pyx_sc("e(boot_coef_B)"), pyx_sc("e(boot_coef_attempted)"), pyx_sc("e(boot_coef_failed)"), pyx_sc("e(boot_coef_twostep)"), pyx_sc("e(boot_grid_stage1)"), pyx_sc("e(boot_grid_stage2)")))
    mata: pyx_export("../out/bc_unit_td_grid.csv", st_matrix("e(ci_grid)"))
    mata: pyx_export("../out/bc_unit_td_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/bc_unit_td_bootci.csv", st_matrix("e(b_bootci)"))
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
gen double qdisc = floor(debt/0.25 + 0.5)*0.25
drop if firm >= 11 & firm <= 40 & mod(year, 2) == 0
display "@@CASE unit_one_step"
capture noisily xtdpthresh invest cashflow, qx(debt) grid(30) boot(99) boottype(unit) rseed(20260611) gridci(40) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/bc_unit_one_step_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(ci_unresolved)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(pval_lin)"), pyx_sc("e(boot_linearity_valid)"), pyx_sc("e(rseed)"), pyx_sc("e(pval_cont)"), pyx_sc("e(boot_continuity_valid)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_draws)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_p)"), pyx_sc("e(boot_coef_B)"), pyx_sc("e(boot_coef_attempted)"), pyx_sc("e(boot_coef_failed)"), pyx_sc("e(boot_coef_twostep)"), pyx_sc("e(boot_grid_stage1)"), pyx_sc("e(boot_grid_stage2)")))
    mata: pyx_export("../out/bc_unit_one_step_grid.csv", st_matrix("e(ci_grid)"))
    mata: pyx_export("../out/bc_unit_one_step_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/bc_unit_one_step_bootci.csv", st_matrix("e(b_bootci)"))
}

use "../data/invest.dta", clear
xtset firm year
egen double peer_q = mean(tobin_q), by(year)
display "@@CASE full_help"
capture noisily xtdpthresh invest , qx(debt) collapse boot(99) rseed(20260611) gridci(40) maxlag(3 8) endogenous(cashflow tobin_q debt)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/bc_full_help_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(ci_unresolved)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(pval_lin)"), pyx_sc("e(boot_linearity_valid)"), pyx_sc("e(rseed)"), pyx_sc("e(pval_cont)"), pyx_sc("e(boot_continuity_valid)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_draws)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_p)"), pyx_sc("e(boot_coef_B)"), pyx_sc("e(boot_coef_attempted)"), pyx_sc("e(boot_coef_failed)"), pyx_sc("e(boot_coef_twostep)"), pyx_sc("e(boot_grid_stage1)"), pyx_sc("e(boot_grid_stage2)")))
    mata: pyx_export("../out/bc_full_help_grid.csv", st_matrix("e(ci_grid)"))
    mata: pyx_export("../out/bc_full_help_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/bc_full_help_bootci.csv", st_matrix("e(b_bootci)"))
}

use "../data/invest.dta", clear
xtset firm year
egen double peer_q = mean(tobin_q), by(year)
display "@@CASE full_help_kink"
capture noisily xtdpthresh invest , qx(debt) kink collapse boot(99) rseed(20260611) gridci(40) maxlag(3 8) endogenous(cashflow tobin_q debt)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/bc_full_help_kink_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(ci_unresolved)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(pval_lin)"), pyx_sc("e(boot_linearity_valid)"), pyx_sc("e(rseed)"), pyx_sc("e(pval_cont)"), pyx_sc("e(boot_continuity_valid)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_draws)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_p)"), pyx_sc("e(boot_coef_B)"), pyx_sc("e(boot_coef_attempted)"), pyx_sc("e(boot_coef_failed)"), pyx_sc("e(boot_coef_twostep)"), pyx_sc("e(boot_grid_stage1)"), pyx_sc("e(boot_grid_stage2)")))
    mata: pyx_export("../out/bc_full_help_kink_grid.csv", st_matrix("e(ci_grid)"))
    mata: pyx_export("../out/bc_full_help_kink_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/bc_full_help_kink_bootci.csv", st_matrix("e(b_bootci)"))
}

use "../data/invest.dta", clear
xtset firm year
egen double peer_q = mean(tobin_q), by(year)
display "@@CASE full_help_fod"
capture noisily xtdpthresh invest , qx(debt) collapse method(fod) boot(99) rseed(20260611) gridci(40) maxlag(3 8) endogenous(cashflow tobin_q debt)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/bc_full_help_fod_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(ci_unresolved)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(pval_lin)"), pyx_sc("e(boot_linearity_valid)"), pyx_sc("e(rseed)"), pyx_sc("e(pval_cont)"), pyx_sc("e(boot_continuity_valid)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_draws)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_p)"), pyx_sc("e(boot_coef_B)"), pyx_sc("e(boot_coef_attempted)"), pyx_sc("e(boot_coef_failed)"), pyx_sc("e(boot_coef_twostep)"), pyx_sc("e(boot_grid_stage1)"), pyx_sc("e(boot_grid_stage2)")))
    mata: pyx_export("../out/bc_full_help_fod_grid.csv", st_matrix("e(ci_grid)"))
    mata: pyx_export("../out/bc_full_help_fod_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/bc_full_help_fod_bootci.csv", st_matrix("e(b_bootci)"))
}

use "../data/invest.dta", clear
xtset firm year
egen double peer_q = mean(tobin_q), by(year)
display "@@CASE full_cont"
capture noisily xtdpthresh invest , qx(debt) collapse conttest boot(99) rseed(20260611) gridci(40) maxlag(3 8) endogenous(cashflow tobin_q debt)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/bc_full_cont_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(ci_unresolved)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(pval_lin)"), pyx_sc("e(boot_linearity_valid)"), pyx_sc("e(rseed)"), pyx_sc("e(pval_cont)"), pyx_sc("e(boot_continuity_valid)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_draws)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_p)"), pyx_sc("e(boot_coef_B)"), pyx_sc("e(boot_coef_attempted)"), pyx_sc("e(boot_coef_failed)"), pyx_sc("e(boot_coef_twostep)"), pyx_sc("e(boot_grid_stage1)"), pyx_sc("e(boot_grid_stage2)")))
    mata: pyx_export("../out/bc_full_cont_grid.csv", st_matrix("e(ci_grid)"))
    mata: pyx_export("../out/bc_full_cont_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/bc_full_cont_bootci.csv", st_matrix("e(b_bootci)"))
}

use "../data/invest.dta", clear
xtset firm year
egen double peer_q = mean(tobin_q), by(year)
display "@@CASE full_citest"
capture noisily xtdpthresh invest , qx(debt) collapse boot(99) rseed(20260611) gridci(40) citest(0.25) maxlag(3 8) endogenous(cashflow tobin_q debt)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/bc_full_citest_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(ci_unresolved)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(pval_lin)"), pyx_sc("e(boot_linearity_valid)"), pyx_sc("e(rseed)"), pyx_sc("e(pval_cont)"), pyx_sc("e(boot_continuity_valid)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_draws)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_p)"), pyx_sc("e(boot_coef_B)"), pyx_sc("e(boot_coef_attempted)"), pyx_sc("e(boot_coef_failed)"), pyx_sc("e(boot_coef_twostep)"), pyx_sc("e(boot_grid_stage1)"), pyx_sc("e(boot_grid_stage2)")))
    mata: pyx_export("../out/bc_full_citest_grid.csv", st_matrix("e(ci_grid)"))
    mata: pyx_export("../out/bc_full_citest_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/bc_full_citest_bootci.csv", st_matrix("e(b_bootci)"))
}

exit, clear
