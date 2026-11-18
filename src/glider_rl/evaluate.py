"""Evaluate methods on a fixed set of maps and summarise paired results.

Usage (one command per evaluation; raw per-episode rows go to CSV):
    python -m glider_rl.evaluate --split test --methods straight planner_time planner_energy \
        --runs main_s0 main_s1 --condition main --out results/eval/test_main.csv
    python -m glider_rl.evaluate --summarize results/eval/test_main.csv --out results/summary.csv

Methods: straight, planner_time, planner_energy, random, and RL runs given with --runs
(folders under results/runs/, each containing model.zip). Map sets come only from the
config splits (train/val/test). Protocol: docs/EVAL_PROTOCOL.md.
"""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd
import yaml

from .baselines import Policy, make_random_policy, run_episode, straight_line_policy
from .env import GliderEnv
from .planner import PlannerPolicy
from .utils import RESULTS_DIR, bootstrap_ci, load_config, set_by_path, split_seeds

BASELINES = ("straight", "planner_time", "planner_energy", "random")


def baseline_policy(method: str, cfg: dict[str, Any]) -> Policy:
    """Policy object for a non-learning method."""
    r = cfg["env"]["reward"]
    if method == "straight":
        return straight_line_policy
    if method == "planner_time":
        return PlannerPolicy(cfg, 1.0, 0.0)
    if method == "planner_energy":
        return PlannerPolicy(cfg, r["w_time"], r["w_energy"])
    if method == "random":
        return make_random_policy(0)
    raise ValueError(method)


def rl_policy(run_dir: Path) -> Policy:
    """Deterministic policy from a saved PPO model (a run folder or a .zip file)."""
    import torch
    from stable_baselines3 import PPO

    torch.set_num_threads(1)
    path = Path(run_dir)
    model = PPO.load(path if path.suffix == ".zip" else path / "model.zip", device="cpu")
    return lambda obs, env: model.predict(obs, deterministic=True)[0]


def run_config(run_dir: Path) -> dict[str, Any]:
    """Config a run was trained with."""
    return load_config(run_dir / "config.yaml")


def evaluate(policy: Policy, cfg: dict[str, Any], map_seeds: Iterable[int], kind: str | None,
             tags: dict[str, Any]) -> list[dict[str, Any]]:
    """Run ``policy`` on every map; one row per episode (episode seed = map seed)."""
    env = GliderEnv(cfg, kind=kind, map_seeds=np.asarray(list(map_seeds)))
    return [{**tags, **run_episode(env, policy, int(m), seed=int(m))} for m in env.map_seeds]


def eval_cli(args: argparse.Namespace) -> None:
    """Evaluate baselines and RL runs; write raw rows to ``args.out``."""
    base_cfg = load_config(args.config, args.set)
    seeds = split_seeds(base_cfg, args.split)
    if args.max_maps:
        seeds = seeds[: args.max_maps]
    rows: list[dict[str, Any]] = []
    for m in args.methods:
        tags = {"method": m + args.suffix, "run": m + args.suffix, "train_seed": -1, "condition": args.condition, "split": args.split}
        rows += evaluate(baseline_policy(m, base_cfg), base_cfg, seeds, args.kind, tags)
        print(f"{m}: done", flush=True)
    for run in args.runs:
        run_dir = RESULTS_DIR / "runs" / run
        cfg = run_config(run_dir)
        for item in args.set:   # evaluation-time overrides (e.g. observation noise)
            key, value = item.split("=", 1)
            set_by_path(cfg, key, yaml.safe_load(value))
        method = args.rl_label or "rl"
        tags = {"method": method, "run": run, "train_seed": cfg["train_seed"],
                "condition": args.condition, "split": args.split}
        rows += evaluate(rl_policy(run_dir), cfg, seeds, args.kind, tags)
        print(f"{run}: done", flush=True)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(out, index=False)
    print("wrote", out)


# ---------------------------------------------------------------------------- summary
def _seed_stats(per_seed: pd.Series) -> tuple[float, float]:
    """Mean and std over training seeds (std = 0 for deterministic baselines)."""
    return float(per_seed.mean()), float(per_seed.std(ddof=1)) if len(per_seed) > 1 else 0.0


