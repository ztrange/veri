#!/usr/bin/env bash
# Unit tests for when the conductor ticks an acceptance criterion in the issue body, as
# skills/tdd/SKILL.md prescribes it, read as text.
#
# Contract under test:
#   1. In both SKILL.md's cycle loop and its pin path, the instruction that runs
#      `tick-issue-criterion.sh` also runs `criterion-finished.sh`, ticks on its exit 0 and
#      ticks nothing on its exit 3; the cycle loop's instruction still posts `### ✅ Step done`.
#   2. SKILL.md step 2's plan-writing guidance tells the conductor to end each ledger step with
#      ` ⟦criterion k⟧` for the criterion it serves, and to leave a gap step without one.
#
# Run: scripts/tests/skill-criterion-finished.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"
skill_md="skills/tdd/SKILL.md"
skill_path="$ROOT/$skill_md"


source "$HERE/lib/harness.sh"
source "$HERE/lib/first-record.sh"

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
  rec="$(first_record "$(section_records "$head")" -F 'tick-issue-criterion.sh')"
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
  ledger_rec="$(first_record "$plan_recs" -F "$marker" -F "$phrase1" -F "$phrase2")"
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
pr_rec="$(first_record "$(section_records '### 4. Draft PR')" -F '⟦full-suite⟧' -E 'tick')"
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

name="#727: $skill_md's step 2 writes a criterion that is a property of the branch's own diff as one ⟦diff-checked⟧ ledger line, not a Red/Green step and adding no test, and keeps a criterion stating a rule future changes must keep a Red/Green step"
problems=()
if off_cycle_line '⟦diff-checked⟧' 'own diff' 'test' \
  "that is a property of the branch's own diff"; then
  for shape in removed unchanged confined; do
    [[ "$ledger_rec" == *"$shape"* ]] ||
      problems+=("plan guidance: the ⟦diff-checked⟧ instruction never names a criterion of something $shape")
  done
  [[ "$ledger_rec" =~ (adds|add|leaves)\ no\ test ]] ||
    problems+=("plan guidance: the ⟦diff-checked⟧ instruction never says its step adds no test")
fi
grep -E 'future change[^.]*red/green|red/green[^.]*future change' < <(grep -F 'rule' <<<"$plan_recs") > /dev/null ||
  problems+=("plan guidance: no instruction in step 2 says a criterion stating a rule future changes must keep is still a Red/Green step")
report "$name"

name="#727: $skill_md's cycle loop runs a ⟦diff-checked⟧ step with no Red leaf — a develop-diff leaf built by build-develop-prompt.sh diff, then the blind diff verifier against git merge-base HEAD origin/<default> — ticking the step and its criterion on PASS, revising under REVISE_BUDGET on REJECT and bailing as a system failure on exit 2"
problems=()
dc_rec="$(section_records '### 3. The cycle loop' | grep -F '⟦diff-checked⟧' | tr '\n' ' ')"
if [[ -z "$dc_rec" ]]; then
  problems+=("cycle loop: no instruction under '### 3. The cycle loop' names a ⟦diff-checked⟧ step — the rule could not be checked")
else
  [[ "$dc_rec" =~ (no|without|never|skips?)\ [^.]*red\ leaf ]] ||
    problems+=("cycle loop: the ⟦diff-checked⟧ instruction never says the step runs no Red leaf")
  [[ "$dc_rec" == *develop-diff* && "$dc_rec" == *"build-develop-prompt.sh diff"* ]] ||
    problems+=("cycle loop: the ⟦diff-checked⟧ instruction never launches a develop-diff leaf built by build-develop-prompt.sh diff")
  [[ "$dc_rec" =~ (verify|run-verdict)\.sh\ --step\ [^\ ]+\ (--fast-cmd\ [^\ ]+\ )?diff\  ]] ||
    problems+=("cycle loop: the ⟦diff-checked⟧ instruction never runs the blind diff verifier with --step")
  [[ "$dc_rec" == *"git merge-base head origin/<default>"* ]] ||
    problems+=("cycle loop: the ⟦diff-checked⟧ instruction never verifies against the run's branch point, git merge-base HEAD origin/<default>")
  [[ "$dc_rec" =~ pass[^.]*tick && "$dc_rec" == *tick-issue-criterion.sh* ]] ||
    problems+=("cycle loop: the ⟦diff-checked⟧ instruction never ties ticking the step and its issue criterion to PASS")
  [[ "$dc_rec" =~ reject[^.]*revis && "$dc_rec" == *revise_budget* ]] ||
    problems+=("cycle loop: the ⟦diff-checked⟧ instruction never makes a REJECT a revise under REVISE_BUDGET")
  [[ "$dc_rec" =~ exit\ \*?\*?2[^.]*system[^.]*bail|exit\ \*?\*?2[^.]*bail[^.]*system ]] ||
    problems+=("cycle loop: the ⟦diff-checked⟧ instruction never makes the verifier's exit 2 a system bail")
