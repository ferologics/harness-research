# TODO

## Now

- [x] Prime Agent switches read from source (results in [docs/primitives.md](docs/primitives.md#matched-reference-points))
- [x] `pi-acp` 0.0.34 drives Pi 1.4.0 end to end; verifiers upstream already pins both (`32c1f14`)
- [x] SWE-rebench-V2 2025 tasks map 1:1 to public `swerebenchv2/` Docker Hub tags (40 of 40 sampled exist)
- [ ] Smoke-run Prime Agent through the verifiers adapter: does refinement run with `--no-session`?
- [ ] Harness subclasses in this repo: Pi with dual extensions per rung; Prime Agent with `settings.json` and `RLM_MAX_DEPTH`

## Setup

- [ ] Linux box: Docker with the NVIDIA runtime; serve stock Qwen3.8-27B (pin engine build, quantization, chat template, sampling); test one OpenAI-compatible request with tool calls.
- [ ] Install verifiers and prime-envs; run `swerebench_v2` on one task with the `bash` harness against the local model.
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
- [ ] B (conditional): decide from A3 whether GLM-5.2 runs are worth it, and which

## Later

- [ ] Memory track: [experiments/memory-sequences/PLAN.md](experiments/memory-sequences/PLAN.md)
- [ ] NL2RepoBench whole-repo stratum
- [ ] OOLONG on the local GPU only, if still interesting
- [ ] Weekly literature-watch job feeding [docs/literature.md](docs/literature.md)
