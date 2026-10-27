"""Port Prime Agent's model-facing prompt text into the rung prompt files of the Pi duals.

Every line comes from Prime Agent's prompt layers or its system-prompt builder at the
pinned commit. The only edits are the ones listed in each rung's SPEC.md: product-name
renames and dropped parts that belong to building blocks the rung does not have.

Usage:
    uv run python duals/scripts/port_prompts.py ~/.cache/checkouts/github.com/PrimeIntellect-ai/prime-agent
"""

import subprocess
import sys
from pathlib import Path

COMMIT = "8aac8692456c00c01d4e53e60e6d3347a3506559"  # prime-agent v0.10.1
LAYERS = "crates/pa-core/src/prompts/layers"
DUALS = Path(__file__).resolve().parents[1]

# crates/pa-core/src/kernel/bootstrap/mod.rs, DEFAULT_RLM_EXTRA_PACKAGES prompt labels.
PACKAGE_LABELS = [
    "requests",
    "httpx",
    "yaml (PyYAML)",
    "tomli",
    "dotenv (python-dotenv)",
    "pandas",
    "numpy",
    "scipy",
    "bs4 (Beautiful Soup)",
    "lxml",
    "pydantic",
    "tyro",
]

# crates/pa-core/src/prompts/system_prompt.rs, session_role_section, has_ipython branch.
BASH_AWAIT_LINE = (
    "`await bash(cmd)` waits at most `yield_after` seconds (`bash(cmd, yield_after=...)`, default 10, "
    "max 300; `None` uses the default, not an unbounded wait). If the command is still running, it "
    "returns a snapshot: `r.running` is True, `r.exit_code` is None, `r.output` is the output so far, "
    "and `r.handle` is the live handle. A completed result has `r.running` False and an integer "
    "`r.exit_code`. The command keeps running after a snapshot; end the turn and collect the final "
    "result on the `[bash-done]` notification."
)

# usage.md rules about working through the REPL (rung L1). The other rules belong to
# later rungs: delegation and multi-agent rules (L2, L3), memory and refinement (L4),
# general behaviour and style (L5), goals (not ported).
L1_USAGE_PREFIXES = [
    "- Agents run shell commands with `bash()`",
    "- `bash(\"\"\"...\"\"\")` should be used",
    "- Shell state does not persist between calls",
    "- Edits of existing files must be performed using `edit`",
    "- Agents use Python for reading files",
    "- Agents always assign read/search results",
    "- Agents do not keep the turn open by polling",
    "- Agents use the Python REPL to keep intermediate variables",
    "- Since compaction removes individual variables",
    "- Python is the orchestration language",
    "- Agents do not assume the REPL is the native runtime",
    "- Agents do not install dependencies into the kernel",
]


def layer(checkout: Path, name: str) -> str:
    return subprocess.run(
        ["git", "-C", str(checkout), "show", f"{COMMIT}:{LAYERS}/{name}"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout


def section(text: str, heading: str) -> list[str]:
    lines = text.splitlines()
    start = lines.index(heading)
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
    return lines[start:end]


def l1_prompt(checkout: Path) -> str:
    core = layer(checkout, "core.md")
    usage = layer(checkout, "usage.md")

    intro = core.split("## Core tools")[0].strip().splitlines()
    intro = [line.replace("# prime-agent harness", "# Harness").replace("The prime-agent harness", "This harness") for line in intro]

    tools = section(core, "## Core tools")
    dropped = ("- `websearch.run(", "- `attach_image(")
    tools = [line for line in tools if not line.startswith(dropped)]

    rules = [line for line in usage.splitlines() if line.startswith(tuple(L1_USAGE_PREFIXES))]
    if len(rules) != len(L1_USAGE_PREFIXES):
        raise SystemExit(f"expected {len(L1_USAGE_PREFIXES)} usage rules, found {len(rules)}")

    parts = [
        "\n".join(intro),
        "\n".join(tools).strip(),
        "## Rules\n\n" + "\n".join(rules),
        "## Session\n\n"
        + "Background `bash()` completions wake you with a queued `[bash-done]` turn.\n"
        + BASH_AWAIT_LINE,
        "Pre-installed Python packages: "
        + ", ".join(PACKAGE_LABELS)
        + ".\nInstall additional packages with `uv pip install <pkg>` (this is a uv-managed venv with no pip module).",
    ]
    return "\n\n".join(parts) + "\n"


def main() -> None:
    checkout = Path(sys.argv[1]).expanduser()
    out = DUALS / "pi" / "l1-repl" / "prompt.md"
    out.write_text(l1_prompt(checkout))
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
