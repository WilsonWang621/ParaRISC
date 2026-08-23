#!/usr/bin/env python
"""Day 1 environment smoke check."""

from __future__ import annotations

import importlib
from pathlib import Path
import sys


def require_import(module_name: str) -> object:
    try:
        return importlib.import_module(module_name)
    except Exception as exc:  # pragma: no cover - exact environment error matters.
        raise SystemExit(f"failed to import {module_name}: {exc}") from exc


def main() -> int:
    print(f"python: {sys.executable}")
    print(f"version: {sys.version.split()[0]}")

    assassyn = require_import("assassyn")
    location = getattr(assassyn, "__file__", "<namespace package>")
    print(f"assassyn: {location}")

    run_driver_smoke()
    print("smoke: ok")
    return 0


def run_driver_smoke() -> None:
    from assassyn.frontend import Module, module
    from assassyn.test import run_test

    class Driver(Module):
        def __init__(self):
            super().__init__(ports={})

        @module.combinational
        def build(self):
            from assassyn.frontend import RegArray, UInt, log

            cnt = RegArray(UInt(32), 1)
            (cnt & self)[0] <= cnt[0] + UInt(32)(1)
            log("cnt: {}", cnt[0])

    def top():
        driver = Driver()
        driver.build()

    def check(raw: str) -> None:
        expected = 0
        for line in raw.splitlines():
            if "cnt:" not in line:
                continue
            got = int(line.split()[-1])
            if got != expected:
                raise AssertionError(f"driver count mismatch: got {got}, expected {expected}")
            expected += 1
        if expected != 100:
            raise AssertionError(f"driver emitted {expected} counts, expected 100")

    workspace = Path("build/assassyn-smoke")
    workspace.mkdir(parents=True, exist_ok=True)
    run_test("driver_smoke", top, check, path=str(workspace), verilog=False)
    print("assassyn driver: ok")


if __name__ == "__main__":
    raise SystemExit(main())
