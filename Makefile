PYTHON ?= python

.PHONY: smoke test-unit test-isa test-reference test-all

smoke:
	PYTHON=$(PYTHON) scripts/check.sh

test-unit:
	@echo "test-unit: no unit tests yet"

test-isa:
	$(PYTHON) -m pytest tests/isa

test-reference:
	$(PYTHON) -m pytest tests/reference

test-all: smoke test-unit test-isa test-reference
