# -*- coding: utf-8 -*-
"""
swflow.swe - 2D depth-averaged shallow-water solver for wind-driven lake circulation.

Grid (Arakawa C, free surface at centers):
  eta (ny, nx)    at cell centers
  u   (ny, nx+1)  at x-faces; face index i separates cells i-1 (west) and i (east)
  v   (ny+1, nx)  at y-faces; face index j separates cells j-1 (south) and j (north)
Boundary faces (i=0,nx ; j=0,ny) are land -> flux = 0 (closed basin default).

Equations (depth-integrated, wind-driven, Coriolis, Manning bottom friction,
constant eddy viscosity, centered advection):
  d eta/dt + d(Hu)/dx + d(Hv)/dy = 0
  du/dt = -g d eta/dx + f v - adv_u + tau_wx/(rho H) - g n^2 |u| u / H^(4/3) + nu lap(u)
  dv/dt = -g d eta/dy - f u - adv_v + tau_wy/(rho H) - g n^2 |v| v / H^(4/3) + nu lap(v)
Integration: explicit Heun (RK2); bottom friction semi-implicit.
"""
import numpy as np

G = 9.81
RHO_AIR = 1.225
RHO_W = 1000.0

class SweConfig:
    def __init__(self, dx=50.0, lat=30.5566, dt=2.0, n_manning=0.022,
                 c_d_wind=1.3e-3, nu=0.5, h_dry=0.15, use_adv=True, use_coriolis=True):
        self.dx = dx; self.lat = lat; self.dt = dt
        self.n = n_manning; self.c_d_wind = c_d_wind
        self.nu = nu; self.h_dry = h_dry
        self.use_adv = use_adv; self.use_coriolis = use_coriolis
        self.f = 2.0 * 7.2921e-5 * np.sin(np.radians(lat))

