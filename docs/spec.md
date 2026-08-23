# ParaRISC Specification

## Goal

ParaRISC is a staged RV32IM CPU implementation using Assassyn. The project starts from a software reference model and an in-order baseline, then grows into a configurable out-of-order CPU with optimization and synthesis experiments.

## Initial ISA Scope

The target ISA is RV32IM for user-level integer programs.

Required instruction groups:

- RV32I integer arithmetic and logic.
- RV32I loads and stores.
- RV32I conditional branches.
- `JAL` and `JALR`, because compiler-generated function calls and returns usually require them.
- RV32M multiply and divide operations.

Out of scope unless course requirements say otherwise:

- CSR instructions.
- Privileged instructions.
- Exceptions and interrupts.
- Virtual memory.
- Floating point.
- Atomic instructions.
- `FENCE` and memory-ordering features beyond the project memory model.

## Required Programs

The implementation must correctly run:

- Sum from 0 to 100.
- Vector element-wise multiplication.
- Vector element-wise addition.

## Correctness Standard

For every supported configuration, architectural results must match sequential RV32IM execution:

- `x0` is always zero.
- Committed register values match the reference model.
- Stores become architecturally visible only when committed.
- Wrong-path execution cannot modify architectural state.

## Day 1 Stop Conditions

Day 1 is complete when:

- `python -c 'import assassyn'` succeeds in the selected environment.
- A minimal Assassyn driver smoke check runs.
- `make smoke` succeeds.
- The initial scaffold is committed as `chore: scaffold ParaRISC repository`.

## Open Questions

- Confirm with course staff whether `COMMIT_WIDTH` must equal `BACKEND_WIDTH`.
- Confirm whether the official tests require all RV32M divide and remainder edge cases.
- Confirm the expected memory image format and I/O conventions.
- Confirm whether any CSR instructions appear in the supplied toolchain output.
