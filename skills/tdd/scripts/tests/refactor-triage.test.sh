#!/usr/bin/env bash
# Unit tests for scripts/refactor-triage.sh — reads a finished refactor leaf's report on
# stdin and says whether another refactor leaf is worth launching. Zero-dependency
# plain-shell asserts, same idiom as refactor-budget.test.sh, the suite for the script on
# the refactor loop's other axis — refactor-triage.sh's own header is where the two axes
# are told apart.
#
# Why this exists (issue #149): the loop's two stop conditions are a leaf reporting
# `nothing left to tidy` and `refactor-budget.sh` exiting 3, and in practice only the
# second fires — a leaf asked for one transform always finds one, so the loop spends its
# whole budget on transforms that reword and re-cite. Since #149 every `CANDIDATES:` line
# the leaf reports carries the class of the transform it names, `structural` or `cosmetic`
# as prompts/develop-refactor.md's *The two classes of candidate* defines them. This script
# is what turns those classed lines into the loop's third stop condition.
#
# Contract under test, in the four-code convention (CLAUDE.md, *Exit codes are the API*):
#   report on stdin → exit 0, printing the structural candidates, when at least one is
#                     listed: there is work left that is worth a leaf.
#                   → exit 3 when only cosmetic candidates or `none` remain.
#                   → exit 2, diagnostic on stderr and nothing on stdout, when a candidate
#                     line carries no class or an unknown one, or the report lists no
#                     `CANDIDATES:` line at all.
#
# And then the caller's half of that same contract: SKILL.md's *Refactor loop* is where a
# conductor learns to run this script and what to do with each answer, and a script nothing
# calls decides nothing. That case reads the document as text, the way refactor-budget.test.sh
# case 8 reads it for the sibling script's default.
#
# Run: scripts/tests/refactor-triage.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
TRIAGE="$HERE/../refactor-triage.sh"

source "$HERE/lib/harness.sh"

name="a report listing structural candidates exits 0 and prints them"
problems=()

leaf_report="$(mktemp)"
cat > "$leaf_report" <<'REPORT'
RESULT: applied "fold verify.sh's two prompt paths into one", suite green
FLAGS: none
CANDIDATES: structural | fold verify.sh's two mktemp calls into one helper
CANDIDATES: cosmetic | reflow the header comment to ninety columns
CANDIDATES: structural | rename $tmp to $prompt_file, which is what it holds
REPORT

out="$(mktemp)"
"$TRIAGE" <"$leaf_report" >"$out" 2>/dev/null && code=0 || code=$?

[[ "$code" == 0 ]] ||
  problems+=("want exit 0 while structural candidates remain, got $code")

lines="$(grep -c '' "$out")"
[[ "$lines" == 2 ]] ||
  problems+=("want the 2 structural candidates on stdout, one per line, got $lines line(s): $(printf '%q' "$(cat "$out")")")

while IFS= read -r transform; do
  hits="$(grep -cF "$transform" "$out")"
  [[ "$hits" == 1 ]] ||
    problems+=("want the structural candidate '$transform' named on exactly 1 line of stdout, found on $hits")
done <<'STRUCTURAL'
fold verify.sh's two mktemp calls into one helper
rename $tmp to $prompt_file, which is what it holds
STRUCTURAL

cosmetic='reflow the header comment to ninety columns'
grep -qF "$cosmetic" "$out" &&
  problems+=("the cosmetic candidate '$cosmetic' is on stdout; only structural ones belong there")

rm -f "$leaf_report" "$out"
report "$name"

name="a report with no structural candidate left exits 3"
problems=()

cosmetic_only="$(mktemp)"
cat > "$cosmetic_only" <<'REPORT'
RESULT: applied "extract the two mktemp calls into one helper", suite green
FLAGS: none
CANDIDATES: cosmetic | reflow the header comment to ninety columns
CANDIDATES: cosmetic | re-cite SKILL.md's Refactor entry by section, not line
REPORT

nothing_left="$(mktemp)"
cat > "$nothing_left" <<'REPORT'
RESULT: applied "inline the single-use $phase_label variable", suite green
FLAGS: none
CANDIDATES: none
REPORT

stops_probe() {
  local label="$1" fixture="$2" code
  "$TRIAGE" <"$fixture" >/dev/null 2>&1 && code=0 || code=$?
  [[ "$code" == 3 ]] ||
    problems+=("$label: want exit 3 — nothing worth another leaf — got $code")
}

stops_probe "only cosmetic candidates" "$cosmetic_only"
stops_probe "CANDIDATES: none" "$nothing_left"

rm -f "$cosmetic_only" "$nothing_left"
report "$name"

name="a malformed report exits 2 with a diagnostic on stderr and nothing on stdout"
problems=()

