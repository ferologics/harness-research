# Memory track: does the continual harness help on later tasks in the same repo?

**Status:** draft. Runs after the ladder's phase A3.

## Question

Does Prime Agent's continual harness (memory store plus refine) make later tasks in the same repository more often solved or cheaper? Does the Pi dual (rung L5) do the same?

Single tasks cannot show this: refine carries lessons from one task to the next.

## Tasks

SWE-rebench-V2 repos with at least 10 tasks: 106 repos, 1,954 tasks ([scripts/swerebench_pool.py](../../scripts/swerebench_pool.py)). Pick 3 repos, 10 tasks each, run in creation order.

## Arms

| Arm | Harness | State between tasks |
|---|---|---|
| L5-carry | Pi + duals up to L5 | store carried through the sequence |
| L5-reset | Pi + duals up to L5 | store wiped before each task |
| P-carry | Prime Agent | refinements carried (global scope) |
| P-reset | Prime Agent | refinements wiped before each task |

## Metric

Gain = carry − reset on the same task, by position in the sequence (the gain metric from CL-Bench). Reported for success, tokens, and turns.

4 arms × 30 tasks × 2 sequence runs = 240 local runs.

## Prior evidence

Memory systems often fail to beat no memory on coding tasks (VibeMemBench, CL-Bench, MemDev-Bench; see [docs/literature.md](../../docs/literature.md)).

## Open

- How Prime Agent carries state between separate sessions: global scope, or local state copied forward.
- Whether the verifiers adapter keeps a harness directory between tasks.
