#!/usr/bin/env bash
# Unit tests for the suites under skills/tdd/scripts/tests/ — none of them may force a read or
# write failure through permission bits, which uid 0 ignores.
#
# Contract under test:
#   No suite under skills/tdd/scripts/tests/ takes read or write permission away from a path
#   with chmod, outside a comment. An offender is reported as `<suite>:<line>`.
#
# Run: skills/tdd/scripts/tests/no-permission-bits.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"

SUBJECT='skills/tdd/scripts/tests'

CHMOD_WORD='(^|[^[:alnum:]_.-])chmod'
REVOKING_MODE='(000|a-r|u-w|-w)'
CHMOD_FLAGS='([[:space:]]+-[RHLPfhv]+)*'
SHELL_CHMOD="$CHMOD_WORD$CHMOD_FLAGS[[:space:]]+$REVOKING_MODE([[:space:]]|$)"
PATH_CHMOD='\.chmod\(0o000\)'
PERMISSION_BIT_CHMOD="$SHELL_CHMOD|$PATH_CHMOD"


source "$HERE/lib/harness.sh"

flat() { local s="$1"; printf '%s' "${s//$'\n'/\/}"; }

split_site() {
  local rest
  site_file="${1%%:*}"
  rest="${1#*:}"
  site_line="${rest%%:*}"
  site_text="${rest#*:}"
}

