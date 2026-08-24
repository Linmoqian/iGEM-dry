# -*- coding: utf-8 -*-
"""
swflow.particles - Lagrangian particle tracking in a 2D flow field.
- bilinear interpolation of cell-centered (u,v)
- RK4 advection + random walk (eddy diffusion)
- land handling: iterative backtracking (reflection-like), kill fallback
"""
import numpy as np

class ParticleTracer:
    def __init__(self, uc, vc, mask, xs, ys, dx=None, rng=None, wind_vec=None, w_a=0.0):
        self.uc = uc; self.vc = vc; self.mask = mask
        self.xs = xs; self.ys = ys
        self.dx = float(dx) if dx is not None else float(xs[1]-xs[0])
        self.rng = rng or np.random.default_rng(7)
        # surface wind drift (windage): adds w_a * wind_vec [m/s] on top of the
        # depth-averaged current, because the 2D field underestimates the surface layer
        # (Fenocchi et al. 2016; Wang et al. 2017). w_a ~ 0.02 (2%) recommended, based
        # on report/实验记录 E3 (area insensitive, position highly sensitive).
        self.wind_vec = None if wind_vec is None else np.asarray(wind_vec, float)
        self.w_a = float(w_a)
        self._has_wind = self.wind_vec is not None and self.w_a > 0.0

    def _cell_index(self, x, y):
        i = np.floor((x - self.xs[0]) / self.dx).astype(int)
        j = np.floor((y - self.ys[0]) / self.dx).astype(int)
        return i, j

    def in_water(self, x, y):
        i, j = self._cell_index(x, y)
        ny, nx = self.mask.shape
        inside = (i >= 0) & (i < nx) & (j >= 0) & (j < ny)
        ii = np.clip(i, 0, nx-1); jj = np.clip(j, 0, ny-1)
        return inside & self.mask[jj, ii]

    def _interp(self, field, x, y):
        i = (x - self.xs[0]) / self.dx - 0.5
        j = (y - self.ys[0]) / self.dx - 0.5
        i0 = np.floor(i).astype(int); j0 = np.floor(j).astype(int)
        fx = i - i0; fy = j - j0
        ny, nx = field.shape
        ok = (i0 >= 0) & (i0 < nx-1) & (j0 >= 0) & (j0 < ny-1)
        i0c = np.clip(i0, 0, nx-2); j0c = np.clip(j0, 0, ny-2)
        f00 = field[j0c, i0c]; f10 = field[j0c, i0c+1]
        f01 = field[j0c+1, i0c]; f11 = field[j0c+1, i0c+1]
        fxi = np.where(ok, fx, 0.0); fyj = np.where(ok, fy, 0.0)
        val = f00*(1-fxi)*(1-fyj) + f10*fxi*(1-fyj) + f01*(1-fxi)*fyj + f11*fxi*fyj
        return np.where(ok, val, 0.0)

    def _flow(self, x, y):
        return self._interp(self.uc, x, y), self._interp(self.vc, x, y)

    def advect(self, pos, D=0.0, dt=1.0):
        """one RK4 substep with random walk (+ optional windage split symmetric); pos (n,2)"""
        x, y = pos[:, 0].copy(), pos[:, 1].copy()
        if self._has_wind:
            half = 0.5 * self.w_a * self.wind_vec * dt
            x = x + half[0]; y = y + half[1]
        k1x, k1y = self._flow(x, y)
        k2x, k2y = self._flow(x + 0.5*dt*k1x, y + 0.5*dt*k1y)
        k3x, k3y = self._flow(x + 0.5*dt*k2x, y + 0.5*dt*k2y)
        k4x, k4y = self._flow(x + dt*k3x, y + dt*k3y)
        xn = x + dt*(k1x + 2*k2x + 2*k3x + k4x)/6.0
        yn = y + dt*(k1y + 2*k2y + 2*k3y + k4y)/6.0
        if self._has_wind:
            xn = xn + half[0]; yn = yn + half[1]
        if D > 0:
            s = np.sqrt(2*D*dt)
            xn = xn + s*self.rng.standard_normal(x.shape)
            yn = yn + s*self.rng.standard_normal(x.shape)
        # land handling: iteratively backtrack along the displacement
        x0 = x.copy(); y0 = y.copy()
        ok = self.in_water(xn, yn)
        niter = 0
        while (~ok).any() and niter < 10:
            bad = ~ok
            scale = 0.5
            xn[bad] = x0[bad] + scale*(xn[bad]-x0[bad])
            yn[bad] = y0[bad] + scale*(yn[bad]-y0[bad])
            ok = self.in_water(xn, yn)
            niter += 1
        # kill what still fails
        still_bad = ~self.in_water(xn, yn)
        if still_bad.any():
            xn[still_bad] = x0[still_bad]
            yn[still_bad] = y0[still_bad]
        return np.column_stack([xn, yn])

    def run(self, pos0, T, dt=5.0, D=0.3, record=False, rec_every=1):
        pos = np.asarray(pos0, float).copy()
        nsteps = int(round(T/dt))
        traj = [pos.copy()] if record else None
        for k in range(nsteps):
            pos = self.advect(pos, D=D, dt=dt)
            if record and k % max(1, rec_every) == 0:
                traj.append(pos.copy())
        return pos, (traj if record else None)

    def density(self, pos, sigma_m, norm=True):
        """particle density [1/m^2] by cell binning + gaussian smoothing; sigma_m in meters.
        Numerical note: the smoothed field is masked to the lake and re-normalized, so mass
        that numerically diffused onto land is redistributed inside the lake; near-shore
        concentration is therefore slightly overestimated (small effect, flagged in docs)."""
        from scipy.ndimage import gaussian_filter
        ny, nx = self.mask.shape
        hist = np.zeros((ny, nx))
        i, j = self._cell_index(pos[:, 0], pos[:, 1])
        good = (i >= 0) & (i < nx) & (j >= 0) & (j < ny)
        np.add.at(hist, (j[good], i[good]), 1.0)
        sig = sigma_m/self.dx
        hist = gaussian_filter(hist, sig)
        hist = np.where(self.mask, hist, 0.0)
        if norm:
            tot = hist.sum()
            if tot > 0:
                hist = hist/ (tot*self.dx*self.dx)
        return hist
