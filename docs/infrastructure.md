# Infrastructure

## Eval stack

- **[verifiers](https://github.com/PrimeIntellect-ai/verifiers)** (MIT). The v1 API runs a taskset with a pluggable harness inside a container. All model calls pass through its interception proxy, which records the trace and counts tokens the same way for every harness. Runtime backends: `docker`, `prime`, `subprocess`, `custom`.
- **[prime-envs](https://github.com/PrimeIntellect-ai/prime-envs)** tasksets, including `swe/swerebench_v2` and `code/nl2repobench`.

Checked at verifiers `32c1f14` (Oct 26 2026) and prime-envs `ff6abb4` (Oct 22 2026).

## Harness adapters

An adapter is verifiers' per-harness code: it installs the harness in the task container, points its model calls at the proxy, sends the task prompt, and collects the result.

| Adapter | Pinned version | Notes |
|---|---|---|
| `pi` | Pi `1.4.0` through `pi-acp 0.0.34`; MCP through Pi's built-in support | Upstream bumped in `32c1f14` (#2988). Runs in a fresh agent directory, so no personal settings load. Loads one extension of its own (the tool gate). |
| `prime_agent` | `v0.10.1`, commit `8aac869` | Config: `autonomous` (default false), `dialect`, `env`. Passes `--no-session`, which may disable refinement (see [primitives.md](primitives.md#matched-reference-points)). |

Our arms need two things the adapters don't offer: loading the dual extensions into Pi, and writing Prime Agent's `settings.json`. Both go into small harness subclasses in this repo, loaded through verifiers' plugin loader, so no upstream change is needed.

`pi-acp 0.0.34` drives Pi 1.4.0 end to end: initialize, new session, a prompt with one bash tool call and its result, final answer (tested on macOS against a fake OpenAI-compatible server, outside verifiers).

## Task data

### SWE-rebench-V2 (ladder, memory track)

Prime Intellect's filtered and verified set, `PrimeIntellect/SWE-rebench-V2-Filtered-Verified` ([scripts/swerebench_pool.py](../scripts/swerebench_pool.py)):

- 6,272 tasks across 1,890 repos, created 2014–2025.
- 2025 or later: 544 tasks across 332 repos. Files changed in the reference fix: 1 file 178, 2–4 files 242, 5+ files 124.
- Repos with at least 10 tasks: 106 repos, 1,954 tasks.
- Every image reference points to Prime's registry (`prime/primeintellect/<repo>:<tag>`), which Docker cannot pull. All 544 tasks from 2025 match Nebius' `nebius/SWE-rebench-V2` by `instance_id` with the same `<repo>:<tag>`, and 40 of 40 sampled tags exist on Docker Hub under `swerebenchv2/`. Whether the image contents are identical is not checked.

### NL2RepoBench (later stratum)

104 tasks: generate a whole Python repository from a natural-language spec; score is the hidden pytest pass rate. Canonical images are public on GHCR for the Docker runtime.

### OOLONG (deferred)

Counts from [scripts/oolong_counts.py](../scripts/oolong_counts.py): oolong-synth validation 1,300 rows (`spam`, `trec_coarse`), test 5,200 rows (8 datasets); 50 questions over 2 context windows (25 each) per dataset and context length. The paper's "OOLONG (Yahoo, 128k)" row is the test split, `yahoo`, 131,072 tokens. OOLONG-Pairs: 20 questions per context-length bucket.

## Models and serving

### Local: Qwen3.8-27B on the RTX 5090 (32 GB, Linux)

Stock weights only. Two community-validated setups (Local AI Registry):

| Engine | Weights | Context | Concurrency | Measured decode |
|---|---|---|---|---|
| TabbyAPI / ExLlamaV3 | `turboderp/Qwen3.8-27B-exl3`, 4 bpw, Q4 cache | 262,144 | 2 | 73.7 tok/s (validated) |
| llama.cpp | `unsloth/Qwen3.8-27B-GGUF`, Q4_0, q8_0 cache | 262,144 | 1 | 109 tok/s with speculative decoding; prefill 2,354 tok/s (observed) |

Pin the engine build, quantization, chat template, and sampling settings before phase A1. With one or two requests served at a time, subagent arms run slower locally; local wall time is not a metric.

### Paid: GLM-5.2 through Prime Inference

Gateway model. $1.54 input and $4.84 output per million tokens; no cached-input price listed (catalog checked Oct 26 2026). Budget: $150 credit.

## Hardware

Linux on the RTX 5090 box runs the model server, Docker, and the task containers.
