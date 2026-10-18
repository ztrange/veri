#!/usr/bin/env bash
# Tests for scripts/add-ledger-step.sh — inserts a step, marked ⟦added⟧, next to an anchor
# step already in the plan. Operates on a real temp file.
#
# Run: scripts/tests/add-ledger-step.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ADD="$HERE/../add-ledger-step.sh"
source "$HERE/lib/harness.sh"

check_code() {
  local name="$1" code="$2" want_code="$3" want="$4" got
  got="$(cat "$led")"
  if [[ "$code" == "$want_code" && "$got" == "$want" ]]; then
    ok
  else
    no "$name (code=$code)"
    diff <(printf '%s\n' "$want") <(printf '%s\n' "$got") | sed 's/^/    /'
  fi
}

check() { check_code "$1" "$2" 0 "$3"; }

work="$(scratch_dir)"

led="$work/issue-42.md"

seeded='# Plan for #42

- [x] lowercase the slug ⟦criterion 1⟧
- [ ] collapse to single hyphen ⟦criterion 2⟧
- [ ] strip edge hyphens ⟦criterion 3⟧'

seed() { printf '%s\n' "$seeded" > "$led"; }

seed
"$ADD" "$led" after 'collapse to single hyphen' 'collapse a unicode dash too'; code=$?
want='# Plan for #42

- [x] lowercase the slug ⟦criterion 1⟧
- [ ] collapse to single hyphen ⟦criterion 2⟧
- [ ] collapse a unicode dash too ⟦added⟧ ⟦criterion 2⟧
- [ ] strip edge hyphens ⟦criterion 3⟧'
check "after: inserts the added step below the anchor, carrying its criterion" "$code" "$want"

seed
VERI_STEP_GROWTH=1 "$ADD" "$led" before 'collapse to single hyphen' 'one more edge case' 'and another'; code=$?
want="$seeded"'

## Owed steps

- one more edge case
- and another'
check_code "over budget: inserts no checkbox, exits 1, and owes both texts as plain bullets" \
  "$code" 1 "$want"

usage='usage: add-ledger-step.sh [--criterion <k>] <ledger-file> after|before|instead-of <anchor-substring> <text> [<text> …]  (--planned goes with --criterion <k>)'
name="no argument, and three arguments, each exit 2 with nothing on stdout and stderr exactly the usage line"
"$ADD" > "$work/usage0.out" 2> "$work/usage0.err"; code0=$?
"$ADD" l.md after anchor > "$work/usage3.out" 2> "$work/usage3.err"; code3=$?
if [[ "$code0" == 2 && ! -s "$work/usage0.out" && "$(cat "$work/usage0.err")" == "$usage" \
   && "$code3" == 2 && ! -s "$work/usage3.out" && "$(cat "$work/usage3.err")" == "$usage" ]]; then
  ok
else
  no "$name (code0=$code0, code3=$code3)"
  sed 's/^/    0 args stderr: /' "$work/usage0.err"
  sed 's/^/    3 args stderr: /' "$work/usage3.err"
fi

name="run through a symlink to the skill directory and from another working directory, a relative <ledger-file> is read and rewritten in the caller's working directory exactly as when run in place"
ln -s "$(cd "$HERE/../.." && pwd)" "$work/linked-skill"
linked_add="$work/linked-skill/scripts/add-ledger-step.sh"
mkdir -p "$work/in-place" "$work/elsewhere"
printf '%s\n' "$seeded" > "$work/in-place/l.md"
printf '%s\n' "$seeded" > "$work/elsewhere/l.md"
(cd "$work/in-place" && "$ADD" l.md after 'collapse to single hyphen' 't' 2> "$work/in-place.after.err"); in_after=$?
(cd "$work/elsewhere" && "$linked_add" l.md after 'collapse to single hyphen' 't' 2> "$work/linked.after.err"); linked_after=$?
(cd "$work/in-place" && "$ADD" l.md after 'no such step' 't' 2> "$work/in-place.none.err"); in_none=$?
(cd "$work/elsewhere" && "$linked_add" l.md after 'no such step' 't' 2> "$work/linked.none.err"); linked_none=$?
if [[ "$in_after" == 0 && "$linked_after" == 0 && "$in_none" == 2 && "$linked_none" == 2 ]] \
   && grep -Fx -- '- [ ] t ⟦added⟧ ⟦criterion 2⟧' "$work/in-place/l.md" > /dev/null \
   && cmp -s "$work/in-place/l.md" "$work/elsewhere/l.md" \
   && cmp -s "$work/in-place.after.err" "$work/linked.after.err" \
   && [[ "$(cat "$work/in-place.none.err")" == "add-ledger-step.sh: anchor matches no single step: no such step" ]] \
   && cmp -s "$work/in-place.none.err" "$work/linked.none.err"; then
  ok
else
  no "$name (after: in place $in_after, linked $linked_after; no match: in place $in_none, linked $linked_none)"
  diff "$work/in-place/l.md" "$work/elsewhere/l.md" | sed 's/^/    ledger: /'
  diff "$work/in-place.none.err" "$work/linked.none.err" | sed 's/^/    stderr: /'
fi

