# veri — developer tasks.
#
# `make test` runs every shell unit-test suite that ships with the solve-issue skill.
# This is also the command veri's own conductor detects in preflight ("Makefile with a
# test target → make test"), so veri can be run against its own repository: the suite is
# green when this target exits 0.

.PHONY: test unit
TESTS := $(sort $(wildcard skills/tdd/scripts/tests/*.test.sh))

# `make unit` is the fast tier (#336): only the suites under tests/unit/, through the same
# recipe as `test`, which runs them too. SUITES is set per target, so the two share one runner;
# `profile` below takes `test`'s list from the same line rather than restating it.
UNIT_TESTS := $(sort $(wildcard skills/tdd/scripts/tests/unit/*.test.sh))
test profile: SUITES = $(TESTS) $(if $(filter command line,$(origin TESTS)),,$(UNIT_TESTS))
unit: SUITES = $(UNIT_TESTS)
PY_TESTS := $(sort $(wildcard skills/tdd/scripts/tests/py/test_*.py))

# The fast tier's admission-bar guard: `unit` alone puts UNIT_GUARD_BIN first on a suite's PATH,
# where git and python3 refuse, naming themselves; gh and curl fall through to OFFLINE_BIN's shims,
# which already refuse any call, named, and log it. A unit suite mocks all four as shell functions,
# which bash finds before PATH, so only a real process call reaches a guard. `test` leaves the
# prefix empty and runs the same suites unguarded. OFFLINE_ENV below is a recursive `=`
# rather than `:=` for this reason: it must read GUARD_PATH per target, when the recipe expands it.
UNIT_GUARD_BIN := $(CURDIR)/skills/tdd/scripts/tests/unit-guard
unit: GUARD_PATH = $(UNIT_GUARD_BIN):

# The line every suite under that glob prints last, as an ERE — the "count line" the
# recipe's failure message names and CLAUDE.md's testing idiom requires, defined here
# rather than inline so the term has one place to point at. `$$` is make's escape for a
# literal `$`, so grep is handed an end-of-line anchor.
COUNT_LINE := ^[0-9]+ passed, [0-9]+ failed$$

# What a suite that never printed that line is told, as a printf format taking the suite's
# name. It is a variable for the same reason COUNT_LINE is one, and now for a second: these
# two texts are the whole of the guard's judgement — what a count line looks like, and what
# a suite lacking one is called — and they are read by two invocations, `make test` below and
# skills/tdd/scripts/run-suite.sh over a single suite. Written out in both, they would be two
# guards that agree only until someone tightens the pattern or rewords the refusal in one of
# them, and a leaf's verdict on a partially-dead suite would then depend on how it happened to
# invoke it (#418). So they are declared here, once, and the runner asks make for them through
# the `count-line-guard` target below rather than restating them.
COUNTLESS := %s: never reached its count line\n

# count-line-guard — print those two definitions as shell assignments, for run-suite.sh to
# eval. make is asked rather than the Makefile read, because the value of a make variable is
# make's to say: `$$` above is an escape, and a reader parsing the line out with sed would have
# to re-implement that and every other expansion to arrive at the string grep is actually
# handed. Nothing in the repository's own test or docs lanes depends on this target; it exists
# so the guard has one home.
.PHONY: count-line-guard
count-line-guard:
	@printf "COUNT_LINE='%s'\nCOUNTLESS='%s'\n" '$(COUNT_LINE)' '$(COUNTLESS)'

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
# PIPESTATUS is bash's, not the /bin/sh make runs recipes with. Only the suite's stdout goes
# through tee into that file; its stderr goes straight to the recipe's own (fd 3), so a line a
# dying writer prints there after the count line — GNU tail's `error writing 'standard output':
# Broken pipe`, on Linux CI under a suite that passed 13 of 13 (#526) — can never become the
# last line the count-line check reads. A suite prints its count line on stdout.
#
# Every suite also runs offline (#301), in this same run rather than a second one. gh and curl are
# not the hot path — a run makes a handful of calls to each, against ~1,900 git calls — so they
# still go through bash shims in OFFLINE_BIN that refuse any call and write it to a reach log the
# recipe empties before every suite; a suite whose log is not empty afterwards fails, one line per
# attempt naming the suite and what it tried. git does not go through a shim any more (measured
# 2026-09-18: that wrapper cost ~26 ms/call against ~8 ms for the real binary, and was 1,820 of a
# run's 4,834 bash starts). Instead, `git` on every suite's PATH is a plain symlink straight to the
# real binary (the recipe's git_bin directory — a symlink costs no bash start at all, unlike a wrapper script), and
# what used to be the shim's job — refusing a remote reach — is now git's own transport allowlist:
# protocol.allow=never with protocol.file.allow=always, set the same way the recipe already sets
# http.proxy, via GIT_CONFIG_COUNT/KEY/VALUE. That refuses every non-file transport (https, ssh,
# git://, and the scp-style user@host:path git treats as ssh) and leaves a local remote — a bare
# path, or file:// — untouched, since suites here clone, fetch and push between scratch repos on
# disk. The trade-off, accepted: a suite whose git reach is refused is no longer named on a "tried
# the network: …" line the way a gh or curl reach still is — the failure is git's own "transport …
# not allowed", on stderr, wherever the suite sends it. count-line-guard.test.sh pins both halves.
#
# The proxies point at a port nothing listens on, for anything that gets past the shims; loopback
# is exempt, because a suite that serves a page on 127.0.0.1 (dashboard.test.sh) asks it there.
#
# Three more things are fixed for every suite rather than inherited from whoever typed `make test`
# (make-test-env.test.sh pins all three). Each cost the development Mac time CI never paid:
#   - LC_ALL=C. macOS's BSD awk, tr, grep and sed run ~12x slower over text in a UTF-8 locale,
#     and the terminal a conductor runs in sets one: 121 s of a 440 s run, measured 2026-09-18.
#     Python still reads UTF-8 under it (PEP 538 coerces the C locale).
#   - stdin is /dev/null. A suite inherited make's, and under a leaf's backgrounded `make test`
#     that is a socket that never closes: the stub claude's `cat` in run-conductor.test.sh
#     waited on it for 28 minutes.
#   - The real git. /usr/bin/git on macOS is xcrun's shim, ~21 ms a call on top of git's own,
#     over ~1,900 calls a run. `xcrun -f git` names the binary it forwards to; where there is
#     no xcrun (Linux, CI) the git on PATH is already the real one. A suite that runs this
#     recipe itself inherits the outer run's resolved OFFLINE_REAL_GIT rather than re-asking
#     xcrun, since xcrun's answer does not depend on PATH and a nested `command -v git` would
#     otherwise name the outer run's own symlink — harmless (a symlink to a symlink still
#     resolves to the real binary with no extra process), but pointless to redo.
OFFLINE_BIN := $(CURDIR)/skills/tdd/scripts/tests/offline
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
OFFLINE_ENV = PATH="$(GUARD_PATH)$$git_bin:$(OFFLINE_BIN):$$PATH" OFFLINE_REAL_GIT="$$real_git" GIT_EXEC_PATH="$$exec_path" OFFLINE_REACH_LOG="$$reach_log" \
	GIT_CONFIG_COUNT=3 GIT_CONFIG_KEY_0=http.proxy GIT_CONFIG_VALUE_0=$(OFFLINE_PROXY) \
	GIT_CONFIG_KEY_1=protocol.allow GIT_CONFIG_VALUE_1=never \
	GIT_CONFIG_KEY_2=protocol.file.allow GIT_CONFIG_VALUE_2=always \
	HTTP_PROXY=$(OFFLINE_PROXY) HTTPS_PROXY=$(OFFLINE_PROXY) NO_PROXY=127.0.0.1,localhost \
	LC_ALL=C

# veri needs bash 5 (since 2026-09-18), and the suites run under whatever `bash` is first on
# PATH — every one starts with `#!/usr/bin/env bash`. Nothing tests veri on bash 3.2 any more,
# the bash macOS ships in /bin, so a stale PATH must not be left to fail however a bash-4-only
# construct happens to fail inside some suite: the recipe asks that bash its major version
# before any suite runs, and refuses naming what to install. VERI_BASH_MAJOR stands in for the
# answer, for bash-version-guard.test.sh, because CI's runner has no older bash to ask. An
# answer that is not a number (no bash on PATH at all) is refused too, rather than compared.
BASH_GUARD := bash_major="$${VERI_BASH_MAJOR:-$$(bash -c 'echo "$${BASH_VERSINFO[0]}"' 2>/dev/null)}"; \
	case "$$bash_major" in ''|*[!0-9]*) bash_major=0 ;; esac; \
	if [ "$$bash_major" -lt 5 ]; then \
	  printf 'veri needs bash 5 or newer; the bash on PATH is version %s. Install it with `brew install bash` (it lands ahead of /bin/bash on PATH), or your package manager on Linux.\n' "$${VERI_BASH_MAJOR:-$$(bash -c 'echo "$${BASH_VERSION}"' 2>/dev/null)}" >&2; \
	  exit 2; \
	fi

test unit:
	@$(BASH_GUARD)
	@fail=0; suite_out="$$(mktemp)"; suite_status="$$(mktemp)"; reach_log="$$(mktemp)"; git_bin="$$(mktemp -d)"; \
	trap 'rm -f "$$suite_out" "$$suite_status" "$$reach_log"; rm -rf "$$git_bin"' EXIT; \
	py_bin="$${VERI_VENV:-$$HOME/.veri-tools/venv}/bin/python3"; \
	[ -x "$$py_bin" ] || py_bin="$$(command -v python3)"; \
	$(OFFLINE_GIT); \
	for t in $(SUITES); do \
	  suite_name="$$(basename "$$t")"; \
	  printf '== %s\n' "$$suite_name"; \
	  : > "$$reach_log"; \
	  { $(OFFLINE_ENV) "$$t" < /dev/null 2>&3; echo $$? > "$$suite_status"; } 3>&2 | tee "$$suite_out"; \
	  [ "$$(cat "$$suite_status")" -eq 0 ] || fail=1; \
	  last_line="$$(tail -n 1 "$$suite_out")"; \
	  printf '%s\n' "$$last_line" | grep -E '$(COUNT_LINE)' > /dev/null || { \
	    printf '$(COUNTLESS)' "$$suite_name"; \
	    if grep '[^[:space:]]' "$$suite_out" > /dev/null; then printf '%s: its last line was: %s\n' "$$suite_name" "$$last_line"; \
	    else printf '%s: its output was empty\n' "$$suite_name"; fi; fail=1; \
	  }; \
	  while IFS= read -r reached; do \
	    printf '%s: tried the network: %s\n' "$$suite_name" "$$reached"; fail=1; \
	  done < "$$reach_log"; \
	done; \
	if [ -n "$(PY_TESTS)" ]; then \
	  printf '== pytest\n'; \
	  $(OFFLINE_ENV) "$$py_bin" -m pytest $(PY_TESTS) < /dev/null || fail=1; \
	fi; \
	echo "----"; \
	if [ $$fail -eq 0 ]; then echo "all suites green"; else echo "SUITES FAILED"; exit 1; fi

# `make profile` runs the suites `test` runs, under the same offline environment, through
# profile.sh: one line per case at or above VERI_PROFILE_THRESHOLD seconds, slowest first
# (#329). A tool a human runs on demand — not part of `test`, and nothing gates on it.
.PHONY: profile
profile:
	@$(BASH_GUARD)
	@reach_log="$$(mktemp)"; git_bin="$$(mktemp -d)"; \
	trap 'rm -f "$$reach_log"; rm -rf "$$git_bin"' EXIT; \
	$(OFFLINE_GIT); \
	$(OFFLINE_ENV) skills/tdd/scripts/profile.sh $(SUITES) < /dev/null

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
