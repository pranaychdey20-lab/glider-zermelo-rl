"""Definition and launcher of all training runs (main, Pareto sweep, ablations).

Usage:
    python -m glider_rl.experiments --group main            # 5 seeds, default config
    python -m glider_rl.experiments --group pareto ablations --parallel 4
    python -m glider_rl.experiments --group long --parallel 5   # extra: 6M-step main runs
    python -m glider_rl.experiments --group stable --parallel 5 # extra: LR decay + target KL
    python -m glider_rl.experiments --list

Each run is ``python -m glider_rl.train --run <name> --seed <s> --set ...`` in its own
process (torch uses 1 thread), logging to results/logs/<name>.log. Finished runs
(model.zip present) are skipped, so the command can be re-run to resume.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import time
from dataclasses import dataclass, field

from .utils import RESULTS_DIR, load_config

PARETO_RATIOS = (0.0, 0.25, 1.0, 4.0, 16.0)   # w_energy / w_time, with w_time + w_energy = 2
LONG_TIMESTEPS = 6_000_000                     # extra experiment: 3x the main budget


@dataclass
class Run:
    """One training run."""

    name: str
    seed: int
    overrides: list[str] = field(default_factory=list)
    group: str = "main"
    timesteps: int | None = None   # None -> ppo.total_timesteps


def pareto_weights(ratio: float) -> tuple[float, float]:
    """(w_time, w_energy) with w_energy / w_time = ratio and w_time + w_energy = 2."""
    return 2.0 / (1.0 + ratio), 2.0 * ratio / (1.0 + ratio)


def all_runs(n_main_seeds: int = 5, n_seeds: int = 3) -> list[Run]:
    """Every training run of the study."""
    runs = [Run(f"main_s{s}", s) for s in range(n_main_seeds)]
    for r in PARETO_RATIOS:
        if r == 1.0:
            continue   # identical to main (w_time = w_energy = 1); main seeds 0-2 are reused
        wt, we = pareto_weights(r)
        runs += [Run(f"pareto_r{r:g}_s{s}", s, [f"env.reward.w_time={wt}", f"env.reward.w_energy={we}"], "pareto")
                 for s in range(n_seeds)]
    ablations = {"abl_nocurrent": ["env.observe_current=false"],
                 "abl_noenergy": ["env.reward.w_energy=0.0"],
                 "abl_fixedmap": ["env.fixed_map_seed=0"]}
    for name, ov in ablations.items():
        runs += [Run(f"{name}_s{s}", s, ov, "ablations") for s in range(n_seeds)]
    runs += [Run(f"long_s{s}", s, [], "long", LONG_TIMESTEPS) for s in range(n_main_seeds)]
    runs += [Run(f"stable_s{s}", s, ["ppo.lr_schedule=linear", "ppo.target_kl=0.02"], "stable")
             for s in range(n_main_seeds)]
    return runs


def launch(runs: list[Run], parallel: int, timesteps: int | None) -> None:
    """Run training processes with at most ``parallel`` at a time."""
    todo = [r for r in runs if not (RESULTS_DIR / "runs" / r.name / "model.zip").exists()]
    logs = RESULTS_DIR / "logs"
    logs.mkdir(parents=True, exist_ok=True)
    active: list[tuple[Run, subprocess.Popen]] = []
    while todo or active:
        while todo and len(active) < parallel:
            r = todo.pop(0)
            cmd = [sys.executable, "-m", "glider_rl.train", "--run", r.name, "--seed", str(r.seed)]
            if timesteps or r.timesteps:
                cmd += ["--timesteps", str(timesteps or r.timesteps)]
            if r.overrides:
                cmd += ["--set", *r.overrides]
            fh = open(logs / f"{r.name}.log", "w", encoding="utf-8")
            active.append((r, subprocess.Popen(cmd, stdout=fh, stderr=subprocess.STDOUT)))
            print(time.strftime("%H:%M:%S"), "start", r.name, flush=True)
        time.sleep(5)
        for item in list(active):
            if item[1].poll() is not None:
                active.remove(item)
                print(time.strftime("%H:%M:%S"), "end", item[0].name, "rc", item[1].returncode, flush=True)


def main() -> None:
    """CLI entry point."""
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--group", nargs="*", default=["main"], choices=["main", "pareto", "ablations", "long", "stable"])
    ap.add_argument("--parallel", type=int, default=4)
    ap.add_argument("--timesteps", type=int, default=None, help="override ppo.total_timesteps")
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args()
    cfg = load_config()
    runs = [r for r in all_runs(len(cfg["eval"]["train_seeds"])) if r.group in args.group]
    if args.list:
        for r in runs:
            print(r.name, r.seed, " ".join(r.overrides))
        return
    launch(runs, args.parallel, args.timesteps)


if __name__ == "__main__":
    main()
