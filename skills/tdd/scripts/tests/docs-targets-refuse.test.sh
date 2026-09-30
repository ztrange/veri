#!/usr/bin/env bash
# Unit tests for the four documentation targets in this repository's Makefile — what they do
# when the shell that invoked them is one of veri's own. Like hermetic-suites.test.sh,
# count-line-guard.test.sh and prose-lag-green.test.sh this suite has no script as its
# subject: its subject is a recipe. Zero-dependency plain-shell asserts, same idiom as
# prose-lag-green.test.sh.
#
# Why this exists (issue #143): the third door a documentation build walks through into a
# development run is an agent typing `make docs`. Nothing refuses it today, and CLAUDE.md's
# "one trap" section tells any agent that touched the page to run exactly that — so on
# 2026-09-13 the conductor solving #106 spent ~5.5 min on `make docs` and `make docs-check`
# inside a run whose test command was `make test`, and then paid for the rebuild again at
# merge. The development lane's cost is three `make test` runs a step; a page build is not
# part of that bargain, and neither is the red a stale page can hand back.
#
# The conductor gives every leaf it launches, and every command it runs itself, the run's
# test command as VERI_TEST_CMD. That variable is therefore the one fact a recipe can read
# that says "you are inside a development run" — and a value that is not itself a
# documentation target is what makes the run a development one.
#
# Contract under test:
#   With VERI_TEST_CMD set to a development command (`make test`), each of `make docs`,
#   `make docs-test`, `make docs-check` and `make docs-fresh` exits 2, runs none of the
#   things it would otherwise run, and says on stderr why it refused.
#
#   And the far side of the same door: with VERI_TEST_CMD unset — a human, `make
#   merge-gates`, CI — or set to a documentation target, the run is not a development one
#   and those same four targets run exactly as they did before the guard existed.
#
# All three halves are asked of every one of the four targets, because a guard written into
# three recipes and forgotten in the fourth leaves the door it was built to shut open, and
# `docs-check` is not covered by its two prerequisites: it is the target a human types, so
# what it does is a fact of its own.
#
# Exit 2 is the weakest of the three probes and is asked anyway, because it is what the
# criterion names and what a caller branches on. `make` maps every failed recipe onto its
# own exit 2 whatever the recipe returned, so that code alone would also be given by a
# recipe that broke for an unrelated reason — which is precisely why the other two probes
# are there: a recipe that died on its own would have run something, or would have said
# nothing about VERI_TEST_CMD on its way out.
#
# Nothing here runs the real build. "Runs nothing" is observed in a scratch tree holding
# this repository's Makefile, copied byte for byte and cmp-checked so the recipe under test
# is the committed one, and a tripwire standing in for each thing the four targets invoke:
# the page builder, the freshness check and one suite under the directory `docs-test` globs.
# Each tripwire appends a word to a log, so an empty log after a run is the observation that
# the recipe stopped before reaching any of them. Standing the recipes up over stand-ins is
# also the only way to ask the question at all: a run of the real build against this
# repository would rewrite the committed page, which is a change this phase must not leave
# behind, and would cost minutes inside a target that runs three times per step.
#
# probe_tripwires_fire_when_the_variable_is_unset is what keeps that observation from being
# vacuous: with VERI_TEST_CMD out of the environment the same four targets over the same
# tree have to reach their tripwires and come back 0. Without it, a scratch tree whose
# Makefile could not find anything would pass every probe above by failing at everything.
# It is asked with `env -u` rather than by not setting the variable, because once this
# issue lands every leaf running `make test` has VERI_TEST_CMD in its environment already —
# a suite's answer must be a fact about the recipe, not about its caller (#87).
#
# No line of code below spells the generated tree's name with its slash — it is built onto
# GENERATED_DIR — so this suite does not break the rule no-docs-reads.test.sh keeps. Writing
# a tripwire into a scratch tree is not reading that tree: no assertion here is decided by a
# byte of this repository's own copy of it.
#
# Run: skills/tdd/scripts/tests/docs-targets-refuse.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/lib/harness.sh"
ROOT="$(cd "$HERE/../../../.." && pwd)"

pass=0 fail=0
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

MAKEFILE="$ROOT/Makefile"
LOG="$WORK/ran.log"

GENERATED_DIR='docs'

TARGETS=(docs docs-test docs-check docs-fresh)

DEV_CMD='make test'

DOCS_CMD='make docs-test'

TRIPWIRE_VAR='VERI_TRIPWIRE_LOG'
GUARD_VAR='VERI_TEST_CMD'

flat() { printf '%s' "$1" | tr '\n' '/'; }

