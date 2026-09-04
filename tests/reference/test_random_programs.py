import random

from src.pararisc.isa.encoding import (
    FUNCT7_BASE,
    FUNCT7_SUB_SRA,
    OPCODE_BRANCH,
    OPCODE_LOAD,
    OPCODE_OP,
    OPCODE_OP_IMM,
    OPCODE_STORE,
    encode_b_type,
    encode_i_type,
    encode_r_type,
    encode_s_type,
)
from src.pararisc.reference.rv32im_model import RV32IMModel
from src.pararisc.reference.trace import compare_traces, trace_to_jsonl


def test_seeded_random_program_is_reproducible():
    program, initial_regs, initial_memory = _generate_random_program(seed=0xC0DE, instruction_count=80)

    first_model = _make_model(program, initial_regs, initial_memory)
    second_model = _make_model(program, initial_regs, initial_memory)

    first_trace = first_model.run(len(program))
    second_trace = second_model.run(len(program))

    assert compare_traces(first_trace, second_trace) is None
    assert trace_to_jsonl(first_trace) == trace_to_jsonl(second_trace)
    assert first_model.regs == second_model.regs
    assert first_model.memory.data == second_model.memory.data


def test_seeded_random_program_covers_expected_instruction_classes():
    program, initial_regs, initial_memory = _generate_random_program(seed=0x1234, instruction_count=120)
    model = _make_model(program, initial_regs, initial_memory)

    traces = model.run(len(program))

    assert len(traces) == len(program)
    assert _count_memory_traces(traces) > 0
    assert _count_register_traces(traces) > 0
    assert any(trace.rd is None and trace.memory_address is None for trace in traces)


def _generate_random_program(seed: int, instruction_count: int) -> tuple[list[int], dict[int, int], dict[int, int]]:
    rng = random.Random(seed)
    program = []

    initial_regs = {index: rng.getrandbits(32) for index in range(1, 16)}
    initial_regs[20] = 0x1000

    initial_memory = {}
    for offset in range(0, 128, 4):
        value = rng.getrandbits(32)
        for byte_index in range(4):
            initial_memory[0x1000 + offset + byte_index] = (value >> (byte_index * 8)) & 0xFF

    generators = [
        _random_op_imm,
        _random_op,
        _random_branch,
        _random_load,
        _random_store,
    ]
    for _ in range(instruction_count):
        program.append(rng.choice(generators)(rng))

    return program, initial_regs, initial_memory


def _random_op_imm(rng: random.Random) -> int:
    funct3 = rng.choice([0b000, 0b010, 0b011, 0b100, 0b110, 0b111])
    return encode_i_type(OPCODE_OP_IMM, rng.randrange(1, 16), funct3, rng.randrange(1, 16), rng.randrange(-2048, 2048))


def _random_op(rng: random.Random) -> int:
    funct3, funct7 = rng.choice(
        [
            (0b000, FUNCT7_BASE),
            (0b000, FUNCT7_SUB_SRA),
            (0b001, FUNCT7_BASE),
            (0b010, FUNCT7_BASE),
            (0b011, FUNCT7_BASE),
            (0b100, FUNCT7_BASE),
            (0b101, FUNCT7_BASE),
            (0b101, FUNCT7_SUB_SRA),
            (0b110, FUNCT7_BASE),
            (0b111, FUNCT7_BASE),
        ]
    )
    return encode_r_type(OPCODE_OP, rng.randrange(1, 16), funct3, rng.randrange(1, 16), rng.randrange(1, 16), funct7)


def _random_branch(rng: random.Random) -> int:
    funct3 = rng.choice([0b000, 0b001, 0b100, 0b101, 0b110, 0b111])
    return encode_b_type(OPCODE_BRANCH, funct3, rng.randrange(1, 16), rng.randrange(1, 16), 4)


def _random_load(rng: random.Random) -> int:
    funct3, alignment = rng.choice([(0b000, 1), (0b001, 2), (0b010, 4), (0b100, 1), (0b101, 2)])
    offset = rng.randrange(0, 96 // alignment) * alignment
    return encode_i_type(OPCODE_LOAD, rng.randrange(1, 16), funct3, 20, offset)


def _random_store(rng: random.Random) -> int:
    funct3, alignment = rng.choice([(0b000, 1), (0b001, 2), (0b010, 4)])
    offset = rng.randrange(0, 96 // alignment) * alignment
    return encode_s_type(OPCODE_STORE, funct3, 20, rng.randrange(1, 16), offset)


def _make_model(program: list[int], initial_regs: dict[int, int], initial_memory: dict[int, int]) -> RV32IMModel:
    model = RV32IMModel()
    for index, value in initial_regs.items():
        model.write_reg(index, value)
    for address, value in initial_memory.items():
        model.memory.store_u8(address, value)
    model.load_program(0x80000000, program)
    return model


def _count_memory_traces(traces) -> int:
    return sum(1 for trace in traces if trace.memory_address is not None)


def _count_register_traces(traces) -> int:
    return sum(1 for trace in traces if trace.rd is not None)
