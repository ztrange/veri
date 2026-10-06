#!/usr/bin/env bash
# Tests for scripts/coverage-blocker.sh — files an unlabelled coverage issue for a refactor
# issue Cover answered `COVERED: no`, and names it under the refactor issue's `## Blocked by`.
# Driven against a stub `gh` on PATH.
#
# Contract under test:
#   coverage-blocker.sh <refactor-issue-number>
#   GH_REPO=owner/name coverage-blocker.sh <refactor-issue-number>
#
# Run: scripts/tests/coverage-blocker.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
BLOCKER="$HERE/../coverage-blocker.sh"
SOLVABLE="$HERE/../solvable-issues.sh"
source "$HERE/lib/harness.sh"

work="$(scratch_dir)"

stubdir="$work/bin"
mkdir -p "$stubdir"
cat > "$stubdir/gh" <<'STUB'
#!/bin/sh
case "$*" in
  *PATCH*)
    for a in "$@"; do
      case "$a" in *=@*) cp "${a#*=@}" "$FAKE_OUT" ;; esac
    done
    echo '{}' ;;
  "api "*"repos/"*"/issues/60"*) python3 -c 'import json, sys; print(json.dumps({"body": sys.argv[1]}))' "$FAKE_BODY" ;;
  "api "*"repos/"*"/issues?"*) echo '[]' ;;
  "api "*"repos/"*"/issues"*)
    printf '%s\n' "$@" > "$FAKE_CREATE"
    echo "https://github.com/owner/name/issues/77" ;;
esac
STUB
chmod +x "$stubdir/gh"

run_blocker() {
  local body="$1" create="$2" out="$3"
  shift 3
  env -u VERI_GH_DRIVER PATH="$stubdir:$PATH" FAKE_BODY="$body" FAKE_CREATE="$create" FAKE_OUT="$out" "$BLOCKER" "$@"
}

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

no_claims="$work/no-claims"
new_repo -b main "$no_claims" >/dev/null 2>&1
cd "$no_claims" || exit 2

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

name="coverage-blocker with no issue number exits 2 with a usage line and files no issue"
create3="$work/create3.args"
err="$(run_blocker x "$create3" "$work/edited3.body" 2>&1 >/dev/null)" && code=0 || code=$?
if [[ "$code" == 2 && "$err" == *usage* && ! -f "$create3" ]]; then
  ok
else
  no "$name (exit=$code want 2; stderr='$err' want a usage line; issue created=$([[ -f "$create3" ]] && echo yes || echo no) want no)"
fi

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

refuseddir="$work/refused"
mkdir -p "$refuseddir"
cat > "$refuseddir/gh" <<'STUB'
#!/bin/sh
refusal='GitHub GraphQL is not available from Claude Code sessions; use the REST API (gh api repos/{owner}/{repo}/...)'
unexpected() { echo "gh stub: unexpected call: gh $*" >&2; exit 1; }
case "$1" in
  issue|pr|repo) echo "HTTP 403: $refusal" >&2; exit 1 ;;
esac
record() {
  : > "$1"
  prev=""
  for a in "$@"; do
    printf '%s\n' "$a" >> "$1"
    case "$a" in
      *=@-) cat >> "$1" ;;
      *=@*) cat "${a#*=@}" >> "$1" ;;
    esac
    if [ "$prev" = "--input" ]; then
      if [ "$a" = "-" ]; then cat >> "$1"; else cat "$a" >> "$1"; fi
    fi
    prev="$a"
  done
}
case "$*" in
  "api graphql"*) echo "HTTP 403: $refusal" >&2; exit 1 ;;
  "api "*"repos/"*"/issues/60"|"api "*"repos/"*"/issues/60 "*)
    case "$*" in
      *PATCH*) record "$FAKE_OUT" "$@"; echo '{}' ;;
      *-f*|*-F*|*--field*|*--raw-field*|*--input*|*-X*|*--method*) unexpected "$@" ;;
      *"-q .body"*|*"--jq .body"*) printf '%s\n' "$FAKE_BODY" ;;
      *-q*|*--jq*|*--template*) unexpected "$@" ;;
      *) python3 -c 'import json, sys; print(json.dumps({"number": 60, "body": sys.argv[1], "labels": []}))' "$FAKE_BODY" ;;
    esac ;;
  "api "*"repos/"*"/issues"|"api "*"repos/"*"/issues "*)
    record "$FAKE_CREATE" "$@"
    case "$*" in
      *"-q .html_url"*|*"--jq .html_url"*) echo "https://github.com/owner/name/issues/77" ;;
      *-q*|*--jq*|*--template*) unexpected "$@" ;;
      *) echo '{"number": 77, "html_url": "https://github.com/owner/name/issues/77"}' ;;
    esac ;;
  *) unexpected "$@" ;;
esac
STUB
chmod +x "$refuseddir/gh"

name="under a gh that refuses GraphQL and answers REST, files the coverage issue and records the block with the same stdout and exit as a working gh (#568)"
body='## What to build

Extract the parser.

## Blocked by

None (can start immediately).
'
working_out="$work/working-out" refused_out="$work/refused-out" refused_edit="$work/refused-edit"
run_blocker "$body" "$work/working-create" "$work/working-edit" 60 > "$working_out" 2>/dev/null && working_code=0 || working_code=$?
env -u VERI_GH_DRIVER PATH="$refuseddir:$PATH" FAKE_BODY="$body" FAKE_CREATE="$work/refused-create" FAKE_OUT="$refused_edit" \
  "$BLOCKER" 60 > "$refused_out" 2>"$work/refused.err" && code=0 || code=$?
