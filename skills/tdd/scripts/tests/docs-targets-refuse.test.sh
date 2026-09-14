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
# The suite sits at skills/<skill>/scripts/tests, so four levels up is the repo root.
ROOT="$(cd "$HERE/../../../.." && pwd)"

pass=0 fail=0
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

# The runner under test, and the log every tripwire in the scratch tree appends to. The log
# lives outside the tree so that a target which wipes or rebuilds part of it cannot take the
# evidence with it.
MAKEFILE="$ROOT/Makefile"
LOG="$WORK/ran.log"

# The generated tree's name, without its trailing slash, so no line of this file names a
# path inside it. The tripwires are written to paths built from it.
GENERATED_DIR='docs'

# The four targets, in the order the criterion names them. A list, not a loop body written
# four times: the rule is about the door, and all four are the same door.
TARGETS=(docs docs-test docs-check docs-fresh)

# What a development run's test command looks like — this repository's own, which is what
# veri detects when run against itself and what the #106 conductor had set while it ran the
# page build. The value is the whole signal: it is not a documentation target, so a recipe
# reading it is inside a run that never asked for a page.
DEV_CMD='make test'

# What a documentation run's test command looks like: the target veri detects for an issue
# whose subject is the page. The guard has to read the variable's value and not merely its
# presence, because this is the one run that legitimately builds the page — a guard that
# fired on any veri run at all would leave the documentation lane unable to run its own
# tests, which is the same door shut on the wrong side.
DOCS_CMD='make docs-test'

# The two environment variables this suite is written around, each spelled once. The first is
# where the stand-ins are told to log. The second is the variable the recipes refuse over, and
# it plays three parts at once: what a probe sets to make the run a development one, what a
# probe unsets to ask the premise, and the word a stderr line has to carry for the refusal to
# have said why. One name for all three because they are one string — a suite that set one
# variable and looked for another on stderr would pass while the recipe named the wrong knob,
# and "refusing" with no knob in it sends its reader to the Makefile to find out which.
TRIPWIRE_VAR='VERI_TRIPWIRE_LOG'
GUARD_VAR='VERI_TEST_CMD'

# report <name> — close a case whose probes collected into the `problems` array: an empty
# array is a pass, otherwise one FAIL line for the case and one indented line per problem,
# so the output says which target and which half of the contract broke rather than just
# that the case did.
report() {
  local name="$1"
  if [[ "${#problems[@]}" -eq 0 ]]; then
    pass=$((pass + 1))
  else
    fail=$((fail + 1))
    echo "FAIL - $name"
    printf '    %s\n' "${problems[@]}"
  fi
}

# flat <text> — one line of it, for a failure message: newlines become slashes so a run's
# output quoted inside an indented problem line stays one line.
flat() { printf '%s' "$1" | tr '\n' '/'; }

# python_tripwire <path> <word> — one of the two python files the recipes name, written as a
# stand-in: it appends <word> to the log and exits 0. The heredoc is unquoted so the log's
# variable name comes from TRIPWIRE_VAR rather than being spelled again here — run_target sets
# that same variable, and a stand-in reading a different one would never fire, which would make
# every "nothing ran" observation below vacuous. Nothing in the python interpolates but those
# two placeholders: it has no `$`, no backtick, and `\n` survives an unquoted heredoc intact.
python_tripwire() {
  cat > "$1" <<PY
import os
with open(os.environ["$TRIPWIRE_VAR"], "a") as log:
    log.write("$2\n")
PY
}

# shell_tripwire <path> <word> — the third stand-in, and python_tripwire's twin: the suite the
# documentation target globs, written as an executable that appends <word> to the log, prints
# the count line every suite in this repository ends with, and exits 0. Its heredoc is unquoted
# for the same reason python_tripwire's is — the log's variable name is written once, in
# TRIPWIRE_VAR, so a stand-in can never end up reading a different one than run_target sets. `\$`
# is a literal dollar, so the file receives `"$VERI_TRIPWIRE_LOG"`; the only other thing the
# writing shell expands is <word>, which is why nothing else here carries a `$` or a backtick.
shell_tripwire() {
  cat > "$1" <<SH
#!/usr/bin/env bash
set -uo pipefail
printf '$2\n' >> "\$$TRIPWIRE_VAR"
echo "1 passed, 0 failed"
SH
  chmod +x "$1"
}

