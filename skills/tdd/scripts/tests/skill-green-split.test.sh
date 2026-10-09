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
    inside' "$skill_path"
}

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

entry="$(add_ledger_step_entry)"
if [[ -z "${entry// /}" ]]; then
  problems+=("$skill_md has no '- \`\$S/add-ledger-step.sh' entry under The scripts")
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

entry="$(add_ledger_step_entry | plain --join)"
if [[ -z "${entry// /}" ]]; then
  problems+=("$skill_md has no '- \`\$S/add-ledger-step.sh' entry under The scripts")
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

finish