name="#1579: the shim header describes --planned (no ⟦added⟧, not counted toward VERI_STEP_GROWTH) and its exit-2 list names --planned without --criterion, a criterion a ledger step already serves, no readable spec file, and a k not unticked in the issue body, and no longer lists a --criterion no ledger step carries"
hdr="$(sed -n '/^#/p' "$ADD")"
exit2="$(printf '%s\n' "$hdr" | sed -n '/^# Exit:/,$p')"
missing=""
printf '%s\n' "$hdr" | grep -F -- '--planned' | grep -F 'VERI_STEP_GROWTH' > /dev/null || missing="$missing [header: --planned not counted toward VERI_STEP_GROWTH]"
printf '%s\n' "$hdr" | grep -F -- '--planned' | grep -F '⟦added⟧' > /dev/null || missing="$missing [header: --planned without ⟦added⟧]"
printf '%s\n' "$exit2" | grep -F -- '--planned without --criterion' > /dev/null || missing="$missing [exit 2: --planned without --criterion]"
printf '%s\n' "$exit2" | grep -F 'already serves' > /dev/null || missing="$missing [exit 2: a criterion a ledger step already serves]"
printf '%s\n' "$exit2" | grep -F 'unticked in the issue body' > /dev/null || missing="$missing [exit 2: k not unticked in the issue body]"
printf '%s\n' "$exit2" | grep -F 'readable spec file' > /dev/null || missing="$missing [exit 2: --planned with no readable spec file]"
printf '%s\n' "$exit2" | grep -F 'no ledger step carries' > /dev/null && missing="$missing [exit 2 still lists a --criterion no ledger step carries, which exits 0 since #1292]"
if [[ -z "$missing" ]]; then
  ok
else
  no "$name (missing:$missing)"
fi

name="#1579: SCRIPTS.md's add-ledger-step.sh entry documents --planned (no ⟦added⟧, not counted toward VERI_STEP_GROWTH) and its exit-2 refusals: no --criterion, an already-served criterion, no readable spec file, a k not unticked in the issue body"
entry="$(sed -n '/^- `\$S\/add-ledger-step\.sh /,/^- `\$S\/classify-bail\.sh/p' "$HERE/../../SCRIPTS.md")"
missing=""
printf '%s\n' "$entry" | grep -F -- '--planned' | grep -F 'VERI_STEP_GROWTH' > /dev/null || missing="$missing [--planned not counted toward VERI_STEP_GROWTH]"
printf '%s\n' "$entry" | grep -F -- '--planned' | grep -F '⟦added⟧' > /dev/null || missing="$missing [--planned without ⟦added⟧]"
printf '%s\n' "$entry" | grep -F -- '--planned without --criterion' > /dev/null || missing="$missing [exit 2: --planned without --criterion]"
printf '%s\n' "$entry" | grep -F 'already serves' > /dev/null || missing="$missing [exit 2: a criterion a ledger step already serves]"
printf '%s\n' "$entry" | grep -F 'unticked in the issue body' > /dev/null || missing="$missing [exit 2: k not unticked in the issue body]"
printf '%s\n' "$entry" | grep -F 'cannot read the spec file' > /dev/null || missing="$missing [exit 2: no readable spec file]"
if [[ -z "$missing" ]]; then
  ok
else
  no "$name (missing:$missing)"
fi

name="#1538: add-ledger-step.sh asked to insert a replaces-case step whose replaces clause has an unquoted name after a quoted one, or a quoted name followed by a trailing parenthetical, exits 1, prints a line naming that step and leaves the ledger byte-identical"
shape=""
for text in "x: replaces 'a', b in t/x.test.sh ⟦replaces-case⟧" "x: replaces 'a' (from #12) in t/x.test.sh ⟦replaces-case⟧"; do
  seed
  "$ADD" "$led" after 'collapse to single hyphen' "$text" > "$work/unread.out" 2> "$work/unread.err"; code=$?
  names=no; grep -F "$text" "$work/unread.err" > /dev/null && names=yes
  trace=no; grep -F 'Traceback' "$work/unread.err" > /dev/null && trace=yes
  same=no; [[ "$(cat "$led")" == "$seeded" ]] && same=yes
  shape="$shape $code:$(wc -l < "$work/unread.err" | tr -d ' '):$names:$trace:$same"
done
if [[ "$shape" == " 1:1:yes:no:yes 1:1:yes:no:yes" ]]; then
  ok
else
  no "$name (code:lines:names-step:traceback:ledger-unchanged =$shape)"
fi

name="#1619: add-ledger-step.sh inserting a second ⟦suite-repair⟧ step while .tdd/events.jsonl holds a line that is not UTF-8 exits 2, prints no traceback, names the log and leaves the ledger byte-identical"
mkdir -p "$work/nonutf8/.tdd"
nled="$work/nonutf8/.tdd/issue-42.md"
nlog="$work/nonutf8/.tdd/events.jsonl"
printf '%s\n' "$seeded" '- [x] fix the full-suite failure: first.test.sh ⟦suite-repair⟧ ⟦criterion 1⟧' > "$nled"
nbefore="$(cat "$nled")"
printf '{"ts":1,"issue":"42","event":"resume"}\n\377\376 broken\n' > "$nlog"
"$ADD" "$nled" after 'strip edge hyphens' 'fix the full-suite failure: second.test.sh ⟦suite-repair⟧' > "$work/nonutf8.out" 2> "$work/nonutf8.err"; code=$?
names=no; grep -F "$nlog" "$work/nonutf8.err" > /dev/null && names=yes
trace=no; grep -F 'Traceback' "$work/nonutf8.err" > /dev/null && trace=yes
same=no; [[ "$(cat "$nled")" == "$nbefore" ]] && same=yes
if [[ "$code:$names:$trace:$same" == "2:yes:no:yes" ]]; then
  ok
else
  no "$name (code:names-log:traceback:ledger-unchanged=$code:$names:$trace:$same)"
fi

finish
