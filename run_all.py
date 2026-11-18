"""Reproduce every table, figure and animation from saved raw results.

    python run_all.py            # no model needed: CSVs + trajectories -> summaries, figures, GIF/MP4
    python run_all.py --evaluate # re-run all evaluations from trained models (results/runs/*/model.zip)
    python run_all.py --full     # retrain everything, re-evaluate, re-record demos, then regenerate

Raw inputs: results/eval/*.csv (one row per episode), results/runs/*/episodes.csv
(training logs), results/trajectories/*.npz (recorded demo trajectories).
Outputs: results/summary.csv (main test table), results/summary_all.csv (every condition),
results/paired_ratios.csv (per-map RL / baseline energy and time ratios),
results/figures/*.png|gif|mp4.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from glider_rl import plots  # noqa: E402
from glider_rl.animate import render_saved  # noqa: E402
from glider_rl.evaluate import paired_ratios, summarize  # noqa: E402
from glider_rl.experiments import PARETO_RATIOS, pareto_weights  # noqa: E402
from glider_rl.utils import load_config  # noqa: E402

RES = ROOT / "results"
EVAL = RES / "eval"
FIG = RES / "figures"
NOISE = (0.05, 0.1, 0.2, 0.3)
MAIN_SEEDS = range(5)
SUB_SEEDS = range(3)


def ev(*args: str) -> list[str]:
    """Command line of one evaluation job."""
    return [sys.executable, "-m", "glider_rl.evaluate", "--split", "test", *args]


def eval_jobs() -> list[list[str]]:
    """Every evaluation behind the reported numbers (test maps only)."""
    main_runs = [f"main_s{s}" for s in MAIN_SEEDS]
    jobs = [
        ev("--methods", "straight", "planner_time", "planner_energy", "random", "--condition", "main",
           "--out", str(EVAL / "test_main_baselines.csv")),
        ev("--runs", *main_runs, "--condition", "main", "--out", str(EVAL / "test_main_rl.csv")),
        ev("--kind", "double_gyre", "--methods", "straight", "planner_time", "planner_energy",
           "--condition", "double_gyre", "--out", str(EVAL / "test_gyre_baselines.csv")),
        ev("--kind", "double_gyre", "--runs", *main_runs, "--condition", "double_gyre",
           "--out", str(EVAL / "test_gyre_rl.csv")),
    ]
    for sd in NOISE:
        jobs.append(ev("--runs", *main_runs, "--condition", f"noise_{sd:g}", "--set", f"env.obs_noise_std_mps={sd}",
                       "--out", str(EVAL / f"test_noise{sd:g}_rl.csv")))
    for r in PARETO_RATIOS:
        wt, we = pareto_weights(r)
        runs = [f"main_s{s}" for s in SUB_SEEDS] if r == 1.0 else [f"pareto_r{r:g}_s{s}" for s in SUB_SEEDS]
        jobs.append(ev("--runs", *runs, "--rl-label", f"rl_r{r:g}", "--condition", "pareto",
                       "--out", str(EVAL / f"test_pareto_r{r:g}_rl.csv")))
        jobs.append(ev("--methods", "planner_energy", "--suffix", f"_r{r:g}", "--condition", "pareto",
                       "--set", f"env.reward.w_time={wt}", f"env.reward.w_energy={we}",
                       "--out", str(EVAL / f"test_pareto_r{r:g}_planner.csv")))
    for abl in ("nocurrent", "noenergy", "fixedmap"):
        jobs.append(ev("--runs", *[f"abl_{abl}_s{s}" for s in SUB_SEEDS], "--rl-label", f"rl_{abl}",
                       "--condition", "ablations", "--out", str(EVAL / f"test_abl_{abl}.csv")))
    jobs.append(ev("--runs", *[f"main_s{s}" for s in SUB_SEEDS], "--condition", "ablations",
                   "--out", str(EVAL / "test_abl_main_rl.csv")))
    jobs.append(ev("--runs", *[f"long_s{s}" for s in MAIN_SEEDS], "--rl-label", "rl_long", "--condition", "long",
                   "--out", str(EVAL / "test_long_rl.csv")))   # extra experiment (6M steps)
    jobs.append(ev("--runs", *[f"stable_s{s}" for s in MAIN_SEEDS], "--rl-label", "rl_stable",
                   "--condition", "stable", "--out", str(EVAL / "test_stable_rl.csv")))   # extra 2
    return jobs


def load(*names: str, condition: str | None = None) -> pd.DataFrame:
    """Concatenate raw CSVs (optionally relabelling their condition)."""
    frames = [pd.read_csv(EVAL / n) for n in names if (EVAL / n).exists()]
    if not frames:
        return pd.DataFrame(columns=["method", "condition", "map_seed", "train_seed", "success"])
    df = pd.concat(frames, ignore_index=True)
    if condition:
        df["condition"] = condition
    return df


def summaries(n_boot: int) -> pd.DataFrame:
    """Build every summary table from raw CSVs."""
    base = load("test_main_baselines.csv")
    base_nr = base[base.method != "random"]
    parts = [load("test_main_baselines.csv", "test_main_rl.csv"),
             load("test_gyre_baselines.csv", "test_gyre_rl.csv")]
    for sd in NOISE:   # baselines read true currents: their rows are the noise-free ones
        parts.append(pd.concat([base_nr.assign(condition=f"noise_{sd:g}"),
                                load(f"test_noise{sd:g}_rl.csv")], ignore_index=True))
    pareto = [f"test_pareto_r{r:g}_{k}.csv" for r in PARETO_RATIOS for k in ("rl", "planner")]
    parts.append(pd.concat([base[base.method == "straight"].assign(condition="pareto"),
                            load(*pareto, condition="pareto")], ignore_index=True))
    abl = [f"test_abl_{a}.csv" for a in ("nocurrent", "noenergy", "fixedmap")] + ["test_abl_main_rl.csv"]
    parts.append(pd.concat([base_nr.assign(condition="ablations"), load(*abl, condition="ablations")],
                           ignore_index=True))
    parts.append(pd.concat([base_nr.assign(condition="long"), load("test_main_rl.csv", condition="long"),
                            load("test_long_rl.csv")], ignore_index=True))
    parts.append(pd.concat([base_nr.assign(condition="stable"), load("test_main_rl.csv", condition="stable"),
                            load("test_stable_rl.csv")], ignore_index=True))
    out = []
    for p in parts:
        if not p.empty and (p.method.str.startswith("rl_").any() or p.condition.iloc[0] in ("main", "double_gyre")
                            or p.condition.iloc[0].startswith("noise")):
            out.append(summarize(p, n_boot=n_boot))
    s = pd.concat(out, ignore_index=True)
    rl = load("test_main_baselines.csv", "test_main_rl.csv", "test_stable_rl.csv", "test_long_rl.csv")
    pairs = [paired_ratios(rl, m, ref, n_boot) for m in ("rl", "rl_stable", "rl_long")
             for ref in ("planner_energy", "planner_time", "straight") if (rl.method == m).any()]
    pd.DataFrame(pairs).to_csv(RES / "paired_ratios.csv", index=False)
    s.to_csv(RES / "summary_all.csv", index=False)
    main = s[s.condition == "main"]
    main.to_csv(RES / "summary.csv", index=False)
    return s


def figures(s: pd.DataFrame, cfg: dict) -> None:
    """All static figures and animations."""
    FIG.mkdir(parents=True, exist_ok=True)
    runs = RES / "runs"
    groups = {"main (w_t=w_e=1)": sorted(runs.glob("main_s*"))}
    for a in ("nocurrent", "noenergy"):   # fixed-map runs train on one map: not comparable, omitted
        groups[f"ablation: {a}"] = sorted(runs.glob(f"abl_{a}_s*"))
    groups = {k: [p for p in v if (p / "episodes.csv").exists()] for k, v in groups.items()}
    groups = {k: v for k, v in groups.items() if v}
    if groups:
        plots.training_curves(groups, FIG / "training_curves.png")
    titles = {"main": "Test maps (200, eddies + jets); RL = 5 training seeds",
              "double_gyre": "Held-out time-varying double gyre (200 test maps); RL = 5 seeds",
              "ablations": "Ablations on test maps (RL variants: 3 seeds each)",
              "long": "Extra: RL trained 2M (rl) vs 6M steps (rl_long), 5 seeds each, test maps",
              "stable": "Extra: RL main (rl) vs LR decay + target KL (rl_stable), 2M steps, 5 seeds each"}
    for cond, title in titles.items():
        if (s.condition == cond).any():
            plots.results_bars(s, cond, FIG / f"results_{cond}.png", title)
    if (s.condition == "pareto").any():
        plots.pareto_plot(s, "pareto", FIG / "pareto.png")
    levels = {"main": 0.0, **{f"noise_{sd:g}": sd for sd in NOISE}}
    if s.condition.str.startswith("noise").any():
        plots.robustness_plot(s, levels, FIG / "robustness_noise.png")
    for npz in sorted((RES / "trajectories").glob("*.npz")):
        for p in render_saved(npz, cfg, FIG):
            print("wrote", p)


def main() -> None:
    """CLI entry point."""
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--evaluate", action="store_true", help="re-run evaluations from trained models")
    ap.add_argument("--full", action="store_true", help="retrain + re-evaluate + re-record demos")
    args = ap.parse_args()
    py = sys.executable
    if args.full:
        subprocess.run([py, "-m", "glider_rl.experiments", "--group", "main", "pareto", "ablations"], check=True)
        subprocess.run([py, str(ROOT / "scripts" / "record_demos.py")], check=True)
    if args.full or args.evaluate:
        for job in eval_jobs():
            print(" ".join(job[2:]), flush=True)
            subprocess.run(job, check=True)
    cfg = load_config()
    s = summaries(cfg["eval"]["n_bootstrap"])
    print(s[s.condition == "main"].to_string())
    figures(s, cfg)


if __name__ == "__main__":
    main()
