"""Port of Stata's ``xthenreg`` (Seo, Kim and Kim 2019, Stata Journal 19(3)).

Dynamic panel threshold regression with endogeneity, first-differenced GMM
(Seo and Shin 2016).  The port reproduces the Mata code of ``xthenreg.ado``
step by step (grid, instruments, first- and second-step weights, covariance,
sup-Wald linearity test), but computes the criterion on the whole threshold
grid from *sufficient statistics*:

* only the regime columns of the moment matrix ``g2`` depend on the threshold;
* they are sums over units of ``Z[:, i] * F[i] * 1(q[i] > gamma)``, which
  ``engine="fast"`` evaluates for every grid point with one sort and one
  cumulative sum per period (``engine="reference"`` recomputes them point by
  point, as the Stata code does, and is used to prove equivalence).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Sequence

import numpy as np
import pandas as pd
from scipy.stats import norm

from ._linalg import cholinv, invsym, invsym_batch
from .grid import mm_quantile, rangen

Z_975 = 1.959963984540054  # constant used by xthenreg.ado


# --------------------------------------------------------------------------
# data preparation
# --------------------------------------------------------------------------
@dataclass
class _Design:
    N: int
    T: int
    y: np.ndarray          # (N, T)
    q: np.ndarray          # (N, T)
    XL: np.ndarray         # (N, T, k1) level regressors; block 0 = (1, y_1..y_{T-1})
    IV: Optional[np.ndarray]  # (N, T, k_inst) or None
    n_plain: int
    n_endo: int
    n_exo: int
    static: bool
    kink: bool
    names: list = field(default_factory=list)   # names of x variables (without lag y)

    @property
    def k1(self) -> int:
        return self.XL.shape[2]

    @property
    def keff(self) -> int:
        """Number of regressors entering the criterion (drops lag y if static)."""
        return self.k1 - 1 if self.static else self.k1

    @property
    def periods(self):
        return range(1, self.T) if self.static else range(2, self.T)


def _prepare(data: pd.DataFrame, id: str, time: str, y: str, q: str,
             x: Sequence[str], endogenous: Sequence[str], exogenous: Sequence[str],
             inst: Sequence[str], static: bool, kink: bool,
             where: Optional[np.ndarray] = None) -> _Design:
    x, endogenous, exogenous, inst = list(x), list(endogenous), list(exogenous), list(inst)
    df = data.sort_values([id, time]).reset_index(drop=True)
    # xtset check performed by Stata: the whole dataset must be strongly balanced
    cnt = df.groupby(id)[time].nunique()
    times_all = df[time].unique()
    if df.duplicated([id, time]).any() or not (cnt == len(times_all)).all():
        raise ValueError("The given data are not strongly balanced (xthenreg requirement).")
    touse = np.ones(len(df), dtype=bool) if where is None else np.asarray(where, dtype=bool)
    varlist = [y, q] + x
    touse &= ~df[varlist].isna().any(axis=1).to_numpy()
    d = df[touse]
    extra = endogenous + exogenous + inst
    if extra and d[extra].isna().any().any():
        raise ValueError("Missing values in endogenous(), exogenous() or inst() variables.")
    times = np.sort(d[time].unique())
    T = len(times)
    counts = d.groupby(id)[time].transform("size").to_numpy()
    d = d[counts == T]                       # units observed in every period
    N = d[id].nunique()
    if N == 0:
        raise ValueError("No unit is observed in every period.")
    allx = x + endogenous + exogenous
    Y = d[y].to_numpy(float).reshape(N, T)
    Q = d[q].to_numpy(float).reshape(N, T)
    k1 = 1 + len(allx)
    XL = np.empty((N, T, k1))
    XL[:, 0, 0] = 1.0
    XL[:, 1:, 0] = Y[:, :-1]
    for j, v in enumerate(allx, start=1):
        XL[:, :, j] = d[v].to_numpy(float).reshape(N, T)
    IV = None
    if inst:
        IV = np.stack([d[v].to_numpy(float).reshape(N, T) for v in inst], axis=2)
    return _Design(N=N, T=T, y=Y, q=Q, XL=XL, IV=IV, n_plain=len(x),
                   n_endo=len(endogenous), n_exo=len(exogenous),
                   static=static, kink=kink, names=allx)


# --------------------------------------------------------------------------
# instruments and weights
# --------------------------------------------------------------------------
def _build_Z(ds: _Design) -> list:
    """Instrument blocks ``Z_t`` of shape (m_t, N), one per equation period."""
    N, T, XL, Y = ds.N, ds.T, ds.XL, ds.y
    n_plain, n_endo = ds.n_plain, ds.n_endo
    plain = range(1, 1 + n_plain)
    endo = range(1 + n_plain, 1 + n_plain + n_endo)
    exo = range(1 + n_plain + n_endo, ds.k1)
    blocks = []
    for t in ds.periods:
        rows = [np.ones((1, N))]
        if not ds.static:
            rows.append(Y[:, : t - 1].T)                       # y_1 .. y_{t-2}
        for v in plain:
            rows.append((XL[:, t, v] - XL[:, t - 1, v])[None, :])   # Delta x_t
        for v in endo:
            if t - 1 > 0:
                rows.append(XL[:, : t - 1, v].T)               # x_1 .. x_{t-2}
        for v in exo:
            rows.append(XL[:, : t + 1, v].T)                   # x_1 .. x_t
        if ds.IV is not None:
            rows.append(ds.IV[:, t, :].T)
        blocks.append(np.vstack(rows))
    return blocks


def _weight_first(Zb: list, N: int) -> np.ndarray:
    """First-step weight ``(2*W2 - W1 - W1')^{-1}`` (GMM_W_n_con / _static)."""
    sizes = [z.shape[0] for z in Zb]
    L = sum(sizes)
    off = np.concatenate([[0], np.cumsum(sizes)])
    M = np.zeros((L, L))
    for b, Zt in enumerate(Zb):
        sl = slice(off[b], off[b + 1])
        M[sl, sl] += 2.0 * (Zt @ Zt.T) / N
        if b > 0:
            Zp = Zb[b - 1]
            C = (Zp @ Zt.T) / N
            M[off[b - 1]:off[b], sl] -= C
            M[sl, off[b - 1]:off[b]] -= C.T
    return invsym(M)


def _omega_weight(Zfull: np.ndarray, E_rep: np.ndarray, N: int) -> np.ndarray:
    """GMM_W_n_2_con: inverse of the centred moment covariance."""
    GZ = Zfull * E_rep
    s = GZ.sum(axis=1)
    om = GZ @ GZ.T / N - np.outer(s, s) / N ** 2
    return invsym(om)


# --------------------------------------------------------------------------
# moments
# --------------------------------------------------------------------------
class _Moments:
    """Everything the criterion needs, built once per estimation."""

    def __init__(self, ds: _Design, engine: str = "fast"):
        self.ds = ds
        self.engine = engine
        self.N = ds.N
        self.Zb = _build_Z(ds)
        self.sizes = [z.shape[0] for z in self.Zb]
        self.L = int(sum(self.sizes))
        self.off = np.concatenate([[0], np.cumsum(self.sizes)])
        self.Z = np.vstack(self.Zb)
        N = ds.N
        k0 = 1 if ds.static else 0           # first x block used in the criterion
        self.k0 = k0
        per = list(ds.periods)
        self.per = per
        self.dY = [ds.y[:, t] - ds.y[:, t - 1] for t in per]
        self.Xt = [ds.XL[:, t, k0:] for t in per]
        self.Xp = [ds.XL[:, t - 1, k0:] for t in per]
        self.dX = [a - b for a, b in zip(self.Xt, self.Xp)]
        self.Qt = [ds.q[:, t] for t in per]
        self.Qp = [ds.q[:, t - 1] for t in per]
        self.g1 = np.concatenate([Zt @ dy for Zt, dy in zip(self.Zb, self.dY)]) / N
        self.D = np.vstack([Zt @ dx for Zt, dx in zip(self.Zb, self.dX)]) / N   # (L, keff)
        self.keff = self.Xt[0].shape[1]
        self.W1 = _weight_first(self.Zb, N)

    # -- regime columns of g2 for a vector of thresholds -------------------
    def _A(self, Zt, F, Qs, grid):
        """sum_i Z[:, i] F[i, :] 1(Qs[i] > grid[g]) for every g -> (G, m, nf)."""
        G = len(grid)
        m, N = Zt.shape
        nf = F.shape[1]
        if self.engine == "reference":
            out = np.empty((G, m, nf))
            for g in range(G):
                r = (Qs > grid[g]).astype(float)
                out[g] = Zt @ (F * r[:, None])
            return out
        b = np.searchsorted(grid, Qs, side="left")
        order = np.argsort(b, kind="stable")
        bs = b[order]
        Zs = Zt[:, order]
        Fs = F[order]
        outer = (Zs.T[:, :, None] * Fs[:, None, :])
        cum = np.zeros((N + 1, m, nf))
        np.cumsum(outer, axis=0, out=cum[1:])
        cnt = np.searchsorted(bs, np.arange(G), side="right")
        return cum[-1][None] - cum[cnt]

    def regime_g2(self, grid: np.ndarray) -> np.ndarray:
        """g2(gamma) for every grid point, shape (G, L, p)."""
        ds = self.ds
        G = len(grid)
        keff = self.keff
        N = self.N
        if ds.kink:
            p = keff + 1
        else:
            p = 2 * keff + 1
        out = np.empty((G, self.L, p))
        out[:, :, :keff] = self.D[None]
        for b, t in enumerate(self.per):
            Zt = self.Zb[b]
            sl = slice(self.off[b], self.off[b + 1])
            if ds.kink:
                Ft = np.column_stack([np.ones(N), self.Qt[b]])
                Fp = np.column_stack([np.ones(N), self.Qp[b]])
                At = self._A(Zt, Ft, self.Qt[b], grid)
                Ap = self._A(Zt, Fp, self.Qp[b], grid)
                kt = At[:, :, 1] - grid[:, None] * At[:, :, 0]
                kp = Ap[:, :, 1] - grid[:, None] * Ap[:, :, 0]
                out[:, sl, keff] = (kt - kp) / N
            else:
                Ft = np.column_stack([np.ones(N), self.Xt[b]])
                Fp = np.column_stack([np.ones(N), self.Xp[b]])
                At = self._A(Zt, Ft, self.Qt[b], grid)
                Ap = self._A(Zt, Fp, self.Qp[b], grid)
                diff = (At - Ap) / N
                out[:, sl, keff] = diff[:, :, 0]
                out[:, sl, keff + 1:] = diff[:, :, 1:]
        return out

    def g2_at(self, gamma: float) -> np.ndarray:
        return self.regime_g2(np.array([gamma], dtype=float))[0]

    # -- criterion on a grid ------------------------------------------------
    def solve_grid(self, grid: np.ndarray, W: np.ndarray, g1: Optional[np.ndarray] = None):
        """GMM estimate and criterion at every grid point for weight ``W``."""
        g1 = self.g1 if g1 is None else g1
        g2 = self.regime_g2(grid)
        return self._solve(g2, W, g1)

    @staticmethod
    def _solve(g2, W, g1):
        Wg2 = np.einsum("lm,gmp->glp", W, g2, optimize=True)
        A = np.einsum("glp,glq->gpq", g2, Wg2, optimize=True)
        bvec = np.einsum("glp,l->gp", Wg2, g1, optimize=True)
        Ainv = invsym_batch(A)
        theta = np.einsum("gpq,gq->gp", Ainv, bvec)
        gbar = g1[None] - np.einsum("glp,gp->gl", g2, theta, optimize=True)
        J = np.einsum("gl,lm,gm->g", gbar, W, gbar, optimize=True)
        return theta, J, g2, Ainv

    def residuals(self, theta: np.ndarray, gamma: float) -> list:
        """Per-period residuals e_t (N,) at (theta, gamma)."""
        ds = self.ds
        keff = self.keff
        res = []
        for b in range(len(self.per)):
            if ds.kink:
                kt = np.where(self.Qt[b] > gamma, self.Qt[b] - gamma, 0.0)
                kp = np.where(self.Qp[b] > gamma, self.Qp[b] - gamma, 0.0)
                fit = self.dX[b] @ theta[:keff] + theta[keff] * (kt - kp)
            else:
                rt = (self.Qt[b] > gamma).astype(float)
                rp = (self.Qp[b] > gamma).astype(float)
                fit = (self.dX[b] @ theta[:keff] + theta[keff] * (rt - rp)
                       + (self.Xt[b] * rt[:, None] - self.Xp[b] * rp[:, None]) @ theta[keff + 1:])
            res.append(self.dY[b] - fit)
        return res

    def e_rep(self, res: list) -> np.ndarray:
        return np.vstack([np.repeat(e[None, :], m, axis=0) for e, m in zip(res, self.sizes)])


# --------------------------------------------------------------------------
# covariance
# --------------------------------------------------------------------------
def _cov(mo: _Moments, theta2, r2, omega_hat, h_0, qall_sd, full: bool = True):
    """Covariance matrix (cov_mat_con / cov_mat_con_kink)."""
    ds = mo.ds
    N, keff = mo.N, mo.keff
    h = h_0 * 1.06 * N ** (-0.2) * qall_sd
    g2 = mo.g2_at(r2)
    if ds.kink:
        Gb = -g2[:, :keff]
        Gd = g2[:, keff:keff + 1]
        d0 = theta2[keff]
        Gr = np.empty((mo.L, 1))
        for b in range(len(mo.per)):
            sl = slice(mo.off[b], mo.off[b + 1])
            ind = (mo.Qt[b] > r2).astype(float) - (mo.Qp[b] > r2).astype(float)
            Gr[sl, 0] = -d0 * (mo.Zb[b] @ ind) / N
        G = np.hstack([Gb, Gd, Gr])
        return cholinv(G.T @ omega_hat @ G) / N
    Gb = -g2[:, :keff]
    Gd = -g2[:, keff:]
    delta = theta2[keff:]
    Gr = np.empty((mo.L, 1))
    for b in range(len(mo.per)):
        sl = slice(mo.off[b], mo.off[b + 1])
        phi_p = norm.pdf((r2 - mo.Qp[b]) / h)
        phi_t = norm.pdf((r2 - mo.Qt[b]) / h)
        fp = delta[0] + mo.Xp[b] @ delta[1:]
        ft = delta[0] + mo.Xt[b] @ delta[1:]
        s = phi_p * fp - phi_t * ft
        Gr[sl, 0] = (mo.Zb[b] @ s) / (N * h)
    G = np.hstack([Gb, Gd, Gr])
    return cholinv(G.T @ omega_hat @ G) / N


# --------------------------------------------------------------------------
# result container
# --------------------------------------------------------------------------
@dataclass
class XthenregResult:
    b: np.ndarray
    V: np.ndarray
    CI: np.ndarray
    names: list
    N: int
    T: int
    L: int
    boots_p: float
    grid: np.ndarray
    J1: np.ndarray
    J2: np.ndarray
    r1: float
    depvar: str
    qvar: str
    options: dict

    @property
    def se(self) -> np.ndarray:
        return np.sqrt(np.diag(self.V))

    @property
    def threshold(self) -> float:
        return float(self.b[-1])

    def to_dataframe(self) -> pd.DataFrame:
        z = self.b / self.se
        from scipy.stats import norm as _n
        p = 2 * (1 - _n.cdf(np.abs(z)))
        return pd.DataFrame({"coef": self.b, "se": self.se, "z": z, "p": p,
                             "ci_lo": self.CI[:, 0], "ci_hi": self.CI[:, 1]},
                            index=self.names)

    def summary(self) -> str:
        df = self.to_dataframe()
        head = (f"xthenreg (Seo-Kim-Kim) | depvar: {self.depvar} | threshold var: {self.qvar}\n"
                f"N = {self.N}, T = {self.T}, moment conditions = {self.L}\n")
        if self.boots_p >= 0:
            head += f"Bootstrap p-value for linearity test = {self.boots_p:.4f}\n"
        return head + df.to_string(float_format=lambda v: f"{v:11.6f}")

    def __repr__(self):
        return self.summary()


# --------------------------------------------------------------------------
# main entry point
# --------------------------------------------------------------------------
def xthenreg(data: pd.DataFrame, id: str, time: str, y: str, q: str,
             x: Sequence[str] = (), endogenous: Sequence[str] = (),
             exogenous: Sequence[str] = (), inst: Sequence[str] = (),
             kink: bool = False, static: bool = False, grid_num: int = 100,
             trim_rate: float = 0.4, h_0: float = 1.5, boost: int = 0,
             seed: Optional[int] = None, weights: Optional[np.ndarray] = None,
             where: Optional[np.ndarray] = None, engine: str = "fast") -> XthenregResult:
    """Dynamic (or static) panel threshold regression with endogeneity.

    Mirrors ``xthenreg y q x, endogenous() exogenous() inst() kink static
    grid_num() trim_rate() h_0() boost()``.  ``weights`` (B, N) lets the caller
    inject the standard-normal bootstrap draws (used to compare with Stata).
    """
    ds = _prepare(data, id, time, y, q, x, endogenous, exogenous, inst, static, kink, where)
    mo = _Moments(ds, engine=engine)
    N, T = ds.N, ds.T

    # grid: rangen between the trim/2 and 1 - trim/2 quantiles of all q values
    qvec = ds.q.reshape(-1)
    lo = mm_quantile(qvec, trim_rate / 2)
    hi = mm_quantile(qvec, 1 - trim_rate / 2)
    grid = rangen(lo, hi, grid_num)

    # ---- first step
    theta1, J1, _, _ = mo.solve_grid(grid, mo.W1)
    i1 = int(np.argmin(J1))
    r1 = float(grid[i1])
    th1 = theta1[i1]

    # ---- second step
    res1 = mo.residuals(th1, r1)
    W2 = _omega_weight(mo.Z, mo.e_rep(res1), N)
    theta2, J2, _, _ = mo.solve_grid(grid, W2)
    i2 = int(np.argmin(J2))
    r2 = float(grid[i2])
    th2 = theta2[i2]

    res2 = mo.residuals(th2, r2)
    omega_hat = _omega_weight(mo.Z, mo.e_rep(res2), N)
    sd_q = float(np.std(qvec, ddof=1))
    V = _cov(mo, th2, r2, omega_hat, h_0, sd_q)

    est = np.concatenate([th2, [r2]])
    sds = np.sqrt(np.diag(V))
    CI = np.column_stack([est - Z_975 * sds, est + Z_975 * sds])

    # ---- bootstrap linearity test (optional)
    boots_p = -1.0
    if boost and boost > 0:
        boots_p = _sup_wald_bootstrap(mo, grid, W2, res2, boost, seed, weights)

    # ---- labels
    vars_ = ds.names
    if static:
        if kink:
            names = [f"{v}_b" for v in vars_] + ["kink_slope", "r"]
        else:
            names = [f"{v}_b" for v in vars_] + ["cons_d"] + [f"{v}_d" for v in vars_] + ["r"]
    else:
        if kink:
            names = ["Lag_y_b"] + [f"{v}_b" for v in vars_] + ["kink_slope", "r"]
        else:
            names = (["Lag_y_b"] + [f"{v}_b" for v in vars_] + ["cons_d", "Lag_y_d"]
                     + [f"{v}_d" for v in vars_] + ["r"])
    opts = dict(kink=kink, static=static, grid_num=grid_num, trim_rate=trim_rate,
                h_0=h_0, boost=boost, engine=engine)
    return XthenregResult(b=est, V=V, CI=CI, names=names, N=N, T=T, L=mo.L,
                          boots_p=boots_p, grid=grid, J1=J1, J2=J2, r1=r1,
                          depvar=y, qvar=q, options=opts)


# --------------------------------------------------------------------------
# sup-Wald linearity test (fast bootstrap of Seo and Shin 2016)
# --------------------------------------------------------------------------
def _dlt_len(mo: _Moments) -> int:
    ds = mo.ds
    k_full = ds.k1                      # k_1 of the Mata code (includes the lag-y block)
    if ds.kink:
        return 2                        # as in xthenreg.ado (includes the last slope)
    return k_full if ds.static else k_full + 1


def _sup_wald_bootstrap(mo: _Moments, grid, W2, res2, B, seed, weights):
    ds = mo.ds
    N, L = mo.N, mo.L
    dl = _dlt_len(mo)
    G = len(grid)
    keff = mo.keff

    # ---- original-sample sup-Wald: two-step GMM at every fixed grid point
    g2 = mo.regime_g2(grid)
    th1, _, _, _ = mo._solve(g2, mo.W1, mo.g1)
    wald = np.empty(G)
    cov_rec = []
    for g in range(G):
        r = float(grid[g])
        e1 = mo.residuals(th1[g], r)
        Wb = _omega_weight(mo.Z, mo.e_rep(e1), N)
        Wg2 = Wb @ g2[g]
        A = g2[g].T @ Wg2
        Ainv = invsym(A)
        th2 = Ainv @ (Wg2.T @ mo.g1)
        e2 = mo.residuals(th2, r)
        om = _omega_weight(mo.Z, mo.e_rep(e2), N)
        # V_s = chol(om)' (G_b, G_d)  -> V_s'V_s = G' om G
        g2r = g2[g]
        Gb = -g2r[:, :keff]
        if ds.kink:
            Gd = g2r[:, keff:keff + 1]
        else:
            Gd = -g2r[:, keff:]
        Gm = np.hstack([Gb, Gd])
        S = Gm.T @ om @ Gm
        size_c = S.shape[0]
        Sinv = cholinv(S)
        sel = slice(size_c - dl, size_c)
        cov_w = Sinv[sel, sel]
        dlt = th2[size_c - dl:size_c]
        wald[g] = N * dlt @ cholinv(cov_w) @ dlt
        cov_rec.append(cov_w)
    sup_ori = float(np.max(wald))

    # ---- bootstrap draws
    if weights is not None:
        eta = np.asarray(weights, dtype=float)
        if eta.shape != (B, N):
            raise ValueError(f"weights must have shape ({B}, {N}), got {eta.shape}")
    else:
        rng = np.random.default_rng(seed)
        eta = rng.standard_normal((B, N))

    E_rep = mo.e_rep(res2)
    Gunit = mo.Z * E_rep                         # (L, N): g_i = Z[:, i] * e_rep[:, i]
    G1 = eta @ Gunit.T / N                       # (B, L)
    # theta_{g,b} = Ainv_g g2_g' W2 g1_b ; only the last dl entries matter
    Wg2 = np.einsum("lm,gmp->glp", W2, g2, optimize=True)
    A = np.einsum("glp,glq->gpq", g2, Wg2, optimize=True)
    Ainv = invsym_batch(A)
    M = np.einsum("gpq,glq->gpl", Ainv, Wg2, optimize=True)      # (G, p, L)
    p = M.shape[1]
    theta_b = np.einsum("gpl,bl->gbp", M, G1, optimize=True)     # (G, B, p)
    dlt_b = theta_b[:, :, p - dl:]
    cov_inv = np.stack([cholinv(c) for c in cov_rec])            # (G, dl, dl)
    wald_b = N * np.einsum("gbi,gij,gbj->gb", dlt_b, cov_inv, dlt_b, optimize=True)
    sup_b = wald_b.max(axis=0)
    return float(np.sum(sup_b > sup_ori) / B)
