"""RV32 immediate extraction helpers."""

from __future__ import annotations

from .encoding import bits


def sign_extend(value: int, width: int) -> int:
    """Sign-extend value interpreted as a width-bit two's-complement integer."""

    if width <= 0:
        raise ValueError("sign extension width must be positive")
    sign_bit = 1 << (width - 1)
    mask = (1 << width) - 1
    value &= mask
    return (value ^ sign_bit) - sign_bit


def imm_i(instruction: int) -> int:
    """Extract signed I-type immediate."""

    return sign_extend(bits(instruction, 31, 20), 12)


def imm_s(instruction: int) -> int:
    """Extract signed S-type immediate."""

    raw = (bits(instruction, 31, 25) << 5) | bits(instruction, 11, 7)
    return sign_extend(raw, 12)


def imm_b(instruction: int) -> int:
    """Extract signed B-type byte offset."""

    raw = (
        (bits(instruction, 31, 31) << 12)
        | (bits(instruction, 7, 7) << 11)
        | (bits(instruction, 30, 25) << 5)
        | (bits(instruction, 11, 8) << 1)
    )
    return sign_extend(raw, 13)


def imm_u(instruction: int) -> int:
    """Extract U-type immediate with low 12 bits cleared."""

    return instruction & 0xFFFFF000


def imm_j(instruction: int) -> int:
    """Extract signed J-type byte offset."""

    raw = (
        (bits(instruction, 31, 31) << 20)
        | (bits(instruction, 19, 12) << 12)
        | (bits(instruction, 20, 20) << 11)
        | (bits(instruction, 30, 21) << 1)
    )
    return sign_extend(raw, 21)
