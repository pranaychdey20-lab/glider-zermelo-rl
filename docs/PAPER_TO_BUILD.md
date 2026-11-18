# From papers to the build: what is used, what is not

Status column is updated by the implementation session. "Coincident" = the build did the same thing before the papers were read (not derived from them).

| # | Idea | Source | In our build before this step | Planned change | Status |
|---|---|---|---|---|---|
| 1 | Observe local current velocity | R1, R10 | Yes (local current + 5x5 patch) | keep | Coincident |
| 2 | Observation ablation: position-only / velocity only / patch / patch + short history | R1, R10 | Only "no current" ablation | replicate on our maps | TODO |
| 3 | Short memory (M past current readings) | R10 | No | add history option, M in {1,5,10} | TODO |
| 4 | No absolute position in the observation | R1 | Absolute x/L, y/L included (to see walls) | ablation without it (walls then seen via distance-to-wall features) | TODO |
| 5 | Do not give global field parameters | R10 | Not given | keep; document | Coincident |
| 6 | Strong local-information baseline (analog of surfing) | R6 | Only naive straight-line vs a global planner | add "current-compensated heading" heuristic (local current only) | TODO |
| 7 | PPO recipe: obs normalisation, LR anneal, target KL 0.02, clip 0.1, GAE, small nets, best-checkpoint on validation, more seeds | R6 | LR decay + target KL added after 6M run failed; no obs normalisation, no checkpoint selection | add VecNormalize, clip 0.1, validation checkpoint selection | TODO |
| 8 | Reward = -time + scaled shaping + bonus (+ control penalty) | R1, R10 | Same form | keep; try shaping scale | Coincident |
| 9 | Compare RL to planner knowing the whole flow; expect gap | R1 | Done | report gap in context of R1 | Done |
| 10 | Privileged-information RL (planner cost-to-go / waypoint as input) to try to beat the planner | not in the 3 papers; motivated by R1's open-loop vs closed-loop argument and R7 (not read) | No | optional hybrid experiment, clearly labelled as privileged-information | TODO |
