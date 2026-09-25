#!/usr/bin/env bash
# Unit test for the shape of the refactor phase skills/tdd/SKILL.md prescribes. Like
# skill-suite-runs.test.sh and skill-leaf-launch.test.sh this suite belongs to no single
# script: its subject is the procedure, read as text, the way the session that follows it
# reads it. Zero-dependency plain-shell asserts, same idiom, picked up by `make test`'s
# glob by existing.
#
# Why this exists (issue #150): ADR-0010 ran one transform per leaf so a break could be
# traced to one change, and the conductor paid a cold `claude -p` start and a re-read of
# the spec and the touched files for every transform. Measured: #144's refactor loops plus
# verify-refactor took 2,147 of that run's 3,735 leaf-seconds, and one #137 step's five
# transforms took 49 minutes between them. Tracing a break to one change needs a commit per
# transform and a suite run between transforms; it does not need a leaf each.
#
# So the leaf now applies the whole budget and commits each transform itself, and the
# conductor's job changes from producing that result to CHECKING it. That check is the only
# thing standing between a killed or a disobedient leaf and a verify-refactor run on a state
# nobody looked at: the transform a dying leaf left on disk is uncommitted work no verifier
# has seen, and a commit since the green one whose subject is not `refactor:` is production
# code smuggled past the blind verifier of the phase that was supposed to be
# behavior-preserving. Neither is visible to verify-refactor, which judges the settled tree.
#
# Contract under test — nine criteria, the procedure, the account of it, what the leaf's
# report grows, what a growth budget too full to hold it means, whose proposals that
# growth carries, where an overfit flag is answered, which flag class grows the plan, where
# a beyond-spec flag goes instead, and how often one step may triangulate, one case each:
#   1. SKILL.md's Refactor section launches ONE leaf for the step rather than one per
#      transform; before verify-refactor it asks `git status --porcelain` and refuses to go
#      on while the tree is dirty; it asks the subjects of the commits since the green
#      commit and refuses to go on when one of them is not a `refactor:`; and it counts
#      those commits with `git rev-list --count` and narrates the count against the budget,
#      saying so when the count is over it rather than leaving the overrun out.
#   2. CONTEXT.md's **Cycle** entry and CLAUDE.md's three-budgets invariant describe that
#      same shape — one refactor leaf for the step, not a transformation per leaf — and
#      point a reader at the ADR that now records it.
#   3. SKILL.md's Refactor section passes the leaf's `NEW_STEP:` values to one
#      `add-ledger-step.sh … after '<STEP>'` call once verify-refactor has PASSed, and the
#      ledger those steps landed in rides the commit that clears the refactor-pending mark
#      (issue #361).
#   4. That section narrates `add-ledger-step.sh` exit 1 — the plan-growth budget is full, so
#      nothing was inserted and every value was filed under the ledger's `## Owed steps`
#      heading — as the owed steps it is, and does not bail on it (issue #361).
##   5. That same one call carries the passing verify-refactor verdict's own `NEW_STEP:`
#      values as well as the leaf's, so the unhandled edge case the refactor verifier now
#      proposes instead of REJECTing for reaches the plan (issue #362).
#   6. That section answers an `overfit` flag with one triangulating red/green pair inside
#      the step that raised it — no ledger step, no second `### ✅ Step done` — and then
#      resumes that step's own refactor loop with the budget it had left (issue #175).
#   7. That section amends the plan from an `uncovered-spec` flag and from **no other**
#      flag class (issue #175).
#   8. That section narrates a `beyond-spec` flag as a follow-up — in the `### 🛠️ Refactor`
#      comment and in the PR body — and neither plans nor builds it in this run (issue #175).
##   9. That section runs a step's triangulation at most once, narrating a flag raised inside
#      that triangulation's own refactor loop about the same code rather than triangulating
#      it a second time (issue #175).
#  10. That section's account of the leaf's report footer names exactly the report lines the
#      built refactor prompt asks for — no line the prompt does not emit, none it emits left
#      out (issue #175).
#
# Case 1 is one criterion — the conductor launches one leaf and checks its result instead of
# producing it — and its probes are its parts: a document that launched one leaf and then
# walked into verify-refactor over a dirty tree would be exactly as wrong as one that still
# looped leaves, and a reader repairing either repairs the same section. `problems` says
# which part is missing.
#
# Each probe accepts any wording that carries its fact — how the document phrases it is the
# writer's — but the refusals are asked of the text AROUND their own check rather than of
# the section at large: this section already tells the conductor to stop, to bail and to
# narrate, for the leaf's own exit 2 and for the triage's answers, and a probe that read the
# whole section would be answered by those sentences and pass a document that never says
# what a dirty tree means.
#
# Run: scripts/tests/skill-refactor-leaf.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
# The suite sits at skills/<skill>/scripts/tests, so four levels up is the repo root.
ROOT="$(cd "$HERE/../../../.." && pwd)"

# The document twice, the way skill-suite-runs.test.sh names its two: the path as every
# problem message spells it, and the same path resolved for the probes to open, so a message
# can never name a file the probes did not read.
skill_md="skills/tdd/SKILL.md"
skill_path="$ROOT/$skill_md"

# This repository's own two documents, named the same way and for the same reason. They are
# what a session is handed before it opens SKILL.md at all: CONTEXT.md says what a cycle is,
# CLAUDE.md says what may never be broken about the budgets. A message about one must never
# spell the other's path, which is why each is a pair rather than a path built at the call
# site.
context_md="CONTEXT.md"
context_path="$ROOT/$context_md"
claude_md="CLAUDE.md"
claude_path="$ROOT/$claude_md"

# The claim itself, spelled once. Three probes ask for it and they span all three documents —
# SKILL.md's Refactor section in case 1, CONTEXT.md's Cycle entry and CLAUDE.md's budget
# invariant in case 2. That they ask in the *same* words is the claim and not an incidental
# repetition: what any one of them fails with is that the procedure and the account of it can
# be reworded apart without either noticing, and three independent literals here would leave
# this suite free to drift exactly that way itself. The optional noun is whichever one a
# document puts between the number and the leaf; the alternation is the union of the three,
# because which of them a given document reaches for is the writer's business and not a fact
# about the phase.
one_leaf='(one|a single) (refactor |developer |transform )?leaf'

