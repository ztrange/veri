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

name="$skill_md's Green section, on SPLIT:, restores the tree to HEAD, adds the split steps before STEP in one add-ledger-step.sh call, commits the ledger, emits step-split and returns to next-unchecked.sh"
problems=()

if [[ -n "$unreadable" ]]; then
  problems+=("$unreadable what the conductor does with a SPLIT: report could not be established")
else
  grep -qE 'split' <<<"$section" ||
    problems+=("$skill_md's Green section never branches on the leaf's SPLIT: report, so the answer develop-green.md now offers reaches a conductor with nothing to do with it")

  grep -qE 'git (restore|checkout|reset)[^.]{0,60}head|restore[^.]{0,60}(the tree|to) head' <<<"$section" ||
    problems+=("$skill_md's Green section never restores the tree to HEAD on a SPLIT:, so the uncommitted red test stays on disk and the first split step starts against a failing case nobody wrote for it")

  calls="$(grep -oE "$add_ledger_step" <<<"$section" | grep -c '')"
  if [[ "$calls" -eq 0 ]]; then
    problems+=("$skill_md's Green section never runs add-ledger-step.sh on a SPLIT:, so the criteria the leaf named are narrated and the plan the run reads is unchanged")
  elif [[ "$calls" -gt 1 ]]; then
    problems+=("$skill_md's Green section runs add-ledger-step.sh $calls times, so a step's SPLIT: criteria are inserted a call at a time and the growth budget is read once per criterion rather than once for the split")
  else
    added="$(window "$section" "$add_ledger_step")"
    grep -qE "before ['\"]?(<step>|\\$\\(\\\$s/next-unchecked\\.sh)" <<<"$added" ||
      problems+=("$skill_md's Green section runs add-ledger-step.sh without anchoring the insertion before the step being split, so the smaller steps land after the step they were supposed to come first")
    grep -qE 'commit' <<<"$added" ||
      problems+=("$skill_md's Green section grows the ledger on a SPLIT: without committing it, so the split steps are lost the moment the run is resumed from the committed ledger")
  fi

  grep -qE 'step-split' <<<"$section" ||
    problems+=("$skill_md's Green section never emits step-split, so nothing in the run log says the step was split rather than silently restarted")

  grep -qE 'next-unchecked' <<<"$section" ||
    problems+=("$skill_md's Green section never loops back to next-unchecked.sh after a split, so the conductor goes on into verify-green with no implementation for it to judge")
fi

report "$name"

name="$skill_md's Green section bails with cause step-too-big when add-ledger-step.sh exits 1 on a split, and its Bailing section lists that cause as a process failure"
problems=()

if [[ -n "$unreadable" ]]; then
  problems+=("$unreadable what the conductor does when a split is over budget could not be established")
elif ! grep -qE 'step-too-big' <<<"$section"; then
  problems+=("$skill_md's Green section never names the step-too-big cause, so a split refused for growth budget leaves the conductor to invent a stop for a step whose criteria are already filed as owed")
else
  over="$(window "$section" 'step-too-big')"
  grep -qE 'exits? 1' <<<"$over" ||
    problems+=("$skill_md's Green section names step-too-big without saying it is add-ledger-step.sh's exit 1 that causes it, so the conductor cannot tell the over-budget refusal from a call that worked")
  grep -qE 'bail' <<<"$over" ||
    problems+=("$skill_md's Green section names step-too-big without bailing on it, so a run whose split was refused carries on into a step it has no plan for")
fi

causes="$(bailing_causes)"
if [[ -z "${causes// /}" ]]; then
  problems+=("$skill_md's Bailing section has no causes list starting at killed-stuck — the classification of step-too-big could not be read")
else
  grep -qE 'step-too-big[^.]{0,220}process' <<<"$causes" ||
    problems+=("$skill_md's Bailing causes list never classifies step-too-big as a process failure, so the label a human reads calls a methodology verdict a broken pipe")
fi

report "$name"


step_too_big_cause() {
  awk '
    !in_s && index($0, "## Bailing") == 1 { in_s = 1; next }
    in_s && /^#/ { exit }
    in_s && inside && (/^- / || /^$/) { exit }
    in_s && /^- `step-too-big`/ { inside = 1 }
    inside' "$skill_path" | plain --join
}

