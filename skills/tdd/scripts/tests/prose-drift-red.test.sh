#!/usr/bin/env bash
# Unit tests for what the `test` recipe says over a tree whose code has moved past the
# SYSTEM prose that states it. The mirror of prose-lag-green.test.sh, which asks the same
# runner about the prose the development lane is being taken off; like that suite,
# hermetic-suites.test.sh and no-docs-reads.test.sh this one has no script as its subject —
# its subject is the verdict the development lane's own runner reaches over a tree.
# Zero-dependency plain-shell asserts, same idiom as prose-lag-green.test.sh.
#
# Why this exists (issue #143): the way to take the development lane off generated prose
# wrongly is to take it off prose altogether. VERI_REFACTOR_BUDGET's default is stated three
# times in this lane — the assignment in refactor-budget.sh that encodes it, that script's
# own header, and SKILL.md's Refactor entry — and the two sentences live under skills/, the
# lane's own tree, which is exactly where a leaf that moves the constant is already editing.
# Nothing outside this lane reads them, so if `make test` stops catching that drift nothing
# does: a conductor reads `(default 5)` in SKILL.md, narrates and budgets a five-transform
# loop, and the script cuts it somewhere else.
#
# refactor-budget.test.sh case 8 is the guard. This suite is the same rule observed rather
# than read: the constant is moved, both sentences are left exactly as they were, and the
# runner is asked for its verdict.
#
# Contract under test:
#   Over a copy of this tree with refactor-budget.sh's VERI_REFACTOR_BUDGET default bumped by
#   one and both prose statements of it untouched, `make test` runs the suite that owns that
#   script, comes back non-zero with its own `SUITES FAILED` verdict, and the output names
#   both sentences the change left behind.
#
# Naming them is not decoration, it is what keeps the case about the guard. Bumping the
# constant also falsifies the cases that pin the figure itself, so `SUITES FAILED` alone
# would still be printed over a tree whose drift guard had been deleted — the criterion is
# that the sentences are checked, so the red has to mention them.
#
# The roster is narrowed to one suite through the recipe's own TESTS variable, for the two
# reasons prose-lag-green.test.sh sets out at length and does not need restating here: the
# copy is a partial tree, so suites reading what it does not carry would fail for reasons
# that are not the criterion; and this case runs inside `make test`, which runs three times
# per step, so the whole roster over a copy would add minutes to every step of every issue.
#
# What the copy carries is what refactor-budget.test.sh resolves against its own repo root —
# the skill tree, which holds both the script and SKILL.md — plus the Makefile, which is the
# runner itself. Nothing else is copied, and in particular the generated tree is not: no
# assertion here is decided by a byte of it, and no line below names a path in it, which is
# what no-docs-reads.test.sh asks of every suite in this directory.
#
# Run: skills/tdd/scripts/tests/prose-drift-red.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/lib/harness.sh"
ROOT="$(cd "$HERE/../../../.." && pwd)"

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

TUNABLE='VERI_REFACTOR_BUDGET'
SCRIPT='skills/tdd/scripts/refactor-budget.sh'
SUITE='skills/tdd/scripts/tests/refactor-budget.test.sh'
SUITE_NAME="${SUITE##*/}"

SKILL_MARKER='SKILL.md'
HEADER_MARKER='header'

FAILED_LINE='SUITES FAILED'

flat() { printf '%s' "$1" | tr '\n' '/'; }

why() { flat "$( { grep -E '^FAIL - ' <<< "$1"; tail -5 <<< "$1"; } )"; }

figure() {
  local hit
  hit="$(head -1 < <(grep -oE "$2" "$1"))"
  [[ -n "$hit" ]] || { echo '<none>'; return; }
  printf '%s' "$hit" | grep -oE '[0-9]+' | tail -1
}

ENCODED_RE="$TUNABLE:-[0-9]+"
HEADER_RE="$TUNABLE \(default [0-9]+"
SKILL_RE="$TUNABLE.{0,3} \(default [0-9]+"

tree_whose_default_moved() {
  local planted="$WORK/tree" here_default
  mkdir -p "$planted"
  cp -R "$ROOT/skills" "$planted/skills"
  cp "$ROOT/Makefile" "$planted/"
  here_default="$(figure "$ROOT/$SCRIPT" "$ENCODED_RE")"
  sed -E "s/$TUNABLE:-[0-9]+/$TUNABLE:-$((here_default + 1))/" \
    "$ROOT/$SCRIPT" > "$planted/$SCRIPT.planted"
  mv "$planted/$SCRIPT.planted" "$planted/$SCRIPT"
  chmod 755 "$planted/$SCRIPT"
  printf '%s' "$planted"
}

probe_plant_is_real() {
  local moved here site
  moved="$(figure "$1/$SCRIPT" "$ENCODED_RE")"
  here="$(figure "$ROOT/$SCRIPT" "$ENCODED_RE")"
  [[ "$moved" =~ ^[0-9]+$ && "$here" =~ ^[0-9]+$ && "$moved" != "$here" ]] ||
    problems+=("the case is vacuous: $SCRIPT encodes $moved in the copy against $here here, so the constant the prose describes has not moved")
  while IFS='|' read -r site file regex; do
    [[ -n "$site" ]] || continue
    [[ "$(figure "$1/$file" "$regex")" == "$here" ]] ||
      problems+=("the case is vacuous: $site in the copy says $(figure "$1/$file" "$regex"), not the $here it said before the plant, so no sentence was left behind")
  done <<SITES
$SCRIPT-header|$SCRIPT|$HEADER_RE
SKILL.md-refactor|skills/tdd/SKILL.md|$SKILL_RE
SITES
}

name="\`make test\` is red over a tree whose $TUNABLE default has moved and whose two prose statements of it have not, naming both"
problems=()

planted="$(tree_whose_default_moved)"
probe_plant_is_real "$planted"

out="$(make -C "$planted" test TESTS="$SUITE" 2>&1)" && code=0 || code=$?

[[ "$code" != 0 ]] ||
  problems+=("want a non-zero exit from the runner over a tree whose $TUNABLE default has drifted from the prose stating it; got 0: $(flat "$out")")
grep -Fqx "$FAILED_LINE" <<< "$out" ||
  problems+=("want the runner's own '$FAILED_LINE' over that tree; got: $(why "$out")")
grep -Fqx "== $SUITE_NAME" <<< "$out" ||
  problems+=("want the runner to have announced '== $SUITE_NAME' — an empty roster says nothing about the guard; got: $(flat "$out")")
grep -Fq "$SKILL_MARKER" <<< "$out" ||
  problems+=("want the red to name '$SKILL_MARKER', the statement the plant left behind — a red that never mentions it is the figure's own cases failing, not the drift guard; got: $(why "$out")")
grep -Fq "$HEADER_MARKER" <<< "$out" ||
  problems+=("want the red to name the script's own '$HEADER_MARKER', the other statement the plant left behind; got: $(why "$out")")

report "$name"

finish
