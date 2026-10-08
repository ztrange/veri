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

name="refactor-overflow files one issue naming the parent and listing every candidate after the first <reached>, and prints its URL"
problems=()

owed_file="$work/issue-504-refactor-owed.md"
"$OWED" append "$owed_file" 'first step' <<'REPORT'
CANDIDATES: structural | fold verify.sh's two mktemp calls into one helper
CANDIDATES: structural | hoist the ledger path into one variable
REPORT
"$OWED" append "$owed_file" 'second step' <<'REPORT'
CANDIDATES: structural | hoist the ledger path into one variable
CANDIDATES: structural | split the verdict parser out of run-leaf.sh
REPORT

title_file="$work/title" body_file="$work/body" out="$work/out"
(cd "$work" && env PATH="$stubdir:$PATH" FAKE_TITLE="$title_file" FAKE_BODY="$body_file" \
  "$OVERFLOW" 504 "$owed_file" 1 >"$out" 2>"$work/err") && code=0 || code=$?

[[ "$code" == 0 ]] ||
  problems+=("want exit 0, got $code: $(cat "$work/err")")

printed="$(cat "$out")"
[[ "$printed" == "https://github.com/owner/name/issues/912" ]] ||
  problems+=("want the new issue's URL on stdout, got '$printed'")

title="$(cat "$title_file" 2>/dev/null)"
[[ "$title" == *"#504"* ]] ||
  problems+=("want the filed issue's title to name the parent #504, got '$title'")

body="$(cat "$body_file" 2>/dev/null)"
[[ "$body" == *"#504"* ]] ||
  problems+=("want the filed issue's body to name the parent #504, got '$body'")

for unreached in \
  "fold verify.sh's two mktemp calls into one helper" \
  "split the verdict parser out of run-leaf.sh"
do
  [[ "$body" == *"$unreached"* ]] ||
    problems+=("want the unreached candidate '$unreached' in the filed issue's body, got '$body'")
done

[[ "$body" != *"hoist the ledger path into one variable"* ]] ||
  problems+=("want the reached candidate 'hoist the ledger path into one variable' left out of the filed issue's body, got '$body'")

report "$name"

name="refactor-overflow files nothing and exits 3 when no candidate is left unreached, and exits 2 on a missing or non-numeric argument"
problems=()

calls="$work/calls"

headed_only="$work/headed-only.md"
printf '### first step\n' > "$headed_only"

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

overflow_case "with the owed file missing" 3 504 "$work/no-such-file.md" 0
overflow_case "with no candidate in the owed file" 3 504 "$headed_only" 0
overflow_case "when <reached> covers every candidate" 3 504 "$owed_file" 3
overflow_case "on a missing argument" 2 504 "$owed_file"
overflow_case "on a non-numeric <reached>" 2 504 "$owed_file" two
overflow_case "on a non-numeric <n>" 2 five-oh-four "$owed_file" 1
overflow_case "on an empty <owed-file>" 2 504 "" 1

report "$name"

name="refactor-overflow files nothing and exits 3 when every unreached candidate in the owed file is test-only"
problems=()

test_only_owed="$work/issue-663-refactor-owed.md"
"$OWED" append "$test_only_owed" 'first step' <<'REPORT'
CANDIDATES: test-only | fold the suite's two fixture writers into one helper
CANDIDATES: test-only | hoist the stub directory into the harness
REPORT

overflow_case "with only test-only candidates in the owed file" 3 663 "$test_only_owed" 0

report "$name"

name="a report with only structural and cosmetic candidates goes through refactor-owed append, list and render, refactor-triage and refactor-overflow exactly as before test-only existed"
problems=()

TRIAGE="$HERE/../refactor-triage.sh"
first_report='RESULT: applied "split the verdict parser out of run-leaf.sh", suite green
FLAGS: none
CANDIDATES: structural | fold verify.sh'"'"'s two mktemp calls into one helper
CANDIDATES: cosmetic | reflow the header comment to ninety columns
CANDIDATES: structural | hoist the ledger path into one variable'
second_report='RESULT: applied "name the ledger path once", suite green
FLAGS: none
CANDIDATES: cosmetic | rename $tmp to $prompt_file
CANDIDATES: structural | hoist the ledger path into one variable'
cosmetic_report='CANDIDATES: cosmetic | reflow the header comment to ninety columns'

