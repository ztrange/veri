#!/usr/bin/env bash
# Sourced by suites: commit_suffix_offenders prints one line per develop-*.md in <dir> that asks
# for a commit without stating the `(#<issue>)` subject suffix; returns 1 when it printed any.
# Usage: source "$HERE/lib/commit-suffix.sh"; commit_suffix_offenders <dir>

commit_suffix_offenders() {
  local file rc=0
  for file in "$1"/develop-*.md; do
    [[ -f "$file" ]] || continue
    grep -iE '(^|[^[:alpha:]])commit (it|that|the|these|everything|each|this|your)([^[:alpha:]]|$)' "$file" > /dev/null || continue
    grep -F '(#<issue>)' "$file" > /dev/null && continue
    printf '%s: asks for a commit without stating the (#<issue>) subject suffix\n' "$file"
    rc=1
  done
  return "$rc"
}
