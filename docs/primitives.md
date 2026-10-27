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
| L1 | Python REPL as the only interface | One tool, `python_repl`: a persistent CPython namespace, top-level `await`, variables that survive turns and compactions, output that reaches the model only when printed. `bash()` returns a handle at once and sends a notice when the command ends; `edit()` replaces exact unique matches; files are read with Python; no read tool | `read`, `write`, `edit`, `bash` tools; bash blocks; scripts run in fresh processes | Pi's tools replaced by `python_repl` backed by a persistent kernel; `bash()` and `edit()` as Python functions with the same behaviour; Prime's core-tools and REPL usage text |
| L2 | Subagents | `rlm.spawn`: persistent background child agents one level deeper; depth limit 2 by default; model selectable; results arrive as messages or files, never as return values; `list_subagents`, `collect`, `delete_subagent`, `rename`, `progress_note` | none | Child Pi processes with the same rung configuration at depth + 1, persistent and resumable by name; same function names and prompt text |
| L3 | Agent messaging | `agent_message.send` to parent, sibling, or child; `agent_observe` for status and recent messages | none | A message broker between the run's Pi processes; same API and prompt text |
| L4 | Continual harness and refine | Typed store of prompt notes, memories, skills (Python callables), and subagent specs; local or global scope; create/read/update/delete API; `refine.run()` asks a separate model call for JSON edits from the trajectory; automatic refine at the root agent with a review gate, every 25 turns and at compaction, 20-minute cooldown | none | Same store, API, and prompts (refine and review prompts verbatim from `planner.rs`); same defaults |
| L5 | General guidance text | `opinionated.md` and the general rules in `usage.md`: coding habits, delegation habits, writing style | Pi's own system prompt | The same text appended |

Each dual ships a spec with its Prime source (file and commit) and every deliberate difference.

## Why the REPL is a rung

In Prime Agent the REPL is not a feature next to other tools: it is the only way the model acts, and subagents, messaging, and memory are Python functions inside it. Reaching Prime Agent's set of building blocks therefore means switching Pi's interface at some point. L1 measures that switch on its own (success, turns, tokens), so its effect is not credited to the subagents rung that follows.

## Prime Agent's REPL and Pi's codemode

Pi ships codemode, built in and off by default. It shares the REPL's core idea and lacks three of its properties:

| | Pi codemode | Prime Agent REPL |
|---|---|---|
| Model writes code that calls tools; only printed output returns | yes | yes |
| Can be the only way to act | yes (`codemode.mode: only`) | yes |
| Other building blocks callable from code | yes (scripts call any registered tool) | yes (Python functions) |
| State kept between calls | no, apart from a small JSON store | yes; variables survive turns and compactions |
| Runtime | sandboxed JavaScript; files and network only through tools | Python with files, network, libraries |
| Background work | calls are cancelled when the script ends | commands keep running between turns and send a notice when done |

## Interface arms (Module B)

Run only if the core shows the L0 → L1 step changing success or cost (see the ladder plan).

- **C0:** Pi as shipped with `codemode.mode: only`. Nothing built.
- **T4:** the L2–L4 building blocks (subagents, messaging, continual harness and refine) as ordinary Pi tools, backed by the same implementation as the duals, with no REPL. Tool descriptions are adapted from Prime's text; the calling surface is the deliberate difference.
- **C4:** T4 with `codemode.mode: only`, so scripts call the building-block tools.

With L0, L1, and L4 these form a 3×2: interface (plain tools, codemode, REPL) × building blocks (none, all three). It shows whether the REPL matters beyond codemode, on its own or only together with the building blocks.

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

## Matched reference points (Module A)

| Pi rung | Prime Agent with the same building blocks |
|---|---|
| L1 | `rlmMaxDepth: 0`, `harnessRefinements: false` |
| L3 | `rlmMaxDepth: 2`, `harnessRefinements: false` |
| L5 | defaults |

What the switches do (read from prime-agent source, `8aac869` / v0.10.1):

- **`rlmMaxDepth: 0`** refuses every spawn: a spawn fails when the caller's depth is at least the limit (`pa-daemon/src/rlm_children/host.rs`). The limit resolves from the session's persisted value, then settings, then the `RLM_MAX_DEPTH` environment variable, then the default 2 (`rlm_host.rs`), so the adapter's `env` option can set it. The prompt still describes subagents; a model that tries gets the depth-limit error.
- **`harnessRefinements: false`** is a master switch for scheduling, planning, and applying refinements, for automatic refine, and for delivering harness state to the model (`refinement_gate.rs`, `refine.rs`, `harness_digest.rs`, `wiring.rs`). It is read only from `settings.json` in the agent directory, so the adapter must write that file. The agent's own Python memory calls are not gated in the code read so far, but their contents no longer reach the model's context.
- **Session persistence.** Refinement needs a local harness directory, which exists only for persisted sessions (`session/manager/queries.rs`). The verifiers adapter passes `--no-session` since `32c1f14`. If no other path supplies the directory, refinement is off in Prime Agent's default verifiers configuration. To verify with a smoke run before arm P is defined.
