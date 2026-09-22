#!/usr/bin/env bash
# Unit test for CLAUDE.md as a record of its own rules — every rule the document carried is
# still findable in it after prose is moved out. Like claude-md-counts.test.sh,
# lane-rule-recorded.test.sh and model-knobs-recorded.test.sh this suite belongs to no
# single script: its subject is the document an agent reads before it opens a file.
# Zero-dependency plain-shell asserts, same idiom as model-knobs-recorded.test.sh.
#
# Why this exists (issue #202): CLAUDE.md is re-sent and re-billed on every request of every
# session in this repository, leaves included — 3,607 tokens × 1,285 requests on the night of
# 2026-09-14, priced in ADR-0018. The saving is in moving the reasoning out: a case history a
# leaf cannot act on belongs in its issue, a decision a human needs belongs in an ADR, and
# what stays behind is the rule and a pointer. The hazard of that edit is not that it removes
# too little — it is that a rule leaves with the paragraph that explained it, and nothing
# fires, because the only thing that was holding that rule to this repository was the
# sentence being here. A trim that drops a rule reads exactly like a trim that tightened it.
#
# Contract under test:
#   Every rule in the roster below is carried by SOME ONE record of CLAUDE.md — one
#   paragraph, one bullet or one table row. A rule stated in full and a rule stated in one
#   sentence with a pointer to the ADR or the issue now holding its reasoning both satisfy
#   that; a rule that left with its paragraph does not.
#
# Asked of a record and never of the whole document, because a document-wide match would
# answer "yes, those words are in here" for two surviving fragments sections apart that
# never state the rule together — which is the exact wreckage a trim leaves and the only
# thing this suite is here to see.
#
# The roster is the rules this document is the only record of. Four rules are deliberately
# not in it, each because another suite already holds the document to it and a second copy
# here would drift: the counts (claude-md-counts.test.sh), the two-lane rule
# (lane-rule-recorded.test.sh), the count-line rule (count-line-guard.test.sh) and the
# per-role model knobs (model-knobs-recorded.test.sh).
#
# Each rule is asked as the regexes any wording carrying it would match — the identifiers a
# reader would have to act on, never a fixed sentence — because the trim's whole purpose is
# to reword, and a suite that pinned today's phrasing would fail the edit it exists to
# protect. The protocol lane-rule-recorded.test.sh and model-knobs-recorded.test.sh both use
# on this same document.
#
# No line of code below names a path in the generated tree: the rules that are about the
# page are asked by the names that are not paths — walkthrough.html, docs-fresh, docs-check
# — which is the rule no-docs-reads.test.sh enforces on this directory.
#
# Run: skills/tdd/scripts/tests/claude-md-rules-recorded.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
# The suite sits at skills/<skill>/scripts/tests, so four levels up is the repo root.
ROOT="$(cd "$HERE/../../../.." && pwd)"

# The document twice — the path as every failure message spells it, and the same path
# resolved for the probe to read — so a message can never name a file the probe did not
# open. The pairing claude-md-counts.test.sh and model-knobs-recorded.test.sh both use.
claude_md="CLAUDE.md"
claude_path="$ROOT/$claude_md"

pass=0 fail=0

# run_case <name> <probe> — one case: empty the `problems` array, run <probe> to collect into
# it, then close the case. An empty array is a pass, otherwise one FAIL line for the case and
# one indented line per problem, so the output says which rule is no longer recorded rather
# than just that one is not. Written once so a case is added as its name and its probe, never
# as another copy of the reset-run-and-report around them.
run_case() {
  local name="$1" probe="$2"
  problems=()
  "$probe"
  if [[ "${#problems[@]}" -eq 0 ]]; then
    pass=$((pass + 1))
  else
    fail=$((fail + 1))
    echo "FAIL - $name"
    printf '    %s\n' "${problems[@]}"
  fi
}

# plain — stdin with emphasis marks and backticks dropped and the case folded, so a regex
# below is written one way and still matches prose that marked the same words up as
# `make docs` or **never merged**. The normalisation lane-rule-recorded.test.sh and
# model-knobs-recorded.test.sh both use on this document.
plain() { tr -d '*`' | tr '[:upper:]' '[:lower:]'; }

# The awk program `records` and `section_records` both split their input with, named once
# because the two read the same document and a copy that drifted would leave one of them
# answering a different question about it. A program rather than a function because awk is
# what does the splitting, and the only difference between the two readers is what they hand
# it: the whole file, or one section of it.
RECORD_SPLIT='/^([-*] |\| )/ { if (rec != "") print rec; rec = $0; next }
              /^[[:space:]]*$/ { if (rec != "") print rec; rec = ""; next }
              rec == "" { rec = $0; next }
              { rec = rec " " $0 }
              END { if (rec != "") print rec }'

