.PHONY: build lint test verify check

override ROOT := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
PYTHON ?= python3

lint:
	$(ROOT)scripts/check-baseline.sh

test:
	$(PYTHON) $(ROOT)scripts/test-settings-helpers.py
	$(PYTHON) $(ROOT)scripts/test-view-helpers.py

build:
	$(PYTHON) -m py_compile $(ROOT)app/settings.py $(ROOT)home/views.py $(ROOT)scripts/test-settings-helpers.py $(ROOT)scripts/test-view-helpers.py

verify: lint test build

check: verify
