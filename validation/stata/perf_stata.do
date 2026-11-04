version 17
set more off
clear all
file open fh using "C:/Users/Fred-derick/Desktop/Dynamic threshold/pyxtdpthresh/validation/stata/perf_stata.csv", write text replace
file write fh "size,bootstrap,rep,seconds" _n
forvalues r = 1/5 {
    use "../data/invest.dta", clear
    xtset firm year
    timer clear 1
    timer on 1
    quietly xtdpthresh invest cashflow, qx(tobin_q) noboot
    timer off 1
    quietly timer list 1
    file write fh "hansen,0,`r',`=r(t1)'" _n
}
forvalues r = 1/5 {
    use "../data/invest.dta", clear
    xtset firm year
    timer clear 1
    timer on 1
    quietly xtdpthresh invest cashflow, qx(tobin_q) boot(299) gridci(100) rseed(20260611)
    timer off 1
    quietly timer list 1
    file write fh "hansen,1,`r',`=r(t1)'" _n
}
forvalues r = 1/5 {
    use "../data/perf_2000.dta", clear
    xtset id t
    timer clear 1
    timer on 1
    quietly xtdpthresh y , qx(q) noboot
    timer off 1
    quietly timer list 1
    file write fh "2000,0,`r',`=r(t1)'" _n
}
forvalues r = 1/5 {
    use "../data/perf_2000.dta", clear
    xtset id t
    timer clear 1
    timer on 1
    quietly xtdpthresh y , qx(q) boot(299) gridci(100) rseed(20260611)
    timer off 1
    quietly timer list 1
    file write fh "2000,1,`r',`=r(t1)'" _n
}
forvalues r = 1/3 {
    use "../data/perf_10000.dta", clear
    xtset id t
    timer clear 1
    timer on 1
    quietly xtdpthresh y , qx(q) noboot
    timer off 1
    quietly timer list 1
    file write fh "10000,0,`r',`=r(t1)'" _n
}
forvalues r = 1/3 {
    use "../data/perf_10000.dta", clear
    xtset id t
    timer clear 1
    timer on 1
    quietly xtdpthresh y , qx(q) boot(299) gridci(100) rseed(20260611)
    timer off 1
    quietly timer list 1
    file write fh "10000,1,`r',`=r(t1)'" _n
}
file close fh
exit, clear
