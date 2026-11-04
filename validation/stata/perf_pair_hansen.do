version 17
set more off
clear all
use "../data/invest.dta", clear
xtset firm year
timer clear 1
timer on 1
quietly xtdpthresh invest cashflow, qx(tobin_q) boot(299) gridci(100) rseed(20260611)
timer off 1
quietly timer list 1
file open fh using "C:/Users/Fred-derick/Desktop/Dynamic threshold/pyxtdpthresh/validation/stata/perf_pairs.csv", write text append
file write fh "stata,hansen,`=r(t1)'" _n
file close fh
exit, clear
