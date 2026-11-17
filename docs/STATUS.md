# Status

Updated: 2026-11-18 04:40 IST

## Tracks
- [ ] Track A (build): see docs/BUILD_SPEC.md
- [ ] Track B (literature): see literature/

## Track A checklist
- [x] Stage 0 setup (venv, deps, package skeleton, config)
- [x] Stage 1 fields, dynamics, straight-line baseline, tests, first animation
- [ ] Stage 2 classical planner
- [ ] Stage 3 gym env + PPO
- [ ] Stage 4 evaluation protocol
- [ ] Stage 5 experiments (Pareto, ablations, robustness)
- [ ] Stage 6 demos and figures, run_all.py
- [ ] Stage 7 handoff docs

## Log
(append entries below, newest last)
- 2026-11-17 22:58 UTC Track B: literature/ done - papers_table.md + papers.csv (30 verified via live search; direct page fetch blocked by network policy, see file), deep_read.md (S3, R1, R6 + glossary), novelty_check.md (benchmark-level claim only; 'first RL glider' is false).
- 2026-11-18 04:35 IST (23:05 UTC 17 Nov) Track A stage 0: venv (Python 3.13, torch 2.15 CPU-run from PyPI since the CPU wheel index is blocked), pyproject, configs/default.yaml, package skeleton.
- 2026-11-18 04:40 IST Track A stage 1: eddy/jet/double-gyre stream-function fields, RK2 dynamics, assumed energy model, gym env core, straight-line baseline, 27 tests pass, first animation results/figures/stage1_straight_line.gif (map 10006: straight-line captured by an eddy, timeout). Not done yet: planner, RL.
- 2026-11-18 04:45 IST Track A stage 2: grid Dijkstra planner (16-connected, (cell, arrival direction) state, crab-heading edge speeds, time-optimal and energy-aware costs) + look-ahead path follower; 8 planner tests. VALIDATION maps (100): success straight 65%, planner_time 96%, planner_energy 96%. On the 65 maps all succeed: mean time 25.9 h (straight) vs 23.1 h (both planners); energy 47.6 vs 45.3 / 45.2 kJ. Planner does NOT always win: slower than straight on 15/65 maps (12 of them by one 10-min step; 10025, 10044, 10083 by 1.2-1.5 h), and uses MORE energy than straight on 44/65 maps because its path follower turns ~5x more (turning energy ~6 kJ vs 1.2 kJ); energy-aware cost barely changes this. 4 maps defeat every method. Animation: results/figures/stage2_straight_vs_planner.gif (map 10006).
- 2026-11-18 05:00 IST (23:30 UTC) Track A stage 3: GliderEnv passes gymnasium check_env; 7 env tests (reward bookkeeping, shaping telescopes, circling gives negative return, seeded noise). Quick 300k PPO check: world-frame observation reached ~5% training success, so the observation was changed to a goal-aligned frame (ASSUMPTIONS.md) -> 77% success on validation maps (straight 65%, planner 96%). Scaled: 5 seeds x 2M steps (8 envs, CPU, ~19 min/run with 5 in parallel). Training success (stochastic policy) rises from ~74% in the first 250k steps to 80-83% at 2M for all 5 seeds; it is still below the planner. Logs: results/runs/main_s*/episodes.csv, progress.csv. Note: a git autostash replaced the open log files mid-run; episodes.csv/progress.csv were recovered in full from /proc, but the TensorBoard event files of main_s* are incomplete.
