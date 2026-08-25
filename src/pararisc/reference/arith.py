"""RV32 integer arithmetic helpers for the reference model."""

from __future__ import annotations


MASK32 = 0xFFFFFFFF
SIGN32 = 0x80000000
INT32_MIN = -0x80000000
INT32_MAX = 0x7FFFFFFF


def u32(value: int) -> int:
    """Return value modulo 2^32."""

    return value & MASK32


def i32(value: int) -> int:
    """Interpret value as a signed 32-bit two's-complement integer."""

    value &= MASK32
    if value & SIGN32:
        return value - (1 << 32)
    return value


def shamt(value: int) -> int:
    """Extract the RV32 shift amount from a register or immediate value."""

    return value & 0x1F


def bool32(condition: bool) -> int:
    """Return a 32-bit integer boolean."""

    return 1 if condition else 0


def trunc_div_signed(dividend: int, divisor: int) -> int:
    """Signed integer division with truncation toward zero."""

    if divisor == 0:
        raise ZeroDivisionError("division by zero")
    quotient = abs(dividend) // abs(divisor)
    if (dividend < 0) != (divisor < 0):
        quotient = -quotient
    return quotient
