"""verifiers harness `prime-switches`: Prime Agent with its own switches set.

The upstream `prime_agent` harness does everything; this plugin writes Prime Agent's
`settings.json` (`rlmMaxDepth`, `harnessRefinements`) into the session's agent
directory, and can drop `--no-session`, which may disable refinement.

    --env.agent.harness.id prime-switches --env.agent.harness.rlm-max-depth 0
"""

import json

from verifiers.v1.acp import ACPConfig, ACPHarness
from verifiers.v1.clients import ModelContext
from verifiers.v1.harnesses.prime_agent import PrimeAgentHarness, PrimeAgentHarnessConfig
from verifiers.v1.runtimes import Runtime
from verifiers.v1.task import TaskData
from verifiers.v1.trace import Trace

__all__ = ["PrimeSwitchesHarness", "PrimeSwitchesHarnessConfig"]


class PrimeSwitchesHarnessConfig(PrimeAgentHarnessConfig):
    rlm_max_depth: int | None = None
    """Prime Agent's `rlmMaxDepth`; 0 refuses every subagent spawn. None keeps the default (2)."""
    harness_refinements: bool | None = None
    """Prime Agent's `harnessRefinements`; False turns refinement and memory delivery off."""
    persist_session: bool = False
    """Drop the adapter's `--no-session`: refinement needs a persisted session."""


def settings(config: PrimeSwitchesHarnessConfig) -> dict[str, object]:
    values: dict[str, object] = {}
    if config.rlm_max_depth is not None:
        values["rlmMaxDepth"] = config.rlm_max_depth
    if config.harness_refinements is not None:
        values["harnessRefinements"] = config.harness_refinements
    return values


class PrimeSwitchesHarness(PrimeAgentHarness, ACPHarness[PrimeSwitchesHarnessConfig]):
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
        values = settings(self.config)
        if values:
            agent_dir = config.env["PRIME_AGENT_CODING_AGENT_DIR"]
            await runtime.write(f"{agent_dir}/settings.json", json.dumps(values).encode())
        if self.config.persist_session:
            config.command = [arg for arg in config.command if arg != "--no-session"]
        return config
