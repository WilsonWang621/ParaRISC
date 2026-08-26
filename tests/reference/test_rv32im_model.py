import pytest

from src.pararisc.isa.encoding import (
    FUNCT7_BASE,
    FUNCT7_MULDIV,
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
from src.pararisc.reference.rv32im_model import (
    IllegalInstruction,
    RV32IMModel,
)


def test_addi_updates_register_and_pc():
    model = RV32IMModel()
    model.load_program(0x80000000, [encode_i_type(OPCODE_OP_IMM, 1, 0b000, 0, 5)])

    trace = model.step()

    assert model.read_reg(1) == 5
    assert model.pc == 0x80000004
    assert trace.sequence == 0
    assert trace.pc == 0x80000000
    assert trace.rd == 1
    assert trace.rd_value == 5
    assert trace.memory_address is None
    assert trace.memory_value is None
    assert trace.next_pc == 0x80000004


def test_addi_result_wraps_to_32_bits():
    model = RV32IMModel()
    model.write_reg(1, 0xFFFFFFFF)
    model.load_program(0, [encode_i_type(OPCODE_OP_IMM, 2, 0b000, 1, 1)])

    model.step()

    assert model.read_reg(2) == 0


def test_op_imm_comparisons_use_signed_and_unsigned_semantics():
    model = RV32IMModel()
    model.write_reg(1, 0xFFFFFFFF)
    program = [
        encode_i_type(OPCODE_OP_IMM, 2, 0b010, 1, 1),
        encode_i_type(OPCODE_OP_IMM, 3, 0b011, 1, 1),
    ]
    model.load_program(0, program)

    model.run(2)

    assert model.read_reg(2) == 1
    assert model.read_reg(3) == 0


def test_op_imm_logic_operations():
    model = RV32IMModel()
    model.write_reg(1, 0xFFFF0000)
    program = [
        encode_i_type(OPCODE_OP_IMM, 2, 0b100, 1, 0x0FF),
        encode_i_type(OPCODE_OP_IMM, 3, 0b110, 1, 0x0FF),
        encode_i_type(OPCODE_OP_IMM, 4, 0b111, 1, 0x0FF),
    ]
    model.load_program(0, program)

    model.run(3)

    assert model.read_reg(2) == 0xFFFF00FF
    assert model.read_reg(3) == 0xFFFF00FF
    assert model.read_reg(4) == 0


def test_op_imm_shift_operations():
    model = RV32IMModel()
    model.write_reg(1, 0x80000000)
    program = [
        encode_i_type(OPCODE_OP_IMM, 2, 0b001, 1, 1),
        encode_i_type(OPCODE_OP_IMM, 3, 0b101, 1, 1),
        encode_i_type(OPCODE_OP_IMM, 4, 0b101, 1, (0b0100000 << 5) | 1),
    ]
    model.load_program(0, program)

    model.run(3)

    assert model.read_reg(2) == 0
    assert model.read_reg(3) == 0x40000000
    assert model.read_reg(4) == 0xC0000000


def test_r_type_add_sub_and_wraparound():
    model = RV32IMModel()
    model.write_reg(1, 0xFFFFFFFF)
    model.write_reg(2, 2)
    program = [
        encode_r_type(OPCODE_OP, 3, 0b000, 1, 2, FUNCT7_BASE),
        encode_r_type(OPCODE_OP, 4, 0b000, 2, 1, 0b0100000),
    ]
    model.load_program(0, program)

    model.run(2)

    assert model.read_reg(3) == 1
    assert model.read_reg(4) == 3


def test_r_type_signed_and_unsigned_comparisons():
    model = RV32IMModel()
    model.write_reg(1, 0xFFFFFFFF)
    model.write_reg(2, 1)
    program = [
        encode_r_type(OPCODE_OP, 3, 0b010, 1, 2, FUNCT7_BASE),
        encode_r_type(OPCODE_OP, 4, 0b011, 1, 2, FUNCT7_BASE),
    ]
    model.load_program(0, program)

    model.run(2)

    assert model.read_reg(3) == 1
    assert model.read_reg(4) == 0


def test_r_type_logic_operations():
    model = RV32IMModel()
    model.write_reg(1, 0xF0F00000)
    model.write_reg(2, 0x0FF00FF0)
    program = [
        encode_r_type(OPCODE_OP, 3, 0b100, 1, 2, FUNCT7_BASE),
        encode_r_type(OPCODE_OP, 4, 0b110, 1, 2, FUNCT7_BASE),
        encode_r_type(OPCODE_OP, 5, 0b111, 1, 2, FUNCT7_BASE),
    ]
    model.load_program(0, program)

    model.run(3)

    assert model.read_reg(3) == 0xFF000FF0
    assert model.read_reg(4) == 0xFFF00FF0
    assert model.read_reg(5) == 0x00F00000


def test_r_type_shift_operations_use_low_five_bits():
    model = RV32IMModel()
    model.write_reg(1, 0x80000000)
    model.write_reg(2, 33)
    program = [
        encode_r_type(OPCODE_OP, 3, 0b001, 1, 2, FUNCT7_BASE),
        encode_r_type(OPCODE_OP, 4, 0b101, 1, 2, FUNCT7_BASE),
        encode_r_type(OPCODE_OP, 5, 0b101, 1, 2, 0b0100000),
    ]
    model.load_program(0, program)

    model.run(3)

    assert model.read_reg(3) == 0
    assert model.read_reg(4) == 0x40000000
    assert model.read_reg(5) == 0xC0000000


def test_lui_writes_upper_immediate():
    model = RV32IMModel()
    model.load_program(0, [encode_u_type(OPCODE_LUI, 1, 0x12345000)])

    trace = model.step()

    assert model.read_reg(1) == 0x12345000
    assert trace.rd == 1
    assert trace.rd_value == 0x12345000


def test_auipc_adds_immediate_to_current_pc():
    model = RV32IMModel()
    model.load_program(0x80000000, [encode_u_type(OPCODE_AUIPC, 1, 0x12345000)])

    trace = model.step()

    assert model.read_reg(1) == 0x92345000
    assert trace.pc == 0x80000000
    assert trace.rd_value == 0x92345000
    assert trace.next_pc == 0x80000004


def test_auipc_wraps_to_32_bits():
    model = RV32IMModel()
    model.load_program(0xFFFFF000, [encode_u_type(OPCODE_AUIPC, 1, 0x2000)])

    model.step()

    assert model.read_reg(1) == 0x1000


def test_jal_writes_link_and_updates_pc():
    model = RV32IMModel()
    model.load_program(0x80000000, [encode_j_type(OPCODE_JAL, 1, 16)])

    trace = model.step()

    assert model.read_reg(1) == 0x80000004
    assert model.pc == 0x80000010
    assert trace.rd == 1
    assert trace.rd_value == 0x80000004
    assert trace.next_pc == 0x80000010


def test_jal_supports_negative_offset():
    model = RV32IMModel()
    model.load_program(0x80000010, [encode_j_type(OPCODE_JAL, 1, -16)])

    model.step()

    assert model.read_reg(1) == 0x80000014
    assert model.pc == 0x80000000


def test_jalr_writes_link_and_clears_target_bit_zero():
    model = RV32IMModel()
    model.write_reg(2, 0x80000003)
    model.load_program(0x1000, [encode_i_type(OPCODE_JALR, 1, 0b000, 2, 4)])

    trace = model.step()

    assert model.read_reg(1) == 0x1004
    assert model.pc == 0x80000006
    assert trace.rd == 1
    assert trace.rd_value == 0x1004
    assert trace.next_pc == 0x80000006


def test_jal_to_x0_discards_link_but_updates_pc():
    model = RV32IMModel()
    model.load_program(0x2000, [encode_j_type(OPCODE_JAL, 0, 8)])

    trace = model.step()

    assert model.read_reg(0) == 0
    assert model.pc == 0x2008
    assert trace.rd == 0
    assert trace.rd_value == 0x2004


def test_beq_taken_updates_pc_without_register_write():
    model = RV32IMModel()
    model.write_reg(1, 7)
    model.write_reg(2, 7)
    model.load_program(0x1000, [encode_b_type(OPCODE_BRANCH, 0b000, 1, 2, 12)])

    trace = model.step()

    assert model.pc == 0x100C
    assert trace.rd is None
    assert trace.rd_value is None
    assert trace.next_pc == 0x100C


def test_beq_not_taken_advances_by_four():
    model = RV32IMModel()
    model.write_reg(1, 7)
    model.write_reg(2, 8)
    model.load_program(0x1000, [encode_b_type(OPCODE_BRANCH, 0b000, 1, 2, 12)])

    trace = model.step()

    assert model.pc == 0x1004
    assert trace.next_pc == 0x1004


def test_bne_taken_with_negative_offset():
    model = RV32IMModel()
    model.write_reg(1, 7)
    model.write_reg(2, 8)
    model.load_program(0x1010, [encode_b_type(OPCODE_BRANCH, 0b001, 1, 2, -16)])

    model.step()

    assert model.pc == 0x1000


def test_signed_branches_use_signed_comparison():
    blt_model = RV32IMModel()
    blt_model.write_reg(1, 0xFFFFFFFF)
    blt_model.write_reg(2, 1)
    blt_model.load_program(0, [encode_b_type(OPCODE_BRANCH, 0b100, 1, 2, 8)])

    bge_model = RV32IMModel()
    bge_model.write_reg(1, 0xFFFFFFFF)
    bge_model.write_reg(2, 1)
    bge_model.load_program(0, [encode_b_type(OPCODE_BRANCH, 0b101, 1, 2, 8)])

    assert blt_model.step().next_pc == 8
    assert bge_model.step().next_pc == 4


def test_unsigned_branches_use_unsigned_comparison():
    bltu_model = RV32IMModel()
    bltu_model.write_reg(1, 0xFFFFFFFF)
    bltu_model.write_reg(2, 1)
    bltu_model.load_program(0, [encode_b_type(OPCODE_BRANCH, 0b110, 1, 2, 8)])

    bgeu_model = RV32IMModel()
    bgeu_model.write_reg(1, 0xFFFFFFFF)
    bgeu_model.write_reg(2, 1)
    bgeu_model.load_program(0, [encode_b_type(OPCODE_BRANCH, 0b111, 1, 2, 8)])

    assert bltu_model.step().next_pc == 4
    assert bgeu_model.step().next_pc == 8


def test_load_byte_and_halfword_sign_extend():
    model = RV32IMModel()
    model.write_reg(1, 0x1000)
    model.memory.store_u8(0x1004, 0x80)
    model.memory.store_u16(0x1008, 0x8001)
    program = [
        encode_i_type(OPCODE_LOAD, 2, 0b000, 1, 4),
        encode_i_type(OPCODE_LOAD, 3, 0b001, 1, 8),
    ]
    model.load_program(0, program)

    first = model.step()
    second = model.step()

    assert model.read_reg(2) == 0xFFFFFF80
    assert model.read_reg(3) == 0xFFFF8001
    assert first.memory_address == 0x1004
    assert first.memory_value == 0xFFFFFF80
    assert second.memory_address == 0x1008
    assert second.memory_value == 0xFFFF8001


def test_load_byte_and_halfword_unsigned_zero_extend():
    model = RV32IMModel()
    model.write_reg(1, 0x1000)
    model.memory.store_u8(0x1004, 0x80)
    model.memory.store_u16(0x1008, 0x8001)
    program = [
        encode_i_type(OPCODE_LOAD, 2, 0b100, 1, 4),
        encode_i_type(OPCODE_LOAD, 3, 0b101, 1, 8),
    ]
    model.load_program(0, program)

    model.run(2)

    assert model.read_reg(2) == 0x80
    assert model.read_reg(3) == 0x8001


def test_load_word_little_endian():
    model = RV32IMModel()
    model.write_reg(1, 0x1000)
    model.memory.store_u8(0x1000, 0x78)
    model.memory.store_u8(0x1001, 0x56)
    model.memory.store_u8(0x1002, 0x34)
    model.memory.store_u8(0x1003, 0x12)
    model.load_program(0, [encode_i_type(OPCODE_LOAD, 2, 0b010, 1, 0)])

    trace = model.step()

    assert model.read_reg(2) == 0x12345678
    assert trace.rd == 2
    assert trace.rd_value == 0x12345678
    assert trace.memory_address == 0x1000
    assert trace.memory_value == 0x12345678


def test_store_byte_halfword_and_word_little_endian():
    model = RV32IMModel()
    model.write_reg(1, 0x1000)
    model.write_reg(2, 0x12345678)
    program = [
        encode_s_type(OPCODE_STORE, 0b000, 1, 2, 0),
        encode_s_type(OPCODE_STORE, 0b001, 1, 2, 4),
        encode_s_type(OPCODE_STORE, 0b010, 1, 2, 8),
    ]
    model.load_program(0, program)

    first = model.step()
    second = model.step()
    third = model.step()

    assert model.memory.load_u8(0x1000) == 0x78
    assert model.memory.load_u16(0x1004) == 0x5678
    assert model.memory.load_u32(0x1008) == 0x12345678
    assert first.memory_address == 0x1000
    assert first.memory_value == 0x78
    assert second.memory_address == 0x1004
    assert second.memory_value == 0x5678
    assert third.memory_address == 0x1008
    assert third.memory_value == 0x12345678
    assert first.rd is None
    assert first.rd_value is None


def test_load_store_effective_address_wraps_to_32_bits():
    model = RV32IMModel()
    model.write_reg(1, 0xFFFFFFFF)
    model.write_reg(2, 0xAA)
    program = [
        encode_s_type(OPCODE_STORE, 0b000, 1, 2, 1),
        encode_i_type(OPCODE_LOAD, 3, 0b100, 0, 0),
    ]
    model.load_program(0x100, program)

    model.run(2)

    assert model.memory.load_u8(0) == 0xAA
    assert model.read_reg(3) == 0xAA


def test_m_extension_multiply_low_and_high_results():
    model = RV32IMModel()
    model.write_reg(1, 0xFFFFFFFE)
    model.write_reg(2, 3)
    model.write_reg(3, 0xFFFFFFFF)
    program = [
        encode_r_type(OPCODE_OP, 4, 0b000, 1, 2, FUNCT7_MULDIV),
        encode_r_type(OPCODE_OP, 5, 0b001, 1, 2, FUNCT7_MULDIV),
        encode_r_type(OPCODE_OP, 6, 0b010, 1, 2, FUNCT7_MULDIV),
        encode_r_type(OPCODE_OP, 7, 0b011, 3, 2, FUNCT7_MULDIV),
    ]
    model.load_program(0, program)

    model.run(4)

    assert model.read_reg(4) == 0xFFFFFFFA
    assert model.read_reg(5) == 0xFFFFFFFF
    assert model.read_reg(6) == 0xFFFFFFFF
    assert model.read_reg(7) == 0x00000002


def test_m_extension_signed_division_and_remainder_truncate_toward_zero():
    model = RV32IMModel()
    model.write_reg(1, 0xFFFFFFF9)
    model.write_reg(2, 3)
    program = [
        encode_r_type(OPCODE_OP, 3, 0b100, 1, 2, FUNCT7_MULDIV),
        encode_r_type(OPCODE_OP, 4, 0b110, 1, 2, FUNCT7_MULDIV),
    ]
    model.load_program(0, program)

    model.run(2)

    assert model.read_reg(3) == 0xFFFFFFFE
    assert model.read_reg(4) == 0xFFFFFFFF


def test_m_extension_unsigned_division_and_remainder():
    model = RV32IMModel()
    model.write_reg(1, 0xFFFFFFFF)
    model.write_reg(2, 2)
    program = [
        encode_r_type(OPCODE_OP, 3, 0b101, 1, 2, FUNCT7_MULDIV),
        encode_r_type(OPCODE_OP, 4, 0b111, 1, 2, FUNCT7_MULDIV),
    ]
    model.load_program(0, program)

    model.run(2)

    assert model.read_reg(3) == 0x7FFFFFFF
    assert model.read_reg(4) == 1


def test_m_extension_division_by_zero_results():
    model = RV32IMModel()
    model.write_reg(1, 0x12345678)
    model.write_reg(2, 0)
    program = [
        encode_r_type(OPCODE_OP, 3, 0b100, 1, 2, FUNCT7_MULDIV),
        encode_r_type(OPCODE_OP, 4, 0b101, 1, 2, FUNCT7_MULDIV),
        encode_r_type(OPCODE_OP, 5, 0b110, 1, 2, FUNCT7_MULDIV),
        encode_r_type(OPCODE_OP, 6, 0b111, 1, 2, FUNCT7_MULDIV),
    ]
    model.load_program(0, program)

    model.run(4)

    assert model.read_reg(3) == 0xFFFFFFFF
    assert model.read_reg(4) == 0xFFFFFFFF
    assert model.read_reg(5) == 0x12345678
    assert model.read_reg(6) == 0x12345678


def test_m_extension_int_min_divide_by_minus_one_results():
    model = RV32IMModel()
    model.write_reg(1, 0x80000000)
    model.write_reg(2, 0xFFFFFFFF)
    program = [
        encode_r_type(OPCODE_OP, 3, 0b100, 1, 2, FUNCT7_MULDIV),
        encode_r_type(OPCODE_OP, 4, 0b110, 1, 2, FUNCT7_MULDIV),
    ]
    model.load_program(0, program)

    model.run(2)

    assert model.read_reg(3) == 0x80000000
    assert model.read_reg(4) == 0


def test_nop_keeps_x0_zero_and_advances_pc():
    model = RV32IMModel()
    model.write_reg(0, 123)
    model.load_program(0x1000, [encode_i_type(OPCODE_OP_IMM, 0, 0b000, 0, 0)])

    trace = model.step()

    assert model.read_reg(0) == 0
    assert model.pc == 0x1004
    assert trace.rd == 0
    assert trace.rd_value == 0


def test_run_returns_ordered_traces():
    model = RV32IMModel()
    program = [
        encode_i_type(OPCODE_OP_IMM, 1, 0b000, 0, 1),
        encode_i_type(OPCODE_OP_IMM, 2, 0b000, 1, 2),
    ]
    model.load_program(0x2000, program)

    traces = model.run(2)

    assert [trace.sequence for trace in traces] == [0, 1]
    assert [trace.pc for trace in traces] == [0x2000, 0x2004]
    assert [trace.next_pc for trace in traces] == [0x2004, 0x2008]
    assert model.read_reg(2) == 3


def test_illegal_instruction_raises():
    model = RV32IMModel()
    model.load_program(0, [0x00000000])

    with pytest.raises(IllegalInstruction):
        model.step()


def test_register_index_must_be_valid():
    model = RV32IMModel()
    with pytest.raises(ValueError):
        model.read_reg(32)
    with pytest.raises(ValueError):
        model.write_reg(-1, 0)
