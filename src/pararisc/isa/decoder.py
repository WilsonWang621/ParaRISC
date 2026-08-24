"""RV32IM instruction decoder."""

from __future__ import annotations

from collections.abc import Iterable

from src.pararisc.common.interfaces import DecodedUop, FuType, UopFlag

from .encoding import (
    FUNCT7_BASE,
    FUNCT7_MULDIV,
    FUNCT7_SUB_SRA,
    OPCODE_AUIPC,
    OPCODE_BRANCH,
    OPCODE_JAL,
    OPCODE_JALR,
    OPCODE_LOAD,
    OPCODE_LUI,
    OPCODE_OP,
    OPCODE_OP_IMM,
    OPCODE_STORE,
    funct3,
    funct7,
    normalize_instruction,
    opcode,
    rd,
    rs1,
    rs2,
)
from .immediate import imm_b, imm_i, imm_j, imm_s, imm_u


BRANCH_OPS = {
    0b000: "BEQ",
    0b001: "BNE",
    0b100: "BLT",
    0b101: "BGE",
    0b110: "BLTU",
    0b111: "BGEU",
}

LOAD_OPS = {
    0b000: "LB",
    0b001: "LH",
    0b010: "LW",
    0b100: "LBU",
    0b101: "LHU",
}

STORE_OPS = {
    0b000: "SB",
    0b001: "SH",
    0b010: "SW",
}

OP_IMM_BASE_OPS = {
    0b000: "ADDI",
    0b010: "SLTI",
    0b011: "SLTIU",
    0b100: "XORI",
    0b110: "ORI",
    0b111: "ANDI",
}

OP_BASE_OPS = {
    (0b000, FUNCT7_BASE): ("ADD", FuType.ALU),
    (0b000, FUNCT7_SUB_SRA): ("SUB", FuType.ALU),
    (0b001, FUNCT7_BASE): ("SLL", FuType.ALU),
    (0b010, FUNCT7_BASE): ("SLT", FuType.ALU),
    (0b011, FUNCT7_BASE): ("SLTU", FuType.ALU),
    (0b100, FUNCT7_BASE): ("XOR", FuType.ALU),
    (0b101, FUNCT7_BASE): ("SRL", FuType.ALU),
    (0b101, FUNCT7_SUB_SRA): ("SRA", FuType.ALU),
    (0b110, FUNCT7_BASE): ("OR", FuType.ALU),
    (0b111, FUNCT7_BASE): ("AND", FuType.ALU),
}

OP_MULDIV_OPS = {
    0b000: ("MUL", FuType.MUL),
    0b001: ("MULH", FuType.MUL),
    0b010: ("MULHSU", FuType.MUL),
    0b011: ("MULHU", FuType.MUL),
    0b100: ("DIV", FuType.DIV),
    0b101: ("DIVU", FuType.DIV),
    0b110: ("REM", FuType.DIV),
    0b111: ("REMU", FuType.DIV),
}


def decode(instruction: int, pc: int = 0) -> DecodedUop:
    """Decode one 32-bit RV32IM instruction word."""

    inst = normalize_instruction(instruction)
    op = opcode(inst)

    if op == OPCODE_LUI:
        return _uop(inst, pc, "LUI", rd_value=rd(inst), imm_value=imm_u(inst), fu_type=FuType.ALU, flags=[UopFlag.WRITES_RD])

    if op == OPCODE_AUIPC:
        return _uop(inst, pc, "AUIPC", rd_value=rd(inst), imm_value=imm_u(inst), fu_type=FuType.ALU, flags=[UopFlag.WRITES_RD])

    if op == OPCODE_JAL:
        return _uop(
            inst,
            pc,
            "JAL",
            rd_value=rd(inst),
            imm_value=imm_j(inst),
            fu_type=FuType.JUMP,
            flags=[UopFlag.WRITES_RD, UopFlag.IS_JUMP],
        )

    if op == OPCODE_JALR:
        if funct3(inst) != 0b000:
            return _illegal(inst, pc)
        return _uop(
            inst,
            pc,
            "JALR",
            rs1_value=rs1(inst),
            rd_value=rd(inst),
            imm_value=imm_i(inst),
            fu_type=FuType.JUMP,
            flags=[UopFlag.WRITES_RD, UopFlag.READS_RS1, UopFlag.IS_JUMP],
        )

    if op == OPCODE_BRANCH:
        name = BRANCH_OPS.get(funct3(inst))
        if name is None:
            return _illegal(inst, pc)
        flags = [UopFlag.READS_RS1, UopFlag.READS_RS2, UopFlag.IS_BRANCH]
        if name.endswith("U"):
            flags.append(UopFlag.IS_UNSIGNED)
        return _uop(
            inst,
            pc,
            name,
            rs1_value=rs1(inst),
            rs2_value=rs2(inst),
            imm_value=imm_b(inst),
            fu_type=FuType.BRANCH,
            flags=flags,
        )

    if op == OPCODE_LOAD:
        name = LOAD_OPS.get(funct3(inst))
        if name is None:
            return _illegal(inst, pc)
        flags = [UopFlag.WRITES_RD, UopFlag.READS_RS1, UopFlag.IS_LOAD]
        if name.endswith("U"):
            flags.append(UopFlag.IS_UNSIGNED)
        return _uop(
            inst,
            pc,
            name,
            rs1_value=rs1(inst),
            rd_value=rd(inst),
            imm_value=imm_i(inst),
            fu_type=FuType.LOAD,
            flags=flags,
        )

    if op == OPCODE_STORE:
        name = STORE_OPS.get(funct3(inst))
        if name is None:
            return _illegal(inst, pc)
        return _uop(
            inst,
            pc,
            name,
            rs1_value=rs1(inst),
            rs2_value=rs2(inst),
            imm_value=imm_s(inst),
            fu_type=FuType.STORE,
            flags=[UopFlag.READS_RS1, UopFlag.READS_RS2, UopFlag.IS_STORE],
        )

    if op == OPCODE_OP_IMM:
        return _decode_op_imm(inst, pc)

    if op == OPCODE_OP:
        return _decode_op(inst, pc)

    return _illegal(inst, pc)


