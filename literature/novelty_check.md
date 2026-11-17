# Novelty check: is there already an open-source RL glider/AUV navigation environment in ocean currents?

Date of search: 2026-11-17/18 (UTC). Paper IDs (R7, C6, ...) refer to `papers_table.md`.

## How I searched

- **GitHub:** repository search through the GitHub API (this worked from the container). About 30 queries, including: `underwater glider reinforcement learning`, `glider ocean current reinforcement`, `auv ocean current reinforcement learning`, `zermelo reinforcement learning`, `zermelo navigation`, `zermelo ppo`, `navigation vortical flow reinforcement`, `flow navigation reinforcement learning`, `energy efficient navigation flow`, `navigation double gyre`, `double gyre reinforcement`, `ocean currents path planning rl`, `auv gym environment`, `underwater gymnasium`, `stable-baselines3 ocean`, `hycom reinforcement`, `microswimmer reinforcement`, `glider path planning`, `underwater glider`, `MarineGym`, `OceanPlatformControl`. For each relevant hit I read the README via raw.githubusercontent.com.
- **Web:** live web search for papers that ship code or describe environments (results in `papers_table.md`). Direct publisher/arXiv page fetches were blocked by the container's network policy, so web items were checked through the record pages returned by search.
- **Limits:** GitHub search only matches names/descriptions/topics, not code. Repos with poor descriptions, GitLab/Zenodo code and supplementary files of papers can be missed. Treat "not found" as "not found by this search", not "does not exist".

## What I found

### A. Closest: RL navigation in 2-D flows with public code

