#!/usr/bin/env bash
# lib/preserve.sh — sourced, not run: defines `preserve_attempt`.
#
# preserve_attempt <who> <issue> <step> <phase> <attempt> <mark> — run preserve-attempt.sh,
# which sits one directory above this file, with its stdout sent to stderr; on its failure
# print `<who>: could not preserve …` on stderr. Always returns 0.
preserve_attempt() {
  local who="$1" issue="$2" step="$3" phase="$4" attempt="$5" mark="$6"
  local here
  here="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
  "$here/preserve-attempt.sh" "$issue" "$step" "$phase" "$attempt" "$mark" >&2 \
    || echo "$who: could not preserve the $mark attempt (issue $issue step $step $phase attempt $attempt)" >&2
  return 0
}
