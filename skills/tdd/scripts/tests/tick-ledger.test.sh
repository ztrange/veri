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

printf -- '- [x] collapse to single hyphen\n- [ ] collapse to single hyphen (again)\n' > "$led"
"$TICK" "$led" "collapse to single hyphen"; code=$?
{ [[ "$code" == 0 ]] && grep -q '^- \[x\] collapse to single hyphen (again)$' "$led"; } \
  && ok || no "skips checked, ticks next matching (code=$code)"

seed
"$TICK" --refactor-pending "$led" "collapse to single hyphen"; marked=$?
"$TICK" "$led" "strip edge hyphens"; plain=$?
{ [[ "$marked" == 0 ]] && [[ "$plain" == 0 ]] \
  && grep -q '^- \[x\] collapse to single hyphen ⟂ refactor pending$' "$led" \
  && grep -q '^- \[x\] strip edge hyphens$' "$led"; } \
  && ok || no "--refactor-pending marks the ticked line, plain tick does not (marked=$marked plain=$plain)"

S="$HERE/.."
printf -- '- [x] add lowercasing ⟦criterion 1⟧\n- [ ] collapse to single hyphen ⟦criterion 1⟧\n- [ ] strip edge hyphens\n' > "$led"
want_step='collapse to single hyphen ⟦criterion 1⟧'
next="$("$S/next-unchecked.sh" < "$led")"; c_next=$?
"$TICK" --refactor-pending "$led" "$next"; c_tick=$?
marked_line="$(sed -n 2p "$led")"
pending="$("$S/next-pending-refactor.sh" < "$led")"; c_pend=$?
"$S/clear-refactor-pending.sh" "$led" "$pending"; c_clear=$?
want_led="$(printf -- '- [x] add lowercasing ⟦criterion 1⟧\n- [x] collapse to single hyphen ⟦criterion 1⟧\n- [ ] strip edge hyphens')"
{ [[ "$c_next$c_tick$c_pend$c_clear" == 0000 ]] \
  && [[ "$next" == "$want_step" ]] \
  && [[ "$marked_line" == "- [x] $want_step ⟂ refactor pending" ]] \
  && [[ "$pending" == "$want_step" ]] \
  && [[ "$(cat "$led")" == "$want_led" ]]; } \
  && ok || no "criterion notation: the four ledger scripts match and print step text as without it (codes=$c_next$c_tick$c_pend$c_clear next='$next' marked='$marked_line' pending='$pending' ledger='$(cat "$led")')"

stub="$work/stub"
mkdir -p "$stub/lib"
cp "$TICK" "$stub/tick-ledger.sh"
cp "$HERE/../tick-criterion.sh" "$stub/tick-criterion.sh"
cp "$HERE/.."/lib/*.sh "$stub/lib/"
cat > "$stub/lib/ledger.sh" <<'EOF'
ledger_tick() {
  cat > /dev/null
  printf 'ledger_tick [%s] [%s]\n' "$1" "${2:-}"
}
EOF
seed
"$stub/tick-ledger.sh" --refactor-pending "$led" "collapse to single hyphen"; code=$?
got="$(cat "$led")"
want='ledger_tick [collapse to single hyphen] [pending]'
{ [[ "$code" == 0 ]] && [[ "$got" == "$want" ]]; } \
  && ok || no "--refactor-pending ticks through lib/ledger.sh's ledger_tick … pending (code=$code)
$(diff <(printf '%s\n' "$want") <(printf '%s\n' "$got"))"

foreign="$work/foreign"
mkdir -p "$foreign/lib"
cp "$TICK" "$foreign/tick-ledger.sh"
cp "$HERE/../clear-refactor-pending.sh" "$foreign/clear-refactor-pending.sh"
cp "$HERE/.."/lib/*.sh "$foreign/lib/"
cat > "$foreign/lib/ledger.sh" <<'EOF'
ledger_tick() { cat > /dev/null; return 7; }
ledger_clear_pending() { cat > /dev/null; return 7; }
EOF
seed
"$foreign/tick-ledger.sh" "$led" "collapse to single hyphen" 2>/dev/null; tick=$?
"$foreign/clear-refactor-pending.sh" "$led" "collapse to single hyphen" 2>/dev/null; clear=$?
{ [[ "$tick" == 2 ]] && [[ "$clear" == 2 ]]; } \
  && ok || no "a foreign ledger-transform code exits 2 from tick-ledger.sh and clear-refactor-pending.sh (tick=$tick clear=$clear)"

"$TICK" > "$work/usage.out" 2> "$work/usage.err"; code=$?
want_err='usage: tick-ledger.sh [--refactor-pending] <ledger-file> <matcher>'
{ [[ "$code" == 2 ]] && [[ ! -s "$work/usage.out" ]] && [[ "$(cat "$work/usage.err")" == "$want_err" ]]; } \
  && ok || no "no argument → exit 2, nothing on stdout, the usage line on stderr (code=$code out='$(cat "$work/usage.out")' err='$(cat "$work/usage.err")')"

"$TICK" "$work/no-such-ledger.md" "collapse to single hyphen" > "$work/missing.out" 2> /dev/null; code=$?
{ [[ "$code" == 1 ]] && [[ ! -s "$work/missing.out" ]]; } \
  && ok || no "a missing ledger → exit 1, nothing on stdout (code=$code out='$(cat "$work/missing.out")')"

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
