/**
 * Host side of Prime Agent's kernel protocol (prime-agent-runtime `rlm.repl`, protocol 3).
 *
 * The kernel itself is Prime Agent's own Python runtime, installed by
 * duals/scripts/setup-kernel.sh. This file only starts it, runs cells, and answers
 * the host requests a REPL-only session needs (background bash completion notices).
 */

import { type ChildProcessWithoutNullStreams, spawn } from "node:child_process";
import { randomUUID } from "node:crypto";
import { createInterface } from "node:readline";

const BASH_ACTIVITY_MIME = "application/vnd.prime-agent.bash-activity+json";

// crates/pa-core/src/kernel/bootstrap/runtime_code.rs: header, `bash` binding with
// completion notices wired, and the skill pre-import loop for the `edit` skill.
// Rung L1 binds no `rlm` (subagents) and no `mcp`.
const BOOTSTRAP_CODE = `import asyncio
import os as _prime_agent_os

_prime_agent_os.environ["NO_COLOR"] = "1"

import rlm as _prime_agent_rlm_module
bash = _prime_agent_rlm_module.bash
_prime_agent_rlm_module._set_completion_notices_wired(True)

import importlib as _prime_agent_importlib
import inspect as _prime_agent_inspect
import sys as _prime_agent_sys
import types as _prime_agent_types

class _PrimeAgentCallableSkillModule(_prime_agent_types.ModuleType):
    async def __call__(self, *args, **kwargs):
        result = self.run(*args, **kwargs)
        if _prime_agent_inspect.isawaitable(result):
            return await result
        return result

def _prime_agent_wrap_skill_module(module):
    run = getattr(module, "run", None)
    if not callable(run):
        return module
    wrapped = _PrimeAgentCallableSkillModule(module.__name__)
    wrapped.__dict__.update(module.__dict__)
    try:
        wrapped.__signature__ = _prime_agent_inspect.signature(run)
    except Exception:
        pass
    doc = getattr(run, "__doc__", None)
    if doc:
        wrapped.__doc__ = doc
    _prime_agent_sys.modules[module.__name__] = wrapped
    return wrapped

for _prime_agent_skill_name in ["edit"]:
    globals()[_prime_agent_skill_name] = _prime_agent_wrap_skill_module(
        _prime_agent_importlib.import_module(_prime_agent_skill_name)
    )
`;

// crates/pa-core/src/tools/ipython.rs, kernel_restart_notice.
export const KERNEL_RESTART_NOTICE =
    "<ipython_kernel_reset>\nThe Python kernel was restarted after a previous interrupted cell kept running. Variables, imports, async tasks, and open resources from before the restart are no longer available; recreate them before using them.\n</ipython_kernel_reset>";

type KernelEvent = {
    event: string;
    id: string | null;
    text?: string;
    ename?: string;
    evalue?: string;
    traceback?: string[];
    status?: string;
    data?: Record<string, unknown>;
};

export type CellResult = {
    status: "ok" | "error" | "aborted";
    stdout: string;
    stderr: string;
    result?: string;
    error?: { ename: string; evalue: string; traceback: string[] };
    backgroundOutput?: string;
};

export type BashNotice = { pid: number; command: string; exitCode: number };

type RunningCell = {
    id: string;
    stdout: string;
    stderr: string;
    background: string;
    result?: string;
    error?: CellResult["error"];
    resolve: (status: string) => void;
};

export class Kernel {
    private process?: ChildProcessWithoutNullStreams;
    private ready?: Promise<void>;
    private cell?: RunningCell;
    private readonly notices = new Map<number, BashNotice>();
    private readonly liveActivities = new Set<string>();
    private noticeWaiters: Array<() => void> = [];
    /** How many times a kernel process was started; above 1 means a restart. */
    started = 0;

    constructor(
        private readonly python: string,
        private readonly cwd: string,
    ) {}

    /** Start the kernel and run the bootstrap cell. Returns true when it was (re)started now. */
    async ensure(): Promise<boolean> {
        if (this.process && this.process.exitCode === null && this.ready) {
            await this.ready;
            return false;
        }
        this.started += 1;
        const child = spawn(this.python, ["-m", "rlm.repl"], {
            cwd: this.cwd,
            env: { ...process.env, NO_COLOR: "1" },
            stdio: ["pipe", "pipe", "pipe"],
        });
        this.process = child;
        let stderrTail = "";
        child.stderr.on("data", (chunk) => {
            stderrTail = (stderrTail + chunk.toString()).slice(-4000);
        });
        let markReady: () => void = () => {};
        let failReady: (error: Error) => void = () => {};
        this.ready = new Promise<void>((resolve, reject) => {
            markReady = resolve;
            failReady = reject;
        });
        child.on("exit", (code) => {
            failReady(new Error(`kernel exited before it was ready (code ${code}): ${stderrTail}`));
            this.cell?.resolve("error");
        });
        createInterface({ input: child.stdout }).on("line", (line) => {
            let event: KernelEvent;
            try {
                event = JSON.parse(line);
            } catch {
                return;
            }
            if (event.event === "ready") {
                markReady();
                return;
            }
            this.handle(event);
        });
        await this.ready;
        const boot = await this.run(BOOTSTRAP_CODE);
        if (boot.status !== "ok") {
            throw new Error(`kernel bootstrap failed: ${boot.error?.traceback.join("\n") ?? boot.stderr}`);
        }
        return true;
    }

