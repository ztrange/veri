#!/usr/bin/env bash
# Unit tests for what skills/tdd/SKILL.md tells the conductor to do at the draft PR step.
# Like skill-refactor-pending.test.sh and skill-commit.test.sh this suite belongs to no
# single script: its subject is the procedure document, read as text, the way the session
# that follows it reads it. Picked up by `make test`'s glob by existing.
# Zero-dependency plain-shell asserts, same idiom as skill-refactor-pending.test.sh.
#
# Why this exists (issue #191): the conductor now pushes the branch after every green
# commit and after every verify-refactor PASS, so by the time a run reaches step 4 the
# branch is already on the remote. The push that used to live in that step was the run's
# FIRST push, and binding durability to it is what kept hours of commits on one disk. The
# step's remaining job is the one it was always named for — ask a human to look — and that
# job is prose, so a document that still opens with `git push` is the whole of the
# regression: the conductor would be following an instruction whose premise no longer
# holds, and a reader would still be told the branch reaches the remote only here.
#
# The suite's subject is the whole of where this document pushes, not step 4 alone: the
# premise the Draft PR case rests on — that the branch is already on the remote — is a
# claim about the cycle loop, and a suite that pinned only the half that stopped pushing
# would go green on a document that had stopped pushing everywhere.
#
# Contract under test:
#   1. SKILL.md's `### 4. Draft PR` step opens the PR against the already-pushed branch: it
#      still runs `gh pr create`, and no instruction of that step pushes the branch first.
#   2. SKILL.md's Green PASS and verify-refactor PASS branches each run `push-branch.sh`,
#      so the branch reaches the remote at both of the points that write the ledger.
#   3. SKILL.md's Draft PR step and its Guardrails invariant about opening the PR both name
#      `detect-test-command.sh --tier all`'s command, run exactly once, as the only
#      full-suite gate left in the cycle (issue #341).
#   4. SKILL.md's Draft PR step answers a red result on that full run by adding a repair step
#      to the ledger rather than bailing; the same step says a unit-tier test is added when
#      the failure exposes a gap, and that the verifier judges the fix against the full
#      command (issue #341).
#   5. SKILL.md's Draft PR step bails on a second red result on the full run after a repair
#      step, naming every suite still red rather than only the first (issue #341).
#   6. SKILL.md's Draft PR step puts `refactor-owed.sh render`'s output in the PR body, from
#      the run's own owed file, and omits the section when that render exits 3 (issue #359).
#   7. SKILL.md's Draft PR step copies the ledger's `## Owed steps` bullets into the PR
#      body under a `## Owed steps` heading of its own (issue #360).
#
# Run: scripts/tests/skill-draft-pr.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
# The suite sits at skills/<skill>/scripts/tests, so four levels up is the repo root.
ROOT="$(cd "$HERE/../../../.." && pwd)"

# The document twice, the way skill-refactor-pending.test.sh names its two: the path as
# every problem message spells it, and the same path resolved for the reader below to open.
# One constant for each, so a message can never name a file the reader did not read.
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

# records_of — the lines on stdin as records: the document's numbered steps, bullets and
# paragraphs, one per line and lowercased. A record runs from a `N. ` or a `- ` (indented or
# not) in column one, or from the first line after a blank, up to the next such line or the
# next blank; a fenced command block inside a bullet is part of that bullet's record, which
# is what lets a probe ask whether the instruction that opens the PR is the one carrying the
# command. Runs of whitespace collapse to one space, so a wrapped sentence reads as one, and
# case is folded last because the sentences are the writer's.
records_of() {
  awk '
    function flush() { if (rec != "") { gsub(/[[:space:]]+/, " ", rec); print rec } rec = "" }
    /^[0-9]+\. / || /^[[:space:]]*- / { flush(); rec = $0; next }
    /^[[:space:]]*$/ { flush(); next }
    rec == "" { rec = $0; next }
    { rec = rec " " $0 }
    END { flush() }' | tr '[:upper:]' '[:lower:]'
}

# section_records <heading prefix> <closer regex> — the records of the section whose
# heading STARTS WITH <heading prefix>, where a line matching <closer regex> is what ends
# one. Every read here is scoped to a section, because the document pushes a branch and
# takes a PASS branch on several paths: an unscoped read would answer one criterion with
# another path's instruction, and fail a document that had done exactly what was asked.
# Which headings close a section is the caller's, since the levels differ by section. A
# prefix rather than the whole heading because a heading may carry trailing prose after an
# em dash; the prefix is what identifies it and is quotable in a problem message.
section_records() {
  awk -v h="$1" -v closers="$2" \
    '$0 ~ closers { inside = (index($0, h) == 1); next } inside' "$skill_path" | records_of
}

