import pytest

from src.pararisc.reference.trace import (
    CommitTrace,
    compare_traces,
    trace_from_jsonl,
    trace_to_jsonl,
)


def test_trace_jsonl_round_trip():
    traces = [
        CommitTrace(0, 0x1000, 0x13, 1, 5, None, None, 0x1004),
        CommitTrace(1, 0x1004, 0x23, None, None, 0x2000, 0xAA, 0x1008),
    ]

    text = trace_to_jsonl(traces)

    assert trace_from_jsonl(text) == traces
    assert text.endswith("\n")


def test_empty_trace_serializes_to_empty_string():
    assert trace_to_jsonl([]) == ""
    assert trace_from_jsonl("") == []


def test_compare_traces_returns_none_for_equal_traces():
    traces = [CommitTrace(0, 0, 0x13, 1, 1, None, None, 4)]
    assert compare_traces(traces, list(traces)) is None


def test_compare_traces_reports_first_field_mismatch():
    expected = [
        CommitTrace(0, 0, 0x13, 1, 1, None, None, 4),
        CommitTrace(1, 4, 0x13, 2, 2, None, None, 8),
    ]
    actual = [
        CommitTrace(0, 0, 0x13, 1, 1, None, None, 4),
        CommitTrace(1, 4, 0x13, 2, 3, None, None, 8),
    ]

    mismatch = compare_traces(expected, actual)

    assert mismatch is not None
    assert mismatch.index == 1
    assert mismatch.field == "rd_value"
    assert mismatch.expected == expected[1]
    assert mismatch.actual == actual[1]


def test_compare_traces_reports_length_mismatch():
    expected = [CommitTrace(0, 0, 0x13, 1, 1, None, None, 4)]
    actual = []

    mismatch = compare_traces(expected, actual)

    assert mismatch is not None
    assert mismatch.index == 0
    assert mismatch.field == "length"
    assert mismatch.expected == expected[0]
    assert mismatch.actual is None


def test_trace_from_jsonl_rejects_invalid_json():
    with pytest.raises(ValueError, match="invalid trace JSON"):
        trace_from_jsonl("{")


def test_trace_from_jsonl_rejects_invalid_field_type():
    with pytest.raises(ValueError, match="sequence"):
        trace_from_jsonl('{"sequence":null,"pc":0,"instruction":19,"rd":1,"rd_value":1,"memory_address":null,"memory_value":null,"next_pc":4}\n')
