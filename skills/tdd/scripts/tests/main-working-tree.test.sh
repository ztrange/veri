#!/usr/bin/env bash
# Unit tests for scripts/lib/main-working-tree.sh — the one definition of `main_working_tree`
# that status.sh and solvable-issues.sh both source, rather than each carrying a copy.
#
# Why this exists (issue #281): the function was byte-identical in both scripts, so the #166
# resolution rule — the main working tree is the first `worktree <path>` line of git's
# registry, never the checkout the script was called from — lived in two places, and a fix to
# one copy would leave the other resolving runs and locks somewhere else.
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
SCRIPTS="$HERE/.."
HELPER="$SCRIPTS/lib/main-working-tree.sh"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
pass=0 fail=0

# report <name> — close a case whose probes collected into the `problems` array: an empty
# array is a pass, otherwise one FAIL line for the case and one indented line per problem.
report() {
  local name="$1"
  if [[ "${#problems[@]}" -eq 0 ]]; then
    pass=$((pass + 1))
  else
    fail=$((fail + 1))
    echo "FAIL - $name"
    printf '    %s\n' "${problems[@]}"
  fi
}

# 1. One helper, and both scripts resolve through it.
#
# A repository with one commit (`git worktree add` refuses a repo with nothing to check out)
# and a linked worktree of it, so "called from a linked worktree" is a real registration and
# not a directory that merely looks like one. The expected path is git's own first registry
# line, read from the main tree, so a /var vs /private/var difference on macOS cannot fail it.
main_repo="$work/main"
git init -q -b main "$main_repo" >/dev/null 2>&1
git -C "$main_repo" -c user.name=veri -c user.email=veri@example.test \
  commit -q --allow-empty -m initial >/dev/null 2>&1
linked="$work/linked"
git -C "$main_repo" worktree add -q -b side "$linked" main >/dev/null 2>&1
first_line="$(head -n 1 < <(git -C "$main_repo" worktree list --porcelain))"
want_main="${first_line#worktree }"

problems=()

# The real helper, sourced from inside the linked worktree.
got_main="$(cd "$linked" && source "$HELPER" 2>/dev/null && main_working_tree 2>/dev/null)"
[[ -n "$want_main" && "$got_main" == "$want_main" ]] \
  || problems+=("sourcing $HELPER from a linked worktree: main_working_tree printed '$got_main', want '$want_main'")

# Both scripts, copied beside a stand-in helper that answers a decoy directory instead. The
# real main tree above has no runs and no locks; the decoy has run #5 holding a live lock (this
# suite's own pid). So a script that reads the decoy resolved the main tree through the helper,
# and one that reads the real main tree carries its own copy of the rule.
decoy="$work/decoy"
git init -q -b tdd/5-decoy "$decoy/.tdd/wt/5" >/dev/null 2>&1
mkdir -p "$decoy/.tdd/wt/5/.tdd"
printf '# Plan for #5 — decoy run\n\n- [ ] a step\n' > "$decoy/.tdd/wt/5/.tdd/issue-5.md"
printf '%s\n' "$$" > "$decoy/.tdd/wt/5/.tdd/conductor.pid"

copy="$work/scripts"
mkdir -p "$copy/lib"
cp "$SCRIPTS/status.sh" "$SCRIPTS/solvable-issues.sh" "$copy/"
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

echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