class ShallowWaterSolver:
    def __init__(self, mask, depth, cfg):
        self.mask = mask; self.depth = depth; self.cfg = cfg
        ny, nx = mask.shape
        self.ny = ny; self.nx = nx
        self.cell_wet = mask & (depth >= cfg.h_dry)
        self.uf_wet = np.zeros((ny, nx+1), bool)
        self.uf_wet[:, 1:nx] = self.cell_wet[:, :-1] & self.cell_wet[:, 1:]
        self.vf_wet = np.zeros((ny+1, nx), bool)
        self.vf_wet[1:ny, :] = self.cell_wet[:-1, :] & self.cell_wet[1:, :]

    def init_state(self):
        return {'eta': np.zeros((self.ny, self.nx), float),
                'u': np.zeros((self.ny, self.nx+1), float),
                'v': np.zeros((self.ny+1, self.nx), float)}

    # ---------- force / geometry helpers ----------
    def face_depths(self, eta):
        H = np.where(self.mask, self.depth + eta, 0.0)
        Hx = np.zeros((self.ny, self.nx+1)); Hx[:, 1:self.nx] = 0.5*(H[:, :-1] + H[:, 1:])
        Hy = np.zeros((self.ny+1, self.nx)); Hy[1:self.ny, :] = 0.5*(H[:-1, :] + H[1:, :])
        Hx = np.where(self.uf_wet, np.maximum(Hx, 0.02), 0.0)
        Hy = np.where(self.vf_wet, np.maximum(Hy, 0.02), 0.0)
        return Hx, Hy

    def v_at_uface(self, v):
        """v interpolated to u-faces (j, i): 4-pt avg of v at y-faces (j,i-1),(j,i),(j+1,i-1),(j+1,i)"""
        return 0.25*(v[0:self.ny, 0:self.nx-1] + v[0:self.ny, 1:self.nx]
                     + v[1:self.ny+1, 0:self.nx-1] + v[1:self.ny+1, 1:self.nx])

    def u_at_vface(self, u):
        """u interpolated to v-faces (j, i): 4-pt avg of u at x-faces (j-1,i),(j-1,i+1),(j,i),(j,i+1)"""
        return 0.25*(u[0:self.ny-1, 0:self.nx] + u[0:self.ny-1, 1:self.nx+1]
                     + u[1:self.ny, 0:self.nx] + u[1:self.ny, 1:self.nx+1])

    def rhs(self, st, tau_x, tau_y):
        cfg = self.cfg; dx = cfg.dx; nu = cfg.nu
        eta = st['eta']; u = st['u']; v = st['v']
        ny, nx = eta.shape
        uf_wet = self.uf_wet; vf_wet = self.vf_wet
        Hx, Hy = self.face_depths(eta)
        # ---- mass conservation ----
        Fx = Hx * u
        Fy = Hy * v
        deta = -((Fx[:, 1:] - Fx[:, :-1]) / dx + (Fy[1:, :] - Fy[:-1, :]) / dx)
        # ---- u momentum ----
        du = np.zeros_like(u)
        pgrad = (eta[:, 1:] - eta[:, :-1]) / dx          # (ny, nx-1) at faces 1..nx-1
        du[:, 1:nx] = -G * pgrad
        if cfg.use_coriolis:
            du[:, 1:nx] += cfg.f * self.v_at_uface(v)     # (ny, nx-1)
        Hxs = np.where(uf_wet, np.maximum(Hx, 0.05), 1.0)
        du += tau_x / (RHO_W * Hxs)
        if cfg.use_adv:
            uc = 0.5*(u[:, :-1] + u[:, 1:])                # (ny, nx)
            dudx = np.zeros_like(u)
            dudx[:, 1:nx] = (uc[:, 1:] - uc[:, :-1]) / dx  # (ny, nx-1)
            dudy = np.zeros_like(u)
            if ny > 2:
                dudy[1:-1, 1:-1] = (u[2:, 1:-1] - u[:-2, 1:-1]) / (2*dx)
            vfac = np.zeros((ny, nx+1))
            vfac[:, 1:nx] = self.v_at_uface(v)             # (ny, nx-1)
            du[1:-1, 1:nx] -= u[1:-1, 1:nx]*dudx[1:-1, 1:nx] + vfac[1:-1, 1:nx]*dudy[1:-1, 1:nx]
        lap = np.zeros_like(u)
        lap[:, 1:nx] += (u[:, 2:] - 2*u[:, 1:nx] + u[:, :-2]) / dx**2
        if ny > 2:
            lap[1:-1, 1:nx] += (u[2:, 1:nx] - 2*u[1:-1, 1:nx] + u[:-2, 1:nx]) / dx**2
        du += nu * lap
        du = np.where(uf_wet, du, 0.0)
        # ---- v momentum ----
        dv = np.zeros_like(v)
        pgrady = (eta[1:, :] - eta[:-1, :]) / dx          # (ny-1, nx) at faces 1..ny-1
        dv[1:ny, :] = -G * pgrady
        if cfg.use_coriolis:
            dv[1:ny, :] -= cfg.f * self.u_at_vface(u)     # (ny-1, nx)
        Hys = np.where(vf_wet, np.maximum(Hy, 0.05), 1.0)
        dv += tau_y / (RHO_W * Hys)
        if cfg.use_adv:
            vc = 0.5*(v[:-1, :] + v[1:, :])                # (ny, nx)
            dvdy = np.zeros_like(v)
            dvdy[1:ny, :] = (vc[1:, :] - vc[:-1, :]) / dx  # (ny-1, nx)
            dvdx = np.zeros_like(v)
            if nx > 2:
                dvdx[1:-1, 1:-1] = (v[1:-1, 2:] - v[1:-1, :-2]) / (2*dx)
            ufac = np.zeros((ny+1, nx))
            ufac[1:ny, :] = self.u_at_vface(u)             # (ny-1, nx)
            dv[1:-1, :] -= ufac[1:-1, :]*dvdx[1:-1, :] + v[1:-1, :]*dvdy[1:-1, :]
        lv = np.zeros_like(v)
        lv[1:ny, :] += (v[2:, :] - 2*v[1:ny, :] + v[:-2, :]) / dx**2
        if nx > 2:
            lv[1:ny, 1:-1] += (v[1:ny, 2:] - 2*v[1:ny, 1:-1] + v[1:ny, :-2]) / dx**2
        dv += nu * lv
        dv = np.where(vf_wet, dv, 0.0)
        return deta, du, dv

    def friction(self, st):
        cfg = self.cfg; dx = cfg.dx
        H = np.where(self.mask, self.depth + st['eta'], 0.0)
        Hx = np.zeros_like(st['u']); Hx[:, 1:self.nx] = 0.5*(H[:, :-1] + H[:, 1:])
        Hy = np.zeros_like(st['v']); Hy[1:self.ny, :] = 0.5*(H[:-1, :] + H[1:, :])
        Hx = np.where(self.uf_wet, np.maximum(Hx, 0.05), 1e9)
        Hy = np.where(self.vf_wet, np.maximum(Hy, 0.05), 1e9)
        cd = cfg.n ** 2 * G
        c1 = 1.0 + cfg.dt * cd * np.abs(st['u']) / Hx ** (4.0/3.0)
        c2 = 1.0 + cfg.dt * cd * np.abs(st['v']) / Hy ** (4.0/3.0)
        st['u'] = st['u'] / c1
        st['v'] = st['v'] / c2

    def step(self, st, tau_x, tau_y):
        dt = self.cfg.dt
        eta0 = st['eta'].copy(); u0 = st['u'].copy(); v0 = st['v'].copy()
        d0 = self.rhs(st, tau_x, tau_y)
        st['eta'] = eta0 + dt*d0[0]; st['u'] = u0 + dt*d0[1]; st['v'] = v0 + dt*d0[2]
        self.friction(st)
        d1 = self.rhs(st, tau_x, tau_y)
        st['eta'] = eta0 + 0.5*dt*(d0[0] + d1[0])
        st['u'] = u0 + 0.5*dt*(d0[1] + d1[1])
        st['v'] = v0 + 0.5*dt*(d0[2] + d1[2])
        self.friction(st)

    def volume(self, st):
        H = np.where(self.mask, self.depth + st['eta'], 0.0)
        return float((H*self.mask).sum()) * self.cfg.dx**2


def wind_stress(wind_mps, direction_deg, cd=1.3e-3):
    """Meteorological direction: the direction the wind comes FROM (deg, 0=N, 90=E).
    Returns (tau_x, tau_y) wind stress [N/m^2] (positive towards +x/+y)."""
    theta = np.radians(direction_deg)
    ux = -np.sin(theta)
    uy = -np.cos(theta)
    tau = RHO_AIR * cd * wind_mps ** 2
    return tau * ux, tau * uy