# tree_with_tripwires — a disposable tree holding the real Makefile and a stand-in for each
# thing the four targets invoke, printed as a path. The page builder and the freshness check
# are stood up as the two python files the recipes name; the suite the documentation target
# globs is stood up as one executable under the directory that glob looks in, so it is found
# by existing exactly as a real one would be. Each appends a word to the log and exits 0,
# which is what makes "the log is empty" mean "the recipe stopped before reaching it".
tree_with_tripwires() {
  local tree="$WORK/tree"
  mkdir -p "$tree/$GENERATED_DIR/tests"
  cp "$MAKEFILE" "$tree/Makefile"

  python_tripwire "$tree/$GENERATED_DIR/build-walkthrough.py" "built the page"
  python_tripwire "$tree/$GENERATED_DIR/check-walkthrough.py" "checked the page is fresh"
  shell_tripwire "$tree/$GENERATED_DIR/tests/tripwire.test.sh" "ran a documentation suite"

  printf '%s' "$tree"
}

# The three globals run_target leaves a run in, initialized once here rather than again at the
# head of every case: they are one function's output, and each of them is written on every
# path through it, so a case that re-blanked them was restating that rather than deciding it.
# Initialized at all — instead of left to the first run — because `set -u` is declared above,
# and a probe added later that reads a run it did not make should fail on its own assertion
# rather than kill the suite at an unbound name.
run_code=0
run_out=""
run_err=""

# run_target <tree> <target> <env...> — one invocation of the recipe under test, with the log
# emptied first and the two streams kept apart, leaving the exit status in `run_code`, stdout
# in `run_out` and stderr in `run_err`. The streams are captured separately because "says why
# on stderr" is a claim about which stream carried the diagnostic, and a 2>&1 capture cannot
# tell a recipe that explained itself from one that printed the same words on stdout. Only the
# capture differs — stderr needs a file because a command substitution can only take stdout —
# and the file is read here rather than by each probe, so both streams reach them as text.
run_target() {
  local tree="$1" target="$2" err="$WORK/err"
  shift 2
  : > "$LOG"
  run_out="$(env "$TRIPWIRE_VAR=$LOG" "$@" make -C "$tree" "$target" 2>"$err")" &&
    run_code=0 || run_code=$?
  run_err="$(cat "$err")"
}

# run_streams — what the last run said, on one line, for a failure message. Both streams
# together because a target that did the wrong thing can have explained itself on either, and
# a message quoting one of them leaves the next reader running the command again to see the
# other. Named here rather than spelled at each probe that reports an unexpected exit status:
# the pair is one thought — "and here is what it printed while doing that" — and it is read
# off run_target's globals for the same reason report() reads `problems`, so a probe cannot
# quote one run's status beside another run's output.
run_streams() { printf 'stdout: %s, stderr: %s' "$(flat "$run_out")" "$(flat "$run_err")"; }

# probe_runner_is_this_repositorys <tree> — the premise every probe below rests on: the
# Makefile in the scratch tree is this repository's, byte for byte. Without it the case could
# be satisfied by a runner this suite quietly adjusted on its way past, and would say nothing
# about what an agent typing `make docs` in this repository gets.
probe_runner_is_this_repositorys() {
  cmp -s "$MAKEFILE" "$1/Makefile" ||
    problems+=("the runner under test is not this repository's Makefile, so nothing here says what its documentation targets do")
}

# probe_tripwires_fire_when_the_variable_is_unset <tree> — the other premise, and the one
# that makes "nothing ran" mean something: with the guard variable out of the environment, each
# of the four targets over this same tree reaches a tripwire and comes back 0. A tree in which
# they could not — a stand-in at the wrong path, a glob that matched nothing — would answer
# every probe below with a refusal it had nothing to do with.
probe_tripwires_fire_when_the_variable_is_unset() {
  local target
  for target in "${TARGETS[@]}"; do
    run_target "$1" "$target" env -u "$GUARD_VAR"
    [[ "$run_code" == 0 ]] ||
      problems+=("the premise broke: with $GUARD_VAR unset, 'make $target' over the scratch tree exited $run_code, so a refusal below is not distinguishable from a tree that cannot run: $(flat "$run_err")")
    [[ -s "$LOG" ]] ||
      problems+=("the premise broke: with $GUARD_VAR unset, 'make $target' reached none of the stand-ins, so an empty log after a refusal says nothing")
  done
}

