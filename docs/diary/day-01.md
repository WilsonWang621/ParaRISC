# Day 01 Diary

## Goals

- Freeze the first project scope.
- Establish the minimal repository scaffold.
- Verify the Assassyn environment.
- Create stable make targets for future work.

## Completed

- Created initial project documents.
- Created initial command entry points.
- Created source and test directories required for Day 1.

## Commands Run

```bash
make smoke
python -c 'import assassyn; print(assassyn.__file__)'
git ls-remote https://github.com/Synthesys-Lab/assassyn.git HEAD
python -m pip install git+https://github.com/Synthesys-Lab/assassyn.git
```

Current result: `make smoke` finds the local Assassyn checkout at `/home/wangwenxuan/ACM/PPCA/CSA/assassyn`, imports the Python package, elaborates the minimal Driver smoke system, compiles the generated Rust simulator with Cargo, and passes. `make test-all` also passes; the unit, ISA, and reference targets are placeholders until Day 2 adds tests.

## Open Questions

- Confirm whether `COMMIT_WIDTH` must equal `BACKEND_WIDTH`.
- Confirm exact official program build and memory image format.
- Confirm whether course tests contain CSR or `FENCE` instructions.

## Next Day

- Implement instruction encoding helpers.
- Implement immediate extraction.
- Start the table-driven decoder.
- Add decoder unit tests for R/I/S/B/U/J formats.
