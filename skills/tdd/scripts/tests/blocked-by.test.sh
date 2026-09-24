#!/usr/bin/env bash
# Unit tests for scripts/lib/blocked_by.py — the one reading of an issue body's `## Blocked by`
# section, importable by any caller rather than locked inside solvable-issues.sh's heredoc.
#
# Why this exists (issue #460): the parsing lived only in solvable-issues.sh's embedded Python,
# so a second reader (#271's `workqueue.sh next`) had to copy it, and a copy that reads a
# reference differently disagrees with solvable-issues.sh about which issues are takeable.
#
# Contract under test:
#   lib/blocked_by.py   blockers(<body>, <repo slug>) → the issue numbers named under
#                       `## Blocked by`, as `#<n>` or as https://github.com/<slug>/issues/<n>
#
# Run: scripts/tests/blocked-by.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
LIB="$HERE/../lib"
pass=0 fail=0

# check <name> <expected> <actual>
check() {
  if [[ "$2" == "$3" ]]; then
    pass=$((pass + 1))
  else
    fail=$((fail + 1))
    echo "FAIL - $1"
    diff <(printf '%s\n' "$2") <(printf '%s\n' "$3") | sed 's/^/    /'
  fi
}

# blockers <repo slug> — the module's answer for the body on stdin, as a Python list literal.
blockers() {
  python3 -c '
import sys
sys.path.insert(0, sys.argv[1])
from blocked_by import blockers
print(blockers(sys.stdin.read(), sys.argv[2]))
' "$LIB" "$1" 2>&1
}

# 1. Both reference forms: a `#<n>` and the full URL GitHub renders for this repository.
body='## Problem

Something.

## Blocked by

- #12
- https://github.com/acme/widgets/issues/34
'
check "blocked_by.blockers reads both the #<n> form and the full https://github.com/<owner>/<name>/issues/<n> URL of the given repository" \
  "[12, 34]" "$(printf '%s' "$body" | blockers acme/widgets)"

# 2. No blockers: a section reading `None.`, and a body with no `## Blocked by` section at all.
none_body='## Problem

Something about #7.

## Blocked by

None.
'
absent_body='## Problem

Something about #7.

## Acceptance criteria

1. Works.
'
check "blocked_by.blockers returns no blockers for a section reading None. and for a body with no ## Blocked by section" \
  "[]
[]" "$(printf '%s' "$none_body" | blockers acme/widgets; printf '%s' "$absent_body" | blockers acme/widgets)"

# 3. The slug decides which URLs are local: given one, another repository's issue #56 is not a
#    blocker; given none (the empty slug solvable-issues.sh passes without --repo), every
#    github.com issue URL is read as local.
mixed_body='## Blocked by

- #1
- https://github.com/other/project/issues/56
- https://github.com/acme/widgets/issues/34
'
check "blocked_by.blockers ignores another repository's issue URL when a slug is given, and reads any github.com issue URL as local when none is" \
  "[1, 34]
[1, 56, 34]" "$(printf '%s' "$mixed_body" | blockers acme/widgets; printf '%s' "$mixed_body" | blockers '')"

echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
