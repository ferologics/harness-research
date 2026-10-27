# Vision

## Question

Do the building blocks that elaborate agent harnesses add on top of a minimal coding agent produce real gains for coding, and do they compound? Or does a minimal harness hold up as tasks get bigger, without them?

The concrete case is Prime Agent against Pi. Prime Agent's paper reports it matching or beating Pi, Claude Code, and Codex. Its first author says its performance "scales more than a sum of its parts." Its only direct comparison with Pi is one table, on one model, without intervals, and mostly on long-context tasks.

## Approach

1. **Inventory** Prime Agent's building blocks from its source code ([docs/primitives.md](docs/primitives.md)).
2. **Build an objective Pi dual** for each block in this repo: the same mechanism, the same trigger, model-facing text ported from Prime Agent, Prime's defaults, and nothing extra.
3. **Zero to hero:** start from Pi as shipped and add one dual at a time until Pi has Prime Agent's set of building blocks. Run Prime Agent as shipped beside the ladder. Follow-up modules (Prime Agent's own switches; REPL vs Pi's codemode) run only when the core results call for them.
4. **Coding tasks at several sizes**, sliced from public benchmarks on Prime Intellect's eval stack.
5. **Two models:** breadth on stock Qwen3.8-27B served locally; confirmation on GLM-5.2, the paper's model.

Decisions behind these choices are in [docs/decisions.md](docs/decisions.md).

## Principles

- **Objective duals.** A dual mirrors what the Prime Agent block does. It never depends on third-party packages or anyone's personal setup.
- **One substrate per comparison.** Pi rungs differ only by the dual under test. Prime Agent configurations differ only by Prime's own switches.
- **Pre-register.** Arms, tasks, metrics, and decision rules are frozen before the main runs.
- **Noise floor.** Repeated runs show how much results move when nothing changes.
- **Cost next to success.** Tokens, turns, and cost are reported with every success rate.
- **No verdict in advance.** Pi matching Prime Agent, beating it, or losing to it are all results.

## What success looks like

1. The Pi vs Prime Agent gap on coding as a function of task size, with intervals.
2. The ladder: which building block changes success, cost, or turns, and whether Pi with every dual matches Prime Agent.
3. An interaction estimate ("more than the sum of its parts") from Prime Agent's own switches.
4. The duals and all run data published, so anyone can rerun the comparison.
