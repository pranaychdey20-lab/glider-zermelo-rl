# Deep-read plan: 3 papers + glossary

IDs refer to `papers_table.md`. Pick-up order: read **R1 first** (closest to what you are building, open access, short), then **S3** (to place it in the field), then **R6** (to see the gap and why our evaluation protocol matters).

| Role | Paper | Why this one |
|---|---|---|
| Survey | **S3** Panda, Das, Subudhi, Pati (2020), *A comprehensive review of path planning algorithms for AUVs*, Int. J. Automation and Computing 17(3):321-352, doi:10.1007/s11633-019-1204-9 | Broadest map of the classical AUV path-planning world your A*/Dijkstra baseline comes from. Splits methods by whether the environment is predictable or not, which is the exact line between "planner with known currents" and "learned policy with local sensing". |
| Method (closest) | **R1** Gunnarson, Mandralis, Novati, Koumoutsakos, Dabiri (2021), *Learning efficient navigation in vortical flow fields*, Nature Communications 12:7143, doi:10.1038/s41467-021-27015-y | Same problem shape as yours: fixed-speed vehicle, point-to-point, unsteady 2-D flow, RL policy vs an optimal-control planner, and a comparison of what the agent observes. Open access. |
| Recent gap | **R6** Mecanna, Loisy, Eloy (2025), *A critical assessment of RL methods for microswimmer navigation in complex flows*, EPJ E / arXiv:2505.05525 | Argues that much of the RL-in-flows literature uses weak algorithms and weak comparisons. This is the honest gap your project can address: a careful, multi-seed, baseline-heavy evaluation, plus an explicit energy term that these papers don't have. |

Backup choices if one is hard to get: survey **S2** (Zeng et al. 2015); method **C10** (Biferale et al. 2019, arXiv open); gap **R9** (Darvariu et al. 2026: real Slocum gliders, a planner rather than RL, compared with straight-to-goal).

> Note: I could not open the full texts from this container (network policy), only the record pages. The guides below say *what to look for*; they don't claim what the papers' figures or sections contain. Fill in the answers yourself while reading, then bring them back for the critique/quiz step.

---

## 1. Survey - S3 Panda et al. (2020)

**Get it:** <https://link.springer.com/article/10.1007/s11633-019-1204-9> (may be paywalled; try your college library login, or search the title for an author copy).

**What to look for**
- The taxonomy: how they divide "predictable" vs "unpredictable" environments, and single-AUV vs multi-AUV planning.
- Where ocean currents appear: is current treated as a disturbance, a cost or something to exploit?
- Which cost functions are used (distance, time, energy, risk) and whether energy is modelled or just stood in for by distance.
- How learning-based methods (neural nets, RL) are placed in the taxonomy, and what limitations the authors attach to classical graph search (grid resolution, needing a known map).
- Any table that compares methods. Note what is compared (computation, optimality, dynamic environments).

**5 questions to answer while reading**
1. In the authors' taxonomy, which box does *your* RL policy fall into, and which box does your A*/Dijkstra baseline fall into?
2. What assumptions does graph search (A*, Dijkstra) make about the environment, and which of them does a time-varying current break?
3. How do the reviewed papers define "optimal": shortest, fastest, or lowest energy? Which do they use most often?
4. What do the authors list as open problems? Is "exploiting currents for energy" one of them?
5. Name two classical methods from the review that you are *not* comparing against, and give one sentence on why that is acceptable for a 2-day project.

**How it connects to a slide**
- **Slide "Related work / where this fits":** a 2x2 grid (known vs unknown environment x classical vs learned) with your two baselines and your RL agent placed in it. Cite S3 (and S2) as the source of the grid.

---

## 2. Method paper - R1 Gunnarson et al. (2021)

**Get it:** <https://www.nature.com/articles/s41467-021-27015-y> (open access). Preprint: arXiv:2102.10536.

**What to look for**
- **The setup:** swimmer speed vs flow speed, the flow (unsteady cylinder wake), start/target placement, episode termination. Compare each with your config: V = 0.3 m/s, eddies up to 0.5 m/s, 50x50 km, goal radius 1 km.
- **The observation:** what the "velocity-sensing" and "vorticity-sensing" agents actually receive. Your observation (local current + 5x5 current patch + goal vector) is closer to which one?
- **The action:** heading directly, or heading change? Yours is a heading change of up to +/-30 deg per step.
- **The reward:** is it time-based, distance-based, or both? Is there shaping? Compare with your -time -energy +progress shaping +goal bonus.
- **The baseline:** how the "global optimal control planner" is computed and what it is allowed to know. This is your planner baseline's analogue.
- **The evaluation:** how many episodes, how success rate is defined, whether results are averaged over training seeds, and whether policies are tested on flows they never saw.
- What they say about failure cases (agents trapped in vortices?).

