#!/usr/bin/env bash
# Unit tests for scripts/refactor-budget.sh — bounds the refactor loop so a step costs
# the same on every run: given the number of transforms done so far, it says whether
# another leaf may run.
# Zero-dependency plain-shell asserts, same idiom as classify-bail.test.sh.
#
# Contract under test (issue #42):
#   refactor-budget.sh <count>  → exit 0 while <count> is below VERI_REFACTOR_BUDGET
#                                 (default 5, issue #106), exit 3 once the budget is spent;
#                                 a one-line status on stdout either way, so the
#                                 conductor can mirror it (`refactor 5/5 — budget spent`).
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
#    of 5 applies — counts 0 and 4 mean "another transform may run" (exit 0) and count 5
#    means "budget spent" (exit 3). Every answer prints a one-line status.
#    The three probes are one criterion, so they are reported as one case; `problems`
#    collects what went wrong in each so the FAIL line says which count broke.
name="default budget: counts 0 and 4 exit 0, count 5 exits 3, each with a one-line status"
problems=()
for probe in "0 0" "4 0" "5 3"; do
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
#    most quietly: `1.5` is not an integer, so `[[ 1.5 -lt 5 ]]` cannot evaluate it — bash
#    prints its own arithmetic syntax error and the comparison comes back false, which
#    reads as "budget spent" (exit 3) with a status line on stdout. Exit 3 means "nothing
#    to do", a real answer, so the conductor would stop the refactor loop on a malformed
#    call instead of bailing. Same fail-closed answer as the other bad shapes: exit 2, a
#    diagnostic on stderr, nothing on stdout.
name="a decimal count exits 2 with a diagnostic on stderr and no status on stdout"
problems=()
count_probe "count 1.5" 1.5
report "$name"

# 6. the other side of cases 4 and 5: a guard that refuses bad counts must still let the
#    good ones through untouched. 0, 4 and 5 span the default budget's range — first,
#    last-below, spent — and each keeps the answer it gave before the guard existed:
#    exit 0, 0, 3, one line on stdout and, because a valid call is not a diagnosable one,
#    nothing at all on stderr. That last probe is what case 1 cannot see: it sends stderr
#    to /dev/null, so a guard that fired its diagnostic and carried on would pass there and
#    fail here. Three counts, one criterion, so one case; `problems` says which broke.
name="valid counts 0, 4 and 5 keep their answers — exit 0, 0, 3, one line on stdout, nothing on stderr"
problems=()
for probe in "0 0" "4 0" "5 3"; do
  count="${probe% *}" exp_code="${probe#* }"
  # Separate streams into their own files: the case is about which stream carries what.
  out="$(mktemp)" err="$(mktemp)"
  env -u VERI_REFACTOR_BUDGET "$BUDGET" "$count" >"$out" 2>"$err" && code=0 || code=$?
  [[ "$code" == "$exp_code" ]] ||
    problems+=("count $count: want exit $exp_code, got $code")
  # One line: exactly one newline in the file, and something before it.
  [[ "$(wc -l <"$out")" -eq 1 && -s "$out" ]] ||
    problems+=("count $count: want a one-line status on stdout, got: $(printf '%q' "$(cat "$out")")")
  [[ ! -s "$err" ]] ||
    problems+=("count $count: want nothing on stderr, got: $(printf '%q' "$(cat "$err")")")
  rm -f "$out" "$err"
done
report "$name"

# 7. the default budget is 5, not 2 (issue #106). Two transforms was low enough that most
#    steps stopped by budget rather than by "nothing left to tidy", which made the loop read
#    as running once; five gives a step room to actually run dry. One criterion with three
#    faces, so one case: with VERI_REFACTOR_BUDGET unset the boundary sits between 4 and 5
#    (count 4 exits 0, count 5 exits 3); an explicit value still overrides the default
#    rather than being clamped by it (VERI_REFACTOR_BUDGET=3 makes count 3 spent); and the
#    status line names the budget actually in force — `refactor 4/5`, not a stale `/2` —
#    because that line is what the conductor mirrors into the issue thread.
#    `problems` says which probe broke.
name="the default budget is 5: unset, count 4 exits 0 and count 5 exits 3, an explicit value still overrides, and the status line names the budget in force"
problems=()
# Each probe: <env value, or `-` for unset> <count> <expected exit> <expected k/budget>
# The status's leading word is the same in every probe, so it lives in the format below
# rather than in the data: a probe is four whitespace-separated fields, none of which
# contains whitespace itself, so `set --` splits it without anything needing rejoining.
for probe in "- 4 0 4/5" "- 5 3 5/5" "3 3 3 3/3"; do
  set -- $probe
  budget_env="$1" count="$2" exp_code="$3" exp_status="refactor $4"
  label="VERI_REFACTOR_BUDGET=$budget_env count $count"
  # The two kinds of probe differ only in how the child's environment is set up, so branch
  # on that alone and leave one copy of the call itself: `-u VAR` clears the variable for
  # the child only — the probe then sees the script's own default and nothing the
  # surrounding run has set — while `VAR=value` sets it for that child just as narrowly.
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

# 8. the default refactor-budget.sh encodes and the prose that states it must not drift
#    apart. Case 7 asks the running script what its default is; this case asks whether the
#    sentences about it still say the same number. `VERI_REFACTOR_BUDGET`'s default is
#    written down three times in this lane: once as code
#    (`budget="${VERI_REFACTOR_BUDGET:-N}"`) and twice as prose — the script's own header
#    and SKILL.md's Refactor entry. Changing the constant alone leaves both sentences
#    confidently stating the old figure and nothing else in this lane notices.
#
#    This is supervise.test.sh case 10's guarantee — "the default supervise.sh encodes and
#    the prose that states it must not drift apart", issue #98 — applied to the second
#    number of that shape, including which statements are not its own: the figure is stated
#    twice more in docs/wt/commentary.py (the stage-5 three-budgets diagram and this
#    script's own commentary), and reading that file from here would put the page's prose on
#    the development lane's critical path, where a rewording turns every leaf's `make test`
#    red over a file no development change touched (#143, ADR 0016). Both sites moved to
#    docs/tests/commentary-figures.test.sh (#146); no-docs-reads.test.sh keeps them out.
#
#    Each site is located by a regex that ends at the figure it asks about, and a site
#    whose pattern can no longer be found reports `<none>` — a rewording that moves a
#    statement out of the check's sight is drift too, and must fail rather than pass
#    silently. CLAUDE.md names the tunable but states no number for it, so there is nothing
#    there to compare and it is not a site.
ROOT="$(cd "$HERE/../../../.." && pwd)"

# stated <file> <extended-regex> — the figure the first match of <regex> states, or
# '<none>' / '<no-file>' when there is nothing to read. Newlines are squashed to spaces
# first, because the prose below wraps at ~90 columns and a statement split across two
# lines is still one statement; the figure is the LAST run of digits in the match, which is
# why every regex here stops at it.
stated() {
  local hit
  [[ -f "$1" ]] || { echo '<no-file>'; return; }
  hit="$(head -1 < <(tr '\n' ' ' < "$1" | grep -oE "$2"))"
  [[ -n "$hit" ]] || { echo '<none>'; return; }
  printf '%s' "$hit" | grep -oE '[0-9]+' | tail -1
}

# The code site, read through that same helper: `budget="${VERI_REFACTOR_BUDGET:-N}"`
# states the figure as much as the two sentences do, and it is the one the others must
# match. The script's header mentions the tunable earlier in the file, but says `(default
# N)` rather than `:-N`, so this pattern's first match is the assignment itself.
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

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