name="$skill_md's Bailing entry for step-too-big names all three splits that lead to it: a Green leaf's SPLIT:, the revise-exhausted split and the over-budget split"
problems=()

bullet="$(step_too_big_cause)"
if [[ -z "${bullet// /}" ]]; then
  problems+=("$skill_md's Bailing causes list has no step-too-big bullet — which splits lead to it could not be read")
else
  grep -E 'green[^.]*split:|split:[^.]*green' <<<"$bullet" > /dev/null ||
    problems+=("$skill_md's step-too-big entry does not name a Green leaf's SPLIT:")
  grep -E 'exhausted' <<<"$bullet" > /dev/null ||
    problems+=("$skill_md's step-too-big entry does not name the revise-exhausted split")
  grep -E 'over-budget' <<<"$bullet" > /dev/null ||
    problems+=("$skill_md's step-too-big entry does not name the over-budget split")
fi

report "$name"

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

name="#1281: $skill_md's three split add-ledger-step.sh calls pass no --criterion and say a split keeps its anchor's criterion; the uncovered-spec call passes --criterion <k> read from the issue's numbered acceptance criteria, one call per criterion, bailing on exit 2"
problems=()

splits="$(split_calls)"
[[ "$(grep -cF 'instead-of' <<<"$splits")" -ge 2 ]] ||
  problems+=("$skill_md has fewer than two instead-of add-ledger-step.sh calls — the over-budget and revise-exhausted splits could not both be read")
grep -F 'before "$($S/next-unchecked.sh' <<<"$splits" > /dev/null ||
  problems+=("$skill_md has no add-ledger-step.sh call anchored before \"\$(\$S/next-unchecked.sh — the Green SPLIT: call could not be read")
while IFS= read -r call; do
  [[ -n "$call" ]] || continue
  trimmed="${call#*:}"
  trimmed="${trimmed#"${trimmed%%[![:space:]]*}"}"
  grep -F -- '--criterion' <<<"$trimmed" > /dev/null &&
    problems+=("$skill_md's split call passes --criterion, though a split is the same behaviour broken smaller and keeps its anchor's criterion: $trimmed")
  grep -F -- "anchor's criterion" <<<"$(call_neighbourhood "$call")" > /dev/null ||
    problems+=("$skill_md never says beside this split call that the split keeps its anchor's criterion: $trimmed")
done <<<"$splits"

uncovered="$(uncovered_spec_call)"
if [[ -z "$uncovered" ]]; then
  problems+=("$skill_md has no add-ledger-step.sh call anchored after \"\$(\$S/next-pending-refactor.sh — the uncovered-spec call could not be read")
else
  grep -F -- '--criterion <k>' <<<"$uncovered" > /dev/null ||
    problems+=("$skill_md's uncovered-spec add-ledger-step.sh call passes no --criterion <k>, so a behaviour serving another criterion inherits its anchor's")
  around="$(call_neighbourhood "$(head -n 1 <<<"$uncovered")")"
  grep -E 'numbered acceptance criteri' <<<"$around" > /dev/null ||
    problems+=("$skill_md never says beside its uncovered-spec call that k is read from the issue's numbered acceptance criteria")
  grep -E 'one (add-ledger-step\.sh )?call per criterion' <<<"$around" > /dev/null ||
    problems+=("$skill_md never says beside its uncovered-spec call that behaviours serving different criteria are added in one call per criterion")
  grep -E 'exits? 2[^.]{0,200}bail' <<<"$around" > /dev/null ||
    problems+=("$skill_md never says beside its uncovered-spec call that add-ledger-step.sh exit 2 — no step carries k — bails naming that cause")
fi

if [[ -z "${entry// /}" ]]; then
  problems+=("$no_entry")
else
  grep -F -- '--criterion' <<<"$entry" > /dev/null ||
    problems+=("$skill_md's add-ledger-step.sh entry under The scripts never documents --criterion")
fi

report "$name"

repair_call_neighbourhood() {
  awk -v tag="$1" '
    { text[NR] = $0 }
    index($0, "$S/add-ledger-step.sh") && index($0, tag) { at = NR }
    END { if (at) for (i = at - 20; i <= at + 20; i++) if (i in text) print text[i] }
  ' "$skill_path" | plain --join
}

name="#1281: the ⟦suite-repair⟧ and ⟦ci-repair⟧ add-ledger-step.sh calls say they pass no --criterion because the repair step serves its anchor's criterion"
problems=()

