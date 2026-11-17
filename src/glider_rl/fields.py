"""Synthetic, divergence-free ocean-current fields built from stream functions.

Convention (used everywhere in this repo):  u = d(psi)/dy,  v = -d(psi)/dx.
With this convention a positive Gaussian bump in psi rotates COUNTER-CLOCKWISE
(positive relative vorticity zeta = dv/dx - du/dy = -laplacian(psi) > 0 at the centre).
An eddy with ``spin = +1`` is therefore counter-clockwise, ``spin = -1`` clockwise.

Every field is generated from an integer seed, so the same seed gives the same map.
Velocities are computed from analytic derivatives of psi; tests check them against
finite differences of psi and check the numerical divergence is ~0.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

ArrayLike = float | np.ndarray


class CurrentField:
    """Base class: a 2D current field defined by a stream function."""

    time_varying: bool = False
    kind: str = "base"

    def psi(self, x: ArrayLike, y: ArrayLike, t: float = 0.0) -> np.ndarray:
        """Stream function [m^2/s]."""
        raise NotImplementedError

    def velocity(self, x: ArrayLike, y: ArrayLike, t: float = 0.0) -> tuple[np.ndarray, np.ndarray]:
        """Current (u, v) [m/s] at positions x, y [m] and time t [s]."""
        raise NotImplementedError


@dataclass
class UniformDrift(CurrentField):
    """Uniform current: psi = U*y - V*x  ->  (u, v) = (U, V)."""

    u0: float
    v0: float
    kind: str = "drift"

    def psi(self, x, y, t=0.0):
        return self.u0 * np.asarray(y, float) - self.v0 * np.asarray(x, float)

    def velocity(self, x, y, t=0.0):
        shape = np.broadcast(np.asarray(x), np.asarray(y)).shape
        return np.full(shape, self.u0), np.full(shape, self.v0)


@dataclass
class GaussianEddies(CurrentField):
    """Sum of Gaussian eddies psi_i = s_i A_i exp(-r^2 / 2R_i^2), A_i = peak_i R_i sqrt(e).

    The swirl speed of one eddy peaks at r = R_i with value ``peak_i``.
    """

    xc: np.ndarray
    yc: np.ndarray
    radius: np.ndarray
    peak: np.ndarray
    spin: np.ndarray
    kind: str = "eddies"

    @property
    def amp(self) -> np.ndarray:
        """Signed stream-function amplitude of each eddy [m^2/s]."""
        return self.spin * self.peak * self.radius * np.sqrt(np.e)

    def _terms(self, x, y):
        dx = np.asarray(x, float)[..., None] - self.xc
        dy = np.asarray(y, float)[..., None] - self.yc
        g = self.amp * np.exp(-(dx**2 + dy**2) / (2 * self.radius**2))
        return dx, dy, g

    def psi(self, x, y, t=0.0):
        return self._terms(x, y)[2].sum(-1)

    def velocity(self, x, y, t=0.0):
        dx, dy, g = self._terms(x, y)
        r2 = self.radius**2
        u = (-g * dy / r2).sum(-1)   # d psi / dy
        v = (g * dx / r2).sum(-1)    # -d psi / dx
        return u, v


@dataclass
class MeanderingJet(CurrentField):
    """Meandering jet psi = U W tanh((eta - eta_c(xi)) / W), eta_c = eta0 + a sin(k xi + phi).

    (xi, eta) are along-/cross-jet coordinates rotated by ``theta`` about the domain centre.
    The jet core speed is U; it flows in direction ``theta`` (plus meander).
    """

    peak: float
    width: float
    theta: float
    eta0: float
    amp: float
    wavenumber: float
    phase: float
    centre: float
    kind: str = "jet"

    def _coords(self, x, y):
        xr = np.asarray(x, float) - self.centre
        yr = np.asarray(y, float) - self.centre
        c, s = np.cos(self.theta), np.sin(self.theta)
        xi = c * xr + s * yr
        eta = -s * xr + c * yr
        z = (eta - self.eta0 - self.amp * np.sin(self.wavenumber * xi + self.phase)) / self.width
        return xi, z

    def psi(self, x, y, t=0.0):
        _, z = self._coords(x, y)
        return self.peak * self.width * np.tanh(z)

    def velocity(self, x, y, t=0.0):
        xi, z = self._coords(x, y)
        sech2 = 1.0 / np.cosh(z) ** 2
        slope = self.amp * self.wavenumber * np.cos(self.wavenumber * xi + self.phase)
        u_xi = self.peak * sech2              # d psi / d eta
        u_eta = self.peak * sech2 * slope     # -d psi / d xi
        c, s = np.cos(self.theta), np.sin(self.theta)
        return c * u_xi - s * u_eta, s * u_xi + c * u_eta


@dataclass
class DoubleGyre(CurrentField):
    """Time-varying double gyre (Shadden et al. 2005 form) scaled to the square domain.

    X = 2x/L in [0, 2], Y = y/L in [0, 1];  f = eps sin(wt) X^2 + (1 - 2 eps sin(wt)) X;
    psi = sgn A sin(pi f) sin(pi Y).  A = peak L / (2 pi) so the fastest speeds are ~peak.
    """

    size: float
    peak: float
    eps: float
    omega: float
    phase: float
    sign: float
    kind: str = "double_gyre"
    time_varying: bool = True

    @property
    def amp(self) -> float:
        return self.sign * self.peak * self.size / (2 * np.pi)

    def _f(self, X, t):
        a = self.eps * np.sin(self.omega * t + self.phase)
        return a * X**2 + (1 - 2 * a) * X, 2 * a * X + (1 - 2 * a)

    def psi(self, x, y, t=0.0):
        X = 2 * np.asarray(x, float) / self.size
        Y = np.asarray(y, float) / self.size
        f, _ = self._f(X, t)
        return self.amp * np.sin(np.pi * f) * np.sin(np.pi * Y)

    def velocity(self, x, y, t=0.0):
        X = 2 * np.asarray(x, float) / self.size
        Y = np.asarray(y, float) / self.size
        f, fx = self._f(X, t)
        u = self.amp * np.sin(np.pi * f) * np.pi * np.cos(np.pi * Y) / self.size
        dpsi_dx = self.amp * np.pi * np.cos(np.pi * f) * fx * (2 / self.size) * np.sin(np.pi * Y)
        return u, -dpsi_dx


@dataclass
class SumField(CurrentField):
    """Superposition of fields (still divergence-free)."""

    parts: tuple[CurrentField, ...]
    kind: str = "sum"

    @property
    def time_varying(self) -> bool:  # type: ignore[override]
        return any(p.time_varying for p in self.parts)

    def psi(self, x, y, t=0.0):
        return sum(p.psi(x, y, t) for p in self.parts)

    def velocity(self, x, y, t=0.0):
        us, vs = zip(*(p.velocity(x, y, t) for p in self.parts))
        return sum(us), sum(vs)


def make_eddies(rng: np.random.Generator, cfg: dict[str, Any]) -> GaussianEddies:
    """Random Gaussian eddies; centres may lie slightly outside the domain."""
    e = cfg["fields"]["eddies"]
    size = cfg["domain"]["size_m"]
    n = int(rng.integers(e["n_min"], e["n_max"] + 1))
    return GaussianEddies(
        xc=rng.uniform(-0.1 * size, 1.1 * size, n),
        yc=rng.uniform(-0.1 * size, 1.1 * size, n),
        radius=rng.uniform(e["radius_min_m"], e["radius_max_m"], n),
        peak=rng.uniform(e["peak_min_mps"], e["peak_max_mps"], n),
        spin=rng.choice([-1.0, 1.0], n),
    )


def make_jet(rng: np.random.Generator, cfg: dict[str, Any]) -> MeanderingJet:
    """Random meandering jet crossing the domain near its centre."""
    j = cfg["fields"]["jet"]
    size = cfg["domain"]["size_m"]
    return MeanderingJet(
        peak=float(rng.uniform(j["peak_min_mps"], j["peak_max_mps"])),
        width=float(rng.uniform(j["width_min_m"], j["width_max_m"])),
        theta=float(rng.uniform(0, 2 * np.pi)),
        eta0=float(rng.uniform(-0.2 * size, 0.2 * size)),
        amp=float(rng.uniform(0, j["meander_amp_max_m"])),
        wavenumber=float(2 * np.pi / rng.uniform(j["meander_wavelength_min_m"], j["meander_wavelength_max_m"])),
        phase=float(rng.uniform(0, 2 * np.pi)),
        centre=size / 2,
    )


def make_double_gyre(rng: np.random.Generator, cfg: dict[str, Any]) -> DoubleGyre:
    """Random-phase time-varying double gyre (held-out test field)."""
    g = cfg["fields"]["double_gyre"]
    return DoubleGyre(
        size=cfg["domain"]["size_m"],
        peak=float(rng.uniform(g["peak_min_mps"], g["peak_max_mps"])),
        eps=float(rng.uniform(g["eps_min"], g["eps_max"])),
        omega=2 * np.pi / g["period_s"],
        phase=float(rng.uniform(0, 2 * np.pi)),
        sign=float(rng.choice([-1.0, 1.0])),
    )


def make_drift(rng: np.random.Generator, cfg: dict[str, Any]) -> UniformDrift:
    """Weak uniform drift in a random direction."""
    mag = rng.uniform(0, cfg["fields"]["drift_max_mps"])
    ang = rng.uniform(0, 2 * np.pi)
    return UniformDrift(float(mag * np.cos(ang)), float(mag * np.sin(ang)))


FIELD_MAKERS = {"eddies": make_eddies, "jet": make_jet, "double_gyre": make_double_gyre}


@dataclass
class Task:
    """One navigation problem ("map"): a current field plus start and goal."""

    seed: int
    kind: str
    field: CurrentField
    start: np.ndarray
    goal: np.ndarray


def choose_kind(seed: int, cfg: dict[str, Any]) -> str:
    """Field type of a map seed, drawn from ``fields.train_mix``."""
    mix = cfg["fields"]["train_mix"]
    kinds = sorted(mix)
    p = np.array([mix[k] for k in kinds], float)
    return str(np.random.default_rng([seed, 0]).choice(kinds, p=p / p.sum()))


def make_field(seed: int, cfg: dict[str, Any], kind: str | None = None) -> CurrentField:
    """Current field of map ``seed`` (``kind`` forces a field type, e.g. 'double_gyre')."""
    kind = kind or choose_kind(seed, cfg)
    rng = np.random.default_rng([seed, 1])
    main = FIELD_MAKERS[kind](rng, cfg)
    if kind == "double_gyre":
        return main
    return SumField((main, make_drift(rng, cfg)), kind=kind)


def sample_start_goal(seed: int, cfg: dict[str, Any]) -> tuple[np.ndarray, np.ndarray]:
    """Start and goal inside the margin, separated by [min, max] distance."""
    d = cfg["domain"]
    rng = np.random.default_rng([seed, 2])
    lo, hi = d["margin_m"], d["size_m"] - d["margin_m"]
    while True:
        start = rng.uniform(lo, hi, 2)
        dist = rng.uniform(d["min_start_goal_m"], d["max_start_goal_m"])
        ang = rng.uniform(0, 2 * np.pi)
        goal = start + dist * np.array([np.cos(ang), np.sin(ang)])
        if np.all(goal >= lo) and np.all(goal <= hi):
            return start, goal


def make_task(seed: int, cfg: dict[str, Any], kind: str | None = None) -> Task:
    """Build map ``seed``: field + start/goal, fully determined by the seed."""
    kind = kind or choose_kind(seed, cfg)
    start, goal = sample_start_goal(seed, cfg)
    return Task(int(seed), kind, make_field(seed, cfg, kind), start, goal)