def summarize(df: pd.DataFrame, ref: str = "straight", n_boot: int = 2000,
              unpaired: tuple[str, ...] = ("random",)) -> pd.DataFrame:
    """Paired summary per (condition, method).

    success: per-seed success rate -> mean/std over seeds; CI = bootstrap over maps of the
    seed-averaged per-map success. time/energy/path: on maps where EVERY method in the
    condition succeeds (strict pairing; for RL, every training seed); methods in ``unpaired``
    (sanity baselines such as random) do not restrict this map set. energy_ratio: per map
    energy / reference-method energy on maps where both succeed (RL: per seed).
    """
    out = []
    for cond, d in df.groupby("condition"):
        ok_all = d[~d.method.isin(unpaired)].groupby("map_seed")["success"].all()
        common = ok_all[ok_all].index
        ref_e = d[d.method == ref].set_index("map_seed")["energy_J"] if ref in set(d.method) else None
        ref_ok = d[d.method == ref].set_index("map_seed")["success"] if ref_e is not None else None
        for method, dm in d.groupby("method", sort=False):
            row: dict[str, Any] = {"condition": cond, "method": method, "n_seeds": dm.train_seed.nunique(),
                                   "n_maps": dm.map_seed.nunique(), "n_common_maps": len(common)}
            per_seed = dm.groupby("train_seed")["success"].mean()
            row["success_mean"], row["success_std"] = _seed_stats(per_seed)
            per_map = dm.groupby("map_seed")["success"].mean().values
            row["success_ci_lo"], row["success_ci_hi"] = bootstrap_ci(per_map, n_boot)
            for col, scale, name in (("time_s", 3600, "time_h"), ("energy_J", 1000, "energy_kJ"),
                                     ("path_m", 1000, "path_km")):
                dc = dm[dm.map_seed.isin(common) & dm.success]   # unpaired methods: own successes only
                seed_means = dc.groupby("train_seed")[col].mean() / scale
                row[f"{name}_mean"], row[f"{name}_std"] = _seed_stats(seed_means) if len(dc) else (np.nan, np.nan)
                pm = dc.groupby("map_seed")[col].mean().values / scale
                row[f"{name}_ci_lo"], row[f"{name}_ci_hi"] = bootstrap_ci(pm, n_boot)
            if ref_e is not None:
                dr = dm[dm.success & dm.map_seed.map(ref_ok).fillna(False).astype(bool)].copy()
                dr["ratio"] = dr.energy_J.values / dr.map_seed.map(ref_e).values
                seed_means = dr.groupby("train_seed")["ratio"].mean()
                row["energy_ratio_mean"], row["energy_ratio_std"] = _seed_stats(seed_means) if len(dr) else (np.nan, np.nan)
                row["energy_ratio_ci_lo"], row["energy_ratio_ci_hi"] = bootstrap_ci(
                    dr.groupby("map_seed")["ratio"].mean().values, n_boot)
                row["energy_ratio_n_maps"] = dr.map_seed.nunique()
            out.append(row)
    return pd.DataFrame(out)


def main() -> None:
    """CLI entry point."""
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", default=None)
    ap.add_argument("--split", default="val", choices=["train", "val", "test"])
    ap.add_argument("--kind", default=None, help="force field type, e.g. double_gyre")
    ap.add_argument("--methods", nargs="*", default=[], choices=BASELINES)
    ap.add_argument("--runs", nargs="*", default=[])
    ap.add_argument("--rl-label", default=None, help="method name for the RL runs (default 'rl')")
    ap.add_argument("--suffix", default="", help="appended to baseline method names, e.g. _r4")
    ap.add_argument("--condition", default="main")
    ap.add_argument("--set", nargs="*", default=[], help="config overrides a.b=value (applied to RL runs too)")
    ap.add_argument("--max-maps", type=int, default=0)
    ap.add_argument("--summarize", nargs="*", default=None, help="raw CSVs to summarise instead")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    if args.summarize:
        df = pd.concat([pd.read_csv(p) for p in args.summarize], ignore_index=True)
        s = summarize(df)
        s.to_csv(args.out, index=False)
        print(s.to_string())
    else:
        eval_cli(args)


if __name__ == "__main__":
    main()
