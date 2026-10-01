#!/usr/bin/env bash
# Unit tests for scripts/lib/main-working-tree.sh — the one definition of `main_working_tree`
# that status.sh and solvable-issues.sh both source.
#
# Contract under test:
#   source lib/main-working-tree.sh; main_working_tree   → the main working tree's path, as
#                                                          git prints it, from a linked worktree
#   status.sh and solvable-issues.sh                      → look for runs and locks under
#                                                          whatever that helper answers
#
# Run: scripts/tests/main-working-tree.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/lib/harness.sh"
SCRIPTS="$HERE/.."
HELPER="$SCRIPTS/lib/main-working-tree.sh"
work="$(scratch_dir)"

main_repo="$work/main"
new_repo -b main "$main_repo" >/dev/null 2>&1
git -C "$main_repo" -c user.name=veri -c user.email=veri@example.test \
  commit -q --allow-empty -m initial >/dev/null 2>&1
linked="$work/linked"
git -C "$main_repo" worktree add -q -b side "$linked" main >/dev/null 2>&1
first_line="$(head -n 1 < <(git -C "$main_repo" worktree list --porcelain))"
want_main="${first_line#worktree }"

problems=()

got_main="$(cd "$linked" && source "$HELPER" 2>/dev/null && main_working_tree 2>/dev/null)"
[[ -n "$want_main" && "$got_main" == "$want_main" ]] \
  || problems+=("sourcing $HELPER from a linked worktree: main_working_tree printed '$got_main', want '$want_main'")

decoy="$work/decoy"
new_repo -b tdd/5-decoy "$decoy/.tdd/wt/5" >/dev/null 2>&1
mkdir -p "$decoy/.tdd/wt/5/.tdd"
printf '# Plan for #5 — decoy run\n\n- [ ] a step\n' > "$decoy/.tdd/wt/5/.tdd/issue-5.md"
printf '%s\n' "$$" > "$decoy/.tdd/wt/5/.tdd/conductor.pid"

copy="$work/scripts"
mkdir -p "$copy/lib"
cp "$SCRIPTS/status.sh" "$SCRIPTS/solvable-issues.sh" "$copy/"
cp "$SCRIPTS/lib/blocked_by.py" "$SCRIPTS/lib/github.sh" "$SCRIPTS/lib/exit-contract.sh" "$copy/lib/"
printf 'main_working_tree() { printf "%%s\\n" %q; }\n' "$decoy" > "$copy/lib/main-working-tree.sh"

status_out="$(cd "$linked" && env -u VERI_LABEL "$copy/status.sh" 2>/dev/null)" && status_code=0 || status_code=$?
[[ "$status_code" -eq 0 && "$status_out" == *"#5"* ]] \
  || problems+=("status.sh beside a helper answering the decoy: printed '$status_out' (exit $status_code), want the decoy's run #5 (exit 0)")

fx="$work/gh"
mkdir -p "$fx"
printf '[]\n' > "$fx/prs.json"
cat > "$fx/issues.json" <<'JSON'
[
  {"number": 5, "title": "claimed in the decoy", "labels": [{"name": "ready-for-agent"}],
   "state": "OPEN", "body": "## Blocked by\n\nNone.\n"},
  {"number": 6, "title": "claimed nowhere", "labels": [{"name": "ready-for-agent"}],
   "state": "OPEN", "body": "## Blocked by\n\nNone.\n"}
]
JSON
solvable_out="$(cd "$linked" && env -u VERI_LABEL -u VERI_PRIORITY_LABEL VERI_GH_JSON="$fx" \
  "$copy/solvable-issues.sh" 2>/dev/null)" && solvable_code=0 || solvable_code=$?
[[ "$solvable_code" -eq 0 && "$solvable_out" == "6" ]] \
  || problems+=("solvable-issues.sh beside a helper answering the decoy: printed '$(tr '\n' ' ' <<<"$solvable_out")' (exit $solvable_code), want '6' — #5 is claimed by the decoy's live lock")

report "a shared lib/main-working-tree.sh defines main_working_tree, and status.sh and solvable-issues.sh both resolve the main working tree through it"

finish
