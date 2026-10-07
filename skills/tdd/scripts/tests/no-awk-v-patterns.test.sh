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

PLANTED_FIXTURE="fixture text this suite writes into a scratch tree as the planted suite; it is scanned, never run, so no value ever reaches a -v binding"
CASE_NAME="a case name, a string this suite prints and never runs, so no value ever reaches a -v binding"
BRACKET_CLASSES="wait_ci_run and push_run spell every literal character as a bracket class, [$] [.], never with a backslash, so the -v value holds none to drop"
declare -A EXEMPT=(
  [no-awk-v-patterns.test.sh:110]="$PLANTED_FIXTURE"
  [no-awk-v-patterns.test.sh:111]="$PLANTED_FIXTURE"
  [no-awk-v-patterns.test.sh:125]="$PLANTED_FIXTURE"
  [no-awk-v-patterns.test.sh:196]="$PLANTED_FIXTURE"
  [no-awk-v-patterns.test.sh:200]="$CASE_NAME"
  [no-awk-v-patterns.test.sh:209]="$PLANTED_FIXTURE"
  [no-awk-v-patterns.test.sh:213]="$CASE_NAME"
  [no-awk-v-patterns.test.sh:222]="$PLANTED_FIXTURE"
  [no-awk-v-patterns.test.sh:226]="$CASE_NAME"
  [no-awk-v-patterns.test.sh:234]="$PLANTED_FIXTURE"
  [no-awk-v-patterns.test.sh:247]="$PLANTED_FIXTURE"
  [no-awk-v-patterns.test.sh:259]="$PLANTED_FIXTURE"
  [no-awk-v-patterns.test.sh:295]="$PLANTED_FIXTURE"
  [no-awk-v-patterns.test.sh:339]="$PLANTED_FIXTURE" [no-awk-v-patterns.test.sh:357]="$PLANTED_FIXTURE"
  [parallel-conductors.test.sh:950]="record is handed only '^3[.] [*][*]Parallel[*][*]' and '^[*][*]In flight[*][*]:', literal characters spelled as bracket classes, so the -v value holds no backslash to drop"
  [skill-draft-pr.test.sh:762]="$BRACKET_CLASSES"
  [skill-draft-pr.test.sh:778]="$BRACKET_CLASSES"
  [skill-draft-pr.test.sh:807]="$BRACKET_CLASSES"
  [skill-draft-pr.test.sh:853]="$BRACKET_CLASSES"
  [skill-plan-verify.test.sh:34]="every pattern its line_of is handed spells a literal character as a bracket class, [.] [(] [$] [<], never with a backslash, so the -v value holds none to drop"
  [skill-plan-verify.test.sh:48]="bullet_text is handed only exit2_re, '[(]exit 2[)]', a literal parenthesis spelled as a bracket class, so the -v value holds no backslash to drop"
  [skill-red-prediction.test.sh:25]="doc_text's from is handed only '### 🔴 Red' and 'red-divergence', plain text with no backslash to drop"
  [solvable-issues.test.sh:379]="loop_bullet is handed only '^- [*][*]Exit 3:', '^- [*][*]Exit 0:' and '^### ', literal characters spelled as bracket classes, so the -v value holds no backslash to drop"
)

source "$HERE/lib/harness.sh"
source "$HERE/lib/exemption-reasons.sh"