| Repo / paper | What it is (from README / record page) | Overlap with this project | What it lacks relative to this project |
|---|---|---|---|
| [piao233/FieldNav-LASS](https://github.com/piao233/FieldNav-LASS) (official code of **R7**, Zhang et al. 2025, Ocean Engineering 327:120937) | PPO agent + learned flow-prediction network ("look-ahead state space") for Zermelo-type point-to-point navigation when the agent is slower than the flow. Double-gyre and cylinder-flow environments. README reports success rates, e.g. double gyre 69.23% (base) vs 95.45% (true LASS) vs 94.90% (predicted LASS). | **High**: PPO, double gyre, slower-than-flow agent, Zermelo framing. | No explicit energy model or time-energy trade-off seen in the README; no classical graph-planner baseline seen; flows are fixed datasets (.mat), not procedurally generated per seed. |
| [GTI-UFMG/lat2026-rl-flow](https://github.com/GTI-UFMG/lat2026-rl-flow) ("Energy-efficient navigation in unknown static flow fields using RL", Alves Neto, Campos, Macharet; conference submission) | 2-D navigation with obstacles from a binary map, vortex-like flow sources, cost based on flow exposure; Sarsa, Q-learning, DQN, Dueling DQN. | **Medium-high**: "energy-efficient" RL navigation in flow fields. | Static flow; "energy" is exposure to flow intensity, not vehicle energy; no PPO/continuous heading, no planner baseline listed, not glider-scale. |
| [Kismet22/HRL-FlowNavigation-ObstacleAvoidance](https://github.com/Kismet22/HRL-FlowNavigation-ObstacleAvoidance) | Hierarchical RL for navigation and obstacle avoidance in unsteady vortical flows; includes an end-to-end PPO baseline. Paper DOI "to be added". | Medium: PPO in unsteady vortical flows. | Fluid-structure, cylinder-type scenarios; no energy-time trade-off or glider model described. |
| [anandk97/rl-swimmer](https://github.com/anandk97/rl-swimmer) | Custom Gym environments for a microswimmer in 2-D turbulence; DQN vs naive "point at target" controller. | Medium: Gym env + flow navigation + naive baseline. | Microswimmer scale, discrete DQN, no energy model or planner. |
| [lauraachoquett/microswimmer_internship](https://github.com/lauraachoquett/microswimmer_internship) | Flow-aware path planner + RL tracking policy for microswimmers (2-D; 3-D in a sister repo). | Medium: planner + RL in flows. | Microswimmer; RL follows the planner's path rather than competing with it. |
| [feizhanxia/Greenhand_QLearning](https://github.com/feizhanxia/Greenhand_QLearning) | Notes + reproduction of "Flow navigation by smart microswimmers via RL" (tabular Q-learning). | Low. | Tutorial-level. |
| [VinamrJain/zermelo](https://github.com/VinamrJain/zermelo) | "Ongoing work" research package for Zermelo navigation with an *unknown* field (balloons on ERA5 winds, ocean drifters). The agent also outputs a belief about the field. MIT licence. | Medium: Zermelo framing, unknown flows. | Focus is field estimation/belief, aerial/drifter examples; no glider energy model seen. |
| **R10** Braghin et al. 2026 (arXiv:2607.13553) | TD3 in a parametric chaotic double gyre; velocity-aware agents more energy-efficient. | **High** on idea (energy, double gyre, RL). | Code not found by my search; abstract mentions no classical-planner baseline. |
| **R8** Gadhvi & Manjanna 2025 (arXiv:2512.06912) | SAC with local velocity sensing; energy-efficient surface vehicle in vortical flows. | High on idea (energy-aware RL in flows). | Code not found by my search; surface vehicle; preprint. |

### B. AUV/underwater RL environments (not current-exploiting route planning)

| Repo | What it is | Why it is not the same |
|---|---|---|
| [Marine-RL/MarineGym](https://github.com/Marine-RL/MarineGym) (IROS 2025, arXiv:2503.09203) | GPU-parallel RL framework on Isaac Sim/OmniDrones for UUV control tasks; high step throughput. | 6-DoF vehicle control, needs Isaac Sim + NVIDIA GPU; not a large-scale current-field routing task. |
| [OceanGPT/OceanGym](https://github.com/OceanGPT/OceanGym) | Embodied underwater benchmark (perception + navigation) with water-flow simulation. | Perception/LLM-agent benchmark; not energy-aware routing in mesoscale currents. |
| [narcispr/gym_auv](https://github.com/narcispr/gym_auv) | Gymnasium AUV docking environment with currents (~30 m scale). | Docking manoeuvre, not long-range navigation. |
| [camillasterud/gym-auv](https://github.com/camillasterud/gym-auv) | Gym environment for AUV collision avoidance and path following (from repo description; README not retrieved). | Path following/collision avoidance, not currents. |
| [gokulp01/bluerov2_gym](https://github.com/gokulp01/bluerov2_gym) | Gymnasium BlueROV2 dynamics with disturbances, SB3-compatible. | ROV control, small scale. |
| [Blackcipher101/rov-rl-mujoco](https://github.com/Blackcipher101/rov-rl-mujoco) | MuJoCo ROV, Brax PPO vs classical controllers, includes a 0.2 m/s current in one task. | ROV, obstacle avoidance; current is a disturbance, not something to exploit. |
| [warplab/isaac-auv-env](https://github.com/warplab/isaac-auv-env), [Erikx3/gym_dockauv](https://github.com/Erikx3/gym_dockauv) | IsaacLab AUV env; AUV docking env. | Control/docking. |

### C. Glider simulators / planners without RL

| Repo / paper | What it is |
|---|---|
| [YogangSingh/2D-Simulations-Underwater-Glider-Motion](https://github.com/YogangSingh/2D-Simulations-Underwater-Glider-Motion) | MATLAB vertical-plane glider equations of motion after Graver (2005). |
| [Bhaswanth-A/AUG-Simulator](https://github.com/Bhaswanth-A/AUG-Simulator) | Python 2-D/3-D glider motion simulator with PID pitch/rudder control. |
| [grande-dev/OpenMAUVe](https://github.com/grande-dev/OpenMAUVe) | OpenModelica simulator for AUVs, gliders and hybrids (description only). |
| [amp-at-clover/gpplib](https://github.com/amp-at-clover/gpplib) | "Glider Path Planning library" (last pushed 2014; description only). |
| [RAPID-route/RAPID-route.github.io](https://github.com/RAPID-route/RAPID-route.github.io) | Project page for an Ocean Engineering paper: GPU differential-evolution planner for gliders in time-varying currents with 3-D seabed avoidance (no RL). |
| [MariusWiggert/OceanPlatformControl](https://github.com/MariusWiggert/OceanPlatformControl) | Code from the Berkeley/MIT line of work on low-power ocean platforms riding forecast currents (hj_reachability-based; README shows set-up instructions only). Related papers: Killer et al. 2023, Doering et al. 2023 (further reading). |
| **R9** Darvariu et al. 2026 | Real Slocum-glider MCTS planner over 3 months / 1000 km (no code found by my search). |

### D. Glider + deep RL papers (no code found)

Two Ocean Engineering papers on DRL path planning for underwater gliders in time-varying/uncertain currents (2022, 2024) and a cited SAC-on-forecasts glider paper (Gao) exist (see UNVERIFIED in `papers_table.md`). I found **no public code** for them. Their existence alone means **"first RL for underwater gliders in currents" is false**.

## Verdict: what the project can and cannot honestly claim

**Cannot claim (already done by others):**
- "First use of RL for underwater-glider path planning in ocean currents" (Ocean Engineering 2022/2024 glider DRL papers; Gao, as cited in R9).
- "First RL solution of the Zermelo problem" (C10, R2, R1).
- "First PPO agent in a double gyre" (R7, which also has public code).
- "First energy-aware RL navigation in flows" (R8, R10, R4).
- Any claim that RL beats classical planning in general (R6 shows the field's results are fragile; our own numbers decide this, per BUILD_SPEC honesty rules).

**Can claim (a benchmark/integration contribution, not a new algorithm), provided Track A delivers it:**

> *"An open-source, CPU-reproducible benchmark for energy-aware underwater-glider navigation in procedurally generated 2-D ocean-current fields. It compares a PPO policy with a straight-line controller and with time-optimal and energy-aware graph planners (A\*/Dijkstra) on identical held-out maps. It reports the time-energy trade-off (Pareto sweep over w_energy/w_time) over multiple training seeds with paired bootstrap confidence intervals, plus ablations and a held-out double-gyre transfer test. In my search (GitHub + web, Nov 2026) I did not find a public repository that combines glider-scale parameters, an explicit vehicle energy model with a Pareto sweep, an energy-aware classical planner baseline on paired maps, and multi-seed CI reporting."*

Conditions and caveats to state on the slide:
1. The novelty is in the **combination and the evaluation rigour**, not in the method. Say "benchmark", not "new algorithm".
2. The energy model is an **assumption** (hotel load + turning cost), not a validated glider energy model (BUILD_SPEC itself notes that real glider energy is dominated by the buoyancy pump and hotel load). Say so.
3. If the build drops any element (e.g. the Pareto sweep or the 5 seeds), the claim shrinks accordingly. Re-check against docs/HANDOFF.md before presenting.
4. R10 (Braghin 2026) and the two unverified Ocean Engineering glider DRL papers may overlap more than their abstracts show. Skim them before the presentation, and if one already has a planner baseline + Pareto sweep, change the claim to "reproducible open-source re-implementation and benchmark".
5. Never say "first" or "nobody has done this". Say "I did not find a public implementation that ...".

**Suggested one-line slide version:** *"Not a new algorithm: an open, reproducible benchmark asking whether PPO beats energy-aware classical planning for a slow glider in eddying currents, with the time-energy trade-off measured over multiple seeds."*
