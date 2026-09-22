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
pass=0 fail=0

# report <name> — close a case whose probes collected into the `problems` array: an empty
# array is a pass, otherwise one FAIL line for the case and one indented line per problem,
# so the output says which probe broke rather than just that the case did. Same helper
# refactor-budget.test.sh uses.
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

# 1. the loop continues while structural work is left. A report whose CANDIDATES: lines
#    list two structural transforms and one cosmetic one is the "keep going" answer: exit
#    0, and the structural candidates on stdout so the conductor can mirror them into its
#    `### 🛠️ Refactor` comment.
#
#    What the case pins is that each structural candidate is named on a line of its own
#    and that the cosmetic one is not there — not the exact prefix each line carries,
#    which is the script's business, not the loop's. The line count is what says the
#    surrounding RESULT:/FLAGS: lines were read and not echoed.
#
#    The fixture is a whole report rather than three bare candidate lines because that is
#    what the conductor pipes in: the leaf's last lines, verbatim (develop-refactor.md,
#    *Report*). Quoted heredoc, so `$tmp` inside the third candidate stays the two
#    characters a leaf would have written and is not expanded here.
name="a report listing structural candidates exits 0 and prints them"
problems=()

leaf_report="$(mktemp)"
# The heredoc writes to a file rather than into `report="$(cat <<'REPORT' … )"`: bash 3.2
# — the level this repository holds itself to — scans a command substitution for its
# closing paren without knowing a heredoc is inside it, so the apostrophe in `verify.sh's`
# below reads as an unterminated quote and the whole suite fails to parse.
cat > "$leaf_report" <<'REPORT'
RESULT: applied "fold verify.sh's two prompt paths into one", suite green
FLAGS: none
CANDIDATES: structural | fold verify.sh's two mktemp calls into one helper
CANDIDATES: cosmetic | reflow the header comment to ninety columns
CANDIDATES: structural | rename $tmp to $prompt_file, which is what it holds
REPORT

# Keep the two streams apart: stdout goes to a file the case reads back, and the diagnostic
# stream is discarded, so a diagnostic cannot arrive mixed into stdout and count as a
# candidate. Discarded rather than captured because no probe here reads it — the cases that
# assert on a diagnostic are the exit-2 ones, and they capture it themselves.
out="$(mktemp)"
"$TRIAGE" <"$leaf_report" >"$out" 2>/dev/null && code=0 || code=$?

[[ "$code" == 0 ]] ||
  problems+=("want exit 0 while structural candidates remain, got $code")

lines="$(grep -c '' "$out")"
[[ "$lines" == 2 ]] ||
  problems+=("want the 2 structural candidates on stdout, one per line, got $lines line(s): $(printf '%q' "$(cat "$out")")")

# -F so the transform text is matched as the literal a leaf wrote, not as a pattern: `$`
# and `'` are ordinary characters in a candidate.
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

# 2. the loop's third stop condition. A report with no structural candidate left is the
#    "stop" answer: exit 3, "nothing to do" in the four-code convention — a real answer,
#    not a failure, so the conductor ends the refactor loop and goes to verify-refactor
#    rather than bailing. The two ways a leaf says it are one criterion, so they are one
#    case: a report whose CANDIDATES: lines are all cosmetic — the point of #149, since
#    those are exactly the transforms the budget used to be spent on — and a report whose
#    single line is `CANDIDATES: none`, which is what develop-refactor.md's *Report*
#    asks for when the leaf sees nothing left at all. `problems` says which fixture broke.
#
#    Whole reports again rather than bare candidate lines, for case 1's reason: the
#    conductor pipes in the leaf's last lines verbatim. Each is written to a file rather
#    than through a command substitution, also for case 1's reason — bash 3.2 mis-scans an
#    apostrophe inside a heredoc nested in `$( … )`.
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

# stops_probe <label> <fixture> — run the script on one report and collect its problem.
# A function rather than a `for` over packed strings: a label like `CANDIDATES: none`
# carries the punctuation any obvious separator would use.
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