two_class_owed="$work/issue-505-refactor-owed.md"
"$OWED" append "$two_class_owed" 'first step' <<<"$first_report"
"$OWED" append "$two_class_owed" 'second step' <<<"$second_report"

want_owed="### first step
- fold verify.sh's two mktemp calls into one helper
- hoist the ledger path into one variable
### second step
- hoist the ledger path into one variable"
expect_both() {
  local what="$1" want_code="$2" want_out="$3" got_code="$4" got_out="$5"
  [[ "$got_code" == "$want_code" && "$got_out" == "$want_out" ]] ||
    problems+=("$what: want exit $want_code and" "$want_out" "got exit $got_code and" "$got_out")
}

expect_both "the owed file append wrote" 0 "$want_owed" 0 "$(cat "$two_class_owed")"

got="$("$OWED" list "$two_class_owed" 2>&1)" && code=0 || code=$?
expect_both "list" 0 "hoist the ledger path into one variable
fold verify.sh's two mktemp calls into one helper" "$code" "$got"

got="$("$OWED" render "$two_class_owed" 2>&1)" && code=0 || code=$?
expect_both "render" 0 "## Refactor owed

$want_owed" "$code" "$got"

got="$("$TRIAGE" <<<"$first_report" 2>&1)" && code=0 || code=$?
expect_both "refactor-triage on structural and cosmetic lines" 0 "fold verify.sh's two mktemp calls into one helper
hoist the ledger path into one variable" "$code" "$got"

got="$("$TRIAGE" <<<"$cosmetic_report" 2>&1)" && code=0 || code=$?
expect_both "refactor-triage on cosmetic lines alone" 3 "" "$code" "$got"

title_file="$work/title-golden" body_file="$work/body-golden"
got="$(cd "$work" && env PATH="$stubdir:$PATH" FAKE_TITLE="$title_file" FAKE_BODY="$body_file" \
  "$OVERFLOW" 505 "$two_class_owed" 1 2>&1)" && code=0 || code=$?
expect_both "refactor-overflow" 0 "https://github.com/owner/name/issues/912" "$code" "$got"
expect_both "refactor-overflow's filed title" 0 "Refactor owed by #505" 0 "$(cat "$title_file" 2>/dev/null)"
expect_both "refactor-overflow's filed body" 0 "Structural candidates #505's closing pass could not reach:

- fold verify.sh's two mktemp calls into one helper" 0 "$(cat "$body_file" 2>/dev/null)"

report "$name"

name="refactor-overflow sends no label with the issue it files, makes no call that labels or edits the parent issue, and writes no file into the repository"
problems=()

repo="$work/repo"
mkdir -p "$repo/.tdd"
cp "$owed_file" "$repo/.tdd/issue-504-refactor-owed.md"
snapshot() { (cd "$repo" && find . -type f -exec cksum {} + | sort); }
before="$(snapshot)"
: > "$calls"
(cd "$repo" && env PATH="$stubdir:$PATH" FAKE_CALLS="$calls" \
  FAKE_TITLE="$work/title-5" FAKE_BODY="$work/body-5" \
  "$OVERFLOW" 504 .tdd/issue-504-refactor-owed.md 1 >"$out" 2>"$work/err") && code=0 || code=$?

[[ "$code" == 0 ]] ||
  problems+=("want exit 0, got $code: $(cat "$work/err")")
[[ -s "$calls" ]] ||
  problems+=("want the one gh call that files the issue, got none")
while IFS= read -r call; do
  [[ "$call" != *label* ]] ||
    problems+=("want no label sent or applied, got the gh call '$call'")
  [[ "$call" != *"issue edit"* && "$call" != *"issues/504"* ]] ||
    problems+=("want no call that edits the parent #504, got the gh call '$call'")
