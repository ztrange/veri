#!/usr/bin/env bash
# Unit tests for when the conductor ticks an acceptance criterion in the issue body — like
# skill-refactor-pending.test.sh this suite belongs to no single script: its subject is
# prose, skills/tdd/SKILL.md, read as text the way the session that follows it reads it.
# Zero-dependency plain-shell asserts, same idiom as skill-refactor-pending.test.sh.
#
# Why this exists (issue #168): a plan is made of steps, not criteria, and one criterion is
# routinely built across several steps. Ticking the issue's criterion at every step's end
# told a reader a behaviour existed two steps before its code did (#116), and a bail in
# between left the tick standing. `criterion-finished.sh` answers whether every step serving
# a criterion is done; the tick is only honest if the two places that tick — the *Step done*
# mirror after verify-refactor's PASS and the pin's mirror — ask it first.
#
# Contract under test:
#   1. In both SKILL.md's cycle loop and its pin path, the instruction that runs
#      `tick-issue-criterion.sh` also runs `criterion-finished.sh`, ticks on its exit 0 and
#      ticks nothing on its exit 3; the cycle loop's instruction still posts `### ✅ Step done`.
#   2. SKILL.md step 2's plan-writing guidance tells the conductor to end each ledger step with
#      ` ⟦criterion k⟧` for the criterion it serves, and to leave a gap step without one — the
#      gate in 1 can only answer for a criterion the ledger records.
#
# The gate is asked of the SAME instruction as the tick it guards, for the reason
# skill-refactor-pending.test.sh gives for its clear: a condition prescribed in some other
# section drifts away from the branch it belongs to the first time either is reworded.
#
# Run: scripts/tests/skill-criterion-finished.test.sh
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

records_of() {
  awk '
    function flush() { if (rec != "") { gsub(/[[:space:]]+/, " ", rec); print rec } rec = "" }
    /^[0-9]+\. / || /^[[:space:]]*- / { flush(); rec = $0; next }
    /^[[:space:]]*$/ { flush(); next }
    rec == "" { rec = $0; next }
    { rec = rec " " $0 }
    END { flush() }' | tr '[:upper:]' '[:lower:]'
}

section_records() {
  awk -v head="$1" '
    $0 == head { inside = 1; level = index(head, " "); next }
    inside && /^#+ / && index($0, " ") <= level { exit }
    inside' "$skill_path" | records_of
}

gated_tick() {
  local label="$1" head="$2" extra="$3" rec
  rec="$(head -1 < <(section_records "$head" | grep -F 'tick-issue-criterion.sh'))"
  if [[ -z "$rec" ]]; then
    problems+=("$label: no instruction under '$head' runs tick-issue-criterion.sh — the gate could not be checked")
    return
  fi
  [[ "$rec" == *criterion-finished.sh* ]] ||
    problems+=("$label: the instruction that ticks the issue criterion never runs criterion-finished.sh")
  [[ "$rec" =~ exit\ \*?\*?0 ]] ||
    problems+=("$label: the tick is not tied to criterion-finished.sh's exit 0")
  [[ "$rec" =~ exit\ \*?\*?3 && "$rec" =~ (nothing|no criterion|not tick|without ticking|skip) ]] ||
    problems+=("$label: the instruction never says exit 3 ticks nothing")
  if [[ -n "$extra" ]]; then
    [[ "$rec" =~ $extra ]] ||
      problems+=("$label: the instruction no longer posts the comment matching /$extra/")
  fi
}

name="$skill_md's Step done and pin paths tick an issue criterion only on criterion-finished.sh exit 0, ticking nothing on exit 3"
problems=()
gated_tick 'Step done (cycle loop)' '### 3. The cycle loop' '### ✅ step done'
gated_tick 'pin path' '## Already satisfied — the pin' ''
report "$name"

name="$skill_md's step 2 tells the conductor to end each ledger step with ⟦criterion k⟧ and to leave a gap step without one"
problems=()
plan_recs="$(section_records '### 2. Scope & plan → the ledger')"
grep -Eq '(^| )end(s|ing)? ' < <(grep -F '⟦criterion k⟧' <<<"$plan_recs") ||
  problems+=("plan guidance: no instruction in step 2 tells the conductor to end a ledger step with ⟦criterion k⟧")
