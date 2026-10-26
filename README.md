# harness-research

Do the building blocks that elaborate agent harnesses add on top of a minimal coding agent produce real gains, and do they compound? The concrete case is Prime Agent against Pi: starting from Pi as shipped, add objective duals of Prime Agent's building blocks one at a time and compare every step with Prime Agent itself, on coding tasks of several sizes.

Start with [VISION.md](VISION.md) and [docs/decisions.md](docs/decisions.md). Current work is in [TODO.md](TODO.md).

## Layout

| Path | Contents |
|---|---|
| [AGENTS.md](AGENTS.md) | Rules for agents working in this repo |
| [docs/decisions.md](docs/decisions.md) | Agreed decisions and their reasons |
| [docs/primitives.md](docs/primitives.md) | Prime Agent's building blocks, their Pi duals, matched reference points |
| [docs/claims.md](docs/claims.md) | Claims under test, with sources |
| [docs/literature.md](docs/literature.md) | Prior work and which controls each study used |
| [docs/infrastructure.md](docs/infrastructure.md) | Eval stack, task data, models, hardware |
| [experiments/ladder/](experiments/ladder/PLAN.md) | Zero to hero: Pi to Prime Agent, one building block at a time |
| [experiments/memory-sequences/](experiments/memory-sequences/PLAN.md) | Does the continual harness help on later tasks in the same repo? |
| [scripts/](scripts/) | Data inspection scripts |

## Status

Planning. No duals are built and no experiment has run.
