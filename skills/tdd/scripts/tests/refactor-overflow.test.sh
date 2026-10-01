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

finish
