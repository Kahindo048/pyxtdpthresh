version 17
set more off
clear all
file open fh using "C:/Users/Fred-derick/Desktop/Dynamic threshold/pyxtdpthresh/validation/stata/perf_unit.csv", write text replace
file write fh "kind,rep,seconds" _n
foreach kind in wild unit {
    forvalues r = 1/3 {
        use "../data/invest.dta", clear
        keep if firm <= 150
        xtset firm year
        timer clear 1
        timer on 1
        quietly xtdpthresh invest cashflow, qx(tobin_q) collapse boottype(`kind') boot(99) gridci(40) rseed(1)
        timer off 1
        quietly timer list 1
        file write fh "`kind',`r',`=r(t1)'" _n
    }
}
file close fh
exit, clear
