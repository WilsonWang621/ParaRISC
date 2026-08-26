import pytest

from src.pararisc.isa.encoding import (
    FUNCT7_BASE,
    OPCODE_OP,
    OPCODE_OP_IMM,
    encode_i_type,
    encode_r_type,
)
from src.pararisc.reference.rv32im_model import (
    IllegalInstruction,
    RV32IMModel,
    UnsupportedInstruction,
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


def test_supported_decode_but_unimplemented_execute_raises():
    model = RV32IMModel()
    add = encode_r_type(OPCODE_OP, 1, 0b000, 2, 3, FUNCT7_BASE)
    model.load_program(0, [add])

    with pytest.raises(UnsupportedInstruction):
        model.step()


def test_register_index_must_be_valid():
    model = RV32IMModel()
    with pytest.raises(ValueError):
        model.read_reg(32)
    with pytest.raises(ValueError):
        model.write_reg(-1, 0)
