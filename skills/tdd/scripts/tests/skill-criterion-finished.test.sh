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

plan_recs="$(section_records '### 2. Scope & plan → the ledger')"
rc_rec="$(first_record "$plan_recs" -F '⟦replaces-case⟧' -F 'implementation case')"

name="#1397: $skill_md's pin section sends a ⟦replaces-case⟧ step whose Red reports PASSES through verify-pin, then a green leaf deleting exactly the named cases, judged by the replaces-case verify-green and accepted only once mutation-parity.sh exits 0, then one tick"
problems=()
pin_rc_rec="$(first_record "$(section_records '## Already satisfied — the pin')" -F '⟦replaces-case⟧')"
if [[ -z "$pin_rc_rec" ]]; then
  problems+=("pin path: no instruction under '## Already satisfied — the pin' states the path for a ⟦replaces-case⟧ step whose Red reports PASSES — the path could not be checked")
else
  [[ "$pin_rc_rec" == *passes* ]] ||
    problems+=("pin path: the ⟦replaces-case⟧ instruction never names a Red that reports PASSES")
  [[ "$pin_rc_rec" =~ verify-pin|verify\.sh\ pin ]] ||
    problems+=("pin path: the ⟦replaces-case⟧ instruction never runs verify-pin first")
  [[ "$pin_rc_rec" =~ green\ leaf && "$pin_rc_rec" =~ delet && "$pin_rc_rec" == *"exactly the named"* ]] ||
    problems+=("pin path: the ⟦replaces-case⟧ instruction never launches a green leaf that deletes exactly the named cases")
  [[ "$pin_rc_rec" == *verify-green* ]] ||
    problems+=("pin path: the ⟦replaces-case⟧ instruction never judges the deletion by the replaces-case verify-green")
  [[ "$pin_rc_rec" == *mutation-parity.sh* && "$pin_rc_rec" =~ exits?\ \*{0,2}0 ]] ||
    problems+=("pin path: the ⟦replaces-case⟧ instruction never accepts the deletion only once mutation-parity.sh exits 0")
  [[ "$pin_rc_rec" =~ one\ tick|tick[^.]*once|single\ tick ]] ||
    problems+=("pin path: the ⟦replaces-case⟧ instruction never ends the step in one tick")
fi
report "$name"

name="#1397: $skill_md's pin PASS bullet names the ⟦replaces-case⟧ exception before its tick-and-commit, and the pin path and step 2 say whether Refactor and ⟂ refactor pending follow the deletion green"
problems=()
pin_recs="$(section_records '## Already satisfied — the pin')"
pass_rec="$(first_record "$pin_recs" -F 'pass (exit 0)')"
if [[ -z "$pass_rec" ]]; then
  problems+=("pin PASS: no PASS (exit 0) bullet under '## Already satisfied — the pin' — the exception could not be checked")
else
  pass_before_tick="${pass_rec%%tick-ledger.sh*}"
  [[ "$pass_before_tick" == *⟦replaces-case⟧* ]] ||
    problems+=("pin PASS: the bullet never names the ⟦replaces-case⟧ exception before its tick-ledger.sh commit")
fi
pin_refactor_rec="$(first_record "$pin_recs" -F '⟦replaces-case⟧' -F 'refactor pending')"
[[ -n "$pin_refactor_rec" && "$pin_refactor_rec" =~ delet && "$pin_refactor_rec" =~ refactor[^\ ]*\ (phase|leaf|follows|runs|does|is) ]] ||
  problems+=("pin path: no ⟦replaces-case⟧ instruction says whether Refactor and ⟂ refactor pending follow the deletion green")
[[ "$rc_rec" =~ refactor ]] ||
  problems+=("plan guidance: the ⟦replaces-case⟧ step-kind paragraph never says whether Refactor follows the deletion green")
report "$name"

name="#1397: $skill_md's Guardrails line on a test that passes against unmodified code carves out the ⟦replaces-case⟧ deletion green"
problems=()
guard_rec="$(first_record "$(section_records '## Guardrails')" -F 'passes against unmodified code')"
if [[ -z "$guard_rec" ]]; then
  problems+=("guardrails: no line under '## Guardrails' names a test that passes against unmodified code — the carve-out could not be checked")
else
  [[ "$guard_rec" == *⟦replaces-case⟧* ]] ||
    problems+=("guardrails: the line never carves out a ⟦replaces-case⟧ step")
  [[ "$guard_rec" =~ green && "$guard_rec" =~ delet ]] ||
    problems+=("guardrails: the line never names the green that deletes the named cases")
fi
report "$name"

name="#1397: $skill_md's ⟦replaces-case⟧ pin-then-delete path keeps its meaning: the Guardrails exception is not negated, nothing is committed or ticked before the deletion green, and the deletion is accepted only once mutation-parity.sh exits 0"
problems=()
guard_after="${guard_rec#*⟦replaces-case⟧}"
[[ "$guard_rec" =~ (save|except|unless|but)\ (on\ )?(a\ )?\`?⟦replaces-case⟧ ]] ||
  problems+=("guardrails: the ⟦replaces-case⟧ clause is not introduced as an exception (save/except/unless/but)")
[[ ! "$guard_after" =~ (^|[^a-z])(never|not|no)([^a-z]|$) ]] ||
  problems+=("guardrails: the ⟦replaces-case⟧ clause negates the deletion green: $guard_after")
pin_before_green="${pin_rc_rec%%green leaf*}"
pin_before_green="${pin_before_green//commit nothing/}"
[[ "$pin_rc_rec" == *"green leaf"* && ! "$pin_before_green" =~ commit|tick ]] ||
  problems+=("pin path: a commit or tick comes before the deletion green: $pin_before_green")
[[ "$pin_rc_rec" == *"accepted only once"* && ! "$pin_rc_rec" =~ whether\ or\ not|regardless|even\ if ]] ||
  problems+=("pin path: the deletion is not accepted only once mutation-parity.sh exits 0")
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
