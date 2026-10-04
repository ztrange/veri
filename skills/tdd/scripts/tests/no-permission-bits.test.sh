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
PERMISSION_BIT_CHMOD="$CHMOD_WORD[[:space:]]+$REVOKING_MODE([[:space:]]|$)"


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
PLANT_CHMOD_000="chmod $(printf '%03d' 0) \"\$ledger\""

probe_a_planted_chmod_000() {
  local ROOT line problem
  ROOT="$(scratch_dir)"
  mkdir -p "$ROOT/${PLANT_REL%/*}"
  printf '%s\n' '#!/usr/bin/env bash' 'ledger="$(mktemp)"' "$PLANT_CHMOD_000" > "$ROOT/$PLANT_REL"
  line="$(grep -nxF -- "$PLANT_CHMOD_000" "$ROOT/$PLANT_REL")"
  line="${line%%:*}"
  problems=()
  probe_no_suite_revokes_permission_bits
  planted_chmod_000_named="not named"
  for problem in ${problems+"${problems[@]}"}; do
    [[ "$problem" == "$PLANT_REL:$line forces a read or write failure through permission bits"* ]] && planted_chmod_000_named="named"
  done
  problems=()
}

name="a planted suite line starting with a chmod to mode zero, then a path, turns the guard red, naming <suite>:<line> (#846)"
planted_chmod_000_named=""

probe_a_planted_chmod_000

expect_eq "$name" "named" "$planted_chmod_000_named"

PLANT_REVOKING_MODES=(a-r u-w -w)

probe_planted_revoking_modes() {
  local ROOT mode plant line problem named
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
    plant="chmod $mode \"\$ledger\""
    line="$(grep -nxF -- "$plant" "$ROOT/$PLANT_REL")"
    line="${line%%:*}"
    named="not named"
    for problem in ${problems+"${problems[@]}"}; do
      [[ "$problem" == "$PLANT_REL:$line forces a read or write failure through permission bits"* ]] && named="named"
    done
    planted_revoking_modes_named+="$mode $named;"
  done
  problems=()
}

name="planted suite lines running a chmod to a-r, u-w and -w, then a path, each turn the guard red, naming its own <suite>:<line> (#846)"
planted_revoking_modes_named=""

probe_planted_revoking_modes

expect_eq "$name" "a-r named;u-w named;-w named;" "$planted_revoking_modes_named"

finish
