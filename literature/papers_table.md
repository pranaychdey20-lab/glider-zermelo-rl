# Literature table: RL energy-aware underwater-glider navigation in ocean currents (Zermelo)

Track B deliverable. 30 papers: 5 surveys, 10 foundational, 10 recent (2021+), 5 simulation/implementation. Machine-readable copy: `papers.csv` (same content, same IDs).

## How these were verified (read this first)

- Searched live on 2026-11-17/18 (UTC). This container's network policy **blocked direct page fetches** to arXiv, doi.org, PMC, Crossref, Semantic Scholar, publishers (proxy returned 403). So each paper was verified through **live web-search results that returned the official record page** (arXiv abstract page, publisher/DOI page, PMC, or an institutional repository) and the title, authors, year and venue/DOI were matched, usually across two independent records. The `verification_note` column says which records were seen.
- The three papers named in the brief were checked and are real, with the details given: Reddy et al. PNAS 2016 (C8), Biferale et al. Chaos 2019 (C10), Gunnarson et al. Nature Communications 2021 (R1).
- Summaries are my own words, written from the record pages, not copies of abstracts. **Numbers in summaries are only those stated on the record pages.** When you paste the official abstract, also click the link: if any field disagrees with the page, the page wins - tell me and I will fix the row.
- Anything I could not tie to its own record page is in **UNVERIFIED** at the bottom and is **not** counted in the 30.
- Fields marked 'check page' (R7 full author list, C10 article number) are the only partial items among the 30.

## Quick index

| ID | Year | First author | Short title | Category | Supports |
|---|---|---|---|---|---|
| S1 | 2016 | Rudnick | Ocean research enabled by underwater gliders | Survey | Slide 1-2 motivation; justification of the slow-vehicle (V~0.3 m/s) setting |
| S2 | 2015 | Zeng | A survey on path planning for persistent autonomy of autonomous und... | Survey | Related-work slide; positioning of the A*/Dijkstra baseline |
| S3 | 2020 | Panda | A comprehensive review of path planning algorithms for autonomous u... | Survey | Deep-read survey; taxonomy for the related-work slide; why a learned policy is worth testing |
| S4 | 2025 | Hong | Control of marine robots in the era of data-driven intelligence | Survey | Recent-survey slide; framing RL as complement to planners |
| S5 | 2025 | Cai | Reinforcement learning for active matter | Survey | Survey of the RL-in-flows lineage (Reddy, Biferale, Gunnarson) |
| C1 | 1931 | Zermelo | Über das Navigationsproblem bei ruhender oder veränderlicher Windve... | Classic | Problem-statement slide; the name of the project |
| C2 | 2001 | Leonard | Model-based feedback control of autonomous underwater gliders | Classic | Glider-model slide; justification (and limitation) of the 2-D kinematic, constant-speed abstraction |
| C3 | 2005 | Garau | Path planning of autonomous underwater vehicles in current fields w... | Classic | Planner-baseline slide (A*/Dijkstra with current-aware edge costs) |
| C4 | 2005 | Shadden | Definition and properties of Lagrangian coherent structures from fi... | Classic | Double-gyre held-out test field; stream-function slide |
| C5 | 2014 | Lolla | Time-optimal path planning in dynamic flows using level set equatio... | Classic | 'Optimal reference' slide; explains what an exact Zermelo solver looks like vs RL |
| C6 | 2018 | Kularatne | Going with the flow: a graph based approach to optimal path plannin... | Classic | Energy-aware planner baseline; edge-cost design |
| C7 | 1999 | Ng | Policy invariance under reward transformations: theory and applicat... | Classic | Reward-design slide; why shaping by distance-to-goal does not change the optimum |
| C8 | 2016 | Reddy | Learning to soar in turbulent environments | Classic | Early evidence that RL can learn to exploit a flow; 'RL in flows' history slide |
| C9 | 2017 | Schulman | Proximal policy optimization algorithms | Classic | Method slide (PPO); hyperparameter defaults |
| C10 | 2019 | Biferale | Zermelo's problem: optimal point-to-point navigation in 2D turbulen... | Classic | Closest classic precedent: Zermelo + RL; 'why not just solve the optimal control' slide |
| R1 | 2021 | Gunnarson | Learning efficient navigation in vortical flow fields | Recent | Deep-read method paper; observation design (local current); RL-vs-planner comparison |
| R2 | 2021 | Buzzicotti | Optimal control of point-to-point navigation in turbulent time depe... | Recent | Supports claim that RL is competitive with optimal control in time-varying flow |
| R3 | 2022 | Chowdhury | Optimal path planning of autonomous marine vehicles in stochastic d... | Recent | Alternative baseline family (MDP/DP); uncertainty in currents |
| R4 | 2024 | Greeley | On the convergence of a reinforcement learning process to a general... | Recent | Energy objective in RL guidance; interpretable learned behaviour (good discussion point) |
| R5 | 2025 | Jiao | Sensing flow gradients is necessary for learning autonomous underwa... | Recent | Observation design (why the 5x5 current patch is a gradient-like signal) |
| R6 | 2025 | Mecanna | A critical assessment of reinforcement learning methods for microsw... | Recent | Deep-read gap paper; justifies the strong baselines + multi-seed + CI protocol |
| R7 | 2025 | Zhang | Efficient navigation in vortical flows based on reinforcement learn... | Recent | Closest recent method (PPO + double gyre + Zermelo); novelty check |
| R8 | 2025 | Gadhvi | Khalasi: energy-efficient navigation for surface vehicles in vortic... | Recent | Energy-aware RL precedent; argument against static-grid planners |
| R9 | 2026 | Darvariu | Online navigation planning for long-term autonomous operation of un... | Recent | Real-world glider gap: shows what field systems use (planning, straight-to-goal baseline); future-work slide |
| R10 | 2026 | Braghin | Flow-aware optimal navigation in unsteady flows through reinforceme... | Recent | Very close recent work (double gyre, energy, sensing) - must be cited in novelty statement |
| I1 | 2021 | Raffin | Stable-Baselines3: reliable reinforcement learning implementations | Simulation/implementation | Implementation slide; reproducibility |
| I2 | 2024 | Towers | Gymnasium: a standard interface for reinforcement learning environm... | Simulation/implementation | Environment design slide |
| I3 | 2021 | Agarwal | Deep reinforcement learning at the edge of the statistical precipice | Simulation/implementation | Evaluation-protocol slide: 5 training seeds, bootstrap CIs, no single-seed claims |
| I4 | 2007 | Chassignet | The HYCOM (HYbrid Coordinate Ocean Model) data assimilative system | Simulation/implementation | Future-work slide (real currents); 'why synthetic fields first' discussion |
| I5 | 2011 | Chelton | Global observations of nonlinear mesoscale eddies | Simulation/implementation | ASSUMPTIONS.md: are 5-12 km, 0.1-0.5 m/s eddies realistic? |