# records — the document as one line per record, normalised through `plain`. A record runs
# from a `- `, a `* ` or a `| ` in column one, or from the first line after a blank, up to
# the next such line or the next blank. Table rows start one of their own because half this
# document's rules are a row of the commands table, and a table read as a single record
# would let a rule be answered by the row below it. CLAUDE.md wraps mid-sentence, so joining
# a record onto one line is also what keeps a claim split over a line break readable as one
# sentence. Same shape as model-knobs-recorded.test.sh's `records`.
records() {
  awk "$RECORD_SPLIT" "$claude_path" | plain
}

# section_records <heading> — the records of ONE section of the document: from the heading to
# the next `## `, split and normalised exactly as `records` splits the whole file. Read by
# heading where a rule belongs to a section rather than to the document, which is the reading
# lane-rule-recorded.test.sh uses on this same file: a sentence three sections away answers
# for prose the agent reading that section does not have in front of it.
section_records() {
  awk -v heading="$1" '$0 == heading { f = 1; next } f && /^## / { exit } f' "$claude_path" |
    awk "$RECORD_SPLIT" | plain
}

# The document as records, read once: the four cases below all ask their question of the same
# text, and `records` is an awk pass over the file, so asking it once and passing the answer
# around costs one process instead of four. Read at load, before any case runs.
ALL_RECORDS="$(records)"

# one_record_matches <text> <regex>... — exit 0 when one line of <text> (a record, as
# `records` prints them) matches every regex, 1 otherwise. Asked of one record at a time for
# the reason the header gives: fragments of a rule sections apart must not answer for it.
one_record_matches() {
  local text="$1" line re
  shift
  while IFS= read -r line; do
    for re in "$@"; do
      [[ "$line" =~ $re ]] || continue 2
    done
    return 0
  done <<< "$text"
  return 1
}

# records_carry <text> <problem> <regex>... — the shape every invariant case below shares:
# pass when one record of <text> matches all of <regex>, and collect <problem> when none does.
# Written once so an invariant is added as the regexes that carry it and the message naming
# what left, never as another copy of the guard-and-append around them. <text> is a parameter
# because a rule is asked either of the whole document or of one section of it, and those two
# readings differ in nothing but which records they read.
records_carry() {
  local text="$1" problem="$2"
  shift 2
  one_record_matches "$text" "$@" && return
  problems+=("$problem")
}

# record_carries <problem> <regex>... — `records_carry` over the whole document, which is how
# every rule that belongs to no one section is asked.
record_carries() {
  records_carry "$ALL_RECORDS" "$@"
}

# The roster: one rule per line, `;`-separated — the rule as a failure message names it,
# then every regex a record carrying it has to match. A semicolon rather than a pipe because
# the regexes alternate. Read from a heredoc rather than written as a function call each, so
# the rules read as the list of claims they are and a rule is added as a line.
#
# No apostrophe appears in a roster line: bash 3.2 parses a `$(…)` by scanning for the
# closing paren and reads a lone quote inside the heredoc as one that was opened, which is a
# syntax error at the end of the file rather than at the line that caused it.
#
# Two or three regexes per rule, and they are the parts a reader could not act without: the
# identifier (`supervise.sh`, `GIT_COMMITTER_DATE`, `--sort=-v:refname`) and the verb that
# makes it a rule rather than a mention (`never`, `refuse`, `not tested`). A rule cut down to
# one sentence and a pointer still carries both; a rule that left does not.
ROSTER=$(cat <<'ROWS'
make test is the baseline, and a red one stops a run before it starts;make test;baseline|stay green;refuse|refus
make docs publishes the page by hand only, never on a merge;make docs;by hand|disabled;publish|deploy
make install-hooks installs the tag hook once per clone and refuses to clobber a foreign one;install-hooks;reference-transaction;refus|clobber
make merge-gates runs before a merge and which gates a change owes, including what is exempt;merge-gates;before merging|merging any pr;nothing for;skills/;adr;makefile
docs-check is not part of make test, nor in CI, so documentation lag never blocks a run;docs-check;not.*part of;block|never
CONTEXT.md is where the glossary lives;context.md;glossar|terms
walkthrough.html is generated and never hand-edited;walkthrough;generat;never edit|by hand
the page build fails on a bad reference but only reports a line no commentary claims;fail;chunk|commentary;owed
exit code 1 is a clean negative — a real answer;clean negative|1 ;reject|leaf ran and failed
exit code 2 is no answer obtained;no answer;killed-stuck|unparseable|bad argument
exit code 3 is nothing to do, and not an error;nothing to do;not an error
1 and 2 are never collapsed — a process failure is not a system failure;never collapse|not collapse;process;system
a version is an annotated tag whose message is the capability, and nothing else keeps it;annotated;capability;changelog|version file
git tag is sorted with -v:refname, never plain sort;sort=-v:refname;lexical|v0.9
a backfilled tag needs GIT_COMMITTER_DATE;git_committer_date;backfill|retro
a regen commit built at the tag is not the fixpoint — build, commit, rebuild, amend;amend;unreleased;docs-check|fixpoint
every leaf is launched through supervise.sh and nothing bypasses it;supervise.sh;never|only|bypass
the verifier is blind by construction — the prompt builder takes no rationale;blind;build-verify-prompt.sh;rationale|leak
the committed ledger is the source of truth, and the refactor-pending mark is what a resumed run reads;ledger;source of truth;refactor pending
the three budgets are three axes and are never merged;veri_stuck_retries;revise_budget;veri_refactor_budget;never merged|one knob
the git questions a walkthrough build asks are a pinned budget;once per script;budget|pins;git
a tag changes the page without a commit, and the hook only notices;tag;hook;notice|never rebuild
a test injects rather than waiting on a real model or a real clock, which is why every tunable has a default;claude_bin;veri_heartbeat;:-default
a guard never watched to fail is not tested;guard|failure path;not tested|watched;break
ROWS
)

