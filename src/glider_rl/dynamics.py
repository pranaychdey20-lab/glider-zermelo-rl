"""Glider kinematics and the (assumed) energy model.

Ground velocity = V (cos h, sin h) + current(x, y, t).  The heading h is held constant
over a control step of length dt and the position is integrated with RK2 (midpoint)
or explicit Euler, optionally with several sub-steps.

ENERGY MODEL (ASSUMPTION, not a physical glider model):
    e_step = (e_hotel + e_turn * |dh| / pi) * dt      [J]
with e_hotel, e_turn in W and dh the heading change applied at the start of the step.
Real glider energy is dominated by the buoyancy pump and the hotel load; heading
changes cost very little. This model only gives the planner/RL a reason to avoid
needless turning on top of the hotel load (which is proportional to time).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from .fields import CurrentField
from .utils import wrap_angle


@dataclass
class GliderState:
    """Position [m], heading [rad, from +x counter-clockwise], time [s], energy used [J]."""

    x: float
    y: float
    heading: float
    t: float = 0.0
    energy: float = 0.0

    @property
    def pos(self) -> np.ndarray:
        return np.array([self.x, self.y])


def ground_velocity(field: CurrentField, x: float, y: float, t: float,
                    heading: float, speed: float) -> np.ndarray:
    """Ground velocity [m/s] = through-water velocity + current."""
    u, v = field.velocity(x, y, t)
    return np.array([speed * np.cos(heading) + float(u), speed * np.sin(heading) + float(v)])


def integrate(field: CurrentField, pos: np.ndarray, t: float, heading: float,
              speed: float, dt: float, substeps: int = 1, method: str = "rk2") -> np.ndarray:
    """Advance a position over ``dt`` at fixed heading; returns the new position."""
    h = dt / substeps
    p = np.array(pos, float)
    for i in range(substeps):
        ti = t + i * h
        k1 = ground_velocity(field, p[0], p[1], ti, heading, speed)
        if method == "euler":
            p = p + h * k1
        elif method == "rk2":
            mid = p + 0.5 * h * k1
            p = p + h * ground_velocity(field, mid[0], mid[1], ti + 0.5 * h, heading, speed)
        else:
            raise ValueError(f"unknown integrator {method}")
    return p


def step_energy(dheading: float, dt: float, cfg: dict[str, Any]) -> float:
    """Energy [J] of one step under the assumed model (never negative)."""
    e = cfg["energy"]
    return (e["e_hotel_w"] + e["e_turn_w"] * abs(float(dheading)) / np.pi) * dt


def step(state: GliderState, dheading: float, field: CurrentField, cfg: dict[str, Any]) -> GliderState:
    """Apply a heading change [rad], then integrate one control step."""
    g = cfg["glider"]
    heading = float(wrap_angle(state.heading + dheading))
    p = integrate(field, state.pos, state.t, heading, g["speed_mps"], g["dt_s"],
                  g["substeps"], g["integrator"])
    return GliderState(float(p[0]), float(p[1]), heading, state.t + g["dt_s"],
                       state.energy + step_energy(dheading, g["dt_s"], cfg))
