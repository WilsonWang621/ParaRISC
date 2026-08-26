"""Architectural commit trace records for the reference model."""

from __future__ import annotations

from dataclasses import dataclass
import json


@dataclass(frozen=True)
class CommitTrace:
    """One architecturally committed instruction."""

    sequence: int
    pc: int
    instruction: int
    rd: int | None
    rd_value: int | None
    memory_address: int | None
    memory_value: int | None
    next_pc: int

    def to_dict(self) -> dict[str, int | None]:
        return {
            "sequence": self.sequence,
            "pc": self.pc,
            "instruction": self.instruction,
            "rd": self.rd,
            "rd_value": self.rd_value,
            "memory_address": self.memory_address,
            "memory_value": self.memory_value,
            "next_pc": self.next_pc,
        }

    @classmethod
    def from_dict(cls, data: dict[str, int | None]) -> "CommitTrace":
        return cls(
            sequence=_require_int(data, "sequence"),
            pc=_require_int(data, "pc"),
            instruction=_require_int(data, "instruction"),
            rd=_optional_int(data, "rd"),
            rd_value=_optional_int(data, "rd_value"),
            memory_address=_optional_int(data, "memory_address"),
            memory_value=_optional_int(data, "memory_value"),
            next_pc=_require_int(data, "next_pc"),
        )


@dataclass(frozen=True)
class TraceMismatch:
    """First difference between two commit traces."""

    index: int
    expected: CommitTrace | None
    actual: CommitTrace | None
    field: str


TRACE_FIELDS = (
    "sequence",
    "pc",
    "instruction",
    "rd",
    "rd_value",
    "memory_address",
    "memory_value",
    "next_pc",
)


def trace_to_jsonl(traces: list[CommitTrace]) -> str:
    """Serialize traces as deterministic JSON Lines."""

    lines = [json.dumps(trace.to_dict(), sort_keys=True, separators=(",", ":")) for trace in traces]
    return "\n".join(lines) + ("\n" if lines else "")


def trace_from_jsonl(text: str) -> list[CommitTrace]:
    """Parse traces serialized by trace_to_jsonl."""

    traces = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            data = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid trace JSON on line {line_number}") from exc
        if not isinstance(data, dict):
            raise ValueError(f"trace line {line_number} is not a JSON object")
        traces.append(CommitTrace.from_dict(data))
    return traces


def compare_traces(expected: list[CommitTrace], actual: list[CommitTrace]) -> TraceMismatch | None:
    """Return the first mismatch, or None when traces match exactly."""

    common_len = min(len(expected), len(actual))
    for index in range(common_len):
        lhs = expected[index]
        rhs = actual[index]
        for field in TRACE_FIELDS:
            if getattr(lhs, field) != getattr(rhs, field):
                return TraceMismatch(index=index, expected=lhs, actual=rhs, field=field)

    if len(expected) != len(actual):
        index = common_len
        return TraceMismatch(
            index=index,
            expected=expected[index] if index < len(expected) else None,
            actual=actual[index] if index < len(actual) else None,
            field="length",
        )

    return None


def _require_int(data: dict[str, int | None], key: str) -> int:
    value = data.get(key)
    if not isinstance(value, int):
        raise ValueError(f"trace field {key} must be an integer")
    return value


def _optional_int(data: dict[str, int | None], key: str) -> int | None:
    value = data.get(key)
    if value is None or isinstance(value, int):
        return value
    raise ValueError(f"trace field {key} must be an integer or null")