pass=0 fail=0

# report <name> — close a case whose probes collected into the `problems` array: an empty
# array is a pass, otherwise one FAIL line for the case and one indented line per problem,
# so the output says which half of the conductor's job broke rather than just that it did.
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

# plain — stdin with emphasis marks and backticks dropped and the case folded, because
# `refuse` and **refuse** are the same sentence. Borrowed from skill-suite-runs.test.sh,
# which reads this same section for what its leaf runs.
plain() {
  tr -d '*`' | tr '[:upper:]' '[:lower:]'
}

# The heading the section is found by, spelled once: the probes look for it and the three
# fail-closed messages below name it, and a suite where those are separate literals can be
# re-pointed at a renamed heading while still telling a reader it searched for the old one.
refactor_heading='#### Refactor'

# refactor_section — the lines after the first heading starting `$refactor_heading`, up to
# the next heading of any level, normalised through `plain` and joined onto one line: none of
# the probes below is about order, and a claim that wraps across two lines is still one
# claim. The prefix stops at the word the phase is named for, so a heading reworded from
# "Refactor loop" — which is what this issue stops it being — is still the section found.
refactor_section() {
  awk -v h="$refactor_heading" \
    'index($0, h) == 1 { inside = 1; next } inside && /^#/ { exit } inside' "$skill_path" |
    plain | tr '\n' ' '
}
section="$(refactor_section)"

# unreadable_section — true when there is no section to probe: a heading renamed away from
# `#### Refactor`, or one with nothing under it. Spelled once for the two cases that fail
# closed on it, so the normalisation — a section of nothing but spaces is as unreadable as an
# empty one — cannot be tightened in one case and left loose in the other, which is the state
# where "the phase is gone" reads as a pass in one of them.
unreadable_section() {
  [[ -z "${section// /}" ]]
}

# unreadable_problem <what-could-not-be-established> — the message the three fail-closed
# cases share, differing only in what each of them was about to ask. Spelled once for the
# same reason `unreadable_section` is: three copies of the sentence are three chances for one
# of them to keep naming a heading this suite has stopped looking for.
unreadable_problem() {
  printf "%s has no '%s' section to read — %s" "$skill_md" "$refactor_heading" "$1"
}

# unnamed_class_problem <class> <what-that-costs> — the message cases 6 and 7 share when the
# section never names the flag class they are about. Both are the same complaint — the leaf's
# FLAGS: line carries a class and the document ignores it, so the conductor routes the flag on
# its own judgement — and both end in the same measurement, the six `plan: amend` commits #175
# counted, which is what that judgement produced. Spelled once for the reason `unreadable_problem`
# above is: two copies drift, and a reader then gets two different accounts of what an unrouted
# flag costs. Only the class and the clause naming its own cost differ.
unnamed_class_problem() {
  printf "%s's Refactor section never names the %s class the leaf's FLAGS: line carries, so %s — the six plan: amend commits this issue counted" "$skill_md" "$1" "$2"
}

# windows <extended-regex> [radius] — the section text within <radius> characters either side
# of every match, one window per line, or nothing when there is none. The default 250 rather
# than a rounder, larger number because BSD grep — the one on the development machine this
# repository holds itself portable to — refuses an interval whose bound is over 255. A probe
# passes a narrower radius when 250 would reach a neighbouring bullet that answers its
# question for it. `win` and `wins` below are the two readings of this one answer, and they
# share it so that a radius clamped for BSD grep in one is clamped in the other too.
windows() {
  local radius="${2:-250}"
  grep -oE ".{0,$radius}$1.{0,$radius}" <<<"$section"
}

# win <extended-regex> [radius] — the first of those windows, or the empty string when there
# is none: the text a reader meets while working out what to do about that check. The reader
# consumes to EOF through the process substitution rather than a pipe, so `head` leaving early
# never lands on the writer as a SIGPIPE `pipefail` would hand up as the probe's answer (#422).
win() {
  head -1 < <(windows "$@")
}

# phrase <extended-regex> <text> — the first phrase of <text> that matches, or the empty
# string when nothing does. Every "is the superseded wording still here" probe below asks
# exactly that and then quotes the answer back in its complaint, so what they have in common
# — take the matches, keep the first, and keep the reader's exit off the writer's status
# (#422) — is written here rather than once per probe. `win` above is the other question:
# that one is about a match's surroundings, this one about the match itself.
phrase() {
  head -1 < <(grep -oE "$1" <<<"$2")
}

# wins <extended-regex> [radius] — every one of those windows rather than the first, joined
# onto one line. Case 6 asks about a word the section already uses for something else: the
# refactor template's account of itself says the leaf flags overfit code, and the PASS branch
# says the leaf was forbidden to generalize it, so the FIRST overfit in this section is never
# the routing rule that case is about. Taking only that one would fail a document that carries
# the rule perfectly well a paragraph further down.
wins() {
  windows "$@" | tr '\n' ' '
}

# either_order <a> <b> <gap> — one parenthesised regex for "<a> and <b> in the same clause",
# whichever of them the writer put first: `((<a>)<gap>(<b>)|(<b>)<gap>(<a>))`. Every proximity
# probe below wants that and nothing narrower — which way round a document says it is the
# writer's business — and each of them used to spell the mirror out by hand, where the two
# halves can drift apart unnoticed and the probe silently stops accepting one of the two orders.
# <gap> is passed rather than fixed because what counts as "the same clause" differs:
# `.{0,120}` reaches across a sentence boundary, `[^.]{0,200}` refuses to.
#
# Each operand is grouped HERE rather than trusted to arrive grouped, because an alternation
# passed in bare binds looser than the mirror this builds: `a|b` as <b> yields
# `(<a><gap>a|b|b<gap><a>)`, whose second branch is the bare word `b` and matches anywhere in
# the section — a probe that reads as a proximity check and is answered by one word. Grouping
# an operand that already carries its own parentheses is a no-op, so the call sites that spell
# them stay correct.
either_order() {
  printf '((%s)%s(%s)|(%s)%s(%s))' "$1" "$3" "$2" "$2" "$3" "$1"
}

