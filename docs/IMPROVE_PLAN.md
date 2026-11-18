# Can ideas from the papers make our RL beat the planner? (plan, NOT yet tested)

Written 2026-11-18 11:25 IST under a 6-minute deadline. No new experiment was run, so nothing here is a result. Paper IDs refer to literature/papers_table.md.

## Why RL loses now (measured, docs/HANDOFF.md)
The planner knows the WHOLE current field; RL sees an 8 x 8 km patch. On maps both solve RL needs ~10% more time and ~5% more energy; 16 test maps are solved by the planner but by no RL seed. The no-current ablation (66.8%, straight-line level) shows RL's skill comes from the flow information it gets, so giving it better information is the most promising lever.

## Ideas, ranked by expected gain per hour
1. **Give RL what the planner knows (R1, S3 "known vs unknown environment").** R1 compares agents by what they observe; S3 splits planning by whether the flow is known. Our comparison mixes the two. Add to the observation a coarse global view: e.g. the current on an 8x8 grid over the whole 50 km domain, or the planner's time-to-goal map around the glider. Then RL and planner have the same information and RL can still beat it by handling things the planner approximates (frozen-snapshot currents, grid discretisation, turn limit, jittery path follower that costs ~5x straight-line turning energy). Cost: ~30 min code + 20 min training (5 seeds x 2M).
2. **Residual RL on top of the planner (hybrid; S1/S3 "hybrid" category).** Action = planner heading + learned correction. RL starts at planner level (95% success) and only has to learn improvements, mainly smoother turning (energy) and handling time-varying flow (double gyre). This is the most likely way to *beat* the planner on energy. Cost: ~30 min code + 20 min training.
3. **Stable PPO by default (R6: "common RL methods do poorly when not carefully chosen and tuned").** Already measured: LR decay + target KL gave 85.0% (test) / 85.6% (fresh confirmatory maps) vs 80.4% / 82.4%. Use it as the base for 1 and 2. A small validation-only sweep (entropy coefficient, n_steps, network size) is the next R6-style step.
4. **Velocity sensing is the right signal (R1).** R1 found velocity-sensing agents beat vorticity-sensing ones; our patch already senses velocity. A wider or multi-scale patch (e.g. 5x5 at 2 km plus 5x5 at 8 km spacing) is a cheap version of idea 1.
5. **Where RL could genuinely win: unknown or forecast-error currents.** The planner's advantage disappears if its field is wrong. Test both on "true field = forecast + random eddy perturbation" with the planner given only the forecast; RL senses the true local current. This matches the realistic glider setting (HYCOM forecasts, I4) and is the fairest "RL beats planner" story.

## Honest framing for the presentation until these are run
"RL with local sensing beats the naive heading but not a planner with perfect global knowledge; the papers (R1, R6) suggest the gap comes from information and tuning, and ideas 1, 2 and 5 are the planned tests."

## How to run the next step (suggested order)
Idea 2 (residual) -> idea 1 (global observation) -> idea 5 (forecast error), each with 5 seeds, decisions on validation maps only, final numbers on the fresh `confirm` split or a new pre-registered one.
