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
#   1. No instruction of SKILL.md's `### 4. Draft PR` step pushes the branch: it readies a PR
#      whose branch is already on the remote. Which PR commands the step runs is case 10's.
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
#   8. SKILL.md's `### 2. Scope & plan` step pushes the branch and opens the draft PR —
#      `Closes #<n>` in the body, a title marking the work in progress — after the plan
#      commit and before the Plan comment (issue #195).
#   9. SKILL.md's Green PASS branch, the one place a step is ticked, edits the PR body with
#      the done-of-total step count read from the run's ledger (issue #195).
#  10. SKILL.md's Draft PR step creates no PR: it retitles the open one, rewrites its body
#      and marks it ready for review (issue #195).
#  11. SKILL.md's `## Resume` section reuses the open PR its branch already carries and never
#      opens a second one (issue #195).
#  12. SKILL.md's `## Bailing` section leaves that PR open carrying the bail diagnostic —
#      it neither closes it nor still says to open none (issue #195).
#  13. SKILL.md's step 1.2 no longer explains the pid lock by saying the draft PR is opened
#      once every step is green (issue #195).
#  14. SKILL.md's Draft PR step runs `rebase-onto-default.sh` after its dirty-tree and
#      pending-refactor check and before the `done` mark, the metrics commit and
#      `gh pr ready`; its exit 3 continues unchanged and its exit 2 bails with `no-verdict`
#      (issue #238).
#  15. SKILL.md's Draft PR step, after a rebase that changed the tree, runs the full test
#      command once on the rebased tip, bails on red with the PR left a draft, and on green
#      pushes with `push-branch.sh --force-with-lease=<branch>:<pre-rebase-sha>`, never a bare
#      force (issue #238).
#  16. SKILL.md's Draft PR step, on `rebase-onto-default.sh` exit 1, launches a develop-rebase
#      leaf through `supervise.sh`, then a blind verify-rebase through `run-verdict.sh`, revises
#      on REJECT within REVISE_BUDGET, and readies the PR only after a verify-rebase PASS
#      (issue #238).
#  17. SKILL.md's Draft PR step, on a conflicted rebase not resolved within budget — a
#      `REBASE: FAILED`, `REVISE_BUDGET` exhausted, or a killed leaf — resets the branch to
#      `<pre-rebase-sha>`, leaves the PR a draft and bails with a comment naming every
#      conflicting file (issue #238).
#  18. SKILL.md's Draft PR step, after `gh pr ready`, waits on `wait-ci.sh` and then
#      reads the readied PR's statusCheckRollup fail-closed: an empty rollup is never a pass, and a conclusion other than SUCCESS,
#      NEUTRAL or SKIPPED counts as failed (issue #542).
#  19. SKILL.md's Draft PR step never counts a pending check as green, and bounds its CI
#      wait: a check still pending when the bound runs out bails with a cause
#      `classify-bail.sh` classifies (issue #542).
#  20. SKILL.md's Draft PR step bounds the command that waits on the readied PR's checks
#      itself: `wait-ci.sh` with no max-seconds, or one under a tool call's 600, and no
#      `gh pr checks` after `gh pr ready` (issues #542, #544).
#  21. SKILL.md's Draft PR step waits on the readied PR's checks and reads their rollup before
#      the `done` mark and the `metrics:` commit, so a red CI result or a `ci-timeout` bail is
#      never reached by a run that already recorded itself done (issue #542).
#  22. SKILL.md's Draft PR command block itself bails with cause `ci-timeout` on `wait-ci.sh`'s
#      exit 2, between the wait and the `done` mark, and its prose says so (issues #542, #544).
#  23. SKILL.md's Draft PR step answers a failed CI check by reading `gh run view --log-failed`,
#      appending a repair step that quotes the failing suite and its `FAIL -` line, committing
#      it and returning to the cycle loop, all before the `done` mark (issue #542).
#  24. SKILL.md's Draft PR step bails on a second red CI result after a CI repair step: its
#      command block runs a bail between the `--log-failed` read and the `done` mark, with a
#      cause `classify-bail.sh` maps to `system` or `process`, and its prose says so (#542).
#  25. SKILL.md's Draft PR step waits on CI by calling `wait-ci.sh` after `gh pr ready` and
#      again on its exit 3, with no wait loop inside one command block and no pending test
#      that reads `.status` alone (#544).
#  26. SKILL.md's Draft PR step stops at a `ci-timeout` or `ci-red` bail: neither the `done`
#      mark nor the `metrics:` commit follows the bail in its command block, and its prose
#      sends the run to *Bailing* (#544).
#  27. SKILL.md's Draft PR step appends its CI repair step with a `⟦ci-repair⟧` text and
#      recognises a second red by that mark on a ledger line, not by the repair step's prose
#      (#544).
#  28. SKILL.md's Draft PR step leaves no CI run on the readied PR that nothing reads: every push
#      its command lines make after the first `wait-ci.sh` call has a `wait-ci.sh` call after
#      it (#544).
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

# section_lines <heading prefix> <closer regex> — the document's lines, verbatim, from the
# heading that STARTS WITH <heading prefix> to the next line matching <closer regex>. Every
# read here is scoped to a section, because the document pushes a branch and takes a PASS
# branch on several paths: an unscoped read would answer one criterion with another path's
# instruction, and fail a document that had done exactly what was asked. Which headings close
# a section is the caller's, since the levels differ by section. A prefix rather than the
# whole heading because a heading may carry trailing prose after an em dash; the prefix is
# what identifies it and is quotable in a problem message. The slicing is here alone because
# two readings are taken of the same slice — as records and as command lines — and a section
# read two ways by two copies of this awk is a section that can come to mean two things.
section_lines() {
  awk -v h="$1" -v closers="$2" \
    '$0 ~ closers { inside = (index($0, h) == 1); next } inside' "$skill_path"
}

# section_records <heading prefix> <closer regex> — that slice as records.
section_records() { section_lines "$1" "$2" | records_of; }

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

# section_or_problem <heading prefix> <closer regex> <what> — read into `records` the section
# whose heading starts with <heading prefix>, <closer regex> ending it, or record the one
# problem that says the case could not be read at all, naming <what> it could therefore not
# check. Non-zero when the section is gone, so each case below is its probes alone rather than
# its probes and its own missing-section branch: every case here asks the document for one
# slice first, and would otherwise spell the same fetch and the same fail-closed message eight
# times over. The closer is a parameter because the cases read sections at two levels — the
# numbered steps, which a heading of either level ends, and since #195 `## Resume`, which only
# another `## ` does. Which slice it read is recorded in `section_heading`/`section_closer`,
# so a case wanting the same slice's command lines asks `section_commands` for them rather
# than spelling the heading and the closer a second time.
section_or_problem() {
  section_heading="$1" section_closer="$2"
  records="$(section_records "$1" "$2")"
  [[ -n "$records" ]] && return 0
  problems+=("$skill_md has no $1 section to read — $3 could not be checked")
  return 1
}

# step_or_problem <heading prefix> <what> — that reader for a numbered step, whose closer is
# always the same. The heading stays a parameter because the cases read two steps —
# `### 4. Draft PR` and, since #195, `### 2. Scope & plan`, which `### 2b. Start comment` ends.
step_or_problem() { section_or_problem "$1" '^## |^### ' "$2"; }