# draft_pr_instructions — the records of the `### 4. Draft PR` step, which a heading of
# either level ends.
draft_pr_instructions() {
  section_records '### 4. Draft PR' '^## |^### '
}

# first_record <text> [<grep-options> <pattern>]... — the first record of <text> that
# matches every option-and-pattern pair given, or nothing when none does. Six cases ask the
# document this same question and differ only in the filters and in the complaint they then
# file, so the reading is written here once. The filters run over a variable rather than as a
# pipeline into `head`, which is what keeps a filter's own SIGPIPE — `head` leaving as soon as
# it has its line, under this suite's `pipefail` — from ever being the answer (issue #422).
first_record() {
  local text="$1"
  shift
  while [[ "$#" -gt 0 ]]; do
    text="$(grep "$1" -- "$2" <<< "$text")"
    shift 2
  done
  head -1 <<< "$text"
}

# draft_pr_or_problem <what> — read the `### 4. Draft PR` step into `records`, or record the
# one problem that says the case could not be read at all, naming <what> it could therefore
# not check. Non-zero when the section is gone, so each case below is its probes alone rather
# than its probes and its own missing-section branch: every case here asks the document for
# the same slice first, and would otherwise spell the same fetch and the same fail-closed
# message six times over.
draft_pr_or_problem() {
  records="$(draft_pr_instructions)"
  [[ -n "$records" ]] && return 0
  problems+=("$skill_md has no ### 4. Draft PR section to read — $1 could not be checked")
  return 1
}

# 1. The criterion, as one case: the step opens the PR for a branch that is already on the
#    remote. Both halves are asked of the same slice, and the opening half is asked first so
#    the case fails closed — a section emptied or renamed must not read as "it no longer
#    pushes". `git push` rather than the word "push": the step's first sub-step still refuses
#    to go on while there is nothing *fit* to push, and that refusal is #116's gate, not a
#    push. What this criterion is about is whether the step issues the command.
name="$skill_md's Draft PR step opens the PR against the already-pushed branch, with no push of its own"
problems=()

if draft_pr_or_problem "whether the step still pushes"; then
  grep -qF 'gh pr create' <<< "$records" ||
    problems+=("$skill_md's Draft PR step never runs gh pr create, so there is no PR being opened against the pushed branch at all")
  pushes="$(first_record "$records" -F 'git push')"
  [[ -z "$pushes" ]] ||
    problems+=("$skill_md's Draft PR step still pushes the branch itself, so the procedure reads as though the branch reaches the remote only once the run is review-ready: $(printf '%.120s' "$pushes")")
fi
report "$name"

# pass_record <heading prefix> — the record of the PASS branch inside the `####` section
# whose heading starts with <heading prefix>, or nothing when there is no such section or
# no such branch in it. Any heading ends one of these, the document's innermost level.
pass_record() {
  first_record "$(section_records "$1" '^#')" -E '^ *- \*\*pass'
}

# 2. The criterion, as one case: the branch reaches the remote at both of the points that
#    already write the ledger. Those two points are branches of the procedure, not sections
#    of it — Green's PASS, which ticks the step and commits, and verify-refactor's PASS,
#    which clears the mark and commits — so what is pinned is that each of those two
#    records carries the call. A push written elsewhere in either section would leave the
#    REJECT and bail paths pushing commits the PASS path does not.
#
#    `push-branch.sh` by name: the script is where the not-a-bail rule lives, so an
#    instruction that pushed with a bare `git push` instead would make a transport failure
#    stop a run the methodology said was fine. The two sections are probed in one loop and
#    each contributes its own problem line, so the output says which of the two is missing.
name="$skill_md's Green PASS and verify-refactor PASS both push the branch, at the two points that write the ledger"
problems=()

for heading in '#### Green' '#### Refactor loop'; do
  record="$(pass_record "$heading")"
  if [[ -z "$record" ]]; then
    problems+=("$skill_md has no PASS branch under '$heading' to read — whether the branch is pushed where the ledger is written could not be checked")
  else
    grep -qF 'push-branch.sh' <<< "$record" ||
      problems+=("$skill_md's '$heading' PASS branch never runs push-branch.sh, so the commits it ticks and commits stay on one disk until the run is review-ready: $(printf '%.120s' "$record")")
  fi
done
report "$name"