cmp -s "$working_out" "$refused_out" && same=yes || same=no
blocked=no
[[ -f "$refused_edit" ]] && grep -Fx -- "- #77" "$refused_edit" > /dev/null \
  && ! grep -F "None (can start" "$refused_edit" > /dev/null && blocked=yes
if [[ "$working_code" == 0 && "$code" == "$working_code" && "$same" == yes && "$blocked" == yes ]]; then
  ok
else
  no "$name (exit want $working_code got $code; stdout same=$same; blocked=$blocked want yes)
$(cat "$work/refused.err")"
fi

restdir="$work/rest"
mkdir -p "$restdir"
cat > "$restdir/gh" <<'STUB'
#!/bin/sh
echo "$*" >> "$FAKE_CALLS"
case "$1 $2" in
  "issue create"|"issue edit") exit 1 ;;
esac
case "$*" in
  *PATCH*)
    for a in "$@"; do
      case "$a" in *=@*) cp "${a#*=@}" "$FAKE_OUT" ;; esac
    done
    echo '{}' ;;
  "api "*"repos/"*"/issues/60") python3 -c 'import json, sys; print(json.dumps({"body": sys.argv[1]}))' "$FAKE_BODY" ;;
  "api "*"repos/"*"/issues?"*) echo '[]' ;;
  "api "*"repos/"*"/issues"*) echo "https://github.com/owner/name/issues/77" ;;
  *) exit 1 ;;
esac
STUB
chmod +x "$restdir/gh"

name="coverage-blocker files the issue and edits the body through gh api only, never gh issue create or edit (#568)"
body='## What to build

Extract the parser.

## Blocked by

None (can start immediately).
'
calls="$work/rest-calls" rest_edit="$work/rest-edit"
: > "$calls"
env -u VERI_GH_DRIVER PATH="$restdir:$PATH" FAKE_BODY="$body" FAKE_CALLS="$calls" FAKE_OUT="$rest_edit" \
  "$BLOCKER" 60 > "$work/rest-out" 2>"$work/rest.err" && code=0 || code=$?
issue_calls="$(grep -E '^issue (create|edit)' "$calls")"
blocked=no
[[ -f "$rest_edit" ]] && grep -Fx -- "- #77" "$rest_edit" > /dev/null && blocked=yes
if [[ "$code" == 0 && -z "$issue_calls" && "$blocked" == yes \
      && "$(cat "$work/rest-out")" == "https://github.com/owner/name/issues/77" ]]; then
  ok
else
  no "$name (exit want 0 got $code; issue create/edit calls='$issue_calls' want none; blocked=$blocked want yes)
$(cat "$work/rest.err")"
fi

name="coverage-blocker.sh run through a symlink to the skill directory and from another working directory prints the same URL, PATCHes the same body and exits as when run in place"
body='## What to build

Extract the parser.

## Blocked by

None (can start immediately).
'
ln -s "$(cd "$HERE/../.." && pwd)" "$work/linked-skill"
mkdir -p "$work/elsewhere"
run_blocker "$body" "$work/inplace-create" "$work/inplace-edit" 60 > "$work/inplace-out" 2>"$work/inplace.err" && in_place_code=0 || in_place_code=$?
(cd "$work/elsewhere" && env -u VERI_GH_DRIVER PATH="$stubdir:$PATH" FAKE_BODY="$body" FAKE_CREATE="$work/linked-create" FAKE_OUT="$work/linked-edit" \
  "$work/linked-skill/scripts/coverage-blocker.sh" 60 > "$work/linked-out" 2>"$work/linked.err") && linked_code=0 || linked_code=$?
if [[ "$in_place_code" == 0 && "$linked_code" == "$in_place_code" \
      && "$(cat "$work/inplace-out")" == "https://github.com/owner/name/issues/77" \
      && -f "$work/linked-edit" ]] && cmp -s "$work/inplace-out" "$work/linked-out" \
      && cmp -s "$work/inplace-edit" "$work/linked-edit"; then
  ok
else
  no "$name (exit in place $in_place_code, linked $linked_code, want 0 both)
$(diff "$work/inplace-out" "$work/linked-out")
$(diff "$work/inplace-edit" "$work/linked-edit" 2>&1)
$(cat "$work/linked.err")"
fi

name="coverage-blocker.sh with no argument and with an empty argument exits 2 with exactly its usage line on stderr and nothing on stdout"
usage_line='usage: coverage-blocker.sh <refactor-issue-number>'
run_blocker x "$work/usage-none-create" "$work/usage-none-edit" > "$work/usage-none.out" 2> "$work/usage-none.err" && none_code=0 || none_code=$?
run_blocker x "$work/usage-empty-create" "$work/usage-empty-edit" "" > "$work/usage-empty.out" 2> "$work/usage-empty.err" && empty_code=0 || empty_code=$?
if [[ "$none_code" == 2 && "$empty_code" == 2 \
      && "$(cat "$work/usage-none.err")" == "$usage_line" && "$(cat "$work/usage-empty.err")" == "$usage_line" \
      && ! -s "$work/usage-none.out" && ! -s "$work/usage-empty.out" ]]; then
  ok
else
  no "$name (exit none=$none_code empty=$empty_code want 2 both; stderr none='$(cat "$work/usage-none.err")' empty='$(cat "$work/usage-empty.err")' want '$usage_line'; stdout none='$(cat "$work/usage-none.out")' empty='$(cat "$work/usage-empty.out")' want '')"
fi

finish