    async run(code: string, signal?: AbortSignal): Promise<CellResult> {
        const id = randomUUID();
        const finished = new Promise<string>((resolve) => {
            this.cell = { id, stdout: "", stderr: "", background: "", resolve };
        });
        const onAbort = () => this.send({ type: "interrupt", id });
        signal?.addEventListener("abort", onAbort, { once: true });
        this.send({ type: "execute", id, code });
        const status = await finished;
        signal?.removeEventListener("abort", onAbort);
        const cell = this.cell as RunningCell;
        this.cell = undefined;
        return {
            status: signal?.aborted ? "aborted" : status === "ok" ? "ok" : "error",
            stdout: cell.stdout,
            stderr: cell.stderr,
            result: cell.result,
            error: cell.error,
            backgroundOutput: cell.background || undefined,
        };
    }

    /** Pending `[bash-done]` notices, removed from the queue. */
    takeNotices(): BashNotice[] {
        const taken = [...this.notices.values()];
        this.notices.clear();
        return taken;
    }

    hasLiveBackground(): boolean {
        return this.liveActivities.size > 0;
    }

    /** Resolve when a notice arrives or no background command is left running. */
    waitForNoticeOrIdle(): Promise<void> {
        if (this.notices.size > 0 || !this.hasLiveBackground()) return Promise.resolve();
        return new Promise((resolve) => this.noticeWaiters.push(resolve));
    }

    shutdown(): void {
        if (!this.process || this.process.exitCode !== null) return;
        this.send({ type: "shutdown" });
        setTimeout(() => this.process?.kill("SIGKILL"), 2000).unref();
    }

    private wake(): void {
        if (this.notices.size > 0 || !this.hasLiveBackground()) {
            const waiters = this.noticeWaiters;
            this.noticeWaiters = [];
            for (const waiter of waiters) waiter();
        }
    }

    private send(request: Record<string, unknown>): void {
        this.process?.stdin.write(`${JSON.stringify(request)}\n`);
    }

    private reply(id: string, data: Record<string, unknown>): void {
        this.send({ type: "host_reply", id, data });
    }

    private handle(event: KernelEvent): void {
        const cell = this.cell;
        const ownCell = cell !== undefined && event.id === cell.id;
        switch (event.event) {
            case "stdout":
            case "stderr":
                if (ownCell) {
                    cell[event.event] += event.text ?? "";
                } else if (cell && event.id === null) {
                    cell.background += event.text ?? "";
                }
                return;
            case "result":
                if (ownCell) cell.result = event.text;
                return;
            case "error":
                if (ownCell) {
                    cell.error = {
                        ename: event.ename ?? "Error",
                        evalue: event.evalue ?? "",
                        traceback: event.traceback ?? [],
                    };
                }
                return;
            case "done":
                if (ownCell) cell.resolve(event.status ?? "error");
                return;
            case "display": {
                const activity = event.data?.[BASH_ACTIVITY_MIME] as { id?: string; active?: boolean } | undefined;
                if (activity?.id) {
                    if (activity.active) this.liveActivities.add(activity.id);
                    else this.liveActivities.delete(activity.id);
                    this.wake();
                }
                return;
            }
            case "host_request":
                this.hostRequest(event.id as string, event.data ?? {});
                return;
        }
    }

    private hostRequest(id: string, data: Record<string, unknown>): void {
        if (data.type === "bash.completed") {
            const notice = {
                pid: Number(data.pid),
                command: String(data.command ?? ""),
                exitCode: Number(data.exitCode),
            };
            this.notices.set(notice.pid, notice);
            this.reply(id, { status: "ok", result: {} });
            this.wake();
            return;
        }
        if (data.type === "bash.consumed") {
            this.notices.delete(Number(data.pid));
            this.reply(id, { status: "ok", result: {} });
            return;
        }
        this.reply(id, { status: "error", error: `${String(data.type)} is not available in this session` });
    }
}