# names_the_full_gate <record> — true when <record> runs `detect-test-command.sh --tier all`'s
# command and says it runs exactly once, as the only full-suite gate.
names_the_full_gate() {
  grep -qE 'detect-test-command\.sh --tier all' <<< "$1" &&
    grep -qF 'exactly once' <<< "$1" &&
    grep -qwF 'only' <<< "$1"
}

# 3. The criterion, as one case (issue #341): the full command runs once per cycle, here. Every
#    leaf now runs the fast command, the affected suites, or both, so the Draft PR step is the
#    one place `detect-test-command.sh --tier all`'s command still runs — and the Guardrails
#    invariant that says the full suite is green before the PR opens must name the same
#    command, or the two would read as two different gates. Both are asked of their own slice:
#    the Draft PR step as a whole, and the one Guardrails record that speaks of opening the PR.
name="$skill_md's Draft PR step and its closing invariant both run detect-test-command.sh --tier all's command exactly once, as the only full-suite gate"
problems=()

if draft_pr_or_problem "which command its full-suite gate runs"; then
  names_the_full_gate "$records" ||
    problems+=("$skill_md's Draft PR step never runs detect-test-command.sh --tier all's command exactly once as the only full-suite gate, so where the full command still runs is unstated")
fi
invariant="$(first_record "$(section_records '## Guardrails' '^## ')" -F 'before you open the pr')"
if [[ -z "$invariant" ]]; then
  problems+=("$skill_md's Guardrails has no invariant about opening the PR to read — which command it gates on could not be checked")
elif ! names_the_full_gate "$invariant"; then
  problems+=("$skill_md's closing invariant never names detect-test-command.sh --tier all's command, run exactly once, as the only full-suite gate: $(printf '%.120s' "$invariant")")
fi
report "$name"

# 4. The criterion, as one case (issue #341): a red result on the one full run is not a bail.
#    The fast tier and the affected suites are what every leaf ran, so a suite that only the
#    full command reaches can go red for the first time here — and that is a gap in the tiers,
#    which the methodology answers with another cycle, not a stop. What is pinned is that the
#    Draft PR step has a record that, on red, adds a "repair step" to the ledger, and that the
#    step's text says the two things that make it a repair rather than a retry: a unit-tier
#    test when the failure exposes a gap, and a verifier judging the fix against the full
#    command. The record is asked for first so the case fails closed — a step with no repair
#    record at all gets one problem line, not three that read as partial progress.
name="$skill_md's Draft PR step adds a repair step to the ledger on a red full run, rather than bailing"
problems=()

if draft_pr_or_problem "what a red full run does"; then
  repair="$(first_record "$records" -F 'repair step' -wF 'red' -F 'ledger')"
  if [[ -z "$repair" ]]; then
    problems+=("$skill_md's Draft PR step has no record adding a repair step to the ledger on a red full run, so a suite only the full command reaches still ends the run in a bail")
  else
    grep -qF 'unit-tier test' <<< "$records" && grep -qwF 'gap' <<< "$records" ||
      problems+=("$skill_md's Draft PR step never says a unit-tier test is added when the red full run exposes a gap the fast tier missed")
    grep -qE 'verifier[^.]*full command' <<< "$records" ||
      problems+=("$skill_md's Draft PR step never says the repair step's verifier judges the fix against the full command")
  fi
fi
report "$name"

# 5. The criterion, as one case (issue #341): the repair step is one more cycle, not a loop.
#    A full run that is red again after the repair step has had its chance ends the run, and
#    the bail names every suite still red — a report naming only the first would send the
#    human who reads it to fix one suite and find the next on the rerun. What is pinned is a
#    record of the Draft PR step that bails on a second red full run after a repair step, and
#    that the same record names every suite still red. The record is asked for first so the
#    case fails closed, the way case 4 does.
name="$skill_md's Draft PR step bails on a second red full run after a repair step, naming every suite still red"
problems=()

if draft_pr_or_problem "what a second red full run does"; then
  second="$(first_record "$records" -wF 'bail' -E 'second red|red again' -F 'repair step')"
  if [[ -z "$second" ]]; then
    problems+=("$skill_md's Draft PR step has no record bailing on a second red full run after a repair step, so a repair that does not take can loop instead of ending the run")
  elif ! grep -qE 'every (suite still red|red suite|failing suite|still-red suite)' <<< "$second"; then
    problems+=("$skill_md's Draft PR step bails on a second red full run without naming every suite still red: $(printf '%.120s' "$second")")
  fi