# 1. The criterion, as one case: the step asks for review on a branch that is already on the
#    remote, and pushes nothing itself. It used to anchor on `gh pr create` first, so that a
#    section emptied of its PR instruction could not read as "it no longer pushes" — since
#    #195 that anchor is case 10's, which asks the same slice which PR commands it issues and
#    fails closed on its own three positive probes. Asking it here too would be the same
#    question twice, and the two answers would now have to disagree: the step must run
#    `gh pr create` for the old probe and must not for case 10's, a requirement met only by a
#    document that names the command in prose. What remains here is the push, and the section
#    being unreadable is still one problem line, from `step_or_problem`. `git push` rather
#    than the word "push": the step's first sub-step still refuses to go on while there is
#    nothing *fit* to push, and that refusal is #116's gate, not a push. What this criterion
#    is about is whether the step issues the command.
name="$skill_md's Draft PR step readies the PR against the already-pushed branch, with no push of its own"
problems=()

if step_or_problem '### 4. Draft PR' "whether the step still pushes"; then
  pushes="$(first_record "$records" -F 'git push')"
  [[ -z "$pushes" ]] ||
    problems+=("$skill_md's Draft PR step still pushes the branch itself, so the procedure reads as though the branch reaches the remote only once the run is review-ready: $(printf '%.120s' "$pushes")")
fi
report "$name"

# pass_or_problem <heading prefix> <what> — read into `record` the PASS branch inside the
# `####` section whose heading starts with <heading prefix>, or record the one problem that
# says the case could not be read at all, naming <what> it could therefore not check.
# Non-zero when there is no such section or no such branch in it, so each case below is its
# probes alone, the way `step_or_problem` does it for a numbered step. Any heading ends one
# of these sections, the document's innermost level.
pass_or_problem() {
  record="$(first_record "$(section_records "$1" '^#')" -E '^ *- \*\*pass')"
  [[ -n "$record" ]] && return 0
  problems+=("$skill_md has no PASS branch under '$1' to read — $2 could not be checked")
  return 1
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
  if pass_or_problem "$heading" "whether the branch is pushed where the ledger is written"; then
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

if step_or_problem '### 4. Draft PR' "which command its full-suite gate runs"; then
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

if step_or_problem '### 4. Draft PR' "what a red full run does"; then
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

if step_or_problem '### 4. Draft PR' "what a second red full run does"; then
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

if step_or_problem '### 4. Draft PR' "whether the run's refactor leftovers reach the PR body"; then
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

if step_or_problem '### 4. Draft PR' "whether the ledger's owed steps reach the PR body"; then
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

# 8. The criterion, as one case (issue #195): the claim every other machine can see is made
#    as soon as there is a commit to hang it on. A PR needs a commit ahead of the base and the
#    plan commit is the run's first, so the draft PR opens there — not at step 4, which for a
#    multi-step issue is hours later, and until then a second machine running `/tdd <scope>`
#    reads the issue as free and takes it again (four such runs were live unseen on
#    2026-09-14). What is pinned is the instruction and its place in the order: the record that
#    runs `gh pr create` sits inside the `### 2. Scope & plan` section, after the record
#    carrying the plan commit and before the one posting the Plan comment, and it carries the
#    two things that make the PR a claim rather than a PR — `Closes #<n>`, which is what names
#    the issue it claims, and a title saying the work is in progress, which is what stops a
#    reader taking a draft for a finished branch. The `gh pr create` record is asked for first
#    so the case fails closed: a section that never opens a PR gets one problem line rather
#    than five reading as partial progress. The push is asked for by script name, the way case
#    2 asks it, because `push-branch.sh` is where the not-a-bail rule lives.
name="$skill_md's Scope & plan step pushes and opens the draft PR after the plan commit, before the Plan comment"
problems=()

# record_number <grep-options> <pattern> — the 1-based position of the first record of
# `records` matching, or nothing when none does. The section's records are in document order,
# so this is what places the three instructions relative to one another. The match is collected
# into a variable before `head` reads it: a `grep … | head -1` pipeline would let the reader
# leave first and hand this suite's `pipefail` grep's SIGPIPE as the answer (issue #422).
record_number() {
  local hits
  hits="$(grep -n "$1" -- "$2" <<< "$records")"
  [[ -n "$hits" ]] || return 0
  head -1 <<< "$hits" | cut -d: -f1
}

if step_or_problem '### 2. Scope & plan' "where the run's draft PR is opened"; then
  # The position first and the record read off it, rather than a `first_record` search for the
  # same string: one read of the document answers both what the instruction says and where it
  # sits, so the two can never be answered by different records.
  pr_at="$(record_number -F 'gh pr create')"
  if [[ -z "$pr_at" ]]; then
    problems+=("$skill_md's Scope & plan step never runs gh pr create, so a multi-step run puts no claim on origin until its last step and a second machine reads the issue as free for the whole of it")
  else
    pr_record="$(sed -n "${pr_at}p" <<< "$records")"
    grep -qF -- '--draft' <<< "$pr_record" ||
      problems+=("$skill_md's Scope & plan step opens the PR without --draft, so a run one step in reads as a branch offered for review: $(printf '%.120s' "$pr_record")")
    grep -qF 'closes #<n>' <<< "$pr_record" ||
      problems+=("$skill_md's Scope & plan step opens the PR without Closes #<n> in its body, so nothing on the PR names the issue it claims: $(printf '%.120s' "$pr_record")")
    grep -qE 'wip|work in progress' <<< "$pr_record" ||
      problems+=("$skill_md's Scope & plan step opens the PR without a title marking the work in progress, so a reader of origin cannot tell a run mid-flight from a finished branch: $(printf '%.120s' "$pr_record")")
    grep -qF 'push-branch.sh' <<< "$records" ||
      problems+=("$skill_md's Scope & plan step never runs push-branch.sh, so the branch the PR is opened against has never reached the remote")

    commit_at="$(record_number -F 'plan: scope #<n> into')"
    comment_at="$(record_number -F 'mirror the plan')"
    if [[ -z "$commit_at" || -z "$comment_at" ]]; then
      problems+=("$skill_md's Scope & plan step no longer has both the plan commit and the Plan comment to place the PR between — where it is opened could not be checked")
    else
      [[ "$commit_at" -lt "$pr_at" ]] ||
        problems+=("$skill_md's Scope & plan step opens the PR at record $pr_at, before the plan commit at record $commit_at — there is no commit ahead of the base for a PR to be opened against yet")
      [[ "$pr_at" -lt "$comment_at" ]] ||
        problems+=("$skill_md's Scope & plan step opens the PR at record $pr_at, after the Plan comment at record $comment_at — the comment is meant to name the PR url, and the claim is meant to be the first act after the plan commit")
    fi
  fi
fi
report "$name"

# 9. The criterion, as one case (issue #195): the claim on origin says how far the run has
#    got. The draft PR now opens at the plan commit, hours before the run ends, so for the
#    whole of a multi-step issue its body is the only thing another machine can read — and a
#    body written once at the plan commit says the same thing at step 1 and at step 7. The
#    ledger already holds the answer: every step is a checkbox, and the tick that closes a
#    step is where the count changes. So what is pinned is that the Green PASS branch — the
#    one place a step is ticked and committed — also edits the PR body, and that the edit
#    names the ledger it counts and states the count as done-of-total rather than a bare
#    "in progress". The `gh pr edit` probe runs first so the case fails closed: a PASS branch
#    that never edits the PR gets one problem line rather than three reading as partial
#    progress. The record is the Green PASS branch's own, the way case 2 reads it, because an
#    unscoped read would answer with step 4's own `gh pr edit`, which rewrites the body once
#    at the end and is a different instruction on a different path.
name="$skill_md's Green PASS branch updates the PR body with the ledger's done-of-total step count"
problems=()

if pass_or_problem '#### Green' "whether the step tick updates the PR body"; then
  if ! grep -qF 'gh pr edit' <<< "$record"; then
    problems+=("$skill_md's Green PASS branch never runs gh pr edit, so the draft PR opened at the plan commit still reads as step 0 for the whole of a multi-step run")
  else
    grep -qF -- '--body' <<< "$record" ||
      problems+=("$skill_md's Green PASS branch edits the PR without --body, so nothing a reader of the PR sees carries the run's progress: $(printf '%.120s' "$record")")
    grep -qF '.tdd/issue-<n>.md' <<< "$record" ||
      problems+=("$skill_md's Green PASS branch edits the PR body without naming the run's .tdd/issue-<n>.md ledger as where the count is read from, so which file answers how far the run has got is left to judgement: $(printf '%.120s' "$record")")
    grep -qE '<done> of <total>|[0-9]+ of [0-9]+|done of|of how many' <<< "$record" ||
      problems+=("$skill_md's Green PASS branch edits the PR body without a done-of-total step count, so a reader learns the run moved but not how far it has left to go: $(printf '%.120s' "$record")")
  fi
fi
report "$name"

# section_commands — the second reading of the slice `section_or_problem` last took: its
# command lines, leading indent stripped, a trailing `\` joined to the line after it the way
# the shell joins one, and case folded last. Cases 10 to 12 ask which `gh` commands a section
# issues, and `records_of` cannot answer that: it glues a bullet's whole fenced block into one
# record, so a record holding `gh pr create --title` would answer "the step retitles the PR"
# for a document that only creates one. The continuation join is what keeps a flag written on
# the next line — as `gh pr create`'s own `--title` is today — part of the command that carries
# it. It takes no arguments and re-reads what `section_or_problem` recorded, because a case
# that named its heading and closer a second time here could name a different section than the
# one its records came from, and then its positive and negative probes would be answered by
# two different slices of the document.
section_commands() {
  section_lines "$section_heading" "$section_closer" |
  awk '{ sub(/^[[:space:]]+/, "")
         buf = (cont ? buf " " $0 : $0)
         if (buf ~ /\\$/) { sub(/\\$/, "", buf); cont = 1; next }
         cont = 0; print buf }
       END { if (cont) print buf }' | tr '[:upper:]' '[:lower:]'
}

