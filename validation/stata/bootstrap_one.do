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
display "@@CASE unit_nocenter"
capture noisily xtdpthresh invest cashflow, qx(debt) collapse nocenter grid(30) boot(99) boottype(unit) rseed(20260611) gridci(40) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/bc_unit_nocenter_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(gamma_lo)"), pyx_sc("e(gamma_hi)"), pyx_sc("e(ci_empty)"), pyx_sc("e(ci_nseg)"), pyx_sc("e(ci_incomplete)"), pyx_sc("e(ci_unresolved)"), pyx_sc("e(boundary_warn)"), pyx_sc("e(pval_lin)"), pyx_sc("e(boot_linearity_valid)"), pyx_sc("e(rseed)"), pyx_sc("e(pval_cont)"), pyx_sc("e(boot_continuity_valid)"), pyx_sc("e(citest_gamma)"), pyx_sc("e(citest_D)"), pyx_sc("e(citest_crit)"), pyx_sc("e(citest_accept)"), pyx_sc("e(citest_draws)"), pyx_sc("e(citest_status)"), pyx_sc("e(citest_p)"), pyx_sc("e(boot_coef_B)"), pyx_sc("e(boot_coef_attempted)"), pyx_sc("e(boot_coef_failed)"), pyx_sc("e(boot_coef_twostep)"), pyx_sc("e(boot_grid_stage1)"), pyx_sc("e(boot_grid_stage2)")))
    mata: pyx_export("../out/bc_unit_nocenter_grid.csv", st_matrix("e(ci_grid)"))
    mata: pyx_export("../out/bc_unit_nocenter_segments.csv", st_matrix("e(ci_segments)"))
    mata: pyx_export("../out/bc_unit_nocenter_bootci.csv", st_matrix("e(b_bootci)"))
}

exit, clear