# probe_targets_refuse <tree> — the criterion itself, for each of the four targets: exit 2,
# an untouched log, and a stderr line naming the variable it refused over. Three problems at
# most per target, each naming it, because which of the three a recipe gets wrong is what
# sends the next author to the right line — a guard that exits 2 after building the page has
# cost the run the minutes the rule exists to save, and one that refuses in silence looks to
# a reader exactly like a broken build.
probe_targets_refuse() {
  local target
  for target in "${TARGETS[@]}"; do
    run_target "$1" "$target" env "$GUARD_VAR=$DEV_CMD"

    [[ "$run_code" == 2 ]] ||
      problems+=("want 'make $target' to exit 2 under $GUARD_VAR='$DEV_CMD'; got $run_code, $(run_streams)")
    [[ ! -s "$LOG" ]] ||
      problems+=("'make $target' ran something under $GUARD_VAR='$DEV_CMD' — a development run must not pay for a page build: $(flat "$(cat "$LOG")")")
    grep -q "$GUARD_VAR" <<<"$run_err" ||
      problems+=("nothing on stderr from 'make $target' named $GUARD_VAR, so its refusal does not say why: $(flat "$run_err")")
  done
}

# 1. One criterion, one case: inside a development run, all four documentation targets
#    refuse. Three probes, each asked of the whole target list: the two premises first —
#    the runner is the real one, and the stand-ins the refusal is measured against really
#    do fire — then the criterion.
name="with $GUARD_VAR='$DEV_CMD', make docs, docs-test, docs-check and docs-fresh each exit 2 without running anything and say why on stderr"
problems=()

tree="$(tree_with_tripwires)"
probe_runner_is_this_repositorys "$tree"
probe_tripwires_fire_when_the_variable_is_unset "$tree"
probe_targets_refuse "$tree"

report "$name"

# probe_targets_run <tree> <situation> <env...> — the other criterion, asked of each of the
# four targets under one environment in which the guard must not fire: exit 0, and a log the
# run left something in. Both halves, because either alone can be had by accident — a recipe
# that refused before doing anything would still exit 0 if its guard said so, and a recipe
# that reached its stand-in and then broke would still leave the log written.
#
# <situation> is carried into the failure message rather than derived from the environment,
# because "unset" and "set to a documentation target" are two different reasons for the same
# expectation and which one broke is what sends the next author to the right half of the
# guard's condition.
probe_targets_run() {
  local tree="$1" situation="$2" target
  shift 2
  for target in "${TARGETS[@]}"; do
    run_target "$tree" "$target" "$@"

    [[ "$run_code" == 0 ]] ||
      problems+=("want 'make $target' to run as before with $situation; got exit $run_code, $(run_streams)")
    [[ -s "$LOG" ]] ||
      problems+=("'make $target' with $situation reached none of the stand-ins, so it did not run as before: the guard fired outside a development run")
  done
}

# 2. The criterion's other side, and one case because it is one rule: the guard fires only
#    inside a development run, so in the two environments that are not one — the variable
#    absent, and the variable naming a documentation target — all four targets run as they
#    did. The two are asked together rather than as two cases because a guard gets them both
#    wrong or both right in the same line of the Makefile: `-n "$VERI_TEST_CMD"` alone shuts
#    out the documentation lane, and no condition at all shuts out the human.
#
#    Case 1 already runs the four targets with the variable unset, but as its premise —
#    there it is what makes an empty log mean something, and its failure says the scratch
#    tree is broken. Here the same run is the claim itself, and its failure says the guard
#    is. A premise that the criterion happens to share is not the criterion asserted.
name="with $GUARD_VAR unset, or set to '$DOCS_CMD', make docs, docs-test, docs-check and docs-fresh each run as before"
problems=()

tree="$(tree_with_tripwires)"
probe_runner_is_this_repositorys "$tree"
probe_targets_run "$tree" "$GUARD_VAR unset" env -u "$GUARD_VAR"
probe_targets_run "$tree" "$GUARD_VAR='$DOCS_CMD'" env "$GUARD_VAR=$DOCS_CMD"

report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
