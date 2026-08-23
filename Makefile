PYTHON ?= python

.PHONY: smoke test-unit test-isa test-reference test-all

smoke:
	PYTHON=$(PYTHON) scripts/check.sh

test-unit:
	@echo "test-unit: no unit tests yet"

test-isa:
	@echo "test-isa: no ISA tests yet"

test-reference:
	@echo "test-reference: no reference tests yet"

test-all: smoke test-unit test-isa test-reference
