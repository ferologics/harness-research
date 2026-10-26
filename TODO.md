# TODO

## Now: checks that could still change the plan

- [ ] Prime Agent switches: does `rlmMaxDepth: 0` disable spawning; what does `harnessRefinements: false` turn off; how do settings reach the verifiers adapter?
- [ ] `pi-acp` 0.0.34 with Pi 1.4.x: does it work? If not, fix it upstream or drive Pi in print mode.
- [ ] SWE-rebench-V2 images: map Prime-registry tags to public `docker.io/swerebenchv2/...` images; pull a few to confirm.

## Setup

- [ ] Linux box: Docker with the NVIDIA runtime; serve stock Qwen3.8-27B (pin engine build, quantization, chat template, sampling); test one OpenAI-compatible request with tool calls.
- [ ] Install verifiers and prime-envs; run `swerebench_v2` on one task with the `bash` harness against the local model.
- [ ] Upstream PR to verifiers: Pi adapter on Pi 1.4.x with an `extensions` option.
- [ ] Ask Seth Karten the open questions in [docs/claims.md](docs/claims.md#open-questions-for-the-authors).

## Build the duals (in ladder order)

Each dual gets a spec (Prime source file and commit, deliberate differences) and a smoke test. See [docs/primitives.md](docs/primitives.md).

- [ ] L1 Python REPL as the only interface (`bash()` with completion notices, `edit()`)
- [ ] L2 subagents
- [ ] L3 agent messaging
- [ ] L4 continual harness and refine (prompts ported verbatim)
- [ ] L5 general guidance text
- [ ] T4 tool wrappers: L2–L4 as plain Pi tools, same backends, no REPL

## Run the ladder

- [ ] A1 smoke: 3 tasks × 11 arms; record time per run
- [ ] Build the candidate list: 30 tasks per stratum, one per repo ([scripts/swerebench_pool.py](scripts/swerebench_pool.py))
- [ ] A2 screening: L0 and P on 90 candidates; select the subset
- [ ] Freeze [experiments/ladder/PLAN.md](experiments/ladder/PLAN.md)
- [ ] A3 main runs
- [ ] B: GLM-5.2 smoke for cost, then L0, L5, P on 25 tasks

## Later

- [ ] Memory track: [experiments/memory-sequences/PLAN.md](experiments/memory-sequences/PLAN.md)
- [ ] NL2RepoBench whole-repo stratum
- [ ] OOLONG on the local GPU only, if still interesting
- [ ] Weekly literature-watch job feeding [docs/literature.md](docs/literature.md)