fi
report "$name"

name="#875: $skill_md's ⟦diff-checked⟧ step records its step base sha with git rev-parse HEAD before the develop-diff leaf runs and passes it to the blind diff verifier after the branch point"
problems=()
if [[ -z "$dc_rec" ]]; then
  problems+=("cycle loop: no instruction under '### 3. The cycle loop' names a ⟦diff-checked⟧ step — the rule could not be checked")
else
  [[ "$dc_rec" =~ git\ rev-parse\ head[^.]*before[^.]*develop-diff ]] ||
    problems+=("cycle loop: the ⟦diff-checked⟧ instruction never records the step's base sha with git rev-parse HEAD before the develop-diff leaf runs")
  [[ "$dc_rec" =~ run-verdict\.sh\ --step\ [^\ ]+\ (--fast-cmd\ [^\ ]+\ )?diff\ \<spec-file\>\ \<branch-base-sha\>\ \<step-base-sha\> ]] ||
    problems+=("cycle loop: the ⟦diff-checked⟧ instruction never passes the step base sha to run-verdict.sh after the branch point")
fi
report "$name"

name="#976: $skill_md takes a ⟦diff-checked⟧ step's step base sha, on a fresh run and on a resume alike, as the last commit that changed the ledger, never a HEAD taken after a killed attempt's commit"
problems=()
base_idiom='git log -1 --format=%h -- .tdd/issue-<n>.md'
base_rec="$(records_of < "$skill_path" | grep -F '⟦diff-checked⟧' | grep -F -- "$base_idiom" | tr '\n' ' ')"
if [[ -z "$base_rec" ]]; then
  problems+=("no instruction of $skill_md takes a ⟦diff-checked⟧ step's base sha with '$base_idiom'")
else
  [[ "$base_rec" =~ step\ base\ sha[^.]*last\ commit\ that\ changed\ the\ ledger|last\ commit\ that\ changed\ the\ ledger[^.]*step\ base\ sha ]] ||
    problems+=("the ⟦diff-checked⟧ base sha instruction never says the step base sha is the last commit that changed the ledger")
  [[ "$base_rec" =~ fresh && "$base_rec" =~ resum ]] ||
    problems+=("the ⟦diff-checked⟧ base sha instruction never says the rule holds on a fresh run and on a resume alike")
  [[ "$base_rec" =~ (never|not)\ [^.]*head[^.]*killed ]] ||
    problems+=("the ⟦diff-checked⟧ base sha instruction never rules out a HEAD taken after a killed attempt's commit")
fi
report "$name"

name="#671: $skill_md's step 2 plans a criterion replacing an implementation case under ADR 0027 as one ⟦replaces-case⟧ step naming the suite path and the case's exact name, whose Red is the pytest case failing against the code before the change"
problems=()
rc_rec="$(first_record "$plan_recs" -F '⟦replaces-case⟧' -F 'implementation case')"
if [[ -z "$rc_rec" ]]; then
  problems+=("plan guidance: no instruction in step 2 names ⟦replaces-case⟧ for a criterion replacing an implementation case")
else
  [[ "$rc_rec" == *"adr 0027"* ]] ||
    problems+=("plan guidance: the ⟦replaces-case⟧ instruction never ties the mark to ADR 0027")
  [[ "$rc_rec" =~ one\ step ]] ||
    problems+=("plan guidance: the ⟦replaces-case⟧ instruction never says the criterion is planned as one step")
  [[ "$rc_rec" =~ suite(.s)?\ path|path\ of\ the\ suite ]] ||
    problems+=("plan guidance: the ⟦replaces-case⟧ instruction never says the step names the suite path")
  [[ "$rc_rec" == *"exact name"* ]] ||
    problems+=("plan guidance: the ⟦replaces-case⟧ instruction never says the step names the case's exact name")
  [[ "$rc_rec" =~ (^|[^a-z])red([^a-z]|$) && "$rc_rec" =~ pytest\ case[^.]*fail[^.]*before\ the\ change ]] ||
    problems+=("plan guidance: the ⟦replaces-case⟧ instruction never says the step's Red is the pytest case failing against the code before the change")
fi
report "$name"

name="#1260: $skill_md's ⟦replaces-case⟧ planning paragraph lets one step name one suite path and a list of its cases each by exact name, grouping related cases of one suite into one step, about a dozen at most, one case a valid group of one"
problems=()
if [[ -z "$rc_rec" ]]; then
  problems+=("plan guidance: no instruction in step 2 names ⟦replaces-case⟧ for a criterion replacing an implementation case — the rule could not be checked")
