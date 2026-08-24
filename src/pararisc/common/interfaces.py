"""Public data structures shared by ParaRISC pipeline stages."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto


class FuType(Enum):
    """Functional unit class selected by decode."""

    INVALID = auto()
    ALU = auto()
    BRANCH = auto()
    JUMP = auto()
    LOAD = auto()
    STORE = auto()
    MUL = auto()
    DIV = auto()
    SYSTEM = auto()


class UopFlag(Enum):
    """Boolean decode attributes carried with a decoded uop."""

    WRITES_RD = auto()
    READS_RS1 = auto()
    READS_RS2 = auto()
    IS_BRANCH = auto()
    IS_JUMP = auto()
    IS_LOAD = auto()
    IS_STORE = auto()
    IS_UNSIGNED = auto()


@dataclass(frozen=True)
class DecodedUop:
    """Decoded instruction fields before rename or execution."""

    valid: bool
    illegal: bool
    pc: int
    instruction: int
    opcode: str
    rs1: int = 0
    rs2: int = 0
    rd: int = 0
    imm: int = 0
    fu_type: FuType = FuType.INVALID
    flags: frozenset[UopFlag] = field(default_factory=frozenset)

    @property
    def writes_rd(self) -> bool:
        return UopFlag.WRITES_RD in self.flags

    @property
    def reads_rs1(self) -> bool:
        return UopFlag.READS_RS1 in self.flags

    @property
    def reads_rs2(self) -> bool:
        return UopFlag.READS_RS2 in self.flags
