.PHONY: build lint test verify check

ROOT := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
override PYTHON := env -u PYTHONPATH -u PYTHONHOME -u MAKEFILES -u MAKEFLAGS -u MFLAGS -u GNUMAKEFLAGS PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 python3 -I -S

lint:
	$(ROOT)scripts/check-baseline.sh

test:
	$(PYTHON) $(ROOT)scripts/test-settings-helpers.py
	$(PYTHON) $(ROOT)scripts/test-view-helpers.py
	$(PYTHON) $(ROOT)scripts/test-workflow-checkout.py

build:
	$(PYTHON) -m py_compile $(ROOT)app/settings.py $(ROOT)home/views.py $(ROOT)scripts/check-workflow-checkout.py $(ROOT)scripts/test-settings-helpers.py $(ROOT)scripts/test-view-helpers.py $(ROOT)scripts/test-workflow-checkout.py

verify: lint test build

check: verify
