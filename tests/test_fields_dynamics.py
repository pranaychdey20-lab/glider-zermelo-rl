"""Stage 1 tests: fields, dynamics, energy, determinism."""
import numpy as np
import pytest

from glider_rl.baselines import run_episode, straight_line_policy
from glider_rl.dynamics import GliderState, integrate, step, step_energy
from glider_rl.env import GliderEnv
from glider_rl.fields import (GaussianEddies, SumField, UniformDrift, make_field, make_task)
from glider_rl.utils import load_config, with_overrides

CFG = load_config()
FIELD_CASES = [(s, k) for k in ("eddies", "jet", "double_gyre") for s in (0, 7, 123)]


class Zero(UniformDrift):
    def __init__(self):
        super().__init__(0.0, 0.0)


def _grid(cfg, n=41):
    xs = np.linspace(0, cfg["domain"]["size_m"], n)
    return np.meshgrid(xs, xs, indexing="xy")


def test_zero_current_straight_heading_arrives_at_d_over_v():
    cfg = with_overrides(CFG, glider__max_steps=1000)
    V, dt = cfg["glider"]["speed_mps"], cfg["glider"]["dt_s"]
    d = 18000.0  # exactly 100 steps
    p = integrate(Zero(), np.array([1000.0, 2000.0]), 0.0, 0.0, V, d / V, substeps=7)
    assert np.allclose(p, [1000.0 + d, 2000.0], atol=1e-6)
    s = GliderState(0.0, 0.0, np.pi / 4)
    n = 0
    while np.hypot(s.x, s.y) < d - 1e-6:
        s = step(s, 0.0, Zero(), cfg)
        n += 1
    assert n * dt == pytest.approx(d / V)
    assert np.hypot(s.x, s.y) == pytest.approx(d)


def test_uniform_current_vector_sum():
    f = UniformDrift(0.1, -0.2)
    V, h, T = 0.3, 0.7, 3600.0
    p = integrate(f, np.zeros(2), 0.0, h, V, T, substeps=3)
    expect = T * np.array([V * np.cos(h) + 0.1, V * np.sin(h) - 0.2])
    assert np.allclose(p, expect, atol=1e-9)


@pytest.mark.parametrize("seed,kind", FIELD_CASES)
def test_velocity_matches_stream_function_and_divergence_free(seed, kind):
    f = make_field(seed, CFG, kind)
    X, Y = _grid(CFG)
    t, h = 12345.0, 1.0
    u, v = f.velocity(X, Y, t)
    dpsi_dy = (f.psi(X, Y + h, t) - f.psi(X, Y - h, t)) / (2 * h)
    dpsi_dx = (f.psi(X + h, Y, t) - f.psi(X - h, Y, t)) / (2 * h)
    scale = max(np.abs(u).max(), np.abs(v).max())
    assert np.allclose(u, dpsi_dy, atol=1e-6 * scale + 1e-9)
    assert np.allclose(v, -dpsi_dx, atol=1e-6 * scale + 1e-9)
    div = ((f.velocity(X + h, Y, t)[0] - f.velocity(X - h, Y, t)[0])
           + (f.velocity(X, Y + h, t)[1] - f.velocity(X, Y - h, t)[1])) / (2 * h)
    vort_scale = scale / 1000.0  # ~ velocity / 1 km
    assert np.abs(div).max() < 1e-6 * vort_scale


@pytest.mark.parametrize("seed,kind", FIELD_CASES)
def test_field_speeds_are_plausible(seed, kind):
    f = make_field(seed, CFG, kind)
    X, Y = _grid(CFG)
    speed = np.hypot(*f.velocity(X, Y, 0.0))
    assert 0.02 < speed.max() < 1.2


@pytest.mark.parametrize("spin", [1.0, -1.0])
def test_eddy_spin_sign_convention(spin):
    """spin=+1 -> counter-clockwise: east of centre flows north, north of centre flows west."""
    e = GaussianEddies(np.array([0.0]), np.array([0.0]), np.array([5000.0]), np.array([0.3]), np.array([spin]))
    u_e, v_e = e.velocity(5000.0, 0.0)
    u_n, v_n = e.velocity(0.0, 5000.0)
    assert np.sign(v_e) == spin and abs(u_e) < 1e-12
    assert np.sign(u_n) == -spin and abs(v_n) < 1e-12
    assert np.hypot(u_e, v_e) == pytest.approx(0.3)  # peak swirl speed at r = R
    h = 1.0  # vorticity sign at centre
    zeta = (e.velocity(h, 0.0)[1] - e.velocity(-h, 0.0)[1] - e.velocity(0.0, h)[0] + e.velocity(0.0, -h)[0]) / (2 * h)
    assert np.sign(zeta) == spin


def test_same_seed_same_field_and_task():
    a, b, c = make_task(42, CFG), make_task(42, CFG), make_task(43, CFG)
    X, Y = _grid(CFG, 11)
    assert np.array_equal(a.field.velocity(X, Y)[0], b.field.velocity(X, Y)[0])
    assert np.array_equal(a.start, b.start) and np.array_equal(a.goal, b.goal)
    assert not np.array_equal(a.start, c.start)


def test_start_goal_constraints():
    d = CFG["domain"]
    for s in range(200):
        t = make_task(s, CFG)
        dist = np.linalg.norm(t.goal - t.start)
        assert d["min_start_goal_m"] <= dist <= d["max_start_goal_m"]
        for p in (t.start, t.goal):
            assert np.all(p >= d["margin_m"]) and np.all(p <= d["size_m"] - d["margin_m"])


def test_energy_never_negative():
    rng = np.random.default_rng(0)
    for dh in rng.uniform(-np.pi, np.pi, 100):
        assert step_energy(dh, 600.0, CFG) >= 0
    env = GliderEnv(CFG, split="val")
    env.reset(seed=0)
    e_prev = 0.0
    for a in rng.uniform(-1, 1, 200):
        _, _, term, trunc, _ = env.step(np.array([a]))
        assert env.state.energy >= e_prev
        e_prev = env.state.energy
        if term or trunc:
            break


def test_stepping_is_deterministic():
    env1, env2 = GliderEnv(CFG, split="val"), GliderEnv(CFG, split="val")
    r1 = run_episode(env1, straight_line_policy, 10003)
    r2 = run_episode(env2, straight_line_policy, 10003)
    assert r1 == r2


def test_rk2_more_accurate_than_euler():
    """Against a fine RK2 reference in a strong eddy, RK2 error << Euler error."""
    f = SumField((GaussianEddies(np.array([25000.0]), np.array([25000.0]), np.array([6000.0]),
                                 np.array([0.5]), np.array([1.0])), Zero()))
    p0 = np.array([25000.0 + 6000.0, 25000.0])
    ref = integrate(f, p0, 0.0, 1.0, 0.3, 600.0, substeps=2000, method="rk2")
    e_euler = np.linalg.norm(integrate(f, p0, 0.0, 1.0, 0.3, 600.0, 2, "euler") - ref)
    e_rk2 = np.linalg.norm(integrate(f, p0, 0.0, 1.0, 0.3, 600.0, 2, "rk2") - ref)
    assert e_rk2 < 0.1 * e_euler
