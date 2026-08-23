# Decision 0001: Initial Project Scope

## Status

Accepted for Day 1.

## Decision

The project will target RV32IM and follow the staged roadmap:

1. Reference model.
2. Single-cycle or minimal executable Assassyn core.
3. Five-stage in-order CPU.
4. Single-issue out-of-order CPU.
5. Configurable multi-issue out-of-order CPU.
6. Optimization, parameter sweep, and synthesis experiments.

The initial implementation will include `JAL` and `JALR`. CSR, privileged mode, exceptions, interrupts, floating point, atomics, and virtual memory are out of scope unless course materials require them.

## Rationale

This scope preserves the project goal while keeping Day 1 focused on environment, contracts, and command structure. Function calls from compiled C normally require jumps and returns, so excluding `JAL` and `JALR` would create avoidable integration risk.

## Consequences

- The decoder and reference model must handle RV32I control flow and RV32M arithmetic.
- Tests should include function-call shaped programs before the in-order baseline is frozen.
- Any course requirement that contradicts this decision must update `docs/spec.md`.
