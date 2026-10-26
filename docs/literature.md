# Evidence map

What each study varied and which controls it used. `?` means not checked. The **Read** column says how much of the source was checked: `full` (paper text), `abstract`, `excerpt` (search-result excerpt), or `secondary` (someone else's summary).

## Whole-harness comparisons

| Study | Varied | Repeats / intervals | Equal spend | Size sweep | Key finding | Read |
|---|---|---|---|---|---|---|
| [HarnessTax](https://arena.ai/blog/coding-agents-harness-tax) (Arena/Berkeley, Sep 2026) | 7 models × Claude Code, Codex, Pi; SWE-bench Lite + Terminal-Bench 2.0, 30 tasks each | 3 runs/task; bootstrap CIs | reports cost | no | Success within a few points; cost up to 5×. Pi on the cost/success frontier. | full |
| [What Does a Harness Buy?](https://arxiv.org/abs/2610.04433) (Oct 2026) | Claude Code, mini-SWE-agent, OpenCode; SWE-bench Verified | reruns to set a noise floor | reports cost | no | Swapping harnesses flips 13% of tasks, same as rerunning. 45 tasks can't reliably detect a 13-point gap. Cost differs up to 3×. | abstract + press |
| [Scaffold Effect](https://arxiv.org/abs/2607.22585) (2026) | Goose, OpenCode, OpenHands-SDK; Terminal-Bench Pro, 50 tasks | paired bootstrap CIs | reports tokens | no | Up to 40× tokens per solved task; pass-rate gaps 0–8 pts, mostly within CIs. | excerpt |
| [Harness-Bench](https://www.alphaxiv.org/abs/2605.27922) (2026) | 7 harnesses × 10 models, 300 workflow tasks | single run | reports cost | no | Higher-scoring models are less harness-sensitive (ρ = −0.76). No harness leads across all models. | secondary |
| [Prime Agent](https://arxiv.org/abs/2608.23552) (Aug 2026) | Prime Agent vs Pi, Claude Code, Codex, native CLIs | "uncertainty intervals are unavailable" | partly (ARC curves) | no | See [claims.md](claims.md). | full |

## Component-level studies

| Study | Components varied | Design | Equal info | Repeats / tests | Size sweep | Key finding | Read |
|---|---|---|---|---|---|---|---|
| [Empirical Study of Harness Design](https://arxiv.org/abs/2609.20804) (Sep 2026) | planning, action space, context management (5 strategies) | one-at-a-time from a full baseline | n/a | McNemar + Benjamini–Hochberg | context budget 32k–128k | Context management matters under tight budgets; planning helps weak models, saves cost for strong ones; bash-only works for bash-capable models. | abstract + excerpt |
| [Beyond the Model / NanoHarness](https://arxiv.org/html/2609.32459) (Sep 2026) | tool registry, compression, planning, subagents, lazy skills | add-one + all-on | n/a | ? | no | Task-specific subagents and tools help; compression and generic subagents hurt on ProgramBench. Combined gain is not the sum. | excerpt |
| AHE (Agentic Harness Engineering) | evolved harness components | ablation | ? | ? | ? | Reported: individual gains sum to +11.1 pts, full system +7.3 (subadditive). | secondary only |
| [Recursive Language Models](https://arxiv.org/abs/2512.24601) (v3, May 2026) | context offloading; sub-call depth 0–3 | ablation by depth; Claude Code / OpenCode with and without offloading | partly (offload baselines use a different model) | ? | input 2^13–2^18 tokens | Offloading explains most gains on CodeQA and BrowseComp+; sub-calls win on information-dense OOLONG-Pairs. | full (v1) + excerpt (v3) |
| [Coding Agents for Long Context](https://xunjianyin.github.io/papers/coding-agents-long-context.html) | unmodified Codex / Claude Code with text as files | vs RAG, ReAct, RLM | yes | ? | ? | Plain coding agents with files beat published bests on 4 of 5 long-context benchmarks. | excerpt |

## Harness evolution and self-improvement

| Study | Question | Controls | Key finding | Read |
|---|---|---|---|---|
| [Rethinking the Evaluation of Harness Evolution](https://arxiv.org/abs/2607.12227) (Jul–Oct 2026) | Does evolution beat simple test-time scaling? | matched feedback and inference budgets; held-out tasks | No on Terminal-Bench 2.1; yes on ARC-AGI-3 (+80%) and EdgeBench games (+11%). Limited generalization. | abstract |
| [Harness-Delta Attribution](https://arxiv.org/html/2610.22466) (Oct 2026) | Where do evolution gains come from? | compute-matched baseline; neutralized shortcuts; held-out | Held-out gain smaller than search-set gain in 13 of 15 settings, under half in 8. | excerpt |
| [Elicitation or Expansion?](https://arxiv.org/abs/2610.27889) (Oct 2026) | More reliable success vs new solvable tasks | pass@k curves | pass@1 advantages can reverse at larger k; aggregate gains hide shortfalls on hard tasks. | abstract |
| [HarnessDev](https://arxiv.org/html/2609.01437) (Sep 2026) | Can models build and evolve harnesses? | hidden held-out tasks | Generated harnesses lag mature ones on code and search; evolution gains unstable and transfer partially. | excerpt |
| [Continual Harness](https://arxiv.org/abs/2605.09998) (May 2026) | Online self-refinement for embodied agents (Pokémon) | vs minimal and hand-engineered harnesses | Recovers most of the gap to an expert harness from a minimal start. | abstract |

## Methodology references

- METR, [Metrics of Agent Ability](https://metr.org/notes/2026-07-24-metrics-of-model-ability/) (Jul 2026): score at fixed expenditure vs score at practical plateau vs expenditure at fixed score vs returns to expenditure.
- [Harness Engineering: Anatomy of Eleven Systems](https://arxiv.org/abs/2609.00006) (Jul 2026): source-code study of 11 coding harnesses; 7 subsystems, 29 patterns; harnesses converging by imitation.
- [Scaling Laws for Agent Harnesses via Effective Feedback Compute](https://arxiv.org/html/2605.29682v1) (May 2026): harness efficiency, not raw compute, explains success in their module ablations. Excerpt only.
- [STITCH: Composing Task-specific Harnesses](https://arxiv.org/html/2609.38912) (Sep 2026): a fixed harness is suboptimal across heterogeneous tasks; composes reusable primitives per task. Excerpt only.