## Surveys (5)

### S1. Ocean research enabled by underwater gliders (2016)

- **Authors:** Rudnick, D. L.
- **Venue:** Annual Review of Marine Science 8:519-541
- **DOI:** 10.1146/annurev-marine-122414-033913
- **Link:** <https://doi.org/10.1146/annurev-marine-122414-033913>
- **Topic:** Glider modelling/ops
- **Plain-language summary:** A review of what underwater gliders had achieved in ocean science up to 2016, from submesoscale and biogeochemical studies to measurements of internal waves and turbulence. Useful background for the motivation slide: what gliders are and what science they make possible.
- **Supports this part of the project:** Slide 1-2 motivation; justification of the slow-vehicle (V~0.3 m/s) setting
- **Limitation:** Oceanographic-science focus; says little about navigation or path-planning algorithms.
- **Verification:** Search returned the Annual Reviews record plus marineinfo.org and peeref records; title, author, volume, pages and DOI agree.

### S2. A survey on path planning for persistent autonomy of autonomous underwater vehicles (2015)

- **Authors:** Zeng, Z.; Lian, L.; Sammut, K.; He, F.; Tang, Y.; Lammas, A.
- **Venue:** Ocean Engineering 110(A):303-313
- **DOI:** 10.1016/j.oceaneng.2015.10.007
- **Link:** <https://doi.org/10.1016/j.oceaneng.2015.10.007>
- **Topic:** AUV/glider path planning
- **Plain-language summary:** Surveys how AUV paths are represented and optimised, how paths are re-planned when the environment changes, and how several AUVs plan together, with path planning framed as the key to long (persistent) missions. Gives the vocabulary for the classical side of the project.
- **Supports this part of the project:** Related-work slide; positioning of the A*/Dijkstra baseline
- **Limitation:** Written in 2015, before deep RL became common in this area.
- **Verification:** Flinders University research portal + library records; author list, volume/pages and DOI agree.

### S3. A comprehensive review of path planning algorithms for autonomous underwater vehicles (2020)

- **Authors:** Panda, M.; Das, B.; Subudhi, B.; Pati, B. B.
- **Venue:** International Journal of Automation and Computing 17(3):321-352
- **DOI:** 10.1007/s11633-019-1204-9
- **Link:** <https://link.springer.com/article/10.1007/s11633-019-1204-9>
- **Topic:** AUV/glider path planning
- **Plain-language summary:** Reviews single- and multi-AUV path-planning methods, grouped by whether the underwater environment is treated as predictable or unpredictable. It points out that many classical planners assume the environment is known in advance, which is a poor fit for changing ocean conditions.
- **Supports this part of the project:** Deep-read survey; taxonomy for the related-work slide; why a learned policy is worth testing
- **Limitation:** Published 2020, so it misses the 2021+ deep-RL-in-flow papers listed below.
- **Verification:** Springer article page returned by search; four authors, issue, pages and DOI confirmed (also OUCI record).

### S4. Control of marine robots in the era of data-driven intelligence (2025)

- **Authors:** Hong, L.; Liu, L.; Peng, Z.; Zhang, F.
- **Venue:** arXiv:2506.21063 (review; the manuscript template targets Annu. Rev. Control Robot. Auton. Syst. - final DOI not confirmed)
- **DOI:** none / not applicable (use URL)
- **Link:** <https://arxiv.org/abs/2506.21063>
- **Topic:** Data-driven/RL control of marine robots
- **Plain-language summary:** A recent review of control for single and cooperative marine robots that sorts data-driven methods into model-based, model-free (including RL) and hybrid approaches, and lists open-source resources. Its conclusion is that learning complements rather than replaces classical control, with data efficiency, interpretability and on-board deployment still open.
- **Supports this part of the project:** Recent-survey slide; framing RL as complement to planners
- **Limitation:** Focuses on low-level control more than flow-exploiting route planning; cite the arXiv version unless the journal DOI is found.
- **Verification:** arXiv abstract page returned by search (submitted 26 Jun 2025, cs.RO); authors confirmed.

