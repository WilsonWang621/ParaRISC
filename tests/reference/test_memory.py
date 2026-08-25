import pytest

from src.pararisc.reference.memory import ByteMemory


def test_unwritten_memory_reads_as_zero():
    memory = ByteMemory()
    assert memory.load_u8(0x1000) == 0
    assert memory.load_u16(0x1000) == 0
    assert memory.load_u32(0x1000) == 0


def test_store_and_load_u32_little_endian():
    memory = ByteMemory()
    memory.store_u32(0x1000, 0x12345678)
    assert memory.load_u8(0x1000) == 0x78
    assert memory.load_u8(0x1001) == 0x56
    assert memory.load_u8(0x1002) == 0x34
    assert memory.load_u8(0x1003) == 0x12
    assert memory.load_u16(0x1000) == 0x5678
    assert memory.load_u32(0x1000) == 0x12345678


def test_partial_store_overwrites_only_target_bytes():
    memory = ByteMemory()
    memory.store_u32(0x1000, 0x12345678)
    memory.store_u16(0x1002, 0xABCD)
    memory.store_u8(0x1000, 0xEF)
    assert memory.load_u32(0x1000) == 0xABCD56EF


def test_store_masks_value_width():
    memory = ByteMemory()
    memory.store_u8(0x1000, 0x1FF)
    memory.store_u16(0x1002, 0x1FFFF)
    assert memory.load_u8(0x1000) == 0xFF
    assert memory.load_u16(0x1002) == 0xFFFF


def test_load_program_writes_instruction_words():
    memory = ByteMemory()
    memory.load_program(0x80000000, [0x00000013, 0x00100093])
    assert memory.load_u32(0x80000000) == 0x00000013
    assert memory.load_u32(0x80000004) == 0x00100093


def test_address_must_be_in_rv32_range():
    memory = ByteMemory()
    with pytest.raises(ValueError):
        memory.load_u8(-1)
    with pytest.raises(ValueError):
        memory.store_u8(0x1_0000_0000, 0)