# line_of <ere> — the number of the first line of `commands` matching <ere> at its start, or
# nothing. Cases 14 and 15 both order one command line of the Draft PR step against another,
# so the lookup is written here once rather than as an awk per probe.
line_of() { awk -v re="$1" '$0 ~ ("^" re) { print NR; exit }' <<< "$commands"; }
done_mark='veri_issue=[^ ]* veri_actor=conductor [$]s/event[.]sh done'
metrics_commit='git commit -m "metrics:'
rollup_read='gh pr view .*--json statuscheckrollup'
wait_ci_run='[^#]*[$]s/wait-ci[.]sh '
log_failed_read='[^#]*gh run view [^#]*--log-failed'

# unmarked_records — `records` with its Markdown emphasis and code marks stripped, so a probe
# reads "rebase-onto-default.sh's exit 1" whether the document bolds it, backticks it or both.
# Cases 14, 15 and 16 all read the Draft PR step's prose this way, so the set of marks
# stripped is written once rather than as three copies that could come to strip different ones.
unmarked_records() { tr -d '*`' <<< "$records"; }

# 10. The criterion, as one case (issue #195): the run has had a PR since its plan commit, so
#     the step named for opening one must open none. A second `gh pr create` against a branch
#     that already has an open PR is not a no-op — it is either a refusal that ends the run at
#     its last step, or a second PR for the same branch, and then the claim another machine
#     reads and the PR a human is asked to merge are two different pages. What is left for the
#     step is the three edits that turn the claim into a review request: the title stops saying
#     the work is in progress, the body is rewritten into its final form, and the draft is
#     marked ready. The three positive probes run before the negative one so the case fails
#     closed — a step emptied or renamed must not read as "it creates no PR" — and each probe
#     anchors at the start of a command line, so prose naming `gh pr create` to say the step no
#     longer runs it is not read as the step running it.
name="$skill_md's Draft PR step creates no PR: it retitles and rewrites the open one and marks it ready for review"
problems=()

if step_or_problem '### 4. Draft PR' "whether the step creates a second PR"; then
  commands="$(section_commands)"
  grep -qE '^gh pr edit .*--title' <<< "$commands" ||
    problems+=("$skill_md's Draft PR step never runs gh pr edit with --title, so the PR keeps the work-in-progress title it was opened with at the plan commit and a reader of origin cannot tell the finished branch from a run mid-flight")
  grep -qE '^gh pr edit .*--body' <<< "$commands" ||
    problems+=("$skill_md's Draft PR step never runs gh pr edit with --body, so the body a human reads at the merge is still the one-line claim the plan commit opened")
  grep -qE '^gh pr ready' <<< "$commands" ||
    problems+=("$skill_md's Draft PR step never runs gh pr ready, so a finished run leaves a draft nobody is asked to review")
  creates="$(first_record "$commands" -E '^gh pr create')"
  [[ -z "$creates" ]] ||
    problems+=("$skill_md's Draft PR step still runs gh pr create, so a run whose draft PR has been open since its plan commit either fails at its last step or opens a second PR for the same branch: $(printf '%.120s' "$creates")")
fi
report "$name"

# 11. The criterion, as one case (issue #195): a resume finds the claim already on its branch
#     and uses it. The PR is opened at the plan commit by step 2.3, and a resume skips step 2
#     outright — so the section that governs a re-run is the only place that can say what
#     becomes of the PR the first run left open. Said nowhere, a resumed run has no url to
#     hand the tick's `gh pr edit` and step 4's rewrite, and the reading that fills the gap is
#     the one this criterion forbids: open one. A second `gh pr create` against a branch that
#     already has an open PR is either a refusal that ends the resume where it started, or a
#     second PR for the same branch — two pages claiming one issue, which is the failure the
#     whole of #195 exists to prevent. So what is pinned is the pair: the section reads the
#     branch's PR with `gh pr view`, and it issues no `gh pr create` that is not conditioned on
#     there being no open PR to reuse — the run killed inside step 2.3's own window left a
#     branch with none, and opening the first one is not opening a second. The positive probe
#     runs first so the case fails closed: a section that says nothing about the PR at all gets
#     the one problem line that says so, not a pass earned by never naming `gh pr create`.
name="$skill_md's Resume reuses the open PR already on its branch and opens no second one"
problems=()

