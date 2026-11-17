"""Classical planner: Dijkstra on a 16-connected grid, plus a path-following controller.

Edge travel time uses the ground speed s along the edge direction d when the glider
picks the heading that cancels the cross-current (Zermelo "crabbing"):
    V h = s d - c,  |h| = 1   ->   s = c.d + sqrt(V^2 - (c x d)^2)   (needs |c x d| <= V, s > 0)
Graph nodes are (cell, arrival direction), so the energy-aware cost can charge for the
heading change between consecutive edges:
    cost = w_time * T + w_energy * (T + (e_turn / e_hotel) * dt * |dh| / pi)
which is the RL reward's time+energy part (both divided by the same T_scale).
w_energy = 0 gives the time-optimal planner. Time-varying fields are planned on a frozen
snapshot and re-planned every ``planner.replan_every`` steps.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import dijkstra

from .baselines import heading_to_action, straight_line_policy
from .env import GliderEnv
from .fields import CurrentField
from .utils import wrap_angle

MOVES = np.array([(1, 0), (2, 1), (1, 1), (1, 2), (0, 1), (-1, 2), (-1, 1), (-2, 1),
                  (-1, 0), (-2, -1), (-1, -1), (-1, -2), (0, -1), (1, -2), (1, -1), (2, -1)])


def crab_heading(c: np.ndarray, d: np.ndarray, V: float) -> tuple[float, float]:
    """Heading [rad] making ground velocity parallel to unit vector(s) ``d``, and ground speed.

    Works on arrays (last axis = 2). Infeasible directions get speed 0 and the heading that
    fights the cross-current.
    """
    along = np.sum(c * d, -1)
    cross = c[..., 0] * d[..., 1] - c[..., 1] * d[..., 0]
    disc = V**2 - cross**2
    s = np.where(disc >= 0, along + np.sqrt(np.maximum(disc, 0)), 0.0)
    s = np.where(s > 1e-3, s, 0.0)
    w = s[..., None] * d - c                                   # = V h when feasible
    perp = c - along[..., None] * d
    w = np.where((s > 0)[..., None], w, -perp)
    return np.arctan2(w[..., 1], w[..., 0]), s


@dataclass
class Plan:
    """A planned path (waypoints [m]) and its predicted cost/time."""

    waypoints: np.ndarray
    cost: float
    ok: bool


def plan_path(field: CurrentField, start: np.ndarray, goal: np.ndarray, heading0: float,
              t0: float, cfg: dict[str, Any], w_time: float, w_energy: float) -> Plan:
    """Dijkstra from ``start`` to ``goal`` on a frozen snapshot of the field at ``t0``."""
    p = cfg["planner"]
    L, sp, V = cfg["domain"]["size_m"], p["grid_spacing_m"], cfg["glider"]["speed_mps"]
    coords = np.arange(sp, L - sp + 1e-6, sp)                   # keep 1 cell off the walls
    n, K = len(coords), len(MOVES)
    turn_w = w_energy * cfg["energy"]["e_turn_w"] / cfg["energy"]["e_hotel_w"] * cfg["glider"]["dt_s"] / np.pi
    I, J = np.meshgrid(np.arange(n), np.arange(n), indexing="ij")   # I -> x index, J -> y index
    # per (cell, move): validity, travel time and required heading
    I2 = I[..., None] + MOVES[:, 0]
    J2 = J[..., None] + MOVES[:, 1]
    inside = (I2 >= 0) & (I2 < n) & (J2 >= 0) & (J2 < n)
    length = np.hypot(*MOVES.T) * sp
    dirs = MOVES / np.hypot(*MOVES.T)[:, None]
    mx = coords[I][..., None] + 0.5 * MOVES[:, 0] * sp
    my = coords[J][..., None] + 0.5 * MOVES[:, 1] * sp
    u, v = field.velocity(mx, my, t0)
    head, speed = crab_heading(np.stack([u, v], -1), np.broadcast_to(dirs, mx.shape + (2,)), V)
    valid = inside & (speed > 0)
    T = np.where(valid, length / np.maximum(speed, 1e-9), np.inf)
    cost_move = (w_time + w_energy) * T                          # (n, n, K)

    node = lambda i, j, k: (i * n + j) * K + k                   # noqa: E731
    src_id = n * n * K
    # edges (cell, k_in) -> (cell + move_m, m)
    Ip, Jp = I[..., None] - MOVES[:, 0], J[..., None] - MOVES[:, 1]   # predecessor cell for k_in
    has_in = (Ip >= 0) & (Ip < n) & (Jp >= 0) & (Jp < n)
    Ipc, Jpc = np.clip(Ip, 0, n - 1), np.clip(Jp, 0, n - 1)
    k_idx = np.arange(K)
    in_ok = has_in & valid[Ipc, Jpc, k_idx]                       # (n, n, K_in)
    in_head = head[Ipc, Jpc, k_idx]                               # heading on incoming edge
    turn = np.abs(wrap_angle(head[:, :, None, :] - in_head[..., None]))   # (n, n, K_in, K_out)
    ok = in_ok[..., None] & valid[:, :, None, :]
    w = cost_move[:, :, None, :] + turn_w * turn
    ii, jj, kk, mm = np.nonzero(ok)
    rows = node(ii, jj, kk)
    cols = node(I2[ii, jj, mm], J2[ii, jj, mm], mm)
    data = w[ii, jj, kk, mm]
    # virtual source -> out-edges of the start cell
    si, sj = [int(np.clip(np.rint(s / sp - 1), 0, n - 1)) for s in start]
    gi, gj = [int(np.clip(np.rint(g / sp - 1), 0, n - 1)) for g in goal]
    ms = np.nonzero(valid[si, sj])[0]
    rows = np.concatenate([rows, np.full(ms.size, src_id)])
    cols = np.concatenate([cols, node(I2[si, sj, ms], J2[si, sj, ms], ms)])
    data = np.concatenate([data, cost_move[si, sj, ms] + turn_w * np.abs(wrap_angle(head[si, sj, ms] - heading0))])
    graph = coo_matrix((data + 1e-12, (rows, cols)), shape=(src_id + 1, src_id + 1)).tocsr()
    dist, pred = dijkstra(graph, indices=src_id, return_predecessors=True)
    goal_nodes = node(gi, gj, k_idx)
    best = goal_nodes[np.argmin(dist[goal_nodes])]
    if not np.isfinite(dist[best]):
        return Plan(np.array([start, goal]), float("inf"), False)
    path = []
    cur = best
    while cur != src_id and cur >= 0:
        cell = cur // K
        path.append((coords[cell // n], coords[cell % n]))
        cur = pred[cur]
    path.append((coords[si], coords[sj]))
    wps = np.array(path[::-1] + [tuple(goal)], float)
    return Plan(wps, float(dist[best]), True)


class PlannerPolicy:
    """Follow a planned path with a look-ahead point and current-compensating heading."""

    def __init__(self, cfg: dict[str, Any], w_time: float, w_energy: float) -> None:
        self.cfg = cfg
        self.w_time, self.w_energy = w_time, w_energy
        self.lookahead = cfg["planner"]["lookahead_m"]
        self.replan_every = int(cfg["planner"]["replan_every"])
        self.plan: Plan | None = None

    def reset(self, env: GliderEnv) -> None:
        """Plan from the episode start."""
        self._replan(env)
        self.n_steps = 0

    def _replan(self, env: GliderEnv) -> None:
        s = env.state
        self.plan = plan_path(env.task.field, s.pos, env.task.goal, s.heading, s.t,
                              self.cfg, self.w_time, self.w_energy)
        self.idx = 0

    def __call__(self, obs: np.ndarray, env: GliderEnv) -> np.ndarray:
        if (self.replan_every > 0 and env.task.field.time_varying and self.n_steps > 0
                and self.n_steps % self.replan_every == 0):
            self._replan(env)
        self.n_steps += 1
        if not self.plan.ok:
            return straight_line_policy(obs, env)
        pos, wps = env.state.pos, self.plan.waypoints
        d = np.linalg.norm(wps[self.idx:] - pos, axis=1)
        self.idx += int(np.argmin(d))                             # never move backwards
        ahead = np.nonzero(np.linalg.norm(wps[self.idx:] - pos, axis=1) >= self.lookahead)[0]
        target = wps[self.idx + ahead[0]] if ahead.size else wps[-1]
        vec = target - pos
        dvec = vec / max(np.linalg.norm(vec), 1e-9)
        u, v = env.task.field.velocity(pos[0], pos[1], env.state.t)
        h, _ = crab_heading(np.array([float(u), float(v)]), dvec, env.V)
        return heading_to_action(float(h), env)
