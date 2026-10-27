#!/bin/sh
# Build the Python environment the REPL duals run in: Prime Agent's own kernel
# runtime and edit skill at a pinned commit, plus the packages Prime Agent
# pre-installs in its kernel (DEFAULT_RLM_EXTRA_PACKAGES).
#
# Usage: duals/scripts/setup-kernel.sh <venv-dir>
# Prints the kernel interpreter path on success.
set -eu

venv="${1:?usage: setup-kernel.sh <venv-dir>}"
commit="8aac8692456c00c01d4e53e60e6d3347a3506559"  # prime-agent v0.10.1
repo="git+https://github.com/PrimeIntellect-ai/prime-agent@${commit}"

uv venv --quiet --python 3.13 "$venv"
uv pip install --quiet --python "$venv/bin/python" \
    "prime-agent-runtime @ ${repo}#subdirectory=prime-agent-runtime" \
    "edit @ ${repo}#subdirectory=skills/edit" \
    dill \
    requests httpx pyyaml tomli python-dotenv pandas numpy scipy beautifulsoup4 lxml pydantic tyro
echo "$venv/bin/python"