if section_or_problem '## Resume' '^## ' "what a resumed run does with the PR its branch already carries"; then
  # The command lines rather than the records for the positive probe, the way case 10 asks its
  # three: prose naming `gh pr view` to explain a neighbouring step is not the resume issuing it.
  grep -qE '^gh pr view' <<< "$(section_commands)" ||
    problems+=("$skill_md's Resume section never runs gh pr view, so a resumed run never reads the open PR its branch already carries and has no url for the tick's gh pr edit or step 4's rewrite")
  creates="$(first_record "$records" -F 'gh pr create')"
  if [[ -n "$creates" ]]; then
    grep -qE 'no open pr|no pr|none|no such pr' <<< "$creates" ||
      problems+=("$skill_md's Resume section runs gh pr create without conditioning it on there being no open PR to reuse, so a resume of a run that already opened one leaves the issue claimed by two pages: $(printf '%.120s' "$creates")")
  fi
fi
report "$name"

# 12. The criterion, as one case (issue #195): the run has had a draft PR since its plan
#     commit, and a bail is the ending that most needs it. The PR is the cross-machine claim —
#     `solvable-issues.sh` leaves out an issue an open PR says `Closes #<n>` for — so a bail
#     that took the PR down would hand the issue back to the pool for the next machine to
#     re-take and re-bail, and would discard the visible record a bail exists to leave. A bail
#     also means a human has to look, and the draft PR is where they look: the diagnostic the
#     issue thread gets has to reach the PR too, or the page a reader opens says a run is in
#     progress when it stopped. So what is pinned is the pair: the section puts the bail
#     diagnostic on the PR, and it neither closes that PR nor still instructs the run to open
#     none. The positive probe runs first so the case fails closed — a Bailing section emptied
#     of every PR instruction must not read as "it leaves the PR open" by never naming one.
name="$skill_md's Bailing section leaves the draft PR open carrying the bail diagnostic, and opens no PR"
problems=()

if section_or_problem '## Bailing' '^## ' "what a bailed run does with the draft PR its branch already carries"; then
  # The command lines for the positive probe, the way cases 10 and 11 ask theirs: prose
  # naming a `gh pr` command to explain a neighbouring step is not the bail issuing it.
  commands="$(section_commands)"
  grep -qE '^gh pr comment|^gh pr edit .*--body' <<< "$commands" ||
    problems+=("$skill_md's Bailing section runs neither gh pr comment nor gh pr edit --body, so the bail diagnostic reaches the issue thread and never the draft PR a human is pointed at, which still reads as a run in progress")
  closes="$(first_record "$commands" -E '^gh pr close')"
  [[ -z "$closes" ]] ||
    problems+=("$skill_md's Bailing section closes the PR, so the issue goes back into solvable-issues.sh's pool for the next machine to re-take and re-bail, and the visible record of the bail is gone: $(printf '%.120s' "$closes")")
  opens_none="$(first_record "$records" -F 'open no pr')"
  [[ -z "$opens_none" ]] ||
    problems+=("$skill_md's Bailing section still tells the run to open no PR, an instruction whose premise went with #195: the PR has been open since the plan commit, so there is nothing here to withhold: $(printf '%.120s' "$opens_none")")
fi
report "$name"

# 13. The criterion, as one case (issue #195): step 1.2's pid lock is explained by saying what
#     the run has instead of it, and what it has changed. The passage justifying the lock rests
#     on the draft PR being opened "once every step is green" — the order #195 reversed: the PR
#     now opens at the plan commit, minutes into the run, so the hours-long window the passage
#     describes is gone and the sentence tells a conductor the opposite of what the procedure
#     it is reading does. A stale rationale is not a harmless leftover here: it is the one
#     paragraph that says which of the two signals covers what, so a reader who believes it
#     reads the pid lock as the only claim for the whole run and the PR as an end-of-run
#     artefact, which is the model #195 exists to replace. So what is pinned is the absence of
#     that premise from the step that carries the lock: no record of `### 1.` says the PR is
#     opened once every step is green.
name="$skill_md's worktree step no longer says the draft PR is opened once every step is green"
problems=()

if step_or_problem '### 1. Read the issue' "what step 1.2 says the claim is before the PR exists"; then
  stale="$(first_record "$records" -F 'every step is green')"
  [[ -z "$stale" ]] ||
    problems+=("$skill_md's worktree step still says the draft PR is opened once every step is green, the order #195 reversed — the PR now opens at the plan commit, so the window this passage gives as the reason for the pid lock no longer exists: $(printf '%.120s' "$stale")")
fi
report "$name"

# 14. The criterion, as one case (issue #238): two runs branch from the same `main`, and when
#     the first merges the second's branch owes a rebase. That rebase used to happen after veri
#     finished, in the operator's merge routine, with nothing re-verified; `rebase-onto-default.sh`
#     now does it inside the run, and a script's exit code is only an answer if the prose that
#     calls it branches on it. Where it runs is read off the section's command lines, the order
#     the conductor types them in: after sub-step 1's two questions, so it never rebases a tree
#     holding work no verifier has seen, and before the `done` mark, the `metrics:` commit and
#     `gh pr ready`, so nothing is recorded as finished and no human is asked to look at a branch
#     still behind the default one. What its exit codes do is read off the records naming it.
name="$skill_md's Draft PR step runs rebase-onto-default.sh after its dirty-tree and pending-refactor check and before the done mark, the metrics commit and gh pr ready; exit 3 continues unchanged, exit 2 bails with no-verdict"
problems=()

if step_or_problem '### 4. Draft PR' "where the step rebases onto the default branch"; then
  commands="$(section_commands)"
  rebase="$(line_of '[$]s/rebase-onto-default[.]sh')"
  if [[ -z "$rebase" ]]; then
    problems+=("$skill_md's Draft PR step runs no \$S/rebase-onto-default.sh, so a branch behind the default one is still readied for review un-rebased")
  else
    # rebase_runs <after|before> <ere> — record a problem unless rebase-onto-default.sh runs
    # on the side of the first command line matching <ere> that <after|before> names.
    rebase_runs() {
      local at
      at="$(line_of "$2")"
      if [[ -z "$at" ]]; then
        problems+=("$skill_md's Draft PR step runs no $2, so the rebase's order against it could not be checked")
      elif { [[ "$1" == after ]] && [[ "$at" -ge "$rebase" ]]; } ||
           { [[ "$1" == before ]] && [[ "$at" -le "$rebase" ]]; }; then
        problems+=("$skill_md's Draft PR step runs rebase-onto-default.sh (command line $rebase) not $1 $2 (command line $at)")
      fi
    }
    for before in 'git status --porcelain' '[$]s/next-pending-refactor[.]sh'; do
      rebase_runs after "$before"
    done
    for after in "$done_mark" '[$]s/metrics[.]sh' "$metrics_commit" 'gh pr ready'; do
      rebase_runs before "$after"
    done
    plain="$(unmarked_records)"
    said="$(first_record "$plain" -F 'rebase-onto-default.sh' -E 'exit 3' -E 'continu')"
    [[ -n "$said" ]] ||
      problems+=("no instruction of $skill_md's Draft PR step naming rebase-onto-default.sh says its exit 3 continues unchanged")
    said="$(first_record "$plain" -F 'rebase-onto-default.sh' -E 'exit 2' -E 'bail' -F 'no-verdict')"
    [[ -n "$said" ]] ||
      problems+=("no instruction of $skill_md's Draft PR step naming rebase-onto-default.sh says its exit 2 bails with no-verdict")
  fi
