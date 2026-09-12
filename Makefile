# veri — developer tasks.
#
# `make test` runs every shell unit-test suite that ships with the solve-issue skill.
# This is also the command veri's own conductor detects in preflight ("Makefile with a
# test target → make test"), so veri can be run against its own repository: the suite is
# green when this target exits 0.

.PHONY: test
TESTS := $(sort $(wildcard skills/tdd/scripts/tests/*.test.sh))

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
# purpose and asserts it refuses), then the committed page still matches a fresh build
# AND still agrees with the two files it describes but is not generated from (the
# phases build-verify-prompt.sh accepts, SKILL.md's revise budget).
# A guard nobody has watched fail is decoration, which is why the tests run first.
.PHONY: docs docs-check docs-test docs-fresh merge-gates install-hooks
docs:
	@python3 docs/build-walkthrough.py

# The capability index is built from `git tag`, which makes a tag the one input to
# the page that can change without a commit — so nothing rebuilds when it does, and
# docs-check goes red until someone notices. This hook is the notice. It is a git
# hook rather than a step in any skill because a tag cut by hand, by another agent,
# or in another worktree is the same problem; .git/hooks is shared by every worktree,
# so one install covers all of them.
#
# Refuses rather than clobbering a reference-transaction hook it does not recognise —
# the guardrail hooks use the same name, and silently replacing one would remove a
# protection to install a convenience.
install-hooks:
	@h="$$(git rev-parse --git-common-dir)/hooks/reference-transaction"; \
	if [ -e "$$h" ] && ! grep -q veri-docs-lag-notice "$$h"; then \
	  echo "refusing: $$h already exists and is not veri's."; \
	  echo "          Merge the two by hand, then re-run."; exit 1; \
	fi; \
	mkdir -p "$$(dirname "$$h")"; \
	cp docs/hooks/reference-transaction "$$h" && chmod 755 "$$h"; \
	echo "installed $$h"

docs-test:
	@docs/tests/build-guards.test.sh
	@docs/tests/merge-gates.test.sh

# The freshness half of docs-check on its own: rebuild once, compare to the committed
# page (~2 s). Split out because merge-gates owes it far more often than the guards.
docs-fresh:
	@python3 docs/check-walkthrough.py

docs-check: docs-test docs-fresh

# The docs gates left CI on 2026-09-11 (the guards made every job ~4x longer on billed
# runners), and a push hook would run them on pushes that touched nothing the page reads.
# This is the replacement: run once at merge time, in the PR's worktree on the rebased
# tip, it diffs the branch against origin/main and runs only the gates the changed files
# warrant — nothing for a README PR, docs-fresh for a script change, both for a change
# to the build pipeline. docs/merge-gates.sh has the rules and the exit codes;
# VERI_GATES=all forces both, VERI_GATES_BASE picks another base.
merge-gates:
	@docs/merge-gates.sh
