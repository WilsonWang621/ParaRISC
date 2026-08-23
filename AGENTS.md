# ParaRISC Agent Guide

This repository implements ParaRISC, a staged RV32IM CPU project using Assassyn.

## Working Rules

- Keep `main` runnable. Do not leave unexplained failing tests on it.
- Prefer small, reviewable patches with one behavioral purpose.
- Read `docs/spec.md`, `docs/interfaces.md`, and `docs/timing-model.md` before changing CPU behavior.
- Update the relevant document when changing ISA scope, public interfaces, timing semantics, test commands, or verification assumptions.
- Do not mix public interface changes with unrelated optimizations.
- Add or update tests for behavioral changes.
- Preserve architectural correctness before performance.

## Ownership Boundaries

- The user owns datapath decisions, state-machine semantics, same-cycle priority rules, and acceptance of optimizations.
- Codex may scaffold files, add tests, write command wrappers, generate repetitive decoder/test code, parse reports, update docs, and produce minimal fixes for clear failing tests.
- Codex must not silently change frozen public interfaces, commit trace format, or timing semantics.

## Standard Commands

```bash
make smoke
make test-unit
make test-isa
make test-reference
make test-all
```

`make smoke` is the Day 1 environment gate.
