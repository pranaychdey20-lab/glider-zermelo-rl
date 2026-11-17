# Assumptions and deviations from docs/BUILD_SPEC.md

Every modelling choice that is not dictated by the spec, and every deviation, is listed here.

## Environment / tooling
- **torch wheel**: the PyTorch CPU index (download.pytorch.org) is blocked by this container's network policy, so torch 2.15.0 was installed from PyPI (CUDA build). It runs on CPU only (`torch.cuda.is_available() == False`). The `.venv` is 5.7 GB because of the unused CUDA libraries. On a laptop, `pip install torch --index-url https://download.pytorch.org/whl/cpu` is the lighter option.
- Python 3.13 (spec: 3.10+).

## Model
- **Energy model is an ASSUMPTION**: `e_step = (e_hotel + e_turn*|dh|/pi) * dt` with e_hotel = 0.5 W, e_turn = 5 W (so a 30 deg turn in one step costs 0.83 W extra, i.e. 2.7x the hotel power for that step). Units: W and J (reported in kJ). Real glider energy is dominated by the buoyancy pump and hotel load; heading changes are cheap. Consequence: in this model energy ~ hotel*time + turning, so energy and time are strongly correlated and the time/energy trade-off is mainly "how much turning".
- Initial heading points straight at the goal for every method (same start state).
- Heading changes are applied instantaneously at the start of a step; position is integrated with RK2 (midpoint), 2 sub-steps per 600 s step. A test shows RK2 error is < 10% of Euler's against a fine reference in a strong eddy.
- Goal reached = end-of-step position within 1 km. The glider moves <= ~520 m per step, so it cannot jump over the 2 km-wide goal disc.
- **Stream-function sign**: spec convention u = dpsi/dy, v = -dpsi/dx. With it, a positive psi bump spins counter-clockwise; `spin=+1` means counter-clockwise (positive vorticity). Tested.
- Eddies: Gaussian psi; "peak" is the maximum swirl speed (reached at r = R). Eddy centres are drawn in [-5, 55] km so eddies can sit partly outside the domain. Uniform drift magnitude uniform in [0, 0.05] m/s.
- Jet: meandering tanh-profile jet, core speed 0.2-0.5 m/s, width 3-6 km, random direction, meander amplitude <= 6 km, wavelength 20-50 km, centre line within +-10 km of the domain centre.
- Map mixture for train/val/test: 70% eddies, 30% jet, chosen from the map seed. Double gyre (Shadden-type, period 2 days, eps 0.1-0.3, peak 0.2-0.4 m/s, random phase and sign) is used ONLY as a held-out test field.
- Stream functions are evaluated analytically everywhere, including outside the domain (needed for the observation patch near walls).

## Environment / observation
- Observation adds **normalised position (x/L, y/L)** to the spec's list, because leaving the domain is a failure and the agent otherwise cannot see the walls. 60 entries total; layout documented in `src/glider_rl/env.py`.
- Patch: 5x5 samples, 2 km spacing (8 km x 8 km window), world-frame axes.
- Reward scales: T_scale = d0/V (still-water straight-line time of this episode), E_scale = e_hotel*T_scale. With w_time = w_energy = 1 the hotel energy term equals the time term numerically, so the energy term adds ~"time + turning".
- Shaping uses the spec's form k*(d_prev - d_now)/d0 (telescopes exactly in the undiscounted return), k = 5, goal bonus 5, out-of-domain and timeout penalty 5.
- "Straight-line" baseline = point the nose at the goal every step (subject to the 30 deg/step turn limit), no current compensation. This is the naive strategy the project wants to beat.

## Planner
- Grid 1 km, 16-connected, nodes kept >= 1 km from the walls; node state = (cell, arrival direction) so turning can be charged. Ground speed on an edge uses the current at the edge midpoint and the crab heading that cancels the cross-current; edges with |cross-current| > V or non-positive ground speed are removed.
- Energy-aware cost = w_time*T + w_energy*(T + (e_turn/e_hotel)*dt*|dh|/pi): the same time+energy objective as the RL reward. Turning is measured between the crab headings of consecutive edges (approximation).
- Execution: a look-ahead (2 km) path follower that computes the crab heading from the true local current (privileged information the RL agent only sees through its observation), subject to the same turn limit, dynamics and energy model as RL.
- Time-varying fields (double gyre): planned on a frozen snapshot, re-planned every `planner.replan_every` steps (only for time-varying fields).

## Changes made during the build (with reason)
- **Goal-frame observation (stage 3).** First quick PPO run (300k steps, world-frame observation) reached only ~5% training success (straight-line gets 65% on validation). Switching to a goal-aligned frame (heading relative to the goal bearing, currents as along/across-track components, patch axes aligned with the goal direction) gave ~75% training success within 200k steps. The observation still contains everything the spec lists (goal vector relative to the glider as distance + relative bearing, heading, local current, 5x5 patch, time, energy), plus world position and bearing so the walls are visible. 62 entries. Diagnostic logs kept in results/runs/diag_*.
- **Path-follower look-ahead** kept at 2 km: 3 km and 4 km were tried on VALIDATION maps; turning energy dropped only ~10% and success dropped (96% -> 94-95%).
- **PPO budget**: 2M steps per run (spec: "scale" after the 300k check). 8 envs (DummyVecEnv, single process), 1 torch thread per run, 4-5 runs in parallel on 4 cores. SB3 defaults otherwise, net [128,128], log_std_init 0 (log_std_init -1 was tried in the 300k check on validation and was not better: 73% vs 77% success).
- **Pareto sweep weights**: w_energy/w_time in {0, 0.25, 1, 4, 16} with w_time + w_energy = 2, so the total cost scale stays comparable to the progress shaping and terminal terms (otherwise large w_energy would make leaving the domain early attractive). Ratio 1 is the main config (w_time = w_energy = 1), so main seeds 0-2 are reused as that Pareto point.
- **Ablation "no energy term"** = main config with w_energy = 0 (w_time = 1); it differs from the Pareto ratio-0 point (w_time = 2) only by the time-weight scale.
- **Fixed-map ablation** trains on train map seed 0 only.
