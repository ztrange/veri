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

finish
