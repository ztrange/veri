#!/usr/bin/env bash
# Tests for scripts/workqueue.sh — the only writer of `.tdd/workqueue`, the file that assigns
# issues to named workers and records what happened to each (issue #271).
#
# Contract under test:
#   workqueue.sh assign <worker> <issue>...  → appends one `<worker>\t<issue>\tqueued\t` line
#                                              per issue to `.tdd/workqueue` in the main
#                                              working tree, in the order given
#
# Run: scripts/tests/workqueue.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
SCRIPT="$HERE/../workqueue.sh"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
pass=0 fail=0

# new_repo <dir> — a repository with one commit, so the script has a main working tree to
# resolve and nothing in `.tdd/` yet.
new_repo() {
  git init -q -b main "$1" >/dev/null 2>&1
  git -C "$1" -c user.name=veri -c user.email=veri@example.test \
    commit -q --allow-empty -m initial >/dev/null 2>&1
}

# 1. assign appends one queued line per issue, in the order given.
repo="$work/assign-order"
new_repo "$repo"
out="$(cd "$repo" && "$SCRIPT" assign alpha 12 7 30 2>&1)" && code=0 || code=$?
want="$(printf 'alpha\t12\tqueued\t\nalpha\t7\tqueued\t\nalpha\t30\tqueued\t')"
got="$(cat "$repo/.tdd/workqueue" 2>/dev/null || printf '<no .tdd/workqueue>')"
if [[ "$code" -eq 0 && "$got" == "$want" ]]; then
  pass=$((pass + 1))
else
  fail=$((fail + 1))
  echo "FAIL - assign appends one queued line per issue, in the order given"
  echo "    exit: $code (want 0), output: $out"
  diff <(printf '%s\n' "$want") <(printf '%s\n' "$got") | sed 's/^/    /'
fi

# 2. an unknown subcommand exits 2 and leaves the queue file byte-identical.
repo="$work/unknown-subcommand"
new_repo "$repo"
mkdir -p "$repo/.tdd"
printf 'beta\t4\tqueued\t\n' > "$repo/.tdd/workqueue"
cp "$repo/.tdd/workqueue" "$work/unknown-subcommand.before"
out="$(cd "$repo" && "$SCRIPT" frobnicate alpha 12 2>&1)" && code=0 || code=$?
if [[ "$code" -eq 2 ]] && cmp -s "$work/unknown-subcommand.before" "$repo/.tdd/workqueue"; then
  pass=$((pass + 1))
else
  fail=$((fail + 1))
  echo "FAIL - an unknown subcommand exits 2 and leaves the queue file byte-identical"
  echo "    exit: $code (want 2), output: $out"
  diff "$work/unknown-subcommand.before" "$repo/.tdd/workqueue" 2>&1 | sed 's/^/    /'
fi

# 3. an unknown subcommand in a repo with no queue exits 2 and creates no queue file.
repo="$work/unknown-subcommand-no-queue"
new_repo "$repo"
out="$(cd "$repo" && "$SCRIPT" frobnicate alpha 12 2>&1)" && code=0 || code=$?
if [[ "$code" -eq 2 && ! -e "$repo/.tdd/workqueue" ]]; then
  pass=$((pass + 1))
else
  fail=$((fail + 1))
  echo "FAIL - an unknown subcommand in a repo with no queue exits 2 and creates no queue file"
  echo "    exit: $code (want 2), output: $out"
  echo "    .tdd/workqueue: $([[ -e "$repo/.tdd/workqueue" ]] && echo present || echo absent) (want absent)"
fi

echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
