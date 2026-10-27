# Decisions

Agreed decisions with their reasons. Read this before proposing anything. A proposal that conflicts with an entry needs explicit agreement to reopen it.

## Scope

| Decision | Why |
|---|---|
| The target is coding. Long-context benchmarks (OOLONG and similar) are deferred and run only on the local GPU, if at all. | Pi and Prime Agent are coding harnesses. OOLONG is synthetic aggregation, the RLM approach's home ground, and says little about coding. |
| The concrete case is Prime Agent vs Pi. | Prime Agent claims to match or beat Pi and to be "more than a sum of its parts"; its only direct Pi comparison is one table, one model, no intervals. |
| Vendor benchmarks with a handful of tasks (for example Empryo's) are not evidence. | Four bugs, one or two runs, tasks chosen by the vendor. |

## Design

| Decision | Why |
|---|---|
| The baseline is Pi as shipped, current release (1.4.x). No old Pi versions. | The question is about Pi today. |
| Each Prime Agent building block gets an objective Pi dual, built in this repo: same mechanism, same trigger, model-facing text ported from Prime Agent, Prime's defaults, nothing extra. Third-party Pi packages and the maintainer's personal Pi setup are never used as arms. | The comparison must be reviewable and independent of anyone's configuration. |
| The main design is zero to hero: Pi as shipped, then one dual at a time, up to Prime Agent's set of building blocks. Prime Agent runs beside the ladder, with its own switches turned off at matching rungs. | Shows whether Pi with Prime's building blocks performs like Prime Agent, and which block moves results. |
| The REPL enters the ladder once, as Prime Agent's only interface (L1). There is no optional-REPL rung. A tools-only arm (T4) carries the subagents, messaging, and memory duals without the REPL. | An optional REPL next to Pi's tools is not a Prime Agent building block. T4 answers "does the REPL matter?" in one 2×2 (interface × building blocks) instead of more REPL rungs. |
| The memory dual ports Prime Agent's continual harness and refine (prompts verbatim). pi-mem, pi-reflect, and similar packages are not used. | Faithful to the claim being tested. |
| Experiments are pre-registered; calibration uses only dev tasks. | Avoids tuning toward results. |

## Models, money, and infrastructure

| Decision | Why |
|---|---|
| Breadth runs use stock Qwen3.8-27B served locally on the RTX 5090 (Linux). Measured runs never use uncensored or abliterated variants. | Free runs; stock weights keep results reproducible and comparable. |
| Confirmation runs use GLM-5.2 (the paper's model) through Prime Inference, within the $150 credit. | Matches the paper; the credits exist. |
| GLM-5.2 runs happen only if the local results show something worth confirming; what to run is decided after the local main runs. | Avoids spending on a question the local data may already answer. |
| The eval stack is Prime Intellect's `verifiers` v1 with `prime-envs` tasksets on a Docker runtime. Loading the duals and setting Prime Agent's switches happen in small harness subclasses in this repo; no fork of verifiers. | Their infrastructure, uniform token accounting. Upstream already runs current Pi (`32c1f14`). |
| Tasks come from existing public benchmarks, sliced for signal and cost. First: SWE-rebench-V2 (2025+, strata by files changed in the fix). Later: NL2RepoBench whole-repo builds. Memory track: same-repo SWE-rebench-V2 sequences. | Real coding, public, a size knob, cost-sensitive. |
| Recursive Task Synthesis is not used for now. | Mostly short "easy" terminal tasks (2–10 minute expert estimates); no labelled round field to use as a horizon knob. |
