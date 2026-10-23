# veri — developer tasks.
#
# `make test` runs every pytest case that ships with the solve-issue skill, in one pytest
# invocation. This is also the command veri's own conductor detects in preflight ("Makefile
# with a test target → make test"), so veri can be run against its own repository: the suite is
# green when this target exits 0. `make test TESTS="<pytest file or node id> …"` runs only those:
# each entry must name a pytest file or node id, and a directory, a missing file or any entry
# selecting no suite is refused with exit 2 naming the entry, rather than run.
.PHONY: test unit
TESTS :=
UNIT_TESTS :=
TESTS_NAMED := $(filter command line,$(origin TESTS))
UNIT_TESTS_NAMED := $(filter command line,$(origin UNIT_TESTS))
rwildcard = $(foreach d,$(wildcard $(1)/*),$(call rwildcard,$(d),$(2))$(if $(filter $(2),$(notdir $(d))),$(d)))
PY_ALL := $(sort $(call rwildcard,skills/tdd/scripts/tests/py,test_%.py))
PY_UNIT := $(sort $(wildcard skills/tdd/scripts/tests/py/unit/test_*.py))
py_tests = $(if $(1),$(foreach t,$(2),$(if $(findstring .py,$(t)),$(t))),$(3))
py_refused = $(if $(1),$(foreach t,$(2),$(if $(findstring .py,$(t)),,$(t))))
unit: PY_TESTS = $(call py_tests,$(UNIT_TESTS_NAMED),$(UNIT_TESTS),$(PY_UNIT))
PY_REFUSED = $(call py_refused,$(TESTS_NAMED),$(TESTS))
PY_TESTS := $(call py_tests,$(TESTS_NAMED),$(TESTS),$(PY_ALL))
unit: PY_SELECT = -m "not process and not tree_audit"
# The fast tier's default worker count: each xdist worker pays its own start-up and collection, so
# one per core is slower than 4 on `make unit` (16.1 s against 11.4 s on the 16-core development
# Mac, #2053). `make test` keeps pytest_leg.py's own default: the cores other running legs leave
# free, at least 1, read from the registry under ~/.veri-pytest-legs (VERI_PYTEST_LEGS; #2100).
# VERI_PYTEST_WORKERS overrides both, used as given.
unit: PY_WORKERS = 4

# Every case runs offline. gh and curl are refused by the plugin pytest_leg.py loads; `git` on
# PATH is a plain symlink straight to the real binary (the recipe's git_bin directory), and
# git's own transport allowlist refuses a remote reach: protocol.allow=never with
# protocol.file.allow=always, set via GIT_CONFIG_COUNT/KEY/VALUE. A local remote — a bare path,
# or file:// — is untouched, since cases clone, fetch and push between scratch repos on disk.
#
# The proxies point at a port nothing listens on, for anything that gets past the plugin; loopback
# is exempt, because a suite that serves a page on 127.0.0.1 asks it there.
#
# Three more things are fixed for every suite rather than inherited from whoever typed `make test`
#. Each cost the development Mac time CI never paid:
#   - LC_ALL=C. macOS's BSD awk, tr, grep and sed run ~12x slower over text in a UTF-8 locale,
#     and the terminal a conductor runs in sets one: 121 s of a 440 s run, measured 2026-09-18.
#     Python still reads UTF-8 under it (PEP 538 coerces the C locale).
#   - stdin is /dev/null. A suite inherited make's, and under a leaf's backgrounded `make test`
#     that is a socket that never closes: a stub claude's `cat`
#     waited on it for 28 minutes.
#   - The real git. /usr/bin/git on macOS is xcrun's shim, ~21 ms a call on top of git's own,
#     over ~1,900 calls a run. `xcrun -f git` names the binary it forwards to; where there is
#     no xcrun (Linux, CI) the git on PATH is already the real one. A suite that runs this
#     recipe itself inherits the outer run's resolved OFFLINE_REAL_GIT rather than re-asking
#     xcrun, since xcrun's answer does not depend on PATH and a nested `command -v git` would
#     otherwise name the outer run's own symlink — harmless (a symlink to a symlink still
#     resolves to the real binary with no extra process), but pointless to redo.
OFFLINE_PROXY := http://127.0.0.1:1

# The two halves of that environment `test` and `profile` share, so a suite runs under the
# same one either way: OFFLINE_GIT resolves the real git and symlinks it into the recipe's
# $git_bin; OFFLINE_ENV is the assignments and the locale a suite is started under, and
# reads $git_bin, $real_git and $reach_log from the recipe that expands it.
OFFLINE_GIT := real_git="$${OFFLINE_REAL_GIT:-$$(xcrun -f git 2>/dev/null || command -v git)}"; \
	ln -sf "$$real_git" "$$git_bin/git"; \
	exec_path="$$("$$real_git" --exec-path)"; \
	if [ -d "$$(dirname "$$real_git")/../share/git-core/templates" ]; then \
	  export GIT_TEMPLATE_DIR="$$(dirname "$$real_git")/../share/git-core/templates"; \
	else unset GIT_TEMPLATE_DIR; fi
OFFLINE_SCRATCH := git_bin="$$(mktemp -d)"; \
	trap 'rm -rf "$$git_bin"' EXIT; \
	$(OFFLINE_GIT)
OFFLINE_ENV = PATH="$$git_bin:$$PATH" MAKEFLAGS= OFFLINE_REAL_GIT="$$real_git" GIT_EXEC_PATH="$$exec_path" \
	GIT_CONFIG_COUNT=4 GIT_CONFIG_KEY_0=http.proxy GIT_CONFIG_VALUE_0=$(OFFLINE_PROXY) \
	GIT_CONFIG_KEY_1=protocol.allow GIT_CONFIG_VALUE_1=never \
	GIT_CONFIG_KEY_2=protocol.file.allow GIT_CONFIG_VALUE_2=always \
	GIT_CONFIG_KEY_3=maintenance.auto GIT_CONFIG_VALUE_3=false \
	HTTP_PROXY=$(OFFLINE_PROXY) HTTPS_PROXY=$(OFFLINE_PROXY) NO_PROXY=127.0.0.1,localhost \
	LC_ALL=C

VENV_LIB := skills/tdd/scripts/lib/venv-python.sh
VENV_DIR := $$(bash -c '. $(VENV_LIB) && venv_dir')
VENV_PY := $$(bash -c '. $(VENV_LIB) && venv_python')

# veri needs bash 5 (since 2026-09-18), and the suites run under whatever `bash` is first on
# PATH — every one starts with `#!/usr/bin/env bash`. Nothing tests veri on bash 3.2 any more,
# the bash macOS ships in /bin, so a stale PATH must not be left to fail however a bash-4-only
# construct happens to fail inside some suite: the recipe asks that bash its major version
# before any suite runs, and refuses naming what to install. VERI_BASH_MAJOR stands in for the
# answer, because CI's runner has no older bash to ask. An
# answer that is not a number (no bash on PATH at all) is refused too, rather than compared.
BASH_GUARD := bash_major="$${VERI_BASH_MAJOR:-$$(bash -c 'echo "$${BASH_VERSINFO[0]}"' 2>/dev/null)}"; \
	case "$$bash_major" in ''|*[!0-9]*) bash_major=0 ;; esac; \
	if [ "$$bash_major" -lt 5 ]; then \
	  printf 'veri needs bash 5 or newer; the bash on PATH is version %s. Install it with `brew install bash` (it lands ahead of /bin/bash on PATH), or your package manager on Linux.\n' "$${VERI_BASH_MAJOR:-$$(bash -c 'echo "$${BASH_VERSION}"' 2>/dev/null)}" >&2; \
	  exit 2; \
	fi

MAX_MAKE_DEPTH := 4

test unit:
	@if [ "$(MAKELEVEL)" -gt $(MAX_MAKE_DEPTH) ]; then printf 'make: refusing a make %s nested at depth %s, deeper than %s\n' "$@" "$(MAKELEVEL)" "$(MAX_MAKE_DEPTH)" >&2; exit 2; fi
	@$(BASH_GUARD)
	@for e in $(PY_REFUSED); do printf 'refusing: %s selects no suite\n' "$$e" >&2; exit 2; done
	@unset BASH_ENV ENV; fail=0; git_bin="$$(mktemp -d)"; pycache="$$(mktemp -d)"; \
	trap 'rm -rf "$$git_bin" "$$pycache"' EXIT; \
	$(OFFLINE_GIT); \
	skills/tdd/scripts/prose-owed.sh . || fail=1; \
	if [ -n "$(PY_TESTS)" ]; then \
	  py_bin="$(VENV_PY)"; \
	  printf '== pytest\n'; \
	  PYTHONPYCACHEPREFIX="$$pycache" COLUMNS=200 $(OFFLINE_ENV) $(if $(PY_WORKERS),VERI_PYTEST_WORKERS="$${VERI_PYTEST_WORKERS:-$(PY_WORKERS)}") "$$py_bin" skills/tdd/scripts/veri/pytest_leg.py --timeout="$${VERI_PYTEST_TIMEOUT:-30}" $(PY_SELECT) $(PY_TESTS) < /dev/null || { leg=$$?; [ $$leg -ne 2 ] || exit 2; fail=1; }; \
	fi; \
	echo "----"; \
	if [ $$fail -eq 0 ]; then echo "all suites green"; else echo "SUITES FAILED"; exit 1; fi

.PHONY: install-dev
install-dev:
	@venv="$(VENV_DIR)"; \
	if [ ! -x "$$venv/bin/python3" ]; then \
	  builder="$$(bash -c '. $(VENV_LIB) && venv_builder')" || exit 2; \
	  "$$builder" -m venv "$$venv"; \
	else \
	  bash -c '. $(VENV_LIB) && venv_usable "$$1"' _ "$$venv" || exit 2; \
	fi; \
	"$$venv/bin/python3" -m pip install -r requirements-dev.txt && \
	printf '%s: export PATH="%s/bin:$$PATH"\n' "$$(bash -c '. $(VENV_LIB) && venv_path_advice "$$1"' _ "$$venv")" "$$venv"

# `make profile` runs the suites `test` runs, under the same offline environment, through
# profile.sh: one line per case at or above VERI_PROFILE_THRESHOLD seconds, slowest first
# (#329). A tool a human runs on demand — not part of `test`, and nothing gates on it.
.PHONY: profile
profile:
	@$(BASH_GUARD)
	@$(OFFLINE_SCRATCH); \
	if [ -n "$(PY_TESTS)" ]; then \
	  py_bin="$(VENV_PY)"; \
	  $(OFFLINE_ENV) "$$py_bin" skills/tdd/scripts/veri/pytest_leg.py -q --durations=0 --durations-min="$${VERI_PROFILE_THRESHOLD:-1}" $(PY_SELECT) $(PY_TESTS) < /dev/null | grep -E '^[0-9.]+s +call +' || true; \
	fi

# `make unreachable` lists the scripts no declared entry point reaches, through unreachable.sh.
.PHONY: unreachable
unreachable:
	@skills/tdd/scripts/unreachable.sh "$(CURDIR)"

# `make watch` reruns `make unit` when a tracked file changes (#340). A developer
# convenience — not part of `test`, `unit` or `merge-gates`, and nothing gates on it.
#
# The loop names make through WATCH_MAKE, a `:=` copy of $(MAKE), because make runs any recipe
# line that mentions $(MAKE) itself even under `make -n` — which would start the loop for real.
WATCH_MAKE := $(MAKE)
# One poll pass is `watch_snapshot` from WATCH_LIB: one `watch_stat` call per pass, whatever the
# number of tracked files.
WATCH_LIB := skills/tdd/scripts/lib/watch.sh
.PHONY: watch
watch:
	@$(BASH_GUARD)
	@interval="$${VERI_WATCH_INTERVAL:-1}"; \
	case "$$interval" in ''|*[!0-9.]*|.*|*.|*.*.*) \
	  printf 'VERI_WATCH_INTERVAL must be a number of seconds, got %s\n' "$$interval" >&2; \
	  exit 2 ;; \
	esac; \
	. ./$(WATCH_LIB); \
	seen="$$(watch_snapshot)"; \
	while :; do \
	  sleep "$$interval"; \
	  now="$$(watch_snapshot)"; \
	  [ "$$now" = "$$seen" ] && continue; \
	  seen="$$now"; \
	  $(WATCH_MAKE) --no-print-directory unit || :; \
	done

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

# `make run-finished ISSUE=<n>` says whether run <n> is safe to merge, through run-finished.sh.
.PHONY: run-finished
run-finished:
	@skills/tdd/scripts/run-finished.sh "$(ISSUE)"
