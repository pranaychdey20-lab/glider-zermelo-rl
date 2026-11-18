"""Train a PPO agent (stable-baselines3, CPU).

Usage:
    python -m glider_rl.train --seed 0 --run main_s0 [--timesteps N] [--set env.reward.w_energy=0]

Writes to results/runs/<run>/: config.yaml, model.zip (git-ignored), episodes.csv
(one row per finished training episode), progress.csv (SB3 logger) and TensorBoard
events in results/tb/<run>.
"""
from __future__ import annotations

import argparse
import csv
import time
from pathlib import Path
from typing import Any, Callable

import numpy as np
import torch
import yaml
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import BaseCallback
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.logger import configure

from .env import GliderEnv
from .utils import RESULTS_DIR, load_config


class EpisodeLogger(BaseCallback):
    """Write per-episode metrics and reward-term sums to CSV; log means to SB3."""

    def __init__(self, path: Path) -> None:
        super().__init__()
        self.path = path
        self.fh = None
        self.writer = None
        self.recent: list[dict[str, Any]] = []

    def _on_step(self) -> bool:
        for info in self.locals["infos"]:
            m = info.get("episode_metrics")
            if m is None:
                continue
            row = {"timesteps": self.num_timesteps, **m}
            if self.writer is None:
                self.fh = open(self.path, "w", newline="", encoding="utf-8")
                self.writer = csv.DictWriter(self.fh, fieldnames=list(row))
                self.writer.writeheader()
            self.writer.writerow(row)
            self.recent = (self.recent + [m])[-200:]
        return True

    def _on_rollout_end(self) -> None:
        if not self.recent:
            return
        for k in ("success", "time_s", "energy_J", "R_time", "R_energy", "R_progress", "R_terminal"):
            self.logger.record(f"episode/{k}", float(np.mean([m[k] for m in self.recent])))
        for reason in ("timeout", "out_of_domain"):
            self.logger.record(f"episode/frac_{reason}", float(np.mean([m["reason"] == reason for m in self.recent])))
        self.fh.flush()

    def _on_training_end(self) -> None:
        if self.fh:
            self.fh.close()


def learning_rate(p: dict[str, Any]) -> float | Callable[[float], float]:
    """Constant learning rate, or linear decay to 0 (SB3 passes progress_remaining 1 -> 0)."""
    if p["lr_schedule"] == "linear":
        return lambda progress_remaining: p["learning_rate"] * progress_remaining
    return p["learning_rate"]


def train(cfg: dict[str, Any], seed: int, run: str, timesteps: int) -> Path:
    """Train one PPO agent; returns the run directory."""
    p = cfg["ppo"]
    torch.set_num_threads(int(p["torch_threads"]))
    out = RESULTS_DIR / "runs" / run
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "config.yaml", "w", encoding="utf-8") as fh:
        yaml.safe_dump({**cfg, "train_seed": seed, "timesteps": timesteps}, fh, sort_keys=False)
    venv = make_vec_env(lambda: GliderEnv(cfg, split="train"), n_envs=p["n_envs"], seed=seed)
    model = PPO("MlpPolicy", venv, seed=seed, device="cpu", verbose=0,
                n_steps=p["n_steps"], batch_size=p["batch_size"], n_epochs=p["n_epochs"],
                learning_rate=learning_rate(p), target_kl=p["target_kl"],
                gamma=p["gamma"], gae_lambda=p["gae_lambda"],
                clip_range=p["clip_range"], ent_coef=p["ent_coef"],
                policy_kwargs={"net_arch": list(p["net_arch"]), "log_std_init": p["log_std_init"]})
    model.set_logger(configure(str(out), ["csv", "tensorboard"]))
    t0 = time.time()
    model.learn(total_timesteps=timesteps, callback=EpisodeLogger(out / "episodes.csv"))
    model.save(out / "model.zip")
    (out / "train_time_s.txt").write_text(f"{time.time() - t0:.1f}\n")
    return out


def main() -> None:
    """CLI entry point."""
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", default=None)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--run", required=True, help="run name (folder under results/runs)")
    ap.add_argument("--timesteps", type=int, default=None)
    ap.add_argument("--quick", action="store_true", help="use ppo.quick_timesteps")
    ap.add_argument("--set", nargs="*", default=[], help="config overrides a.b=value")
    args = ap.parse_args()
    cfg = load_config(args.config, args.set)
    steps = args.timesteps or (cfg["ppo"]["quick_timesteps"] if args.quick else cfg["ppo"]["total_timesteps"])
    print("run dir:", train(cfg, args.seed, args.run, steps))


if __name__ == "__main__":
    main()