no_class="$(mktemp)"
cat > "$no_class" <<'REPORT'
RESULT: applied "extract the two mktemp calls into one helper", suite green
FLAGS: none
CANDIDATES: fold verify.sh's two prompt paths into one
REPORT

unknown_class="$(mktemp)"
cat > "$unknown_class" <<'REPORT'
RESULT: applied "extract the two mktemp calls into one helper", suite green
FLAGS: none
CANDIDATES: cosmic | reflow the header comment to ninety columns
REPORT

no_candidates="$(mktemp)"
cat > "$no_candidates" <<'REPORT'
RESULT: applied "inline the single-use $phase_label variable", suite green
FLAGS: none
REPORT

malformed_probe() {
  local label="$1" fixture="$2" out err code
  out="$(mktemp)" err="$(mktemp)"
  "$TRIAGE" <"$fixture" >"$out" 2>"$err" && code=0 || code=$?
  [[ "$code" == 2 ]] ||
    problems+=("$label: want exit 2 — no answer could be obtained — got $code")
  [[ ! -s "$out" ]] ||
    problems+=("$label: want nothing on stdout, got: $(printf '%q' "$(cat "$out")")")
  [[ -s "$err" ]] ||
    problems+=("$label: want a diagnostic on stderr, got nothing")
  rm -f "$out" "$err"
}

malformed_probe "a candidate line with no class" "$no_class"
malformed_probe "a candidate line with an unknown class" "$unknown_class"
malformed_probe "a report with no CANDIDATES: line" "$no_candidates"

rm -f "$no_class" "$unknown_class" "$no_candidates"
report "$name"

ROOT="$(cd "$HERE/../../../.." && pwd)"
skill_md="skills/tdd/SKILL.md"
skill_path="$ROOT/$skill_md"

plain() {
  tr -d '*`' | tr '[:upper:]' '[:lower:]'
}

refactor_loop() {
  awk -v h='#### Refactor loop' \
    'index($0, h) == 1 { inside = 1; next } inside && /^#/ { exit } inside' "$skill_path" | plain
}

loop_lines="$(refactor_loop)"

line_of() {
  head -1 < <(grep -nE "$1" <<<"$loop_lines") | cut -d: -f1
}

name="$skill_md's refactor loop calls refactor-triage.sh on each committed transform and stops on exit 3 and exit 2"
problems=()

if [[ -z "${loop_lines// /}" ]]; then
  problems+=("$skill_md has no '#### Refactor loop' section to read — where the conductor calls refactor-triage.sh could not be established")
else
  triage_at="$(line_of 'refactor-triage\.sh')"
  commit_at="$(line_of 'git commit -m "refactor:')"

  if [[ -z "$triage_at" ]]; then
    problems+=("$skill_md's refactor loop never names refactor-triage.sh, so nothing asks whether another leaf is worth launching and the budget stays the only thing that ends the loop")
  elif [[ -z "$commit_at" ]]; then
    problems+=("$skill_md's refactor loop no longer commits the transform, so whether refactor-triage.sh is called on a committed one could not be established")
  elif [[ "$triage_at" -lt "$commit_at" ]]; then
    problems+=("$skill_md's refactor loop calls refactor-triage.sh (line $triage_at of the section) before it commits the transform (line $commit_at), so the report is triaged against a transform that is not in the history yet")
  fi

  # The call and the 250 characters after it, one window per mention: the text a reader meets
  # while working out what to do with each answer. Newlines go first so a sentence that wraps
  # is still one window. 250 rather than a rounder, larger number because BSD grep — the one
  # on the development machine this repository holds itself portable to — refuses an interval
  # whose bound is over 255.
  windows="$(tr '\n' ' ' <<<"$loop_lines" | grep -oE 'refactor-triage\.sh.{0,250}')"

  # Either order for each pair — the document may reach the code before the consequence or the
  # other way round — but both words within one window, which is what ties the branch to this
  # script rather than to the budget's.
  grep -qE '(exits? 3.{0,120}stop|stop.{0,120}exits? 3)' <<<"$windows" ||
    problems+=("$skill_md's refactor loop never says refactor-triage.sh's exit 3 stops it, so the third stop condition is documented nowhere the conductor reads")
  grep -qE '(exits? 2.{0,160}narrat|narrat.{0,160}exits? 2)' <<<"$windows" ||
    problems+=("$skill_md's refactor loop never says a malformed report — refactor-triage.sh's exit 2 — is narrated, so the conductor is left to bail on one instead of finishing the step it has already committed")
fi

report "$name"

