#!/usr/bin/env bash
# Unit tests for what the conductor's Green section in skills/tdd/SKILL.md does with a
# developer leaf that answered `SPLIT:` instead of an implementation, read as text.
#
# Contract under test:
#   1. SKILL.md's Green section, on `SPLIT:`, restores the tree to `HEAD`, passes the
#      split criteria to ONE `add-ledger-step.sh … before '<STEP>'` call, commits the grown
#      ledger, emits `step-split`, and loops back to `next-unchecked.sh`, which hands over
#      the first split step.
#   2. When `add-ledger-step.sh` exits 1 on that branch, the run bails with cause
#      `step-too-big`, which SKILL.md's Bailing causes list classifies as a **process**
#      failure.
#   3. The three split calls pass no --criterion and say a split keeps its anchor's criterion;
#      the uncovered-spec call passes --criterion <k>, read from the issue's numbered
#      acceptance criteria, one call per criterion, bailing naming the cause on exit 2.
#   4. The ⟦suite-repair⟧ and ⟦ci-repair⟧ add-ledger-step.sh calls, which keep the anchor's
#      criterion on purpose, say beside them that they pass no --criterion because the repair
#      step serves its anchor's criterion.
#   5. The add-ledger-step.sh entry under The scripts says --criterion <k> tags the added steps
#      with criterion k for any whole number k ≥ 1, carried by a step or not, and its exit 2
#      cases include a k that is not a whole number ≥ 1.
#   6. The Green section judges a `⟦ci-repair⟧` step's green against a fresh CI run on the
#      pushed fix — `wait-ci.sh` on the pushed sha — not only a local `make test`, and a red
#      CI there is the second red that bails `ci-red`.
#
# Run: scripts/tests/skill-green-split.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"

skill_md="skills/tdd/SKILL.md"
skill_path="$ROOT/$skill_md"


source "$HERE/lib/harness.sh"
source "$HERE/lib/plain.sh"
source "$HERE/lib/window.sh"


green_heading='#### Green'

green_section() {
  awk -v h="$green_heading" \
    'index($0, h) == 1 { inside = 1; next } inside && /^#/ { exit } inside' "$skill_path" |
    plain --join
}
section="$(green_section)"

unreadable=""
[[ -n "${section// /}" ]] ||
  unreadable="$skill_md has no '$green_heading' section to read —"

add_ledger_step='\$s/add-ledger-step\.sh'

bailing_causes() {
  awk '
    !in_s && index($0, "## Bailing") == 1 { in_s = 1; next }
    in_s && /^#/ { exit }
    in_s {
      if (!want && $0 ~ /killed-stuck/) want = 1
      if (want) print
    }' "$skill_path" | plain --join
}


step_too_big_cause() {
  awk '
    !in_s && index($0, "## Bailing") == 1 { in_s = 1; next }
    in_s && /^#/ { exit }
    in_s && inside && (/^- / || /^$/) { exit }
    in_s && /^- `step-too-big`/ { inside = 1 }
    inside' "$skill_path" | plain --join
}

split_calls() {
  grep -nE '\$S/add-ledger-step\.sh (--criterion [^ ]+ )?\.tdd/.*(instead-of|before "\$\(\$S/next-unchecked\.sh)' "$skill_path"
}

uncovered_spec_call() {
  grep -nE '\$S/add-ledger-step\.sh (--criterion [^ ]+ )?\.tdd/.*after "\$\(\$S/next-pending-refactor\.sh' "$skill_path"
}

call_neighbourhood() {
  awk -v at="${1%%:*}" 'NR >= at - 20 && NR <= at + 20' "$skill_path" | plain --join
}

add_ledger_step_entry() {
  awk '
    inside && (/^- / || /^$/) { exit }
    /^- `\$S\/add-ledger-step\.sh/ { inside = 1 }
    inside' "$skill_path" | plain --join
}
entry="$(add_ledger_step_entry)"
no_entry="$skill_md has no '- \`\$S/add-ledger-step.sh' entry under The scripts"

repair_call_neighbourhood() {
  awk -v tag="$1" '
    { text[NR] = $0 }
    index($0, "$S/add-ledger-step.sh") && index($0, tag) { at = NR }
    END { if (at) for (i = at - 20; i <= at + 20; i++) if (i in text) print text[i] }
  ' "$skill_path" | plain --join
}

require() {
  grep -F -- "$1" > /dev/null <<<"$2" || problems+=("$3")
}

one_line() {
  tr -d '*`' | tr '\n' ' ' | tr -s ' '
}

