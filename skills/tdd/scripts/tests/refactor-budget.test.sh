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

name="default budget: counts 0 and 4 exit 0, count 5 exits 3, each with a one-line status"
problems=()
for probe in "0 0" "4 0" "5 3"; do
  count="${probe% *}" exp_code="${probe#* }"
  out="$(env -u VERI_REFACTOR_BUDGET "$BUDGET" "$count" 2>/dev/null)" && code=0 || code=$?
  [[ "$code" == "$exp_code" ]] ||
    problems+=("count $count: want exit $exp_code, got $code")
  [[ -n "$out" && "$out" != *$'\n'* ]] ||
    problems+=("count $count: want a one-line status on stdout, got: $(printf '%q' "$out")")
done
report "$name"

name="VERI_REFACTOR_BUDGET=0: count 0 exits 3, so the refactor loop never runs"
VERI_REFACTOR_BUDGET=0 "$BUDGET" 0 >/dev/null 2>&1 && code=0 || code=$?
if [[ "$code" == 3 ]]; then
  ok
else
  no "$name (want exit 3, got $code)"
fi

name="a non-numeric or negative VERI_REFACTOR_BUDGET exits 2 with a diagnostic on stderr and no status on stdout"
problems=()
for bad in two -1; do
  out="$(mktemp)" err="$(mktemp)"
  VERI_REFACTOR_BUDGET="$bad" "$BUDGET" 0 >"$out" 2>"$err" && code=0 || code=$?
  [[ "$code" == 2 ]] ||
    problems+=("VERI_REFACTOR_BUDGET=$bad: want exit 2, got $code")
  [[ ! -s "$out" ]] ||
    problems+=("VERI_REFACTOR_BUDGET=$bad: want no status on stdout, got: $(printf '%q' "$(cat "$out")")")
  [[ -s "$err" ]] ||
    problems+=("VERI_REFACTOR_BUDGET=$bad: want a diagnostic on stderr, got nothing")
  rm -f "$out" "$err"
done
report "$name"

count_probe() {
  local label="$1"; shift
  local out err code
  out="$(mktemp)" err="$(mktemp)"
  env -u VERI_REFACTOR_BUDGET "$BUDGET" "$@" >"$out" 2>"$err" && code=0 || code=$?
  [[ "$code" == 2 ]] ||
    problems+=("$label: want exit 2, got $code")
  [[ ! -s "$out" ]] ||
    problems+=("$label: want no status on stdout, got: $(printf '%q' "$(cat "$out")")")
  [[ -s "$err" ]] ||
    problems+=("$label: want a diagnostic on stderr, got nothing")
  rm -f "$out" "$err"
}

name="a non-numeric, negative or missing count exits 2 with a diagnostic on stderr and no status on stdout"
problems=()
count_probe "count abc" abc
count_probe "count -1" -1
count_probe "no argument"
report "$name"

name="a decimal count exits 2 with a diagnostic on stderr and no status on stdout"
problems=()
count_probe "count 1.5" 1.5
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

name="the default budget is 5: unset, count 4 exits 0 and count 5 exits 3, an explicit value still overrides, and the status line names the budget in force"
problems=()
for probe in "- 4 0 4/5" "- 5 3 5/5" "3 3 3 3/3"; do
  set -- $probe
  budget_env="$1" count="$2" exp_code="$3" exp_status="refactor $4"
  label="VERI_REFACTOR_BUDGET=$budget_env count $count"
  if [[ "$budget_env" == "-" ]]; then
    env_prefix=(-u VERI_REFACTOR_BUDGET)
  else
    env_prefix=(VERI_REFACTOR_BUDGET="$budget_env")
  fi
  out="$(env "${env_prefix[@]}" "$BUDGET" "$count" 2>/dev/null)" && code=0 || code=$?
  [[ "$code" == "$exp_code" ]] ||
    problems+=("$label: want exit $exp_code, got $code")
  [[ "$out" == "$exp_status "* ]] ||
    problems+=("$label: want a status starting '$exp_status ', got: $(printf '%q' "$out")")
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

encoded="$(stated "$BUDGET" 'VERI_REFACTOR_BUDGET:-[0-9]+')"

name="the default budget encoded in refactor-budget.sh and every prose statement of it agree"
problems=()
[[ "$encoded" =~ ^[0-9]+$ ]] ||
  problems+=("refactor-budget.sh: no VERI_REFACTOR_BUDGET default found, got: $encoded")
while IFS='|' read -r where file regex; do
  [[ -n "$where" ]] || continue
  got="$(stated "$ROOT/$file" "$regex")"
  [[ "$got" == "$encoded" ]] ||
    problems+=("$where: says $got, refactor-budget.sh encodes $encoded")
