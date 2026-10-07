#!/usr/bin/env bash
# Tests for scripts/tick-ledger.sh — the in-place ledger checkbox tick (file wrapper over
# the tested tick-criterion.sh transform). Operates on a real temp file.
#
# Run: scripts/tests/tick-ledger.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
TICK="$HERE/../tick-ledger.sh"
source "$HERE/lib/harness.sh"

work="$(scratch_dir)"

led="$work/issue-42.md"
seed() { printf '# Plan for #42\n\n- [ ] add lowercasing\n- [ ] collapse to single hyphen\n- [ ] strip edge hyphens\n' > "$led"; }

seed
"$TICK" "$led" "collapse to single hyphen"; code=$?
{ [[ "$code" == 0 ]] \
  && grep -q '^- \[x\] collapse to single hyphen$' "$led" \
  && grep -q '^- \[ \] add lowercasing$' "$led" \
  && grep -q '^- \[ \] strip edge hyphens$' "$led"; } && ok || no "ticks matching step in place (code=$code)"

seed
before="$(cat "$led")"
"$TICK" "$led" "nonexistent step" 2>/dev/null; code=$?
{ [[ "$code" == 3 ]] && [[ "$(cat "$led")" == "$before" ]]; } && ok || no "no match → exit 3, file unchanged (code=$code)"

"$TICK" > "$work/usage.out" 2> "$work/usage.err"; code=$?
want_err='usage: tick-ledger.sh [--refactor-pending] <ledger-file> <matcher>'
{ [[ "$code" == 2 ]] && [[ ! -s "$work/usage.out" ]] && [[ "$(cat "$work/usage.err")" == "$want_err" ]]; } \
  && ok || no "no argument → exit 2, nothing on stdout, the usage line on stderr (code=$code out='$(cat "$work/usage.out")' err='$(cat "$work/usage.err")')"

mkdir "$work/dir-ledger.md"
"$TICK" "$work/dir-ledger.md" "collapse to single hyphen" > "$work/dir.out" 2> "$work/dir.err"; code=$?
dir_err="$(cat "$work/dir.err")"
{ [[ "$code" == 2 ]] && [[ ! -s "$work/dir.out" ]] && [[ "$(wc -l < "$work/dir.err")" -eq 1 ]] \
  && [[ "$dir_err" == *"$work/dir-ledger.md"* ]] && [[ "$dir_err" == *[Dd]irectory* ]] \
  && [[ "$dir_err" != *Traceback* ]]; } \
  && ok || no "#1083: a directory as the ledger → exit 2, one stderr line naming the path and the reason, no traceback (code=$code err='$dir_err')"

"$TICK" "$work/absent-ledger.md" "collapse to single hyphen" > "$work/absent.out" 2> "$work/absent.err"; code=$?
absent_err="$(cat "$work/absent.err")"
{ [[ "$code" == 2 ]] && [[ ! -s "$work/absent.out" ]] && [[ "$(wc -l < "$work/absent.err")" -eq 1 ]] \
  && [[ "$absent_err" == *"$work/absent-ledger.md"* ]] && [[ "$absent_err" != *Traceback* ]]; } \
  && ok || no "#1083: a ledger path that does not exist → exit 2, one stderr line naming the path, no traceback (code=$code err='$absent_err')"

printf 'not a directory\n' > "$work/plain-file"
"$TICK" "$work/plain-file/issue-42.md" "collapse to single hyphen" > "$work/notdir.out" 2> "$work/notdir.err"; code=$?
notdir_err="$(cat "$work/notdir.err")"
{ [[ "$code" == 2 ]] && [[ ! -s "$work/notdir.out" ]] && [[ "$(wc -l < "$work/notdir.err")" -eq 1 ]] \
  && [[ "$notdir_err" == "tick-ledger.sh: $work/plain-file/issue-42.md: "?* ]] && [[ "$notdir_err" != *Traceback* ]] \
  && [[ "$(cat "$work/plain-file")" == 'not a directory' ]]; } \
  && ok || no "#1118: a ledger path running through a regular file → exit 2, one 'tick-ledger.sh: <path>: <reason>' stderr line, no traceback, nothing written (code=$code err='$notdir_err')"

