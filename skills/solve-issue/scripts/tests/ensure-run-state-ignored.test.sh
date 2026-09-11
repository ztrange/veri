#!/usr/bin/env bash
# Unit tests for scripts/ensure-run-state-ignored.sh — installs veri's run-state rule into
# a target repo's .gitignore, so the first `git add -A` cannot sweep run scratch (leaf logs,
# .rc markers, .prompt files, the blind spec) into history while still committing the ledger.
#
# Contract under test (issue #27):
#   ensure-run-state-ignored.sh [repo-root]   (default: the current directory)
#   afterwards, in that repo, `git check-ignore` says
#     .tdd/develop-red.log  IS ignored      (exit 0)
#     .tdd/issue-7.md       is NOT ignored  (exit 1)
#
# The assertion is on git's own ignore decision, not on the text of .gitignore: the rule is
# order-sensitive (`.tdd/*`, then a negation, then a re-ignore) and grepping for lines would
# pass on an ordering git rejects.
#
# Run: scripts/tests/ensure-run-state-ignored.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ENSURE="$HERE/../ensure-run-state-ignored.sh"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
pass=0 fail=0
ok() { pass=$((pass + 1)); }
no() { fail=$((fail + 1)); echo "FAIL - $1"; }

# new_repo <path> — an empty git repo at <path>, so check-ignore has a repo to answer within.
new_repo() {
  mkdir -p "$1"
  git init -q "$1" >/dev/null 2>&1
}

# ignored <repo> <path> — git's verdict on one path, as an exit code we can assert on.
# 0 = ignored, 1 = not ignored, anything else = git errored (a broken test, not a verdict).
ignored() {
  git -C "$1" check-ignore -q "$2" 2>/dev/null
}

# 1. a repo with no .gitignore at all gets one that separates run scratch from the ledger
repo="$work/fresh"
new_repo "$repo"

"$ENSURE" "$repo" >/dev/null 2>&1

ignored "$repo" .tdd/develop-red.log && log_code=0 || log_code=$?
ignored "$repo" .tdd/issue-7.md && ledger_code=0 || ledger_code=$?

{ [[ "$log_code" == 0 ]] && [[ "$ledger_code" == 1 ]]; } \
  && ok || no "no .gitignore: creates one ignoring .tdd/develop-red.log but not .tdd/issue-7.md (develop-red.log=$log_code want 0 ignored, issue-7.md=$ledger_code want 1 not ignored)"

# 2. a repo that already carries the rule — running it a second time changes nothing and says so
repo="$work/twice"
new_repo "$repo"

"$ENSURE" "$repo" >/dev/null 2>&1
before="$work/twice.gitignore.before"
cp "$repo/.gitignore" "$before"

out="$("$ENSURE" "$repo" 2>/dev/null)" && code=0 || code=$?
cmp -s "$before" "$repo/.gitignore" && same=0 || same=$?

{ [[ "$same" == 0 ]] && [[ "$code" == 0 ]] && [[ "$out" == *"already present"* ]]; } \
  && ok || no "already carries the rule: leaves .gitignore byte-identical and reports already present (cmp=$same want 0 identical, exit=$code want 0, stdout='$out' want it to contain 'already present')"

# 3. a repo whose .gitignore already has unrelated rules — they survive, and the run gets reported.
# The seed deliberately ends WITHOUT a trailing newline: that is where a naive append fuses `*.log`
# and `.tdd/*` into one line, silently destroying both rules. We assert the old rules still *work*
# (via git, not by grepping) rather than that the bytes are still somewhere in the file.
repo="$work/unrelated"
new_repo "$repo"
printf 'node_modules/\n*.log' > "$repo/.gitignore"

out="$("$ENSURE" "$repo" 2>/dev/null)" && code=0 || code=$?

ignored "$repo" node_modules/x && modules_code=0 || modules_code=$?
ignored "$repo" debug.log && debuglog_code=0 || debuglog_code=$?
ignored "$repo" .tdd/develop-red.log && log_code=0 || log_code=$?
ignored "$repo" .tdd/issue-7.md && ledger_code=0 || ledger_code=$?

{ [[ "$modules_code" == 0 ]] && [[ "$debuglog_code" == 0 ]] \
  && [[ "$log_code" == 0 ]] && [[ "$ledger_code" == 1 ]] \
  && [[ "$code" == 0 ]] && [[ "$out" == *"added"* ]]; } \
  && ok || no "unrelated .gitignore: keeps every existing line and reports added (node_modules/x=$modules_code want 0 still ignored, debug.log=$debuglog_code want 0 still ignored, develop-red.log=$log_code want 0 ignored, issue-7.md=$ledger_code want 1 not ignored, exit=$code want 0, stdout='$out' want it to contain 'added')"

# 4. a repo whose .gitignore carries ONLY the rule's last line — a partial block, not the rule.
# Appending to it cannot repair it (`.tdd/*` after the spec re-ignore reads differently), so the
# script must refuse: non-zero exit, a diagnostic on stderr, and the file untouched byte for byte.
repo="$work/partial"
new_repo "$repo"
printf '.tdd/issue-*-spec.md\n' > "$repo/.gitignore"
before="$work/partial.gitignore.before"
cp "$repo/.gitignore" "$before"

err="$work/partial.stderr"
"$ENSURE" "$repo" >/dev/null 2>"$err" && code=0 || code=$?
cmp -s "$before" "$repo/.gitignore" && same=0 || same=$?
[[ -s "$err" ]] && diag=0 || diag=1

{ [[ "$code" != 0 ]] && [[ "$diag" == 0 ]] && [[ "$same" == 0 ]]; } \
  && ok || no "partial rule (only .tdd/issue-*-spec.md): refuses with a diagnostic and touches nothing (exit=$code want non-zero, stderr-non-empty=$diag want 0, cmp=$same want 0 identical)"

# 5. a repo whose .gitignore carries all three lines but in an order git reads differently:
# the negation last, so `!.tdd/issue-*.md` un-ignores the spec the line above just re-ignored.
# Every line is present, yet the rule is not — so this is the same refusal as case 4, and the
# script must not mistake "all three lines somewhere" for "the block, in order".
repo="$work/misordered"
new_repo "$repo"
printf '.tdd/*\n.tdd/issue-*-spec.md\n!.tdd/issue-*.md\n' > "$repo/.gitignore"
before="$work/misordered.gitignore.before"
cp "$repo/.gitignore" "$before"

err="$work/misordered.stderr"
"$ENSURE" "$repo" >/dev/null 2>"$err" && code=0 || code=$?
cmp -s "$before" "$repo/.gitignore" && same=0 || same=$?
[[ -s "$err" ]] && diag=0 || diag=1

{ [[ "$code" != 0 ]] && [[ "$diag" == 0 ]] && [[ "$same" == 0 ]]; } \
  && ok || no "misordered rule (negation last): refuses with a diagnostic and touches nothing (exit=$code want non-zero, stderr-non-empty=$diag want 0, cmp=$same want 0 identical)"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
