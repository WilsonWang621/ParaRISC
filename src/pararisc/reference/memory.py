"""Byte-addressed little-endian memory for the reference model."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ByteMemory:
    """Sparse byte-addressed memory."""

    data: dict[int, int] = field(default_factory=dict)

    def load_u8(self, address: int) -> int:
        self._check_address(address)
        return self.data.get(address, 0)

    def load_u16(self, address: int) -> int:
        self._check_address(address)
        return self.load_u8(address) | (self.load_u8(address + 1) << 8)

    def load_u32(self, address: int) -> int:
        self._check_address(address)
        return (
            self.load_u8(address)
            | (self.load_u8(address + 1) << 8)
            | (self.load_u8(address + 2) << 16)
            | (self.load_u8(address + 3) << 24)
        )

    def store_u8(self, address: int, value: int) -> None:
        self._check_address(address)
        self.data[address] = value & 0xFF

    def store_u16(self, address: int, value: int) -> None:
        self._check_address(address)
        self.store_u8(address, value)
        self.store_u8(address + 1, value >> 8)

    def store_u32(self, address: int, value: int) -> None:
        self._check_address(address)
        self.store_u8(address, value)
        self.store_u8(address + 1, value >> 8)
        self.store_u8(address + 2, value >> 16)
        self.store_u8(address + 3, value >> 24)

    def load_program(self, base_address: int, instructions: list[int]) -> None:
        for index, instruction in enumerate(instructions):
            self.store_u32(base_address + index * 4, instruction)

    @staticmethod
    def _check_address(address: int) -> None:
        if not 0 <= address <= 0xFFFFFFFF:
            raise ValueError(f"address outside RV32 range: {address:#x}")
