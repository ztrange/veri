#!/usr/bin/env bash
# Unit tests for where skills/tdd/SKILL.md asks whether a run can still afford to finish
# (issue #453). Like skill-stopping.test.sh this suite belongs to no single script: its
# subject is the procedure, read as text, the way the session that follows it reads it.
# Zero-dependency plain-shell asserts, same idiom as skill-refactor-touched.test.sh.
#
# Why this exists: the per-issue ceiling as practised parked at whatever step it was crossed
# at — #409 parked at 8 of 9 steps, one step from a draft PR. A parked run's spend is not lost,
# so the cost of parking rises with every step taken, and the moment to park is the step
# boundary at which the run first knows it cannot finish. run-affordable.sh answers that
# question; this suite pins that the procedure asks it there, and what a park then says.
#
# Contract under test:
#   1. The cycle loop (`### 3. The cycle loop`, up to `### 4.`) calls `$S/run-affordable.sh`
#      after the step's ledger commit (`chore: refactor verified …`), with the count
#      `next-unchecked.sh` implies — which leaves out the `⟦full-suite⟧` and `⟦human-owed⟧`
#      lines that script skips, or the count overstates what is left; on exit 1 the run parks, and the park's comment carries
#      spent, steps remaining, the median, the projection, the ceiling, and the two answers —
#      raise `VERI_RUN_BUDGET` and resume, or split the issue.
#   2. The same step boundary — from the call to the next verdict bullet (`- **REJECT`) — also
#      says what its exit 3 does (no full step done yet, so no median: carry on) and what its
#      exit 2 does (no answer could be obtained), so neither is left for the session to guess.
#   3. The park on exit 1 — up to the exit 2 answer — says it is not a bail and that
#      `classify-bail.sh` is not called on it: nothing failed, and a resume handles the ledger.
#
# Run: scripts/tests/skill-run-affordable.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"
skill_md="skills/tdd/SKILL.md"
skill_path="$ROOT/$skill_md"

pass=0 fail=0

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

plain() {
  tr -d '*`' | tr '[:upper:]' '[:lower:]'
}

cycle_loop() {
  awk '/^### 3\. The cycle loop/ { inside = 1; next } /^### 4\./ { inside = 0 } inside' "$skill_path"
}

loop="$(cycle_loop)"
call_at="$(grep -n -m1 '\$S/run-affordable\.sh' <<<"$loop" | cut -d: -f1)"
after_call=""
[[ -n "$call_at" ]] && after_call="$(sed -n "${call_at},\$p" <<<"$loop")"

name="$skill_md calls run-affordable.sh at the step boundary, after the step's ledger commit, with the count next-unchecked.sh implies, and parks on exit 1 carrying spent, steps remaining, the median, the projection, the ceiling and the two answers"
problems=()

commit_at="$(grep -n -m1 'git commit -m "chore: refactor verified' <<<"$loop" | cut -d: -f1)"

if [[ -z "$call_at" ]]; then
  problems+=("the cycle loop has no \$S/run-affordable.sh call")
else
  if [[ -z "$commit_at" ]]; then
    problems+=("the cycle loop has no 'chore: refactor verified' ledger commit to call it after")
  elif (( call_at < commit_at )); then
    problems+=("\$S/run-affordable.sh is called at line $call_at of the cycle loop, before the step's ledger commit at line $commit_at")
  fi
  # The call and the text that answers it: from a few lines before the call (where the count
  # may be computed) to the end of the cycle loop.
  from=$(( call_at > 5 ? call_at - 5 : 1 ))
  around="$(sed -n "${from},\$p" <<<"$loop" | plain)"
  for probe in 'next-unchecked.sh' 'exit 1' 'park' 'spent' 'steps remaining' 'median' \
               'projection' 'ceiling' 'veri_run_budget' 'resume' 'split' \
               '⟦full-suite⟧' '⟦human-owed⟧'; do
    [[ "$around" == *"$probe"* ]] ||
      problems+=("the text around the \$S/run-affordable.sh call never says '$probe'")
  done
fi
report "$name"

# 2. The step boundary also answers run-affordable.sh's exit 3 and exit 2.
name="$skill_md says what the step boundary does when run-affordable.sh exits 3 (no full step done yet, carry on) or exits 2 (no answer could be obtained)"
problems=()

if [[ -z "$call_at" ]]; then
  problems+=("the cycle loop has no \$S/run-affordable.sh call")
else
  # The boundary: from the call to the next verdict bullet, which belongs to verify-refactor.
  boundary="$(awk '/^[[:space:]]*- \*\*REJECT/ { exit } { print }' <<<"$after_call" | plain)"
  for probe in 'exit 3' 'no full step' 'exit 2' 'no answer'; do
    [[ "$boundary" == *"$probe"* ]] ||
      problems+=("the step boundary after the \$S/run-affordable.sh call never says '$probe'")
  done
fi
report "$name"

# 3. The affordability park is not a bail, and classify-bail.sh is not called on it.
name="$skill_md says an affordability park on run-affordable.sh exit 1 is not a bail and that classify-bail.sh is not called on it"
problems=()

if [[ -z "$call_at" ]]; then
  problems+=("the cycle loop has no \$S/run-affordable.sh call")
else
  # The park: from the exit 1 answer after the call up to the exit 2 answer, which is a bail.
  park="$(plain <<<"$after_call" |
    awk '/on exit 1/ { inside = 1 } /on exit 2/ { exit } inside')"
  if [[ -z "$park" ]]; then
    problems+=("the step boundary after the \$S/run-affordable.sh call has no exit 1 answer")
  else
    for probe in 'not a bail' 'classify-bail.sh'; do
      [[ "$park" == *"$probe"* ]] ||
        problems+=("the exit 1 park after the \$S/run-affordable.sh call never says '$probe'")
    done
  fi
fi
report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
