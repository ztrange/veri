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
source "$HERE/lib/harness.sh"

check() {
  if [[ "$2" == "$3" ]]; then
    pass=$((pass + 1))
  else
    fail=$((fail + 1))
    echo "FAIL - $1"
    diff <(printf '%s\n' "$2") <(printf '%s\n' "$3") | sed 's/^/    /'
  fi
}

blockers() {
  python3 -c '
import sys
sys.path.insert(0, sys.argv[1])
from blocked_by import blockers
print(blockers(sys.stdin.read(), sys.argv[2]))
' "$LIB" "$1" 2>&1
}

body='## Problem

Something.

## Blocked by

- #12
- https://github.com/acme/widgets/issues/34
'
check "blocked_by.blockers reads both the #<n> form and the full https://github.com/<owner>/<name>/issues/<n> URL of the given repository" \
  "[12, 34]" "$(printf '%s' "$body" | blockers acme/widgets)"

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

mixed_body='## Blocked by

- #1
- https://github.com/other/project/issues/56
- https://github.com/acme/widgets/issues/34
'
check "blocked_by.blockers ignores another repository's issue URL when a slug is given, and reads any github.com issue URL as local when none is" \
  "[1, 34]
[1, 56, 34]" "$(printf '%s' "$mixed_body" | blockers acme/widgets; printf '%s' "$mixed_body" | blockers '')"

later_body='## Blocked by

- #3

## Notes

See #9.
'
check "blocked_by.blockers stops reading the section at the next ## heading, so a #<n> under a later heading is not a blocker" \
  "[3]" "$(printf '%s' "$later_body" | blockers acme/widgets)"

scratch="$(mktemp -d)"
mkdir -p "$scratch/scripts" "$scratch/gh" "$scratch/cwd"
cp "$HERE/../solvable-issues.sh" "$scratch/scripts/"
cp -R "$LIB" "$scratch/scripts/lib"
rm -rf "$scratch/scripts/lib/__pycache__"
printf 'def blockers(*args, **kwargs):\n    return [99]\n' > "$scratch/scripts/lib/blocked_by.py"
printf '[]\n' > "$scratch/gh/prs.json"
cat > "$scratch/gh/issues.json" <<'JSON'
[
  {"number": 5, "title": "takeable", "state": "OPEN",
   "labels": [{"name": "ready-for-agent"}], "body": "## Blocked by\n\nNone.\n"},
  {"number": 99, "title": "the planted blocker", "state": "OPEN",
   "labels": [], "body": "## Blocked by\n\nNone.\n"}
]
JSON
planted_out="$(cd "$scratch/cwd" && env -u VERI_LABEL -u VERI_PRIORITY_LABEL \
  VERI_GH_JSON="$scratch/gh" PYTHONDONTWRITEBYTECODE=1 \
  "$scratch/scripts/solvable-issues.sh" 2>/dev/null)" && planted_code=0 || planted_code=$?
rm -rf "$scratch"
check "solvable-issues.sh takes its blocker parsing from the blocked-by module rather than defining its own" \
  "code=3 out=" "code=$planted_code out=$planted_out"

scratch="$(mktemp -d)"
py="$(command -v python3)"
inproc_out="$(cd "$scratch" && env PATH=/nonexistent GIT_CEILING_DIRECTORIES="$scratch" \
  PYTHONDONTWRITEBYTECODE=1 "$py" -c '
import os, subprocess, sys
spawned = []
def spy(name):
    def trap(*args, **kwargs):
        spawned.append(name)
        raise RuntimeError("child process started via " + name)
    return trap
subprocess.Popen.__init__ = spy("subprocess.Popen")
for name in ("system", "popen", "fork", "forkpty", "posix_spawn", "posix_spawnp",
             "execv", "execve", "execvp", "execvpe", "spawnv", "spawnve", "spawnvp", "spawnvpe"):
    if hasattr(os, name):
        setattr(os, name, spy("os." + name))
sys.path.insert(0, sys.argv[1])
from blocked_by import blockers
for body, slug in zip(sys.argv[2::2], sys.argv[3::2]):
    try:
        print(blockers(body, slug))
    except Exception as e:
        print("raised:", e)
print("spawned=%s" % spawned)
' "$LIB" "$body" acme/widgets "$none_body" acme/widgets "$absent_body" acme/widgets \
  "$mixed_body" acme/widgets "$mixed_body" '' "$later_body" acme/widgets 2>&1)"
rm -rf "$scratch"
check "a caller that is not solvable-issues.sh imports the blocked-by module and gets its answers with no gh, no repository and no child process started" \
  "[12, 34]
[]
[]
[1, 34]
[1, 56, 34]
[3]
spawned=[]" "$inproc_out"

finish