target_list() {
  local last=$(( ${#TARGETS[@]} - 1 )) joined
  joined="$(printf '%s, ' "${TARGETS[@]:0:$last}")"
  printf '%s and %s' "${joined%, }" "${TARGETS[$last]}"
}

python_tripwire() {
  cat > "$1" <<PY
import os
with open(os.environ["$TRIPWIRE_VAR"], "a") as log:
    log.write("$2\n")
PY
}

shell_tripwire() {
  cat > "$1" <<SH
#!/usr/bin/env bash
set -uo pipefail
printf '$2\n' >> "\$$TRIPWIRE_VAR"
echo "1 passed, 0 failed"
SH
  chmod +x "$1"
}

TREE=""

tree_with_tripwires() {
  TREE="$WORK/tree"
  mkdir -p "$TREE/$GENERATED_DIR/tests"
  cp "$MAKEFILE" "$TREE/Makefile"

  python_tripwire "$TREE/$GENERATED_DIR/build-walkthrough.py" "built the page"
  python_tripwire "$TREE/$GENERATED_DIR/check-walkthrough.py" "checked the page is fresh"
  shell_tripwire "$TREE/$GENERATED_DIR/tests/tripwire.test.sh" "ran a documentation suite"
}

run_code=0
run_out=""
run_err=""

run_target() {
  local target="$1" err="$WORK/err"
  shift
  : > "$LOG"
  run_out="$(env "$TRIPWIRE_VAR=$LOG" "$@" make -C "$TREE" "$target" 2>"$err")" &&
    run_code=0 || run_code=$?
  run_err="$(cat "$err")"
}

run_streams() { printf 'stdout: %s, stderr: %s' "$(flat "$run_out")" "$(flat "$run_err")"; }

probe_runner_is_this_repositorys() {
  cmp -s "$MAKEFILE" "$TREE/Makefile" ||
    problems+=("the runner under test is not this repository's Makefile, so nothing here says what its documentation targets do")
}

probe_tripwires_fire_when_the_variable_is_unset() {
  local target
  for target in "${TARGETS[@]}"; do
    run_target "$target" env -u "$GUARD_VAR"
    [[ "$run_code" == 0 ]] ||
      problems+=("the premise broke: with $GUARD_VAR unset, 'make $target' over the scratch tree exited $run_code, so a refusal below is not distinguishable from a tree that cannot run: $(run_streams)")
    [[ -s "$LOG" ]] ||
      problems+=("the premise broke: with $GUARD_VAR unset, 'make $target' reached none of the stand-ins, so an empty log after a refusal says nothing")
  done
}

probe_targets_refuse() {
  local target
  for target in "${TARGETS[@]}"; do
    run_target "$target" env "$GUARD_VAR=$DEV_CMD"

    [[ "$run_code" == 2 ]] ||
      problems+=("want 'make $target' to exit 2 under $GUARD_VAR='$DEV_CMD'; got $run_code, $(run_streams)")
    [[ ! -s "$LOG" ]] ||
      problems+=("'make $target' ran something under $GUARD_VAR='$DEV_CMD' — a development run must not pay for a page build: $(flat "$(cat "$LOG")")")
    grep -q "$GUARD_VAR" <<<"$run_err" ||
      problems+=("nothing on stderr from 'make $target' named $GUARD_VAR, so its refusal does not say why: $(flat "$run_err")")
  done
}

name="with $GUARD_VAR='$DEV_CMD', make $(target_list) each exit 2 without running anything and say why on stderr"
problems=()

tree_with_tripwires
probe_runner_is_this_repositorys
probe_tripwires_fire_when_the_variable_is_unset
probe_targets_refuse

report "$name"

probe_targets_run() {
  local situation="$1" target
  shift
  for target in "${TARGETS[@]}"; do
    run_target "$target" "$@"

    [[ "$run_code" == 0 ]] ||
      problems+=("want 'make $target' to run as before with $situation; got exit $run_code, $(run_streams)")
    [[ -s "$LOG" ]] ||
      problems+=("'make $target' with $situation reached none of the stand-ins, so it did not run as before: the guard fired outside a development run")
  done
}

name="with $GUARD_VAR unset, or set to '$DOCS_CMD', make $(target_list) each run as before"
problems=()

tree_with_tripwires
probe_runner_is_this_repositorys
probe_targets_run "$GUARD_VAR unset" env -u "$GUARD_VAR"
probe_targets_run "$GUARD_VAR='$DOCS_CMD'" env "$GUARD_VAR=$DOCS_CMD"

report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
