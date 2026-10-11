#!/usr/bin/env bash
# Tests for scripts/refactor-overflow.sh — files the structural candidates a run's closing
# pass could not reach as one issue naming the parent issue. Driven against a stub `gh` on PATH.
#
# Contract under test:
#   refactor-overflow.sh <n> <owed-file> <reached>
#
# Run: scripts/tests/refactor-overflow.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
OVERFLOW="$HERE/../refactor-overflow.sh"
OWED="$HERE/../refactor-owed.sh"
source "$HERE/lib/harness.sh"

work="$(scratch_dir)"

stubdir="$work/bin"
mkdir -p "$stubdir"
cat > "$stubdir/gh" <<'STUB'
#!/bin/sh
printf '%s\n' "$*" >> "${FAKE_CALLS:-/dev/null}"
case "$*" in
  "issue create"*|"api "*"repos/"*"/issues"*) ;;
  *) exit 1 ;;
esac
while [ "$#" -gt 0 ]; do
  case "$1" in
    --title|-t) shift; printf '%s\n' "$1" >> "$FAKE_TITLE" ;;
    --body|-b) shift; printf '%s\n' "$1" >> "$FAKE_BODY" ;;
    --body-file|-F)
      case "$2" in
        *=*) ;;
        *) shift; cat "$1" >> "$FAKE_BODY" ;;
      esac ;;
    title=*) printf '%s\n' "${1#title=}" >> "$FAKE_TITLE" ;;
    body=@*) cat "${1#body=@}" >> "$FAKE_BODY" ;;
    body=*) printf '%s\n' "${1#body=}" >> "$FAKE_BODY" ;;
  esac
  shift
done
echo "https://github.com/owner/name/issues/912"
STUB
chmod +x "$stubdir/gh"

owed_file="$work/issue-504-refactor-owed.md"
"$OWED" append "$owed_file" 'first step' <<'REPORT'
CANDIDATES: structural | fold verify.sh's two mktemp calls into one helper
CANDIDATES: structural | hoist the ledger path into one variable
REPORT
"$OWED" append "$owed_file" 'second step' <<'REPORT'
CANDIDATES: structural | hoist the ledger path into one variable
CANDIDATES: structural | split the verdict parser out of run-leaf.sh
REPORT

out="$work/out" calls="$work/calls"

overflow_case() {
  local label="$1" want="$2" code
  shift 2
  : > "$calls"
  (cd "$work" && env PATH="$stubdir:$PATH" FAKE_CALLS="$calls" \
    "$OVERFLOW" "$@" >"$out" 2>"$work/err") && code=0 || code=$?
  [[ "$code" == "$want" ]] ||
    problems+=("want exit $want $label, got $code: $(cat "$work/err")")
  [[ ! -s "$out" ]] ||
    problems+=("want empty stdout $label, got '$(cat "$out")'")
  [[ ! -s "$calls" ]] ||
    problems+=("want no gh call $label, got '$(cat "$calls")'")
}

name="refactor-overflow exits 1 with nothing on stdout and lets gh's stderr through when gh fails while filing"
problems=()

failing_stubdir="$work/failing-bin"
mkdir -p "$failing_stubdir"
cat > "$failing_stubdir/gh" <<'STUB'
#!/bin/sh
echo "gh: HTTP 422: Validation Failed" >&2
exit 1
STUB
chmod +x "$failing_stubdir/gh"

(cd "$work" && env PATH="$failing_stubdir:$PATH" \
  "$OVERFLOW" 504 "$owed_file" 1 >"$out" 2>"$work/err") && code=0 || code=$?
[[ "$code" == 2 ]] ||
  problems+=("want exit 2 when gh fails while filing, got $code: $(cat "$work/err")")
[[ ! -s "$out" ]] ||
  problems+=("want empty stdout when gh fails while filing, got '$(cat "$out")'")
got_err="$(cat "$work/err")"
[[ "$got_err" == *"gh: HTTP 422: Validation Failed"* ]] ||
  problems+=("want gh's stderr line 'gh: HTTP 422: Validation Failed' on stderr when gh fails while filing, got '$got_err'")

report "$name"

name="refactor-overflow run through a symlink to the skill directory and from another working directory files the candidates refactor-owed.sh lists beside it, with gh run in the caller's working directory"
problems=()

pwd_stubdir="$work/pwd-bin"
mkdir -p "$pwd_stubdir"
cat > "$pwd_stubdir/gh" <<STUB
#!/bin/sh
pwd -P > "\$FAKE_PWD"
exec "$stubdir/gh" "\$@"
STUB
chmod +x "$pwd_stubdir/gh"

ln -s "$(cd "$HERE/../.." && pwd)" "$work/linked-skill"
mkdir -p "$work/elsewhere"
title_file="$work/title-linked" body_file="$work/body-linked" pwd_file="$work/pwd-linked"
(cd "$work/elsewhere" && env PATH="$pwd_stubdir:$PATH" FAKE_TITLE="$title_file" FAKE_BODY="$body_file" FAKE_PWD="$pwd_file" \
  "$work/linked-skill/scripts/refactor-overflow.sh" 504 "$owed_file" 1 >"$out" 2>"$work/err") && code=0 || code=$?

