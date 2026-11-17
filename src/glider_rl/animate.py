"""Animations of glider trajectories over current streamlines (GIF + MP4)."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Sequence

import imageio.v2 as imageio
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from .fields import Task  # noqa: E402

KM = 1000.0


def draw_field(ax: plt.Axes, task: Task, cfg: dict[str, Any], t: float = 0.0, n: int = 60) -> None:
    """Speed colour map + streamlines of the field at time ``t``, start/goal markers."""
    L = cfg["domain"]["size_m"]
    xs = np.linspace(0, L, n)
    X, Y = np.meshgrid(xs, xs, indexing="xy")
    u, v = task.field.velocity(X, Y, t)
    ax.pcolormesh(X / KM, Y / KM, np.hypot(u, v), cmap="Blues", vmin=0, vmax=0.6, shading="auto", alpha=0.6)
    ax.streamplot(X / KM, Y / KM, u, v, color="0.45", density=1.1, linewidth=0.6, arrowsize=0.7)
    ax.plot(*task.start / KM, "ko", ms=8, label="start")
    ax.add_patch(plt.Circle(task.goal / KM, cfg["domain"]["goal_radius_m"] / KM, color="gold", zorder=5))
    ax.plot(*task.goal / KM, "k*", ms=12, label="goal", zorder=6)
    ax.set_xlim(0, L / KM)
    ax.set_ylim(0, L / KM)
    ax.set_aspect("equal")
    ax.set_xlabel("x [km]")
    ax.set_ylabel("y [km]")


def animate_runs(task: Task, runs: Sequence[dict[str, Any]], cfg: dict[str, Any], out_stem: Path,
                 title: str = "", fps: int = 12, max_frames: int = 90, mp4: bool = True) -> list[Path]:
    """Animate several runs on one map.

    Each run: {"label", "color", "traj" (N+1, 2) [m], "energy_trace" (N+1,) [J], "reason"}.
    Writes ``out_stem``.gif (and .mp4); returns the written paths.
    """
    dt = cfg["glider"]["dt_s"]
    n_max = max(len(r["traj"]) for r in runs)
    frame_every = max(1, int(np.ceil(n_max / max_frames)))
    frames_idx = list(range(0, n_max, frame_every)) + [n_max - 1] * 6     # hold last frame
    fig, (ax, axp) = plt.subplots(1, 2, figsize=(9.6, 5.4), gridspec_kw={"width_ratios": [3, 1.4]}, dpi=80)
    draw_field(ax, task, cfg)
    ax.set_title(title, fontsize=10)
    lines, dots = [], []
    for r in runs:
        (ln,) = ax.plot([], [], color=r["color"], lw=2.2, label=r["label"])
        (dot,) = ax.plot([], [], "o", color=r["color"], ms=6, mec="k")
        lines.append(ln)
        dots.append(dot)
    ax.legend(loc="upper left", fontsize=7, framealpha=0.8)
    axp.axis("off")
    txt = axp.text(0.0, 0.98, "", va="top", family="monospace", fontsize=8.5, transform=axp.transAxes)
    frames = []
    for i in frames_idx:
        rows = [f"t = {i * dt / 3600:5.1f} h\n"]
        for r, ln, dot in zip(runs, lines, dots):
            k = min(i, len(r["traj"]) - 1)
            ln.set_data(r["traj"][: k + 1, 0] / KM, r["traj"][: k + 1, 1] / KM)
            dot.set_data([r["traj"][k, 0] / KM], [r["traj"][k, 1] / KM])
            done = k == len(r["traj"]) - 1
            status = r.get("reason", "") if done else "running"
            rows.append(f"{r['label']}\n  time   {k * dt / 3600:5.1f} h\n"
                        f"  energy {r['energy_trace'][k] / 1000:5.1f} kJ\n  {status}\n")
        txt.set_text("\n".join(rows))
        fig.canvas.draw()
        frames.append(np.asarray(fig.canvas.buffer_rgba())[..., :3].copy())
    plt.close(fig)
    out_stem = Path(out_stem)
    out_stem.parent.mkdir(parents=True, exist_ok=True)
    paths = [out_stem.with_suffix(".gif")]
    imageio.mimsave(paths[0], frames, duration=1000 / fps, loop=0)
    if mp4:
        paths.append(out_stem.with_suffix(".mp4"))
        imageio.mimsave(paths[1], frames, fps=fps, macro_block_size=8)
    return paths


STYLE = {"straight": ("straight-line", "#c62828"), "planner_time": ("planner (time)", "#e07b00"),
         "planner_energy": ("planner (energy)", "#8e44ad"), "rl": ("RL (PPO)", "#2e8b3e")}


def record_runs(map_seed: int, methods: Sequence[str], cfg: dict[str, Any], rl_run: str | None = None,
                kind: str | None = None) -> tuple[Task, list[dict[str, Any]]]:
    """Roll out methods on one map with trajectory recording ('rl' needs ``rl_run``)."""
    from .baselines import run_episode
    from .env import GliderEnv
    from .evaluate import baseline_policy, rl_policy
    from .utils import RESULTS_DIR

    env = GliderEnv(cfg, kind=kind, map_seeds=np.array([map_seed]), record=True)
    runs = []
    for m in methods:
        pol = rl_policy(RESULTS_DIR / "runs" / rl_run) if m == "rl" else baseline_policy(m, cfg)
        res = run_episode(env, pol, map_seed, seed=map_seed)
        label, color = STYLE[m]
        runs.append({**res, "label": label, "color": color, "method": m})
    return env.task, runs


def save_runs(path: Path, map_seed: int, kind: str, runs: list[dict[str, Any]], note: str = "") -> None:
    """Save recorded trajectories so animations can be re-rendered without any model."""
    path.parent.mkdir(parents=True, exist_ok=True)
    arrays = {}
    for r in runs:
        arrays[f"{r['method']}__traj"] = r["traj"]
        arrays[f"{r['method']}__energy"] = r["energy_trace"]
        arrays[f"{r['method']}__reason"] = np.array(r["reason"])
    np.savez_compressed(path, map_seed=map_seed, kind=kind, methods=np.array([r["method"] for r in runs]),
                        note=np.array(note), **arrays)


def load_runs(path: Path, cfg: dict[str, Any]) -> tuple[Task, list[dict[str, Any]], str]:
    """Inverse of ``save_runs``; the map is rebuilt from its seed and field kind."""
    from .fields import make_task

    z = np.load(path)
    task = make_task(int(z["map_seed"]), cfg, str(z["kind"]))
    runs = []
    for m in z["methods"]:
        m = str(m)
        label, color = STYLE[m]
        runs.append({"method": m, "label": label, "color": color, "traj": z[f"{m}__traj"],
                     "energy_trace": z[f"{m}__energy"], "reason": str(z[f"{m}__reason"])})
    return task, runs, str(z["note"])


def render_saved(path: Path, cfg: dict[str, Any], out_dir: Path) -> list[Path]:
    """Render a saved trajectory file to GIF + MP4 in ``out_dir``."""
    task, runs, note = load_runs(path, cfg)
    title = f"map {task.seed} ({task.kind}) {note}".strip()
    return animate_runs(task, runs, cfg, out_dir / Path(path).stem, title)


def main() -> None:
    """CLI: record trajectories (needs models for 'rl') or render saved ones (no model)."""
    import argparse

    from .utils import RESULTS_DIR, load_config

    ap = argparse.ArgumentParser(description=main.__doc__)
    ap.add_argument("--config", default=None)
    ap.add_argument("--map", type=int, default=10003)
    ap.add_argument("--kind", default=None)
    ap.add_argument("--methods", nargs="+", default=["straight", "planner_time"])
    ap.add_argument("--rl-run", default=None, help="results/runs/<name> to use for method 'rl'")
    ap.add_argument("--note", default="")
    ap.add_argument("--save", default=None, help="save trajectories to this .npz instead of rendering")
    ap.add_argument("--render", nargs="*", default=None, help=".npz files to render")
    ap.add_argument("--out", default=str(RESULTS_DIR / "figures" / "baselines"))
    args = ap.parse_args()
    cfg = load_config(args.config)
    if args.render is not None:
        for f in args.render:
            for p in render_saved(Path(f), cfg, Path(args.out)):
                print("wrote", p)
        return
    task, runs = record_runs(args.map, args.methods, cfg, args.rl_run, args.kind)
    if args.save:
        save_runs(Path(args.save), args.map, task.kind, runs, args.note)
        print("saved", args.save, [(r["method"], r["reason"]) for r in runs])
        return
    title = f"map {args.map} ({task.kind}) {args.note}".strip()
    for p in animate_runs(task, runs, cfg, Path(args.out), title):
        print("wrote", p)


if __name__ == "__main__":
    main()