for tag in '⟦suite-repair⟧' '⟦ci-repair⟧'; do
  around="$(repair_call_neighbourhood "$tag")"
  if [[ -z "${around// /}" ]]; then
    problems+=("$skill_md has no add-ledger-step.sh call adding a $tag step")
    continue
  fi
  grep -F -- '--criterion' <<<"$around" > /dev/null ||
    problems+=("$skill_md never says beside its $tag add-ledger-step.sh call that it passes no --criterion")
  grep -F -- "anchor's criterion" <<<"$around" > /dev/null ||
    problems+=("$skill_md never says beside its $tag add-ledger-step.sh call that the repair step serves its anchor's criterion")
done

report "$name"

name="#1292: $skill_md's add-ledger-step.sh entry under The scripts says --criterion <k> tags the added steps with criterion k for any whole number k ≥ 1, carried or not, and lists a k that is not a whole number ≥ 1 among its exit 2 cases"
problems=()

if [[ -z "${entry// /}" ]]; then
  problems+=("$no_entry")
else
  grep -E 'whole number[^.]{0,20}(≥|>=|at least) ?1' <<<"$entry" > /dev/null ||
    problems+=("$skill_md's add-ledger-step.sh entry never says --criterion <k> takes any whole number k ≥ 1")
  grep -E 'whether or not[^.]{0,80}carr|carried or not|(no|not yet)[^.]{0,30}step[^.]{0,20}carr' <<<"$entry" > /dev/null ||
    problems+=("$skill_md's add-ledger-step.sh entry never says --criterion <k> tags the steps whether or not a ledger step already carries criterion k")
  exit2="$(grep -oE 'exit 2[^.]*' <<<"$entry")"
  grep -E 'not a whole number' <<<"$exit2" > /dev/null ||
    problems+=("$skill_md's add-ledger-step.sh entry never lists a --criterion k that is not a whole number ≥ 1 among its exit 2 cases: '$exit2'")
fi

report "$name"

name="#1431 $skill_md's Green section judges a ⟦ci-repair⟧ step's green against a fresh CI run on the pushed fix (wait-ci.sh on the pushed sha), not only a local make test, and a red CI there bails ci-red"
problems=()

if [[ -n "$unreadable" ]]; then
  problems+=("$unreadable how a ⟦ci-repair⟧ step's green is judged could not be established")
elif [[ "$section" != *'⟦ci-repair⟧'* ]]; then
  problems+=("$skill_md's Green section never names a ⟦ci-repair⟧ step, so its green is judged by a local make test alone")
else
  rule="${section#*⟦ci-repair⟧}"
  rule="${rule:0:700}"
  grep -F 'wait-ci.sh' <<<"$rule" > /dev/null ||
    problems+=("$skill_md's ⟦ci-repair⟧ green rule never runs wait-ci.sh on the fix")
  grep -E 'push[^.]{0,60}sha|sha[^.]{0,60}push' <<<"$rule" > /dev/null ||
    problems+=("$skill_md's ⟦ci-repair⟧ green rule never waits on the pushed sha")
  grep -E 'not only[^.]{0,60}make test' <<<"$rule" > /dev/null ||
    problems+=("$skill_md's ⟦ci-repair⟧ green rule never says a local make test alone does not judge it")
  grep -F 'ci-red' <<<"$rule" > /dev/null ||
    problems+=("$skill_md's ⟦ci-repair⟧ green rule never bails ci-red on a red CI there")
fi

report "$name"

name="#1473 $skill_md's Green section names the ⟦ci-repair⟧ verify-green variant and says its evidence is CI — the failing job's log before the fix and a green CI run on the pushed fix — not a local revert-goes-red check"
problems=()

if [[ -n "$unreadable" ]]; then
  problems+=("$unreadable which verify-green judges a ⟦ci-repair⟧ step could not be established")