green_paragraph() {
  awk 'index($0, "On a `⟦replaces-case⟧` step, a PASS is accepted") { inside = 1 }
       inside && /^3\. / { exit }
       inside' "$skill_path" | one_line
}
section="$(green_paragraph)"

name="#1406 $skill_md runs replaces-case-survivors.sh before the verify-green launch command, not after it"
problems=()

survivors_line="$(grep -nF 'replaces-case-survivors.sh "' "$skill_path" | sed -n 1p | cut -d: -f1)"
launch_line="$(grep -nF 'supervise.sh verdict-green' "$skill_path" | sed -n 1p | cut -d: -f1)"

if [[ -z "$survivors_line" || -z "$launch_line" ]]; then
  problems+=("$skill_md lacks a replaces-case-survivors.sh run or a verdict-green launch line (survivors=${survivors_line:-none}, launch=${launch_line:-none}) — their order could not be established")
elif [[ "$survivors_line" -gt "$launch_line" ]]; then
  problems+=("$skill_md:$survivors_line runs replaces-case-survivors.sh after the verify-green launch at line $launch_line, so a conductor following the page in order launches the verifier before it checks for survivors")
fi

report "$name"

name="#1558 $skill_md runs every replaces-case-survivors.sh occurrence before the verify-green launch it gates, on the Green path and the pin path alike"
problems=()

green_launch="$(grep -nF 'supervise.sh verdict-green' "$skill_path" | sed -n 1p | cut -d: -f1)"
pin_start="$(grep -nF 'A `⟦replaces-case⟧` step whose Red reports' "$skill_path" | sed -n 1p | cut -d: -f1)"
pin_launch="$(grep -nF 'Judge it by the replaces-case verify-green' "$skill_path" | sed -n 1p | cut -d: -f1)"
occurrences="$(grep -nF 'replaces-case-survivors.sh "' "$skill_path" | cut -d: -f1)"

if [[ -z "$green_launch" || -z "$pin_start" || -z "$pin_launch" || -z "$occurrences" ]]; then
  problems+=("$skill_md lacks a survivors run or a launch marker (green launch=${green_launch:-none}, pin path=${pin_start:-none}, pin launch=${pin_launch:-none}) — their order could not be established")
else
  while IFS= read -r at; do
    if [[ "$at" -lt "$pin_start" ]]; then
      context="$(sed -n "$((at - 1)),${at}p" "$skill_path" | one_line)"
      if [[ "$at" -gt "$green_launch" && "$context" != *"Before that verify-green"* ]]; then
        problems+=("$skill_md:$at runs replaces-case-survivors.sh after the Green verify-green launch at line $green_launch")
      fi
    elif [[ "$at" -gt "$pin_launch" ]]; then
      problems+=("$skill_md:$at runs replaces-case-survivors.sh after the pin-path verify-green launch at line $pin_launch")
    fi
  done <<<"$occurrences"
fi

report "$name"

name="#1406 $skill_md orders the unreplaced-cases.sh check before the replaces-case-survivors.sh check, and both before the verify-green launch command"
problems=()

unreplaced_line="$(grep -nF 'unreplaced-cases.sh "' "$skill_path" | sed -n 1p | cut -d: -f1)"
survivors_line="$(grep -nF 'replaces-case-survivors.sh "' "$skill_path" | sed -n 1p | cut -d: -f1)"
launch_line="$(grep -nF 'supervise.sh verdict-green' "$skill_path" | sed -n 1p | cut -d: -f1)"

if [[ -z "$unreplaced_line" || -z "$survivors_line" || -z "$launch_line" ]]; then
  problems+=("$skill_md lacks an unreplaced-cases.sh run, a replaces-case-survivors.sh run or a verdict-green launch line (unreplaced=${unreplaced_line:-none}, survivors=${survivors_line:-none}, launch=${launch_line:-none}) — the gate order could not be established")
elif [[ "$unreplaced_line" -gt "$survivors_line" || "$survivors_line" -gt "$launch_line" ]]; then
  problems+=("$skill_md gates are out of order: unreplaced-cases.sh at line $unreplaced_line, replaces-case-survivors.sh at line $survivors_line, verify-green launch at line $launch_line")