### S5. Reinforcement learning for active matter (2025)

- **Authors:** Cai, W.; Wang, G.; Zhang, Y.; Qu, X.; Huang, Z.
- **Venue:** Biophysics Reviews 6:031302 (arXiv:2503.23308)
- **DOI:** none / not applicable (use URL)
- **Link:** <https://arxiv.org/abs/2503.23308>
- **Topic:** RL navigation in flows
- **Plain-language summary:** Reviews how RL has been used to find motion strategies for single self-propelled particles and to control swarms, which is where most 'navigate through a flow with RL' papers come from. Lists open problems such as generalising across systems.
- **Supports this part of the project:** Survey of the RL-in-flows lineage (Reddy, Biferale, Gunnarson)
- **Limitation:** Microswimmer/active-matter focus; no vehicle energy model or ocean-scale setting.
- **Verification:** arXiv abstract page; journal reference 'Biophysics Rev. 2025, 6, 031302' as listed on arXiv (journal DOI not opened).

## Foundational / classic (10)

### C1. Über das Navigationsproblem bei ruhender oder veränderlicher Windverteilung (1931)

- **Authors:** Zermelo, E.
- **Venue:** ZAMM - Zeitschrift für Angewandte Mathematik und Mechanik 11(2):114-124
- **DOI:** 10.1002/zamm.19310110205
- **Link:** <https://doi.org/10.1002/zamm.19310110205>
- **Topic:** Zermelo problem
- **Plain-language summary:** The original statement of the navigation problem: a craft with fixed speed relative to the air (or water) must choose its heading over time to reach a target as fast as possible in a known wind (or current) field. Every 'Zermelo' paper in this list starts here.
- **Supports this part of the project:** Problem-statement slide; the name of the project
- **Limitation:** In German; deterministic, fully known flow, minimum time only (no energy).
- **Verification:** Wikipedia citation, MaRDI portal and C. Fraser's history paper agree on volume, issue, pages and DOI.

### C2. Model-based feedback control of autonomous underwater gliders (2001)

- **Authors:** Leonard, N. E.; Graver, J. G.
- **Venue:** IEEE Journal of Oceanic Engineering 26(4):633-645
- **DOI:** 10.1109/48.972106
- **Link:** <https://naomi.princeton.edu/wp-content/uploads/sites/744/2021/03/LeoGraJOE01.pdf>
- **Topic:** Glider modelling/control
- **Plain-language summary:** Derives a nonlinear dynamic model of a buoyancy-driven glider and uses it to analyse steady glide paths and design feedback controllers in the vertical plane, illustrated on a lab-scale glider. It is the standard reference for 'how a glider actually flies'.
- **Supports this part of the project:** Glider-model slide; justification (and limitation) of the 2-D kinematic, constant-speed abstraction
- **Limitation:** Vertical-plane dynamics only; says nothing about horizontal routing in currents.
- **Verification:** Princeton author PDF and Princeton research-portal record; DOI from IEEE record.

### C3. Path planning of autonomous underwater vehicles in current fields with complex spatial variability: an A* approach (2005)

- **Authors:** Garau, B.; Alvarez, A.; Oliver, G.
- **Venue:** Proc. IEEE ICRA 2005, pp. 194-198
- **DOI:** 10.1109/ROBOT.2005.1570118
- **Link:** <https://doi.org/10.1109/ROBOT.2005.1570118>
- **Topic:** AUV/glider path planning
- **Plain-language summary:** Applies A* graph search on a grid to plan AUV routes through spatially varying (static) current fields, with edge costs based on travel time. This is essentially the classical baseline the project builds.
- **Supports this part of the project:** Planner-baseline slide (A*/Dijkstra with current-aware edge costs)
- **Limitation:** Static 2-D currents, time cost only, result depends on grid resolution.
- **Verification:** Crossref record (via search) and bibsonomy entry; DOI and pages agree. Full text not opened.

### C4. Definition and properties of Lagrangian coherent structures from finite-time Lyapunov exponents in two-dimensional aperiodic flows (2005)

- **Authors:** Shadden, S. C.; Lekien, F.; Marsden, J. E.
- **Venue:** Physica D 212(3-4):271-304
- **DOI:** 10.1016/j.physd.2005.10.007
- **Link:** <https://doi.org/10.1016/j.physd.2005.10.007>
- **Topic:** Ocean-current/eddy models
- **Plain-language summary:** Defines Lagrangian coherent structures as ridges of the finite-time Lyapunov exponent field, i.e. the hidden 'walls' that organise how fluid moves. Its first worked example is the analytic double-gyre stream function that the project uses as its held-out test field.
- **Supports this part of the project:** Double-gyre held-out test field; stream-function slide
- **Limitation:** Kinematic toy flow, not ocean dynamics; theory-heavy for a first read.
- **Verification:** Caltech AUTHORS record + MaRDI; Shadden lab LCS tutorial confirms the double gyre is the first example.

### C5. Time-optimal path planning in dynamic flows using level set equations: theory and schemes (2014)

