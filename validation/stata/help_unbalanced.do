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
set seed 20260418
drop if runiform() < 0.15
bysort firm: drop if _N < 4
export delimited firm year invest tobin_q cashflow debt using "../out/hu_sample.csv", replace
display "@@CASE fd"
capture noisily xtdpthresh invest, qx(debt) endogenous(cashflow tobin_q debt) maxlag(3 8) collapse noboot method(fd)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/hu_fd_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(N)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_units)"), pyx_sc("e(grid_effective)"), pyx_sc("e(gamma_stage1)")))
    mata: pyx_export("../out/hu_fd_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/hu_fd_vc.csv", st_matrix("e(V_cond)"))
}
display "@@CASE fod"
capture noisily xtdpthresh invest, qx(debt) endogenous(cashflow tobin_q debt) maxlag(3 8) collapse noboot method(fod)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/hu_fod_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(grid_admitted)"), pyx_sc("e(N)"), pyx_sc("e(N_iv)"), pyx_sc("e(N_units)"), pyx_sc("e(grid_effective)"), pyx_sc("e(gamma_stage1)")))
    mata: pyx_export("../out/hu_fod_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/hu_fod_vc.csv", st_matrix("e(V_cond)"))
}
exit, clear
