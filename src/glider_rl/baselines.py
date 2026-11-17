"""Non-learning baselines and a generic episode runner.

A policy here is a callable ``policy(obs, env) -> action`` (action in [-1, 1]).
Baselines may read the true simulator state via ``env`` (privileged access);
the RL agent only sees ``obs``.
"""
from __future__ import annotations

from typing import Any, Callable

import numpy as np

from .env import GliderEnv
from .utils import wrap_angle

Policy = Callable[[np.ndarray, GliderEnv], np.ndarray]


def heading_to_action(desired: float, env: GliderEnv) -> np.ndarray:
    """Action that turns towards ``desired`` heading as far as the turn limit allows."""
    err = float(wrap_angle(desired - env.state.heading))
    return np.array([np.clip(err / env.max_turn, -1.0, 1.0)], np.float32)


def straight_line_policy(obs: np.ndarray, env: GliderEnv) -> np.ndarray:
    """Naive baseline: point the nose at the goal every step (no current compensation)."""
    d = env.task.goal - env.state.pos
    return heading_to_action(float(np.arctan2(d[1], d[0])), env)


def make_random_policy(seed: int) -> Policy:
    """Uniform random heading changes."""
    rng = np.random.default_rng(seed)
    return lambda obs, env: rng.uniform(-1, 1, 1).astype(np.float32)


def run_episode(env: GliderEnv, policy: Policy, map_seed: int, seed: int = 0) -> dict[str, Any]:
    """Run one episode on ``map_seed``; returns metrics plus trajectory (if recording)."""
    obs, _ = env.reset(seed=seed, options={"map_seed": int(map_seed)})
    if hasattr(policy, "reset"):
        policy.reset(env)
    while True:
        obs, _, term, trunc, info = env.step(policy(obs, env))
        if term or trunc:
            out = dict(info["episode_metrics"])
            if env.record:
                out["traj"] = np.array(env.traj)
                out["energy_trace"] = np.array(env.energies)
            return out