# What a refusal looks like, spelled once for the two probes that ask for one. Both checks
# below — the dirty tree and the non-refactor: commit — owe the same thing beyond the git
# question itself: that the section says the answer STOPS the conductor rather than merely
# informing it, and either check reduced to advice is the same hole. Two literals for one
# question would let a probe be widened to accept a wording the other still rejects, and the
# next writer would then read two different answers to "what counts as refusing". The
# alternation is the union of how this document already writes it; `don.t` rather than
# `don't` because the apostrophe this repository types is a typographic one.
refusal='refus|do(es)? not (go on|continue|proceed)|don.t (go on|continue)|not continue|bail'

name="$skill_md's Refactor section launches one leaf per step and refuses verify-refactor over a dirty tree or a non-refactor: commit since the green commit, narrating the count against the budget"
problems=()

if unreadable_section; then
  # Fail closed: a renamed or emptied section is reported as unreadable rather than probed
  # as an empty string, which would let "the phase is gone" read as "the phase is right".
  problems+=("$(unreadable_problem "how the refactor leaf is launched and what is asked of its result could not be established")")
else
  # 1. One leaf for the step. Both faces, because either alone passes a document that is
  #    half-rewritten: it has to SAY one leaf, and it must no longer tell the conductor to
  #    come back round for the next transform.
  [[ "$section" =~ $one_leaf ]] ||
    problems+=("$skill_md's Refactor section never says one leaf applies the step's transforms, so the conductor is not told that the cold start and the spec re-read are paid once rather than once per transform")
  relaunch="$(phrase 'repeatedly|(each|every|the next) iteration' "$section")"
  [[ -z "$relaunch" ]] ||
    problems+=("$skill_md's Refactor section still launches a leaf per transform — it says '$relaunch' — so the leaf-per-transform cost this issue measured is still prescribed")

  # 2. A dirty tree. The transform a killed leaf left on disk is work no verifier has seen,
  #    and verify-refactor judges the settled tree, so it is the conductor or nothing.
  dirty="$(win 'git status --porcelain')"
  if [[ -z "$dirty" ]]; then
    problems+=("$skill_md's Refactor section never asks git status --porcelain, so the conductor walks into verify-refactor over whatever a killed leaf left uncommitted")
  else
    grep -qE "$refusal" <<<"$dirty" ||
      problems+=("$skill_md's Refactor section asks git status --porcelain without saying a non-empty answer stops it, so the check is asked and its answer is advisory")
  fi

  # 3. A commit since the green one that is not a refactor:. The green commit is the
  #    boundary because it is the one carrying the ledger tick (ADR-0007); a subject that is
  #    not `refactor:` in that range is production code the blind verifier of a
  #    behavior-preserving phase would never be shown.
  subjects="$(win '(--(format|pretty)=%s|subject)')"
  if [[ -z "$subjects" ]]; then
    problems+=("$skill_md's Refactor section never reads the subjects of the commits since the green commit, so a leaf that committed something other than a refactor: goes to verify-refactor unchallenged")
  else
    grep -qE 'refactor:' <<<"$subjects" ||
      problems+=("$skill_md's Refactor section reads commit subjects without saying they must be refactor:, so what the conductor is checking for is left to judgement")
    grep -qE "$refusal" <<<"$subjects" ||
      problems+=("$skill_md's Refactor section never says a non-refactor: commit since the green commit stops it, so the check has no branch and the run continues either way")
  fi

  # 4. The count, and the budget it is read against. `rev-list --count` is named rather than
  #    left to the conductor because the number narrated has to be the number of commits in
  #    the range, not the leaf's own account of what it applied.
  counted="$(win 'rev-list --count')"
  if [[ -z "$counted" ]]; then
    problems+=("$skill_md's Refactor section never counts the refactor: commits with git rev-list --count, so what it narrates is the leaf's word for what it did rather than what is in the history")
  else
    grep -qE 'budget|refactor [0-9k]+/' <<<"$counted" ||
      problems+=("$skill_md's Refactor section counts the refactor: commits without narrating them against the budget, so the cost axis this issue is about is not reported at all")
  fi

  # 5. And the count that is ABOVE the budget, which is the one a run needs to see: the
  #    budget reaches the leaf as a number now, so an overrun is the leaf ignoring it, and a
  #    narration that silently clamps to the budget hides exactly that.
  grep -qE 'overrun|over the budget|above the budget|exceed' <<<"$section" ||
    problems+=("$skill_md's Refactor section never says a count above the budget is narrated as an overrun, so a leaf that ran past the number it was given reads in the thread as one that did not")
fi

report "$name"

# records_of <path> — the document's bullets and paragraphs as records, one per line and
# normalised through `plain`: a record runs from a `- ` in column one (indented or not) or
# from the first line after a blank, up to the next such line or the next blank, with runs
# of whitespace collapsed so a claim wrapped across four lines still reads as one claim.
# The grammar skill-refactor-pending.test.sh reads these same two documents with, spelled
# the same way here so that "what a record is" does not get a second answer in this tree.
records_of() {
  awk '
    function flush() { if (rec != "") { gsub(/[[:space:]]+/, " ", rec); print rec } rec = "" }
    /^[0-9]+\. / || /^[[:space:]]*- / { flush(); rec = $0; next }
    /^[[:space:]]*$/ { flush(); next }
    rec == "" { rec = $0; next }
    { rec = rec " " $0 }
    END { flush() }' "$1" | plain
}

# record <path> <regex>... — the first record of <path> matching every <regex>, or the empty
# string when none does. Each record is found by what it SAYS and not by the heading it sits
# under or the position it holds: the glossary entry opens with its own name, and the
# invariant is the only record in CLAUDE.md naming all three budget variables. A document
# re-ordered or re-sectioned therefore still answers, and a document that stopped making the
# claim answers with nothing — which is the failure the case wants, not a silent pass.
record() {
  local path="$1"; shift
  local rec re ok
  while IFS= read -r rec; do
    ok=1
    for re in "$@"; do [[ "$rec" =~ $re ]] || { ok=0; break; }; done
    [[ "$ok" -eq 1 ]] && { printf '%s' "$rec"; return; }
  done < <(records_of "$path")
}

