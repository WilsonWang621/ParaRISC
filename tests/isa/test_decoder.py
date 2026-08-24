from src.pararisc.common.interfaces import FuType, UopFlag
from src.pararisc.isa.decoder import decode
from src.pararisc.isa.encoding import (
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
    encode_b_type,
    encode_i_type,
    encode_j_type,
    encode_r_type,
    encode_s_type,
    encode_u_type,
)


def test_decode_lui_u_type():
    uop = decode(encode_u_type(OPCODE_LUI, 5, 0x12345000), pc=0x1000)
    assert uop.valid
    assert not uop.illegal
    assert uop.opcode == "LUI"
    assert uop.pc == 0x1000
    assert uop.rd == 5
    assert uop.imm == 0x12345000
    assert uop.fu_type == FuType.ALU
    assert uop.writes_rd


def test_decode_auipc_u_type():
    uop = decode(encode_u_type(OPCODE_AUIPC, 6, 0xFFFFF000))
    assert uop.opcode == "AUIPC"
    assert uop.rd == 6
    assert uop.imm == 0xFFFFF000
    assert uop.writes_rd


def test_decode_jal_j_type():
    uop = decode(encode_j_type(OPCODE_JAL, 1, -2048))
    assert uop.opcode == "JAL"
    assert uop.rd == 1
    assert uop.imm == -2048
    assert uop.fu_type == FuType.JUMP
    assert UopFlag.IS_JUMP in uop.flags


def test_decode_jalr_i_type():
    uop = decode(encode_i_type(OPCODE_JALR, 1, 0b000, 2, 12))
    assert uop.opcode == "JALR"
    assert uop.rd == 1
    assert uop.rs1 == 2
    assert uop.imm == 12
    assert uop.reads_rs1
    assert uop.writes_rd


def test_decode_branch_b_type():
    uop = decode(encode_b_type(OPCODE_BRANCH, 0b000, 3, 4, -4))
    assert uop.opcode == "BEQ"
    assert uop.rs1 == 3
    assert uop.rs2 == 4
    assert uop.imm == -4
    assert uop.fu_type == FuType.BRANCH
    assert uop.reads_rs1
    assert uop.reads_rs2
    assert UopFlag.IS_BRANCH in uop.flags


def test_decode_unsigned_branch_flag():
    uop = decode(encode_b_type(OPCODE_BRANCH, 0b110, 3, 4, 8))
    assert uop.opcode == "BLTU"
    assert UopFlag.IS_UNSIGNED in uop.flags


def test_decode_load_i_type():
    uop = decode(encode_i_type(OPCODE_LOAD, 8, 0b010, 9, -16))
    assert uop.opcode == "LW"
    assert uop.rd == 8
    assert uop.rs1 == 9
    assert uop.imm == -16
    assert uop.fu_type == FuType.LOAD
    assert UopFlag.IS_LOAD in uop.flags


def test_decode_store_s_type():
    uop = decode(encode_s_type(OPCODE_STORE, 0b010, 10, 11, 20))
    assert uop.opcode == "SW"
    assert uop.rs1 == 10
    assert uop.rs2 == 11
    assert uop.imm == 20
    assert uop.fu_type == FuType.STORE
    assert UopFlag.IS_STORE in uop.flags
    assert not uop.writes_rd


def test_decode_op_imm_i_type():
    uop = decode(encode_i_type(OPCODE_OP_IMM, 12, 0b000, 13, -1))
    assert uop.opcode == "ADDI"
    assert uop.rd == 12
    assert uop.rs1 == 13
    assert uop.imm == -1
    assert uop.fu_type == FuType.ALU


def test_decode_shift_immediate_distinguishes_srli_and_srai():
    srli = decode(encode_i_type(OPCODE_OP_IMM, 1, 0b101, 2, 3))
    srai = decode(encode_i_type(OPCODE_OP_IMM, 1, 0b101, 2, (FUNCT7_SUB_SRA << 5) | 3))
    assert srli.opcode == "SRLI"
    assert srli.imm == 3
    assert srai.opcode == "SRAI"
    assert srai.imm == 3


def test_decode_r_type_distinguishes_add_and_sub():
    add = decode(encode_r_type(OPCODE_OP, 1, 0b000, 2, 3, FUNCT7_BASE))
    sub = decode(encode_r_type(OPCODE_OP, 1, 0b000, 2, 3, FUNCT7_SUB_SRA))
    assert add.opcode == "ADD"
    assert sub.opcode == "SUB"
    assert add.rs1 == 2
    assert add.rs2 == 3
    assert add.rd == 1


def test_decode_m_extension_ops():
    mul = decode(encode_r_type(OPCODE_OP, 1, 0b000, 2, 3, FUNCT7_MULDIV))
    divu = decode(encode_r_type(OPCODE_OP, 4, 0b101, 5, 6, FUNCT7_MULDIV))
    remu = decode(encode_r_type(OPCODE_OP, 7, 0b111, 8, 9, FUNCT7_MULDIV))
    assert mul.opcode == "MUL"
    assert mul.fu_type == FuType.MUL
    assert divu.opcode == "DIVU"
    assert divu.fu_type == FuType.DIV
    assert UopFlag.IS_UNSIGNED in divu.flags
    assert remu.opcode == "REMU"
    assert UopFlag.IS_UNSIGNED in remu.flags


def test_illegal_opcode_does_not_write_register():
    uop = decode(0x00000000)
    assert not uop.valid
    assert uop.illegal
    assert uop.opcode == "ILLEGAL"
    assert not uop.writes_rd
    assert uop.fu_type == FuType.INVALID


def test_illegal_funct_combination_does_not_write_register():
    uop = decode(encode_r_type(OPCODE_OP, 1, 0b000, 2, 3, 0b1111111))
    assert not uop.valid
    assert uop.illegal
    assert not uop.writes_rd


def test_x0_write_is_preserved_by_decode():
    uop = decode(encode_i_type(OPCODE_OP_IMM, 0, 0b000, 1, 7))
    assert uop.valid
    assert not uop.illegal
    assert uop.opcode == "ADDI"
    assert uop.rd == 0
    assert uop.writes_rd
