#!/usr/bin/env bash
# Unit test for the four suites that hold CLAUDE.md to what it says — each one is in the
# roster `make test` runs, and each one is green against the document as committed. Like
# hermetic-suites.test.sh and no-docs-reads.test.sh this suite has no script as its
# subject: its subject is the other suites, run as child processes.
# Zero-dependency plain-shell asserts, same idiom as hermetic-suites.test.sh.
#
# Why this exists (issue #202): CLAUDE.md is re-sent and re-billed on every request of every
# session in this repository, and the saving is in moving prose out of it — a case history a
# leaf cannot act on to its issue, a decision a human needs to an ADR. What makes that edit
# safe is not that anything checks its size; #202 forbids a size assertion outright, because
# a byte that stops one bad leaf pays for itself many times over. What makes it safe is that
# four suites already hold the document to the rules it exists for, and a trim is accepted
# only when all four are still green afterwards:
#
#   claude-md-counts.test.sh     the script and suite counts the document states
#   lane-rule-recorded.test.sh   the two-lane rule in "The one trap"
#   count-line-guard.test.sh     the "Testing idiom" count-line rule, and why
#   docs-targets-refuse.test.sh  the development-run refusal
#
# Contract under test:
#   Each of those four is a suite `make test` runs, and each exits 0 with a count line
#   reporting no failures when run against the CLAUDE.md committed in this tree.
#
# Both halves, because the criterion is one sentence about `make test` and one about the
# four: a guard that left the roster is a guard a green `make test` no longer says anything
# about, and it would leave silently — the roster is a glob, so a suite drops out of it by
# being renamed or moved, not by anyone editing a list. Roster membership without a run
# would pin only that the files are there; a run without membership would pin a fact about
# this suite rather than about the baseline the conductor reads.
#
# It costs what it costs: ~5 s, paid by the three leaves a step that run the full suite.
# The four are re-run rather than their result inferred from `make test` failing around
# them, because "the baseline is red somewhere" is not the answer this criterion asks for —
# an accepted trim has to name the guards it did not break.
#
# No line of code below names a path in the generated tree: the suite whose name begins
# with the documentation lane's word is named as a file in this directory, which is where
# it lives, and that is the rule no-docs-reads.test.sh enforces here.
#
# Run: skills/tdd/scripts/tests/claude-md-guards-green.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"

claude_md="CLAUDE.md"

suites_dir="skills/tdd/scripts/tests"

GUARDS=(
  claude-md-counts.test.sh
  lane-rule-recorded.test.sh
  count-line-guard.test.sh
  docs-targets-refuse.test.sh
)

COUNT_LINE='^[0-9]+ passed, 0 failed$'


source "$HERE/lib/harness.sh"

roster() {
  make -C "$ROOT" -n test 2>/dev/null | grep -oE "$suites_dir/[A-Za-z0-9_.-]*\.test\.sh"
}

probe_every_guard_is_rostered_and_green() {
  local rost guard out code last cases guard_work
  rost="$(roster)"

  if [[ -z "$rost" ]]; then
    problems+=("\`make -n test\` named no suite in $suites_dir, so the roster a green run covers could not be read")
  fi

  guard_work="$(mktemp -d)"

  for guard in "${GUARDS[@]}"; do
    if [[ -n "$rost" ]] && ! grep -qxF "$suites_dir/$guard" <<< "$rost"; then
      problems+=("$suites_dir/$guard is not in the roster \`make test\` runs, so a green baseline says nothing about it")
    fi

    ( "$HERE/$guard" > "$guard_work/$guard.out" 2>&1; echo $? > "$guard_work/$guard.status" ) &
  done
  wait

  for guard in "${GUARDS[@]}"; do
    out="$(cat "$guard_work/$guard.out")"
    code="$(cat "$guard_work/$guard.status")"
    last="$(tail -n 1 <<< "$out")"
    cases="$(grep '^FAIL - ' <<< "$out" | tr '\n' '|')"
    if [[ "$code" -ne 0 ]] || ! [[ "$last" =~ $COUNT_LINE ]]; then
      problems+=("$guard is not green against $claude_md: exit $code, last line '$last'${cases:+ — ${cases%|}}")
    fi
  done

  rm -rf "$guard_work"
}

name="the four suites that hold $claude_md are in \`make test\`'s roster and green against the committed document"
problems=()

probe_every_guard_is_rostered_and_green

report "$name"

finish