# 5. what the conductor writes down when the loop ends. Case 4 asks where the script is
#    called and which branch each answer takes; this one asks what survives the run. The
#    `### 🛠️ Refactor` comment is the only place a human reads why a step's tidying stopped,
#    and since #149 there are three ways it can stop rather than two — so a comment that
#    still offers only "ran dry" and "budget spent" narrates a triage-ended loop as one of
#    the other two, and the measurement the issue exists to produce (how often the new
#    condition fires) cannot be read back off the thread. The same comment is where the
#    leftovers are filed, and a structural leftover is work a follow-up owes while a cosmetic
#    one is not: run together in one list, neither is worth anything to whoever reads it.
#
#    Two claims, one criterion — the comment names which of the three ended the loop, and it
#    keeps the two classes of leftover apart — so one case, with `problems` saying which the
#    document dropped. Each probe accepts any wording that carries its fact.
#
#    The probes read the narration sub-step alone rather than the section at large, for case
#    4's reason turned the other way: sub-step 1 lists the loop's own three stop conditions
#    and names `nothing left to tidy` and the budget while doing it, so a probe over the
#    whole section would be answered there and pass a document whose `### 🛠️ Refactor`
#    comment mentions neither.
name="$skill_md's ### 🛠️ Refactor comment names which of the three stop conditions ended the loop and files the leftovers by class"
problems=()

# The narration sub-step as one line: from the section's first line that names a `###`
narration="$(awk '!inside && /###/ && /refactor/ { inside = 1 }
                  inside && /^ *- pass:/ { exit }
                  inside' <<<"$loop_lines" | tr '\n' ' ')"

if [[ -z "${narration// /}" ]]; then
  problems+=("$skill_md's refactor loop names no ### comment to post, so what the ### 🛠️ Refactor comment must say could not be established")
else
  grep -qF 'nothing left to tidy' <<<"$narration" ||
    problems+=("$skill_md never tells the ### 🛠️ Refactor comment to say the loop ran dry — 'nothing left to tidy', the first of the three stop conditions")
  grep -qF 'budget' <<<"$narration" ||
    problems+=("$skill_md never tells the ### 🛠️ Refactor comment to name the budget — the second of the three stop conditions")
  grep -qE '(no|nothing|none)[ a-z]{0,14}structural|only cosmetic|refactor-triage' <<<"$narration" ||
    problems+=("$skill_md never tells the ### 🛠️ Refactor comment to name the third stop condition — that no structural candidate was left — so a loop the triage ended is narrated as one of the other two")
  grep -qF 'cosmetic' <<<"$narration" ||
    problems+=("$skill_md's ### 🛠️ Refactor comment never mentions cosmetic leftovers, so the two classes of candidate go into one undifferentiated backlog")
  grep -qE 'separat|apart|split|by class|per class|each class|own list|own line|own heading|own group' <<<"$narration" ||
    problems+=("$skill_md never tells the ### 🛠️ Refactor comment to keep the structural leftovers apart from the cosmetic ones — a mixed list is a backlog nobody can size")
fi

report "$name"

name="a report carrying NEW_STEP: lines exits with the same code as the same report without them"
problems=()

same_code_probe() {
  local label="$1" fixture="$2" with_steps plain_code steps_code
  "$TRIAGE" <"$fixture" >/dev/null 2>&1 && plain_code=0 || plain_code=$?

  with_steps="$(mktemp)"
  cat "$fixture" > "$with_steps"
  cat >> "$with_steps" <<'STEPS'
NEW_STEP: the parser accepts a second header field
NEW_STEP: the parser rejects a header field it has no name for
STEPS

  "$TRIAGE" <"$with_steps" >/dev/null 2>&1 && steps_code=0 || steps_code=$?
  [[ "$steps_code" == "$plain_code" ]] ||
    problems+=("$label: the report without NEW_STEP: lines exits $plain_code, the same report with them exits $steps_code")
  rm -f "$with_steps"
}

structural_report="$(mktemp)"
cat > "$structural_report" <<'REPORT'
RESULT: applied "inline the single-use $phase_label variable", suite green
CANDIDATES: structural | fold the two mktemp calls into one helper
REPORT

none_report="$(mktemp)"
cat > "$none_report" <<'REPORT'
RESULT: applied "inline the single-use $phase_label variable", suite green
CANDIDATES: none
REPORT

malformed_report="$(mktemp)"
cat > "$malformed_report" <<'REPORT'
RESULT: applied "inline the single-use $phase_label variable", suite green
REPORT

same_code_probe "a report listing a structural candidate" "$structural_report"
same_code_probe "a report whose candidates are CANDIDATES: none" "$none_report"
same_code_probe "a report with no CANDIDATES: line" "$malformed_report"

rm -f "$structural_report" "$none_report" "$malformed_report"
report "$name"

finish
