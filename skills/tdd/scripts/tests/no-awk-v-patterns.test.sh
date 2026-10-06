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

declare -A EXEMPT=()

source "$HERE/lib/harness.sh"

probe_no_suite_passes_a_pattern_through_awk_v() {
  local f name hit lineno text var rest
  local bind_re='-v[[:space:]]+([A-Za-z_][A-Za-z0-9_]*)='
  for f in "$ROOT"/skills/tdd/scripts/tests/*.test.sh; do
    name="$(basename "$f")"
    while IFS= read -r hit; do
      lineno="${hit%%:*}"
      text="${hit#*:}"
      [[ "$text" =~ ^[[:space:]]*# ]] && continue
      [[ -n "${EXEMPT[$name:$lineno]:-}" ]] && continue
      [[ "$text" == *"'"* ]] || continue
      rest="$text"
      while [[ "$rest" =~ $bind_re ]]; do
        var="${BASH_REMATCH[1]}"
        rest="${rest#*"${BASH_REMATCH[0]}"}"
        if [[ "$text" =~ ~[[:space:]]*${var}([^A-Za-z0-9_]) \
          || "$text" =~ match\([^,]*,[[:space:]]*${var}([^A-Za-z0-9_]) ]]; then
          problems+=("$name:$lineno passes awk a pattern through -v, which drops its backslashes: $text")
          break
        fi
      done
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

scan_planted() {
  local ROOT
  ROOT="$(scratch_dir)"
  mkdir -p "$ROOT/${PLANT_REL%/*}"
  printf '%s\n' "$@" > "$ROOT/$PLANT_REL"
  problems=()
  probe_no_suite_passes_a_pattern_through_awk_v
}

probe_a_planted_awk_v_pattern() {
  scan_planted '#!/usr/bin/env bash' 'numbered() {' "  awk -v re=\"\$1\" '\$0 ~ re { print }' \"\$2\"" '}' \
    'starts() {' "  awk -v at=\"\$1\" 'match(\$0, at) { print NR }' \"\$2\"" '}'
  planted_tilde_named="$(problem_naming "planted.test.sh:3")"
  planted_match_named="$(problem_naming "planted.test.sh:6")"
}

name="a planted suite passing awk -v re=\"\$1\", then using re on the right of ~ or in match(, turns the guard red, naming <suite>:<line> (#1037)"
planted_tilde_named=""
planted_match_named=""

probe_a_planted_awk_v_pattern

expect_eq "$name" "named named" "$planted_tilde_named $planted_match_named"

probe_a_planted_comment_quoting_awk_v() {
  scan_planted '#!/usr/bin/env bash' "# awk -v re=\"\$1\" … \$0 ~ re"
  planted_comment_named="$(problem_naming "planted.test.sh:2")"
}

name="a planted suite whose comment line only quotes an awk -v pattern site leaves the guard green (#1037)"
planted_comment_named=""

probe_a_planted_comment_quoting_awk_v

expect_eq "$name" "not named" "$planted_comment_named"

probe_a_planted_awk_v_with_unquoted_program() {
  scan_planted '#!/usr/bin/env bash' 'numbered() {' "  awk -v re=\"\$1\" -f prog.awk \"\$2\"" \
    "  [[ \"\$2\" =~ \$re ]] && echo matched" '}'
  planted_unquoted_named="$(problem_naming "planted.test.sh:3")"
}

name="a planted awk -v re=\"\$1\" -f prog.awk with no single-quoted program leaves the guard green, even when a later quote-free line uses re on the right of =~ (#1037)"
planted_unquoted_named=""

probe_a_planted_awk_v_with_unquoted_program

expect_eq "$name" "not named" "$planted_unquoted_named"

probe_a_planted_awk_v_compared_or_indexed() {
  scan_planted '#!/usr/bin/env bash' 'equal() {' "  awk -v want=\"\$1\" '\$0 == want { print }' \"\$2\"" '}' \
    'holds() {' "  awk -v h=\"\$1\" 'index(\$0, h) { print NR }' \"\$2\"" '}'
  planted_equal_named="$(problem_naming "planted.test.sh:3")"
  planted_index_named="$(problem_naming "planted.test.sh:6")"
}

name="a planted awk -v whose variable is only compared with == or passed to index( leaves the guard green (#1037)"
planted_equal_named=""
planted_index_named=""

probe_a_planted_awk_v_compared_or_indexed

expect_eq "$name" "not named not named" "$planted_equal_named $planted_index_named"

probe_a_planted_awk_matching_no_v_bound_variable() {
  scan_planted '#!/usr/bin/env bash' 'dotted() {' "  awk '\$0 ~ /x\\./ { print }' \"\$1\"" '}' \
    'other() {' "  awk -v n=\"\$1\" '\$0 ~ other { print }' \"\$2\"" '}'
  planted_no_v_named="$(problem_naming "planted.test.sh:3")"
  planted_unmatched_v_named="$(problem_naming "planted.test.sh:6")"
}

name="a planted awk '\$0 ~ /x\\./' with no -v, and an awk -v n=\"\$1\" '\$0 ~ other' whose n is never matched, leave the guard green (#1037)"
planted_no_v_named=""
planted_unmatched_v_named=""

probe_a_planted_awk_matching_no_v_bound_variable

expect_eq "$name" "not named not named" "$planted_no_v_named $planted_unmatched_v_named"

probe_a_planted_awk_matching_a_longer_name() {
  scan_planted '#!/usr/bin/env bash' 'tilde() {' "  awk -v n=\"\$1\" '\$0 ~ name { print }' \"\$2\"" '}' \
    'starts() {' "  awk -v n=\"\$1\" 'match(\$0, name) { print NR }' \"\$2\"" '}'
  planted_longer_tilde_named="$(problem_naming "planted.test.sh:3")"
  planted_longer_match_named="$(problem_naming "planted.test.sh:6")"
}

name="a planted awk -v n=\"\$1\" whose program matches only a longer name, with ~ name or match(\$0, name), leaves the guard green (#1037)"
planted_longer_tilde_named=""
planted_longer_match_named=""

probe_a_planted_awk_matching_a_longer_name

expect_eq "$name" "not named not named" "$planted_longer_tilde_named $planted_longer_match_named"

probe_a_planted_awk_binding_two_v_variables() {
  scan_planted '#!/usr/bin/env bash' 'second() {' \
    "  awk -v a=\"\$x\" -v re=\"\$1\" '\$0 ~ re { print }' \"\$2\"" '}'
  planted_second_v_named="$(problem_naming "planted.test.sh:3")"
}

name="a planted awk -v a=\"\$x\" -v re=\"\$1\" '\$0 ~ re', whose second -v variable is the pattern, turns the guard red, naming <suite>:<line> (#1037)"
planted_second_v_named=""

probe_a_planted_awk_binding_two_v_variables

expect_eq "$name" "named" "$planted_second_v_named"

probe_a_planted_awk_v_pattern_exempted_with_a_reason() {
  local -A EXEMPT=([planted.test.sh:3]="the planted site's pattern carries no backslash")
  scan_planted '#!/usr/bin/env bash' 'numbered() {' "  awk -v re=\"\$1\" '\$0 ~ re { print }' \"\$2\"" '}'
  planted_exempted_named="$(problem_naming "planted.test.sh:3")"
}

name="a planted awk -v re=\"\$1\" '\$0 ~ re' that the exemption table lists with a reason leaves the guard green (#1037)"
planted_exempted_named=""

probe_a_planted_awk_v_pattern_exempted_with_a_reason

expect_eq "$name" "not named" "$planted_exempted_named"

finish