else
  [[ "$rc_rec" =~ list\ of\ [^.]*cases[^.]*each\ by\ (its\ )?exact\ name ]] ||
    problems+=("plan guidance: the ⟦replaces-case⟧ instruction never lets the step name a list of the suite's cases, each by its exact name")
  [[ "$rc_rec" =~ group[^.]*related\ cases\ of\ one\ suite[^.]*one\ step ]] ||
    problems+=("plan guidance: the ⟦replaces-case⟧ instruction never tells the planner to group related cases of one suite into one step")
  [[ "$rc_rec" =~ about\ a\ dozen ]] ||
    problems+=("plan guidance: the ⟦replaces-case⟧ instruction never caps a group at about a dozen cases")
  [[ "$rc_rec" =~ group\ of\ one ]] ||
    problems+=("plan guidance: the ⟦replaces-case⟧ instruction never says one case remains a valid group of one")
fi
report "$name"

name="#671: CONTEXT.md defines contract case, implementation case and the ⟦replaces-case⟧ mark"
problems=()
context_path="$ROOT/CONTEXT.md"
context_entries="$(awk '
  function flush() { if (rec != "") print rec; rec = "" }
  /^\*\*[^*]+\*\*:/ { flush(); rec = $0; next }
  /^#/ || /^[[:space:]]*$/ { flush(); next }
  rec != "" { rec = rec " " $0 }
  END { flush() }' "$context_path")"
for term in 'Contract case' 'Implementation case'; do
  grep -F "**$term**:" <<<"$context_entries" > /dev/null ||
    problems+=("CONTEXT.md: no **$term**: entry")
done
grep -F '⟦replaces-case⟧' <<<"$context_entries" > /dev/null ||
  problems+=("CONTEXT.md: no glossary entry defines the ⟦replaces-case⟧ mark")
report "$name"

name="#481: $skill_md's Draft PR step lists every ⟦human-owed⟧ ledger line in the PR body under ## Owed by a human, each naming its criterion number, and adds no such section when the ledger holds none"
problems=()
owed_rec="$(first_record "$(section_records '### 4. Draft PR')" -F '⟦human-owed⟧' -F '## owed by a human')"
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
  "$(first_record "$(section_records '### 4. Draft PR')" -F 'reached when')"
does_not_hold 'resume' \
  "$(first_record "$(section_records '## Resume')" -E 'go to the \*?\*?draft pr')"
report "$name"

reads_ledger_steps() {
  local anchor="$1" box="$2" lines="$3" line
  if [[ -z "$lines" ]]; then
    problems+=("no instruction of $skill_md runs '$anchor' — the rule could not be checked")
    return
  fi
  while IFS= read -r line; do
    [[ "$line" == *'ledger-steps.sh'* ]] ||
      problems+=("'$anchor' reads without ledger-steps.sh: $line")
    [[ "$line" != *"$box"* ]] ||
      problems+=("'$anchor' still spells its own checkbox pattern: $line")
  done <<< "$lines"
}

name="#495: every $skill_md instruction that ticks criterion k in the issue body reads its text from ledger-steps.sh's records, spelling no checkbox pattern of its own"
problems=()
anchor='tick-issue-criterion.sh <n> "$('
reads_ledger_steps "$anchor" '\[[ x]\]' "$(records_of < "$skill_path" | grep -F -- "$anchor" || true)"
report "$name"

name="#495: every $skill_md instruction that names the last ticked step reads it from ledger-steps.sh's records, spelling no checkbox pattern of its own"
problems=()
for anchor in 'event.sh step-done' 'event.sh pin' 'event.sh step-added anchor="$(' "add-ledger-step.sh .tdd/issue-<n>.md after \"\$("; do
  reads_ledger_steps "$anchor" '\[x\]' \
    "$(grep -F -- "$anchor" "$skill_path" | grep -vF -e 'next-unchecked.sh' -e 'next-pending-refactor.sh' || true)"
done
report "$name"

name="#495: every $skill_md instruction that counts the steps left for run-affordable.sh reads them from ledger-steps.sh's records, spelling no checkbox pattern of its own"
problems=()
anchor='run-affordable.sh "$('
reads_ledger_steps "$anchor" '\[ \]' "$(grep -F -- "$anchor" "$skill_path" || true)"
report "$name"

name="#495: $skill_md's reconcile check compares ledger-steps.sh's state and pending fields, grepping the markdown for neither a tick nor the pending mark"
problems=()
anchor='diff <('
lines="$(grep -F -- "$anchor" "$skill_path" | grep -F -- '.tdd/reconcile-ledger.before' || true)"
reads_ledger_steps "$anchor" '[x]' "$lines"
while IFS= read -r line; do
  [[ -z "$line" || "$line" != *'⟂ refactor pending'* ]] ||
    problems+=("'$anchor' still greps for the pending mark itself: $line")
done <<< "$lines"
report "$name"

finish
