"""Architectural commit trace records for the reference model."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CommitTrace:
    """One architecturally committed instruction."""

    sequence: int
    pc: int
    instruction: int
    rd: int | None
    rd_value: int | None
    memory_address: int | None
    memory_value: int | None
    next_pc: int
