version 17
set more off
clear all

mata:
void pyx_export(string scalar fname, real matrix M)
{
    real scalar fh, i, j
    string scalar line
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
real scalar xdpt2_quantile(real colvector x, real scalar p)
{
    real colvector xs
    real scalar n, h, j, g

    xs = select(x, x :< .)
    n = rows(xs)
    if (n == 0) return(.)
    xs = sort(xs, 1)
    if (p <= 0) return(xs[1])
    if (p >= 1) return(xs[n])

    h = 1 + (n - 1) * p
    j = floor(h)
    g = h - j
    if (j >= n) return(xs[n])
    return((1 - g) * xs[j] + g * xs[j + 1])
}

real colvector xdpt2_quantile_grid(real colvector qv, real scalar p_lo,
                                    real scalar p_hi, real scalar n)
{
    real colvector g
    real scalar i
    if (n <= 1) return(J(1, 1, xdpt2_quantile(qv, p_lo)))
    g = J(n, 1, .)
    for (i = 1; i <= n; i++) {
        g[i] = xdpt2_quantile(qv, p_lo + (p_hi - p_lo) * (i - 1) / (n - 1))
    }
    return(uniqrows(g))
}

real colvector xdpt2_rangen(real scalar a, real scalar b, real scalar n)
{
    real scalar i
    real colvector out
    if (n <= 1) return(J(1, 1, a))
    out = J(n, 1, .)
    for (i = 1; i <= n; i++) {
        out[i] = a + (b - a) * (i - 1) / (n - 1)
    }
    // v0.9.34: the last point is b exactly (a + (b - a) could round below b)
    out[n] = b
    return(out)
}

end

mata:
void run_case(string scalar tag, real colvector q, real colvector p)
{
    real scalar k, lo, hi, mdef, mapp
    real colvector t7, g, adm
    t7 = J(rows(p), 1, .)
    for (k = 1; k <= rows(p); k++) t7[k] = xdpt2_quantile(q, p[k])
    pyx_export("../out/" + tag + "_mm.csv", mm_quantile(q, 1, p))
    pyx_export("../out/" + tag + "_t7.csv", t7)
    lo = xdpt2_quantile(q, 0.2 / 2)
    hi = xdpt2_quantile(q, 1 - 0.2 / 2)
    pyx_export("../out/" + tag + "_rangen.csv", rangen(lo, hi, 100))
    pyx_export("../out/" + tag + "_rangen_x.csv", xdpt2_rangen(lo, hi, 100))
    pyx_export("../out/" + tag + "_rangen1.csv", rangen(lo, hi, 1))
    pyx_export("../out/" + tag + "_qgrid.csv",
               xdpt2_quantile_grid(q, 0.2 / 2, 1 - 0.2 / 2, 30))
    pyx_export("../out/" + tag + "_qgrid1.csv",
               xdpt2_quantile_grid(q, 0.2 / 2, 1 - 0.2 / 2, 1))
    mdef = min((sum(q :<= lo), sum(q :> hi)))
    if (mdef < 2) mdef = 2
    mapp = (30 > mdef ? 30 : mdef)
    pyx_export("../out/" + tag + "_minreg.csv", (mdef \ mapp))
    g = xdpt2_rangen(lo, hi, 100)
    adm = J(rows(g), 1, .)
    for (k = 1; k <= rows(g); k++) {
        adm[k] = (sum(q :<= g[k]) >= mapp) & (sum(q :> g[k]) >= mapp)
    }
    pyx_export("../out/" + tag + "_adm.csv", adm)
}
end

mata:
i = (1::500); q = mod(i*7, 10); p = (-0.10000000000000001 \ 0 \ 0.002 \ 0.0040000000000000001 \ 0.0050000000000000001 \ 0.014 \ 0.025000000000000001 \ 0.050000000000000003 \ 0.10000000000000001 \ 0.123456 \ 0.14999999999999999 \ 0.20000000000000001 \ 0.22500000000000001 \ 0.25 \ 0.33200000000000002 \ 0.5 \ 0.75 \ 0.77500000000000002 \ 0.80000000000000004 \ 0.84999999999999998 \ 0.90000000000000002 \ 0.94999999999999996 \ 0.97499999999999998 \ 0.995 \ 0.998 \ 0.999 \ 1 \ 1.2)
run_case("gr_ties10", q, p)
i = (1::4520); q = mod(i*7919, 10007)/100; p = (-0.10000000000000001 \ 0 \ 0.00022123893805309734 \ 0.00044247787610619468 \ 0.0015486725663716814 \ 0.0050000000000000001 \ 0.025000000000000001 \ 0.050000000000000003 \ 0.10000000000000001 \ 0.123456 \ 0.14999999999999999 \ 0.20000000000000001 \ 0.22500000000000001 \ 0.25 \ 0.33318584070796459 \ 0.5 \ 0.75 \ 0.77500000000000002 \ 0.80000000000000004 \ 0.84999999999999998 \ 0.90000000000000002 \ 0.94999999999999996 \ 0.97499999999999998 \ 0.995 \ 0.999 \ 0.99977876106194685 \ 1 \ 1.2)
run_case("gr_uni4520", q, p)
i = (1::25); q = mod(i*37, 101)/10; p = (-0.10000000000000001 \ 0 \ 0.0050000000000000001 \ 0.025000000000000001 \ 0.040000000000000001 \ 0.050000000000000003 \ 0.080000000000000002 \ 0.10000000000000001 \ 0.123456 \ 0.14999999999999999 \ 0.20000000000000001 \ 0.22500000000000001 \ 0.25 \ 0.28000000000000003 \ 0.32000000000000001 \ 0.47999999999999998 \ 0.5 \ 0.75 \ 0.77500000000000002 \ 0.80000000000000004 \ 0.84999999999999998 \ 0.90000000000000002 \ 0.94999999999999996 \ 0.95999999999999996 \ 0.97499999999999998 \ 0.995 \ 0.999 \ 1 \ 1.2)
run_case("gr_small25", q, p)
i = (1::300); q = mod(i*104729, 1009)/13; p = (-0.10000000000000001 \ 0 \ 0.0033333333333333335 \ 0.0050000000000000001 \ 0.0066666666666666671 \ 0.023333333333333334 \ 0.025000000000000001 \ 0.050000000000000003 \ 0.10000000000000001 \ 0.123456 \ 0.14999999999999999 \ 0.20000000000000001 \ 0.22500000000000001 \ 0.25 \ 0.33333333333333331 \ 0.5 \ 0.75 \ 0.77500000000000002 \ 0.80000000000000004 \ 0.84999999999999998 \ 0.90000000000000002 \ 0.94999999999999996 \ 0.97499999999999998 \ 0.995 \ 0.9966666666666667 \ 0.999 \ 1 \ 1.2)
run_case("gr_n300", q, p)
i = (1::1000); q = (mod(i*7919, 10007)/10007):*(mod(i*7919, 10007)/10007)*50; p = (-0.10000000000000001 \ 0 \ 0.001 \ 0.002 \ 0.0050000000000000001 \ 0.0070000000000000001 \ 0.025000000000000001 \ 0.050000000000000003 \ 0.10000000000000001 \ 0.123456 \ 0.14999999999999999 \ 0.20000000000000001 \ 0.22500000000000001 \ 0.25 \ 0.33300000000000002 \ 0.5 \ 0.75 \ 0.77500000000000002 \ 0.80000000000000004 \ 0.84999999999999998 \ 0.90000000000000002 \ 0.94999999999999996 \ 0.97499999999999998 \ 0.995 \ 0.999 \ 1 \ 1.2)
run_case("gr_skew1000", q, p)
end
exit, clear