done <<'SITES'
refactor-budget.sh-header|skills/tdd/scripts/refactor-budget.sh|VERI_REFACTOR_BUDGET \(default [0-9]+
SKILL.md-refactor|skills/tdd/SKILL.md|VERI_REFACTOR_BUDGET.{0,3} \(default [0-9]+
SITES
report "$name"

name="--issue reads VERI_ISSUE_REFACTOR_BUDGET (default 3): exit 0 under it, 3 once spent, 2 on a bad value; without the flag VERI_REFACTOR_BUDGET still applies"
problems=()
while IFS='|' read -r label envs args exp_code exp_err; do
  [[ -n "$label" ]] || continue
  read -ra env_words <<<"$envs"
  read -ra arg_words <<<"$args"
  err="$(env -u VERI_ISSUE_REFACTOR_BUDGET -u VERI_REFACTOR_BUDGET "${env_words[@]}" \
    "$BUDGET" "${arg_words[@]}" 2>&1 >/dev/null)" && code=0 || code=$?
  [[ "$code" == "$exp_code" ]] ||
    problems+=("$label: want exit $exp_code, got $code")
  [[ -z "$exp_err" || "$err" == *"$exp_err "* ]] ||
    problems+=("$label: want stderr naming '$exp_err', got: $(printf '%q' "$err")")
done <<'PROBES'
--issue default count 0|VERI_REFACTOR_BUDGET=0|--issue 0|0|
--issue default count 1|VERI_REFACTOR_BUDGET=0|--issue 1|0|
--issue default count 2|VERI_REFACTOR_BUDGET=0|--issue 2|0|
--issue default count 3|VERI_REFACTOR_BUDGET=0|--issue 3|3|
--issue VERI_ISSUE_REFACTOR_BUDGET=10 count 9|VERI_REFACTOR_BUDGET=0 VERI_ISSUE_REFACTOR_BUDGET=10|--issue 9|0|
--issue VERI_ISSUE_REFACTOR_BUDGET=10 count 10|VERI_REFACTOR_BUDGET=0 VERI_ISSUE_REFACTOR_BUDGET=10|--issue 10|3|
--issue VERI_ISSUE_REFACTOR_BUDGET=two|VERI_ISSUE_REFACTOR_BUDGET=two|--issue 0|2|VERI_ISSUE_REFACTOR_BUDGET
--issue VERI_ISSUE_REFACTOR_BUDGET=-1|VERI_ISSUE_REFACTOR_BUDGET=-1|--issue 0|2|VERI_ISSUE_REFACTOR_BUDGET
no flag VERI_REFACTOR_BUDGET=2 count 2|VERI_REFACTOR_BUDGET=2 VERI_ISSUE_REFACTOR_BUDGET=20|2|3|
PROBES
report "$name"

name="the refactor-budget.sh header states the --issue default as 3"
problems=()
header_default="$(stated "$BUDGET" 'VERI_ISSUE_REFACTOR_BUDGET \(default [0-9]+')"
[[ "$header_default" == 3 ]] ||
  problems+=("refactor-budget.sh header: want VERI_ISSUE_REFACTOR_BUDGET (default 3), says $header_default")
report "$name"

name="#596 --issue still refuses a bad VERI_ISSUE_REFACTOR_BUDGET and honours an explicit 10; without --issue the default stays 5"
problems=()
while IFS='|' read -r label envs args exp_code exp_status; do
  [[ -n "$label" ]] || continue
  read -ra env_words <<<"$envs"
  read -ra arg_words <<<"$args"
  out="$(env -u VERI_ISSUE_REFACTOR_BUDGET -u VERI_REFACTOR_BUDGET "${env_words[@]}" \
    "$BUDGET" "${arg_words[@]}" 2>/dev/null)" && code=0 || code=$?
  [[ "$code" == "$exp_code" ]] ||
    problems+=("$label: want exit $exp_code, got $code")
  if [[ -z "$exp_status" ]]; then
    [[ -z "$out" ]] || problems+=("$label: want no status on stdout, got: $(printf '%q' "$out")")
  else
    [[ "$out" == "refactor $exp_status "* ]] ||
      problems+=("$label: want a status starting 'refactor $exp_status ', got: $(printf '%q' "$out")")
  fi
done <<'PROBES'
--issue VERI_ISSUE_REFACTOR_BUDGET=two|VERI_ISSUE_REFACTOR_BUDGET=two|--issue 0|2|
--issue VERI_ISSUE_REFACTOR_BUDGET=-1|VERI_ISSUE_REFACTOR_BUDGET=-1|--issue 0|2|
--issue VERI_ISSUE_REFACTOR_BUDGET=1.5|VERI_ISSUE_REFACTOR_BUDGET=1.5|--issue 0|2|
--issue VERI_ISSUE_REFACTOR_BUDGET=10 count 9|VERI_ISSUE_REFACTOR_BUDGET=10|--issue 9|0|9/10
--issue VERI_ISSUE_REFACTOR_BUDGET=10 count 10|VERI_ISSUE_REFACTOR_BUDGET=10|--issue 10|3|10/10
no flag, VERI_REFACTOR_BUDGET unset, count 4|VERI_ISSUE_REFACTOR_BUDGET=3|4|0|4/5
no flag, VERI_REFACTOR_BUDGET unset, count 5|VERI_ISSUE_REFACTOR_BUDGET=3|5|3|5/5
PROBES
report "$name"

finish
