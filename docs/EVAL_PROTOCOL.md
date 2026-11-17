# Evaluation protocol (fixed before any test-map result was computed)

Written 2026-11-18 ~04:50 IST, while the main training runs were still running and before any
evaluation on test maps. Changing it later requires a note in docs/ASSUMPTIONS.md.

## Map splits (map seed -> field + start + goal, see `fields.make_task`)
- train: seeds 0-9999 (sampled uniformly at every reset during training)
- validation: seeds 10000-10099 (used for all design decisions: observation design, PPO sanity checks, planner look-ahead)
- test: seeds 100000-100199 (200 maps; used only for the final numbers below; never for training, tuning or model selection)
- held-out field: test seeds 100000-100199 with the field forced to the time-varying double gyre (never seen in training)

## Methods
- `straight`: nose at the goal every step (naive).
- `planner_time`: Dijkstra time-optimal plan + path follower.
- `planner_energy`: Dijkstra with the same time+energy weights as the RL reward + path follower.
- `rl`: PPO, deterministic actions (mean of the Gaussian policy), FINAL model after the full training budget (no checkpoint selection).
- `random` (sanity only).
All methods run in the same environment (same dynamics, turn limit, energy model, start heading). Episode seed = map seed.

## Training seeds
5 independent PPO training seeds (0-4) for the main configuration; 3 seeds (0-2) for each Pareto weight and ablation (compute budget).

## Metrics (per episode)
success (goal within 1 km before 400 steps and without leaving the domain), arrival time [h], energy [kJ], path length [km], energy ratio vs straight-line (same map).

## Aggregation (`evaluate.summarize`)
- success rate: per training seed over the 200 maps -> mean +/- std over training seeds; 95% CI = percentile bootstrap (2000 resamples) over maps of the seed-averaged per-map success.
- time / energy / path: only on maps where EVERY method in the comparison (every RL seed included) succeeds (strict pairing, identical maps); mean +/- std over training seeds; bootstrap CI over maps. The random policy (sanity check) is excluded from this pairing; amended 05:15 IST after the first summary showed that including it leaves only 4 common maps (no other number changed).
- energy ratio vs straight-line: per (seed, map) where both that method and straight-line succeed; mean +/- std over seeds; bootstrap CI over maps.
- Baselines are deterministic, so their seed std is 0.
- Raw per-episode rows: results/eval/*.csv. Summaries are generated from these files by `run_all.py`.

## Experiments
- 5a Pareto: w_energy/w_time in {0, 0.25, 1, 4, 16} (w_time + w_energy = 2) x 3 seeds; planner_energy evaluated with the same weights.
- 5b Ablations (3 seeds): no current observation; no energy term (w_energy = 0); trained on one fixed map (train seed 0) and tested on the test maps.
- 5c Robustness: main models evaluated with Gaussian current-observation noise std 0.05, 0.1, 0.2, 0.3 m/s (no retraining); all methods on the held-out double gyre.
