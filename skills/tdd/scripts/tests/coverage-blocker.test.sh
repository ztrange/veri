#!/usr/bin/env bash
# Tests for scripts/coverage-blocker.sh — what a refactor-kind run does when Cover answers
# `COVERED: no` (#499): file an unlabelled coverage issue for the refactor issue, and name that
# new issue under the refactor issue's `## Blocked by` heading so the queue cannot retake it and
# refuse again.
#
# Contract under test:
#   coverage-blocker.sh <refactor-issue-number>
#   GH_REPO=owner/name coverage-blocker.sh <refactor-issue-number>
#
# Driven against a stub `gh` on PATH (no network, no real issue), the way
# tick-issue-criterion.test.sh drives its wrapper. "No longer listed" is asked of
# solvable-issues.sh itself, fed the edited body through its VERI_GH_JSON fixture override.
#
# Run: scripts/tests/coverage-blocker.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
BLOCKER="$HERE/../coverage-blocker.sh"
SOLVABLE="$HERE/../solvable-issues.sh"
pass=0 fail=0
ok() { pass=$((pass + 1)); }
no() { fail=$((fail + 1)); echo "FAIL - $1"; }

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

# A stub `gh`: `issue create` records its argv to $FAKE_CREATE and prints the new issue's URL,
# as the real one does; `issue view` prints $FAKE_BODY; `issue edit` copies its --body-file to
# $FAKE_OUT so the test can read what would have been written.
stubdir="$work/bin"
mkdir -p "$stubdir"
cat > "$stubdir/gh" <<'STUB'
#!/bin/sh
if [ "$1" = "issue" ] && [ "$2" = "create" ]; then
  printf '%s\n' "$@" > "$FAKE_CREATE"
  echo "https://github.com/owner/name/issues/77"
elif [ "$1" = "issue" ] && [ "$2" = "view" ]; then
  printf '%s' "$FAKE_BODY"
elif [ "$1" = "issue" ] && [ "$2" = "edit" ]; then
  prev=""
  for a in "$@"; do
    [ "$prev" = "--body-file" ] && cp "$a" "$FAKE_OUT"
    prev="$a"
  done
fi
STUB
chmod +x "$stubdir/gh"

# run_blocker <body> <create-file> <out-file> [args...] — runs coverage-blocker.sh against the stub.
run_blocker() {
  local body="$1" create="$2" out="$3"
  shift 3
  env PATH="$stubdir:$PATH" FAKE_BODY="$body" FAKE_CREATE="$create" FAKE_OUT="$out" "$BLOCKER" "$@"
}

# expect_edit <case> <name> <body> <want> — runs coverage-blocker.sh on refactor issue #60 with
# <body> as its current body, and passes when it exits 0 having written exactly <want>.
expect_edit() {
  local case="$1" name="$2" body="$3" want="$4" code new_body=""
  local edited="$work/edited$case.body"
  run_blocker "$body" "$work/create$case.args" "$edited" 60 >/dev/null 2>"$work/blocker$case.err" && code=0 || code=$?
  [[ -f "$edited" ]] && new_body="$(cat "$edited")"
  if [[ "$code" == 0 && "$new_body" == "$want" ]]; then
    ok
  else
    no "$name (exit=$code want 0)
$(diff <(printf '%s\n' "$want") <(printf '%s\n' "$new_body"))
$(cat "$work/blocker$case.err")"
  fi
}

# solvable-issues.sh reads a run's claim off the main working tree of the repository it is run
# in; a repository of the suite's own claims nothing, so only the fixture answers.
no_claims="$work/no-claims"
git init -q -b main "$no_claims" >/dev/null 2>&1
cd "$no_claims" || exit 2

# 1. The refactor issue #60 is opted in and reads `None` under `## Blocked by`, so it is
# takeable. coverage-blocker.sh files #77 with no label, and rewrites #60's body so the heading
# names #77 in place of the `None` line. Fed that body with #77 open, solvable-issues.sh no
# longer lists #60 — and does not list #77, which carries no opt-in label.
name="coverage-blocker files an unlabelled issue and blocks the refactor issue on it"
body='## What to build

Extract the parser.

## Blocked by

None (can start immediately).

Test command: make test
'
create="$work/create.args" edited="$work/edited.body"
run_blocker "$body" "$create" "$edited" 60 >/dev/null 2>"$work/blocker.err" && code=0 || code=$?

fx="$work/fx"
mkdir -p "$fx"
printf '[]\n' > "$fx/prs.json"
new_body=""
[[ -f "$edited" ]] && new_body="$(cat "$edited")"
python3 -c '
import json, sys
print(json.dumps([
    {"number": 60, "title": "refactor the parser", "state": "OPEN",
     "labels": [{"name": "ready-for-agent"}, {"name": "refactor"}], "body": sys.argv[1]},
    {"number": 77, "title": "cover the parser", "state": "OPEN", "labels": [], "body": "x"},
]))' "$new_body" > "$fx/issues.json"
listed="$(VERI_GH_JSON="$fx" "$SOLVABLE" 2>/dev/null)" && lcode=0 || lcode=$?

labelled=no
[[ -f "$create" ]] && grep -Fx -e '--label' -e '-l' "$create" > /dev/null && labelled=yes
blocked_section="$(printf '%s\n' "$new_body" | sed -n '/^## Blocked by/,/^## /p')"

if [[ "$code" == 0 && -f "$create" && "$labelled" == no \
      && "$blocked_section" == *"#77"* && "$blocked_section" != *None* \
      && "$lcode" == 3 && -z "$listed" ]]; then
  ok
else
  no "$name (blocker exit=$code want 0; issue created=$([[ -f "$create" ]] && echo yes || echo no) want yes; labelled=$labelled want no; Blocked by section='$blocked_section' want #77 and no None; solvable exit=$lcode want 3, listed='$listed' want '')
$(cat "$work/blocker.err")"
fi

# 2. Only the `None` under `## Blocked by` is replaced. A `None` line in another section is the
# issue's own prose, and survives the edit byte for byte, while the one under the heading still
# becomes the new blocker.
name="coverage-blocker replaces only the None line under ## Blocked by"
body='## What to build

None of the callers change.

## Blocked by

None (can start immediately).
'
want='## What to build

None of the callers change.

## Blocked by

- #77'
expect_edit 2 "$name" "$body" "$want"

# 3. Called with no issue number, it refuses with exit 2 and a usage line, and files nothing.
name="coverage-blocker with no issue number exits 2 with a usage line and files no issue"
create3="$work/create3.args"
err="$(run_blocker x "$create3" "$work/edited3.body" 2>&1 >/dev/null)" && code=0 || code=$?
if [[ "$code" == 2 && "$err" == *usage* && ! -f "$create3" ]]; then
  ok
else
  no "$name (exit=$code want 2; stderr='$err' want a usage line; issue created=$([[ -f "$create3" ]] && echo yes || echo no) want no)"
fi

# 4. A `## Blocked by` section that already lists a blocker has no `None` line to replace; the
# new issue is appended after the blockers already there, which stay, and the prose after them
# survives. A `- #N` bullet in a later section is not a blocker, so nothing is appended there.
name="coverage-blocker appends the new blocker to a Blocked by section that already lists blockers"
body='## What to build

Extract the parser.

## Blocked by

- #12

## Related

- #30

Test command: make test
'
want='## What to build

Extract the parser.

## Blocked by

- #12
- #77

## Related

- #30

Test command: make test'
expect_edit 4 "$name" "$body" "$want"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