fi
report "$name"

# 15. The criterion, as one case (issue #238): a rebase that changed the tree has made a tip no
#     suite has run on — two green branches can combine into a red one — and has rewritten the
#     history already on origin, so the branch's remote copy can only be replaced, not
#     fast-forwarded. What is pinned is the pair that makes that safe. The records: the full
#     test command runs once on the rebased tip, and a red result there bails with the PR left
#     a draft rather than readied. The command lines: the push after it is
#     `$S/push-branch.sh --force-with-lease=<branch>:<pre-rebase-sha>`, run after the rebase,
#     pinned to the sha the branch held before it, so a remote copy another writer moved in the
#     meantime is refused rather than clobbered — and no command line of the step pushes with a
#     bare force, which would clobber it. The positive probes run before the negative one so the
#     case fails closed: a step that never pushes at all must not read as "never a bare force".
name="$skill_md's Draft PR step runs the full test command once on a rebased tip, bails on red without readying the PR, and on green pushes with push-branch.sh --force-with-lease=<branch>:<pre-rebase-sha>, never a bare force"
problems=()

if step_or_problem '### 4. Draft PR' "what the step does after a rebase that changed the tree"; then
  commands="$(section_commands)"
  rebase="$(line_of '[$]s/rebase-onto-default[.]sh')"
  leased="$(line_of '[$]s/push-branch[.]sh --force-with-lease=[^ :]+:[^ ]*pre-rebase')"
  if [[ -z "$leased" ]]; then
    problems+=("$skill_md's Draft PR step runs no \$S/push-branch.sh --force-with-lease=<branch>:<pre-rebase-sha>, so a rebased branch's rewritten history has no push pinned to the sha its remote copy held before the rebase")
  elif [[ -z "$rebase" ]] || [[ "$leased" -le "$rebase" ]]; then
    problems+=("$skill_md's Draft PR step runs push-branch.sh --force-with-lease (command line $leased) not after rebase-onto-default.sh (command line ${rebase:-none})")
  fi
  plain="$(unmarked_records)"
  said="$(first_record "$plain" -F 'rebased tip' -E 'full (test )?command|full suite|--tier all' -wF 'once')"
  [[ -n "$said" ]] ||
    problems+=("no instruction of $skill_md's Draft PR step runs the full test command once on the rebased tip, so a rebase that combined two green branches into a red one reaches review unrun")
  said="$(first_record "$plain" -F 'rebased tip' -wF 'red' -wF 'bail' -F 'draft')"
  [[ -n "$said" ]] ||
    problems+=("no instruction of $skill_md's Draft PR step bails on a red rebased tip with the PR left a draft, so a red rebase can still be readied for review")
  bare="$(first_record "$commands" -E '(^git push|^[$]s/push-branch[.]sh).*( --force( |$)| -f( |$)| \+)')"
  [[ -z "$bare" ]] ||
    problems+=("$skill_md's Draft PR step pushes with a bare force, which replaces the branch's remote copy whatever another writer left there: $(printf '%.120s' "$bare")")
fi
report "$name"

# 16. The criterion, as one case (issue #238): a rebase that conflicts is exit 1 from
#     `rebase-onto-default.sh`, and its resolution is new code no verifier has seen. So a leaf
#     resolves it, launched through the supervisor like every other, and a blind verifier
#     judges it before any human is asked to look. What is pinned, off the command lines: a
#     `develop-rebase` leaf launched through `supervise.sh`, then a `verdict-rebase` launch of
#     `run-verdict.sh … rebase`, both after the rebase and both before `gh pr ready`. Off the
#     records: the step names `rebase-onto-default.sh`'s exit 1 as what launches the leaf, a
#     `REJECT` goes round the revise loop within `REVISE_BUDGET`, and the PR is readied only
#     after a verify-rebase `PASS`. The positive probes are all there is, so a step emptied of
#     the path fails rather than reading as one that never needed it.
name="$skill_md's Draft PR step, on rebase-onto-default.sh exit 1, launches a develop-rebase leaf through supervise.sh, then a blind verify-rebase through run-verdict.sh, revises on REJECT within REVISE_BUDGET, and readies the PR only after a verify-rebase PASS"
problems=()

if step_or_problem '### 4. Draft PR' "what the step does with a conflicted rebase"; then
  commands="$(section_commands)"
  rebase="$(line_of '[$]s/rebase-onto-default[.]sh')"
  develop="$(line_of '.*[$]s/supervise[.]sh develop-rebase ')"
  verdict="$(line_of '.*[$]s/supervise[.]sh verdict-rebase [$]s/run-verdict[.]sh .* rebase ')"
  ready="$(line_of 'gh pr ready')"
  if [[ -z "$develop" ]]; then
    problems+=("$skill_md's Draft PR step launches no develop-rebase leaf through \$S/supervise.sh, so a conflicted rebase has nothing to resolve it")
  fi
  if [[ -z "$verdict" ]]; then
    problems+=("$skill_md's Draft PR step launches no verdict-rebase through \$S/supervise.sh \$S/run-verdict.sh … rebase, so a conflict's resolution reaches review seen by no blind verifier")
  fi
  if [[ -n "$develop" ]] && [[ -n "$verdict" ]]; then
    { [[ -n "$rebase" ]] && [[ "$rebase" -lt "$develop" ]] && [[ "$develop" -lt "$verdict" ]] &&
      [[ -n "$ready" ]] && [[ "$verdict" -lt "$ready" ]]; } ||
      problems+=("$skill_md's Draft PR step does not run rebase-onto-default.sh (command line ${rebase:-none}), the develop-rebase leaf ($develop), the verdict-rebase ($verdict) and gh pr ready (${ready:-none}) in that order")
  fi
  plain="$(unmarked_records)"
  said="$(first_record "$plain" -F 'rebase-onto-default.sh' -E 'exit 1' -F 'develop-rebase')"
  [[ -n "$said" ]] ||
    problems+=("no instruction of $skill_md's Draft PR step says rebase-onto-default.sh's exit 1 launches the develop-rebase leaf")
  said="$(first_record "$plain" -wF 'reject' -F 'revise_budget')"
  [[ -n "$said" ]] ||
    problems+=("no instruction of $skill_md's Draft PR step sends a verify-rebase REJECT round the revise loop within REVISE_BUDGET")
  said="$(first_record "$plain" -F 'verify-rebase' -wF 'pass' -E 'ready|readie')"
  [[ -n "$said" ]] ||
    problems+=("no instruction of $skill_md's Draft PR step readies the PR only after a verify-rebase PASS")
fi
report "$name"

# 17. The criterion, as one case (issue #238): the conflicted-rebase path of case 16 can end
#     without a resolution — the leaf reports `REBASE: FAILED`, `REVISE_BUDGET` runs out on
#     verify-rebase `REJECT`s, or the leaf is killed — and then the branch holds a half-made
#     resolution no verifier has passed. What is pinned, off the records: the step names all
#     three of those endings together, it resets the branch hard to `<pre-rebase-sha>` so the
#     branch is left un-rebased, and its bail leaves the PR a draft with a comment naming every
#     conflicting file, so the human the bail hands the conflict to knows where it is. The
#     positive probes are all there is, so a step emptied of the path fails rather than
#     reading as one that never needed it.
name="$skill_md's Draft PR step, on a rebase not resolved within budget (REBASE: FAILED, REVISE_BUDGET exhausted or a killed leaf), resets the branch to <pre-rebase-sha>, leaves the PR a draft and bails naming every conflicting file"
problems=()

