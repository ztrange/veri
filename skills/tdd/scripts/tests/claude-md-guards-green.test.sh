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

plant_roster_without() {
  local tree="$1" missing="$2" guard
  {
    echo 'test:'
    for guard in "${GUARDS[@]}"; do
      [[ "$guard" == "$missing" ]] || printf '\t./%s/%s\n' "$suites_dir" "$guard"
    done
  } > "$tree/Makefile"
}

probe_names_each_guard_missing_from_a_planted_roster() {
  local real_root="$ROOT" real_here="$HERE" stubs tree missing guard raised found
  local unnamed=()
  stubs="$(scratch_dir)"
  for guard in "${GUARDS[@]}"; do
    printf '#!/bin/sh\necho "----"\necho "1 passed, 0 failed"\n' > "$stubs/$guard"
    chmod 755 "$stubs/$guard"
  done

  for missing in "${GUARDS[@]}"; do
    tree="$(scratch_dir)"
    plant_roster_without "$tree" "$missing"
    problems=()
    ROOT="$tree" HERE="$stubs"
    probe_every_guard_is_rostered_and_green
    ROOT="$real_root" HERE="$real_here"
    found=0
    for raised in ${problems+"${problems[@]}"}; do
      [[ "$raised" == *"$suites_dir/$missing is not in the roster"* ]] && found=1
    done
    if [[ "$found" -eq 0 ]]; then
      raised="$(IFS='|'; echo "${problems[*]-}")"
      unnamed+=("with $missing left out of a planted \`make -n test\` roster, the probe raised no problem naming it; it raised: ${raised:-nothing}")
    fi
  done
  problems=(${unnamed+"${unnamed[@]}"})
}

name="with a planted \`make -n test\` roster lacking any one of the four guards, the probe fails naming that guard"
problems=()

probe_names_each_guard_missing_from_a_planted_roster

report "$name"


probe_fails_when_a_planted_roster_names_no_suite() {
  local real_root="$ROOT" real_here="$HERE" stubs tree guard raised found=0
  stubs="$(scratch_dir)"
  for guard in "${GUARDS[@]}"; do
    printf '#!/bin/sh\necho "----"\necho "1 passed, 0 failed"\n' > "$stubs/$guard"
    chmod 755 "$stubs/$guard"
  done

  tree="$(scratch_dir)"
  printf 'test:\n\t@echo no suites here\n' > "$tree/Makefile"
  problems=()
  ROOT="$tree" HERE="$stubs"
  probe_every_guard_is_rostered_and_green
  ROOT="$real_root" HERE="$real_here"
  for raised in ${problems+"${problems[@]}"}; do
    [[ "$raised" == *"\`make -n test\` named no suite in $suites_dir"* ]] && found=1
  done
  raised="$(IFS='|'; echo "${problems[*]-}")"
  problems=()
  if [[ "$found" -eq 0 ]]; then
    problems+=("with a planted \`make -n test\` naming no suite, the probe raised no problem saying so; it raised: ${raised:-nothing}")
  fi
}

name="with a planted \`make -n test\` that names no suite at all, the probe fails saying the roster could not be read"
problems=()

probe_fails_when_a_planted_roster_names_no_suite

report "$name"

finish
