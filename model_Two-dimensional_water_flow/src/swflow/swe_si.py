# -*- coding: utf-8 -*-
"""
swflow.swe_si - Semi-implicit 2D shallow-water solver (Casulli-type free-surface scheme).

Stable for arbitrarily large dt w.r.t. gravity waves; recommended dt~10-60 s at dx=50 m.
Same C-grid conventions as swflow.swe.

Physical options aligned with the Donghu MIKE21 baseline (Li, Huang & Wang 2020,
doi:10.3390/ijgi9020094):
  - bottom friction: Manning, default n = 1/42 ~ 0.0238 (their calibrated M = 42)
  - horizontal viscosity: constant nu OR Smagorinsky (nu_mode='smag', Cs ~0.28-0.32)
  - Coriolis on, advection optional
  - wind stress: tau = rho_a * Cd(U) * |U| * U  (Cd constant or speed-dependent 'wu')
  - source/sink (inflow/outflow gates) via add_source()

Scheme per step:
  eta^{n+1} = eta^n - dt [ d(H^n u^{n+1})/dx + d(H^n v^{n+1})/dy ] + dt*sources
  u^{n+1}   = u^n + dt [ -g d eta^{n+1}/dx + f v^n + tau_wx/(rho H) - friction + visc ]
Substitute -> SPD elliptic system for eta^{n+1} on wet cells, solved with CG.
"""
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla

G = 9.81
RHO_AIR = 1.225
RHO_W = 1000.0

class SweConfigSI:
    def __init__(self, dx=50.0, lat=30.5566, dt=20.0, n_manning=0.0238,
                 c_d_wind=1.3e-3, nu=0.5, h_dry=0.15, use_adv=True, use_coriolis=True,
                 nu_mode="const", cs=0.29, cg_rtol=1e-8, cg_maxiter=200, cd_mode="lake"):
        # note: production scripts (02/09/10/14) pass nu_mode='smag' explicitly
        # (Smagorinsky cs~0.29, per MIKE21 Donghu calibration); 'const' kept as the
        # class default so analytic/regression tests are unaffected.
        self.dx = dx; self.lat = lat; self.dt = dt
        self.n = n_manning; self.c_d_wind = c_d_wind
        self.nu = nu; self.h_dry = h_dry
        self.use_adv = use_adv; self.use_coriolis = use_coriolis
        self.nu_mode = nu_mode; self.cs = cs
        self.cg_rtol = cg_rtol; self.cg_maxiter = cg_maxiter
        self.f = 2.0 * 7.2921e-5 * np.sin(np.radians(lat))
        # cd_mode: 'lake' (Zhang et al. 2024 Fig.4b fit, production default), 'constant',
        # 'wu' (Wu 1980). wind_stress() resolves the actual Cd.
        self.cd_mode = cd_mode

