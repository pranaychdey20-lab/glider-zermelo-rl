# Project context (from the pasted earlier chat)

## Assignment
Pick ONE of 10 robotics topics: parallel manipulator, humanoid robot, sensors in industrial robots, drone controller, snake robot, underwater glider, underwater ROV/AUV, surgical robot, agriculture robot, AI in robotics.
Deliverables: read 30 papers and collect their abstracts; read 3 of them thoroughly; give a 5-minute presentation with a simulation demo.
User also wants: per-topic research and how to simulate it, an easy-language explanation of each, and a table ranking the topics from toughest to easiest, with a column showing whether it has been done in the real world (checking GitHub too) and which topics nobody has tried, so they can pick something new.

## Candidate project (from earlier chat)
RL, energy-aware navigation of an underwater glider through synthetic ocean-current fields (Zermelo-style), compared with straight-line and A*/Dijkstra planner baselines.
- Laptop only (i7, RTX 5060, CPU training), Python, gymnasium, stable-baselines3 (PPO), 2-day budget, publish on GitHub for ML job applications.
- Spec highlights: 50x50 km domain, V=0.3 m/s, dt=600 s, 400 steps, stream-function currents (eddies, jet, held-out double gyre), assumed energy model, potential-based reward shaping.
- Eval: train seeds 0-9999, val 10000-10099, test 100000-100199, 5 training seeds, paired comparisons, bootstrap CIs.
- Stages 0-7 (setup, fields/dynamics, planner, env+PPO, eval, experiments, demos, handoff docs), with docs/STATUS.md, HANDOFF.md, ASSUMPTIONS.md, LEARN.md.
- Prompt 1 (build) and Prompt 2 (audit/report/PPT/release) were drafted.

## Agreed revised order
1. Find and verify 30 papers (5 surveys, 10 classic, 10 recent, 5 implementation) via live search, with a table (citation, year, link, plain summary, relevance, limitation).
2. User copies official abstracts (links provided; summaries written in own words, no verbatim abstracts).
3. Choose 3 papers for deep reading (survey, closest method, recent gap paper).
4. Deep read with Claude's help (reading guide, explanations, critique, quiz) -> "design brief".
5. Build from the design brief.
6. Audit, report, PPT, GitHub release.
Literature topics in order: glider modelling/control; Zermelo/flow-aware navigation; RL for navigation in currents; AUV/glider path planning; RL tools (PPO, SB3); ocean-current data/eddy models.

## Pending
The previous assistant asked: "Should I go ahead with topic 1?" Not yet answered.
Rules: never invent citations or results; mark anything unverified.