**5 questions to answer while reading**
1. Why does a swimmer that is slower than the flow need a strategy at all, instead of just pointing at the target? (Link to the Zermelo problem.)
2. Why does sensing velocity work better than sensing vorticity, according to the authors? Does that support or challenge putting a 5x5 current patch in your observation?
3. What does their optimal-control planner know that the RL agent does not? Is that comparison "fair"? How does that compare with your A*/Dijkstra planner?
4. Which part of their objective corresponds to your w_time term? What would change in their results if an energy term (turning cost, hotel load) were added?
5. Do they test on a different flow than the one used in training? If not, why is your held-out double gyre (C4) a meaningful extra test?

**How it connects to a slide**
- **Slide "Method":** a side-by-side table "Gunnarson 2021 vs this project" with rows: vehicle, flow, observation, action, reward, algorithm, baseline, test flows. The last two rows show what is new in your project (energy term, held-out flow, paired multi-seed comparison with CIs).
- **Demo slide:** their trajectories next to your 3-way animation (straight-line red, planner orange, RL green).

---

## 3. Recent gap paper - R6 Mecanna, Loisy & Eloy (2025)

**Get it:** <https://arxiv.org/abs/2505.05525> (open). Published in European Physical Journal E (2025).

**What to look for**
- The **benchmark task** and the **three flows** (Taylor-Green vortices, ABC flow, 2-D unsteady turbulence).
- **Which algorithms** are compared (tabular Q-learning, A2C, and the deep RL ones) and how each was tuned.
- What they count as a **good result**: compared with what heuristic or reference?
- How many **independent training runs** they use and how they report spread (this is the Agarwal et al., I3, issue).
- Their explanation of **why** popular methods fail: partial observability? non-stationarity? poor exploration?
- Their recommendations for future work.

**5 questions to answer while reading**
1. What is "partial observability" here, and is your glider partially observing its world? (Hint: it sees a 5x5 local patch, not the whole field.)
2. Which algorithm(s) worked best and under what conditions? Is PPO among them, and does that support your choice of SB3-PPO?
3. What heuristic or baseline do the authors compare against? What is the equivalent in your project (straight-line? planner?)
4. List three evaluation practices from this paper that your BUILD_SPEC already follows (e.g. multiple seeds, held-out tests, fixed protocol before results) and one it does not.
5. If your PPO agent does *not* beat the planner, how would this paper help you explain that honestly in the presentation?

**How it connects to a slide**
- **Slide "Gap and contribution":** one line from this paper ("common RL methods do poorly when not carefully chosen and tuned") followed by your answer: energy-aware objective + classical planner baseline + 5 seeds + paired bootstrap CIs + held-out flow. Pair it with R10 (Braghin et al. 2026) and R7 (Zhang et al. 2025) as "closest recent work" so the audience sees you checked.

---

## Glossary (plain language)

