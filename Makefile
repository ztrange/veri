# veri — developer tasks.
#
# `make test` runs every shell unit-test suite that ships with the solve-issue skill.
# This is also the command veri's own conductor detects in preflight ("Makefile with a
# test target → make test"), so veri can be run against its own repository: the suite is
# green when this target exits 0.

.PHONY: test
TESTS := $(sort $(wildcard skills/tdd/scripts/tests/*.test.sh))

# The line every suite under that glob prints last, as an ERE — the "count line" the
# recipe's failure message names and CLAUDE.md's testing idiom requires, defined here
# rather than inline so the term has one place to point at. `$$` is make's escape for a
# literal `$`, so grep is handed an end-of-line anchor.
COUNT_LINE := ^[0-9]+ passed, [0-9]+ failed$$

# A suite's exit code alone is not trusted (#157). Every suite here declares `set -u`, and
# under it a word rather than a number inside `[[ … -le … ]]` is read as a variable name; an
# unset name kills the script, and a script killed that way exits with the status of the
# command before the comparison rather than a failure — routinely 0. build-guards.test.sh
# ran 37 of its 54 cases that way until commit c4a6bdb, and no output said so. So the runner
# also asks each suite for the `<n> passed, <m> failed` line it prints last: output that
# does not end in it means the suite stopped asserting, whatever it exited with. The check
# lives here, once, so a suite added under the glob above is covered by existing.
#
# `tee` rather than a plain capture so a 70 s suite's lines still appear while it runs; the
# file it leaves behind is read only once the suite is done. The suite's own exit status
# travels in a second file because a pipeline's status is its last command's — tee's — and
# PIPESTATUS is bash's, not the /bin/sh make runs recipes with.
test:
	@fail=0; suite_out="$$(mktemp)"; suite_status="$$(mktemp)"; \
	trap 'rm -f "$$suite_out" "$$suite_status"' EXIT; \
	for t in $(TESTS); do \
	  suite_name="$$(basename "$$t")"; \
	  printf '== %s\n' "$$suite_name"; \
	  { "$$t"; echo $$? > "$$suite_status"; } 2>&1 | tee "$$suite_out"; \
	  [ "$$(cat "$$suite_status")" -eq 0 ] || fail=1; \
	  tail -n 1 "$$suite_out" | grep -Eq '$(COUNT_LINE)' || { \
	    printf '%s: never reached its count line\n' "$$suite_name"; fail=1; \
	  }; \
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
#
# All four refuse inside a development run (#143). The conductor hands every leaf it
# launches, and every command it runs itself, the run's test command as VERI_TEST_CMD — so
# that variable in the environment is a recipe's one way of knowing it was typed inside a run
# rather than by a human, and its *value* is what says which lane the run is in. A
# development run's bargain is three `make test` runs a step; a page build is not part of it,
# and neither is the red a stale page hands back. On 2026-09-13 the conductor solving #106
# spent ~5.5 min on `make docs` and `make docs-check` for a page nothing had asked it for,
# then paid for the same rebuild again at merge.
#
# The guard is one line, prefixed to each of the four recipes rather than written into three
# and forgotten in the fourth. It comes first in the recipe, so a refusal costs nothing: a
# guard that exits 2 after building the page has already spent what the rule exists to save.
# docs-check carries its own copy even though its prerequisites refuse before it is reached,
# because it is the target a human types and what it does is a fact of its own.
#
# It stays out of the way of everyone else, on both sides. Unset — a human, `make
# merge-gates`, CI — and the recipes run exactly as they did. Set to a `make docs…` target
# and they also run: that is a documentation issue's own run, the one run that legitimately
# builds the page, and a guard reading only the variable's presence would leave the
# documentation lane unable to run its own tests — the same door shut on the wrong side.
# So the condition is on the value, and `case` rather than a string compare because the lane
# is the whole family of targets (`docs`, `docs-test`, `docs-fresh`, `docs-check`), not one
# of them.
#
# The diagnostic names VERI_TEST_CMD and prints its value, because "refusing" on its own
# sends whoever read it to this file: the variable is both what stopped the build and the
# knob to reach for. It carries no issue number — an unescaped `#` in a variable definition
# opens a make comment and silently truncates the value at it.
DEV_RUN_GUARD := case "$${VERI_TEST_CMD:-}" in \
	  ''|'make docs'*) ;; \
	  *) printf 'refusing: VERI_TEST_CMD=%s is set, so this is a development run, and a development run never owes a page build.\n' "$${VERI_TEST_CMD}" >&2; \
	     exit 2 ;; \
	esac

.PHONY: docs docs-check docs-test docs-fresh merge-gates install-hooks
docs:
	@$(DEV_RUN_GUARD)
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

# A glob, as `test` above is: a suite under docs/tests/ runs by existing, so adding one
# never also owes a Makefile edit nobody knew was owed. It stops at the first suite that
# fails and passes that status out, which is what the target's callers — a human, a merge
# gate — read off it.
DOCS_TESTS := $(sort $(wildcard docs/tests/*.test.sh))

docs-test:
	@$(DEV_RUN_GUARD)
	@for t in $(DOCS_TESTS); do "$$t" || exit $$?; done

# The freshness half of docs-check on its own: rebuild once, compare to the committed
# page (~2 s). Split out because merge-gates owes it far more often than the guards.
docs-fresh:
	@$(DEV_RUN_GUARD)
	@python3 docs/check-walkthrough.py

docs-check: docs-test docs-fresh
	@$(DEV_RUN_GUARD)

# The docs gates left CI on 2026-09-11 (the guards made every job ~4x longer on billed
# runners), and a push hook would run them on pushes that touched nothing the page reads.
# This is the replacement: run once at merge time, in the PR's worktree on the rebased
# tip, it diffs the branch against origin/main and runs only the gates the changed files
# warrant — nothing for a README PR, nothing for a change under skills/ either since #125,
# nothing for a Makefile change either since #164 (the page goes stale by design on every
# tag and every script change, so the check on a development branch failed for what main
# did while the branch was open, whatever the recipe edit was; a recipe that breaks a docs
# target is the docs lane's to catch on its own cadence), docs-fresh alone for a hand-edited
# page, and docs-test (every suite under docs/tests/) plus docs-fresh for a change anywhere
# under docs/ except walkthrough.html itself, which is the build's output rather than one of
# its inputs (#137: the rule is the directory, not a list of its parts, so
# docs/docs-owed.sh and docs/merge-gates.sh no longer match nothing and get no gate).
# docs/merge-gates.sh has the rules and the exit codes;
# VERI_GATES=all forces both, VERI_GATES_BASE picks another base.
merge-gates:
	@docs/merge-gates.sh
