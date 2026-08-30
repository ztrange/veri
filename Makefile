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

# `make docs-check` verifies docs/walkthrough.html still matches the scripts it quotes —
# byte-for-byte listings, line counts, and in-page anchors. Kept out of `test` on purpose:
# veri bails on a red baseline, and doc drift should not block a TDD cycle.
.PHONY: docs-check
docs-check:
	@python3 docs/check-walkthrough.py
