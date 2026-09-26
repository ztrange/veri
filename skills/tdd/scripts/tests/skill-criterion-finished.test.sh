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

# records_of — the lines on stdin as records, lowercased, whitespace collapsed: a record runs
# from a `N. ` or a `- ` (indented or not), or from the first line after a blank, up to the
# next such line or blank. A fenced block inside a bullet stays part of that bullet's record.
# Same grammar as skill-refactor-pending.test.sh's reader of the same name.
records_of() {
  awk '
    function flush() { if (rec != "") { gsub(/[[:space:]]+/, " ", rec); print rec } rec = "" }
    /^[0-9]+\. / || /^[[:space:]]*- / { flush(); rec = $0; next }
    /^[[:space:]]*$/ { flush(); next }
    rec == "" { rec = $0; next }
    { rec = rec " " $0 }
    END { flush() }' | tr '[:upper:]' '[:lower:]'
}

# section_records <heading-line> — the records of the section headed exactly <heading-line>,
# up to the next heading of the same or a higher level.
section_records() {
  awk -v head="$1" '
    $0 == head { inside = 1; level = index(head, " "); next }
    inside && /^#+ / && index($0, " ") <= level { exit }
    inside' "$skill_path" | records_of
}

# gated_tick <label> <heading-line> <extra-regex> — find the record in that section that runs
# tick-issue-criterion.sh and require it to run criterion-finished.sh, tick on exit 0 and tick
# nothing on exit 3, plus <extra-regex> if non-empty. Fails closed when no record ticks at all.
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

# 1. One criterion — the issue criterion is ticked only when its every step is done — asked
#    of both places that tick it.
name="$skill_md's Step done and pin paths tick an issue criterion only on criterion-finished.sh exit 0, ticking nothing on exit 3"
problems=()
gated_tick 'Step done (cycle loop)' '### 3. The cycle loop' '### ✅ step done'
gated_tick 'pin path' '## Already satisfied — the pin' ''
report "$name"

# 2. One criterion — the plan the gate reads is written with the notation it reads.
name="$skill_md's step 2 tells the conductor to end each ledger step with ⟦criterion k⟧ and to leave a gap step without one"
problems=()
plan_recs="$(section_records '### 2. Scope & plan → the ledger')"
grep -Eq '(^| )end(s|ing)? ' < <(grep -F '⟦criterion k⟧' <<<"$plan_recs") ||
  problems+=("plan guidance: no instruction in step 2 tells the conductor to end a ledger step with ⟦criterion k⟧")
grep -Eq '(without|no |none|omit)' < <(grep -F '⟦criterion' <<<"$plan_recs" | grep -F 'gap') ||
  problems+=("plan guidance: no instruction in step 2 says a gap step carries no ⟦criterion k⟧")
report "$name"

# 3. One criterion (#481) — a criterion whose only observable is that the test command passes
#    has no failing test to write, so a Red leaf can only answer UNTESTABLE and the run bails.
#    Step 2 must write it as one `⟦full-suite⟧` ledger line the full-suite run covers, not as
#    a Red/Green step.
name="#481: $skill_md's step 2 writes a criterion whose only observable is the test command passing as one ⟦full-suite⟧ ledger line covered by the full-suite run, not a Red/Green step"
problems=()
grep -F -- '- [ ] <criterion> ⟦full-suite⟧ ⟦criterion k⟧' <<<"$plan_recs" > /dev/null ||
  problems+=("plan guidance: step 2 never shows the ledger line '- [ ] <criterion> ⟦full-suite⟧ ⟦criterion k⟧'")
full_rec="$(head -1 < <(grep -F '⟦full-suite⟧' <<<"$plan_recs" | grep -F 'test command' | grep -F 'full-suite run'))"
if [[ -z "$full_rec" ]]; then
  problems+=("plan guidance: no instruction in step 2 names ⟦full-suite⟧ for a criterion whose only observable is the test command passing, covered by the full-suite run")
else
  [[ "$full_rec" =~ (not|never|no)\ [^.]*red/green ]] ||
    problems+=("plan guidance: the ⟦full-suite⟧ instruction never says such a criterion is not planned as a Red/Green step")
fi
report "$name"

# 4. One criterion (#481) — a ⟦full-suite⟧ line has no Red/Green cycle to tick it, so the
#    Draft PR step must: every such line and the issue criterion it finishes, with no
#    refactor-pending mark, only once the last full-suite run before the PR is readied is
#    green — the rebased tip's when the branch was rebased — and never after a red one.
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

# 5. One criterion (#481) — a criterion whose deliverable is the record of a manual check has
#    no failing test to write and is a human's act, not a leaf's. Step 2 must write it as one
#    `⟦human-owed⟧` ledger line owed by a human, not as a Red/Green step, and never hand it to
#    a developer leaf.
name="#481: $skill_md's step 2 writes a criterion whose deliverable is the record of a manual check as one ⟦human-owed⟧ ledger line owed by a human, not a Red/Green step, never handed to a developer leaf"
problems=()
grep -F -- '- [ ] <criterion> ⟦human-owed⟧ ⟦criterion k⟧' <<<"$plan_recs" > /dev/null ||
  problems+=("plan guidance: step 2 never shows the ledger line '- [ ] <criterion> ⟦human-owed⟧ ⟦criterion k⟧'")
human_rec="$(head -1 < <(grep -F '⟦human-owed⟧' <<<"$plan_recs" | grep -F 'manual check' | grep -F 'human'))"
if [[ -z "$human_rec" ]]; then
  problems+=("plan guidance: no instruction in step 2 names ⟦human-owed⟧ for a criterion whose deliverable is the record of a manual check, owed by a human")
else
  [[ "$human_rec" =~ (not|never|no)\ [^.]*red/green ]] ||
    problems+=("plan guidance: the ⟦human-owed⟧ instruction never says such a criterion is not planned as a Red/Green step")
  [[ "$human_rec" =~ (not|never|no)\ [^.]*developer\ leaf ]] ||
    problems+=("plan guidance: the ⟦human-owed⟧ instruction never says such a criterion is never handed to a developer leaf")
fi
report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
