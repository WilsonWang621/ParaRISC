#!/usr/bin/env sh
set -eu

if [ -z "${ASSASSYN_HOME:-}" ] && [ -d "../assassyn/python/assassyn" ]; then
    ASSASSYN_HOME="$(cd ../assassyn && pwd)"
    export ASSASSYN_HOME
fi

if [ -n "${ASSASSYN_HOME:-}" ]; then
    export PYTHONPATH="$ASSASSYN_HOME/python${PYTHONPATH:+:$PYTHONPATH}"
    export VERILATOR_ROOT="${VERILATOR_ROOT:-$ASSASSYN_HOME/3rd-party/verilator}"
    export CARGO_TARGET_DIR="${CARGO_TARGET_DIR:-$(pwd)/build/cargo-target}"
    export CCACHE_DIR="${CCACHE_DIR:-$(pwd)/build/ccache}"
    export PATH="$ASSASSYN_HOME/3rd-party/verilator/bin:$ASSASSYN_HOME/.assassyn-venv/bin:$PATH"
fi

PYTHON_BIN="${PYTHON:-python}"
exec "$PYTHON_BIN" scripts/check.py
