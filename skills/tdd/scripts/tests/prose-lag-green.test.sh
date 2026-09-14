#!/usr/bin/env bash
# Unit tests for what the `test` recipe says over a tree whose scripts have grown past the
# prose that lists them — like hermetic-suites.test.sh, count-line-guard.test.sh and
# no-docs-reads.test.sh this suite has no script as its subject: its subject is the verdict
# the development lane's own runner reaches over a tree. Zero-dependency plain-shell
# asserts, same idiom as no-docs-reads.test.sh.
#
# Why this exists (issue #143): every commit to a script under skills/tdd/scripts/ leaves
# the generated page behind the code, because that page quotes each script verbatim and
# states its length in the listing's own header. While solvable-issues.test.sh case 13 read
# that number and compared it to the script's own length, a one-line edit to
# solvable-issues.sh turned `make test` red until somebody ran `make docs` and committed the
# result — and `make test` is the target preflight reads its baseline off, that every Green
# leaf runs and that both blind verifiers run, three times per step. So a development commit
# owed a page rebuild to keep a development run alive, which is the coupling ADR 0016 rules
# out: a page behind the code is what docs-owed.sh reports and what `make docs-fresh` catches
# at a docs merge, not something the development lane gets to fail on.
#
# no-docs-reads.test.sh says that statically — no suite `make test` runs so much as names a
# path in the generated tree — and this is the same rule observed rather than read: a script
# is grown, nothing is rebuilt, and the runner is asked for its verdict.
#
# Contract under test:
#   Over a copy of this tree with one line appended to skills/tdd/scripts/solvable-issues.sh
#   and the generated tree copied across untouched, `make test` runs the suite that owns that
#   script, that suite passes, and the runner says `all suites green`.
#
# The roster is narrowed to that one suite through the recipe's own TESTS variable, for two
# reasons that both have to hold.
#
#   Scope. The copy is a partial tree, and deliberately so (see tree_grown_past_its_prose):
#   the whole roster run over one was measured at 98 s and came back SUITES FAILED, seven
#   cases across five suites — count-line-guard, skill-identity, skill-refactor-pending,
#   skill-suite-runs and workflow-timeouts — every one of them reading something the copy
#   does not carry: CLAUDE.md, .github/workflows/, or the git index its tracked-file sweeps
#   ask. None of that is the criterion, and a case that had to copy a whole repository
#   including its worktrees to avoid it would be pinning the copy rather than the rule.
#
#   Cost. This case runs inside `make test` itself, and `make test` runs three times per
#   step — once for develop-green and once for each blind verifier. 98 s of it would add
#   five minutes a step to every issue veri solves, to re-observe on 36 suites what
#   no-docs-reads.test.sh case 2 already establishes about all of them for the price of one
#   `make -n`.
#
# What no static check can establish is that the runner comes back green over a tree in that
# state, and one suite is enough to observe it: solvable-issues.test.sh is the suite that used
# to go red here, and solvable-issues.sh the script whose length it read, so this is the
# scenario the criterion names, run.
#
# The plant is an appended comment, at the END of the script: the page states a length and
# quotes the source, so a line added anywhere makes what the committed page says about that
# script false, and a line added at the end cannot disturb the header or the code that any
# other case reads.
#
# Nothing in the copy is rebuilt, and that is what makes the tree the one the criterion
# describes: the generated tree is copied across byte for byte, so whatever the page in the
# copy says about that script, it says about the file as it stood before the plant.
# probe_plant_is_real asserts the two lengths really did part company — a plant that landed
# somewhere else, or not at all, would leave this case passing over an ordinary tree.
#
# No line of code below spells the generated tree's name with its slash: it is built onto
# GENERATED_DIR, so this file is not the first offender against the rule it exists to
# observe. Copying that tree is not reading it — no assertion here is decided by a byte of
# it, which is the whole of what no-docs-reads.test.sh asks of a suite in this directory.
#
# Run: skills/tdd/scripts/tests/prose-lag-green.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
# The suite sits at skills/<skill>/scripts/tests, so four levels up is the repo root.
ROOT="$(cd "$HERE/../../../.." && pwd)"

pass=0 fail=0
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

# The script the plant grows and the suite that owns it, repo-relative — which is what the
# recipe's TESTS variable is handed, what the failure messages quote and what resolves
# against both trees. Each basename besides, and neither substitutes for the other: the
# runner announces each suite by basename (`== <name>`), which is how this case knows the
# narrowed roster was not empty, while the case name is about the file that grew.
SCRIPT='skills/tdd/scripts/solvable-issues.sh'
SCRIPT_NAME="${SCRIPT##*/}"
SUITE='skills/tdd/scripts/tests/solvable-issues.test.sh'
SUITE_NAME="${SUITE##*/}"

# The generated tree, written once and without its trailing slash, so that no line of this
# file names a path in it. It is copied into the plant and never opened.
GENERATED_DIR='docs'

