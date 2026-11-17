"""Gymnasium environment: glider navigation to a goal through a current field.

Action: one float in [-1, 1] -> heading change of action * max_turn_deg this step.

Observation (float32, 62 entries, all roughly O(1)). Vectors are expressed in the
GOAL FRAME: x-axis = direction from the glider to the goal (b = bearing to goal).
    [0:2]   distance to goal / domain size, distance to goal / initial distance d0
    [2:4]   sin(h - b), cos(h - b)           heading relative to the goal direction
    [4:6]   local current (along, across) / V                         (optionally noisy)
    [6:56]  5x5 patch of currents (along, across) / V, 2 km spacing, patch axes aligned
            with the goal frame, row-major                          (optionally noisy)
    [56]    elapsed time / (max_steps * dt)
    [57]    energy used / maximum possible episode energy
    [58:60] position / domain size (world frame; lets the agent see the walls)
    [60:62] sin(b), cos(b)                   goal-frame orientation in the world
See docs/ASSUMPTIONS.md for why this differs from a plain world-frame observation.

Reward per step (each term logged in ``info['reward_terms']``):
    - w_time * dt / T_scale                    T_scale = d0 / V   (still-water straight time)
    - w_energy * e_step / E_scale              E_scale = e_hotel * T_scale
    + k_progress * (d_prev - d_now) / d0       potential-based progress shaping
    + goal_bonus on arrival, - fail_penalty on leaving the domain,
    - timeout_penalty at the step limit.
The glider always moves at V through the water, so it cannot "stay still"; circling
gains nothing from shaping (it telescopes) and costs time/energy every step.
"""
from __future__ import annotations

from typing import Any

import gymnasium as gym
import numpy as np

from .dynamics import GliderState, step, step_energy
from .fields import Task, make_task
from .utils import split_seeds


