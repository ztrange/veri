#!/usr/bin/env bash
# Unit tests for the suites under skills/tdd/scripts/tests/ — none of them may hand awk a
# pattern through `-v`, which processes the value's escape sequences and drops a `\.`'s backslash.
#
# Contract under test:
#   No suite under skills/tdd/scripts/tests/ passes `awk -v <name>="$…"` where <name> is later
#   used on the right of `~` or in `match(`. An offender is reported as `<suite>:<line>`.
#
# Run: skills/tdd/scripts/tests/no-awk-v-patterns.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"

source "$HERE/lib/harness.sh"

probe_no_suite_passes_a_pattern_through_awk_v() {
  local f name hit lineno text
  for f in "$ROOT"/skills/tdd/scripts/tests/*.test.sh; do
    name="$(basename "$f")"
    while IFS= read -r hit; do
      lineno="${hit%%:*}"
      text="${hit#*:}"
      problems+=("$name:$lineno passes awk a pattern through -v, which drops its backslashes: $text")
    done < <(grep -n 'awk' "$f")
  done
  return 0
}

PLANT_REL='skills/tdd/scripts/tests/planted.test.sh'

problem_naming() {
  local text="$1" problem
  for problem in ${problems+"${problems[@]}"}; do
    [[ "$problem" == *"$text" || "$problem" == *"$text"[!0-9]* ]] && { printf named; return; }
  done
  printf 'not named'
}

plant() {
  local rel="$1"
  shift
  ROOT="$(scratch_dir)"
  mkdir -p "$ROOT/${rel%/*}"
  printf '%s\n' "$@" > "$ROOT/$rel"
  problems=()
}

probe_a_planted_awk_v_pattern() {
  local ROOT
  plant "$PLANT_REL" '#!/usr/bin/env bash' 'numbered() {' "  awk -v re=\"\$1\" '\$0 ~ re { print }' \"\$2\"" '}' \
    'starts() {' "  awk -v at=\"\$1\" 'match(\$0, at) { print NR }' \"\$2\"" '}'
  probe_no_suite_passes_a_pattern_through_awk_v
  planted_tilde_named="$(problem_naming "planted.test.sh:3")"
  planted_match_named="$(problem_naming "planted.test.sh:6")"
}

name="a planted suite passing awk -v re=\"\$1\", then using re on the right of ~ or in match(, turns the guard red, naming <suite>:<line> (#1037)"
planted_tilde_named=""
planted_match_named=""

probe_a_planted_awk_v_pattern

expect_eq "$name" "named named" "$planted_tilde_named $planted_match_named"

finish
