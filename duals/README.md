# Duals

Pi extensions that mirror Prime Agent's building blocks, one per ladder rung (see [docs/primitives.md](../docs/primitives.md)). Each dual has a `SPEC.md` with its Prime Agent sources and every deliberate difference.

| Rung | Dual | Status |
|---|---|---|
| L1 | [pi/l1-repl](pi/l1-repl/SPEC.md): Python REPL as the only interface | built, tested against a fake model |
| L2 | subagents | to build |
| L3 | agent messaging | to build |
| L4 | continual harness and refine | to build |
| L5 | general guidance text | to build |

## Kernel environment

The REPL duals run Prime Agent's own kernel runtime and `edit` skill, installed from the pinned commit:

```sh
duals/scripts/setup-kernel.sh /tmp/duals-kernel
export HARNESS_DUALS_PYTHON=/tmp/duals-kernel/bin/python
```

## Prompts

`scripts/port_prompts.py` regenerates each rung's `prompt.md` from Prime Agent's prompt layers at the pinned commit, so every ported line can be traced to its source:

```sh
uv run python duals/scripts/port_prompts.py ~/.cache/checkouts/github.com/PrimeIntellect-ai/prime-agent
```

## Tests

`tests/fake_model.py` is a scripted OpenAI-compatible server; each dual's test drives `pi -p` against it in a fresh agent directory:

```sh
HARNESS_DUALS_PYTHON=/tmp/duals-kernel/bin/python python3 duals/tests/test_l1_repl.py
```

## Running in evaluations

The verifiers plugins in [harnesses/](../harnesses/) load the duals: `pi-ladder` (Pi with a rung's duals) and `prime-switches` (Prime Agent with its own settings).
