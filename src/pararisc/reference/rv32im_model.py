"""Pure Python sequential RV32IM reference model."""

from __future__ import annotations

from dataclasses import dataclass, field

from src.pararisc.isa.decoder import decode
from src.pararisc.isa.immediate import sign_extend
from src.pararisc.reference.arith import INT32_MIN, bool32, i32, shamt, trunc_div_signed, u32
from src.pararisc.reference.memory import ByteMemory
from src.pararisc.reference.trace import CommitTrace


class IllegalInstruction(Exception):
    """Raised when the reference model fetches an illegal instruction."""


class UnsupportedInstruction(Exception):
    """Raised when decode supports an instruction that execute has not implemented."""


@dataclass
class RV32IMModel:
    """Sequential architectural model with sparse byte-addressed memory."""

    pc: int = 0
    memory: ByteMemory = field(default_factory=ByteMemory)
    regs: list[int] = field(default_factory=lambda: [0] * 32)
    sequence: int = 0

    def load_program(self, base_address: int, instructions: list[int]) -> None:
        self.memory.load_program(base_address, instructions)
        self.pc = u32(base_address)

    def read_reg(self, index: int) -> int:
        self._check_register(index)
        if index == 0:
            return 0
        return self.regs[index]

    def write_reg(self, index: int, value: int) -> None:
        self._check_register(index)
        if index == 0:
            self.regs[0] = 0
            return
        self.regs[index] = u32(value)

    def fetch(self) -> int:
        return self.memory.load_u32(self.pc)

    def step(self) -> CommitTrace:
        pc_before = self.pc
        instruction = self.fetch()
        uop = decode(instruction, pc_before)

        if uop.illegal:
            raise IllegalInstruction(f"illegal instruction at {pc_before:#010x}: {instruction:#010x}")

        next_pc = u32(pc_before + 4)
        rd = None
        rd_value = None
        memory_address = None
        memory_value = None

        if uop.opcode in {"ADDI", "SLTI", "SLTIU", "XORI", "ORI", "ANDI", "SLLI", "SRLI", "SRAI"}:
            rd = uop.rd
            rd_value = self._execute_op_imm(uop.opcode, self.read_reg(uop.rs1), uop.imm)
            self.write_reg(uop.rd, rd_value)
        elif uop.opcode in {"ADD", "SUB", "SLL", "SLT", "SLTU", "XOR", "SRL", "SRA", "OR", "AND"}:
            rd = uop.rd
            rd_value = self._execute_op(uop.opcode, self.read_reg(uop.rs1), self.read_reg(uop.rs2))
            self.write_reg(uop.rd, rd_value)
        elif uop.opcode in {"LUI", "AUIPC"}:
            rd = uop.rd
            rd_value = self._execute_u_type(uop.opcode, pc_before, uop.imm)
            self.write_reg(uop.rd, rd_value)
        elif uop.opcode in {"JAL", "JALR"}:
            rd = uop.rd
            rd_value = u32(pc_before + 4)
            next_pc = self._execute_jump(uop.opcode, pc_before, self.read_reg(uop.rs1), uop.imm)
            self.write_reg(uop.rd, rd_value)
        elif uop.opcode in {"BEQ", "BNE", "BLT", "BGE", "BLTU", "BGEU"}:
            if self._branch_taken(uop.opcode, self.read_reg(uop.rs1), self.read_reg(uop.rs2)):
                next_pc = u32(pc_before + uop.imm)
        elif uop.opcode in {"LB", "LH", "LW", "LBU", "LHU"}:
            rd = uop.rd
            memory_address = u32(self.read_reg(uop.rs1) + uop.imm)
            rd_value = self._execute_load(uop.opcode, memory_address)
            memory_value = rd_value
            self.write_reg(uop.rd, rd_value)
        elif uop.opcode in {"SB", "SH", "SW"}:
            memory_address = u32(self.read_reg(uop.rs1) + uop.imm)
            memory_value = self._execute_store(uop.opcode, memory_address, self.read_reg(uop.rs2))
        elif uop.opcode in {"MUL", "MULH", "MULHSU", "MULHU", "DIV", "DIVU", "REM", "REMU"}:
            rd = uop.rd
            rd_value = self._execute_m_extension(uop.opcode, self.read_reg(uop.rs1), self.read_reg(uop.rs2))
            self.write_reg(uop.rd, rd_value)
        else:
            raise UnsupportedInstruction(f"unsupported instruction in reference model: {uop.opcode}")

        self.pc = next_pc
        self.regs[0] = 0
        trace = CommitTrace(
            sequence=self.sequence,
            pc=pc_before,
            instruction=instruction,
            rd=rd,
            rd_value=rd_value,
            memory_address=memory_address,
            memory_value=memory_value,
            next_pc=next_pc,
        )
        self.sequence += 1
        return trace

    def run(self, max_steps: int) -> list[CommitTrace]:
        traces = []
        for _ in range(max_steps):
            traces.append(self.step())
        return traces

    @staticmethod
    def _execute_op_imm(opcode: str, rs1_value: int, imm: int) -> int:
        if opcode == "ADDI":
            return u32(rs1_value + imm)
        if opcode == "SLTI":
            return bool32(i32(rs1_value) < imm)
        if opcode == "SLTIU":
            return bool32(u32(rs1_value) < u32(imm))
        if opcode == "XORI":
            return u32(rs1_value ^ imm)
        if opcode == "ORI":
            return u32(rs1_value | imm)
        if opcode == "ANDI":
            return u32(rs1_value & imm)
        if opcode == "SLLI":
            return u32(rs1_value << shamt(imm))
        if opcode == "SRLI":
            return u32(rs1_value) >> shamt(imm)
        if opcode == "SRAI":
            return u32(i32(rs1_value) >> shamt(imm))
        raise UnsupportedInstruction(f"unsupported OP-IMM instruction: {opcode}")

    @staticmethod
    def _execute_op(opcode: str, rs1_value: int, rs2_value: int) -> int:
        if opcode == "ADD":
            return u32(rs1_value + rs2_value)
        if opcode == "SUB":
            return u32(rs1_value - rs2_value)
        if opcode == "SLL":
            return u32(rs1_value << shamt(rs2_value))
        if opcode == "SLT":
            return bool32(i32(rs1_value) < i32(rs2_value))
        if opcode == "SLTU":
            return bool32(u32(rs1_value) < u32(rs2_value))
        if opcode == "XOR":
            return u32(rs1_value ^ rs2_value)
        if opcode == "SRL":
            return u32(rs1_value) >> shamt(rs2_value)
        if opcode == "SRA":
            return u32(i32(rs1_value) >> shamt(rs2_value))
        if opcode == "OR":
            return u32(rs1_value | rs2_value)
        if opcode == "AND":
            return u32(rs1_value & rs2_value)
        raise UnsupportedInstruction(f"unsupported OP instruction: {opcode}")

    @staticmethod
    def _execute_u_type(opcode: str, pc: int, imm: int) -> int:
        if opcode == "LUI":
            return u32(imm)
        if opcode == "AUIPC":
            return u32(pc + imm)
        raise UnsupportedInstruction(f"unsupported U-type instruction: {opcode}")

    @staticmethod
    def _execute_jump(opcode: str, pc: int, rs1_value: int, imm: int) -> int:
        if opcode == "JAL":
            return u32(pc + imm)
        if opcode == "JALR":
            return u32(rs1_value + imm) & ~1
        raise UnsupportedInstruction(f"unsupported jump instruction: {opcode}")

    @staticmethod
    def _branch_taken(opcode: str, rs1_value: int, rs2_value: int) -> bool:
        if opcode == "BEQ":
            return u32(rs1_value) == u32(rs2_value)
        if opcode == "BNE":
            return u32(rs1_value) != u32(rs2_value)
        if opcode == "BLT":
            return i32(rs1_value) < i32(rs2_value)
        if opcode == "BGE":
            return i32(rs1_value) >= i32(rs2_value)
        if opcode == "BLTU":
            return u32(rs1_value) < u32(rs2_value)
        if opcode == "BGEU":
            return u32(rs1_value) >= u32(rs2_value)
        raise UnsupportedInstruction(f"unsupported branch instruction: {opcode}")

    def _execute_load(self, opcode: str, address: int) -> int:
        if opcode == "LB":
            return u32(sign_extend(self.memory.load_u8(address), 8))
        if opcode == "LH":
            return u32(sign_extend(self.memory.load_u16(address), 16))
        if opcode == "LW":
            return u32(self.memory.load_u32(address))
        if opcode == "LBU":
            return self.memory.load_u8(address)
        if opcode == "LHU":
            return self.memory.load_u16(address)
        raise UnsupportedInstruction(f"unsupported load instruction: {opcode}")

    def _execute_store(self, opcode: str, address: int, value: int) -> int:
        if opcode == "SB":
            self.memory.store_u8(address, value)
            return value & 0xFF
        if opcode == "SH":
            self.memory.store_u16(address, value)
            return value & 0xFFFF
        if opcode == "SW":
            store_value = u32(value)
            self.memory.store_u32(address, store_value)
            return store_value
        raise UnsupportedInstruction(f"unsupported store instruction: {opcode}")

    @staticmethod
    def _execute_m_extension(opcode: str, rs1_value: int, rs2_value: int) -> int:
        lhs_u = u32(rs1_value)
        rhs_u = u32(rs2_value)
        lhs_s = i32(rs1_value)
        rhs_s = i32(rs2_value)

        if opcode == "MUL":
            return u32(lhs_s * rhs_s)
        if opcode == "MULH":
            return u32((lhs_s * rhs_s) >> 32)
        if opcode == "MULHSU":
            return u32((lhs_s * rhs_u) >> 32)
        if opcode == "MULHU":
            return u32((lhs_u * rhs_u) >> 32)
        if opcode == "DIV":
            if rhs_s == 0:
                return 0xFFFFFFFF
            if lhs_s == INT32_MIN and rhs_s == -1:
                return u32(INT32_MIN)
            return u32(trunc_div_signed(lhs_s, rhs_s))
        if opcode == "DIVU":
            if rhs_u == 0:
                return 0xFFFFFFFF
            return u32(lhs_u // rhs_u)
        if opcode == "REM":
            if rhs_s == 0:
                return lhs_u
            if lhs_s == INT32_MIN and rhs_s == -1:
                return 0
            quotient = trunc_div_signed(lhs_s, rhs_s)
            return u32(lhs_s - quotient * rhs_s)
        if opcode == "REMU":
            if rhs_u == 0:
                return lhs_u
            return u32(lhs_u % rhs_u)
        raise UnsupportedInstruction(f"unsupported M extension instruction: {opcode}")

    @staticmethod
    def _check_register(index: int) -> None:
        if not 0 <= index < 32:
            raise ValueError(f"register index outside RV32 range: {index}")