done < "$calls"
after="$(snapshot)"
[[ "$after" == "$before" ]] ||
  problems+=("want no file written into the repository, got $(diff <(printf '%s\n' "$before") <(printf '%s\n' "$after"))")

report "$name"

name="#691 refactor-overflow files the candidates listed in <skipped-file> beside the unreached ones, and files them even when every candidate was reached"
problems=()

skipped_file="$work/issue-504-structural-skipped"
printf '%s\n' "hoist the ledger path into one variable" > "$skipped_file"

title_file="$work/title-skipped" body_file="$work/body-skipped"
(cd "$work" && env PATH="$stubdir:$PATH" FAKE_TITLE="$title_file" FAKE_BODY="$body_file" \
  "$OVERFLOW" 504 "$owed_file" 1 "$skipped_file" >"$out" 2>"$work/err") && code=0 || code=$?
[[ "$code" == 0 ]] ||
  problems+=("want exit 0 with one candidate skipped and two unreached, got $code: $(cat "$work/err")")
body="$(cat "$body_file" 2>/dev/null)"
for filed in \
  "hoist the ledger path into one variable" \
  "fold verify.sh's two mktemp calls into one helper" \
  "split the verdict parser out of run-leaf.sh"
do
  [[ "$body" == *"$filed"* ]] ||
    problems+=("want '$filed' in the filed issue's body with one candidate skipped and two unreached, got '$body'")
done

title_file="$work/title-all-reached" body_file="$work/body-all-reached"
(cd "$work" && env PATH="$stubdir:$PATH" FAKE_TITLE="$title_file" FAKE_BODY="$body_file" \
  "$OVERFLOW" 504 "$owed_file" 3 "$skipped_file" >"$out" 2>"$work/err") && code=0 || code=$?
[[ "$code" == 0 ]] ||
  problems+=("want exit 0 when every candidate was reached but one was skipped, got $code: $(cat "$work/err")")
body="$(cat "$body_file" 2>/dev/null)"
[[ "$body" == *"hoist the ledger path into one variable"* ]] ||
  problems+=("want the skipped candidate in the filed issue's body when every candidate was reached, got '$body'")

report "$name"

name="#691 refactor-overflow exits 2 and files nothing when <skipped-file> names a file that does not exist"
problems=()

overflow_case "with <skipped-file> missing" 2 504 "$owed_file" 1 "$work/no-such-skipped-file"

report "$name"

name="refactor-overflow's refusals exit 2 with exactly their usage or no-such-skipped-file line on stderr, nothing on stdout and no gh call"
problems=()

usage_line="refactor-overflow: usage: refactor-overflow.sh <n> <owed-file> <reached>"
refusal_case() {
  local label="$1" want_err="$2" got_err
  shift 2
  overflow_case "$label" 2 "$@"
  got_err="$(cat "$work/err")"
  [[ "$got_err" == "$want_err" ]] ||
    problems+=("want exactly '$want_err' on stderr $label, got '$got_err'")
}

refusal_case "with no argument" "$usage_line"
refusal_case "on a non-numeric <n>" "$usage_line" five-oh-four "$owed_file" 1
refusal_case "on a non-numeric <reached>" "$usage_line" 504 "$owed_file" two
refusal_case "on an empty <owed-file>" "$usage_line" 504 "" 1
refusal_case "with <skipped-file> missing" "refactor-overflow: no such skipped file: $work/no-such-skipped-file" \
  504 "$owed_file" 1 "$work/no-such-skipped-file"

report "$name"

name="#776 a <reached> that is not a non-negative whole number exits 2 naming <reached> on stderr"
problems=()

for value in 1.5 -1 abc "" " 7" 7x 0x10; do
  overflow_case "on <reached> '$value'" 2 504 "$owed_file" "$value"
  got_err="$(cat "$work/err")"
  [[ "$got_err" == *"<reached>"* ]] ||
    problems+=("want stderr naming <reached> on <reached> '$value', got '$got_err'")
done

report "$name"

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
