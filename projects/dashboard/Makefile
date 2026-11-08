# Usage: make test — runs pytest over tests/; exits 1 on any non-zero pytest code.
# make itself exits 2 on a failed recipe; -q makes a still-out-of-date phony target exit 1.
rc := $(shell env -u PYTEST_PLUGINS python3 -m pytest -q tests >&2; echo $$?)
ifneq ($(rc),0)
MAKEFLAGS += -q
endif

.PHONY: test
test:
	@true
