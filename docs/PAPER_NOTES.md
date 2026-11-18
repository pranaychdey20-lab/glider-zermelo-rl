# Deep-read notes: 3 papers (read in full from the arXiv PDFs on 2026-11-18)

Honesty note. The first literature pass (literature/papers_table.md) only verified record pages and wrote summaries from them; no full text was read. These notes come from the full arXiv texts of R1, R6 and R10. The survey S3 (Panda et al. 2020) is paywalled and was NOT read; R10 replaces it as the third paper. R7 (Zhang et al. 2025, flow prediction + PPO) is the paper most relevant to "beating the planner" but is paywalled on ScienceDirect and was NOT read. Page/figure claims below are from the texts; interpretation is marked as such.

## R1. Gunnarson, Mandralis, Novati, Koumoutsakos, Dabiri (2021), arXiv:2102.10536
- Problem: fixed-speed point swimmer (speed 0.8 x free-stream) crossing an unsteady cylinder wake, random start/target/start-time; success = within D/12 of target. Heading is the action. Forward Euler, dt = 0.3 D/U.
- Observation study (the key result): flow-blind (relative position only), vorticity (+ previous vorticity), velocity (local u, v). Success: naive swim-to-target 1.3 +/- 0.4%, flow-blind 39.4 +/- 5.8%, vorticity 47.2 +/- 8.7%, velocity 99.9 +/- 0.1% (mean +/- std over 5 trainings, 12,500 episodes each). Explanation offered: with linear dynamics the local velocity nearly determines the next position.
- Agents get position RELATIVE to the target, not absolute position, on purpose, so they cannot memorise where flow features are.
- Reward: r_n = -dt + 10 (|X_{n-1} - X_t| - |X_n - X_t|)/U_swim + bonus; the shaping terms are scaled x10 ("significantly improved training speed and success"); bonus = 200 (about 30x a typical trajectory duration); leaving the domain or hitting the cylinder = failure. A reciprocal-distance shaping term was tried and was worse. Total return = -T_f + const, so maximising it = minimising time.
- Algorithm: V-RACER (off-policy, Remember-and-Forget replay), one 128x128 network, Gaussian policy, 20,000 episodes, 5 repeat trainings.
- Comparison with optimal control: planner = RRT + constrained gradient optimisation (MATLAB fmincon), run 30x, best kept, with full knowledge of the flow. RL (velocity sensing) was 16%, 15%, 23% SLOWER than that planner on three example start/target pairs (8.80 vs 7.38, 18.4 vs 15.6, 33.3 vs 25.7 in D/U units). So even in the original paper RL approaches but does not beat the global planner. Only 3 example pairs, not a distribution.
- Robustness argument: planner trajectories are open loop; RL reacts to what it senses.

## R6. Mecanna, Loisy, Eloy (2025), arXiv:2505.05525 (code: github.com/C0PEP0D/RLflow)
- Benchmark: swimmer must maximise distance travelled along a direction in partially observed flows (Taylor-Green vortices, ABC flow, 2-D turbulence); observation = local velocity-gradient entries. Baselines: naive (always up) and "surfing" policy (analytic, first-order Pontryagin approximation, one tuned parameter tau*). Surfing uses ONLY local information, so it is the fair comparator for a local-sensing learner.
- Result (distance normalised by naive): PPO 1.62 / 2.35 / 1.51 (TGV/ABC/TURB), surfing 1.48 / 2.08 / 1.51, A2C 1.13 / 2.32 / 1.20, Q-learning 1.22 / 1.90 / 1.17. Vanilla Q-learning and A2C do not match the strong heuristic; PPO does, robustly over 10 seeds.
- What it took to make PPO work: vectorised environments, generalised advantage estimation, advantage and observation normalisation, fixed-length rollouts, learning-rate annealing, target KL 0.02, clip 0.1, entropy coef 0, separate small actor (2x40) and critic (2x100) networks, manual hyper-parameter tuning ("performance is highly sensitive" to learning rates and GAE parameters). Evaluation: deterministic (mean-action) policy; best agent over training is selected; turbulence test uses a held-out time segment.
- Message for us: compare against a strong baseline that has the SAME information as the learner, run many seeds, and report honestly.

## R10. Braghin, Botteghi, Tomasetto, Manzoni, Cazzulani (2026), arXiv:2607.13553
- Problem: TD3 agent reaching arbitrary targets and station-keeping in a parametric double gyre (A in [0,0.5], omega in [0.5, 2pi/3], eps 0.1); action = 2-D velocity command with |u| <= 0.2 (weaker than the flow). Reward: -(squared distance) - alpha*|a|^2 + bonus; success = near target for > 100 time steps.
- Five observation sets: naive (time + relative position), velocity, vorticity, velocity history (M past readings, M=10 best of 5/10/15), vorticity history. Success (mean of 3 seeds): naive ~49%, velocity ~60%, vorticity ~58%, vorticity history ~60%, velocity history ~71% (best, and fastest to learn). Velocity-aware agents had lower control penalty (more energy-efficient); vorticity-aware agents got closer to targets.
- Giving the agent the gyre's global parameters lowered performance for almost all agents.
- Limits: 3 seeds, no planner baseline, no success above ~71%, point agent with direct velocity control.

## What the three papers agree on (my synthesis, not a quote)
1. Sense local VELOCITY (current); gradients/vorticity or short memory add information in unsteady flows.
2. Do not give the agent global field parameters or absolute position it can memorise.
3. Reward = time penalty + scaled progress shaping + terminal bonus (+ control/energy penalty).
4. The learner is compared with an optimal planner or a strong analytic heuristic; PPO needs a careful recipe; multiple seeds.
5. RL is expected to approach, not clearly beat, a planner that knows the whole flow (R1: 15-23% slower on three examples). Our measured gap (about 5% more energy, 10-11% more time vs the energy-aware planner on maps both solve) is in the same range, but the setups differ and the numbers are not directly comparable.
