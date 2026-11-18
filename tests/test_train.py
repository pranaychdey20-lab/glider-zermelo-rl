"""Reproducibility: the same training seed gives the same PPO parameters (CPU)."""
import torch
from stable_baselines3 import PPO

from glider_rl import train as train_mod
from glider_rl.utils import load_config, with_overrides


def test_training_is_deterministic_given_seed(tmp_path, monkeypatch):
    monkeypatch.setattr(train_mod, "RESULTS_DIR", tmp_path)
    cfg = with_overrides(load_config(), ppo__n_envs=2, ppo__n_steps=64, ppo__batch_size=64, ppo__n_epochs=2)
    params = []
    for run in ("a", "b"):
        out = train_mod.train(cfg, seed=3, run=run, timesteps=256)
        params.append(PPO.load(out / "model.zip", device="cpu").policy.state_dict())
    assert all(torch.equal(params[0][k], params[1][k]) for k in params[0])