- **Authors:** Lolla, T.; Lermusiaux, P. F. J.; Ueckermann, M. P.; Haley, P. J., Jr.
- **Venue:** Ocean Dynamics 64(10):1373-1397
- **DOI:** 10.1007/s10236-014-0757-y
- **Link:** <https://dspace.mit.edu/handle/1721.1/98278>
- **Topic:** Zermelo/flow-aware navigation
- **Plain-language summary:** Shows that the set of points a vehicle can reach grows like a front that obeys a modified level-set equation, so the time-optimal path can be traced back from where the front first touches the goal. Validated on a Rankine vortex and applied to unsteady double-gyre and island-wake flows.
- **Supports this part of the project:** 'Optimal reference' slide; explains what an exact Zermelo solver looks like vs RL
- **Limitation:** Needs the full current field (forecast) in advance; minimises time, not energy.
- **Verification:** MIT DSpace record (author manuscript) + MSEAS group page; volume/pages/DOI agree.

### C6. Going with the flow: a graph based approach to optimal path planning in general flows (2018)

- **Authors:** Kularatne, D.; Bhattacharya, S.; Hsieh, M. A.
- **Venue:** Autonomous Robots 42(7):1369-1387
- **DOI:** 10.1007/s10514-018-9741-6
- **Link:** <https://scalar.seas.upenn.edu/wp-content/uploads/2019/04/Kularatne_AURO2018.pdf>
- **Topic:** Zermelo/flow-aware navigation
- **Plain-language summary:** Builds a graph over the domain and runs graph search to get both time-optimal and energy-optimal paths in static and time-varying flows, tested on analytic flows, real ocean data and a lab flow tank. The closest classical analogue to the project's 'time-optimal vs energy-aware planner'.
- **Supports this part of the project:** Energy-aware planner baseline; edge-cost design
- **Limitation:** Requires the flow to be known; accuracy limited by graph discretisation.
- **Verification:** Author PDF on UPenn SCALAR lab site + Lehigh project page; RSS 2016 conference version also exists.

### C7. Policy invariance under reward transformations: theory and application to reward shaping (1999)

