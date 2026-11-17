"""Stage 3 tests: Gymnasium API compliance and reward bookkeeping."""
import numpy as np
import pytest
from gymnasium.utils.env_checker import check_env

from glider_rl.baselines import make_random_policy, run_episode, straight_line_policy
from glider_rl.env import GliderEnv
from glider_rl.utils import load_config, with_overrides

CFG = load_config()


def test_check_env_passes():
    check_env(GliderEnv(CFG), skip_render_check=True)


@pytest.mark.parametrize("policy", [straight_line_policy, make_random_policy(1)])
def test_reward_terms_sum_and_shaping_telescopes(policy):
    env = GliderEnv(CFG, split="val")
    obs, _ = env.reset(seed=3, options={"map_seed": 10010})
    total, prog = 0.0, 0.0
    while True:
        obs, r, term, trunc, info = env.step(policy(obs, env))
        assert env.observation_space.contains(obs)
        assert r == pytest.approx(sum(info["reward_terms"].values()))
        total += r
        prog += info["reward_terms"]["progress"]
        if term or trunc:
            break
    m = info["episode_metrics"]
    k = CFG["env"]["reward"]["k_progress"]
    assert prog == pytest.approx(k * (1 - m["final_dist_m"] / m["d0_m"]))
    assert total == pytest.approx(sum(m[f"R_{t}"] for t in ("time", "energy", "progress", "terminal")))


def test_circling_is_not_rewarded():
    """Turning in place forever earns negative return (no stay-still loophole)."""
    env = GliderEnv(with_overrides(CFG, fields__drift_max_mps=0.0), split="val")
    obs, _ = env.reset(seed=0, options={"map_seed": 10010})
    total = 0.0
    while True:
        obs, r, term, trunc, info = env.step(np.array([1.0]))
        total += r
        if term or trunc:
            break
    assert info["reason"] in ("timeout", "out_of_domain")
    assert total < 0


def test_observation_noise_is_seeded():
    cfg = with_overrides(CFG, env__obs_noise_std_mps=0.1)
    a, _ = GliderEnv(cfg).reset(seed=5, options={"map_seed": 3})
    b, _ = GliderEnv(cfg).reset(seed=5, options={"map_seed": 3})
    c, _ = GliderEnv(CFG).reset(seed=5, options={"map_seed": 3})
    assert np.array_equal(a, b) and not np.array_equal(a, c)


def test_no_current_ablation_hides_currents():
    obs, _ = GliderEnv(with_overrides(CFG, env__observe_current=False)).reset(seed=0)
    assert np.all(obs[4:56] == 0)


def test_straight_line_and_random_run_in_env():
    env = GliderEnv(CFG, split="val")
    for pol in (straight_line_policy, make_random_policy(0)):
        m = run_episode(env, pol, 10000)
        assert m["reason"] in ("success", "timeout", "out_of_domain")
        assert m["energy_J"] > 0 and m["path_m"] > 0
