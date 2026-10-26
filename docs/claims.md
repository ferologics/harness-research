# Claims under test

Each claim is quoted or closely paraphrased from its source. Interview timestamps are approximate (auto-generated captions, two-minute buckets).

Sources:

- **Paper:** Karten et al., *Prime Agent: A Self-Improving RLM Harness*, [arXiv:2608.23552](https://arxiv.org/abs/2608.23552) (v1, Aug 24 2026).
- **Interview:** Seth Karten on *Deep Learning with Yacine*, Oct 23 2026, [youtu.be/IBf6bdqHgTU](https://youtu.be/IBf6bdqHgTU).
- **Tweet:** Seth Karten (@sethkarten), reply to @ferologics, Oct 26 2026.

| ID | Claim | Source | Testable as | Experiment |
|---|---|---|---|---|
| C1 | Prime Agent matches or beats native and popular harnesses on long-context and long-horizon tasks. | Paper abstract, Table 1 | Whole-harness gap, same model, with repeats and intervals | Ladder: L0 vs P |
| C2 | "Performance scales more than a sum of its parts. And that also includes the model." | Tweet | Positive interaction between building blocks | Ladder: depth × refinement inside Prime Agent; interface × building blocks on Pi; L5 vs P |
| C3 | "Our evals show we still know the secret sauce to do it best," compared with harnesses that adopted a subset of Prime Agent's features. | Tweet | Prime Agent beats Pi given the same building blocks | Ladder: L5 vs P |
| C4 | The ARC-AGI-3 jump came mainly from REPL access plus a "use a world model" prompt; the continual harness matters more where information isn't in the weights. | Interview ~1:36 | Attribution | Not tested (ARC-AGI-3 is not a coding task) |
| C5 | The REPL and refinement of disk state are "non-overlapping procedures." | Interview ~1:38–1:40 | Zero interaction (additivity). In tension with C2. | Partly: interface × building blocks on Pi (L0, L1, T4, L4); the REPL can't be removed inside Prime Agent |
| C6 | Pi is "terrible compared to prime agent" on long-horizon tasks, even with an added subagent. | Interview ~1:46 | Same as the ladder's L0 vs P | Ladder: L0 vs P |
| C7 | Prime Agent is no worse on short-horizon tasks and equal or better on long-horizon ones. | Interview ~1:44–1:46 | Gap by task size | Ladder: L0 vs P by stratum |
| C8 | REPL use cuts input tokens substantially at similar performance (PMPP-Hard). | Interview ~1:54; paper §3.4 | Tokens per task at equal success | Ladder: L0 vs L1 tokens |
| C9 | Adoption of Prime Agent's features by other harnesses is "the genuine evidence." | Tweet | Not a performance claim; not tested | — |

## What the paper's evidence shows

Table 1 (long-context), Prime Agent vs another harness on the same model. Metrics differ by row. The paper states: "Bold is not statistical significance, and uncertainty intervals are unavailable."

| Matchup | Prime higher on | Notable gaps |
|---|---|---|
| vs Pi (GLM-5.2) | 8 of 9 rows | OOLONG .700 vs .420; OOLONG-Pairs .874 vs .556; EmulatorBench .208 vs .000 |
| vs Claude Code (Opus 5) | 6 of 9 | LongCoT-Mini .722 vs .558; ManyIH IF .225 vs .175; other rows within 2 points |
| vs Codex (GPT-5.6 Sol) | 6 of 9 | All rows within 4.7 points |

Table 1 is the paper's only direct comparison with Pi. The rows closest to coding are EmulatorBench (.208 vs .000; the benchmark is not public yet) and ManyIH Coding (.424 vs .386). The paper does not state the Pi version; the verifiers Pi adapter pinned Pi 0.80.6 when it was added in July 2026. The ladder's L0 vs P contrast is the coding counterpart of this table, with current Pi and intervals.

Other sections:

- nanoGPT: "the choice of harness has little effect on final records compared to the noise of the experiment."
- PMPP-Hard: Prime Agent and native harnesses "remain close, with the ordering reversing between the two model groups."
- ARC-AGI-3: compared against published external numbers because the authors' own native-harness reruns scored lower; the paper says these "situate the result rather than isolate a causal harness effect."

The paper contains no component ablations. In the interview (~1:38), Seth says ablations are coming and that the paper's evals are sufficient.

## Open questions for the authors

1. Which evals does the tweet refer to: the paper's, or internal ones?
2. How was Pi configured for Table 1? Adapter and Pi version, and what "an additional sub agent" was.
3. Which OOLONG-Pairs context-length bucket does Table 1 use?
4. How many runs per task, and which provider served GLM-5.2?
