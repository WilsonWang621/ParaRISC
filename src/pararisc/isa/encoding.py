"""RV32IM instruction field extraction and encoding constants."""

from __future__ import annotations


XLEN = 32
INSTRUCTION_BITS = 32
REGISTER_COUNT = 32


OPCODE_LOAD = 0b0000011
OPCODE_OP_IMM = 0b0010011
OPCODE_AUIPC = 0b0010111
OPCODE_STORE = 0b0100011
OPCODE_OP = 0b0110011
OPCODE_LUI = 0b0110111
OPCODE_BRANCH = 0b1100011
OPCODE_JALR = 0b1100111
OPCODE_JAL = 0b1101111
OPCODE_SYSTEM = 0b1110011


FUNCT7_BASE = 0b0000000
FUNCT7_SUB_SRA = 0b0100000
FUNCT7_MULDIV = 0b0000001


MASK_32 = 0xFFFFFFFF


def bits(value: int, high: int, low: int) -> int:
    """Return inclusive bit slice value[high:low]."""

    if high < low:
        raise ValueError(f"invalid bit slice [{high}:{low}]")
    if low < 0 or high >= INSTRUCTION_BITS:
        raise ValueError(f"bit slice [{high}:{low}] outside 32-bit instruction")
    width = high - low + 1
    return (value >> low) & ((1 << width) - 1)


def opcode(instruction: int) -> int:
    return bits(instruction, 6, 0)


def rd(instruction: int) -> int:
    return bits(instruction, 11, 7)


def funct3(instruction: int) -> int:
    return bits(instruction, 14, 12)


def rs1(instruction: int) -> int:
    return bits(instruction, 19, 15)


def rs2(instruction: int) -> int:
    return bits(instruction, 24, 20)


def funct7(instruction: int) -> int:
    return bits(instruction, 31, 25)


def normalize_instruction(instruction: int) -> int:
    """Keep only the low 32 bits of an instruction word."""

    return instruction & MASK_32


def encode_r_type(
    opcode_value: int,
    rd_value: int,
    funct3_value: int,
    rs1_value: int,
    rs2_value: int,
    funct7_value: int,
) -> int:
    """Build an R-type instruction for tests."""

    return (
        ((funct7_value & 0x7F) << 25)
        | ((rs2_value & 0x1F) << 20)
        | ((rs1_value & 0x1F) << 15)
        | ((funct3_value & 0x7) << 12)
        | ((rd_value & 0x1F) << 7)
        | (opcode_value & 0x7F)
    )


def encode_i_type(
    opcode_value: int,
    rd_value: int,
    funct3_value: int,
    rs1_value: int,
    imm_value: int,
) -> int:
    """Build an I-type instruction for tests."""

    return (
        ((imm_value & 0xFFF) << 20)
        | ((rs1_value & 0x1F) << 15)
        | ((funct3_value & 0x7) << 12)
        | ((rd_value & 0x1F) << 7)
        | (opcode_value & 0x7F)
    )


def encode_s_type(
    opcode_value: int,
    funct3_value: int,
    rs1_value: int,
    rs2_value: int,
    imm_value: int,
) -> int:
    """Build an S-type instruction for tests."""

    imm = imm_value & 0xFFF
    return (
        (bits(imm, 11, 5) << 25)
        | ((rs2_value & 0x1F) << 20)
        | ((rs1_value & 0x1F) << 15)
        | ((funct3_value & 0x7) << 12)
        | (bits(imm, 4, 0) << 7)
        | (opcode_value & 0x7F)
    )


def encode_b_type(
    opcode_value: int,
    funct3_value: int,
    rs1_value: int,
    rs2_value: int,
    imm_value: int,
) -> int:
    """Build a B-type instruction for tests. imm_value is the byte offset."""

    imm = imm_value & 0x1FFF
    return (
        (bits(imm, 12, 12) << 31)
        | (bits(imm, 10, 5) << 25)
        | ((rs2_value & 0x1F) << 20)
        | ((rs1_value & 0x1F) << 15)
        | ((funct3_value & 0x7) << 12)
        | (bits(imm, 4, 1) << 8)
        | (bits(imm, 11, 11) << 7)
        | (opcode_value & 0x7F)
    )


def encode_u_type(opcode_value: int, rd_value: int, imm_value: int) -> int:
    """Build a U-type instruction for tests."""

    return (imm_value & 0xFFFFF000) | ((rd_value & 0x1F) << 7) | (opcode_value & 0x7F)


def encode_j_type(opcode_value: int, rd_value: int, imm_value: int) -> int:
    """Build a J-type instruction for tests. imm_value is the byte offset."""

    imm = imm_value & 0x1FFFFF
    return (
        (bits(imm, 20, 20) << 31)
        | (bits(imm, 10, 1) << 21)
        | (bits(imm, 11, 11) << 20)
        | (bits(imm, 19, 12) << 12)
        | ((rd_value & 0x1F) << 7)
        | (opcode_value & 0x7F)
    )
