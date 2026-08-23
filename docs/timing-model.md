# Timing Model

## Clocking

ParaRISC uses a synchronous model:

- Combinational logic observes the current cycle state.
- Register updates become visible together at the next clock edge.
- A module should have one clear owner for each piece of hardware state.

## Architectural State

- Register file architectural state changes only through commit.
- Data memory architectural state changes only through committed stores.
- Wrong-path instructions may execute internally, but cannot update architectural state.

## Same-Cycle Priorities

The project-wide priority order is:

1. Reset.
2. Flush or recovery from control-flow redirect.
3. Commit of older completed instructions.
4. Writeback or completion marking.
5. Issue, dispatch, rename, decode, and fetch of younger work.

Specific modules may refine this order, but must document the refinement here before implementation.

## Memory Model

The initial model is a single coherent memory image with explicit load/store requests. Asynchronous memory responses must be matched by tag and epoch before they are allowed to affect CPU state.

## Invariants To Cover

- `x0` remains zero.
- ROB commits in program order.
- Wrong-path work does not update RRAT, architectural memory, or commit statistics.
- Store side effects become visible only at commit.
- No physical register is both free and mapped live.
- RAT mappings always point to valid physical registers.
- ROB, RS, and LSQ occupancy never exceeds capacity.
- Flush eventually releases all younger resources.
- Memory responses match tag and epoch.
- Multi-lane rename preserves bundle order.
- Multi-lane commit stops at the first incomplete instruction.
- Flush dominates younger issue and writeback side effects in the same cycle.
