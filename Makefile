.PHONY: lint test verify check

PYTHON ?= python3

lint:
	./scripts/check-baseline.sh

test:
	$(PYTHON) scripts/test-settings-helpers.py
	$(PYTHON) scripts/test-view-helpers.py

verify: lint test

check: verify
