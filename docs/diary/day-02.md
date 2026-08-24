# Day 02 Diary

## Goals

- Implement RV32IM instruction field extraction.
- Implement I/S/B/U/J immediate extraction and sign extension.
- Implement the first public `DecodedUop` type.
- Implement the RV32IM decoder.
- Add ISA tests for instruction formats, immediate boundaries, illegal encodings, and `x0` writes.

## Completed

- Added common decode interfaces:
  - `DecodedUop`
  - `FuType`
  - `UopFlag`
- Added `src/pararisc/isa/encoding.py` with RV32 opcode constants, funct constants, field extractors, and test encoding helpers.
- Added `src/pararisc/isa/immediate.py` with sign extension and I/S/B/U/J immediate extraction.
- Added `src/pararisc/isa/decoder.py` with table-driven RV32IM decode.
- Added `tests/isa/test_immediate.py`.
- Added `tests/isa/test_decoder.py`.
- Changed `make test-isa` to run `python -m pytest tests/isa`.

## Supported Decode Scope

- `LUI`, `AUIPC`
- `JAL`, `JALR`
- `BEQ`, `BNE`, `BLT`, `BGE`, `BLTU`, `BGEU`
- `LB`, `LH`, `LW`, `LBU`, `LHU`
- `SB`, `SH`, `SW`
- `ADDI`, `SLTI`, `SLTIU`, `XORI`, `ORI`, `ANDI`
- `SLLI`, `SRLI`, `SRAI`
- `ADD`, `SUB`, `SLL`, `SLT`, `SLTU`, `XOR`, `SRL`, `SRA`, `OR`, `AND`
- `MUL`, `MULH`, `MULHSU`, `MULHU`, `DIV`, `DIVU`, `REM`, `REMU`

## Commands Run

```bash
python -m pytest tests/isa/test_immediate.py
python -m pytest tests/isa
make test-isa
make test-all
```

Current result:

- `tests/isa`: 22 passed.
- `make test-all`: passed.

`make smoke` may print crates.io DNS warnings in the current environment, then fall back to Cargo offline mode and pass using local cache.

## Open Questions

- Confirm whether illegal instructions should remain `DecodedUop(valid=False, illegal=True)` or later become an exception/ trap path.
- Confirm whether `SYSTEM` instructions should stay fully illegal or get a minimal `ECALL/EBREAK` decode for tests.
- Confirm whether shift-immediate reserved high bits should eventually produce a distinct illegal reason.

## Next Day

- Start the pure Python RV32IM reference interpreter.
- Implement architectural registers, PC, and byte-addressed memory.
- Define the commit trace format.
- Add deterministic reference-model tests for arithmetic, branches, loads, stores, and M-extension edge cases.