else
  variant="$(awk '{ gsub(/\. /, ".\n"); print }' <<<"$section" | grep -F '⟦ci-repair⟧' | grep -i 'verify-green')"
  if [[ -z "$variant" ]]; then
    problems+=("$skill_md's Green section has no sentence naming both ⟦ci-repair⟧ and a verify-green variant, so a CI-only repair is judged by the local revert-goes-red check it can never pass")
  else
    grep -iE 'variant' <<<"$variant" > /dev/null ||
      problems+=("$skill_md's ⟦ci-repair⟧ verify-green sentence never calls it a variant")
    grep -iE "failing job's log|log of the failing job" <<<"$variant" > /dev/null ||
      problems+=("$skill_md's ⟦ci-repair⟧ verify-green sentence never names the failing job's log before the fix as evidence")
    grep -iE 'green CI run' <<<"$variant" > /dev/null ||
      problems+=("$skill_md's ⟦ci-repair⟧ verify-green sentence never names a green CI run on the pushed fix as evidence")
    grep -iE 'not[^.]{0,80}(local )?revert' <<<"$variant" > /dev/null ||
      problems+=("$skill_md's ⟦ci-repair⟧ verify-green sentence never says the local revert-goes-red check does not judge it")
  fi
fi

report "$name"

name="#1473 $skill_md's Green section says the ⟦ci-repair⟧ verify-green variant judges only evidence that exists before the push and never requires a CI run on the fix, whose CI verdict is the post-push wait-ci.sh wait where red bails ci-red"
problems=()

if [[ -n "$unreadable" ]]; then
  problems+=("$unreadable what the ⟦ci-repair⟧ verify-green variant judges could not be established")
else
  tail_text="$(awk '{ gsub(/\. /, ".\n"); print }' <<<"$section" | awk '/⟦ci-repair⟧/ && tolower($0) ~ /verify-green/ { on = 1 } on')"
  if [[ -z "$tail_text" ]]; then
    problems+=("$skill_md's Green section has no sentence naming both ⟦ci-repair⟧ and a verify-green variant")
  else
    grep -iE 'judges only[^.]{0,120}(before|prior to) the push' <<<"$tail_text" > /dev/null ||
      problems+=("$skill_md's ⟦ci-repair⟧ verify-green variant never says it judges only evidence that exists before the push")
    grep -iE 'never requires?[^.]{0,60}CI run' <<<"$tail_text" > /dev/null ||
      problems+=("$skill_md's ⟦ci-repair⟧ verify-green variant never says it does not require a CI run on the fix")
    grep -iE 'wait-ci\.sh' <<<"$tail_text" > /dev/null ||
      problems+=("$skill_md's ⟦ci-repair⟧ verify-green variant never leaves the CI verdict on the fix to the post-push wait-ci.sh wait")
    grep -F 'ci-red' <<<"$tail_text" > /dev/null ||
      problems+=("$skill_md's ⟦ci-repair⟧ verify-green variant never says a red CI on the pushed fix bails ci-red")
    ! grep -iE '(requires?|evidence is)[^.]{0,120}green CI run[^.]{0,40}(on|for) the (pushed )?fix' <<<"$tail_text" > /dev/null ||
      problems+=("$skill_md's ⟦ci-repair⟧ verify-green variant requires a green CI run on the pushed fix, which does not exist until after its PASS")
  fi
fi

report "$name"

require() {
  grep -F -- "$1" > /dev/null <<<"$2" || problems+=("$3")
}

green_paragraph() {
  awk 'index($0, "On a `⟦replaces-case⟧` step, a PASS is accepted") { inside = 1 }
       inside && /^3\. / { exit }
       inside' "$skill_path" | tr -d '*`' | tr '\n' ' ' | tr -s ' '
}
section="$(green_paragraph)"

name="$skill_md's replaces-case green paragraph runs replaces-case-survivors.sh before verify-green and, on survivors, relaunches the green leaf naming them, records an event and launches no verifier"
problems=()

if [[ -z "${section// /}" ]]; then
  problems+=("$skill_md has no replaces-case paragraph in the Green step's Verify (blind) to read — the survivors check could not be established")
else
  require 'replaces-case-survivors.sh' "$section" \
    "$skill_md's replaces-case Green paragraph never runs replaces-case-survivors.sh, so a green that kept a named case reaches a verifier"
  require 'relaunch' "$section" \
    "$skill_md's replaces-case Green paragraph never relaunches the green leaf on survivors"
  require 'event' "$section" \
    "$skill_md's replaces-case Green paragraph never records the relaunch as an event"
  require 'no verifier' "$section" \
    "$skill_md's replaces-case Green paragraph never says no verifier is launched while a named case survives"
fi

report "$name"

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
       inside' "$skill_path" | tr -d '*`' | tr '\n' ' ' | tr -s ' '
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

finish
