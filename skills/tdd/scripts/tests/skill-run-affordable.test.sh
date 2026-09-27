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
#
# Run: scripts/tests/skill-run-affordable.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
# The suite sits at skills/<skill>/scripts/tests, so four levels up is the repo root.
ROOT="$(cd "$HERE/../../../.." && pwd)"
skill_md="skills/tdd/SKILL.md"
skill_path="$ROOT/$skill_md"

pass=0 fail=0

# report <name> — close a case whose probes collected into the `problems` array: an empty
# array is a pass, otherwise one FAIL line for the case and one indented line per problem.
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

# plain — stdin with emphasis and code markup (`*`, backticks) dropped and case folded, so
# `**park**` and `Park` read the same to every probe.
plain() {
  tr -d '*`' | tr '[:upper:]' '[:lower:]'
}

# cycle_loop — the lines of `### 3. The cycle loop`, up to `### 4.`, verbatim and in order.
cycle_loop() {
  awk '/^### 3\. The cycle loop/ { inside = 1; next } /^### 4\./ { inside = 0 } inside' "$skill_path"
}

# 1. The step boundary asks run-affordable.sh, and parks on its exit 1 carrying the projection.
name="$skill_md calls run-affordable.sh at the step boundary, after the step's ledger commit, with the count next-unchecked.sh implies, and parks on exit 1 carrying spent, steps remaining, the median, the projection, the ceiling and the two answers"
problems=()

loop="$(cycle_loop)"
commit_at="$(grep -n -m1 'git commit -m "chore: refactor verified' <<<"$loop" | cut -d: -f1)"
call_at="$(grep -n -m1 '\$S/run-affordable\.sh' <<<"$loop" | cut -d: -f1)"

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

call_at="$(grep -n -m1 '\$S/run-affordable\.sh' <<<"$loop" | cut -d: -f1)"
if [[ -z "$call_at" ]]; then
  problems+=("the cycle loop has no \$S/run-affordable.sh call")
else
  # The boundary: from the call to the next verdict bullet, which belongs to verify-refactor.
  boundary="$(sed -n "${call_at},\$p" <<<"$loop" | awk '/^[[:space:]]*- \*\*REJECT/ { exit } { print }' | plain)"
  for probe in 'exit 3' 'no full step' 'exit 2' 'no answer'; do
    [[ "$boundary" == *"$probe"* ]] ||
      problems+=("the step boundary after the \$S/run-affordable.sh call never says '$probe'")
  done
fi
report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
