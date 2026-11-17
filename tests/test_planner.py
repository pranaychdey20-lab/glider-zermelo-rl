"""Stage 2 tests: crab heading geometry and Dijkstra planner sanity."""
import numpy as np
import pytest

from glider_rl.baselines import run_episode, straight_line_policy
from glider_rl.env import GliderEnv
from glider_rl.fields import UniformDrift
from glider_rl.planner import PlannerPolicy, crab_heading, plan_path
from glider_rl.utils import load_config

CFG = load_config()
V = CFG["glider"]["speed_mps"]


@pytest.mark.parametrize("c", [(0.0, 0.0), (0.1, -0.2), (-0.25, 0.1), (0.0, 0.29)])
def test_crab_heading_makes_ground_velocity_parallel(c):
    c = np.array(c)
    for ang in np.linspace(0, 2 * np.pi, 13):
        d = np.array([np.cos(ang), np.sin(ang)])
        h, s = crab_heading(c, d, V)
        g = V * np.array([np.cos(h), np.sin(h)]) + c
        if s > 0:
            assert np.allclose(g, s * d, atol=1e-9)


def test_crab_heading_infeasible_cross_current():
    h, s = crab_heading(np.array([0.0, 0.5]), np.array([1.0, 0.0]), V)
    assert s == 0.0
    assert np.isclose(np.sin(h), -1.0)  # fights the cross-current


def test_zero_current_plan_time_close_to_straight_line():
    start, goal = np.array([5000.0, 5000.0]), np.array([30000.0, 20000.0])
    plan = plan_path(UniformDrift(0.0, 0.0), start, goal, 0.0, 0.0, CFG, 1.0, 0.0)
    assert plan.ok
    d = np.linalg.norm(goal - start)
    assert d / V <= plan.cost <= 1.06 * d / V   # grid detour < 6 %
    assert np.allclose(plan.waypoints[-1], goal)


def test_planner_uses_favourable_current():
    """Uniform tail current: predicted time equals d / (V + c)."""
    start, goal = np.array([5000.0, 25000.0]), np.array([35000.0, 25000.0])
    plan = plan_path(UniformDrift(0.2, 0.0), start, goal, 0.0, 0.0, CFG, 1.0, 0.0)
    assert plan.cost == pytest.approx(30000.0 / 0.5, rel=1e-6)


def test_planner_episode_succeeds_where_straight_line_is_captured():
    """Map 10006 (validation): straight-line is captured by an eddy, the planner arrives."""
    env = GliderEnv(CFG, split="val")
    assert not run_episode(env, straight_line_policy, 10006)["success"]
    assert run_episode(env, PlannerPolicy(CFG, 1.0, 0.0), 10006)["success"]
