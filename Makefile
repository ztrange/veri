# veri — developer tasks.
#
# `make test` runs every shell unit-test suite that ships with the solve-issue skill.
# This is also the command veri's own conductor detects in preflight ("Makefile with a
# test target → make test"), so veri can be run against its own repository: the suite is
# green when this target exits 0.

.PHONY: test
TESTS := $(sort $(wildcard .claude/skills/solve-issue/scripts/tests/*.test.sh))

test:
	@fail=0; \
	for t in $(TESTS); do \
	  printf '== %s\n' "$$(basename $$t)"; \
	  "$$t" || fail=1; \
	done; \
	echo "----"; \
	if [ $$fail -eq 0 ]; then echo "all suites green"; else echo "SUITES FAILED"; exit 1; fi

# docs/walkthrough.html is GENERATED from the real scripts by docs/build-walkthrough.py,
# so the source it shows cannot drift. `make docs` regenerates it; `make docs-check`
# regenerates into a buffer and diffs against the committed file, which fails both when a
# script has moved on without its commentary and when the page was hand-edited.
#
# Neither is part of `test` on purpose: veri bails on a red baseline (SKILL.md preflight
# 0.3), so prose lagging behind code must not block a TDD cycle on this repo.
# `docs-check` answers one question — is the docs pipeline sound and current? — in two
# phases: the guards still fire (docs/tests/build-guards.test.sh breaks the build on
# purpose and asserts it refuses), then the committed page still matches a fresh build.
# A guard nobody has watched fail is decoration, which is why the tests run first.
.PHONY: docs docs-check docs-test
docs:
	@python3 docs/build-walkthrough.py

docs-test:
	@docs/tests/build-guards.test.sh

docs-check: docs-test
	@python3 docs/check-walkthrough.py