probe_no_suite_passes_a_pattern_through_awk_v() {
  local f name hit lineno text var rest prog quotes i
  local bind_re='-v[[:space:]]+([A-Za-z_][A-Za-z0-9_]*)='
  local -a lines
  for f in "$ROOT"/skills/tdd/scripts/tests/*.sh "$ROOT"/skills/tdd/scripts/tests/lib/*.sh; do [[ -f "$f" ]] || continue
    name="$(basename "$f")"
    mapfile -t lines < "$f"
    while IFS= read -r hit; do
      lineno="${hit%%:*}"
      text="${hit#*:}"
      [[ "$text" =~ ^[[:space:]]*# ]] && continue
      [[ -n "${EXEMPT[$name:$lineno]:-}" ]] && continue
      [[ "$text" == *"'"* ]] || continue
      prog="$text"
      quotes="$(sed "s/\"[^\"]*\"//g; s/[^']//g" <<< "$text")"
      i="$lineno"
      while (( ${#quotes} % 2 == 1 && i < ${#lines[@]} )); do
        prog+=$'\n'"${lines[i]}"
        quotes+="$(sed "s/'\\\\''//g; s/[^']//g" <<< "${lines[i]}")"
        (( i++ ))
      done
      rest="$text"
      while [[ "$rest" =~ $bind_re ]]; do
        var="${BASH_REMATCH[1]}"
        rest="${rest#*"${BASH_REMATCH[0]}"}"
        if [[ "$prog" =~ ~[[:space:]]*${var}([^A-Za-z0-9_]) \
          || "$prog" =~ match\([^,]*,[[:space:]]*${var}([^A-Za-z0-9_]) ]]; then
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
  probe_every_exemption_carries_a_reason
  probe_no_suite_passes_a_pattern_through_awk_v
}

scan_planted_text() {
  local planted
  IFS= read -r -d '' planted
  scan_planted "${planted%$'\n'}"
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

probe_a_planted_awk_v_pattern_exempted_with_no_reason() {
  local -A EXEMPT=([planted.test.sh:3]="")
  scan_planted '#!/usr/bin/env bash' 'numbered() {' "  awk -v re=\"\$1\" '\$0 ~ re { print }' \"\$2\"" '}'
  planted_reasonless_named="$(problem_naming "[planted.test.sh:3] carries no reason")"
}

name="an exemption-table entry for a planted awk -v re=\"\$1\" '\$0 ~ re' that carries no reason turns the guard red, naming the entry (#1037)"
planted_reasonless_named=""

probe_a_planted_awk_v_pattern_exempted_with_no_reason

expect_eq "$name" "named" "$planted_reasonless_named"

probe_a_planted_multi_line_awk_v_pattern() {
  scan_planted '#!/usr/bin/env bash' 'numbered() {' "  awk -v re=\"\$1\" '" \
    '    $0 ~ re { print }' "  ' \"\$2\"" '}'
  planted_multi_line_named="$(problem_naming "planted.test.sh:3")"
}

name="a planted multi-line awk program, -v re=\"\$1\" opening it on one line and \$0 ~ re on a later one, turns the guard red, naming the -v line as <suite>:<line> (#1037)"
planted_multi_line_named=""

probe_a_planted_multi_line_awk_v_pattern

expect_eq "$name" "named" "$planted_multi_line_named"

probe_a_planted_awk_v_program_left_open_at_eof() {
  scan_planted '#!/usr/bin/env bash' 'numbered() {' "  awk -v re=\"\$1\" '" '    $0 ~ re { print }'
  planted_open_at_eof_named="$(problem_naming "planted.test.sh:3")"
}

name="a planted awk -v re=\"\$1\" program whose single quote is never closed before the end of the file is still scanned to the end, naming the -v line as <suite>:<line> (#1037)"
planted_open_at_eof_named=""

probe_a_planted_awk_v_program_left_open_at_eof

expect_eq "$name" "named" "$planted_open_at_eof_named"

probe_a_planted_awk_v_with_a_quote_in_a_double_quoted_string() {
  scan_planted '#!/usr/bin/env bash' 'numbered() {' "  awk -v q=\"'\" -v re=\"\$1\" '" \
    '    $0 ~ re { print q }' "  ' \"\$2\"" '}'
  planted_dq_quote_named="$(problem_naming "planted.test.sh:3")"
}

name="a planted awk -v q=\"'\" -v re=\"\$1\" whose ' inside a double-quoted string comes before the single-quoted program, and whose program uses re on the right of ~, turns the guard red, naming <suite>:<line> (#1050)"
planted_dq_quote_named=""

probe_a_planted_awk_v_with_a_quote_in_a_double_quoted_string

expect_eq "$name" "named" "$planted_dq_quote_named"

probe_a_planted_awk_v_non_offender_with_a_quote_in_a_double_quoted_string() {
  scan_planted_text <<'EOF'
#!/usr/bin/env bash
numbered() {
  awk -v q="'" -v n="$1" '$0 ~ other { print q }' "$2"
}
later() {
  awk '$0 ~ n { print }' "$2"
}
EOF
  planted_dq_quote_non_offender_named="$(problem_naming "planted.test.sh:3")"
}

name="a planted awk whose -v line carries a ' inside a double-quoted string before a single-quoted program that never matches its -v variable leaves the guard green, even when a later awk line uses that name on the right of ~ (#1050)"
planted_dq_quote_non_offender_named=""

probe_a_planted_awk_v_non_offender_with_a_quote_in_a_double_quoted_string

expect_eq "$name" "not named" "$planted_dq_quote_non_offender_named"

probe_a_planted_multi_line_awk_v_with_an_escaped_quote() {
  scan_planted_text <<'EOF'
#!/usr/bin/env bash
numbered() {
  awk -v re="$1" '
    { s = "it'\''s" }
    $0 ~ re { print s }
  ' "$2"
}
EOF
  planted_escaped_quote_named="$(problem_naming "planted.test.sh:3")"
}

name="a planted multi-line awk -v re=\"\$1\" program with a '\\'' escape on a continuation line, and its -v variable on the right of ~ after that escape, turns the guard red, naming the -v line as <suite>:<line> (#1050)"
planted_escaped_quote_named=""

probe_a_planted_multi_line_awk_v_with_an_escaped_quote

expect_eq "$name" "named" "$planted_escaped_quote_named"

probe_a_planted_multi_line_awk_v_non_offender_with_an_escaped_quote() {
  scan_planted_text <<'EOF'
#!/usr/bin/env bash
numbered() {
  awk -v n="$1" '
    { s = "it'\''s" }
    $0 ~ other { print s }
  ' "$2"
}
later() {
  awk '$0 ~ n { print }' "$2"
}
EOF
  planted_escaped_quote_non_offender_named="$(problem_naming "planted.test.sh:3")"
}

name="a planted multi-line awk -v n=\"\$1\" program with a '\\'' escape on a continuation line that closes without matching n leaves the guard green, even when a later line outside that program uses n on the right of ~ (#1050)"
planted_escaped_quote_non_offender_named=""

probe_a_planted_multi_line_awk_v_non_offender_with_an_escaped_quote

expect_eq "$name" "not named" "$planted_escaped_quote_non_offender_named"

probe_a_planted_sourced_helper_awk_v_pattern() {
  local PLANT_REL='skills/tdd/scripts/tests/planted-helpers.sh'
  scan_planted_text <<'EOF'
#!/usr/bin/env bash
numbered() {
  awk -v re="$1" '$0 ~ re { print }' "$2"
}
EOF
  planted_helper_named="$(problem_naming "planted-helpers.sh:3")"
}

name="a planted sourced helper beside the suites, planted-helpers.sh, not a *.test.sh, passing awk -v re=\"\$1\" then using re on the right of ~ turns the guard red, naming <helper>:<line> (#1050)"
planted_helper_named=""

probe_a_planted_sourced_helper_awk_v_pattern

expect_eq "$name" "named" "$planted_helper_named"

probe_a_planted_lib_helper_awk_v_pattern() {
  local PLANT_REL='skills/tdd/scripts/tests/lib/planted-helpers.sh'
  scan_planted_text <<'EOF'
#!/usr/bin/env bash
numbered() {
  awk -v re="$1" '$0 ~ re { print }' "$2"
}
EOF
  planted_lib_helper_named="$(problem_naming "planted-helpers.sh:3")"
}

name="a planted sourced helper under tests/lib/, lib/planted-helpers.sh, passing awk -v re=\"\$1\" then using re on the right of ~ turns the guard red, naming <helper>:<line> (#1050)"
planted_lib_helper_named=""

probe_a_planted_lib_helper_awk_v_pattern

expect_eq "$name" "named" "$planted_lib_helper_named"

name="no suite under skills/tdd/scripts/tests/ passes awk a pattern through -v but where the exemption table says why its value can hold no backslash (#1037)"
problems=()

probe_every_exemption_carries_a_reason "an entry is an exemption only when it says why the value can hold no backslash"
probe_no_suite_passes_a_pattern_through_awk_v

report "$name"

finish