if step_or_problem '### 4. Draft PR' "what the step does with a rebase it could not resolve"; then
  plain="$(unmarked_records)"
  said="$(first_record "$plain" -F 'rebase: failed' -F 'revise_budget' -wE 'killed|kill')"
  [[ -n "$said" ]] ||
    problems+=("no instruction of $skill_md's Draft PR step names REBASE: FAILED, an exhausted REVISE_BUDGET and a killed leaf together as a rebase not resolved within budget")
  said="$(first_record "$plain" -E 'git reset --hard <pre-rebase-sha>')"
  [[ -n "$said" ]] ||
    problems+=("no instruction of $skill_md's Draft PR step resets the branch with git reset --hard <pre-rebase-sha>, so a rebase it could not resolve leaves a half-made resolution on the branch")
  said="$(first_record "$plain" -wF 'bail' -E '(every|each|all) (of the )?conflicting file' -F 'draft')"
  [[ -n "$said" ]] ||
    problems+=("no instruction of $skill_md's Draft PR step bails on an unresolved rebase with the PR left a draft and a comment naming every conflicting file")
fi
report "$name"

# 18. The criterion, as one case (issue #542): a readied PR's CI is the Linux half of the
#     portability promise, so a run that stops at `gh pr ready` never sees a Linux-only red.
#     What is pinned: `wait-ci.sh` runs after `gh pr ready`, a `gh pr view` reading
#     `statusCheckRollup` runs after that wait, and the step reads it the way the merge skill
#     does — an empty rollup is never a pass, and a completed check whose conclusion is not
#     SUCCESS, NEUTRAL or SKIPPED counts as failed.
name="$skill_md's Draft PR step, after gh pr ready, waits on wait-ci.sh and reads the readied PR's statusCheckRollup fail-closed: an empty rollup is never a pass and a conclusion other than SUCCESS, NEUTRAL or SKIPPED counts as failed (#542)"
problems=()

if step_or_problem '### 4. Draft PR' "whether the step reads the readied PR's CI"; then
  commands="$(section_commands)"
  ready="$(line_of 'gh pr ready')"
  watch="$(line_of "$wait_ci_run")"
  rollup="$(line_of "$rollup_read")"
  [[ -n "$ready" && -n "$watch" && "$watch" -gt "$ready" ]] ||
    problems+=("$skill_md's Draft PR step runs no \$S/wait-ci.sh after gh pr ready, so nothing waits for the readied PR's CI to finish")
  [[ -n "$watch" && -n "$rollup" && "$rollup" -gt "$watch" ]] ||
    problems+=("$skill_md's Draft PR step runs no gh pr view --json statusCheckRollup after its \$S/wait-ci.sh, so the run reads CI before it has answered")
  plain="$(unmarked_records)"
  said="$(first_record "$plain" -F 'rollup' -wF 'empty' -E 'never[a-z ]* pass')"
  [[ -n "$said" ]] ||
    problems+=("no instruction of $skill_md's Draft PR step says an empty rollup is never a pass")
  said="$(first_record "$plain" -F 'conclusion' -F 'success' -F 'neutral' -F 'skipped' -E 'fail')"
  [[ -n "$said" ]] ||
    problems+=("no instruction of $skill_md's Draft PR step counts a completed check whose conclusion is not SUCCESS, NEUTRAL or SKIPPED as failed")
fi
report "$name"

# 19. The criterion, as one case (issue #542): the bail's cause is handed to classify-bail.sh
#     itself, so a cause the script does not know fails here rather than at the bail.
name="$skill_md's Draft PR step never counts a pending check as green, and a check still pending when its bounded CI wait runs out bails with a cause classify-bail.sh classifies (#542)"
problems=()

if step_or_problem '### 4. Draft PR' "what the step does with a check still pending"; then
  plain="$(unmarked_records)"
  said="$(first_record "$plain" -E 'pending check|check[a-z ]* pending' -wF 'never' -E 'green|pass')"
  [[ -n "$said" ]] ||
    problems+=("no instruction of $skill_md's Draft PR step says a pending check never counts as green")
  bail="$(first_record "$records" -E 'pending check|check[a-z ]* pending' -E 'bound|timeout|time out|runs out' -wF 'bail')"
  if [[ -z "$bail" ]]; then
    problems+=("no instruction of $skill_md's Draft PR step bounds the CI wait and bails on a check still pending when the bound runs out, so a hung CI job waits forever")
  else
    classified=""
    while IFS= read -r cause; do
      [[ -n "$cause" ]] || continue
      "$ROOT/skills/tdd/scripts/classify-bail.sh" "$cause" > /dev/null 2>&1 && classified="$cause"
    done < <(grep -o '`[^`]*`' <<< "$bail" | tr -d '`')
    [[ -n "$classified" ]] ||
      problems+=("$skill_md's Draft PR step bails on a check still pending past its bound with no cause classify-bail.sh classifies: $(printf '%.120s' "$bail")")
  fi
fi
report "$name"

# 20. The criterion, as one case (issue #542): a bound stated only in prose is one the shell
#     never enforces, so the command that waits must carry it (#544): one Bash call is killed at
#     600 seconds, so a `wait-ci.sh` slice longer than that ends the call rather than the slice,
#     and a `gh pr checks` after `gh pr ready` is a second, unbounded wait.
name="$skill_md's Draft PR step bounds the command that waits on the readied PR's checks itself: wait-ci.sh with no max-seconds or one under 600, and no gh pr checks after gh pr ready (#542, #544)"
problems=()

if step_or_problem '### 4. Draft PR' "whether the step's CI wait is bounded by its own command"; then
  commands="$(section_commands)"
  ready="$(line_of 'gh pr ready')"
  waits="$(line_of "$wait_ci_run")"
  if [[ -z "$ready" || -z "$waits" || "$waits" -le "$ready" ]]; then
    problems+=("$skill_md's Draft PR step runs no \$S/wait-ci.sh after gh pr ready, so there is no CI wait to bound")
  else
    slice="$(awk -v at="$waits" -v re="$wait_ci_run" 'NR == at { sub("^" re " *[^ ]+", ""); print $1 }' <<< "$commands")"
    [[ ! "$slice" =~ ^[0-9]+$ || "$slice" -lt 600 ]] ||
      problems+=("$skill_md's Draft PR step gives wait-ci.sh a slice of $slice seconds, longer than one Bash call lives")
  fi
  checks="$(awk -v a="${ready:-0}" 'NR > a && /^[^#]*gh pr checks/ { print; exit }' <<< "$commands")"
  [[ -z "$checks" ]] ||
    problems+=("$skill_md's Draft PR step still waits with gh pr checks after gh pr ready: $(printf '%.120s' "$checks")")
fi
report "$name"

# 21. The criterion, as one case (issue #542): a run that marks itself `done` and commits its
#     metrics before reading CI has already recorded a finish that a red check or a
#     `ci-timeout` bail then contradicts. Read off the section's command lines, in the order
#     the conductor types them.
name="$skill_md's Draft PR step waits on the readied PR's checks and reads their rollup before the done mark and the metrics commit (#542)"
problems=()