# 3. a report the script cannot read is a system failure, not a decision: exit 2, "no answer
#    could be obtained" in the four-code convention, a diagnostic on stderr and nothing at
#    all on stdout. The stdout half is the load-bearing one — the conductor mirrors that
#    stream into its `### 🛠️ Refactor` comment as the structural leftovers, so a malformed
#    report that printed even one line would seed the comment with a candidate nothing
#    classed. And exit 2 rather than 3 is what keeps a leaf that forgot its classes from
#    reading as "nothing worth doing": 3 would end the loop quietly, 2 makes the conductor
#    narrate the malformed report before it goes to verify-refactor.
#
#    Three ways to hand the script an unreadable report, one criterion, so they are one
#    case — a candidate line with no class, one with a class the two-class vocabulary does
#    not have, and a report carrying no `CANDIDATES:` line at all, which is a leaf that
#    dropped the section develop-refactor.md's *Report* asks for. `problems` says which
#    fixture broke.
#
#    Whole reports again, written to files rather than through command substitution, both
#    for case 1's reasons.
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

# malformed_probe <label> <fixture> — run the script on one unreadable report and collect
# its problems. The two streams go to their own files: the case is about which stream
# carries what, so merging them would hide a diagnostic printed onto stdout.
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

# 4. the loop that calls it. Cases 1–3 ask the script what it answers; this one asks whether
#    anything is listening. The conductor is prose, so the whole of this script's place in the
#    run lives in SKILL.md's *Refactor loop* section: where the call goes, and which branch
#    each of the three answers takes. Get that wrong and the script still passes cases 1–3
#    while the loop keeps ending only when the budget runs out, which is the thing #149 is
#    about.
#
#    It lives in this suite rather than in one of the `skill-*` ones for refactor-budget.test.sh
#    case 8's reason: the sentences under test are statements *about this script*, and a
#    reader repairing them comes here to find out what it actually answers.
#
#    Three claims, one criterion — the loop runs it on each transform's settled result and
#    branches on both non-zero answers — and so one case, with `problems` saying which claim
#    the document dropped:
#      - the call is made AFTER the transform is committed, not before: the report being
#        triaged is the one belonging to a transform that is already in the history, which is
#        what makes a malformed report survivable rather than a bail.
#      - exit 3 stops the loop — the third stop condition.
#      - exit 2 stops it too, and is narrated rather than bailed on.
#
#    Each probe accepts any wording that carries its fact — how the document phrases it is the
#    writer's — but the two exit-code claims are asked of the text *around the call itself*,
#    not of the section at large: this section already talks about stop conditions and about
#    an exit 3, for `refactor-budget.sh` on the loop's other axis, and a probe that read the
#    whole section would be answered by those sentences and pass a document that never says
#    what THIS script's answers mean.
ROOT="$(cd "$HERE/../../../.." && pwd)"
# The document twice: the path as every problem message spells it, and the same path resolved
# for the reader to open, so a message can never name a file the probes did not read.
skill_md="skills/tdd/SKILL.md"
skill_path="$ROOT/$skill_md"

# plain — stdin with emphasis marks and backticks dropped and the case folded, because
# `exits **3**` and "exits 3" are the same sentence. Borrowed from skill-suite-runs.test.sh,
# which reads this same section for what its leaf runs.
plain() {
  tr -d '*`' | tr '[:upper:]' '[:lower:]'
}

# refactor_loop — the lines of the *Refactor loop* section, normalised through `plain`: the
# lines after the heading that starts with `#### Refactor loop`, up to the next heading of any
# level. Lines rather than one blob, because one probe below is about order — which of the
# call and the commit the document does first — and that question disappears once the section
# is joined onto a single line.
refactor_loop() {
  awk -v h='#### Refactor loop' \
    'index($0, h) == 1 { inside = 1; next } inside && /^#/ { exit } inside' "$skill_path" | plain
}

# The section, read once, next to the path it is read from: cases 4 and 5 both probe it and
# nothing between them writes to the document, so deriving it per case was the same awk over
# the same file twice. Shared like `skill_path` and the helpers above, rather than each case
# re-deriving it — `line_of` below already reads it as a global.
loop_lines="$(refactor_loop)"

