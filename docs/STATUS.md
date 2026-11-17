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