fi

report "$name"

name="#1406 $skill_md's replaces-case green paragraph says each survivors relaunch spends one REVISE_BUDGET attempt and a spent budget bails with a cause classify-bail.sh classifies"
problems=()

if [[ -z "${section// /}" ]]; then
  problems+=("$skill_md has no replaces-case paragraph in the Green step's Verify (blind) to read — the relaunch bound could not be established")
else
  require 'REVISE_BUDGET' "$section" \
    "$skill_md's replaces-case Green paragraph never says the survivors relaunch spends a REVISE_BUDGET attempt, so the relaunch is unbounded"
  bail_cause="$(grep -oE 'cause=[a-z-]+' <<<"$section" | sed -n 1p)"
  bail_cause="${bail_cause#cause=}"
  if [[ -z "$bail_cause" ]]; then
    problems+=("$skill_md's replaces-case Green paragraph names no cause= to bail with when the REVISE_BUDGET is spent on survivors")
  elif ! "$ROOT/skills/tdd/scripts/classify-bail.sh" "$bail_cause" > /dev/null 2>&1; then
    problems+=("$skill_md's replaces-case Green paragraph bails with cause=$bail_cause, which classify-bail.sh does not classify")
  fi
fi

report "$name"

name="#1406 $skill_md documents build-develop-prompt.sh green's 8th argument, the cases still owed for deletion, at the green build command and in the script reference entry"
problems=()

green_build="$(grep -F 'build-develop-prompt.sh green ' "$skill_path" | sed -n 1p)"
reference_green="$(awk 'index($0, "- `$S/build-develop-prompt.sh <red") == 1 { inside = 1; next } inside && /^- `/ { exit } inside' "$skill_path" | plain --join)"

if [[ -z "$green_build" ]]; then
  problems+=("$skill_md has no 'build-develop-prompt.sh green ' command line to read")
elif [[ "$green_build" != *owed* ]]; then
  problems+=("$skill_md's green build command passes no argument for the cases still owed for deletion: $green_build")
fi
if [[ "$reference_green" != *"<fast-cmd>"*owed* && "$reference_green" != *"green <spec-file>"*owed*"refactor <spec-file>"* ]]; then
  problems+=("$skill_md's build-develop-prompt.sh reference entry never lists an owed-cases argument in green's synopsis")
fi

report "$name"

pin_paragraph() {
  awk 'index($0, "A `⟦replaces-case⟧` step whose Red reports") == 1 { inside = 1 }
       inside && index($0, "Every other step takes the verdict") { exit }
       inside' "$skill_path" | one_line
}
section="$(pin_paragraph)"

name="#1546 $skill_md's replaces-case pin-path paragraph runs replaces-case-survivors.sh after the deletion green and, on survivors, relaunches it bounded by REVISE_BUDGET before verify-green"
problems=()

if [[ -z "${section// /}" ]]; then
  problems+=("$skill_md has no replaces-case pin-path paragraph to read — the survivors check could not be established")
else
  require 'replaces-case-survivors.sh' "$section" \
    "$skill_md's replaces-case pin-path paragraph never runs replaces-case-survivors.sh, so a pin-path green that skipped the deletion reaches a verifier"
  require 'relaunch' "$section" \
    "$skill_md's replaces-case pin-path paragraph never relaunches the green leaf on survivors"
  require 'REVISE_BUDGET' "$section" \
    "$skill_md's replaces-case pin-path paragraph never says a survivors relaunch spends a REVISE_BUDGET attempt"
  require 'revise-exhausted' "$section" \
    "$skill_md's replaces-case pin-path paragraph never bails cause=revise-exhausted when the budget is spent"
  require 'no verifier' "$section" \
    "$skill_md's replaces-case pin-path paragraph never says no verifier is launched while a named case survives"
fi

report "$name"

name="#1546 $skill_md runs unreplaced-cases.sh, at every place it names it as a run, before the verify-red launch command"
problems=()

red_launch_line="$(grep -nF 'supervise.sh verdict-red' "$skill_path" | sed -n 1p | cut -d: -f1)"
run_lines="$(grep -nE '\$S/unreplaced-cases\.sh|[Rr]un [^.]*unreplaced-cases\.sh' "$skill_path" | cut -d: -f1)"

