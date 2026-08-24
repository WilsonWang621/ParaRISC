from src.pararisc.isa.encoding import (
    OPCODE_BRANCH,
    OPCODE_JAL,
    OPCODE_LUI,
    OPCODE_OP_IMM,
    OPCODE_STORE,
    encode_b_type,
    encode_i_type,
    encode_j_type,
    encode_s_type,
    encode_u_type,
)
from src.pararisc.isa.immediate import imm_b, imm_i, imm_j, imm_s, imm_u, sign_extend


def test_sign_extend_positive_boundary():
    assert sign_extend(0x7FF, 12) == 2047


def test_sign_extend_negative_boundary():
    assert sign_extend(0x800, 12) == -2048
    assert sign_extend(0xFFF, 12) == -1


def test_i_type_immediate_boundaries():
    assert imm_i(encode_i_type(OPCODE_OP_IMM, 1, 0, 2, 2047)) == 2047
    assert imm_i(encode_i_type(OPCODE_OP_IMM, 1, 0, 2, -2048)) == -2048
    assert imm_i(encode_i_type(OPCODE_OP_IMM, 1, 0, 2, -1)) == -1


def test_s_type_immediate_boundaries():
    assert imm_s(encode_s_type(OPCODE_STORE, 2, 1, 3, 2047)) == 2047
    assert imm_s(encode_s_type(OPCODE_STORE, 2, 1, 3, -2048)) == -2048
    assert imm_s(encode_s_type(OPCODE_STORE, 2, 1, 3, -16)) == -16


def test_b_type_immediate_boundaries():
    assert imm_b(encode_b_type(OPCODE_BRANCH, 0, 1, 2, 4094)) == 4094
    assert imm_b(encode_b_type(OPCODE_BRANCH, 0, 1, 2, -4096)) == -4096
    assert imm_b(encode_b_type(OPCODE_BRANCH, 0, 1, 2, -4)) == -4


def test_u_type_immediate_keeps_upper_bits_and_clears_low_bits():
    assert imm_u(encode_u_type(OPCODE_LUI, 1, 0x12345000)) == 0x12345000
    assert imm_u(encode_u_type(OPCODE_LUI, 1, 0xFFFFF000)) == 0xFFFFF000


def test_j_type_immediate_boundaries():
    assert imm_j(encode_j_type(OPCODE_JAL, 1, 1_048_574)) == 1_048_574
    assert imm_j(encode_j_type(OPCODE_JAL, 1, -1_048_576)) == -1_048_576
    assert imm_j(encode_j_type(OPCODE_JAL, 1, -2048)) == -2048