printf '\377\376- [ ] collapse to single hyphen\n' > "$work/undecodable.md"
cp "$work/undecodable.md" "$work/undecodable.orig"
LC_ALL=C.UTF-8 "$TICK" "$work/undecodable.md" "collapse to single hyphen" > "$work/undecodable.out" 2> "$work/undecodable.err"; code=$?
undecodable_err="$(cat "$work/undecodable.err")"
{ [[ "$code" == 2 ]] && [[ ! -s "$work/undecodable.out" ]] && [[ "$(wc -l < "$work/undecodable.err")" -eq 1 ]] \
  && [[ "$undecodable_err" == "tick-ledger.sh: $work/undecodable.md: "?* ]] && [[ "$undecodable_err" != *Traceback* ]] \
  && cmp -s "$work/undecodable.md" "$work/undecodable.orig"; } \
  && ok || no "#1118: a ledger holding bytes that do not decode under a UTF-8 locale → exit 2, one 'tick-ledger.sh: <path>: <reason>' stderr line, no traceback, ledger byte-identical (code=$code err='$undecodable_err')"

CLEAR="$HERE/../clear-refactor-pending.sh"
seed
"$TICK" "$led" "nonexistent step" 2>/dev/null; tick_miss=$?
"$TICK" --refactor-pending "$led" "collapse to single hyphen" 2>/dev/null; tick_hit=$?
"$CLEAR" "$led" "nonexistent step" 2>/dev/null; clear_miss=$?
"$CLEAR" "$led" "collapse to single hyphen" 2>/dev/null; clear_hit=$?
{ [[ "$tick_miss" == 3 && "$tick_hit" == 0 && "$clear_miss" == 3 && "$clear_hit" == 0 ]] \
  && grep -q '^- \[x\] collapse to single hyphen$' "$led"; } \
  && ok || no "#1083: on a readable ledger tick-ledger.sh and clear-refactor-pending.sh exit 3 on no match and 0 on a tick or clear (tick miss=$tick_miss hit=$tick_hit, clear miss=$clear_miss hit=$clear_hit)"

ln -s "$(cd "$HERE/../.." && pwd)" "$work/linked-skill"
mkdir -p "$work/in-place" "$work/caller"
seed_in() { printf '# Plan for #42\n\n- [ ] add lowercasing\n- [ ] collapse to single hyphen\n' > "$1/issue-42.md"; }
seed_in "$work/in-place"; seed_in "$work/caller"
in_place="$(cd "$work/in-place" && "$TICK" --refactor-pending issue-42.md "collapse to single hyphen" 2>&1)"; in_place_code=$?
linked="$(cd "$work/caller" && "$work/linked-skill/scripts/tick-ledger.sh" --refactor-pending issue-42.md "collapse to single hyphen" 2>&1)"; linked_code=$?
if [[ "$linked" == "$in_place" && "$linked_code" -eq "$in_place_code" && "$in_place_code" -eq 0 ]] \
  && cmp -s "$work/in-place/issue-42.md" "$work/caller/issue-42.md" \
  && grep -F -- '- [x] collapse to single hyphen ⟂ refactor pending' "$work/caller/issue-42.md" > /dev/null; then ok; else
  no "tick-ledger.sh run through a symlink to the skill directory and from another working directory ticks the relative ledger under the caller's working directory as it does when run in place"
  diff <(printf '%s\nexit %s\n' "$in_place" "$in_place_code"; cat "$work/in-place/issue-42.md") <(printf '%s\nexit %s\n' "$linked" "$linked_code"; cat "$work/caller/issue-42.md")
fi

finish
