#!/usr/bin/env bash
# Unit test for the four suites that hold CLAUDE.md to what it says:
#
#   claude-md-counts.test.sh     the script and suite counts the document states
#   lane-rule-recorded.test.sh   the two-lane rule in "The one trap"
#   count-line-guard.test.sh     the "Testing idiom" count-line rule
#   docs-targets-refuse.test.sh  the development-run refusal
#
# Contract under test:
#   Each of those four is a suite `make test` runs, and each exits 0 with a count line
#   reporting no failures when run against the CLAUDE.md committed in this tree.
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

  guard_work="$(scratch_dir)"

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