# probe_every_rule_is_carried_by_one_record — the roster against the document. The records
# are read once and every rule asked of them, so a document that could not be read at all
# reports every rule missing from the same empty text; that is fail-closed by construction,
# since there is no way to read CLAUDE.md as blank and have a rule answer.
probe_every_rule_is_carried_by_one_record() {
  local row rule

  if [[ -z "${ALL_RECORDS// /}" ]]; then
    problems+=("$claude_md could not be read, so no rule could be looked for in it")
    return
  fi

  while IFS= read -r row; do
    [[ -n "$row" ]] || continue
    IFS=';' read -r -a fields <<< "$row"
    rule="${fields[0]}"
    record_carries "$claude_md has no single record stating that $rule" "${fields[@]:1}"
  done <<< "$ROSTER"
}

# 1. One criterion, one case: every rule the document carried is still discoverable from it.
#    One case rather than one per rule, because what the next agent needs is not a count of
#    surviving sentences but a document that still holds every rule it is the record of — and
#    the problem lines say which rule left with its paragraph.
run_case "$claude_md still states every rule it is the only record of, in full or in one sentence with a pointer" \
  probe_every_rule_is_carried_by_one_record

# probe_budgets_invariant_names_the_fourth_axis — issue #219 gave the verifier a relaunch
# budget of its own, `VERI_NO_VERDICT_RETRIES`, for a leaf that exited cleanly without a
# `VERDICT:` line. It is not `VERI_STUCK_RETRIES`: that one answers liveness (the process
# never finished), this one protocol compliance (the process finished and ignored the output
# contract). The budgets invariant is where the document says why budgets are never merged,
# so a fourth axis it does not name is one the next reader is free to fold into the stuck
# retries. Asked of ONE record, like the roster above: the new variable, the one it must not
# be merged with, that there are now four, the two failures each answers, and the verb that
# keeps them apart.
probe_budgets_invariant_names_the_fourth_axis() {
  record_carries \
    "$claude_md has no single record naming VERI_NO_VERDICT_RETRIES as a fourth budget axis beside VERI_STUCK_RETRIES, liveness against protocol compliance, never merged" \
    'veri_no_verdict_retries' 'veri_stuck_retries' 'four' \
    'liveness' 'protocol|contract|compliance' 'never merged|not merged|one knob'
}

# 2. One criterion, one case: the budgets invariant names VERI_NO_VERDICT_RETRIES as a fourth
#    axis and why it is not merged with VERI_STUCK_RETRIES (#219).
run_case "$claude_md's budgets invariant names VERI_NO_VERDICT_RETRIES as a fourth axis and why it is not merged with VERI_STUCK_RETRIES" \
  probe_budgets_invariant_names_the_fourth_axis

# probe_blind_invariant_names_the_base_sha — issue #151 gave the refactor verifier a 4th
# positional, `<base-sha>`, the step's green commit, so it can review what the refactor
# changed. The blind-verifier invariant is where the document says no parameter can carry the
# developer's rationale, so a new parameter it does not name — and does not say why it cannot
# leak — reads as the silent end of the guarantee that invariant warns about. Asked of ONE
# record, like the roster above: the invariant, the builder, the parameter, the phase it
# belongs to, what shape confines it (hex), and that it cannot carry rationale.
probe_blind_invariant_names_the_base_sha() {
  record_carries \
    "$claude_md has no single record naming <base-sha> as the refactor phase parameter of build-verify-prompt.sh in the blind-verifier invariant, and why a hex sha cannot leak rationale" \
    'blind' 'build-verify-prompt\.sh' 'base.sha' 'refactor' \
    'hex|0-9a-f' 'rationale|leak'
}

