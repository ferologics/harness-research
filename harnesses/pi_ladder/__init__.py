"""verifiers harness `pi-ladder`: Pi as shipped plus the duals of one ladder rung.

The upstream `pi` harness does everything (install, model routing, ACP); this plugin
only uploads the duals, builds the REPL kernel environment once per runtime, and
launches Pi with the rung's extensions. Install this package editable, from the repo
checkout, so it can read `duals/`.

    --env.agent.harness.id pi-ladder --env.agent.harness.rung L1
"""

import shlex
from pathlib import Path
from typing import Literal

from verifiers.v1.acp import ACPConfig, ACPHarness
from verifiers.v1.clients import ModelContext
from verifiers.v1.harnesses.pi import PiHarness, PiHarnessConfig
from verifiers.v1.harnesses.utils.install import ensure_installed
from verifiers.v1.runtimes import Runtime
from verifiers.v1.runtimes.base import _ENSURE_UV
from verifiers.v1.task import TaskData
from verifiers.v1.trace import Trace

__all__ = ["PiLadderHarness", "PiLadderHarnessConfig"]

DUALS = Path(__file__).resolve().parents[2] / "duals"
REMOTE = "/var/tmp/vf-duals"
KERNEL = f"{REMOTE}/kernel"

Rung = Literal["L0", "L1"]

# Extensions each rung loads, in order. A rung includes every dual below it.
RUNG_EXTENSIONS: dict[str, list[str]] = {
    "L0": [],
    "L1": ["l1-repl"],
}
KERNEL_RUNGS = {"L1"}


class PiLadderHarnessConfig(PiHarnessConfig):
    rung: Rung = "L0"
    """Ladder rung: L0 is Pi as shipped; each later rung adds one dual."""


def extension_args(rung: str) -> list[str]:
    args: list[str] = []
    for name in RUNG_EXTENSIONS[rung]:
        args += ["--extension", f"{REMOTE}/pi/{name}/index.ts"]
    return args


def wrapper_script(inner_command: str, rung: str) -> str:
    """The Pi launcher for a rung: the upstream launcher plus the rung's extensions."""
    return f"#!/bin/sh\nexec {shlex.quote(inner_command)} {shlex.join(extension_args(rung))} \"$@\"\n"


class PiLadderHarness(PiHarness, ACPHarness[PiLadderHarnessConfig]):
    async def setup(self, runtime: Runtime) -> None:
        await super().setup(runtime)
        if not RUNG_EXTENSIONS[self.config.rung]:
            return
        for path in sorted((DUALS / "pi").rglob("*")):
            if path.is_file() and path.suffix in {".ts", ".md"}:
                target = f"{REMOTE}/{path.relative_to(DUALS).as_posix()}"
                await runtime.run(["mkdir", "-p", target.rsplit("/", 1)[0]], {})
                await runtime.write(target, path.read_bytes())
        if self.config.rung in KERNEL_RUNGS:
            script = (DUALS / "scripts" / "setup-kernel.sh").read_text()
            await runtime.write(f"{REMOTE}/setup-kernel.sh", script.encode())
            await ensure_installed(
                runtime,
                directory=REMOTE,
                install=f"{_ENSURE_UV}; sh {REMOTE}/setup-kernel.sh {KERNEL}",
                env={},
                label="pi-ladder kernel",
                ready=f"[ -x {KERNEL}/bin/python ]",
            )

    async def prepare_acp(
        self,
        ctx: ModelContext,
        trace: Trace,
        runtime: Runtime,
        endpoint: str,
        secret: str,
        mcp_urls: dict[str, str],
        data: TaskData,
    ) -> ACPConfig:
        config = await super().prepare_acp(ctx, trace, runtime, endpoint, secret, mcp_urls, data)
        if not RUNG_EXTENSIONS[self.config.rung]:
            return config
        launcher = f"{config.env['PI_CODING_AGENT_DIR']}/pi-ladder"
        await runtime.write(launcher, wrapper_script(config.env["PI_ACP_PI_COMMAND"], self.config.rung).encode())
        await runtime.run(["chmod", "+x", launcher], {})
        config.env["PI_ACP_PI_COMMAND"] = launcher
        if self.config.rung in KERNEL_RUNGS:
            config.env["HARNESS_DUALS_PYTHON"] = f"{KERNEL}/bin/python"
        return config
