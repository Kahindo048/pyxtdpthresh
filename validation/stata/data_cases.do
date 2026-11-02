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

foreach sc in full weak unbal {
    use "../data/invest.dta", clear
    quietly summarize year
    local y0 = r(min)
    if "`sc'" == "weak" drop if year == `y0' + mod(firm, 15)
    if "`sc'" == "unbal" drop if mod(firm + 3*year, 11) == 0
    replace cashflow = . if mod(firm + year, 13) == 0
    xtset firm year
    sort firm year
    local code = 3
    if "`r(balanced)'" == "strongly balanced" local code = 1
    if "`r(balanced)'" == "weakly balanced" local code = 2
    generate double l1 = L.invest
    generate double l2 = L2.invest
    generate double cmp = !missing(invest, cashflow, tobin_q)
    mata: pyx_export("../out/dp_`sc'_balance.csv", `code')
    mata: pyx_export("../out/dp_`sc'_rows.csv", st_data(., ("firm", "year", "l1", "l2", "cmp")))
}
exit, clear
