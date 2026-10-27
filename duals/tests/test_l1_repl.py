"""End-to-end test of the L1 dual: Pi with Prime Agent's REPL as its only tool, driven by a scripted fake model.

Checks: only `python_repl` is declared, the harness prompt is present, variables persist
between calls, `bash()` and `edit()` work, and a background command's `[bash-done]`
notice wakes the agent after it tried to finish.

Usage:
    HARNESS_DUALS_PYTHON=/tmp/duals-kernel/bin/python uv run python duals/tests/test_l1_repl.py
"""

import json
import os
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path

DUALS = Path(__file__).resolve().parents[1]
EXTENSION = DUALS / "pi" / "l1-repl" / "index.ts"

STEPS = [
    {"tool": "python_repl", "arguments": {"code": "x = 41\nx + 1"}},
    {"tool": "python_repl", "arguments": {"code": "print(x + 1)"}},
    {
        "tool": "python_repl",
        "arguments": {
            "code": (
                "r = await bash('printf \"hello world\\\\n\" > note.txt && echo wrote')\n"
                "await edit(path='note.txt', old_str='world', new_str='repl')\n"
                "print(r.output.strip(), open('note.txt').read().strip())"
            )
        },
    },
    {"tool": "python_repl", "arguments": {"code": "h = bash('sleep 1; echo late')\n'started'"}},
    {"text": "first answer"},
    {"text": "final answer after bash-done"},
]


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def tool_results(request: dict) -> list[str]:
    return [m["content"] if isinstance(m["content"], str) else json.dumps(m["content"]) for m in request["messages"] if m["role"] == "tool"]


def main() -> None:
    python = os.environ.get("HARNESS_DUALS_PYTHON")
    if not python:
        sys.exit("set HARNESS_DUALS_PYTHON (see duals/scripts/setup-kernel.sh)")
    tmp = Path(tempfile.mkdtemp(prefix="dual-l1-"))
    agent_dir, work = tmp / "agent", tmp / "work"
    agent_dir.mkdir()
    work.mkdir()
    port = free_port()
    (tmp / "script.json").write_text(json.dumps(STEPS))
    log = tmp / "requests.jsonl"
    models = {
        "providers": {
            "fake": {
                "baseUrl": f"http://127.0.0.1:{port}/v1",
                "api": "openai-completions",
                "apiKey": "unused",
                "models": [{"id": "fake-model", "reasoning": False, "input": ["text"]}],
            }
        }
    }
    (agent_dir / "models.json").write_text(json.dumps(models))
    server = subprocess.Popen([sys.executable, str(DUALS / "tests" / "fake_model.py"), str(port), str(tmp / "script.json"), str(log)])
    time.sleep(0.5)
    env = {**os.environ, "PI_CODING_AGENT_DIR": str(agent_dir), "PI_OFFLINE": "1", "PI_TELEMETRY": "0"}
    try:
        run = subprocess.run(
            ["pi", "-p", "--no-session", "--no-approve", "-e", str(EXTENSION), "--provider", "fake", "--model", "fake-model", "Do the task."],
            cwd=work,
            env=env,
            capture_output=True,
            text=True,
            timeout=120,
        )
    finally:
        server.terminate()
    requests = [json.loads(line) for line in log.read_text().splitlines()]
    first, last = requests[0], requests[-1]
    results = tool_results(last)
    notices = [m for m in last["messages"] if m["role"] == "user" and "[bash-done" in json.dumps(m["content"])]

    checks = {
        "only python_repl declared": [t["function"]["name"] for t in first.get("tools", [])] == ["python_repl"],
        "harness prompt present": "This harness has one tool: `python_repl`" in json.dumps(first["messages"][0]),
        "cell result returned": len(results) > 0 and results[0] == "42",
        "variables persist": len(results) > 1 and results[1].strip() == "42",
        "bash and edit work": len(results) > 2 and "wrote hello repl" in results[2],
        "background bash notice delivered": len(notices) == 1 and "exit:0" in json.dumps(notices[0]["content"]),
        "agent continued after notice": run.stdout.strip().endswith("final answer after bash-done"),
    }
    for name, ok in checks.items():
        print(f"{'PASS' if ok else 'FAIL'}  {name}")
    if not all(checks.values()):
        print("--- pi stdout ---\n" + run.stdout[-2000:] + "\n--- pi stderr ---\n" + run.stderr[-2000:])
        print("--- tool results ---\n" + "\n".join(results))
        sys.exit(1)


if __name__ == "__main__":
    main()