fi
report "$name"

# 6. The criterion, as one case (issue #359, part of #354): the leftovers reach the human
#    who decides the merge. `refactor-owed.sh append` already writes every step's structural
#    candidates into the run's own `.tdd/issue-<n>-refactor-owed.md`, and that file is
#    committed with each step's refactor-pending clear — but a file nobody reads records
#    nothing a reviewer sees. The Draft PR step is where it is read, so what is pinned is
#    that the step runs `render` on that file and puts its output in the PR body, and that an
#    exit 3 from it — no step left anything behind — leaves the section out rather than
#    quoting an empty one. The render call is asked for first so the case fails closed: a step
#    that never renders gets one problem line, not three reading as partial progress. The exit
#    3 half is asked of the step's records rather than of the render record alone, since
#    whether that answer is a clause of the same bullet or the sentence after it is the
#    writer's — but it is asked together with `refactor-owed`, because the step already reads
#    an exit 3 from `next-pending-refactor.sh` and a bare probe would answer with that one.
name="$skill_md's Draft PR step puts refactor-owed.sh render's output in the PR body, and omits the section on exit 3"
problems=()

if draft_pr_or_problem "whether the run's refactor leftovers reach the PR body"; then
  render="$(first_record "$records" -F 'refactor-owed.sh render')"
  if [[ -z "$render" ]]; then
    problems+=("$skill_md's Draft PR step never runs refactor-owed.sh render, so every step's structural leftovers stay in a committed file nobody reading the PR is pointed at")
  else
    grep -qE 'issue-[^ ]*refactor-owed\.md' <<< "$render" ||
      problems+=("$skill_md's Draft PR step runs refactor-owed.sh render without naming the run's .tdd/issue-<n>-refactor-owed.md file, so which file the PR body is rendered from is left to judgement: $(printf '%.120s' "$render")")
    grep -qF 'body' <<< "$render" ||
      problems+=("$skill_md's Draft PR step renders the owed section without putting it in the PR body, so the leftovers are printed where only the conductor sees them: $(printf '%.120s' "$render")")
    grep -F 'refactor-owed' <<< "$records" |
      grep -E 'exits? 3' |
      grep -E 'omit|left out|leaves it out|no section|nothing' > /dev/null ||
      problems+=("$skill_md's Draft PR step never says an exit 3 from refactor-owed.sh render leaves the section out, so a run whose every refactor finished clean gets a ## Refactor owed heading promising leftovers nobody left")
  fi
fi
report "$name"

# 7. The criterion, as one case (issue #360, part of #354): a step the run could not add
#    still reaches the human. When `add-ledger-step.sh` cannot fit a text inside
#    `VERI_STEP_GROWTH`, it appends it as a plain bullet under the ledger's trailing
#    `## Owed steps` heading — a checkbox `next-unchecked.sh` never returns, so nothing in
#    the run will ever read it again. The Draft PR step is the last place it can be read, so
#    what is pinned is that the step copies those bullets out of the run's own ledger and
#    into the PR body under the same `## Owed steps` heading. The copy is asked for first so
#    the case fails closed: a step that never mentions the section gets one problem line
#    rather than two reading as partial progress. The source half asks for the ledger by
#    name — `.tdd/issue-<n>.md` — because the run holds a second file whose name carries
#    "owed", `.tdd/issue-<n>-refactor-owed.md`, and a step that rendered the owed *steps*
#    out of the refactor leftovers would copy the wrong list.
name="$skill_md's Draft PR step copies the ledger's ## Owed steps bullets into the PR body under ## Owed steps"
problems=()

if draft_pr_or_problem "whether the ledger's owed steps reach the PR body"; then
  owed="$(grep -F 'owed steps' <<< "$records")"
  if [[ -z "$owed" ]]; then
    problems+=("$skill_md's Draft PR step never mentions the ledger's ## Owed steps section, so a step the growth budget refused is left in a committed file no reader of the PR is pointed at")
  else
    grep -qF '.tdd/issue-<n>.md' <<< "$owed" ||
      problems+=("$skill_md's Draft PR step speaks of ## Owed steps without naming the run's .tdd/issue-<n>.md ledger as where the bullets are read from, so the run's other owed file could be copied instead: $(printf '%.120s' "$owed")")
    grep -qF 'body' <<< "$owed" ||
      problems+=("$skill_md's Draft PR step never puts the ## Owed steps bullets in the PR body, so they stay where only the conductor sees them: $(printf '%.120s' "$owed")")
  fi
fi
report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
