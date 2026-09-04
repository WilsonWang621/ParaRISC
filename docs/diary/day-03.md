# Day 03 Diary

## Goals

- Build a pure Python sequential RV32IM reference interpreter.
- Model architectural registers, PC, and byte-addressed memory.
- Emit architectural commit traces.
- Add deterministic tests for arithmetic, shifts, branches, jumps, memory, and M-extension edge cases.
- Add reproducible random reference-model tests.

## Completed

- Added reference-model package under `src/pararisc/reference`.
- Added `CommitTrace` and trace JSONL serialization/comparison helpers.
- Added RV32 arithmetic helpers:
  - `u32`
  - `i32`
  - `shamt`
  - `bool32`
  - signed division with truncation toward zero
- Added sparse little-endian `ByteMemory`.
- Added `RV32IMModel` with:
  - 32 architectural registers
  - `x0` hardwired to zero
  - PC fetch and update
  - byte-addressed memory access
  - per-instruction commit trace emission

## Supported Instructions

- `LUI`, `AUIPC`
- `JAL`, `JALR`
- `BEQ`, `BNE`, `BLT`, `BGE`, `BLTU`, `BGEU`
- `LB`, `LH`, `LW`, `LBU`, `LHU`
- `SB`, `SH`, `SW`
- `ADDI`, `SLTI`, `SLTIU`, `XORI`, `ORI`, `ANDI`
- `SLLI`, `SRLI`, `SRAI`
- `ADD`, `SUB`, `SLL`, `SLT`, `SLTU`, `XOR`, `SRL`, `SRA`, `OR`, `AND`
- `MUL`, `MULH`, `MULHSU`, `MULHU`, `DIV`, `DIVU`, `REM`, `REMU`

## Tests Added

- `tests/reference/test_memory.py`
- `tests/reference/test_rv32im_model.py`
- `tests/reference/test_trace.py`
- `tests/reference/test_random_programs.py`

Coverage includes:

- 32-bit wraparound.
- Signed and unsigned comparison.
- Logical and arithmetic right shift.
- Jump link behavior and `JALR` target bit clearing.
- Branch taken and not-taken behavior.
- Load/store little-endian behavior.
- Load sign extension and zero extension.
- M-extension multiply high-word behavior.
- Division by zero.
- `INT_MIN / -1`.
- Handwritten loop program.
- Seeded random program reproducibility.

## Commands Run

```bash
python -m pytest tests/reference
make test-reference
make test-all
```

Current result:

- `tests/reference`: 51 passed.
- `make test-reference`: 51 passed.
- `make test-all`: passed.

`make smoke` may print crates.io DNS warnings in this environment and then pass through Cargo offline mode using local cache.

## Open Questions

- Confirm whether the course test harness expects `ECALL` or `EBREAK` as a stop protocol.
- Confirm whether misaligned load/store should trap, be rejected, or be supported byte-by-byte in the reference model.
- Confirm the Day 4 program image layout: text base, data base, stack pointer, and halt convention.

## Next Day

- Set the program start PC, data region base, stack pointer, and stop protocol.
- Prepare minimal C or assembly programs for sum, vector add, and vector multiply.
- Add RISC-V toolchain scripts for compile, disassemble, and image extraction.
- Check generated disassembly for unsupported instructions.
