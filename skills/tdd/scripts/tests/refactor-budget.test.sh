#!/usr/bin/env bash
# Unit tests for scripts/refactor-budget.sh — given the number of transforms done so far,
# it says whether another refactor leaf may run.
#
# Contract under test:
#   refactor-budget.sh <count>  → exit 0 while <count> is below VERI_REFACTOR_BUDGET
#                                 (default 5), exit 3 once the budget is spent;
#                                 a one-line status on stdout either way
#                                 (`refactor 5/5 — budget spent`).
#   VERI_REFACTOR_BUDGET=0      → exit 3 at count 0: the refactor loop is switched off.
#
# Run: scripts/tests/refactor-budget.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
BUDGET="$HERE/../refactor-budget.sh"

source "$HERE/lib/harness.sh"

name="a bad count exits 2 with nothing on stdout and stderr naming the count, then the usage line"
problems=()
out="$(mktemp)" err="$(mktemp)"
env -u VERI_REFACTOR_BUDGET -u VERI_ISSUE_REFACTOR_BUDGET "$BUDGET" ten >"$out" 2>"$err" && code=0 || code=$?
[[ "$code" == 2 ]] ||
  problems+=("count ten: want exit 2, got $code")
[[ ! -s "$out" ]] ||
  problems+=("count ten: want nothing on stdout, got: $(printf '%q' "$(cat "$out")")")
want_err='refactor-budget: <count> must be a whole number >= 0: ten
usage: refactor-budget.sh [--issue] <count>
'
got_err="$(cat "$err"; printf x)" got_err="${got_err%x}"
[[ "$got_err" == "$want_err" ]] ||
  problems+=("count ten: want stderr $(printf '%q' "$want_err"), got: $(printf '%q' "$got_err")")
rm -f "$out" "$err"
report "$name"

name="valid counts 0, 4 and 5 keep their answers — exit 0, 0, 3, one line on stdout, nothing on stderr"
problems=()
for probe in "0 0" "4 0" "5 3"; do
  count="${probe% *}" exp_code="${probe#* }"
  out="$(mktemp)" err="$(mktemp)"
  env -u VERI_REFACTOR_BUDGET "$BUDGET" "$count" >"$out" 2>"$err" && code=0 || code=$?
  [[ "$code" == "$exp_code" ]] ||
    problems+=("count $count: want exit $exp_code, got $code")
  [[ "$(wc -l <"$out")" -eq 1 && -s "$out" ]] ||
    problems+=("count $count: want a one-line status on stdout, got: $(printf '%q' "$(cat "$out")")")
  [[ ! -s "$err" ]] ||
    problems+=("count $count: want nothing on stderr, got: $(printf '%q' "$(cat "$err")")")
  rm -f "$out" "$err"
done
report "$name"

ROOT="$(cd "$HERE/../../../.." && pwd)"

stated() {
  local hit
  [[ -f "$1" ]] || { echo '<no-file>'; return; }
  hit="$(head -1 < <(tr '\n' ' ' < "$1" | grep -oE "$2"))"
  [[ -n "$hit" ]] || { echo '<none>'; return; }
  printf '%s' "$hit" | grep -oE '[0-9]+' | tail -1
}

name="the refactor-budget.sh header states the --issue default as 3"
problems=()
header_default="$(stated "$BUDGET" 'VERI_ISSUE_REFACTOR_BUDGET \(default [0-9]+')"
[[ "$header_default" == 3 ]] ||
  problems+=("refactor-budget.sh header: want VERI_ISSUE_REFACTOR_BUDGET (default 3), says $header_default")
report "$name"

name="#596 no tracked file outside the docs and .tdd trees states 10 as the VERI_ISSUE_REFACTOR_BUDGET default"
problems=()
issue_var=VERI_ISSUE_REFACTOR_BUDGET
old_default=10
stale="${issue_var}(:-|[^0-9]{0,40}default[^0-9]{0,4})${old_default}([^0-9]|$)"
hits="$(git -C "$ROOT" grep -nE "$stale" -- . ':!docs' ':!projects/docs' ':!.tdd' 2>/dev/null)"
[[ -z "$hits" ]] ||
  problems+=("want no statement of default $old_default for $issue_var, found:"$'\n'"$hits")
report "$name"

name="refactor-budget.sh run through a symlink to the skill directory and from another working directory answers as it does when run in place"
problems=()
work="$(scratch_dir)"
ln -s "$(cd "$HERE/../.." && pwd)" "$work/linked-skill"
mkdir -p "$work/elsewhere"
while IFS='|' read -r count exp_code exp_out; do
  [[ -n "$count" ]] || continue
  in_place="$(env -u VERI_REFACTOR_BUDGET -u VERI_ISSUE_REFACTOR_BUDGET "$BUDGET" "$count" 2>/dev/null)" && in_place_code=0 || in_place_code=$?
  linked="$(cd "$work/elsewhere" && env -u VERI_REFACTOR_BUDGET -u VERI_ISSUE_REFACTOR_BUDGET \
    "$work/linked-skill/scripts/refactor-budget.sh" "$count" 2>/dev/null)" && linked_code=0 || linked_code=$?
  [[ "$linked" == "$exp_out" && "$linked_code" == "$exp_code" ]] ||
    problems+=("count $count linked: want exit $exp_code and $(printf '%q' "$exp_out"), got exit $linked_code and $(printf '%q' "$linked")")
  [[ "$linked" == "$in_place" && "$linked_code" == "$in_place_code" ]] ||
    problems+=("count $count: linked answered exit $linked_code $(printf '%q' "$linked"), in place exit $in_place_code $(printf '%q' "$in_place")")
done <<'PROBES'
4|0|refactor 4/5 — another transform may run
5|3|refactor 5/5 — budget spent
ten|2|
PROBES
report "$name"

finish
