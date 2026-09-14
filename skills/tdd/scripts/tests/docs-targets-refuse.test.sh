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

# The variable the tripwires are told where to log through, and the word a stderr line has
# to carry for the refusal to have said why. The second is the environment variable the
# recipe refused over: a reader who sees it knows both what stopped the build and which
# knob to reach for, where "refusing" alone sends them to read the Makefile.
TRIPWIRE_VAR='VERI_TRIPWIRE_LOG'
REASON='VERI_TEST_CMD'

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

  cat > "$tree/$GENERATED_DIR/build-walkthrough.py" <<'PY'
import os
with open(os.environ["VERI_TRIPWIRE_LOG"], "a") as log:
    log.write("built the page\n")
PY
  cat > "$tree/$GENERATED_DIR/check-walkthrough.py" <<'PY'
import os
with open(os.environ["VERI_TRIPWIRE_LOG"], "a") as log:
    log.write("checked the page is fresh\n")
PY
  cat > "$tree/$GENERATED_DIR/tests/tripwire.test.sh" <<'SH'
#!/usr/bin/env bash
set -uo pipefail
printf 'ran a documentation suite\n' >> "$VERI_TRIPWIRE_LOG"
echo "1 passed, 0 failed"
SH
  chmod +x "$tree/$GENERATED_DIR/tests/tripwire.test.sh"

  printf '%s' "$tree"
}

# run_target <tree> <target> <env...> — one invocation of the recipe under test, with the log
# emptied first and the two streams kept apart, leaving the exit status in `run_code`, stdout
# in `run_out` and the path of the stderr file in `run_err`. Separate files because "says why
# on stderr" is a claim about which stream carried the diagnostic, and a 2>&1 capture cannot
# tell a recipe that explained itself from one that printed the same words on stdout.
run_target() {
  local tree="$1" target="$2"
  shift 2
  : > "$LOG"
  run_err="$WORK/err"
  run_out="$(env "$TRIPWIRE_VAR=$LOG" "$@" make -C "$tree" "$target" 2>"$run_err")" &&
    run_code=0 || run_code=$?
}

# probe_runner_is_this_repositorys <tree> — the premise every probe below rests on: the
# Makefile in the scratch tree is this repository's, byte for byte. Without it the case could
# be satisfied by a runner this suite quietly adjusted on its way past, and would say nothing
# about what an agent typing `make docs` in this repository gets.
probe_runner_is_this_repositorys() {
  cmp -s "$MAKEFILE" "$1/Makefile" ||
    problems+=("the runner under test is not this repository's Makefile, so nothing here says what its documentation targets do")
}

# probe_tripwires_fire_when_the_variable_is_unset <tree> — the other premise, and the one
# that makes "nothing ran" mean something: with VERI_TEST_CMD out of the environment, each of
# the four targets over this same tree reaches a tripwire and comes back 0. A tree in which
# they could not — a stand-in at the wrong path, a glob that matched nothing — would answer
# every probe below with a refusal it had nothing to do with.
probe_tripwires_fire_when_the_variable_is_unset() {
  local target
  for target in "${TARGETS[@]}"; do
    run_target "$1" "$target" env -u VERI_TEST_CMD
    [[ "$run_code" == 0 ]] ||
      problems+=("the premise broke: with VERI_TEST_CMD unset, 'make $target' over the scratch tree exited $run_code, so a refusal below is not distinguishable from a tree that cannot run: $(flat "$(cat "$run_err")")")
    [[ -s "$LOG" ]] ||
      problems+=("the premise broke: with VERI_TEST_CMD unset, 'make $target' reached none of the stand-ins, so an empty log after a refusal says nothing")
  done
}

# probe_target_refuses <tree> <target> — the criterion itself, for one target: exit 2, an
# untouched log, and a stderr line naming the variable it refused over. Three problems at
# most, each naming the target, because which of the three a recipe gets wrong is what sends
# the next author to the right line — a guard that exits 2 after building the page has cost
# the run the minutes the rule exists to save, and one that refuses in silence looks to a
# reader exactly like a broken build.
probe_target_refuses() {
  local target="$2"
  run_target "$1" "$target" env "VERI_TEST_CMD=$DEV_CMD"

  [[ "$run_code" == 2 ]] ||
    problems+=("want 'make $target' to exit 2 under VERI_TEST_CMD='$DEV_CMD'; got $run_code, stdout: $(flat "$run_out"), stderr: $(flat "$(cat "$run_err")")")
  [[ ! -s "$LOG" ]] ||
    problems+=("'make $target' ran something under VERI_TEST_CMD='$DEV_CMD' — a development run must not pay for a page build: $(flat "$(cat "$LOG")")")
  grep -q "$REASON" "$run_err" ||
    problems+=("nothing on stderr from 'make $target' named $REASON, so its refusal does not say why: $(flat "$(cat "$run_err")")")
}

# 1. One criterion, one case: inside a development run, all four documentation targets
#    refuse. The two premises first — the runner is the real one, and the stand-ins the
#    refusal is measured against really do fire — then the four targets, each through the
#    same three probes.
name="with VERI_TEST_CMD='$DEV_CMD', make docs, docs-test, docs-check and docs-fresh each exit 2 without running anything and say why on stderr"
problems=()
run_code=0
run_out=""
run_err=""

tree="$(tree_with_tripwires)"
probe_runner_is_this_repositorys "$tree"
probe_tripwires_fire_when_the_variable_is_unset "$tree"
for target in "${TARGETS[@]}"; do
  probe_target_refuses "$tree" "$target"
done

report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
