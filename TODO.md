# TODO

## Now

- [x] Prime Agent switches read from source (results in [docs/primitives.md](docs/primitives.md#matched-reference-points-module-a))
- [x] `pi-acp` 0.0.34 drives Pi 1.4.0 end to end; verifiers upstream already pins both (`32c1f14`)
- [x] SWE-rebench-V2 2025 tasks map 1:1 to public `swerebenchv2/` Docker Hub tags (40 of 40 sampled exist)
- [ ] L1 dual (REPL as the only interface), tested against a fake model server
- [ ] Harness subclasses: Pi with the dual extensions per rung; Prime Agent with `settings.json` and `RLM_MAX_DEPTH`

## Setup (needs the GPU box)

- [ ] Linux box: Docker with the NVIDIA runtime; serve stock Qwen3.8-27B (pin engine build, quantization, chat template, sampling); test one OpenAI-compatible request with tool calls.
- [ ] Install verifiers and prime-envs; run `swerebench_v2` on one task with the `bash` harness against the local model.
- [ ] A0 drive check: L0 and P on 3 dev tasks. Also answers whether refinement runs under the adapter's `--no-session`.
- [ ] Ask Seth Karten the open questions in [docs/claims.md](docs/claims.md#open-questions-for-the-authors).

## Build the duals (core, in ladder order)

Each dual gets a spec (Prime source file and commit, deliberate differences) and a smoke test. See [docs/primitives.md](docs/primitives.md).

- [ ] L1 Python REPL as the only interface (`bash()` with completion notices, `edit()`)
- [ ] L2 subagents
- [ ] L3 agent messaging
- [ ] L4 continual harness and refine (prompts ported verbatim)
- [ ] L5 general guidance text

## Run the ladder

- [ ] A1 smoke: 3 tasks × each core arm; record time per run
- [ ] Build the candidate list: 30 tasks per stratum, one per repo ([scripts/swerebench_pool.py](scripts/swerebench_pool.py))
- [ ] A2 screening: L0 and P on 90 candidates; select the subset
- [ ] Freeze [experiments/ladder/PLAN.md](experiments/ladder/PLAN.md)
- [ ] A3 core runs
- [ ] Decide modules A and B from the core results; record the decision in the plan
- [ ] B (conditional): decide whether GLM-5.2 runs are worth it, and which

## Later

- [ ] Module B build, if it runs: T4 tool wrappers (L2–L4 as plain Pi tools, same backends); C0 and C4 are configuration only
- [ ] Memory track: [experiments/memory-sequences/PLAN.md](experiments/memory-sequences/PLAN.md)
- [ ] NL2RepoBench whole-repo stratum
- [ ] OOLONG on the local GPU only, if still interesting
- [ ] Weekly literature-watch job feeding [docs/literature.md](docs/literature.md)