class GliderEnv(gym.Env):
    """Underwater-glider Zermelo navigation environment."""

    metadata = {"render_modes": []}
    OBS_DIM = 62

    def __init__(self, cfg: dict[str, Any], split: str = "train", kind: str | None = None,
                 map_seeds: np.ndarray | None = None, record: bool = False) -> None:
        super().__init__()
        self.cfg = cfg
        self.kind = kind
        fixed = cfg["env"].get("fixed_map_seed")
        if map_seeds is not None:
            self.map_seeds = np.asarray(map_seeds)
        elif fixed is not None:
            self.map_seeds = np.array([int(fixed)])
        else:
            self.map_seeds = split_seeds(cfg, split)
        self.record = record
        g, e = cfg["glider"], cfg["env"]
        self.size = cfg["domain"]["size_m"]
        self.V = g["speed_mps"]
        self.dt = g["dt_s"]
        self.max_steps = g["max_steps"]
        self.max_turn = np.deg2rad(g["max_turn_deg"])
        half = e["patch_size"] // 2
        offs = np.arange(-half, half + 1) * e["patch_spacing_m"]
        self.patch_dx, self.patch_dy = [a.ravel() for a in np.meshgrid(offs, offs, indexing="xy")]
        self.e_max = step_energy(self.max_turn, self.dt, cfg) * self.max_steps
        self.action_space = gym.spaces.Box(-1.0, 1.0, (1,), np.float32)
        self.observation_space = gym.spaces.Box(-10.0, 10.0, (self.OBS_DIM,), np.float32)
        self.task: Task | None = None
        self.state: GliderState | None = None

    # ------------------------------------------------------------------ helpers
    def _bearing(self) -> float:
        d = self.task.goal - self.state.pos
        return float(np.arctan2(d[1], d[0]))

    def _currents(self, b: float) -> np.ndarray:
        """Observed local current and patch in the goal frame, divided by V."""
        s = self.state
        c, sn = np.cos(b), np.sin(b)
        px = c * self.patch_dx - sn * self.patch_dy          # patch axes rotated to goal frame
        py = sn * self.patch_dx + c * self.patch_dy
        u, v = self.task.field.velocity(np.concatenate([[s.x], s.x + px]),
                                        np.concatenate([[s.y], s.y + py]), s.t)
        std = self.cfg["env"]["obs_noise_std_mps"]
        if std > 0:
            u = u + self.np_random.normal(0.0, std, u.shape)
            v = v + self.np_random.normal(0.0, std, v.shape)
        cur = np.stack([c * u + sn * v, -sn * u + c * v], axis=1)   # (along, across)
        if not self.cfg["env"]["observe_current"]:
            cur = np.zeros_like(cur)
        return cur.ravel() / self.V

    def _obs(self) -> np.ndarray:
        s = self.state
        b = self._bearing()
        d = self.dist()
        rel = s.heading - b
        obs = np.concatenate([
            [d / self.size, d / self.d0, np.sin(rel), np.cos(rel)], self._currents(b),
            [s.t / (self.max_steps * self.dt), s.energy / self.e_max], s.pos / self.size,
            [np.sin(b), np.cos(b)],
        ])
        return np.clip(obs, -10, 10).astype(np.float32)

    def dist(self) -> float:
        """Distance from glider to goal [m]."""
        return float(np.linalg.norm(self.task.goal - self.state.pos))

    # ---------------------------------------------------------------- gym API
    def reset(self, *, seed: int | None = None, options: dict | None = None):
        super().reset(seed=seed)
        options = options or {}
        map_seed = options.get("map_seed")
        if map_seed is None:
            map_seed = int(self.np_random.choice(self.map_seeds))
        self.task = make_task(int(map_seed), self.cfg, self.kind)
        to_goal = self.task.goal - self.task.start
        self.state = GliderState(float(self.task.start[0]), float(self.task.start[1]),
                                 float(np.arctan2(to_goal[1], to_goal[0])))
        self.d0 = self.dist()
        self.t_scale = self.d0 / self.V
        self.e_scale = self.cfg["energy"]["e_hotel_w"] * self.t_scale
        self.steps = 0
        self.path_len = 0.0
        self.term_sums = {k: 0.0 for k in ("time", "energy", "progress", "terminal")}
        self.traj = [self.state.pos.copy()] if self.record else []
        self.energies = [0.0] if self.record else []
        return self._obs(), {"map_seed": int(map_seed), "kind": self.task.kind}

    def step(self, action):
        r_cfg = self.cfg["env"]["reward"]
        dh = float(np.clip(np.asarray(action, float).ravel()[0], -1, 1)) * self.max_turn
        d_prev = self.dist()
        prev_pos = self.state.pos
        e_before = self.state.energy
        self.state = step(self.state, dh, self.task.field, self.cfg)
        self.steps += 1
        self.path_len += float(np.linalg.norm(self.state.pos - prev_pos))
        d_now = self.dist()
        terms = {
            "time": -r_cfg["w_time"] * self.dt / self.t_scale,
            "energy": -r_cfg["w_energy"] * (self.state.energy - e_before) / self.e_scale,
            "progress": r_cfg["k_progress"] * (d_prev - d_now) / self.d0,
            "terminal": 0.0,
        }
        x, y = self.state.x, self.state.y
        success = d_now <= self.cfg["domain"]["goal_radius_m"]
        out = not (0.0 <= x <= self.size and 0.0 <= y <= self.size)
        timeout = self.steps >= self.max_steps
        reason = "running"
        if success:
            terms["terminal"], reason = r_cfg["goal_bonus"], "success"
        elif out:
            terms["terminal"], reason = -r_cfg["fail_penalty"], "out_of_domain"
        elif timeout:
            terms["terminal"], reason = -r_cfg["timeout_penalty"], "timeout"
        for k, v in terms.items():
            self.term_sums[k] += v
        if self.record:
            self.traj.append(self.state.pos.copy())
            self.energies.append(self.state.energy)
        terminated = bool(success or out)
        truncated = bool(timeout and not terminated)
        info = {"reward_terms": terms, "reason": reason}
        if terminated or truncated:
            info["episode_metrics"] = self.metrics(reason)
        return self._obs(), float(sum(terms.values())), terminated, truncated, info

    def metrics(self, reason: str) -> dict[str, Any]:
        """Per-episode metrics (time [s], energy [J], path length [m])."""
        return {
            "map_seed": self.task.seed, "kind": self.task.kind, "success": reason == "success",
            "reason": reason, "time_s": self.state.t, "energy_J": self.state.energy,
            "path_m": self.path_len, "d0_m": self.d0, "final_dist_m": self.dist(),
            "steps": self.steps, **{f"R_{k}": v for k, v in self.term_sums.items()},
        }