# line_of <extended-regex> — the 1-based position of the first section line matching it, or
# the empty string when none does. Position is what turns two "is it there?" probes into the
# one question the ordering claim asks.
line_of() {
  head -1 < <(grep -nE "$1" <<<"$loop_lines") | cut -d: -f1
}

name="$skill_md's refactor loop calls refactor-triage.sh on each committed transform and stops on exit 3 and exit 2"
problems=()

if [[ -z "${loop_lines// /}" ]]; then
  # Fail closed: a renamed or emptied section is reported as unreadable rather than probed as
  # an empty string, which would let "the loop is gone" read as "the loop is right".
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
# comment — the `### 🛠️ Refactor` heading this case is about — up to the `- PASS:` bullet,
# where the branch on verify-refactor's verdict begins and the narration's own rules stop.
# Joined, because none of the probes below is about order. Opened on the `###` rather than on
# the sub-step's own word `narrate` because sub-step 1 says "stop and narrate" too, and a
# window opened there would take in that sub-step's list of stop conditions.
narration="$(awk '!inside && /###/ && /refactor/ { inside = 1 }
                  inside && /^ *- pass:/ { exit }
                  inside' <<<"$loop_lines" | tr '\n' ' ')"

if [[ -z "${narration// /}" ]]; then
  # Fail closed, as case 4 does: a narration sub-step that names no comment at all is
  # reported as unreadable rather than probed as an empty string.
  problems+=("$skill_md's refactor loop names no ### comment to post, so what the ### 🛠️ Refactor comment must say could not be established")
else
  grep -qF 'nothing left to tidy' <<<"$narration" ||
    problems+=("$skill_md never tells the ### 🛠️ Refactor comment to say the loop ran dry — 'nothing left to tidy', the first of the three stop conditions")
  grep -qF 'budget' <<<"$narration" ||
    problems+=("$skill_md never tells the ### 🛠️ Refactor comment to name the budget — the second of the three stop conditions")
  # Either face of the third condition is accepted — that no structural candidate was left,
  # or that only cosmetic ones were — as is naming the script that decided it.
  grep -qE '(no|nothing|none)[ a-z]{0,14}structural|only cosmetic|refactor-triage' <<<"$narration" ||
    problems+=("$skill_md never tells the ### 🛠️ Refactor comment to name the third stop condition — that no structural candidate was left — so a loop the triage ended is narrated as one of the other two")
  grep -qF 'cosmetic' <<<"$narration" ||
    problems+=("$skill_md's ### 🛠️ Refactor comment never mentions cosmetic leftovers, so the two classes of candidate go into one undifferentiated backlog")
  grep -qE 'separat|apart|split|by class|per class|each class|own list|own line|own heading|own group' <<<"$narration" ||
    problems+=("$skill_md never tells the ### 🛠️ Refactor comment to keep the structural leftovers apart from the cosmetic ones — a mixed list is a backlog nobody can size")
fi

report "$name"

# 6. the report shape #361 leaves behind. Since that issue a refactor leaf's report ends in
#    `NEW_STEP:` lines — the behaviour-level criteria a triangulating step would pin — in
#    place of the `FLAGS:` line it used to carry. This script reads the `CANDIDATES:` lines
#    and nothing else, so those added lines must leave its answer exactly where it was: the
#    conductor pipes in the leaf's last lines verbatim, and a report the new prompt produces
#    must triage as the same report written before it did.
#
#    One criterion — the answer is unchanged — so one case, over a report of each of the
#    three answers cases 1–3 pin, with `problems` saying which pair disagreed. What is
#    asserted is only that the two codes match: which code each report earns is cases 1–3's
#    question, and repeating it here would pin it twice.
name="a report carrying NEW_STEP: lines exits with the same code as the same report without them"
problems=()

# same_code_probe <label> <fixture> — run the script on one report, then on that same report
# with the leaf's `NEW_STEP:` lines appended where develop-refactor.md's *Report* puts them,
# and collect the problem if the two answers differ. The variant is built from the fixture
# itself rather than written out a second time, so the two reports cannot drift apart into
# two different questions.
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

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