# 3. One criterion, one case: the blind-verifier invariant names the base-sha parameter and
#    why a sha cannot leak rationale (#151).
run_case "$claude_md's blind-verifier invariant names the refactor base-sha parameter and why a sha cannot leak rationale" \
  probe_blind_invariant_names_the_base_sha

# probe_budgets_invariant_names_the_fifth_axis — issue #360 gave the plan itself a budget,
# `VERI_STEP_GROWTH`: how many steps one ledger may hold marked `⟦added⟧`, so a run that
# discovers work as it goes can grow its plan without growing it without end. It is a fifth
# axis, not a bigger refactor budget: `VERI_REFACTOR_BUDGET` bounds what one step's tidying
# costs, this one bounds how much plan a run may add. Folded into any of the other four, "let
# the run plan more" and "let a leaf retry / revise / refactor more" would be one decision,
# which is the same collapse this invariant already refuses three times over. Asked of ONE
# record, like the roster above: the new variable, one of the four it must not be merged
# with, that there are now five, the axis it answers, and the verb that keeps them apart.
probe_budgets_invariant_names_the_fifth_axis() {
  record_carries \
    "$claude_md has no single record naming VERI_STEP_GROWTH as a fifth budget axis beside the other four, plan growth, never merged" \
    'veri_step_growth' 'veri_refactor_budget' 'five' \
    'plan' 'never merged|not merged|one knob'
}

# 4. One criterion, one case: the budgets invariant names VERI_STEP_GROWTH as a fifth axis,
#    plan growth, never merged with the other four (#360).
run_case "$claude_md's budgets invariant names VERI_STEP_GROWTH as a fifth axis, plan growth, never merged with the other four" \
  probe_budgets_invariant_names_the_fifth_axis

# The section a suite in this directory is written under, exactly as the document spells it:
# the rule below belongs to it and not to the document at large, because the reader it is
# written for is an author part-way through a new suite, and that author is reading this
# section.
IDIOM_HEADING="## Testing idiom"

# probe_idiom_records_the_sigpipe_rule — issue #422: a suite that declares `set -uo pipefail`
# and ends a pipeline in a reader that leaves before EOF — a `grep` whose options carry `q`,
# or a `head` — asserts on its own writer's SIGPIPE rather than on the reader's answer. The
# writer dies of 141 on the closed pipe, `pipefail` hands that up as the pipeline's status,
# and the assertion is inverted. It is green on the development Mac and red on CI, so the
# leaf and the blind verifier both say green and the PR is red; it cost two consecutive runs
# (#418, #416). `no-sigpipe-pipelines.test.sh` fails the run when a suite is written that
# way, but a guard is read after the fact — the author who reads this section first is the
# one who never writes the shape. Asked of ONE record of the *Testing idiom* section, like
# the roster above: the option that makes it a bug, both readers, the signal, the guard by
# name, the repair, and the verb that makes it a rule rather than a note.
probe_idiom_records_the_sigpipe_rule() {
  local idiom_records
  idiom_records="$(section_records "$IDIOM_HEADING")"

  # Fail closed: an empty section matches no regex, and saying so names the repair — the
  # heading moved — rather than reporting a rule missing from prose nobody could read.
  if [[ -z "${idiom_records// /}" ]]; then
    problems+=("$claude_md has no '$IDIOM_HEADING' section to read, so nothing states the pipefail/SIGPIPE rule where the agent writing a suite would find it")
    return
  fi

  records_carry "$idiom_records" \
    "$claude_md has no single record in its '$IDIOM_HEADING' section stating that a suite declaring pipefail never ends a pipeline in grep -q or head, that the status asserted on is then the writer's SIGPIPE, which case says so (no-sigpipe-pipelines), and what the repair is" \
    'pipefail' \
    'grep -[a-z]*q' \
    '[^a-z]head' \
    'sigpipe' \
    'no-sigpipe-pipelines' \
    '/dev/null|redirect|to eof' \
    'never|must not|does not|no suite'
}

# 5. One criterion, one case: the section an author writing a suite reads states the
#    pipefail/SIGPIPE rule, in one record rather than in fragments a reader has to assemble
#    (#422).
run_case "$claude_md's testing idiom section states the pipefail/SIGPIPE rule" \
  probe_idiom_records_the_sigpipe_rule

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
