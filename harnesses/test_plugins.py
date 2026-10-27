"""Check that verifiers resolves both plugins, validates their configs, and builds the launch pieces.

Full runs need a container runtime and a model; those happen in phase A0 on the GPU box.

Usage:
    uv pip install --python <verifiers-venv-python> -e harnesses
    <verifiers-venv-python> harnesses/test_plugins.py
"""

from verifiers.v1.utils.loaders import harness_class, harness_config_type

from pi_ladder import DUALS, PiLadderHarnessConfig, wrapper_script
from prime_switches import PrimeSwitchesHarnessConfig, settings


def main() -> None:
    checks = {}
    checks["pi-ladder resolves"] = harness_class("pi-ladder").__name__ == "PiLadderHarness"
    checks["pi-ladder config class"] = harness_config_type("pi-ladder") is PiLadderHarnessConfig
    config = harness_config_type("pi-ladder").model_validate({"id": "pi-ladder", "rung": "L1"})
    checks["pi-ladder rung parses"] = config.rung == "L1" and config.version == "1.4.0"
    script = wrapper_script(".vf-pi-agent-x/pi", "L1")
    checks["L1 launcher adds the REPL extension"] = "--extension /var/tmp/vf-duals/pi/l1-repl/index.ts" in script
    checks["L0 launcher adds nothing"] = "--extension" not in wrapper_script("pi", "L0")
    checks["duals found"] = (DUALS / "pi" / "l1-repl" / "index.ts").is_file()

    checks["prime-switches resolves"] = harness_class("prime-switches").__name__ == "PrimeSwitchesHarness"
    checks["prime-switches config class"] = harness_config_type("prime-switches") is PrimeSwitchesHarnessConfig
    prime = harness_config_type("prime-switches").model_validate(
        {"id": "prime-switches", "rlm_max_depth": 0, "harness_refinements": False}
    )
    checks["prime settings written"] = settings(prime) == {"rlmMaxDepth": 0, "harnessRefinements": False}
    checks["prime defaults write nothing"] = settings(PrimeSwitchesHarnessConfig(id="prime-switches")) == {}

    for name, ok in checks.items():
        print(f"{'PASS' if ok else 'FAIL'}  {name}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
