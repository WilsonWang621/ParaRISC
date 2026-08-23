# Public Interfaces

These interfaces are an initial contract draft. They may evolve before the Day 10 freeze, but every change should be documented here.

## FetchPacket

- `valid`
- `pc`
- `instruction`
- `predicted_pc`
- `epoch`

## DecodedUop

- `pc`
- `opcode`
- `rs1`
- `rs2`
- `rd`
- `imm`
- `fu_type`
- `flags`

## RenamedUop

- `ps1`
- `ps2`
- `pdst`
- `old_pdst`
- `rob_tag`
- `src_ready`

## IssuePacket

- `rob_tag`
- `pdst`
- `src_values`
- `operation`
- `imm`

## WritebackPacket

- `rob_tag`
- `pdst`
- `value`
- `branch_taken`
- `target`
- `exception`

## CommitPacket

- `pc`
- `instruction`
- `arch_rd`
- `value`
- `store_info`

## MemoryRequest

- `valid`
- `op`
- `address`
- `data`
- `mask`
- `tag`
- `epoch`

## MemoryResponse

- `valid`
- `data`
- `tag`
- `epoch`

## Interface Change Rule

After the Day 10 interface freeze, a public interface change must:

- Update this file.
- Update every producer and consumer.
- Add compatibility or migration tests.
- Be committed separately from feature or optimization work.