chmod_lines() {
  local hit
  while IFS= read -r hit; do
    split_site "$hit"
    [[ "$site_text" =~ ^[[:space:]]*# ]] && continue
    printf '%s\n' "$hit"
  done < <(cd "$ROOT" && grep -rInE -- "$PERMISSION_BIT_CHMOD" "$SUBJECT")
  return 0
}

probe_no_suite_revokes_permission_bits() {
  local site
  while IFS= read -r site; do
    split_site "$site"
    problems+=("$site_file:$site_line forces a read or write failure through permission bits, which uid 0 ignores, so the failure never happens where veri runs as root: $(flat "$site_text")")
  done < <(chmod_lines)
  return 0
}


name="no suite under skills/tdd/scripts/tests/ forces a read or write failure through permission bits (#846)"
problems=()

probe_no_suite_revokes_permission_bits

report "$name"

PLANT_REL='skills/tdd/scripts/tests/planted.test.sh'

plant_named() {
  local rel="$1" plant="$2" line problem
  line="$(grep -nxF -- "$plant" "$ROOT/$rel")"
  line="${line%%:*}"
  for problem in ${problems+"${problems[@]}"}; do
    [[ "$problem" == "$rel:$line forces a read or write failure through permission bits"* ]] && { printf named; return; }
  done
  printf 'not named'
}
PLANT_CHMOD_000="chmod $(printf '%03d' 0) \"\$ledger\""

probe_a_planted_chmod_000() {
  local ROOT
  ROOT="$(scratch_dir)"
  mkdir -p "$ROOT/${PLANT_REL%/*}"
  printf '%s\n' '#!/usr/bin/env bash' 'ledger="$(mktemp)"' "$PLANT_CHMOD_000" > "$ROOT/$PLANT_REL"
  problems=()
  probe_no_suite_revokes_permission_bits
  planted_chmod_000_named="$(plant_named "$PLANT_REL" "$PLANT_CHMOD_000")"
  problems=()
}

name="a planted suite line starting with a chmod to mode zero, then a path, turns the guard red, naming <suite>:<line> (#846)"
planted_chmod_000_named=""

probe_a_planted_chmod_000

expect_eq "$name" "named" "$planted_chmod_000_named"

PLANT_REVOKING_MODES=(a-r u-w -w)

probe_planted_revoking_modes() {
  local ROOT mode
  ROOT="$(scratch_dir)"
  mkdir -p "$ROOT/${PLANT_REL%/*}"
  printf '%s\n' '#!/usr/bin/env bash' 'ledger="$(mktemp)"' > "$ROOT/$PLANT_REL"
  for mode in "${PLANT_REVOKING_MODES[@]}"; do
    printf '%s\n' "chmod $mode \"\$ledger\"" >> "$ROOT/$PLANT_REL"
  done
  problems=()
  probe_no_suite_revokes_permission_bits
  planted_revoking_modes_named=""
  for mode in "${PLANT_REVOKING_MODES[@]}"; do
    planted_revoking_modes_named+="$mode $(plant_named "$PLANT_REL" "chmod $mode \"\$ledger\"");"
  done
  problems=()
}

name="planted suite lines running a chmod to a-r, u-w and -w, then a path, each turn the guard red, naming its own <suite>:<line> (#846)"
planted_revoking_modes_named=""

probe_planted_revoking_modes

expect_eq "$name" "a-r named;u-w named;-w named;" "$planted_revoking_modes_named"

PLANT_SEPARATORS=(';' '&&' '||' '|' '(' '{' 'then' 'do')
PLANT_SEPARATOR_LINES=(
  "true; $PLANT_CHMOD_000"
  "true && $PLANT_CHMOD_000"
  "false || $PLANT_CHMOD_000"
  "true | $PLANT_CHMOD_000"
  "($PLANT_CHMOD_000)"
  "{ $PLANT_CHMOD_000; }"
  "if true; then $PLANT_CHMOD_000; fi"
  "for f in x; do $PLANT_CHMOD_000; done"
)

probe_planted_chmods_after_a_separator() {
  local ROOT i
  ROOT="$(scratch_dir)"
  mkdir -p "$ROOT/${PLANT_REL%/*}"
  printf '%s\n' '#!/usr/bin/env bash' 'ledger="$(mktemp)"' "${PLANT_SEPARATOR_LINES[@]}" > "$ROOT/$PLANT_REL"
  problems=()
  probe_no_suite_revokes_permission_bits
  planted_separators_named=""
  for i in "${!PLANT_SEPARATORS[@]}"; do
    planted_separators_named+="${PLANT_SEPARATORS[$i]} $(plant_named "$PLANT_REL" "${PLANT_SEPARATOR_LINES[$i]}");"
  done
  problems=()
}

name="a planted chmod to mode zero after ;, &&, ||, |, (, {, then or do on the same line turns the guard red, naming its <suite>:<line> (#846)"
planted_separators_named=""

probe_planted_chmods_after_a_separator

expect_eq "$name" "; named;&& named;|| named;| named;( named;{ named;then named;do named;" "$planted_separators_named"

PLANT_CHMOD_FLAGGED="chmod -R $(printf '%03d' 0) \"\$dir\""

probe_a_planted_chmod_with_a_flag() {
  local ROOT
  ROOT="$(scratch_dir)"
  mkdir -p "$ROOT/${PLANT_REL%/*}"
  printf '%s\n' '#!/usr/bin/env bash' 'dir="$(mktemp)"' "$PLANT_CHMOD_FLAGGED" > "$ROOT/$PLANT_REL"
  problems=()
  probe_no_suite_revokes_permission_bits
  planted_chmod_flagged_named="$(plant_named "$PLANT_REL" "$PLANT_CHMOD_FLAGGED")"
  problems=()
}

name="a planted chmod -R to mode zero, an option flag before its mode, turns the guard red, naming <suite>:<line> (#846)"
planted_chmod_flagged_named=""

probe_a_planted_chmod_with_a_flag

expect_eq "$name" "named" "$planted_chmod_flagged_named"

PLANT_PY_REL='skills/tdd/scripts/tests/py/test_planted.py'
PLANT_PY_CHMOD="    ledger.chmod(0o$(printf '%03d' 0))"

probe_a_planted_pytest_chmod_000() {
  local ROOT
  ROOT="$(scratch_dir)"
  mkdir -p "$ROOT/${PLANT_PY_REL%/*}"
  printf '%s\n' 'def test_unreadable_ledger(tmp_path):' '    ledger = tmp_path / "issue-9.md"' "$PLANT_PY_CHMOD" > "$ROOT/$PLANT_PY_REL"
  problems=()
  probe_no_suite_revokes_permission_bits
  planted_pytest_chmod_named="$(plant_named "$PLANT_PY_REL" "$PLANT_PY_CHMOD")"
  problems=()
}

name="a planted pytest suite that chmods a path to mode 000 turns the guard red, naming <suite>:<line> (#846)"
planted_pytest_chmod_named=""

probe_a_planted_pytest_chmod_000

expect_eq "$name" "named" "$planted_pytest_chmod_named"

finish