grep -Eq '(without|no |none|omit)' < <(grep -F '⟦criterion' <<<"$plan_recs" | grep -F 'gap') ||
  problems+=("plan guidance: no instruction in step 2 says a gap step carries no ⟦criterion k⟧")
report "$name"

off_cycle_line() {
  local marker="$1" phrase1="$2" phrase2="$3" what="$4"
  grep -F -- "- [ ] <criterion> $marker ⟦criterion k⟧" <<<"$plan_recs" > /dev/null ||
    problems+=("plan guidance: step 2 never shows the ledger line '- [ ] <criterion> $marker ⟦criterion k⟧'")
  ledger_rec="$(head -1 < <(grep -F "$marker" <<<"$plan_recs" | grep -F "$phrase1" | grep -F "$phrase2"))"
  if [[ -z "$ledger_rec" ]]; then
    problems+=("plan guidance: no instruction in step 2 names $marker for a criterion $what")
    return 1
  fi
  [[ "$ledger_rec" =~ (not|never|no)\ [^.]*red/green ]] ||
    problems+=("plan guidance: the $marker instruction never says such a criterion is not planned as a Red/Green step")
  return 0
}

name="#481: $skill_md's step 2 writes a criterion whose only observable is the test command passing as one ⟦full-suite⟧ ledger line covered by the full-suite run, not a Red/Green step"
problems=()
off_cycle_line '⟦full-suite⟧' 'test command' 'full-suite run' \
  'whose only observable is the test command passing, covered by the full-suite run'
report "$name"

name="#481: $skill_md's Draft PR step ticks every ⟦full-suite⟧ line and its issue criterion, with no refactor-pending mark, only once the last full-suite run — the rebased tip's after a rebase — is green, never after a red one"
problems=()
pr_rec="$(head -1 < <(section_records '### 4. Draft PR' | grep -F '⟦full-suite⟧' | grep -E 'tick'))"
if [[ -z "$pr_rec" ]]; then
  problems+=("draft PR: no instruction in step 4 ticks a ⟦full-suite⟧ ledger line — the rule could not be checked")
else
  [[ "$pr_rec" == *tick-issue-criterion.sh* ]] ||
    problems+=("draft PR: the ⟦full-suite⟧ tick never ticks the issue criterion it finishes with tick-issue-criterion.sh")
  [[ "$pr_rec" =~ (no|without|never)\ [^.]*refactor.pending ]] ||
    problems+=("draft PR: the ⟦full-suite⟧ tick never says it carries no refactor-pending mark")
  [[ "$pr_rec" =~ last\ full-suite\ run[^.]*green ]] ||
    problems+=("draft PR: the ⟦full-suite⟧ tick is not tied to the last full-suite run being green")
  [[ "$pr_rec" == *"rebased tip"* ]] ||
    problems+=("draft PR: the ⟦full-suite⟧ tick never says the rebased tip's run is the one that counts after a rebase")
  [[ "$pr_rec" =~ (never|not|no)\ [^.]*red ]] ||
    problems+=("draft PR: the ⟦full-suite⟧ tick never says a red run ticks nothing")
fi
report "$name"

name="#481: $skill_md's step 2 writes a criterion whose deliverable is the record of a manual check as one ⟦human-owed⟧ ledger line owed by a human, not a Red/Green step, never handed to a developer leaf"
problems=()
if off_cycle_line '⟦human-owed⟧' 'manual check' 'human' \
  'whose deliverable is the record of a manual check, owed by a human'; then
  [[ "$ledger_rec" =~ (not|never|no)\ [^.]*developer\ leaf ]] ||
    problems+=("plan guidance: the ⟦human-owed⟧ instruction never says such a criterion is never handed to a developer leaf")
fi
report "$name"

name="#481: $skill_md's Draft PR step lists every ⟦human-owed⟧ ledger line in the PR body under ## Owed by a human, each naming its criterion number, and adds no such section when the ledger holds none"
problems=()
owed_rec="$(head -1 < <(section_records '### 4. Draft PR' | grep -F '⟦human-owed⟧' | grep -F '## owed by a human'))"
if [[ -z "$owed_rec" ]]; then
  problems+=("draft PR: no instruction in step 4 lists ⟦human-owed⟧ ledger lines under '## Owed by a human' — the rule could not be checked")