- **Authors:** Ng, A. Y.; Harada, D.; Russell, S.
- **Venue:** Proc. ICML 1999, pp. 278-287
- **DOI:** none / not applicable (use URL)
- **Link:** <https://mlanthology.org/icml/1999/ng1999icml-policy/>
- **Topic:** RL tools (reward design)
- **Plain-language summary:** Proves that adding a shaping reward of the form gamma*Phi(s') - Phi(s) never changes which policy is optimal, and that this potential-based form is essentially the only safe additive shaping. This is the theory behind the project's progress-shaping term.
- **Supports this part of the project:** Reward-design slide; why shaping by distance-to-goal does not change the optimum
- **Limitation:** Says nothing about how to choose a good potential; the guarantee assumes the discounted form is used exactly.
- **Verification:** ML Anthology record + UT Austin reading-list page; pages confirmed (no DOI exists).

### C8. Learning to soar in turbulent environments (2016)

- **Authors:** Reddy, G.; Celani, A.; Sejnowski, T. J.; Vergassola, M.
- **Venue:** PNAS 113(33):E4877-E4884
- **DOI:** 10.1073/pnas.1606075113
- **Link:** <https://www.pnas.org/doi/10.1073/pnas.1606075113>
- **Topic:** RL navigation in flows
- **Plain-language summary:** Trains a simulated (air) glider with the SARSA reinforcement-learning algorithm to climb in turbulent thermals, under realistic flight constraints. The learned policy becomes more cautious as turbulence grows, and the study identifies which sensory cues are worth using.
- **Supports this part of the project:** Early evidence that RL can learn to exploit a flow; 'RL in flows' history slide
- **Limitation:** Atmospheric thermal soaring with tabular RL; aerial glider, not underwater, and no point-to-point goal.
- **Verification:** PNAS DOI page + PMC4995969 + Princeton portal; authors, volume, pages agree. Topic verified as requested.

### C9. Proximal policy optimization algorithms (2017)

- **Authors:** Schulman, J.; Wolski, F.; Dhariwal, P.; Radford, A.; Klimov, O.
- **Venue:** arXiv:1707.06347
- **DOI:** none / not applicable (use URL)
- **Link:** <https://arxiv.org/abs/1707.06347>
- **Topic:** RL tools (PPO)
- **Plain-language summary:** Introduces PPO, a policy-gradient method that alternates between collecting experience and taking several minibatch gradient steps on a 'clipped' objective that stops each update from moving the policy too far. It keeps most of TRPO's stability while being much simpler to implement.
- **Supports this part of the project:** Method slide (PPO); hyperparameter defaults
- **Limitation:** Benchmarked on Atari/MuJoCo; performance is sensitive to implementation details not in the paper.
- **Verification:** arXiv abstract page; five authors confirmed.

### C10. Zermelo's problem: optimal point-to-point navigation in 2D turbulent flows using reinforcement learning (2019)

- **Authors:** Biferale, L.; Bonaccorso, F.; Buzzicotti, M.; Clark Di Leoni, P.; Gustavsson, K.
- **Venue:** Chaos 29:103138 (arXiv:1907.08591)
- **DOI:** 10.1063/1.5120370
- **Link:** <https://arxiv.org/abs/1907.08591>
- **Topic:** RL navigation in flows (Zermelo)
- **Plain-language summary:** Uses an actor-critic RL algorithm to steer a fixed-speed vessel between two points in a 2-D turbulent flow, both frozen and time-evolving. RL finds near-optimal routes, and the classical optimal-navigation solution turns out to be too unstable to use in practice, while RL policies are more robust to noise and to slow vessels.
- **Supports this part of the project:** Closest classic precedent: Zermelo + RL; 'why not just solve the optimal control' slide
- **Limitation:** Minimises time only (no energy); single flow type; small vessel-to-flow geometry.
- **Verification:** arXiv abstract (v1, v2) lists Chaos DOI; topic verified as requested. Article number 103138 from the DOI record as cited - open the DOI to confirm.

## Recent, 2021 onward (10)

### R1. Learning efficient navigation in vortical flow fields (2021)

- **Authors:** Gunnarson, P.; Mandralis, I.; Novati, G.; Koumoutsakos, P.; Dabiri, J. O.
- **Venue:** Nature Communications 12:7143
- **DOI:** 10.1038/s41467-021-27015-y
- **Link:** <https://www.nature.com/articles/s41467-021-27015-y>
- **Topic:** RL navigation in flows
- **Plain-language summary:** Trains a fixed-speed swimmer with deep RL to go point-to-point through an unsteady cylinder wake. A policy that senses local flow velocity reaches the target almost every time and approaches the travel time of a global optimal-control planner, clearly beating a policy that senses vorticity.
- **Supports this part of the project:** Deep-read method paper; observation design (local current); RL-vs-planner comparison
- **Limitation:** One flow (cylinder wake); time objective only, no energy model; no unseen-flow test.
- **Verification:** Nature article page + PMC8654940 + arXiv 2102.10536; topic verified as requested. Open access.

### R2. Optimal control of point-to-point navigation in turbulent time dependent flows using reinforcement learning (2021)

- **Authors:** Buzzicotti, M.; Biferale, L.; Bonaccorso, F.; Clark di Leoni, P.; Gustavsson, K.
- **Venue:** AIxIA 2020 - Advances in Artificial Intelligence, LNCS 12414, pp. 223-234 (Springer, 2021)
- **DOI:** 10.1007/978-3-030-77091-4_14
- **Link:** <https://link.springer.com/chapter/10.1007/978-3-030-77091-4_14>
- **Topic:** RL navigation in flows (Zermelo)
- **Plain-language summary:** Follow-up to the Chaos paper that contrasts the deterministic optimal-navigation solution with stochastic RL policies in time-dependent turbulence. Actor-critic RL again finds near-optimal paths in both frozen and chaotic flows.
- **Supports this part of the project:** Supports claim that RL is competitive with optimal control in time-varying flow
- **Limitation:** Short proceedings paper; time-only objective; idealised turbulence.
- **Verification:** Springer chapter page + arXiv 2103.00329; LNCS volume and pages confirmed.

### R3. Optimal path planning of autonomous marine vehicles in stochastic dynamic ocean flows using a GPU-accelerated algorithm (2022)

- **Authors:** Chowdhury, R.; Subramani, D. N.
- **Venue:** IEEE Journal of Oceanic Engineering 47(4):864-879 (arXiv:2109.00857)
- **DOI:** 10.1109/JOE.2022.3152514
- **Link:** <https://arxiv.org/abs/2109.00857>
- **Topic:** AUV/glider path planning
- **Plain-language summary:** Builds and solves a Markov decision process for marine-vehicle routing in uncertain, time-varying ocean flows entirely on a GPU, reporting 600-1000x speed-ups over CPU code. Shows how 'planning under current uncertainty' is done with dynamic programming rather than learning.
- **Supports this part of the project:** Alternative baseline family (MDP/DP); uncertainty in currents
- **Limitation:** Requires an ensemble flow model and a GPU; plans rather than learns a reusable policy.
- **Verification:** arXiv abstract + IISc eprints + library record; JOE volume/issue/pages/DOI from library record.

### R4. On the convergence of a reinforcement learning process to a generalized energy-optimal guidance policy for unmanned underwater vehicles (2024)

- **Authors:** Greeley, B.; Brandman, J.; Book, J.; Barron, C.; Landry, B.; Olson, C.
- **Venue:** OCEANS 2024 (IEEE)
- **DOI:** 10.1109/OCEANS55160.2024.10754109
- **Link:** <https://doi.org/10.1109/OCEANS55160.2024.10754109>
- **Topic:** RL energy-optimal guidance
- **Plain-language summary:** Trains a deep-RL guidance agent to minimise energy for an underwater vehicle in current profiles that vary randomly with depth. The learned behaviour is to dive once to explore, then return to the most favourable depth and ride it, trading descent cost against uncertain gain.
- **Supports this part of the project:** Energy objective in RL guidance; interpretable learned behaviour (good discussion point)
- **Limitation:** Currents vary with depth but are time-stationary; abstract-level information only.
- **Verification:** Library discovery record (Summon) with DOI, abstract and full author names; IEEE Xplore page not opened.

### R5. Sensing flow gradients is necessary for learning autonomous underwater navigation (2025)

- **Authors:** Jiao, Y.; Hang, H.; Merel, J.; Kanso, E.
- **Venue:** Nature Communications 16:3044
- **DOI:** 10.1038/s41467-025-58125-6
- **Link:** <https://www.nature.com/articles/s41467-025-58125-6>
- **Topic:** RL navigation in flows (sensing)
- **Plain-language summary:** Studies what an RL swimmer must sense to navigate unsteady flows: knowing local flow speed is enough when the agent knows its global position, but navigating from an egocentric view also needs local flow gradients. A careful look at observation design.
- **Supports this part of the project:** Observation design (why the 5x5 current patch is a gradient-like signal)
- **Limitation:** Idealised wake flows; no energy model or glider constraints.
- **Verification:** Nature article page + DOAJ/RePEc records + author-hosted PDF; authors, volume, article number confirmed.

### R6. A critical assessment of reinforcement learning methods for microswimmer navigation in complex flows (2025)

- **Authors:** Mecanna, S.; Loisy, A.; Eloy, C.
- **Venue:** European Physical Journal E (2025); arXiv:2505.05525
- **DOI:** none / not applicable (use URL)
- **Link:** <https://arxiv.org/abs/2505.05525>
- **Topic:** RL navigation in flows (evaluation)
- **Plain-language summary:** Benchmarks the RL algorithms commonly used in the flow-navigation literature on one navigation task in three flows (Taylor-Green vortices, ABC flow, 2-D turbulence). Tabular Q-learning and A2C, still widely used, perform poorly and are not robust; deep RL only works with careful choice of algorithm, implementation and tuning. It also points to earlier work where RL failed to beat a simple physics-based heuristic.
- **Supports this part of the project:** Deep-read gap paper; justifies the strong baselines + multi-seed + CI protocol
- **Limitation:** Microswimmer setting (no energy, no vehicle model); journal DOI not opened.
- **Verification:** arXiv abstract/HTML pages; EPJE publication as stated in the record - confirm DOI on arXiv page.

### R7. Efficient navigation in vortical flows based on reinforcement learning and flow field prediction (2025)

- **Authors:** Zhang, Y.; ...; Cai, S. (full author list on ScienceDirect page)
- **Venue:** Ocean Engineering 327:120937
- **DOI:** 10.1016/j.oceaneng.2025.120937
- **Link:** <https://www.sciencedirect.com/science/article/abs/pii/S002980182500650X>
- **Topic:** RL navigation in flows (PPO, double gyre)
- **Plain-language summary:** Pairs a learned flow-prediction model with a PPO agent so that a vehicle slower than the flow can 'look ahead' when solving a Zermelo-type point-to-point task, tested in a double gyre and a cylinder flow. Code is public (FieldNav-LASS).
- **Supports this part of the project:** Closest recent method (PPO + double gyre + Zermelo); novelty check
- **Limitation:** Time/success focus, not an explicit energy-time trade-off; author list must be copied from the page.
- **Verification:** ScienceDirect abstract page + official GitHub README (piao233/FieldNav-LASS) giving the DOI. Only first/last author seen.

### R8. Khalasi: energy-efficient navigation for surface vehicles in vortical flow fields (2025)

- **Authors:** Gadhvi, R.; Manjanna, S.
- **Venue:** arXiv:2512.06912 (preprint, stated as under review)
- **DOI:** none / not applicable (use URL)
- **Link:** <https://arxiv.org/abs/2512.06912>
- **Topic:** RL energy-aware navigation in flows
- **Plain-language summary:** Uses Soft Actor-Critic with only local velocity measurements to make a surface vehicle exploit vortical flows and save energy, reporting 30-50% better energy conservation than prior methods. It argues that grid planners like A*/Dijkstra assume a time-invariant flow.
- **Supports this part of the project:** Energy-aware RL precedent; argument against static-grid planners
- **Limitation:** Not peer reviewed; surface vehicle, not a buoyancy-driven glider.
- **Verification:** arXiv abstract + HTML pages.

### R9. Online navigation planning for long-term autonomous operation of underwater gliders (2026)

- **Authors:** Darvariu, V.-A.; Hawes, N.; et al. (24 authors)
- **Venue:** arXiv:2602.19315 (preprint, v2 April 2026)
- **DOI:** none / not applicable (use URL)
- **Link:** <https://arxiv.org/abs/2602.19315>
- **Topic:** Glider path planning (field)
- **Plain-language summary:** Models multi-dive glider navigation under uncertain current forecasts as a stochastic shortest-path MDP and solves it online with Monte Carlo Tree Search, re-planning at each surfacing. Tested on real Slocum gliders over about 3 months and 1000 km in the North Sea, improving on straight-to-goal navigation.
- **Supports this part of the project:** Real-world glider gap: shows what field systems use (planning, straight-to-goal baseline); future-work slide
- **Limitation:** Preprint; planner rather than a learned policy; North-Sea-specific results.
- **Verification:** arXiv abstract + HTML v1/v2.

### R10. Flow-aware optimal navigation in unsteady flows through reinforcement learning (2026)

- **Authors:** Braghin, A. M.; Botteghi, N.; Tomasetto, M.; Manzoni, A.; Cazzulani, G.
- **Venue:** arXiv:2607.13553 (preprint)
- **DOI:** none / not applicable (use URL)
- **Link:** <https://arxiv.org/abs/2607.13553>
- **Topic:** RL navigation in flows (energy, double gyre)
- **Plain-language summary:** Trains TD3 agents to reach arbitrary targets in a parametric chaotic double-gyre flow and compares sensors: velocity-aware agents are more energy-efficient, vorticity-aware ones get closer to targets, and feeding global flow parameters hurts.
- **Supports this part of the project:** Very close recent work (double gyre, energy, sensing) - must be cited in novelty statement
- **Limitation:** Preprint; double gyre only; no classical-planner baseline mentioned in the abstract.
- **Verification:** arXiv abstract + PDF listing.

## Simulation / implementation (5)

### I1. Stable-Baselines3: reliable reinforcement learning implementations (2021)

- **Authors:** Raffin, A.; Hill, A.; Gleave, A.; Kanervisto, A.; Ernestus, M.; Dormann, N.
- **Venue:** Journal of Machine Learning Research 22(268):1-8
- **DOI:** none / not applicable (use URL)
- **Link:** <https://jmlr.org/papers/v22/20-1364.html>
- **Topic:** RL tools (SB3)
- **Plain-language summary:** Describes the Stable-Baselines3 library: tested, documented PyTorch implementations of standard deep-RL algorithms (including PPO), benchmarked against reference code. Cite it as the PPO implementation used.
- **Supports this part of the project:** Implementation slide; reproducibility
- **Limitation:** A software paper: no navigation results; default hyperparameters are not tuned for this task.
- **Verification:** JMLR abstract page and PDF.

### I2. Gymnasium: a standard interface for reinforcement learning environments (2024)

- **Authors:** Towers, M.; et al. (16 authors)
- **Venue:** arXiv:2407.17032
- **DOI:** none / not applicable (use URL)
- **Link:** <https://arxiv.org/abs/2407.17032>
- **Topic:** RL tools (Gymnasium)
- **Plain-language summary:** Presents Gymnasium, the maintained successor of OpenAI Gym, which defines the reset/step API, spaces and wrappers so environments and algorithms interoperate. The project's environment follows this interface and its check_env test.
- **Supports this part of the project:** Environment design slide
- **Limitation:** Pure-Python environments are slow compared with compiled ones (the authors say so).
- **Verification:** arXiv abstract page.

### I3. Deep reinforcement learning at the edge of the statistical precipice (2021)

- **Authors:** Agarwal, R.; Schwarzer, M.; Castro, P. S.; Courville, A.; Bellemare, M. G.
- **Venue:** NeurIPS 2021 (Advances in Neural Information Processing Systems 34)
- **DOI:** none / not applicable (use URL)
- **Link:** <https://proceedings.neurips.cc/paper/2021/file/f514cec81cb148559cf475e7426eed5e-Paper.pdf>
- **Topic:** RL evaluation
- **Plain-language summary:** Shows that reporting a single mean over a few training runs is statistically fragile, and recommends bootstrap confidence intervals, performance profiles and the interquartile mean. Outstanding Paper award at NeurIPS 2021.
- **Supports this part of the project:** Evaluation-protocol slide: 5 training seeds, bootstrap CIs, no single-seed claims
- **Limitation:** Designed for multi-task benchmarks; adapting it to one environment family needs care.
- **Verification:** NeurIPS proceedings PDF + poster page + awards page.

### I4. The HYCOM (HYbrid Coordinate Ocean Model) data assimilative system (2007)

- **Authors:** Chassignet, E. P.; Hurlburt, H. E.; Smedstad, O. M.; Halliwell, G. R.; Hogan, P. J.; Wallcraft, A. J.; Baraille, R.; Bleck, R.
- **Venue:** Journal of Marine Systems 65:60-83
- **DOI:** 10.1016/j.jmarsys.2005.09.016
- **Link:** <https://doi.org/10.1016/j.jmarsys.2005.09.016>
- **Topic:** Ocean-current data
- **Plain-language summary:** Describes HYCOM, the eddy-resolving ocean model and data-assimilation system behind widely used ocean-current hindcasts and forecasts. It is the obvious source of realistic currents if the synthetic fields are ever replaced.
- **Supports this part of the project:** Future-work slide (real currents); 'why synthetic fields first' discussion
- **Limitation:** System description from 2007; using the data needs large downloads and regridding.
- **Verification:** NOAA AOML PDF + CU VIVO record + DTIC copy; author list, pages and DOI agree.

### I5. Global observations of nonlinear mesoscale eddies (2011)

- **Authors:** Chelton, D. B.; Schlax, M. G.; Samelson, R. M.
- **Venue:** Progress in Oceanography 91(2):167-216
- **DOI:** 10.1016/j.pocean.2011.01.002
- **Link:** <https://www.doi.org/10.1016/J.POCEAN.2011.01.002>
- **Topic:** Eddy models (parameter sanity check)
- **Plain-language summary:** Tracks about 36,000 long-lived ocean eddies in 16 years of satellite sea-surface height and reports how big, strong, long-lived and nonlinear they are and how they drift (mostly westward). Use it to sanity-check the radii and speeds chosen for the synthetic Gaussian eddies.
- **Supports this part of the project:** ASSUMPTIONS.md: are 5-12 km, 0.1-0.5 m/s eddies realistic?
- **Limitation:** Satellite altimetry only resolves mesoscale eddies; compare its radius distribution with the project's small synthetic eddies before claiming realism.
- **Verification:** DOI resolver page + UMN and WHOI-hosted PDFs; numbers quoted (35,891 eddies, 16 years) appear in the abstract.

## Coverage by project topic

- **Glider modelling and control:** S1, C2
- **Zermelo / flow-aware navigation:** C1, C5, C6, C10
- **RL for navigation in flows:** S5, C8, C10, R1, R2, R5, R6, R7, R8, R10
- **AUV / glider path planning:** S2, S3, C3, C6, R3, R9
- **RL tools: PPO, SB3, Gymnasium, reward shaping, evaluation:** C7, C9, I1, I2, I3
- **Ocean-current data and eddy models:** C4, I4, I5
- **Energy-aware objectives:** C6, R4, R8, R10
- **Data-driven marine control (survey):** S4

## Verified further reading (not counted in the 30)

| Authors (year) | Title | Venue | Link | Why it might be useful |
|---|---|---|---|---|
| Techy, L. (2011) | Optimal navigation in planar time-varying flow: Zermelo's problem revisited | Intelligent Service Robotics 4:271-283 | <https://doi.org/10.1007/s11370-011-0092-9> | Pontryagin-based analytic Zermelo solutions; nice for the theory slide. |
| Bellemare, M. G.; Candido, S.; Castro, P. S.; et al. (2020) | Autonomous navigation of stratospheric balloons using reinforcement learning | Nature 588:77-82 | <https://www.nature.com/articles/s41586-020-2939-8> | RL steering a vehicle that can only exploit a flow (wind), deployed for real. 2020, so neither 'recent' nor counted. |
| Andrychowicz, M.; et al. (2021) | What matters in on-policy reinforcement learning? A large-scale empirical study | ICLR 2021 / arXiv:2006.05990 | <https://arxiv.org/abs/2006.05990> | 250k agents, 50+ PPO-style design choices; use for hyperparameter justification. |
| Henderson, P.; Islam, R.; Bachman, P.; Pineau, J.; Precup, D.; Meger, D. (2018) | Deep reinforcement learning that matters | AAAI 2018, 32(1) | <https://ojs.aaai.org/index.php/AAAI/article/view/11694> | Why multiple seeds and careful baselines are required. |
| Liao, X.; Li, L.; Huang, C.; Zhao, X.; Tan, S. (2024) | Noisy dueling double deep Q-network algorithm for autonomous underwater vehicle path planning | Frontiers in Neurorobotics 18, doi:10.3389/fnbot.2024.1466571 | <https://www.frontiersin.org/journals/neurorobotics/articles/10.3389/fnbot.2024.1466571/full> | Grid-based DRL for AUVs with a current term in the reward; reports ~93% success vs RRT*/DQN/D3QN. |
| Potokar, E.; Ashford, S.; Kaess, M.; Mangelson, J. (2022) | HoloOcean: an underwater robotics simulator | ICRA 2022, pp. 3040-3046 | <https://www.ri.cmu.edu/publications/holoocean-an-underwater-robotics-simulator> | High-fidelity Unreal-Engine simulator (sensors, sonar); overkill for 2-D routing but a credible 'next step'. |
| MarineGym authors (2025) | MarineGym: a high-performance reinforcement learning platform for underwater robotics | IROS 2025 / arXiv:2503.09203 | <https://arxiv.org/abs/2503.09203> | GPU RL platform for UUV control tasks; see novelty_check.md. |
| Doering et al. (2023) | Stranding risk for underactuated vessels in complex ocean currents: analysis and controllers | arXiv:2307.01917 | <https://arxiv.org/abs/2307.01917> | Uses HYCOM/Copernicus hindcasts; reachability-based (not RL) control of weakly actuated vessels. |
| Killer, M.; Wiggert, M.; Krasowski, H.; Doshi, M.; Lermusiaux, P.; Tomlin, C. (2023) | Maximizing seaweed growth on autonomous farms: a dynamic programming approach for underactuated systems navigating on uncertain ocean currents | arXiv:2307.01916 | <https://arxiv.org/abs/2307.01916> | Forecast-based DP for low-power ocean platforms; strong non-RL comparator. |

## UNVERIFIED (do not cite until checked; not counted)

| Authors (year) | Title | Venue | Link seen | Problem |
|---|---|---|---|---|
| Unknown authors (2022) | Path planning for underwater gliders in time-varying ocean current using deep reinforcement learning | Ocean Engineering (2022) | <https://www.sciencedirect.com/science/article/abs/pii/S0029801822015372> | Page exists but authors were not visible and two records disagree on the method (DDPG vs DDQN) and on whether it is about a single glider or a formation. Open the page and copy authors/DOI before using. |
| Unknown authors (2024) | Based on deep reinforcement learning to path planning in uncertain ocean currents for underwater gliders | Ocean Engineering (2024) | <https://www.sciencedirect.com/science/article/abs/pii/S0029801824008382> | Only title and an abstract snippet seen; authors/DOI not confirmed. |
| Gao (year unknown) | Reinforcement learning-based path planning for underwater gliders using ocean current forecasts | Ocean Engineering (as cited by Darvariu et al. 2026) | (no page found) | Seen only as a citation inside arXiv:2602.19315 (SAC policy on forecast currents). Could not find the paper's own page. |
| Wiggert, M.; Doshi, M.; Lermusiaux, P. F. J.; Tomlin, C. J. (2022) | Navigating underactuated agents by hitchhiking forecast flows | IEEE CDC 2022, pp. 2417-2424 (as cited) | (publisher page not opened) | Seen only in reference lists of later arXiv papers. |
| Cichos, F.; Gustavsson, K.; Mehlig, B.; Volpe, G. (2020) | Machine learning for active matter | Nature Machine Intelligence 2:94-103 (as cited) | (publisher page not opened) | Seen only as consistent citations in other papers; likely a good survey but not verified here. |
| Ullah, B.; et al. (2015) | Underwater gliders control strategies: a review | venue not confirmed | <https://khub.utp.edu.my/scholars/5752> | Repository record only; venue/DOI not visible. |
| Yoo, B.; Kim, J. (2016) | Path optimization for marine vehicles in ocean currents using reinforcement learning | venue not verified | <https://www.researchgate.net/publication/286481801_Path_optimization_for_marine_vehicles_in_ocean_currents_using_reinforcement_learning> | Only the ResearchGate title appeared in search; venue/year/DOI not verified. Potentially a useful early RL-in-currents reference. |
