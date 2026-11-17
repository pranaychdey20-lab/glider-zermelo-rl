"""Record demo trajectories (needs trained models) into results/trajectories/*.npz.

Selection rule (fixed in advance, validation maps only, model = main_s0, i.e. training
seed 0, not the best seed):
  * 3-way demo: first validation map (seed order) where straight-line fails and both
    the time-optimal planner and RL succeed.
  * failure demo: first validation map where RL fails.
  * held-out demo: first test map (100000) with the double-gyre field, no selection.
Usage: python scripts/record_demos.py [--rl-run main_s0]
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from glider_rl.animate import record_runs, save_runs  # noqa: E402
from glider_rl.utils import RESULTS_DIR, load_config, split_seeds  # noqa: E402

METHODS = ["straight", "planner_time", "rl"]


def main() -> None:
    """Find demo maps by the fixed rule and save their trajectories."""
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--rl-run", default="main_s0")
    args = ap.parse_args()
    cfg = load_config()
    out = RESULTS_DIR / "trajectories"
    found_demo = found_fail = False
    for m in split_seeds(cfg, "val"):
        task, runs = record_runs(int(m), METHODS, cfg, args.rl_run)
        ok = {r["method"]: r["success"] for r in runs}
        if not found_demo and not ok["straight"] and ok["planner_time"] and ok["rl"]:
            save_runs(out / f"demo_3way_val{m}.npz", int(m), task.kind, runs, "(validation map)")
            found_demo = True
            print("3-way demo map", m)
        if not found_fail and not ok["rl"]:
            save_runs(out / f"demo_rl_failure_val{m}.npz", int(m), task.kind, runs, "(RL failure case)")
            found_fail = True
            print("failure demo map", m)
        if found_demo and found_fail:
            break
    m = int(split_seeds(cfg, "test")[0])
    task, runs = record_runs(m, METHODS, cfg, args.rl_run, kind="double_gyre")
    save_runs(out / f"demo_heldout_gyre_test{m}.npz", m, task.kind, runs, "(held-out field)")
    models = RESULTS_DIR / "models"
    models.mkdir(exist_ok=True)
    shutil.copy(RESULTS_DIR / "runs" / args.rl_run / "model.zip", models / f"{args.rl_run}.zip")


if __name__ == "__main__":
    main()