class ShallowWaterSolverSI:
    def __init__(self, mask, depth, cfg):
        self.mask = mask; self.depth = depth; self.cfg = cfg
        ny, nx = mask.shape
        self.ny = ny; self.nx = nx
        self.cell_wet = mask & (depth >= cfg.h_dry)
        self.idx = -np.ones((ny, nx), np.int32)
        w = np.argwhere(self.cell_wet)
        self.idx[w[:, 0], w[:, 1]] = np.arange(len(w))
        self.N = len(w)
        self.uf_wet = np.zeros((ny, nx+1), bool)
        self.uf_wet[:, 1:nx] = self.cell_wet[:, :-1] & self.cell_wet[:, 1:]
        self.vf_wet = np.zeros((ny+1, nx), bool)
        self.vf_wet[1:ny, :] = self.cell_wet[:-1, :] & self.cell_wet[1:, :]
        # source/sink cells: dict (j,i) -> flow [m3/s]  (positive = inflow)
        self.sources = {}

    def add_source(self, j, i, q):
        self.sources[(int(j), int(i))] = float(q)

    def init_state(self):
        return {"eta": np.zeros((self.ny, self.nx), float),
                "u": np.zeros((self.ny, self.nx+1), float),
                "v": np.zeros((self.ny+1, self.nx), float)}

    def face_depths(self, eta):
        H = self.depth + eta
        H = np.where(self.mask, np.maximum(H, 1e-4), 0.0)   # defensive floor
        Hx = np.zeros((self.ny, self.nx+1)); Hx[:, 1:self.nx] = 0.5*(H[:, :-1] + H[:, 1:])
        Hy = np.zeros((self.ny+1, self.nx)); Hy[1:self.ny, :] = 0.5*(H[:-1, :] + H[1:, :])
        Hx = np.where(self.uf_wet, np.maximum(Hx, 1e-4), 0.0)
        Hy = np.where(self.vf_wet, np.maximum(Hy, 1e-4), 0.0)
        return H, Hx, Hy

    def v_at_uface(self, v):
        return 0.25*(v[0:self.ny, 0:self.nx-1] + v[0:self.ny, 1:self.nx]
                     + v[1:self.ny+1, 0:self.nx-1] + v[1:self.ny+1, 1:self.nx])

    def u_at_vface(self, u):
        return 0.25*(u[0:self.ny-1, 0:self.nx] + u[0:self.ny-1, 1:self.nx+1]
                     + u[1:self.ny, 0:self.nx] + u[1:self.ny, 1:self.nx+1])

    def _nu_field(self, st):
        """cell-centered eddy viscosity: constant or Smagorinsky cs^2 dx^2 |S|"""
        cfg = self.cfg
        if cfg.nu_mode == "const":
            return np.full((self.ny, self.nx), float(cfg.nu))
        dx = cfg.dx
        uc = 0.5*(st["u"][:, :-1] + st["u"][:, 1:])
        vc = 0.5*(st["v"][:-1, :] + st["v"][1:, :])
        Sxx = np.zeros((self.ny, self.nx)); Syy = np.zeros((self.ny, self.nx))
        Sxy = np.zeros((self.ny, self.nx))
        if self.nx > 2:
            Sxx[:, 1:-1] = (uc[:, 2:] - uc[:, :-2])/(2*dx)
            Syy[1:-1, :] = (vc[2:, :] - vc[:-2, :])/(2*dx)
        if self.ny > 2 and self.nx > 2:
            Sxy[1:-1, 1:-1] = 0.5*((uc[2:, 1:-1]-uc[:-2, 1:-1])/(2*dx) + (vc[1:-1, 2:]-vc[1:-1, :-2])/(2*dx))
        strain = np.sqrt(2.0*(Sxx**2 + Syy**2) + 4.0*Sxy**2)
        nu = cfg.cs**2 * dx**2 * np.where(self.mask, strain, 0.0)
        return np.where(self.mask, nu + 1e-6, 0.0)

    def _explicit_u(self, st, tau_x, tau_y, H, Hx, Hy):
        cfg = self.cfg; dx = cfg.dx; dt = cfg.dt
        u = st["u"]; v = st["v"]
        nu_c = self._nu_field(st)
        du = np.zeros_like(u)
        if cfg.use_coriolis:
            du[:, 1:self.nx] += cfg.f * self.v_at_uface(v)
        Hxs = np.where(self.uf_wet, np.maximum(Hx, 1e-3), 1.0)
        du += tau_x / (RHO_W * Hxs)
        if cfg.use_adv:
            uc = 0.5*(u[:, :-1] + u[:, 1:])
            dudx = np.zeros_like(u); dudx[:, 1:self.nx] = (uc[:, 1:] - uc[:, :-1]) / dx
            dudy = np.zeros_like(u)
            if self.ny > 2:
                dudy[1:-1, 1:self.nx] = (u[2:, 1:self.nx] - u[:-2, 1:self.nx]) / (2*dx)
            vfac = np.zeros((self.ny, self.nx+1)); vfac[:, 1:self.nx] = self.v_at_uface(v)
            du[1:-1, 1:self.nx] -= u[1:-1, 1:self.nx]*dudx[1:-1, 1:self.nx] + vfac[1:-1, 1:self.nx]*dudy[1:-1, 1:self.nx]
        nux = np.zeros((self.ny, self.nx+1)); nux[:, 1:self.nx] = 0.5*(nu_c[:, :-1] + nu_c[:, 1:])
        lapx = np.zeros_like(u); lapx[:, 1:self.nx] = (u[:, 2:] - 2*u[:, 1:self.nx] + u[:, :-2]) / dx**2
        lapy = np.zeros_like(u)
        if self.ny > 2:
            lapy[1:-1, 1:self.nx] = (u[2:, 1:self.nx] - 2*u[1:-1, 1:self.nx] + u[:-2, 1:self.nx]) / dx**2
            nuy = np.zeros((self.ny, self.nx+1)); nuy[1:-1, 1:self.nx] = 0.25*(nu_c[:-2, :-1] + nu_c[:-2, 1:] + nu_c[2:, :-1] + nu_c[2:, 1:])
            du += nux*lapx + nuy*lapy
        else:
            du += nux*lapx
        du = np.where(self.uf_wet, du, 0.0)
        return u + dt*du

    def _explicit_v(self, st, tau_x, tau_y, H, Hx, Hy):
        cfg = self.cfg; dx = cfg.dx; dt = cfg.dt
        u = st["u"]; v = st["v"]
        nu_c = self._nu_field(st)
        dv = np.zeros_like(v)
        if cfg.use_coriolis:
            dv[1:self.ny, :] -= cfg.f * self.u_at_vface(u)
        Hys = np.where(self.vf_wet, np.maximum(Hy, 1e-3), 1.0)
        dv += tau_y / (RHO_W * Hys)
        if cfg.use_adv:
            vc = 0.5*(v[:-1, :] + v[1:, :])
            dvdy = np.zeros_like(v); dvdy[1:self.ny, :] = (vc[1:, :] - vc[:-1, :]) / dx
            dvdx = np.zeros_like(v)
            if self.nx > 2:
                dvdx[1:-1, 1:-1] = (v[1:-1, 2:] - v[1:-1, :-2]) / (2*dx)
            ufac = np.zeros((self.ny+1, self.nx)); ufac[1:self.ny, :] = self.u_at_vface(u)
            dv[1:-1, :] -= ufac[1:-1, :]*dvdx[1:-1, :] + v[1:-1, :]*dvdy[1:-1, :]
        nuy = np.zeros((self.ny+1, self.nx)); nuy[1:self.ny, :] = 0.5*(nu_c[:-1, :] + nu_c[1:, :])
        lvy = np.zeros_like(v); lvy[1:self.ny, :] = (v[2:, :] - 2*v[1:self.ny, :] + v[:-2, :]) / dx**2
        lvx = np.zeros_like(v)
        if self.nx > 2:
            lvx[1:self.ny, 1:-1] = (v[1:self.ny, 2:] - 2*v[1:self.ny, 1:-1] + v[1:self.ny, :-2]) / dx**2
            nux = np.zeros((self.ny+1, self.nx)); nux[1:self.ny, 1:-1] = 0.25*(nu_c[:-1, :-2] + nu_c[:-1, 2:] + nu_c[1:, :-2] + nu_c[1:, 2:])
            dv += nuy*lvy + nux*lvx
        else:
            dv += nuy*lvy
        dv = np.where(self.vf_wet, dv, 0.0)
        return v + dt*dv

    def _assemble_system(self, H, Hx, Hy, dt):
        ny, nx = self.ny, self.nx
        dx = self.cfg.dx
        idm = self.idx
        N = self.N
        alpha = (dt**2)*G/(dx*dx)
        jj, ii = np.where(self.cell_wet)
        idx = idm[jj, ii]
        He = Hx[jj, np.minimum(ii+1, nx)]
        Hw = Hx[jj, ii]
        Hn = Hy[np.minimum(jj+1, ny), ii]
        Hs = Hy[jj, ii]
        ie_id = np.full(N, -1); iw_id = np.full(N, -1)
        in_id = np.full(N, -1); is_id = np.full(N, -1)
        ok_e = (ii+1 < nx); ok_w = (ii-1 >= 0); ok_n = (jj+1 < ny); ok_s = (jj-1 >= 0)
        ie_id[ok_e] = idm[jj[ok_e], (ii[ok_e]+1)]
        iw_id[ok_w] = idm[jj[ok_w], (ii[ok_w]-1)]
        in_id[ok_n] = idm[(jj[ok_n]+1), ii[ok_n]]
        is_id[ok_s] = idm[(jj[ok_s]-1), ii[ok_s]]
        ae = np.where(ie_id >= 0, alpha*He, 0.0)
        aw = np.where(iw_id >= 0, alpha*Hw, 0.0)
        an = np.where(in_id >= 0, alpha*Hn, 0.0)
        as_ = np.where(is_id >= 0, alpha*Hs, 0.0)
        diag = 1.0 + ae + aw + an + as_
        R = [idx, idx[ie_id>=0], idx[iw_id>=0], idx[in_id>=0], idx[is_id>=0]]
        C = [np.arange(N), ie_id[ie_id>=0], iw_id[iw_id>=0], in_id[in_id>=0], is_id[is_id>=0]]
        V = [diag, -ae[ie_id>=0], -aw[iw_id>=0], -an[in_id>=0], -as_[is_id>=0]]
        r = np.concatenate(R); c = np.concatenate(C); v = np.concatenate(V)
        return sp.csr_matrix((v, (r, c)), shape=(N, N))

    def step(self, st, tau_x, tau_y):
        cfg = self.cfg; dx = cfg.dx; dt = cfg.dt
        H, Hx, Hy = self.face_depths(st["eta"])
        ustar = self._explicit_u(st, tau_x, tau_y, H, Hx, Hy)
        vstar = self._explicit_v(st, tau_x, tau_y, H, Hx, Hy)
        Fx = Hx*ustar
        Fy = Hy*vstar
        rhs = st["eta"] - dt*((Fx[:, 1:] - Fx[:, :-1])/dx + (Fy[1:, :] - Fy[:-1, :])/dx)
        if self.sources:
            src = np.zeros((self.ny, self.nx))
            for (j, i), q in self.sources.items():
                if self.cell_wet[j, i]:
                    src[j, i] = q/(dx*dx)
            rhs = rhs + dt*src
        A = self._assemble_system(H, Hx, Hy, dt)
        b = rhs[self.cell_wet]
        x, info = spla.cg(A, b, rtol=cfg.cg_rtol, maxiter=cfg.cg_maxiter)
        if info != 0:
            print("WARN cg not converged info=", info)
        eta_new = rhs.copy()
        eta_new[self.cell_wet] = x
        u = ustar.copy()
        u[:, 1:self.nx] -= dt*G*((eta_new[:, 1:] - eta_new[:, :-1])/dx)
        v = vstar.copy()
        v[1:self.ny, :] -= dt*G*((eta_new[1:, :] - eta_new[:-1, :])/dx)
        u = np.where(self.uf_wet, u, 0.0)
        v = np.where(self.vf_wet, v, 0.0)
        cd = cfg.n**2 * G
        Hx_p = np.where(self.uf_wet, np.maximum(Hx, 0.02), 1e9)
        Hy_p = np.where(self.vf_wet, np.maximum(Hy, 0.02), 1e9)
        u = u / (1.0 + dt*cd*np.abs(st["u"])/Hx_p**(4.0/3.0))
        v = v / (1.0 + dt*cd*np.abs(st["v"])/Hy_p**(4.0/3.0))
        st["eta"] = eta_new; st["u"] = u; st["v"] = v

    def volume(self, st):
        H = np.where(self.mask, np.maximum(self.depth + st["eta"], 0.0), 0.0)
        return float((H*self.mask).sum()) * self.cfg.dx**2