# adr_pointer <text> — the first `ADR-NNNN` reference in <text> that is not the superseded
# 0010, or the empty string when there is none. The number is compared rather than the
# string, because this repository writes the reference both ways — `(ADR-0007)` and
# `ADR 0016` — and a probe that matched on spelling would accept `adr 10` as a new record.
# `10#` forces decimal so the leading zeros of `0010` are not read as octal.
adr_pointer() {
  local ref digits
  while IFS= read -r ref; do
    digits="${ref##*[!0-9]}"
    [[ "$((10#$digits))" -eq 10 ]] && continue
    printf '%s' "$ref"
    return
  done < <(grep -oE 'adr[- ]?[0-9]+' <<<"$1")
}

# 2. One criterion — the account of the cycle this repository hands the next agent describes
#    the shape the procedure now runs — and so one case. Case 1 pins SKILL.md, the document
#    the conductor executes; this one pins the two documents a human or an agent reads to
#    find out what the conductor does, before either has opened SKILL.md. As they stand both
#    describe ADR-0010's shape: CONTEXT.md's Cycle entry says "one behavior-preserving
#    transformation per leaf, suite-gated, until none remain", and CLAUDE.md's invariant
#    explains VERI_REFACTOR_BUDGET by "a refactor leaf asked for one always finds one" — a
#    sentence that is only true of a leaf asked for a single transform. Prose that
#    contradicts the procedure is worse than prose that says nothing, because it is the
#    account that is trusted: an agent that re-derives the old shape from it puts the loop
#    back, and reads the conductor's one-leaf launch as the bug.
#
#    Both halves in one case, because it is one fact owed by two records and any repair to it
#    is one edit to each — the same reason skill-refactor-pending.test.sh asks its ledger
#    invariant and its glossary entry together. `problems` says which record is short of it.
#
#    The superseding ADR is asked for here as the pointer these two records carry, and that
#    is the whole of what this suite can ask about it. The record itself is a file under
#    docs/adr/, and a suite in this directory may not name a path there: no-docs-reads.test.sh
#    fails `make test` for it, because that target is the baseline preflight reads and the one
#    both blind verifiers run, and a record in that tree must never be able to turn a
#    development run red. The ADR set has a reader of its own on the other lane's cadence —
#    docs/tests/docs-gap-adr.test.sh, run by `make docs-test`. So what is established from
#    here is that a reader of either record is sent to a decision record that is not the
#    superseded 0010; that the file it names says what it must is that suite's question.
name="$context_md's Cycle entry and $claude_md's budget invariant describe one refactor leaf per step and point at the ADR that records it"
problems=()

# The glossary entry, by its own heading line — `**Cycle**:` opens the record, and a bare
# `cycle` anchor would match the entries around it that use the word in passing.
cycle="$(record "$context_path" '^cycle:')"
# The invariant, by the three variables it is the invariant ABOUT. Naming all three is what
# makes it unique: VERI_REFACTOR_BUDGET alone appears in four other records of that document.
invariant="$(record "$claude_path" 'veri_stuck_retries' 'revise_budget' 'veri_refactor_budget')"

# Fail closed on either record being unreadable, the way case 1 does on a renamed section: a
# glossary entry that was deleted must not read as one that was updated.
if [[ -z "$cycle" ]]; then
  problems+=("$context_md has no Cycle glossary entry to read — what this repository tells the next agent a refactor step is could not be established")
else
  [[ "$cycle" =~ $one_leaf ]] ||
    problems+=("$context_md's Cycle entry never says the refactor step is one leaf, so the glossary still describes the cycle as spending a leaf per transform")
  stale_cycle="$(phrase 'per leaf|until none remain|per leaf invocation' "$cycle")"
  [[ -z "$stale_cycle" ]] ||
    problems+=("$context_md's Cycle entry still says '$stale_cycle', so the entry a reader learns the cycle from is ADR-0010's shape and contradicts the procedure SKILL.md now runs")
fi

if [[ -z "$invariant" ]]; then
  problems+=("$claude_md has no invariant naming all three budgets to read — what VERI_REFACTOR_BUDGET is said to bound could not be established")
else
  [[ "$invariant" =~ $one_leaf ]] ||
    problems+=("$claude_md's budget invariant never says one leaf spends the step's refactor budget, so the cost axis is still explained as a leaf per transform")
  stale_invariant="$(phrase 'asked for one always finds one|one transform per leaf|a transform per leaf' "$invariant")"
  [[ -z "$stale_invariant" ]] ||
    problems+=("$claude_md's budget invariant still explains the budget by '$stale_invariant', which is only true of a leaf asked for a single transform")
fi

# The pointer, asked of the pair rather than of each: what the criterion owes a reader is
# that the records name the decision, and a citation in one of them is a reader sent there.
[[ -n "$(adr_pointer "$cycle $invariant")" ]] ||
  problems+=("neither $context_md's Cycle entry nor $claude_md's budget invariant names an ADR other than the superseded 0010, so nothing in either record points a reader at the decision that replaced one transform per leaf")

report "$name"

# The invocation the growth of the plan is found by, spelled once for the three probes that
# ask for it — case 3 counts them, case 3 and case 5 each read the window around the one.
# `$s` and not `$S` because `plain` folds the section's case; the `$` and the `.` are escaped
# because this is an extended regex and not a path. A suite where the three were separate
# literals could be re-pointed at a renamed script in one probe and go on telling a reader it
# looked for the old one in the other two.
add_ledger_step='\$s/add-ledger-step\.sh'

# 3. One criterion — the refactor leaf's `NEW_STEP:` lines become steps in the plan — and so
#    one case. Case 1 pins what the conductor checks about the leaf's commits; this pins what
#    it does with the one part of the leaf's report that is not a leftover and not a
#    transform: the behaviour-level criterion that would force the general implementation of
#    overfit code the leaf was forbidden to generalize itself. ADR-0009 promised the refactor
#    leaf "confirms the plan contains" such a step, and until this issue nothing added one:
#    the line was narrated into the thread and the plan stayed as it was, so the triangulation
#    the leaf refused to do by hand was owed to nobody.
#
#    The insertion and the commit are one criterion for the same reason the append and its
#    commit are one in skill-refactor-owed.test.sh: resume reads the COMMITTED ledger, so a
#    step inserted into a file nothing commits is a step the next run never sees, and it is
#    the refactor-pending clear that is the one commit a completed step always makes.
#
#    `one` call is asked as the number of `$S/add-ledger-step.sh` invocations the section
#    holds, because the script takes every text at once and reads the growth budget per call:
#    a call per value would refuse the third `NEW_STEP:` line of a step under the default
#    `VERI_STEP_GROWTH` while the one call this criterion asks for either fits them all or
#    files them all as owed. A mention that is not an invocation — the script named in a
#    sentence about what its exit 1 means — carries no `$S/` and is not counted.
name="$skill_md's Refactor section passes the leaf's NEW_STEP: values to one add-ledger-step.sh call after the step, and commits the grown ledger with the refactor-pending clear"
problems=()