[[ "$code" == 0 ]] ||
  problems+=("want exit 0 run through the symlink, got $code: $(cat "$work/err")")
printed="$(cat "$out")"
[[ "$printed" == "https://github.com/owner/name/issues/912" ]] ||
  problems+=("want the new issue's URL on stdout run through the symlink, got '$printed'")
body="$(cat "$body_file" 2>/dev/null)"
want_body="Structural candidates #504's closing pass could not reach:

- fold verify.sh's two mktemp calls into one helper
- split the verdict parser out of run-leaf.sh"
[[ "$body" == "$want_body" ]] ||
  problems+=("want the filed body to list the candidates refactor-owed.sh lists after the first 1:" "$want_body" "got" "$body")
want_pwd="$(cd "$work/elsewhere" && pwd -P)"
got_pwd="$(cat "$pwd_file" 2>/dev/null)"
[[ "$got_pwd" == "$want_pwd" ]] ||
  problems+=("want gh run in the caller's working directory '$want_pwd', got '$got_pwd'")

report "$name"

name="refactor-overflow exits 2 when gh fails filing the issue with status 1, 3 or 5 (#775)"
problems=()

status_stubdir="$work/status-bin"
mkdir -p "$status_stubdir"
cat > "$status_stubdir/gh" <<'STUB'
#!/bin/sh
exit "$FAKE_GH_STATUS"
STUB
chmod +x "$status_stubdir/gh"

for status in 1 3 5; do
  (cd "$work" && env PATH="$status_stubdir:$PATH" FAKE_GH_STATUS="$status" \
    "$OVERFLOW" 504 "$owed_file" 1 >"$out" 2>"$work/err") && code=0 || code=$?
  [[ "$code" == 2 ]] ||
    problems+=("gh filing exit $status: want exit 2, got $code")
done

report "$name"

name="#992 refactor-overflow <n> <owed-file> 0 over an owed file holding only an out-of-scope candidate files one 'Refactor owed by #<n>' issue whose body lists that transform"
problems=()

out_of_scope_owed="$work/issue-992-refactor-owed.md"
"$OWED" append "$out_of_scope_owed" 'first step' <<'REPORT'
CANDIDATES: out-of-scope | extract the five copies of the mktemp dance across the skill
REPORT

: > "$calls"
title_file="$work/title-out-of-scope" body_file="$work/body-out-of-scope"
(cd "$work" && env PATH="$stubdir:$PATH" FAKE_CALLS="$calls" FAKE_TITLE="$title_file" FAKE_BODY="$body_file" \
  "$OVERFLOW" 992 "$out_of_scope_owed" 0 >"$out" 2>"$work/err") && code=0 || code=$?

[[ "$code" == 0 ]] ||
  problems+=("want exit 0 with one out-of-scope candidate owed, got $code: $(cat "$work/err")")
printed="$(cat "$out")"
[[ "$printed" == "https://github.com/owner/name/issues/912" ]] ||
  problems+=("want the new issue's URL on stdout, got '$printed'")
filings="$(grep -cE '^(issue create|api repos/)' "$calls")"
[[ "$filings" == 1 ]] ||
  problems+=("want exactly one gh call filing the issue, got $filings: '$(cat "$calls")'")
title="$(cat "$title_file" 2>/dev/null)"
[[ "$title" == "Refactor owed by #992" ]] ||
  problems+=("want the filed title 'Refactor owed by #992', got '$title'")
body="$(cat "$body_file" 2>/dev/null)"
[[ "$body" == *"extract the five copies of the mktemp dance across the skill"* ]] ||
  problems+=("want the out-of-scope transform in the filed issue's body, got '$body'")
bullets="$(grep -E '^- ' <<<"$body")"
[[ "$bullets" == "- extract the five copies of the mktemp dance across the skill" ]] ||
  problems+=("want the body to list exactly one bullet, the transform, got '$bullets'")

report "$name"

name="#1058 refactor-overflow files no out-of-scope candidate the owed file records as applied, and still files an unapplied out-of-scope one beside it"
problems=()

applied_owed="$work/issue-1058-refactor-owed.md"
"$OWED" append "$applied_owed" 'fourth step' <<'REPORT'
CANDIDATES: out-of-scope | remove gh(), issue() and the subprocess import from coverage_blocker.py
REPORT
"$OWED" applied "$applied_owed" 'out-of-scope | remove gh(), issue() and the subprocess import from coverage_blocker.py' 1b4ed26

overflow_case "with only an applied out-of-scope candidate in the owed file" 3 1058 "$applied_owed" 0

