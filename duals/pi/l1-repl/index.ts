/**
 * Rung L1 dual: Prime Agent's Python REPL as Pi's only interface.
 *
 * Mirrors prime-agent v0.10.1: the `python_repl` tool (name, schema, description),
 * its result text, the kernel bootstrap, background `[bash-done]` notices, and the
 * REPL part of the system prompt. See SPEC.md for sources and deliberate differences.
 *
 * Requires HARNESS_DUALS_PYTHON: the interpreter of a venv built by
 * duals/scripts/setup-kernel.sh.
 */

import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { Type } from "@earendil-works/pi-ai";
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { type BashNotice, type CellResult, KERNEL_RESTART_NOTICE, Kernel } from "./kernel.ts";

const TOOL_NAME = "python_repl";

// crates/pa-core/src/tools/ipython.rs: ipython_tool_description, ipython_tool_schema, prompt_snippet.
const DESCRIPTION =
    "Execute Python code in a persistent Python REPL. Top-level `await` is supported. Variables, imports, and loaded data persist across calls, and are revived on a best-effort basis when a session is resumed (objects that cannot be serialized are dropped and reported). Run shell commands with `bash('cmd')` / `await bash('cmd')`. Project imports, tests, scripts, CLIs, and dependency checks should run through the target project's own environment.";
const CODE_DESCRIPTION =
    "Python code to execute in the persistent Python REPL. Use the target project's own environment for project imports, tests, scripts, CLIs, and dependency checks instead of direct kernel imports.";
const SNIPPET = "python_repl - persistent Python REPL for code, state, and bash() orchestration";

const PROMPT = readFileSync(join(dirname(fileURLToPath(import.meta.url)), "prompt.md"), "utf8");

// crates/pa-core/src/tools/ipython.rs, format_execute_text.
function formatResult(result: CellResult): string {
    let text = result.stdout;
    const append = (part: string) => {
        text += (text ? "\n" : "") + part;
    };
    if (result.stderr) append(result.stderr);
    if (result.result !== undefined) append(result.result);
    if (result.status === "error" && result.error) append(result.error.traceback.join("\n"));
    if (result.backgroundOutput) append(`[background output (unattributed)]\n${result.backgroundOutput}`);
    return text;
}

// crates/pa-core/src/session_engine/messages.rs, create_async_bash_completion_message.
function noticeMessage(notice: BashNotice) {
    return {
        type: "custom_message" as const,
        customType: "async_bash_completion",
        content: `[bash-done pid:${notice.pid} exit:${notice.exitCode}]\n\nCommand: ${JSON.stringify(notice.command)}`,
        display: true,
        details: { pid: notice.pid, command: notice.command, exitCode: notice.exitCode },
    };
}

export default function l1Repl(pi: ExtensionAPI) {
    let kernel: Kernel | undefined;

    const getKernel = (cwd: string): Kernel => {
        if (!kernel) {
            const python = process.env.HARNESS_DUALS_PYTHON;
            if (!python) throw new Error("HARNESS_DUALS_PYTHON is not set; run duals/scripts/setup-kernel.sh");
            kernel = new Kernel(python, cwd);
        }
        return kernel;
    };

    pi.registerTool({
        name: TOOL_NAME,
        label: TOOL_NAME,
        description: DESCRIPTION,
        promptSnippet: SNIPPET,
        parameters: Type.Object({ code: Type.String({ description: CODE_DESCRIPTION }) }),
        executionMode: "sequential",
        async execute(_toolCallId, params, signal, _onUpdate, ctx) {
            const k = getKernel(ctx.cwd);
            const restarted = (await k.ensure()) && k.started > 1;
            const result = await k.run(params.code, signal);
            let text = formatResult(result);
            if (restarted) text = text ? `${KERNEL_RESTART_NOTICE}\n\n${text}` : KERNEL_RESTART_NOTICE;
            return {
                content: [{ type: "text", text }],
                details: { status: result.status, kernelRestarted: restarted },
                isError: result.status !== "ok",
            };
        },
    });

    pi.on("session_start", () => {
        pi.setActiveTools([TOOL_NAME]);
    });

    pi.on("before_agent_start", (event) => {
        event.systemPromptOptions.sections.harness = PROMPT;
    });

    // Prime Agent without a daemon waits for live background commands before the run
    // ends, then wakes the agent with queued `[bash-done]` notices.
    pi.on("agent_before_settle", async () => {
        if (!kernel) return;
        await kernel.waitForNoticeOrIdle();
        const notices = kernel.takeNotices();
        if (notices.length === 0) return;
        return { entries: notices.map(noticeMessage), continue: true };
    });

    pi.on("session_shutdown", () => {
        kernel?.shutdown();
    });
}