if unreadable_section; then
  # Fail closed, the same way case 1 does: a renamed or emptied section is unreadable, not
  # silently right.
  problems+=("$(unreadable_problem "what becomes of the leaf's NEW_STEP: lines could not be established")")
else
  calls="$(grep -oE "$add_ledger_step" <<<"$section" | grep -c '')"
  if [[ "$calls" -eq 0 ]]; then
    problems+=("$skill_md's Refactor section never runs add-ledger-step.sh, so the leaf's NEW_STEP: lines are narrated and nothing grows the plan — the triangulating step the leaf refused to write by hand is owed to nobody")
  elif [[ "$calls" -gt 1 ]]; then
    problems+=("$skill_md's Refactor section runs add-ledger-step.sh $calls times, so a step's NEW_STEP: values are inserted a call at a time and the growth budget is read once per value rather than once for the step")
  else
    added="$(win "$add_ledger_step")"
    grep -qE 'new_step' <<<"$added" ||
      problems+=("$skill_md's Refactor section runs add-ledger-step.sh without saying the texts are the leaf's NEW_STEP: values, so what the inserted step says is left to judgement")
    grep -qE "after ['\"]?<step>" <<<"$added" ||
      problems+=("$skill_md's Refactor section runs add-ledger-step.sh without anchoring the insertion after the step just refactored, so the triangulating step lands somewhere other than next to the code it triangulates")
  fi

  # And the commit. `clear-refactor-pending.sh` is the anchor for the same reason
  # skill-refactor-owed.test.sh uses it: that clear is the one commit a completed step always
  # makes, and a ledger grown but not committed is a plan the next run never reads.
  cleared="$(win 'clear-refactor-pending\.sh')"
  if [[ -z "$cleared" ]]; then
    problems+=("$skill_md's Refactor section never clears the refactor-pending mark, so the commit the grown ledger is supposed to ride does not exist to be read for")
  else
    grep -qE 'add-ledger-step' <<<"$cleared" ||
      problems+=("$skill_md's Refactor section commits the cleared ledger without the steps add-ledger-step.sh inserted into it, so a step added for triangulation is lost the moment the run is resumed from the committed ledger")
  fi
fi

report "$name"

# 4. One criterion — a plan-growth budget that cannot hold the leaf's `NEW_STEP:` values is
#    not a run-ending fault — and so one case. `add-ledger-step.sh` exit 1 is the fifth
#    axis's refusal: nothing is inserted, every text is appended as a plain bullet under the
#    ledger's trailing `## Owed steps` heading, and `render-pr-body.sh` puts that heading in
#    front of the human who decides the merge. The step is therefore recorded, just not
#    planned — which is a narration, not a bail. A section that left exit 1 unspoken leaves
#    the conductor to read a non-zero exit as the failure every other non-zero exit in this
#    phase is, and a run whose refactor verified PASS would end on the one answer that means
#    the plan grew past its budget.
#
#    Asked of the clause itself and not of the section at large, for the reason the refusals
#    in case 1 are: this section already says bail four times over, for the leaf's exit 2,
#    for a malformed verdict and for an exhausted revise budget, and a probe reading the
#    whole section would be answered by those and pass a document that bails here too.
name="$skill_md's Refactor section narrates add-ledger-step.sh exit 1 as owed steps and does not bail on it"
problems=()

if unreadable_section; then
  # Fail closed, the same way cases 1 and 3 do: a renamed or emptied section is unreadable,
  # not silently right.
  problems+=("$(unreadable_problem "what the conductor does when the plan-growth budget cannot hold the leaf's NEW_STEP: values could not be established")")
else
  # The claim, found by what it says rather than by where it sits: an exit 1 spoken of in
  # the same clause as the owed steps it files. 120 characters either way is about one
  # clause, which is what keeps this from matching the other two exit 1s this section
  # carries — the rejected push's and the REJECT verdict's, neither of which has the word
  # `owed` anywhere near it.
  owed_claim="$(either_order 'exit 1' 'owed' '.{0,120}')"
  if ! grep -qE "$owed_claim" <<<"$section"; then
    problems+=("$skill_md's Refactor section never says what add-ledger-step.sh exit 1 means, so a conductor meeting the plan-growth budget's refusal is left to read it as the failure every other non-zero exit in this phase is, and the NEW_STEP: values it filed as owed steps go unmentioned")
  else
    # And that the clause does not end the run. The window is the claim with about a clause
    # either side of it, not the section: `win`'s default 250 would reach the REJECT and
    # killed-stuck bullets from the end of the PASS one, and this probe would then be
    # answered by a bail that is not this one's.
    clause="$(win "$owed_claim" 150)"
    bailed="$(phrase 'bail|abort' "$clause")"
    [[ -z "$bailed" ]] ||
      problems+=("$skill_md's Refactor section says '$bailed' where it narrates add-ledger-step.sh exit 1, so a ledger whose growth budget is full ends a run whose step verified PASS — the owed steps are recorded and the plan simply did not grow, which is nothing to stop for")
  fi
fi

report "$name"

# 5. One criterion — the passing verify-refactor verdict's `NEW_STEP:` values join the leaf's
#    in that same one call — and so one case. Issue #362 stops the refactor verifier
#    REJECTing an unhandled edge case the spec implies: handling one changes behaviour, which
#    the revise leaf is forbidden to do untested, so the verifier proposes it as a `NEW_STEP:`
#    line before the final `VERDICT:`/`REASON:` pair instead. A proposal nothing reads is the
#    same nothing case 3 was written against — the line narrated into the thread and the plan
#    left as it was — so the verdict's values go where the leaf's already go: the one
#    `add-ledger-step.sh … after '<STEP>'` call the PASS branch makes. One call and not a
#    second of its own, because the script reads `VERI_STEP_GROWTH` once per call, and two
#    calls would let the verifier's proposals be refused for a budget the leaf's had already
#    spent.
#
#    Asked of the text around that call rather than of the section at large, the way case 1
#    asks its refusals: this section names verify-refactor throughout — launching it, waiting
#    on it, branching on its verdict — and a probe reading the whole section would be answered
#    by one of those sentences and pass a document where the verifier's proposals still reach
#    nobody.
name="$skill_md's Refactor section passes the passing verify-refactor verdict's NEW_STEP: values to the same add-ledger-step.sh call as the leaf's"
problems=()

if unreadable_section; then
  # Fail closed, the same way cases 1, 3 and 4 do: a renamed or emptied section is
  # unreadable, not silently right.
  problems+=("$(unreadable_problem "what becomes of the verify-refactor verdict's NEW_STEP: lines could not be established")")
else
  added="$(win "$add_ledger_step")"
  if [[ -z "$added" ]]; then
    problems+=("$skill_md's Refactor section never runs add-ledger-step.sh, so the verifier's NEW_STEP: proposals are narrated and nothing grows the plan — the edge case it stopped REJECTing for is proposed to nobody")
  else
    grep -qE 'verif|verdict' <<<"$added" ||
      problems+=("$skill_md's Refactor section runs add-ledger-step.sh over the leaf's NEW_STEP: values alone, so the passing verify-refactor verdict's own values never reach the ledger — the unhandled edge case the verifier stopped REJECTing for is proposed to nobody")
  fi
fi

report "$name"

# 6. One criterion — an `overfit` flag is answered inside the step that raised it — and so
#    one case. Issue #175 measured what the absence costs: six `plan: amend` commits on
#    `origin/main` were made from refactor flags, and #107's three ran from 01:31 to past
#    03:06 for three one-line `fix:` commits and seventeen `refactor:` ones, because a step
#    made from a flag has a refactor loop of its own and that loop flagged the next sibling.
#    The flag now carries its class, so `overfit` — the code passes this step's test without
#    implementing the behaviour this step's criterion states — is this step's own debt: one
#    triangulating red and green pair here, and then the refactor loop this step was already
#    in, with what was left of its budget. Its four probes are its parts, and a document
#    missing any one of them routes the flag somewhere it costs a whole step: a pair with no
#    "and no new ledger line" is the amendment this issue is against, and a pair that never
#    comes back is a refactor loop abandoned mid-budget.
#
#    Asked of the text around the word `overfit` rather than of the section at large — the
#    way case 1 asks its refusals — because this section already talks about triangulation,
#    about ledger steps and about what a step owes, and a probe reading the whole of it would
#    be answered by the PASS branch's `add-ledger-step.sh` sentences and pass a document that
#    still turns every flag into a plan amendment.
# The words this document denies with, spelled once for the three probes that ask for one —
# case 6's two and case 8's — the way `refusal` above is spelled once for case 1's two. All
# three owe the same thing beyond the verb or noun each names: that the section says the flag
# does NOT buy it. Two lists for that one question is how they drift — case 8's carried
# `neither` where case 6's carried `without` — and a probe widened on its own then accepts a
# wording the others still reject, leaving the next writer several answers to "what counts as
# denying it". The alternation is the union of how this document already writes a denial.
denial_word='no|never|neither|without|not'

# ...and how far from its noun it may sit, for the two probes of case 6 that ask for a noun
# phrase: the gap is `[^.]` so the denial and its noun have to sit in one sentence rather than
# a paragraph apart. Case 8 denies a VERB, and spells the adjacency it needs at its own probe,
# where the reason for it is written.
denial="($denial_word)[^.]{0,80}"

# What growing the plan looks like, spelled once for the two probes that name it from opposite
# sides: case 6 asks that an overfit flag is DENIED it, case 7 that an uncovered-spec flag is
# the one class granted it. That is one question — which words does this document use for a
# step the plan gains — and two literals for it would let one side accept a wording the other
# still rejects, so a document could read as both "overfit is denied an amendment" and
# "uncovered-spec is never granted one" over the very same sentence, which is the routing
# neither case would then be checking. The alternation is the union of how this document
# already writes it, `add-ledger-step` among them because the script's own name is one of the
# ways it says so.
amendment='amend|ledger (step|line)|add-ledger-step|grow'

name="$skill_md's Refactor section answers an overfit flag with one triangulating red/green pair inside the step, adding no ledger step and no second step-done, and resumes that step's refactor loop with the budget it had left"
problems=()

if unreadable_section; then
  # Fail closed, the same way cases 1, 3, 4 and 5 do: a renamed or emptied section is
  # unreadable, not silently right.
  problems+=("$(unreadable_problem "what the conductor does with an overfit flag could not be established")")
else
  flagged="$(wins 'overfit')"
  if [[ -z "$flagged" ]]; then
    problems+=("$(unnamed_class_problem overfit "the conductor branches on its own judgement rather than on the leaf's word")")
  else
    # a. The pair itself, and that it is verified: a triangulating test written inside the
    #    step is still a red and a green the blind verifiers see, which is what tells this
    #    apart from the leaf hand-generalizing the code it flagged.
    grep -qE "$(either_order 'triangulat[a-z]*' 'verify-(red|green)' '[^.]{0,200}')" <<<"$flagged" ||
      problems+=("$skill_md's Refactor section never says an overfit flag is answered by a triangulating red and green pair, so the case the leaf named is either built unverified or not built at all")

    # b. And that the pair is all it is. The whole cost this issue measured is the flag
    #    becoming a ledger step, so a document that runs the pair AND amends the plan has
    #    paid for it twice.
    grep -qE "$denial($amendment)" <<<"$flagged" ||
      problems+=("$skill_md's Refactor section answers an overfit flag without saying the plan does not grow for it, so the triangulation becomes a ledger step with a refactor loop of its own — the #107 chain this issue is against")
    grep -qE "$denial(second )?step.done" <<<"$flagged" ||
      problems+=("$skill_md's Refactor section answers an overfit flag without saying the step is not mirrored done a second time, so one step reports itself finished twice and the issue thread stops saying how many steps ran")

    # c. And that the step goes back to where it was. The refactor loop was interrupted by
    #    the flag, not ended by it, and a loop resumed with a fresh budget would let one flag
    #    buy a second step's worth of transforms.
    grep -qE "$(either_order '(resum|return|back)' 'budget' '[^.]{0,160}')" <<<"$flagged" ||
      problems+=("$skill_md's Refactor section never says the step resumes its own refactor loop with the budget it had left after the triangulation, so the tidying the flag interrupted is either abandoned or restarted with a budget the step has already spent")
  fi
fi

report "$name"

# 7. One criterion — the plan grows from an `uncovered-spec` flag and from no other class —
#    and so one case. The classes the leaf now reports are three, and only one of them is a
#    step the plan is missing: `uncovered-spec` names a behaviour the spec requires that no
#    ledger step covers, which is the gap the planner is already asked to catch at scoping
#    time. `overfit` is this step's own debt (case 6) and `beyond-spec` is not this run's
#    work at all, so a document that amends the plan from a flag without saying which class
#    buys it is the document #175 measured: six `plan: amend` commits on `origin/main`, none
#    of them behaviour the issue's spec asked for. Two probes, because either alone passes a
#    half-written section — one that names the class but not that it is the only one still
#    lets every flag grow the plan, and one that says "only this class" without saying which
#    leaves the conductor to pick.
#
#    Asked of the text around `uncovered-spec` rather than of the section at large, the way
#    cases 1 and 6 ask theirs: this section already runs `add-ledger-step.sh` for the leaf's
#    and the verifier's `NEW_STEP:` values, and a probe reading the whole section would be
#    answered by those sentences and pass a document that never routes a flag by its class.
name="$skill_md's Refactor section amends the plan from an uncovered-spec flag and from no other flag class"
problems=()

if unreadable_section; then
  # Fail closed, the same way cases 1, 3, 4, 5 and 6 do: a renamed or emptied section is
  # unreadable, not silently right.
  problems+=("$(unreadable_problem "which flag class grows the plan could not be established")")
else
  uncovered="$(wins 'uncovered-spec')"
  if [[ -z "$uncovered" ]]; then
    problems+=("$(unnamed_class_problem uncovered-spec "no flag is routed to a plan amendment by its class and the conductor amends from whichever flag it reads")")
  else
    # a. That class becomes a plan amendment: the one flag the plan is allowed to grow for.
    grep -qE "$amendment" <<<"$uncovered" ||
      problems+=("$skill_md's Refactor section names the uncovered-spec class without saying it is what amends the plan, so a behaviour the spec requires and no step covers is narrated and never planned")

    # b. And that it is the only one. Without that, the class is named and every other flag
    #    still buys a step of its own, which is the cost this issue is against.
    grep -qE '(only|alone|no other|the one (flag|class))' <<<"$uncovered" ||
      problems+=("$skill_md's Refactor section amends the plan from an uncovered-spec flag without saying that no other flag class does, so an overfit or beyond-spec flag still becomes a ledger step with a refactor loop of its own")
  fi
fi

report "$name"

# 8. One criterion — a `beyond-spec` flag is narrated as a follow-up and built by nobody in
#    this run — and so one case. It is the third of the three classes, and the only one that
#    is not this run's work at all: it names an input class or an edge the issue's spec never
#    asked for, so a step made from it builds behaviour no criterion of the issue states and
#    no verifier can judge against the spec. Narration is therefore the whole of what it
#    earns, and narration in the two places a human actually reads: the `### 🛠️ Refactor`
#    comment, which is where the step accounts for itself while the run is live, and the PR
#    body, which is what the human deciding the merge reads afterwards. A flag narrated only
#    in a comment is lost by the time the merge is decided, which is how a follow-up nobody
#    files becomes the plan amendment #175 measured.
#
#    Three probes, because each names a different way the class is mishandled and a document
#    missing one is wrong in that way: no Refactor comment and the flag never surfaces during
#    the run, no PR body and it never outlives it, no denial and it is narrated AND planned,
#    which costs exactly what the amendment cost.
#
#    Asked of the text around `beyond-spec` rather than of the section at large, the way cases
#    1, 6 and 7 ask theirs: this section already narrates transforms, counts and leftover
#    candidates into that same comment and that same PR body, and a probe reading the whole
#    of it would be answered by those sentences and pass a document that never says where a
#    beyond-spec flag goes.
name="$skill_md's Refactor section narrates a beyond-spec flag as a follow-up in the Refactor comment and in the PR body, planning and building neither"
problems=()

if unreadable_section; then
  # Fail closed, the same way cases 1, 3, 4, 5, 6 and 7 do: a renamed or emptied section is
  # unreadable, not silently right.
  problems+=("$(unreadable_problem "where a beyond-spec flag goes could not be established")")
else
  beyond="$(wins 'beyond-spec')"
  if [[ -z "$beyond" ]]; then
    problems+=("$(unnamed_class_problem beyond-spec "the class the spec never asked for is routed on the conductor's own judgement, the way the classes were before the leaf carried them")")
  else
    # a. It is narrated as a follow-up, in the comment the step accounts for itself in.
    grep -qE "$(either_order 'follow.?up' '(🛠️ )?refactor comment|narrat|post' '[^.]{0,200}')" <<<"$beyond" ||
      problems+=("$skill_md's Refactor section never says a beyond-spec flag is narrated as a follow-up in the 🛠️ Refactor comment, so what the leaf found is neither built nor said out loud and the run ends having dropped it")

    # b. And it outlives the run, in the body the human deciding the merge reads.
    grep -qE 'pr body|body of the (draft )?pr|pull request body' <<<"$beyond" ||
      problems+=("$skill_md's Refactor section never carries a beyond-spec flag into the PR body, so the follow-up is buried in one step's comment and the human deciding the merge never sees it")

    # c. And narration is ALL it earns. A flag narrated and also planned has cost exactly
    #    what this issue measured, whatever the comment said about it.
    #
    #    Asked with the denial word ADJACENT to the verb rather than through `$denial`'s
    #    `[^.]{0,80}` gap, which case 6 uses. The gap is right for those two — what
    #    they deny is a noun phrase a writer may put words in front of — but here it reads
    #    the bullet's own rationale instead of its rule: "without costing it a step: one
    #    made from a beyond-spec flag would build behaviour no criterion of the issue
    #    states" puts `without` within eighty characters of `build`, so the probe was
    #    answered by the sentence explaining WHY the class is not planned and passed a
    #    document whose clause granted both. The denial this case is about is written
    #    against the verb itself, so that is what it matches.
    grep -qE "($denial_word) (planned|plan|built|build)" <<<"$beyond" ||
      problems+=("$skill_md's Refactor section narrates a beyond-spec flag without saying it is neither planned nor built in this run, so the run still builds behaviour the issue's spec never asked for")
  fi
fi

report "$name"

# 9. One criterion — a step triangulates at most once — and so one case. Case 6 lets an
#    overfit flag interrupt the step for a triangulating pair and then resume that step's own
#    refactor loop, and that resumed loop is another refactor leaf reading the same files: it
#    can flag the same code again, and a document that answers the second flag the way it
#    answered the first has rebuilt the chain #107 paid for — three amendments from 01:31 to
#    past 03:06, each one flagged by the refactor loop of the step the previous one created,
#    only now inside a single step instead of across the ledger. So the flag raised inside a
#    triangulation's own refactor loop about the same code is narrated, like a beyond-spec
#    one at case 8, and never triangulated a second time.
#
#    Two probes, because either alone passes a half-written section: a ceiling with nothing
#    said about what happens to the flag that hits it leaves the conductor to drop it
#    silently, and "narrate the second flag" without the ceiling is advice a conductor that
#    triangulates again has not disobeyed.
#
#    Asked of the text around `triangulat` rather than of the section at large, the way cases
#    1, 6, 7 and 8 ask theirs: this section already narrates counts, leftovers and flags into
#    the `### 🛠️ Refactor` comment, and a probe reading the whole of it would be answered by
#    those sentences and pass a document that never puts a ceiling on the triangulation.
name="$skill_md's Refactor section runs a step's triangulation at most once, narrating a flag raised inside that triangulation's own refactor loop about the same code rather than triangulating it again"
problems=()

if unreadable_section; then
  # Fail closed, the same way cases 1, 3, 4, 5, 6, 7 and 8 do: a renamed or emptied section
  # is unreadable, not silently right.
  problems+=("$(unreadable_problem "whether a step's triangulation runs more than once could not be established")")
else
  triangulation="$(wins 'triangulat')"
  if [[ -z "$triangulation" ]]; then
    problems+=("$skill_md's Refactor section never mentions triangulation at all, so there is no ceiling on it to read and an overfit flag raised inside one is answered with another")
  else
    # a. The ceiling itself: once per step, not once per flag.
    grep -qE "at most once|only once|once (per|a) step|(${denial_word}) ((a )?(second|further|another) (triangulat[a-z]*|time)|triangulat[a-z]* (it |them )?(again|a second time))" <<<"$triangulation" ||
      problems+=("$skill_md's Refactor section puts no ceiling on a step's triangulation, so the loop it resumes can flag the same code again and buy a second pair — the #107 chain this issue is against, moved inside one step")

    # b. And what the flag that hits the ceiling earns instead. Narration, the way a
    #    beyond-spec flag earns it at case 8: the second flag is said out loud, not dropped.
    grep -qE "$(either_order 'narrat' '(again|a second (time|triangulation)|same code)' '[^.]{0,200}')" <<<"$triangulation" ||
      problems+=("$skill_md's Refactor section never says a flag raised inside a triangulation's own refactor loop about the same code is narrated, so what the second flag found is dropped without a word")
  fi
fi

report "$name"

# 10. One criterion — SKILL.md describes the refactor leaf's report footer as the built prompt
#     actually writes it — and so one case. The conductor reads that footer through SKILL.md's
#     account of it, never through the template: a line the account names and the prompt never
#     asks for is a line the conductor waits on and never gets, and a line the prompt asks for
#     and the account never names is one the leaf writes and nothing reads. Issue #175 moved
#     the overfit finding from `NEW_STEP:` onto a classed `FLAGS:` line, and it is the account
#     that lagged: the prompt said `FLAGS:` while SKILL.md still said `NEW_STEP:`.
#
#     So the case asks the builder itself for the prompt, the way the conductor does, and
#     compares the labels of that prompt's report lines with the labels SKILL.md's account of
#     the footer names — both directions, since either gap is its own failure. The account is
#     the prose after the first mention of `.tdd/develop-refactor.out` outside a fenced block,
#     up to the next numbered item: the launch command also names that file, inside a fence,
#     and says nothing about what the leaf's report contains.
name="$skill_md's Refactor section names exactly the report lines the built refactor prompt asks the leaf for"
problems=()

spec_tmp="$(mktemp)"
echo "spec" >"$spec_tmp"
emitted="$("$ROOT/skills/tdd/scripts/build-develop-prompt.sh" refactor "$spec_tmp" "step" "make test" "a.sh" |
  sed -nE 's/^([A-Z][A-Z_]+):.*/\1/p' | sort -u)"
rm -f "$spec_tmp"

footer="$(awk -v h="$refactor_heading" '
  index($0, h) == 1 { inside = 1; next }
  inside && /^#/ { exit }
  inside && /^[[:space:]]*```/ { fenced = !fenced; next }
  inside && !fenced && !found && index($0, "develop-refactor.out") { found = 1 }
  found && /^[0-9]+\. / { exit }
  found' "$skill_path" | tr -d '*`' | tr '\n' ' ')"
footer="${footer#*develop-refactor.out}"
named="$(grep -oE '[A-Z][A-Z_]+:' <<<"$footer" | tr -d ':' | sort -u)"

if [[ -z "$emitted" ]]; then
  problems+=("build-develop-prompt.sh refactor printed no report line, so there is nothing to hold $skill_md's account against")
elif [[ -z "${footer// /}" || -z "$named" ]]; then
  problems+=("$(unreadable_problem "no account of the leaf's report after .tdd/develop-refactor.out could be found")")
else
  for label in $named; do
    grep -qxF "$label" <<<"$emitted" ||
      problems+=("$skill_md's Refactor section says the leaf's report carries $label:, a line the built refactor prompt never asks for, so the conductor reads for a line no leaf writes")
  done
  for label in $emitted; do
    grep -qxF "$label" <<<"$named" ||
      problems+=("$skill_md's Refactor section never names $label:, a line the built refactor prompt asks the leaf for, so the leaf writes it and nothing in the procedure reads it")
  done
fi

report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