if step_or_problem '### 4. Draft PR' "whether the step reads CI before recording the run done"; then
  commands="$(section_commands)"
  for ci in "$wait_ci_run" "$rollup_read"; do
    ci_at="$(line_of "$ci")"
    if [[ -z "$ci_at" ]]; then
      problems+=("$skill_md's Draft PR step runs no $ci, so its order against the done mark could not be checked")
      continue
    fi
    for recorded in "$done_mark" "$metrics_commit"; do
      at="$(line_of "$recorded")"
      if [[ -z "$at" ]]; then
        problems+=("$skill_md's Draft PR step runs no $recorded, so the CI read's order against it could not be checked")
      elif [[ "$at" -le "$ci_at" ]]; then
        problems+=("$skill_md's Draft PR step runs $ci (command line $ci_at) after $recorded (command line $at)")
      fi
    done
  done
fi
report "$name"

# 22. The criterion, as one case (issue #542): a bail stated only in prose is one the conductor
#     has to infer, so the command block that waits must itself bail with `ci-timeout` before
#     the run marks itself done. Since #544 the pending check is `wait-ci.sh`'s to see, and a
#     check still pending past the deadline recorded across calls is its exit 2, so the bail is
#     keyed on that exit. A `#` comment in the block is not a command, so what follows one is
#     not read.
name="$skill_md's Draft PR command block bails with cause ci-timeout on wait-ci.sh's exit 2, before the done mark (#542, #544)"
problems=()

if step_or_problem '### 4. Draft PR' "whether the step's command block bails on a check still pending"; then
  commands="$(section_commands)"
  waits="$(line_of "$wait_ci_run")"
  done_at="$(line_of "$done_mark")"
  timeout="$(line_of '[^#]*ci-timeout')"
  if [[ -z "$waits" || -z "$done_at" ]]; then
    problems+=("$skill_md's Draft PR step runs no \$S/wait-ci.sh or no done mark, so where it bails on a pending check could not be checked")
  else
    [[ -n "$timeout" && "$timeout" -ge "$waits" && "$timeout" -lt "$done_at" ]] ||
      problems+=("no command line of $skill_md's Draft PR step bails with cause ci-timeout between \$S/wait-ci.sh and the done mark")
  fi
  plain="$(unmarked_records)"
  said="$(first_record "$plain" -F 'wait-ci.sh' -wF '2' -F 'ci-timeout')"
  [[ -n "$said" ]] ||
    problems+=("no instruction of $skill_md's Draft PR step says wait-ci.sh's exit 2 bails with cause ci-timeout")
fi
report "$name"

# 23. The criterion, as one case (issue #542): a red check is answered the way a red full run
#     is — a repair step the run resumes into — and that step's evidence is the failed log, so
#     the command block reads it, appends the step and commits the ledger before the run marks
#     itself done, and the prose says what the step quotes and where the run goes next.
name="$skill_md's Draft PR step answers a failed CI check with a repair step quoting the gh run view --log-failed FAIL line, committed, resuming the cycle loop (#542)"
problems=()

if step_or_problem '### 4. Draft PR' "whether the step repairs a failed CI check"; then
  commands="$(section_commands)"
  rollup="$(line_of "$rollup_read")"
  done_at="$(line_of "$done_mark")"
  log="$(line_of "$log_failed_read")"
  if [[ -z "$rollup" || -z "$done_at" ]]; then
    problems+=("$skill_md's Draft PR step reads no statusCheckRollup or runs no done mark, so where it repairs a failed check could not be checked")
  elif [[ -z "$log" || "$log" -le "$rollup" || "$log" -ge "$done_at" ]]; then
    problems+=("no command line of $skill_md's Draft PR step runs gh run view --log-failed between the rollup read and the done mark, so a failed check's log is never read")
  else
    added="$(awk -v from="$log" -v to="$done_at" 'NR > from && NR < to && /^[$]s\/add-ledger-step[.]sh [.]tdd\/issue-<n>[.]md / { print NR; exit }' <<< "$commands")"
    [[ -n "$added" ]] ||
      problems+=("no command line of $skill_md's Draft PR step appends a repair step with add-ledger-step.sh between the --log-failed read and the done mark")
    [[ -n "$added" ]] && ! awk -v from="$added" -v to="$done_at" 'NR > from && NR < to && /^git commit / { found = 1 } END { exit !found }' <<< "$commands" &&
      problems+=("no command line of $skill_md's Draft PR step commits the ledger after appending the repair step and before the done mark")
    plain="$(unmarked_records)"
    record="$(first_record "$plain" -F 'log-failed' -F 'repair step')"
    if [[ -z "$record" ]]; then
      problems+=("no record of $skill_md's Draft PR step says what the repair step a failed check appends carries from --log-failed")
    else
      grep -F 'fail -' > /dev/null <<< "$record" ||
        problems+=("$skill_md's Draft PR step never says the CI repair step quotes the failing suite's FAIL - line: $(printf '%.120s' "$record")")
      grep -E 'step 3|cycle loop' > /dev/null <<< "$record" ||
        problems+=("$skill_md's Draft PR step never says the run returns to the cycle loop after appending the CI repair step: $(printf '%.120s' "$record")")
    fi
  fi
fi
report "$name"

# 24. The criterion, as one case (issue #542): a second red CI result after a CI repair step
#     bails, the way a second red full run does, so the repair step is one more cycle and not a
#     loop. The bail is a command line after the failed log is read and before the run marks
#     itself done, and its cause is one `classify-bail.sh` classifies — the real script is
#     asked, so a token it does not know is a bail no human-facing label can name.
name="$skill_md's Draft PR step bails on a second red CI result after a CI repair step with a cause classify-bail.sh maps to system or process (#542)"
problems=()

if step_or_problem '### 4. Draft PR' "whether the step bails on a second red CI result"; then
  commands="$(section_commands)"
  log="$(line_of "$log_failed_read")"
  done_at="$(line_of "$done_mark")"
  if [[ -z "$log" || -z "$done_at" ]]; then
    problems+=("$skill_md's Draft PR step reads no --log-failed or runs no done mark, so where it bails on a second red CI result could not be checked")
  else
    cause="$(awk -v from="$log" -v to="$done_at" \
      'NR > from && NR < to && sub(/^[^#]*[$]s\/event[.]sh bail cause=/, "") && $1 != "ci-timeout" { print $1; exit }' <<< "$commands")"
    if [[ -z "$cause" ]]; then
      problems+=("no command line of $skill_md's Draft PR step bails (event.sh bail cause=…) between the --log-failed read and the done mark, so a second red CI result stops silently")
    else
      label="$("$ROOT/skills/tdd/scripts/classify-bail.sh" "$cause" 2> /dev/null)"
      [[ "$label" == system || "$label" == process ]] ||
        problems+=("$skill_md's Draft PR step bails on a second red CI result with cause $cause, which classify-bail.sh maps to no system or process label")
    fi
  fi
  plain="$(unmarked_records)"
  record="$(first_record "$plain" -F 'second red' -E 'red ci|ci (check|result)')"
  if [[ -z "$record" ]]; then
    problems+=("no record of $skill_md's Draft PR step says what a second red CI result after a repair step does")
  else
    grep -F 'bail' > /dev/null <<< "$record" ||
      problems+=("$skill_md's Draft PR step never says a second red CI result bails: $(printf '%.120s' "$record")")
  fi
