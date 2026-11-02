version 17
set more off
mata:
real scalar kept(real scalar s, real scalar t)
{
    real matrix A, B
    real scalar r
    r = 0.6
    A = s * (1, r \ r, r*r + t)
    B = invsym(A)
    return(B[2,2] != 0)
}
for (sc = -6; sc <= 6; sc = sc + 6) {
    printf("scale 1e%g\n", sc)
    for (k = 8.0; k <= 10.01; k = k + 0.125) printf("  t=10^-%g kept=%g\n", k, kept(10^sc, 10^(-k)))
}
end
