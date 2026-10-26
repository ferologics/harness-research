# Prime Agent building blocks and their Pi duals

Sources: prime-agent `c4c238c` — `crates/pa-core/src/prompts/layers/{core,usage,opinionated}.md`, `crates/pa-core/src/refinement/planner.rs`, `crates/pa-core/src/session_engine/{refine.rs,engine.rs,rlm_host.rs}`, `crates/pa-core/src/settings/`. Pi 1.4.0 docs.

## Lineage

Prime Agent most likely grew from Pi's codebase. This is an inference, not confirmed by its authors:

- Its compaction prompt (`SUMMARIZATION_SYSTEM_PROMPT`) matches Pi's word for word except "AI coding assistant" for "AI assistant."
- It reads `PI_PACKAGE_DIR`, a Pi environment variable.
- Its contributor guide (`AGENTS.md`) tells contributors to scrub "pi"/"pi-mono"/"pi-ai" naming from user-visible surfaces, while stating "we are not a pi fork."

The ladder therefore starts from Pi and retraces the building blocks Prime Agent adds.

## Building blocks and duals

| Rung | Prime Agent block | Prime Agent mechanism | Pi as shipped | Pi dual built here |
|---|---|---|---|---|
| L1 | Python REPL | Persistent CPython namespace; top-level `await`; variables survive turns and compactions; output reaches the model only when printed | none (bash runs scripts in fresh processes) | `python_repl` tool backed by a persistent kernel, added next to Pi's tools |
| L2 | REPL as the only interface | One tool, `python_repl`. `bash()` returns a handle at once and sends a notice when the command ends; `edit()` replaces exact unique matches; files are read with Python; no read tool | `read`, `write`, `edit`, `bash` tools; bash blocks | Pi's tools replaced by `python_repl`; `bash()` and `edit()` as Python functions with the same behaviour; Prime's core-tools and REPL usage text |
| L3 | Subagents | `rlm.spawn`: persistent background child agents one level deeper; depth limit 2 by default; model selectable; results arrive as messages or files, never as return values; `list_subagents`, `collect`, `delete_subagent`, `rename`, `progress_note` | none | Child Pi processes with the same rung configuration at depth + 1, persistent and resumable by name; same function names and prompt text |
| L4 | Agent messaging | `agent_message.send` to parent, sibling, or child; `agent_observe` for status and recent messages | none | A message broker between the run's Pi processes; same API and prompt text |
| L5 | Continual harness and refine | Typed store of prompt notes, memories, skills (Python callables), and subagent specs; local or global scope; create/read/update/delete API; `refine.run()` asks a separate model call for JSON edits from the trajectory; automatic refine at the root agent with a review gate, every 25 turns and at compaction, 20-minute cooldown | none | Same store, API, and prompts (refine and review prompts verbatim from `planner.rs`); same defaults |
| L6 | General guidance text | `opinionated.md` and the general rules in `usage.md`: coding habits, delegation habits, writing style | Pi's own system prompt | The same text appended |

Each dual ships a spec with its Prime source (file and commit) and every deliberate difference.

## Held at each harness's own behaviour

These differ between the two harnesses and are not ported. Any remaining difference at a matched point (below) includes them.

- **Compaction.** Pi uses its built-in summary. Prime Agent compacts when 16,384 tokens remain and keeps REPL variables. The summary prompts are nearly identical.
- **Base system prompt** apart from the ported sections.

## Not ported

Off by default or irrelevant in single-task evaluations: goal mode, autonomous mode (the verifiers adapter defaults it off), heartbeats, `rlm.factory` workflows, MCP, `create_session`, `attach_image`, and the bundled web search skill (task networks are closed).

## Rules for duals

1. Mirror the mechanism: same capability, same trigger (who decides when it runs), same information flow.
2. Port model-facing text from Prime Agent's prompt layers; rename only where names must differ.
3. Use Prime Agent's defaults.
4. Add nothing: no features, hints, or guardrails that Prime Agent lacks.

## Matched reference points

| Pi rung | Prime Agent with the same building blocks |
|---|---|
| L2 | `rlmMaxDepth: 0`, `harnessRefinements: false` |
| L4 | `rlmMaxDepth: 2`, `harnessRefinements: false` |
| L6 | defaults |

To verify before use: that `rlmMaxDepth: 0` disables spawning, what exactly `harnessRefinements: false` turns off (its setting is described as controlling "refinement creation and context loading"), and how these settings reach the verifiers adapter.
