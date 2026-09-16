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
# The suite sits at skills/<skill>/scripts/tests, so four levels up is the repo root.
ROOT="$(cd "$HERE/../../../.." && pwd)"

# The document, named for the failure messages only: this suite never opens it. What it
# asks is whether the four suites that do open it are content with what is in there.
claude_md="CLAUDE.md"

# This directory, repo-relative — the spelling `make test`'s roster uses and the one the
# failure messages have to, so a message can never name a path the roster was not read for.
suites_dir="skills/tdd/scripts/tests"

# The four, in the order #202 lists them. A guard is added to this issue's acceptance test
# by being added here.
GUARDS=(
  claude-md-counts.test.sh
  lane-rule-recorded.test.sh
  count-line-guard.test.sh
  docs-targets-refuse.test.sh
)

# The line every suite prints last, as an ERE, with the failure count pinned to zero: the
# Makefile asks each suite for the same line because an exit code alone is not trusted
# (#157), and a suite that stopped asserting halfway comes back 0 without one.
COUNT_LINE='^[0-9]+ passed, 0 failed$'

pass=0 fail=0

# report <name> — close a case whose probes collected into the `problems` array: an empty
# array is a pass, otherwise one FAIL line for the case and one indented line per problem,
# so the output says which guard is not green rather than just that one is not.
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

# roster — the suites `make test` would run, one path per line, asked of make itself with
# `-n` rather than re-globbed here. A glob spelled in this file would agree with the recipe
# by coincidence; what the criterion is about is the command the conductor types.
roster() {
  make -C "$ROOT" -n test 2>/dev/null | grep -oE "$suites_dir/[A-Za-z0-9_.-]*\.test\.sh"
}

# probe_every_guard_is_rostered_and_green — the four against the roster and against the
# document, in one sweep. The roster is read once for all four: it is a fact about the
# baseline, not about any one guard, so a roster that could not be read is said once and
# the membership question is then not asked at all, rather than answered "missing" four
# times for a reason that is about this probe.
probe_every_guard_is_rostered_and_green() {
  local rost guard out code last cases
  rost="$(roster)"

  if [[ -z "$rost" ]]; then
    # Fail closed: with no roster read, every membership question below would answer
    # "missing" for a reason that is about this probe rather than about the tree.
    problems+=("\`make -n test\` named no suite in $suites_dir, so the roster a green run covers could not be read")
  fi

  for guard in "${GUARDS[@]}"; do
    if [[ -n "$rost" ]] && ! grep -qxF "$suites_dir/$guard" <<< "$rost"; then
      problems+=("$suites_dir/$guard is not in the roster \`make test\` runs, so a green baseline says nothing about it")
    fi

    out="$("$HERE/$guard" 2>&1)" && code=0 || code=$?
    last="$(tail -n 1 <<< "$out")"
    # The suite's own FAIL lines, joined onto one line with `|`, so the message says which
    # claim about the document the guard withheld rather than only that it withheld one.
    cases="$(grep '^FAIL - ' <<< "$out" | tr '\n' '|')"
    if [[ "$code" -ne 0 ]] || ! [[ "$last" =~ $COUNT_LINE ]]; then
      problems+=("$guard is not green against $claude_md: exit $code, last line '$last'${cases:+ — ${cases%|}}")
    fi
  done
}

# 1. One criterion, one case: the four guards #202 names as its acceptance test are all in
#    the baseline's roster and all green against the committed document. One case rather
#    than one per guard, because what an accepted trim needs is not four verdicts but one —
#    and the problem lines say which guard withheld it.
name="the four suites that hold $claude_md are in \`make test\`'s roster and green against the committed document"
problems=()

probe_every_guard_is_rostered_and_green

report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
