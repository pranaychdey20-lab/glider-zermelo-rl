"""Static figures generated from saved raw results (CSV), never from live models."""
from __future__ import annotations

from pathlib import Path
from typing import Sequence

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

# Fixed method -> colour/marker mapping (validated categorical palette; markers are the
# secondary encoding so identity never relies on colour alone).
COLORS = {"straight": "#c62828", "planner_time": "#e07b00", "planner_energy": "#8e44ad", "rl": "#2e8b3e"}
MARKERS = {"straight": "s", "planner_time": "^", "planner_energy": "D", "rl": "o"}
LABELS = {"straight": "straight-line", "planner_time": "planner (time)",
          "planner_energy": "planner (energy)", "rl": "RL (PPO)"}
INK, GRID = "#333333", "#e6e6e6"


def family(method: str) -> str:
    """Base method name of a (possibly suffixed) method label, e.g. 'rl_r4' -> 'rl'."""
    for k in COLORS:
        if method == k or method.startswith(k + "_"):
            return k
    return "rl"


def _style(ax: plt.Axes) -> None:
    ax.grid(True, color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.tick_params(colors=INK, labelsize=8)


def training_curves(groups: dict[str, Sequence[Path]], out: Path, bin_steps: int = 100_000) -> None:
    """Training success rate and episode return vs steps; line = seed mean, band = +/- 1 std."""
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8), dpi=150)
    palette = ["#2e8b3e", "#1f5fa8", "#8e44ad", "#c62828", "#e07b00", "#6b6b6b"]
    for (label, runs), color in zip(groups.items(), palette):
        per_seed = []
        for r in runs:
            d = pd.read_csv(Path(r) / "episodes.csv")
            d["ret"] = d[["R_time", "R_energy", "R_progress", "R_terminal"]].sum(axis=1)
            d = d[d.timesteps < (d.timesteps.max() // bin_steps) * bin_steps]   # drop partial last bin
            d["bin"] = (d.timesteps // bin_steps + 1) * bin_steps
            per_seed.append(d.groupby("bin")[["success", "ret"]].mean())
        for ax, col in zip(axes, ("success", "ret")):
            m = pd.concat([p[col] for p in per_seed], axis=1)
            x = m.index.values / 1e6
            mean, std = m.mean(axis=1).values, m.std(axis=1).fillna(0).values
            ax.plot(x, mean, color=color, lw=2, label=f"{label} (n={len(runs)})")
            ax.fill_between(x, mean - std, mean + std, color=color, alpha=0.18, lw=0)
    axes[0].set_ylabel("training success rate", color=INK)
    axes[1].set_ylabel("training episode return", color=INK)
    for ax in axes:
        ax.set_xlabel("environment steps [millions]", color=INK)
        _style(ax)
    axes[0].legend(fontsize=7, frameon=False)
    fig.suptitle("PPO training (stochastic policy, training maps); band = +/-1 std over seeds", fontsize=9)
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)


def results_bars(summary: pd.DataFrame, condition: str, out: Path, title: str) -> None:
    """Small multiples: success, time, energy, energy ratio; error bars = bootstrap 95% CI over maps."""
    s = summary[(summary.condition == condition) & (summary.method != "random")]   # random: table only
    panels = [("success", "success rate", 1), ("time_h", "arrival time [h]\n(maps all methods solve)", 1),
              ("energy_kJ", "energy [kJ]\n(maps all methods solve)", 1),
              ("energy_ratio", "energy / straight-line energy\n(maps both solve)", 1)]
    fig, axes = plt.subplots(1, 4, figsize=(12, 3.6), dpi=150)
    x = np.arange(len(s))
    for ax, (col, label, _) in zip(axes, panels):
        mean = s[f"{col}_mean"].values
        err = np.abs(np.vstack([mean - s[f"{col}_ci_lo"].values, s[f"{col}_ci_hi"].values - mean]))
        colors = [COLORS[family(m)] for m in s.method]
        ax.bar(x, mean, width=0.6, color=colors, edgecolor="white", linewidth=2)
        ax.errorbar(x, mean, yerr=err, fmt="none", ecolor=INK, elinewidth=1, capsize=3)
        for xi, v in zip(x, mean):
            ax.annotate(f"{v:.2f}", (xi, 0), xytext=(0, 3), textcoords="offset points",
                        ha="center", fontsize=7, color="white", fontweight="bold")
        ax.set_xticks(x, [LABELS.get(m, m) for m in s.method], rotation=30, ha="right", fontsize=7)
        ax.set_title(label, fontsize=8, color=INK)
        _style(ax)
        if col == "energy_ratio":
            ax.axhline(1.0, color=INK, lw=0.8, ls="--")
    fig.suptitle(title, fontsize=9)
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)


def pareto_plot(summary: pd.DataFrame, condition: str, out: Path) -> None:
    """Time vs energy on the maps every Pareto method solves; RL error bars = std over seeds."""
    s = summary[summary.condition == condition]
    fig, ax = plt.subplots(figsize=(6.4, 4.8), dpi=150)
    for fam in ("rl", "planner_energy", "straight", "planner_time"):
        d = s[[family(m) == fam for m in s.method]].copy()
        if d.empty:
            continue
        d["ratio"] = [float(m.split("_r")[-1]) if "_r" in m else np.nan for m in d.method]
        d = d.sort_values("ratio")
        ax.errorbar(d.time_h_mean, d.energy_kJ_mean, xerr=d.time_h_std, yerr=d.energy_kJ_std,
                    color=COLORS[fam], marker=MARKERS[fam], ms=7, lw=1.5 if len(d) > 1 else 0,
                    capsize=2, label=LABELS[fam], mec="white")
        for _, r in d.iterrows():
            if not np.isnan(r.ratio):
                ax.annotate(f"{r.ratio:g}", (r.time_h_mean, r.energy_kJ_mean), xytext=(5, 4),
                            textcoords="offset points", fontsize=7, color=INK)
    ax.set_xlabel("mean arrival time [h]", color=INK)
    ax.set_ylabel("mean energy [kJ]", color=INK)
    ax.set_title(f"Time vs energy, labels = w_energy/w_time\n(n_common_maps = {int(s.n_common_maps.iloc[0])}; "
                 "RL bars = std over 3 seeds)", fontsize=8)
    _style(ax)
    ax.legend(fontsize=7, frameon=False)
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)


def robustness_plot(summary: pd.DataFrame, noise_levels: dict[str, float], out: Path) -> None:
    """Success rate vs observation-noise std; baselines use true currents so they are flat."""
    fig, ax = plt.subplots(figsize=(6, 4), dpi=150)
    rows = summary[summary.condition.isin(noise_levels)].copy()
    rows["noise"] = rows.condition.map(noise_levels)
    for fam in ("straight", "planner_time", "planner_energy", "rl"):
        d = rows[rows.method == fam].sort_values("noise")
        if d.empty:
            continue
        ax.errorbar(d.noise, d.success_mean, yerr=d.success_std, color=COLORS[fam], marker=MARKERS[fam],
                    lw=1.8, capsize=3, label=LABELS[fam], mec="white", ms=7)
    ax.set_xlabel("std of Gaussian noise on observed currents [m/s]", color=INK)
    ax.set_ylabel("success rate (test maps)", color=INK)
    ax.set_title("Robustness to noisy current observations (RL bars = std over seeds)", fontsize=8)
    _style(ax)
    ax.legend(fontsize=7, frameon=False)
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)