# What the recipe prints when every suite it ran came back green — the runner's own verdict,
# which is the thing this case reads rather than the exit code alone (#157: a suite that dies
# partway routinely exits 0, and the recipe's answer is what the conductor branches on).
GREEN_LINE='all suites green'

# report <name> — close a case whose probes collected into the `problems` array: an empty
# array is a pass, otherwise one FAIL line for the case and one indented line per problem,
# so the output says which half of the contract broke rather than just that the case did.
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

# flat <text> — one line of it, for a failure message: newlines become slashes so a runner's
# output stays readable inside an indented problem line.
flat() { printf '%s' "$1" | tr '\n' '/'; }

# why <output> — the part of a runner's output that says what went wrong, flattened onto one
# problem line: every `FAIL - …` line a suite printed — the line every suite in this tree
# reports a failed case with — plus the last few lines, which is where the count line and the
# runner's own verdict are. The tail alone is not enough: a suite prints its failures above
# its count line, so five lines of tail come back saying `1 failed` without saying what
# failed, and naming the site is the whole value of a red case.
why() { flat "$( { grep -E '^FAIL - ' <<< "$1"; tail -5 <<< "$1"; } )"; }

# lines_of <path> — how long a file is, as the builder counts it. The number the deleted case
# compared against the page's listing header, and the one probe_plant_is_real watches move.
lines_of() { awk 'END {print NR}' "$1"; }

# tree_grown_past_its_prose — a disposable copy of this tree with $SCRIPT one line longer and
# nothing regenerated, printed as a path. Named, and out of the case body, so the case reads
# as the three steps it is: build the tree, prove the plant is really a plant, ask the runner.
#
# What is copied is what the suite under test resolves against $REPO_ROOT — the skill tree it
# tests, the two root documents case 11 of it reads — plus the Makefile, which is the runner
# itself, and the generated tree, which is copied so that the plant leaves the tree in the
# state the criterion describes rather than in one with no prose to lag behind. The whole
# repository is not copied: in the primary clone .tdd/ holds this repository's worktrees and
# a recursive copy would descend into them.
tree_grown_past_its_prose() {
  local planted="$WORK/tree"
  mkdir -p "$planted"
  cp -R "$ROOT/skills" "$planted/skills"
  cp -R "$ROOT/$GENERATED_DIR" "$planted/$GENERATED_DIR"
  cp "$ROOT/Makefile" "$ROOT/README.md" "$ROOT/CONTEXT.md" "$planted/"
  printf '\n# a line this script grew after the prose that lists it was written\n' >> "$planted/$SCRIPT"
  printf '%s' "$planted"
}

# probe_plant_is_real <dir> — the plant is only a plant if the script in the copy is no longer
# the script the copied prose describes, and its length is what says so: that is the number
# the deleted case read out of the page's listing header, so a copy whose script is still the
# same length is a tree the old case would have passed over too, and green there would mean
# nothing. Appends to `$problems` the way report() reads it.
probe_plant_is_real() {
  local grown here
  grown="$(lines_of "$1/$SCRIPT")"
  here="$(lines_of "$ROOT/$SCRIPT")"
  [[ "$grown" -gt "$here" ]] ||
    problems+=("the case is vacuous: $SCRIPT is $grown lines in the copy against $here here, so nothing in the copied prose was left describing a file that has moved on")
}

# 1. The criterion: a script grows, no rebuild follows, and the development lane's runner is
#    still green over the result. Exit code and the runner's own verdict line together, for
#    the reason the recipe itself checks both (#157) — a run that died before it reached its
#    answer must not read as the answer.
#
#    The suite's `== <name>` announcement is asserted too, because a TESTS list that resolved
#    to nothing would have the recipe print `all suites green` over an empty roster: the
#    narrowed roster has to have actually run the suite that used to go red here, or the case
#    observes an empty loop.
name="\`make test\` is green over a tree whose $SCRIPT_NAME has grown past the prose listing it, with nothing rebuilt in between"
problems=()

planted="$(tree_grown_past_its_prose)"
probe_plant_is_real "$planted"

out="$(make -C "$planted" test TESTS="$SUITE" 2>&1)" && code=0 || code=$?

[[ "$code" == 0 ]] ||
  problems+=("want exit 0 from the runner over a tree whose $SCRIPT has grown without a rebuild — a development commit must not owe one to keep the baseline green; got $code: $(why "$out")")
grep -Fqx "$GREEN_LINE" <<< "$out" ||
  problems+=("want the runner's own '$GREEN_LINE' over that tree; got: $(why "$out")")
grep -Fqx "== $SUITE_NAME" <<< "$out" ||
  problems+=("want the runner to have announced '== $SUITE_NAME' — an empty roster prints a green verdict over nothing run; got: $(flat "$out")")

report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