def _decode_op_imm(inst: int, pc: int) -> DecodedUop:
    f3 = funct3(inst)
    f7 = funct7(inst)

    if f3 in OP_IMM_BASE_OPS:
        return _uop(
            inst,
            pc,
            OP_IMM_BASE_OPS[f3],
            rs1_value=rs1(inst),
            rd_value=rd(inst),
            imm_value=imm_i(inst),
            fu_type=FuType.ALU,
            flags=[UopFlag.WRITES_RD, UopFlag.READS_RS1],
        )

    if f3 == 0b001 and f7 == FUNCT7_BASE:
        return _uop(
            inst,
            pc,
            "SLLI",
            rs1_value=rs1(inst),
            rd_value=rd(inst),
            imm_value=(inst >> 20) & 0x1F,
            fu_type=FuType.ALU,
            flags=[UopFlag.WRITES_RD, UopFlag.READS_RS1],
        )

    if f3 == 0b101 and f7 in (FUNCT7_BASE, FUNCT7_SUB_SRA):
        return _uop(
            inst,
            pc,
            "SRLI" if f7 == FUNCT7_BASE else "SRAI",
            rs1_value=rs1(inst),
            rd_value=rd(inst),
            imm_value=(inst >> 20) & 0x1F,
            fu_type=FuType.ALU,
            flags=[UopFlag.WRITES_RD, UopFlag.READS_RS1],
        )

    return _illegal(inst, pc)


def _decode_op(inst: int, pc: int) -> DecodedUop:
    f3 = funct3(inst)
    f7 = funct7(inst)

    if f7 == FUNCT7_MULDIV:
        entry = OP_MULDIV_OPS.get(f3)
    else:
        entry = OP_BASE_OPS.get((f3, f7))

    if entry is None:
        return _illegal(inst, pc)

    name, fu_type = entry
    flags = [UopFlag.WRITES_RD, UopFlag.READS_RS1, UopFlag.READS_RS2]
    if name in {"SLTU", "DIVU", "REMU", "MULHU"}:
        flags.append(UopFlag.IS_UNSIGNED)

    return _uop(
        inst,
        pc,
        name,
        rs1_value=rs1(inst),
        rs2_value=rs2(inst),
        rd_value=rd(inst),
        fu_type=fu_type,
        flags=flags,
    )


def _uop(
    instruction: int,
    pc: int,
    opcode_name: str,
    *,
    rs1_value: int = 0,
    rs2_value: int = 0,
    rd_value: int = 0,
    imm_value: int = 0,
    fu_type: FuType,
    flags: Iterable[UopFlag],
) -> DecodedUop:
    return DecodedUop(
        valid=True,
        illegal=False,
        pc=pc,
        instruction=instruction,
        opcode=opcode_name,
        rs1=rs1_value,
        rs2=rs2_value,
        rd=rd_value,
        imm=imm_value,
        fu_type=fu_type,
        flags=frozenset(flags),
    )


def _illegal(instruction: int, pc: int) -> DecodedUop:
    return DecodedUop(
        valid=False,
        illegal=True,
        pc=pc,
        instruction=instruction,
        opcode="ILLEGAL",
        fu_type=FuType.INVALID,
        flags=frozenset(),
    )
