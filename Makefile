.PHONY: build lint test verify check

PYTHON ?= python3

lint:
	./scripts/check-baseline.sh

test:
	$(PYTHON) scripts/test-settings-helpers.py
	$(PYTHON) scripts/test-view-helpers.py

build:
	$(PYTHON) -m py_compile app/settings.py home/views.py scripts/test-settings-helpers.py scripts/test-view-helpers.py

verify: lint test build

check: verify