else
  [[ "$owed_rec" == *"pr body"* ]] ||
    problems+=("draft PR: the ⟦human-owed⟧ instruction never says the lines go into the PR body")
  [[ "$owed_rec" =~ criterion\ (number|k) ]] ||
    problems+=("draft PR: the ⟦human-owed⟧ instruction never says each listed line names its criterion number")
  [[ "$owed_rec" =~ (no|none|omit|without)\ [^.]*(section|heading) ]] ||
    problems+=("draft PR: the ⟦human-owed⟧ instruction never says no such section is added when the ledger holds none")
fi
report "$name"

does_not_hold() {
  local label="$1" rec="$2" marker
  if [[ -z "$rec" ]]; then
    problems+=("$label: the condition could not be found — the rule could not be checked")
    return
  fi
  for marker in '⟦full-suite⟧' '⟦human-owed⟧'; do
    [[ "$rec" == *"$marker"* ]] ||
      problems+=("$label: the condition never names $marker lines")
  done
  [[ "$rec" =~ unchecked[^.]*(not|never)\ hold[^.]*back ]] ||
    problems+=("$label: the condition never says an unchecked off-cycle line does not hold the run back")
}

name="#481: $skill_md's Draft PR entry condition and Resume's go-to-draft-PR condition say unchecked ⟦full-suite⟧ and ⟦human-owed⟧ lines do not hold a run back from its draft PR"
problems=()
does_not_hold 'draft PR entry' \
  "$(head -1 < <(section_records '### 4. Draft PR' | grep -F 'reached when'))"
does_not_hold 'resume' \
  "$(head -1 < <(section_records '## Resume' | grep -E 'go to the \*?\*?draft pr'))"
report "$name"

# 8. One criterion (#495) — criterion k's text, handed to tick-issue-criterion.sh, is read out of
#    the issue body's `## Acceptance criteria` section as ledger-steps.sh's records rather than by
#    a checkbox pattern the procedure spells itself.
name="#495: every $skill_md instruction that ticks criterion k in the issue body reads its text from ledger-steps.sh's records, spelling no checkbox pattern of its own"
problems=()
ticks="$(records_of < "$skill_path" | grep -F 'tick-issue-criterion.sh <n> "$(' || true)"
if [[ -z "$ticks" ]]; then
  problems+=("no instruction of $skill_md hands tick-issue-criterion.sh a criterion text read out of the issue body — the rule could not be checked")
else
  while IFS= read -r rec; do
    [[ "$rec" == *'ledger-steps.sh'* ]] ||
      problems+=("reads criterion k's text without ledger-steps.sh: $(printf '%.160s' "${rec#*tick-issue-criterion.sh}")")
    [[ "$rec" != *'\[[ x]\]'* ]] ||
      problems+=("still spells its own checkbox pattern: $(printf '%.160s' "${rec#*tick-issue-criterion.sh}")")
  done <<< "$ticks"
fi
report "$name"

# 9. One criterion (#495) — the last ticked step, named to event.sh step-done, to event.sh pin and
#    to the CI-repair step-added event and add-ledger-step.sh anchor, is read off ledger-steps.sh's
#    records rather than by a checkbox pattern the procedure spells itself.
name="#495: every $skill_md instruction that names the last ticked step reads it from ledger-steps.sh's records, spelling no checkbox pattern of its own"
problems=()
for anchor in 'event.sh step-done' 'event.sh pin' 'event.sh step-added anchor="$(' "add-ledger-step.sh .tdd/issue-<n>.md after \"\$("; do
  hits="$(grep -F -- "$anchor" "$skill_path" | grep -vF -e 'next-unchecked.sh' -e 'next-pending-refactor.sh' || true)"
  if [[ -z "$hits" ]]; then
    problems+=("no instruction of $skill_md runs '$anchor' on the last ticked step — the rule could not be checked")
    continue
  fi
  while IFS= read -r line; do
    [[ "$line" == *'ledger-steps.sh'* ]] ||
      problems+=("'$anchor' reads the last ticked step without ledger-steps.sh: $(printf '%.160s' "$line")")
    [[ "$line" != *'\[x\]'* ]] ||
      problems+=("'$anchor' still spells its own checkbox pattern: $(printf '%.160s' "$line")")
  done <<< "$hits"
done
report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
