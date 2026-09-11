#!/usr/bin/env bash
# Unit tests for scripts/refactor-budget.sh — bounds the refactor loop so a step costs
# the same on every run: given the number of transforms done so far, it says whether
# another leaf may run.
# Zero-dependency plain-shell asserts, same idiom as classify-bail.test.sh.
#
# Contract under test (issue #42):
#   refactor-budget.sh <count>  → exit 0 while <count> is below VERI_REFACTOR_BUDGET
#                                 (default 2), exit 3 once the budget is spent;
#                                 a one-line status on stdout either way, so the
#                                 conductor can mirror it (`refactor 2/2 — budget spent`).
#   VERI_REFACTOR_BUDGET=0      → exit 3 at count 0: the refactor loop is switched off.
#
# Run: scripts/tests/refactor-budget.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
BUDGET="$HERE/../refactor-budget.sh"
pass=0 fail=0

# report <name> — close a case whose probes collected into the `problems` array: an empty
# array is a pass, otherwise one FAIL line for the case and one indented line per problem,
# so the output says which probe broke rather than just that the case did.
report() {
  local name="$1"
  if [[ "${#problems[@]}" -eq 0 ]]; then
    pass=$((pass + 1))
  else
    fail=$((fail + 1))
    echo "FAIL - $name"
    printf '    %s\n' "${problems[@]}"
  fi
}

# 1. with the default budget — VERI_REFACTOR_BUDGET unset, so the script's own default
#    of 2 applies — counts 0 and 1 mean "another transform may run" (exit 0) and count 2
#    means "budget spent" (exit 3). Every answer prints a one-line status.
#    The three probes are one criterion, so they are reported as one case; `problems`
#    collects what went wrong in each so the FAIL line says which count broke.
name="default budget: counts 0 and 1 exit 0, count 2 exits 3, each with a one-line status"
problems=()
for probe in "0 0" "1 0" "2 3"; do
  count="${probe% *}" exp_code="${probe#* }"
  # env -u clears the variable for the child only, so the test never depends on — nor
  # disturbs — whatever the surrounding run has set.
  out="$(env -u VERI_REFACTOR_BUDGET "$BUDGET" "$count" 2>/dev/null)" && code=0 || code=$?
  [[ "$code" == "$exp_code" ]] ||
    problems+=("count $count: want exit $exp_code, got $code")
  # Command substitution has already eaten any trailing newline, so "exactly one line"
  # is: not empty, and no newline left inside.
  [[ -n "$out" && "$out" != *$'\n'* ]] ||
    problems+=("count $count: want a one-line status on stdout, got: $(printf '%q' "$out")")
done
report "$name"

# 2. a budget of 0 switches the refactor loop off entirely: even before any transform has
#    run — count 0 — the budget is already spent, so the very first ask gets exit 3 and no
#    leaf ever launches. The one-line status is case 1's business; this case pins the exit.
name="VERI_REFACTOR_BUDGET=0: count 0 exits 3, so the refactor loop never runs"
VERI_REFACTOR_BUDGET=0 "$BUDGET" 0 >/dev/null 2>&1 && code=0 || code=$?
if [[ "$code" == 3 ]]; then
  pass=$((pass + 1))
else
  fail=$((fail + 1))
  echo "FAIL - $name (want exit 3, got $code)"
fi

# 3. a budget that is not a whole number ≥ 0 is a system failure, not a decision: the
#    script fails closed like classify-bail.sh does on an unrecognised cause — exit 2
#    ("no answer could be obtained"), a diagnostic on stderr, and nothing on stdout, so a
#    conductor mirroring stdout cannot mistake a misconfigured run for a real status.
#    Non-numeric and negative are the two ways to get it wrong, one criterion, so they are
#    one case; `problems` says which value broke.
name="a non-numeric or negative VERI_REFACTOR_BUDGET exits 2 with a diagnostic on stderr and no status on stdout"
problems=()
for bad in two -1; do
  # Separate the two streams into their own files: the case is about which stream carries
  # what, so they must not be merged.
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

# 4. the count — the script's one positional — gets the same fail-closed treatment as the
#    budget does in case 3: `abc` is not a number, `-1` is below zero and a missing
#    argument is no number at all, so none of the three is a decision the script can
#    make. Each is exit 2, a diagnostic on stderr and nothing on stdout, so a conductor
#    mirroring stdout cannot mistake a malformed call for a real status. Three ways to
#    get one argument wrong, one criterion, so they are one case; `problems` says which
#    call broke.
#
#    `count_probe <label> [args...]` runs the script with exactly the arguments it is
#    given and collects its problems. A function rather than an argv array because the
#    "no argument" probe needs an argument list of length zero, and under `set -u` bash
#    3.2 rejects "${arr[@]}" on an empty array while accepting "$@" with no positionals.
count_probe() {
  local label="$1"; shift
  # Separate streams into their own files: the case is about which stream carries what.
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

# 5. a decimal count is the fourth way to get the positional wrong, and the one that fails
#    most quietly: `1.5` is not an integer, so `[[ 1.5 -lt 2 ]]` cannot evaluate it — bash
#    prints its own arithmetic syntax error and the comparison comes back false, which
#    reads as "budget spent" (exit 3) with a status line on stdout. Exit 3 means "nothing
#    to do", a real answer, so the conductor would stop the refactor loop on a malformed
#    call instead of bailing. Same fail-closed answer as the other bad shapes: exit 2, a
#    diagnostic on stderr, nothing on stdout.
name="a decimal count exits 2 with a diagnostic on stderr and no status on stdout"
problems=()
count_probe "count 1.5" 1.5
report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
