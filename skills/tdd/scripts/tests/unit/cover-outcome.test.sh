#!/usr/bin/env bash
# Unit tests for scripts/cover-outcome.sh — the pure transform that reads a cover leaf's
# report on stdin and says whether the code a refactor step will move is covered, so the
# conductor can go on to Transform or refuse the step.
# Fast tier by its own usage count: git 0, python3 0, server 0, sleep 0.
#
# Contract under test:
#   stdin  = the cover leaf's report (the COVERED:/CAUGHT_BY:/MUTATION: lines at its end)
#   stdout = on COVERED: yes, the test the report's CAUGHT_BY: line names
#   exit   = 0 COVERED: yes · 1 COVERED: no · 2 no readable COVERED: line
#
# Run: scripts/tests/unit/cover-outcome.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
COVER_OUTCOME="$HERE/../../cover-outcome.sh"
source "$HERE/../lib/harness.sh"

run_on() {
  out="$(printf '%s' "$1" | "$COVER_OUTCOME" 2>/dev/null)" && code=0 || code=$?
}

verdict() {
  local name="$1" p
  if (( ${#problems[@]} )); then
    no "$name"
    for p in "${problems[@]}"; do echo "    $p"; done
  else
    ok
  fi
}

caught_by='widget.test.sh: a stubbed widget stays blue'
mutation='widget.sh: painted the widget red'

name="COVERED: yes exits 0 printing CAUGHT_BY, COVERED: no exits 1, neither exits 2"
problems=()
run_on "some narration
COVERED: yes
CAUGHT_BY: $caught_by
MUTATION: $mutation"
[[ "$code" == 0 ]] || problems+=("COVERED: yes: want exit 0, got $code")
[[ "$out" == "$caught_by" ]] || problems+=("COVERED: yes: want stdout '$caught_by', got '$(printf '%s' "$out" | tr '\n' '|')'")
run_on "some narration
COVERED: no
CAUGHT_BY: NONE
MUTATION: $mutation"
[[ "$code" == 1 ]] || problems+=("COVERED: no: want exit 1, got $code")
run_on "some narration with no report lines at all"
[[ "$code" == 2 ]] || problems+=("no COVERED: line: want exit 2, got $code")
verdict "$name"

name="#679: COVERED: unreachable or type-only with a PROOF: line exits 3 printing '<kind>: <proof>'"
problems=()
proof='useWidgetSync: its one caller, WidgetPanel, passes onChange={() => {}}'
run_on "some narration
COVERED: unreachable
CAUGHT_BY: NONE
PROOF: $proof
MUTATION: NONE"
[[ "$code" == 3 ]] || problems+=("COVERED: unreachable: want exit 3, got $code")
[[ "$out" == "unreachable: $proof" ]] || problems+=("COVERED: unreachable: want stdout 'unreachable: $proof', got '$(printf '%s' "$out" | tr '\n' '|')'")
proof='npx tsc --noEmit'
run_on "some narration
COVERED: type-only
CAUGHT_BY: NONE
PROOF: $proof
MUTATION: NONE"
[[ "$code" == 3 ]] || problems+=("COVERED: type-only: want exit 3, got $code")
[[ "$out" == "type-only: $proof" ]] || problems+=("COVERED: type-only: want stdout 'type-only: $proof', got '$(printf '%s' "$out" | tr '\n' '|')'")
verdict "$name"

name="#679: COVERED: unreachable or type-only with no PROOF: line or PROOF: NONE exits 2"
problems=()
for kind in unreachable type-only; do
  run_on "some narration
COVERED: $kind
CAUGHT_BY: NONE
MUTATION: NONE"
  [[ "$code" == 2 ]] || problems+=("COVERED: $kind with no PROOF: line: want exit 2, got $code")
  run_on "some narration
COVERED: $kind
CAUGHT_BY: NONE
PROOF: NONE
MUTATION: NONE"
  [[ "$code" == 2 ]] || problems+=("COVERED: $kind with PROOF: NONE: want exit 2, got $code")
done
verdict "$name"

name="#679: COVERED: no with a PROOF: line still exits 1"
problems=()
run_on "some narration
COVERED: no
CAUGHT_BY: NONE
PROOF: useWidgetSync: its one caller, WidgetPanel, passes onChange={() => {}}
MUTATION: $mutation"
[[ "$code" == 1 ]] || problems+=("COVERED: no with a PROOF: line: want exit 1, got $code")
verdict "$name"

name="#679: a PROOF: line leaves COVERED: yes exiting 0 printing CAUGHT_BY, COVERED: no exiting 1 and no COVERED: line exiting 2"
problems=()
proof='npx tsc --noEmit'
run_on "some narration
COVERED: yes
CAUGHT_BY: $caught_by
PROOF: $proof
MUTATION: $mutation"
[[ "$code" == 0 ]] || problems+=("COVERED: yes with a PROOF: line: want exit 0, got $code")
[[ "$out" == "$caught_by" ]] || problems+=("COVERED: yes with a PROOF: line: want stdout '$caught_by', got '$(printf '%s' "$out" | tr '\n' '|')'")
run_on "some narration
COVERED: no
CAUGHT_BY: NONE
PROOF: $proof
MUTATION: $mutation"
[[ "$code" == 1 ]] || problems+=("COVERED: no with a PROOF: line: want exit 1, got $code")
run_on "some narration with no COVERED: line
PROOF: $proof"
[[ "$code" == 2 ]] || problems+=("no COVERED: line with a PROOF: line: want exit 2, got $code")
verdict "$name"

name="a report with no COVERED: line exits 2, stdout empty, stderr exactly 'cover-outcome: no COVERED: line found'"
problems=()
err_file="$(mktemp)"
out="$(printf '%s' "some narration with no report lines at all" | "$COVER_OUTCOME" 2>"$err_file")" && code=0 || code=$?
err="$(cat "$err_file")"
rm -f "$err_file"
[[ "$code" == 2 ]] || problems+=("want exit 2, got $code")
[[ -z "$out" ]] || problems+=("want empty stdout, got '$(printf '%s' "$out" | tr '\n' '|')'")
[[ "$err" == "cover-outcome: no COVERED: line found" ]] || problems+=("want stderr 'cover-outcome: no COVERED: line found', got '$(printf '%s' "$err" | tr '\n' '|')'")
verdict "$name"

name="run through a symlink to the skill directory and from another working directory, it answers as in place"
problems=()
scratch="$(scratch_dir)"
ln -s "$(cd "$HERE/../../.." && pwd)" "$scratch/skill"
mkdir "$scratch/elsewhere"
answer() {
  local report="$1" bin="$2" dir="$3" o c
  o="$(cd "$dir" && printf '%s' "$report" | "$bin" 2>"$scratch/err")" && c=0 || c=$?
  printf 'exit=%s|stdout=%s|stderr=%s' "$c" "$o" "$(cat "$scratch/err")"
}
for report in "some narration
COVERED: yes
CAUGHT_BY: $caught_by
MUTATION: $mutation" "some narration with no report lines at all"; do
  in_place="$(answer "$report" "$COVER_OUTCOME" "$HERE")"
  linked="$(answer "$report" "$scratch/skill/scripts/cover-outcome.sh" "$scratch/elsewhere")"
  [[ "$linked" == "$in_place" ]] || problems+=("want '$in_place', got '$linked'")
done
verdict "$name"

finish