if [[ -z "$red_launch_line" || -z "$run_lines" ]]; then
  problems+=("$skill_md lacks an unreplaced-cases.sh run or a verdict-red launch line (runs=${run_lines:-none}, launch=${red_launch_line:-none}) — their order could not be established")
else
  while IFS= read -r run_line; do
    if [[ "$run_line" -gt "$red_launch_line" ]]; then
      problems+=("$skill_md:$run_line runs unreplaced-cases.sh after the verify-red launch at line $red_launch_line, so a conductor following the page in order launches the red verifier before it checks for unreplaced cases")
    fi
  done <<< "$run_lines"
fi

report "$name"

name="#1546 $skill_md never runs replaces-case-survivors.sh, at any place it names it as a run, before the last place it runs unreplaced-cases.sh"
problems=()

unreplaced_runs="$(grep -nE '\$S/unreplaced-cases\.sh|[Rr]un [^.]*unreplaced-cases\.sh' "$skill_path" | cut -d: -f1)"
survivors_runs="$(grep -nE '\$S/replaces-case-survivors\.sh|[Rr]uns? [^.]*replaces-case-survivors\.sh' "$skill_path" | cut -d: -f1)"

if [[ -z "$unreplaced_runs" || -z "$survivors_runs" ]]; then
  problems+=("$skill_md lacks an unreplaced-cases.sh run or a replaces-case-survivors.sh run (unreplaced=${unreplaced_runs:-none}, survivors=${survivors_runs:-none}) — their order could not be established")
else
  last_unreplaced="$(sort -n <<< "$unreplaced_runs" | tail -n 1)"
  while IFS= read -r survivors_line; do
    if [[ "$survivors_line" -lt "$last_unreplaced" ]]; then
      problems+=("$skill_md:$survivors_line runs replaces-case-survivors.sh before the unreplaced-cases.sh run at line $last_unreplaced, so the two gates run in the other order")
    fi
  done <<< "$survivors_runs"
fi

report "$name"

name="#1558 $skill_md's Green Verify line that runs replaces-case-survivors.sh before the launch carries a ⟦replaces-case⟧ qualifier, so an ordinary step runs nothing"
problems=()

run_line="$(grep -nF 'Run `$S/replaces-case-survivors.sh "<step text>"` before the launch below' "$skill_path" | sed -n 1p)"

if [[ -z "$run_line" ]]; then
  problems+=("$skill_md has no Green Verify line running replaces-case-survivors.sh before the launch below — the qualifier could not be established")
elif [[ "$run_line" != *'⟦replaces-case⟧'* ]]; then
  problems+=("$skill_md:${run_line%%:*} runs replaces-case-survivors.sh with no ⟦replaces-case⟧ qualifier, so a conductor reading it on an ordinary step runs the script and it exits 2")
fi

report "$name"

name="#1379 $skill_md's every add-ledger-step.sh call site says its exit 2 bails with cause step-add-refused, and Bailing lists that cause as a system failure"
problems=()

call_lines="$(grep -nE '\$S/add-ledger-step\.sh [^ ]*\.tdd/issue-<n>\.md|\$S/add-ledger-step\.sh --criterion <k> \.tdd/issue-<n>\.md' "$skill_path" | cut -d: -f1)"
if [[ -z "$call_lines" ]]; then
  problems+=("$skill_md has no add-ledger-step.sh call site — where its exit 2 is handled could not be established")
else
  while IFS= read -r call_line; do
    near="$(sed -n "${call_line},$((call_line + 30))p" "$skill_path" | plain --join)"
    grep -qE 'exits? 2[^.]{0,120}step-add-refused|step-add-refused[^.]{0,120}exits? 2' <<<"$near" ||
      problems+=("$skill_md:$call_line calls add-ledger-step.sh and never says its exit 2 bails with cause step-add-refused, so a refused call leaves the conductor to invent a cause classify-bail.sh cannot classify")
  done <<<"$call_lines"
fi

causes="$(bailing_causes)"
grep -qE 'step-add-refused[^.]{0,220}system' <<<"$causes" ||
  problems+=("$skill_md's Bailing causes list never classifies step-add-refused as a system failure, so a refused add-ledger-step.sh call has no cause a human can read")

report "$name"

finish