| Term | Simple explanation | Where it shows up |
|---|---|---|
| **Underwater glider** | A torpedo-shaped robot with wings and no propeller. It changes its buoyancy (pumps oil in/out of a bladder) to sink and rise, and the wings turn that up/down motion into slow forward motion (typically a few tenths of a metre per second, much slower than walking; the project assumes 0.3 m/s). Very energy-efficient, so it can stay out for months. | S1, C2, R9 |
| **AUV** | Autonomous Underwater Vehicle: any untethered underwater robot that drives itself. A glider is a special, slow, buoyancy-driven AUV. | S2, S3 |
| **Ocean current field** | A map that gives, for every point (and time), the speed and direction the water is moving. Written u(x,y,t) (east-west) and v(x,y,t) (north-south). | C4, I4 |
| **Ground velocity** | How the glider actually moves over the sea floor = its own velocity through the water + the current. If both are 0.3 m/s and opposite, it stands still. | BUILD_SPEC |
| **Zermelo navigation problem** | "Given a boat of fixed speed in a known current, which heading should it steer at each moment to reach the target as fast as possible?" Posed by Zermelo in 1931. Our version adds energy. | C1, C5, C10 |
| **Stream function (psi)** | A single scalar map from which the current is computed: u = d(psi)/dy, v = -d(psi)/dx. Any current made this way automatically conserves water (no sources or sinks). The current flows along the contour lines of psi. | C4, BUILD_SPEC |
| **Divergence-free** | The water doesn't pile up or vanish anywhere: du/dx + dv/dy = 0. Stream-function currents satisfy this by construction, and the build checks it numerically. | BUILD_SPEC |
| **Eddy (vortex)** | A spinning patch of water, like a whirlpool tens to hundreds of km wide in the real ocean. Clockwise or anticlockwise ("spin"). | I5 |
| **Mesoscale** | Ocean features roughly tens to a couple of hundred km in size, e.g. eddies. "Submesoscale" means smaller (about 1-10 km). | I5, S1 |
| **Jet** | A narrow band of fast current, like a river within the ocean (the Gulf Stream is a famous one). | BUILD_SPEC |
| **Double gyre** | A standard textbook flow: two side-by-side counter-rotating cells whose dividing line wobbles in time. Used as our held-out test field. | C4, C5, R7, R10 |
| **Lagrangian coherent structure (LCS) / FTLE** | Hidden "walls" in a flow that separate regions where floating particles go different ways. FTLE (finite-time Lyapunov exponent) measures how fast nearby particles separate; its ridges mark the LCS. Gliders can ride along them. | C4 |
| **RK2 (Runge-Kutta 2)** | A way to step the motion forward in time that uses the velocity at the midpoint of the step, which is more accurate than Euler (which uses only the starting velocity). | BUILD_SPEC |
| **Hotel load** | Power the vehicle uses just to stay "alive" (computer, sensors, comms), whether or not it moves. Longer missions spend more of it, which is why time costs energy. | BUILD_SPEC energy model |
| **Graph search, Dijkstra, A\*** | Cut the map into a grid of nodes, give each move a cost (here: time or energy given the current), and find the cheapest chain of moves. Dijkstra explores outward by cost; A* adds a "distance-to-goal" guess to search faster. | C3, C6 |
| **Level-set method** | Imagine the set of all places the glider could have reached by time t as a growing blob; track its boundary as an equation. The first time it touches the goal gives the fastest path. | C5 |
| **MDP (Markov decision process)** | The maths model of a decision problem: states, actions, transition rules, rewards. RL and dynamic programming both solve MDPs. | R3, R9 |
| **Reinforcement learning (RL)** | Learning a policy (state -> action rule) by trial and error in a simulator, guided by rewards. | C8-C10, R1-R10 |
| **Policy** | The learned rule: given what the glider observes, which heading change to make. In PPO it is a small neural network. | C9 |
| **Observation** | What the agent is allowed to see each step (here: vector to goal, heading, local current, a 5x5 patch of currents around it, time/energy used). Not the whole map. | R1, R5 |
| **Partial observability** | The agent can't see the full state of the world (e.g. the whole current field), only local hints. Makes the problem harder. | R6 |
| **Reward / reward shaping** | Reward = the score per step. Shaping = extra hints (e.g. "+ for getting closer") to speed up learning. | C7 |
| **Potential-based shaping** | A shaping bonus of the form gamma*Phi(next) - Phi(now), e.g. Phi = -distance to goal. Proven not to change which policy is best, only how fast it is learned. Also blocks the "stay still forever" loophole when combined with a time penalty. | C7 |
| **Policy gradient** | RL methods that adjust the policy network's weights directly in the direction that increases expected reward. | C9 |
| **PPO (Proximal Policy Optimization)** | A popular, stable policy-gradient method: collect a batch of experience, then take several small update steps, but "clip" each update so the new policy can't move too far from the old one. | C9, I1 |
| **Actor-critic** | Two networks: the actor chooses actions, the critic estimates how good a state is, to reduce noise in learning. PPO is an actor-critic method. | C10, R2 |
| **SAC / TD3 / DQN / A2C / SARSA / Q-learning** | Other RL algorithms you will see in papers. SAC and TD3: off-policy, continuous actions. DQN: deep Q-learning, discrete actions. A2C: simple synchronous actor-critic. SARSA and Q-learning: classic tabular methods. | C8, R6, R8, R10 |
| **Stable-Baselines3 (SB3)** | A tested Python library with ready-made RL algorithms (PPO, SAC, ...) in PyTorch. We use its PPO. | I1 |
| **Gymnasium** | The standard Python interface for RL environments: `reset()` gives the first observation; `step(action)` returns observation, reward, terminated, truncated, info. | I2 |
| **Vectorised environments** | Running several copies of the environment in parallel (we use 8) so PPO collects experience faster. | I1 |
| **Training seed** | The random-number seed for one complete training run. Different seeds give different agents, so results are reported over several seeds (we use 5). | I3 |
| **Train / validation / test maps** | Separate pools of current-field seeds: train (0-9999) for learning, validation (10000-10099) for choosing settings, test (100000-100199) touched only once at the end. Stops us fooling ourselves. | BUILD_SPEC, I3 |
| **Paired comparison** | Every method is run on the *same* test maps, so differences come from the method, not from luckier maps. | BUILD_SPEC |
| **Bootstrap confidence interval** | Resample the per-map results with replacement thousands of times, recompute the mean each time, and take the middle 95% as the interval. Shows how sure we are of a mean. | I3 |
| **Pareto front** | When two goals conflict (time vs energy), the set of results where you can't improve one without worsening the other. We sweep w_energy/w_time to trace it. | BUILD_SPEC, C6 |
| **Ablation** | Remove one ingredient (e.g. the current observation) and retrain, to see how much it mattered. | BUILD_SPEC |
| **Held-out / out-of-distribution test** | Testing on a kind of flow never seen in training (our double gyre) to check the policy generalises instead of memorising. | R5, BUILD_SPEC |
| **HYCOM / ocean reanalysis** | A real ocean-model data product that gives estimated currents worldwide. Where realistic currents would come from in future work. | I4 |
