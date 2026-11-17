# LEARN: teaching notes, one section per stage

## Stage 0: setup

**What was built.** A Python package `glider_rl` (in `src/`), a config file `configs/default.yaml` that holds every number the code uses, a test folder, and a virtual environment with numpy/scipy/gymnasium/stable-baselines3/torch. Nothing is hard-coded: change the YAML (or pass `key=value` overrides) and the whole pipeline follows.

**Key idea.** Reproducibility = same code + same config + same seed => same numbers. Every random map is generated from an integer seed with `numpy.random.default_rng([seed, stream])`.

**Change this and watch.** `python -c "from glider_rl.fields import make_task; from glider_rl.utils import load_config; print(make_task(5, load_config()).start)"` twice: identical output. Change 5 to 6: different start.

**Explain it back.**
1. Why put all numbers in a YAML file rather than in the code?
2. What would break if map generation used the global `np.random` state?
3. Why is the venv not committed to git?

## Stage 1: currents, glider motion, straight-line baseline

**What was built.** Three kinds of synthetic ocean currents (Gaussian eddies + weak drift, a meandering jet, and a time-varying double gyre kept for testing only), the glider motion model, the energy model, and the naive "point at the goal" baseline, plus the first animation (`results/figures/stage1_straight_line.gif`, the glider gets captured by an eddy and times out).

**Key equations.**
- Stream function -> current: `u = dpsi/dy, v = -dpsi/dx`. Any such field has zero divergence (`du/dx + dv/dy = psi_yx - psi_xy = 0`), i.e. water is not created or destroyed.
- Glider: `ground velocity = V (cos h, sin h) + current`.
- Worked example: V = 0.3 m/s heading east (h = 0), current (0, 0.2) m/s north. Ground velocity = (0.3, 0.2), speed 0.36 m/s, track 33.7 deg north of east. In one 600 s step the glider moves (180 m, 120 m). Energy that step with no turn: 0.5 W * 600 s = 300 J.
- Eddy: `psi = A exp(-r^2/2R^2)`; swirl speed peaks at r = R with value A/(R sqrt(e)). Positive A spins counter-clockwise with this sign convention.

**Change this and watch.** In `configs/default.yaml` set `fields.eddies.peak_max_mps: 0.15` (weak eddies) and rerun `python -m glider_rl.animate --map 10006 --methods straight --out results/figures/try`. The straight-line glider now reaches the goal: the baseline only fails when currents are comparable to the glider speed.

**Explain it back.**
1. Why does a stream function guarantee a divergence-free field?
2. A current of 0.4 m/s blows exactly sideways to the glider's desired track. Can the glider hold that track? Why?
3. Why does "point at the goal" fail in a strong eddy even though it always aims correctly?

---
### Answers
Stage 0: (1) one place to change, experiments are recorded, no hidden constants. (2) results would depend on call order, so the same seed would not give the same map. (3) it is large, machine-specific and rebuilt from requirements.txt.

Stage 1: (1) divergence = d/dx(dpsi/dy) + d/dy(-dpsi/dx) = 0 because mixed partial derivatives are equal. (2) No: to cancel a 0.4 m/s cross-current it needs a cross component of 0.4 m/s but its total speed is only 0.3 m/s. (3) Aiming is not the same as moving: the current adds a velocity the glider never compensates for, so it is swept around the eddy and its heading keeps chasing a goal it cannot approach.