"$OWED" append "$applied_owed" 'fifth step' <<'REPORT'
CANDIDATES: out-of-scope | extract the five copies of the mktemp dance across the skill
REPORT

title_file="$work/title-applied" body_file="$work/body-applied"
(cd "$work" && env PATH="$stubdir:$PATH" FAKE_TITLE="$title_file" FAKE_BODY="$body_file" \
  "$OVERFLOW" 1058 "$applied_owed" 0 >"$out" 2>"$work/err") && code=0 || code=$?
[[ "$code" == 0 ]] ||
  problems+=("want exit 0 with an unapplied out-of-scope candidate beside the applied one, got $code: $(cat "$work/err")")
bullets="$(grep -E '^- ' "$body_file" 2>/dev/null)"
[[ "$bullets" == "- extract the five copies of the mktemp dance across the skill" ]] ||
  problems+=("want the body to list only the unapplied out-of-scope candidate, got '$bullets'")

report "$name"

name="#1035 refactor-overflow with both unreached structural candidates and out-of-scope transforms files a body with two headed lists, structural under 'could not reach' and out-of-scope under 'did not attempt', under the unchanged title"
problems=()

both_owed="$work/issue-1035-refactor-owed.md"
"$OWED" append "$both_owed" 'first step' <<'REPORT'
CANDIDATES: structural | hoist the ledger path into one variable
CANDIDATES: out-of-scope | extract the five copies of the mktemp dance across the skill
REPORT

title_file="$work/title-both" body_file="$work/body-both"
(cd "$work" && env PATH="$stubdir:$PATH" FAKE_TITLE="$title_file" FAKE_BODY="$body_file" \
  "$OVERFLOW" 1035 "$both_owed" 0 >"$out" 2>"$work/err") && code=0 || code=$?
[[ "$code" == 0 ]] ||
  problems+=("want exit 0 with both kinds owed, got $code: $(cat "$work/err")")
title="$(cat "$title_file" 2>/dev/null)"
[[ "$title" == "Refactor owed by #1035" ]] ||
  problems+=("want the filed title 'Refactor owed by #1035', got '$title'")
body="$(cat "$body_file" 2>/dev/null)"
want_body="Structural candidates #1035's closing pass could not reach:

- hoist the ledger path into one variable

Out-of-scope transforms #1035's closing pass did not attempt:

- extract the five copies of the mktemp dance across the skill"
[[ "$body" == "$want_body" ]] ||
  problems+=("want the body as two headed lists:
$want_body
got:
$body")

report "$name"

name="#1035 refactor-overflow with only out-of-scope transforms files a body carrying only the out-of-scope heading"
problems=()

only_out_of_scope_owed="$work/issue-1035-only-out-of-scope-refactor-owed.md"
"$OWED" append "$only_out_of_scope_owed" 'first step' <<'REPORT'
CANDIDATES: out-of-scope | extract the five copies of the mktemp dance across the skill
REPORT

title_file="$work/title-only-out-of-scope" body_file="$work/body-only-out-of-scope"
(cd "$work" && env PATH="$stubdir:$PATH" FAKE_TITLE="$title_file" FAKE_BODY="$body_file" \
  "$OVERFLOW" 1035 "$only_out_of_scope_owed" 0 >"$out" 2>"$work/err") && code=0 || code=$?
[[ "$code" == 0 ]] ||
  problems+=("want exit 0 with only out-of-scope transforms owed, got $code: $(cat "$work/err")")
body="$(cat "$body_file" 2>/dev/null)"
want_body="Out-of-scope transforms #1035's closing pass did not attempt:

- extract the five copies of the mktemp dance across the skill"
[[ "$body" == "$want_body" ]] ||
  problems+=("want the body as the out-of-scope heading and its list alone:
$want_body
got:
$body")

report "$name"

name="#1035 refactor-overflow with only unreached structural candidates files a body carrying only the structural heading"
problems=()

only_structural_owed="$work/issue-1035-only-structural-refactor-owed.md"
"$OWED" append "$only_structural_owed" 'first step' <<'REPORT'
CANDIDATES: structural | hoist the ledger path into one variable
CANDIDATES: structural | split the verdict parser out of run-leaf.sh
REPORT

title_file="$work/title-only-structural" body_file="$work/body-only-structural"
(cd "$work" && env PATH="$stubdir:$PATH" FAKE_TITLE="$title_file" FAKE_BODY="$body_file" \
  "$OVERFLOW" 1035 "$only_structural_owed" 1 >"$out" 2>"$work/err") && code=0 || code=$?
[[ "$code" == 0 ]] ||
  problems+=("want exit 0 with only unreached structural candidates owed, got $code: $(cat "$work/err")")
body="$(cat "$body_file" 2>/dev/null)"
want_body="Structural candidates #1035's closing pass could not reach:

- split the verdict parser out of run-leaf.sh"
[[ "$body" == "$want_body" ]] ||
  problems+=("want the body as the structural heading and its list alone:
$want_body
got:
$body")

report "$name"

finish