fi
report "$name"

# 25. The criterion, as one case (issue #544): one Bash call is killed at 10 minutes, so the wait
#     is `wait-ci.sh` called again on its exit 3, never a loop in the block; and a legacy
#     StatusContext row has `.state` and no `.status`, so a pending test on `.status` alone
#     never sees it.
name="$skill_md's Draft PR step waits on CI by calling wait-ci.sh again on its exit 3, with no wait loop inside one Bash call and no pending test that reads .status alone (#544)"
problems=()

if step_or_problem '### 4. Draft PR' "how the step waits on the readied PR's CI"; then
  commands="$(section_commands)"
  ready="$(line_of 'gh pr ready')"
  wait_ci="$(line_of "$wait_ci_run")"
  done_at="$(line_of "$done_mark")"
  [[ -n "$ready" && -n "$wait_ci" && -n "$done_at" && "$wait_ci" -gt "$ready" && "$wait_ci" -lt "$done_at" ]] ||
    problems+=("no command line of $skill_md's Draft PR step runs \$S/wait-ci.sh between gh pr ready and the done mark")
  plain="$(unmarked_records)"
  said="$(first_record "$plain" -F 'wait-ci.sh' -wF '3' -E 'again')"
  [[ -n "$said" ]] ||
    problems+=("no instruction of $skill_md's Draft PR step says to call wait-ci.sh again on its exit 3")
  loop="$(first_record "$commands" -E '^(while|until) .*; *do( |$)|^sleep [0-9]|^gh pr checks .*--watch')"
  [[ -z "$loop" ]] ||
    problems+=("$skill_md's Draft PR command block waits inside one Bash call: $(printf '%.120s' "$loop")")
  status_only="$(first_record "$commands" -E '[.]status *==')"
  [[ -z "$status_only" ]] || grep -F '__typename' > /dev/null <<< "$status_only" ||
    problems+=("$skill_md's Draft PR command block tests a check pending by .status alone, so a legacy StatusContext row is never pending: $(printf '%.120s' "$status_only")")
fi
report "$name"

# 26. The criterion, as one case (issue #544): the conductor types a command block top to
#     bottom, so a bail line with the `done` mark or the `metrics:` commit after it in the same
#     block is a bail the run then walks past, recording itself done.
name="$skill_md's Draft PR step stops at a ci-timeout or ci-red bail: no done mark and no metrics commit follow it in its command block, and it goes to Bailing (#544)"
problems=()

if step_or_problem '### 4. Draft PR' "whether a CI bail stops the step"; then
  commands="$(section_commands)"
  followed="$(awk -v done_re="$done_mark" -v metrics_re="$metrics_commit" '
      /^```/ { block++; fenced = !fenced; next }
      !fenced { next }
      /^[^#]*[$]s\/event[.]sh bail cause=ci-(timeout|red)/ {
        match($0, /cause=ci-(timeout|red)/); bails[block] = bails[block] " " substr($0, RSTART + 6, RLENGTH - 6); next }
      bails[block] != "" && ($0 ~ ("^" done_re) || $0 ~ ("^" metrics_re)) {
        print "after" bails[block] ": " $0 }' <<< "$commands")"
  bailed="$(grep -F 'event.sh bail cause=ci-' <<< "$commands")"
  [[ -n "$bailed" ]] ||
    problems+=("$skill_md's Draft PR step runs no event.sh bail cause=ci-timeout or cause=ci-red, so whether a CI bail stops the step could not be checked")
  while IFS= read -r line; do
    [[ -n "$line" ]] || continue
    problems+=("$skill_md's Draft PR command block records the run finished after a CI bail — $(printf '%.160s' "$line")")
  done <<< "$followed"
  plain="$(unmarked_records)"
  said="$(first_record "$plain" -E 'ci-timeout|ci-red' -F 'bailing')"
  [[ -n "$said" ]] ||
    problems+=("no instruction of $skill_md's Draft PR step sends a ci-timeout or ci-red bail to Bailing")
fi
report "$name"

# 27. The criterion, as one case (issue #544): a second red is recognised by the repair step's
#     prose, so rewording that prose silently turns a second red into a first one; the mark is
#     the structural thing both the append and the test must share.
name="$skill_md's Draft PR step appends its CI repair step with a ⟦ci-repair⟧ text and recognises a second red by that mark, not by the repair step's prose (#544)"
problems=()
ci_repair_mark='⟦ci-repair⟧'

if step_or_problem '### 4. Draft PR' "how the step marks and recognises a CI repair step"; then
  commands="$(section_commands)"
  appended="$(first_record "$commands" -E '^[^#]*[$]s/add-ledger-step[.]sh ' -F 'ci failure')"
  if [[ -z "$appended" ]]; then
    problems+=("no command line of $skill_md's Draft PR step appends a CI repair step through add-ledger-step.sh")
  else
    grep -F "$ci_repair_mark" > /dev/null <<< "$appended" ||
      problems+=("$skill_md's Draft PR step appends its CI repair step without the $ci_repair_mark mark: $(printf '%.160s' "$appended")")
  fi
  red="$(first_record "$commands" -E '^[^#]*[$]s/event[.]sh bail cause=ci-red')"
  if [[ -z "$red" ]]; then
    problems+=("no command line of $skill_md's Draft PR step bails with cause ci-red, so how it recognises a second red could not be checked")
  else
    grep -F "$ci_repair_mark" > /dev/null <<< "$red" ||
      problems+=("$skill_md's Draft PR step recognises a second red CI result without the $ci_repair_mark mark: $(printf '%.160s' "$red")")
    grep -F 'fix the ci failure' > /dev/null <<< "$red" &&
      problems+=("$skill_md's Draft PR step recognises a second red CI result by the repair step's prose: $(printf '%.160s' "$red")")
  fi
fi
report "$name"

# 28. The criterion, as one case (issue #544): a push to a PR already out of draft starts a CI
#     run, so a push after the CI read with no `wait-ci.sh` after it is a run nothing reads.
name="$skill_md's Draft PR step leaves no CI run on the readied PR that nothing reads: every push after the CI read is followed by a wait-ci.sh call (#544)"
problems=()

if step_or_problem '### 4. Draft PR' "whether a push after the CI read has its run read"; then
  commands="$(section_commands)"
  read_at="$(line_of "$wait_ci_run")"
  if [[ -z "$read_at" ]]; then
    problems+=("$skill_md's Draft PR step runs no \$S/wait-ci.sh, so whether a later push has its CI run read could not be checked")
  else
    unread="$(awk -v from="$read_at" -v wait_re="^$wait_ci_run" '
        NR <= from { next }
        /^[^#]*([$]s\/push-branch[.]sh|git push)/ { pushed = $0; next }
        pushed != "" && $0 ~ wait_re { pushed = "" }
        END { print pushed }' <<< "$commands")"
    [[ -z "$unread" ]] ||
      problems+=("$skill_md's Draft PR step pushes after the CI read with no wait-ci.sh after it, leaving that push's CI run unread: $(printf '%.120s' "$unread")")
  fi
fi
report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
