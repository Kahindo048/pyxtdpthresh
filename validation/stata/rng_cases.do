version 17
set more off
clear all

mata:
void pyx_export17(string scalar fname, real matrix M)
{
    real scalar fh, i, j
    string scalar line
    if (fileexists(fname)) unlink(fname)
    fh = fopen(fname, "w")
    for (i = 1; i <= rows(M); i++) {
        line = strtrim(strofreal(M[i,1], "%25.17g"))
        for (j = 2; j <= cols(M); j++) line = line + "," + strtrim(strofreal(M[i,j], "%25.17g"))
        fput(fh, line)
    }
    fclose(fh)
}

void dump(real scalar seed, real scalar n)
{
    string scalar tag
    real matrix u, u2
    tag = "../out/rn_s" + strofreal(seed, "%12.0f")
    stata("set seed " + strofreal(seed, "%12.0f"))
    pyx_export17(tag + "_uniform.csv", uniform(n, 1))
    stata("set seed " + strofreal(seed, "%12.0f"))
    pyx_export17(tag + "_normal.csv", invnormal(uniform(n, 1)))
    // matrix fill order: 3 x 4, then 5 more draws to show the stream continues
    stata("set seed " + strofreal(seed, "%12.0f"))
    u = uniform(3, 4)
    pyx_export17(tag + "_matrix.csv", u)
    pyx_export17(tag + "_after.csv", uniform(5, 1))
    // a row vector, as in invnormal(uniform(1, N)) of xthenreg
    stata("set seed " + strofreal(seed, "%12.0f"))
    pyx_export17(tag + "_row.csv", uniform(1, 7))
    // runiform() and uniform() share one stream
    stata("set seed " + strofreal(seed, "%12.0f"))
    pyx_export17(tag + "_runiform.csv", runiform(6, 1))
    // two successive normal blocks, as in a bootstrap loop
    stata("set seed " + strofreal(seed, "%12.0f"))
    pyx_export17(tag + "_boot1.csv", invnormal(uniform(1, 50)))
    pyx_export17(tag + "_boot2.csv", invnormal(uniform(1, 50)))
}
end

mata:
dump(0, 2000)
dump(1, 2000)
dump(123, 2000)
dump(12345, 2000)
dump(2147483647, 2000)
end
exit, clear
