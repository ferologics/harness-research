# Ladder: Pi to Prime Agent, one building block at a time

**Status:** draft. Frozen after smoke runs and screening (phases A1–A2); the freeze commit goes here.

## Questions

Core:

1. Does Prime Agent beat Pi as shipped on coding, and does the gap change with task size?
2. Which building block, added to Pi, changes success, cost, or turns?
3. Does Pi with every dual match Prime Agent?

Module A: 4. Inside Prime Agent, do subagents and refinement add up, or more, or less ("more than a sum of its parts")?

Module B: 5. Does Prime Agent's REPL matter beyond what Pi's own codemode gives, on its own or together with the building blocks?

## Arms

Rungs and duals are defined in [docs/primitives.md](../../docs/primitives.md).

### Core (always runs)

| Arm | Harness | Building blocks |
|---|---|---|
| L0 | Pi 1.4.x as shipped | `read`, `write`, `edit`, `bash` |
| L1 | Pi + dual | Python REPL as the only interface |
| L2 | Pi + duals | + subagents |
| L3 | Pi + duals | + agent messaging |
| L4 | Pi + duals | + continual harness and refine |
| L5 | Pi + duals | + Prime's general guidance text |
| P | Prime Agent v0.10.1 | defaults (depth 2, refinements on, autonomous off); refinement must actually be active (see primitives.md on `--no-session`) |

### Module A: Prime Agent's own switches

Runs after the core, unless the core shows Pi matching Prime Agent at every task size.

| Arm | Prime Agent settings | Also serves as |
|---|---|---|
| P-d0r0 | `rlmMaxDepth: 0`, `harnessRefinements: false` | matched point for L1 |
| P-d2r0 | `rlmMaxDepth: 2`, `harnessRefinements: false` | matched point for L3 |
| P-d0r1 | `rlmMaxDepth: 0`, `harnessRefinements: true` | completes the 2×2 |

### Module B: interface

Runs only if the core shows the L0 → L1 step changing success or cost.

| Arm | Harness | Building blocks |
|---|---|---|
| C0 | Pi as shipped, `codemode.mode: only` | none; nothing built |
| T4 | Pi + duals as plain tools | subagents, messaging, continual harness and refine; no REPL |
| C4 | T4 with `codemode.mode: only` | same as T4, called from codemode scripts |

With L0, L1, and L4, Module B forms a 3×2: interface (plain tools, codemode, REPL) × building blocks (none, all three). C0 vs P-d0r0 compares stock Pi codemode with Prime Agent's own REPL; nothing on either side is built by us.

All arms: same model and sampling, same container image per task, same task prompt, same token budget per task (counting subagents), no wall-clock limit.

## Tasks

**Pool:** SWE-rebench-V2, Prime Intellect's filtered and verified set, tasks created in 2025 or later (fewer chances the models trained on the fix). 544 tasks across 332 repos. By number of files in the reference fix: 1 file 178, 2–4 files 242, 5+ files 124 ([scripts/swerebench_pool.py](../../scripts/swerebench_pool.py)).

**Candidates:** 30 per stratum, at most one per repo. Mostly Python, with at least a third in other languages, so the Python REPL is not favoured by the project language.

**Images:** public `docker.io/swerebenchv2/<repo>:<tag>`; all 544 tasks map by `instance_id` to the same tags (see [docs/infrastructure.md](../../docs/infrastructure.md)).

**Later stratum:** NL2RepoBench whole-repo builds (104 tasks, scored by hidden-test pass rate), in phase D.

## Selecting a high-signal subset

Tasks that every arm solves, or no arm solves, carry no information about differences. So:

1. **Screen** every candidate once with L0 and P on the local model (90 tasks × 2 = 180 runs). Screening runs are not used in the analysis.
2. **Keep** every task where L0 and P disagree, plus a random quarter of the tasks both solved and a quarter of those both failed. Weights from these fractions recover pool-level estimates.
3. **Target** 45–60 tasks. With fewer than 30 disagreements, screen more candidates.

## Phases

| Phase | Model | Runs | Purpose |
|---|---|---|---|
| A0 drive check | Qwen3.8-27B (local) | L0 and P on 3 dev tasks | Can the model drive Prime Agent's REPL at all? If not, rethink the model before building more |
| A1 smoke | Qwen3.8-27B | 3 tasks × each core arm | Debug every arm; measure time per run |
| A2 screening | Qwen3.8-27B | 180 | Select the subset |
| A3 core | Qwen3.8-27B | ~50 tasks × 7 arms × 2 runs ≈ 700 | Questions 1–3 |
| A4 module A | Qwen3.8-27B | ~50 × 3 × 2 ≈ 300 | Question 4; locate where duals and Prime diverge |
| A5 module B | Qwen3.8-27B | ~50 × 3 × 2 ≈ 300 | Question 5, only if its condition holds |
| B confirmation (conditional) | GLM-5.2 (Prime Inference) | decided after A3; at most 75 runs, stop at $120 spent | Only if the local results show a difference worth confirming on the paper's model |
| C | | | Memory track: [experiments/memory-sequences](../memory-sequences/PLAN.md) |
| D | Qwen3.8-27B | tbd | NL2RepoBench whole-repo builds |

A third run is added for a contrast only when its interval crosses the decision threshold (rule fixed at freeze). Each module's go or no-go is recorded here, with the core numbers that decided it, before it runs. If phase B runs, its arms and tasks are recorded here before any paid run.

## Metrics

- Solved: the task's hidden tests pass.
- Tokens: input, cached input, output, including subagents.
- Turns (model calls), subagent count, failure category (wrong fix, no patch, budget hit, crash).
- Cost at a fixed price list (phase B).
- Wall time only in phase B: the local server handles one or two requests at a time, so local wall time reflects the server, not the harness.

## Analysis

- Per task, average over runs; compare arms paired by task; bootstrap intervals over tasks.
- Core contrasts: each rung against the one before it; L0 vs P (question 1, also by stratum); L5 vs P (question 3).
- Module A: the depth × refinement interaction from P, P-d0r0, P-d2r0, P-d0r1 (question 4); L1 vs P-d0r0 and L3 vs P-d2r0 (where duals and Prime diverge).
- Module B: L0 vs C0 vs L1, and T4 vs C4 vs L4 (question 5).
- Rough planning numbers: with about 50 informative tasks and 2 runs each, solve-rate differences of about 15–20 points between two arms, and cost differences of about 20%, should be detectable. Smaller differences will read as "no detectable difference."
- The ladder order is fixed (Prime Agent's own layering: REPL first, everything else inside it). A rung's measured gain depends on the rungs below it; that is stated with every result.

## Deviations

None yet.