def cd_lake(U):
    """Lake wind drag coefficient for light-moderate winds (U in m/s).
    Fit through the Zhang, Chen & Brett (2024, WRR 60:e2023WR035914) Fig.4b positive
    branch (1.6 < U10 <= 3.0, r^2 = 0.901): Cd = 1.32e-3 + 1.27e-3*(U-1.6), clipped to
    their measured band [1.2e-3, 3.6e-3]. Note: Eq. 11 itself requires a wave field and
    collapses under equilibrium SMB waves (see report/实验记录 E1); this curve is the
    parameterization actually adopted for production."""
    return float(np.clip(1.32e-3 + 1.27e-3*(max(float(U), 0.0) - 1.6), 1.2e-3, 3.6e-3))

def wind_stress(wind_mps, direction_deg, cd=1.3e-3, cd_mode="constant"):
    """Meteorological direction: the direction the wind comes FROM (deg, 0=N, 90=E).
    cd_mode: 'constant' -> fixed cd; 'wu' -> Wu (1980): Cd = (0.8 + 0.065*U)*1e-3;
             'lake' -> cd_lake(U) (production default via SweConfigSI.cd_mode).
    Returns (tau_x, tau_y, cd_used) wind stress [N/m^2] (positive towards +x/+y)."""
    W = max(float(wind_mps), 0.0)
    if cd_mode == "wu":
        cd = (0.8 + 0.065*W)*1e-3
    elif cd_mode == "lake":
        cd = cd_lake(W)
    theta = np.radians(direction_deg)
    ux = -np.sin(theta)
    uy = -np.cos(theta)
    tau = RHO_AIR * cd * W ** 2
    return tau * ux, tau * uy, cd
