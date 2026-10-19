#!/usr/bin/env bash
# Unit tests for scripts/push-branch.sh — the push the conductor makes after each step's
# green commit and after each verify-refactor PASS clears the mark.
#
# Contract under test:
#   push-branch.sh, run from the worktree with an origin that cannot be reached
#                       → exit 0, the exit status the conductor branches on.
#                       → HEAD, the commit count and the ledger file are exactly what they
#                         were before the call.
#                       → one line appended to `.tdd/events.jsonl` whose `event` says the
#                         push failed.
#   push-branch.sh, run from the worktree with an origin it can reach
#                       → the run's branch is on that remote, at the commit HEAD is on.
#
# Run: scripts/tests/push-branch.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/lib/harness.sh"
PUSH="$HERE/../push-branch.sh"
work="$(scratch_dir)"

unchanged() {
  local label="$1" before="$2" after="$3"
  [[ "$after" == "$before" ]] ||
    problems+=("$label: want it unchanged at $(printf '%q' "$before"), got $(printf '%q' "$after")")
}

run_fixture() {
  local repo="$1" branch="$2" issue="$3"
  mkdir -p "$repo/.tdd"
  new_repo -b main "$repo" >/dev/null 2>&1
  git_q "$repo" commit -q --allow-empty -m "initial" >/dev/null 2>&1
  git_q "$repo" checkout -q -b "$branch" >/dev/null 2>&1
  cat > "$repo/.tdd/issue-$issue.md"
  git_q "$repo" add -A >/dev/null 2>&1
  git_q "$repo" commit -q -m "feat: a step's green commit (#$issue)" >/dev/null 2>&1
}

git_q() { local repo="$1"; shift; git -C "$repo" -c user.name=veri -c user.email=veri@example.test "$@"; }

remote_at() { git_q "$1" rev-parse --verify -q "refs/heads/$2" 2>/dev/null || echo '<<absent>>'; }

push_counting_git() {
  local stubdir="$1" calls="$2"
  mkdir -p "$stubdir"
  : > "$calls"
  cat > "$stubdir/git" <<STUB
for a in "\$@"; do
  if [ "\$a" = push ]; then echo push >> "$calls"; break; fi
done
exec "$(command -v git)" "\$@"
STUB
  chmod +x "$stubdir/git"
}

jevents() {
  python3 -c '
import sys, json
for line in open(sys.argv[1]).read().splitlines():
    try:
        obj = json.loads(line)
    except Exception:
        print("<<unparseable>>")
        continue
    print(obj.get("event", "<<missing>>") if isinstance(obj, dict) else "<<unparseable>>")
' "$1" 2>/dev/null
}


finish
