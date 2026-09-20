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
# Contract under test — three criteria, the procedure, the account of it, and what the
# leaf's report grows, one case each:
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

# refactor_section — the lines after the first heading starting `#### Refactor`, up to the
# next heading of any level, normalised through `plain` and joined onto one line: none of
# the probes below is about order, and a claim that wraps across two lines is still one
# claim. The prefix stops at the word the phase is named for, so a heading reworded from
# "Refactor loop" — which is what this issue stops it being — is still the section found.
refactor_section() {
  awk -v h='#### Refactor' \
    'index($0, h) == 1 { inside = 1; next } inside && /^#/ { exit } inside' "$skill_path" |
    plain | tr '\n' ' '
}
section="$(refactor_section)"

# win <extended-regex> — the section text within 250 characters either side of the first
# match, or the empty string when there is none: the text a reader meets while working out
# what to do about that check. 250 rather than a rounder, larger number because BSD grep —
# the one on the development machine this repository holds itself portable to — refuses an
# interval whose bound is over 255.
win() {
  grep -oE ".{0,250}$1.{0,250}" <<<"$section" | head -1
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

if [[ -z "${section// /}" ]]; then
  # Fail closed: a renamed or emptied section is reported as unreadable rather than probed
  # as an empty string, which would let "the phase is gone" read as "the phase is right".
  problems+=("$skill_md has no '#### Refactor' section to read — how the refactor leaf is launched and what is asked of its result could not be established")
else
  # 1. One leaf for the step. Both faces, because either alone passes a document that is
  #    half-rewritten: it has to SAY one leaf, and it must no longer tell the conductor to
  #    come back round for the next transform.
  [[ "$section" =~ $one_leaf ]] ||
    problems+=("$skill_md's Refactor section never says one leaf applies the step's transforms, so the conductor is not told that the cold start and the spec re-read are paid once rather than once per transform")
  relaunch="$(grep -oE 'repeatedly|(each|every|the next) iteration' <<<"$section" | head -1)"
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
  stale_cycle="$(grep -oE 'per leaf|until none remain|per leaf invocation' <<<"$cycle" | head -1)"
  [[ -z "$stale_cycle" ]] ||
    problems+=("$context_md's Cycle entry still says '$stale_cycle', so the entry a reader learns the cycle from is ADR-0010's shape and contradicts the procedure SKILL.md now runs")
fi

if [[ -z "$invariant" ]]; then
  problems+=("$claude_md has no invariant naming all three budgets to read — what VERI_REFACTOR_BUDGET is said to bound could not be established")
else
  [[ "$invariant" =~ $one_leaf ]] ||
    problems+=("$claude_md's budget invariant never says one leaf spends the step's refactor budget, so the cost axis is still explained as a leaf per transform")
  stale_invariant="$(grep -oE 'asked for one always finds one|one transform per leaf|a transform per leaf' <<<"$invariant" | head -1)"
  [[ -z "$stale_invariant" ]] ||
    problems+=("$claude_md's budget invariant still explains the budget by '$stale_invariant', which is only true of a leaf asked for a single transform")
fi

# The pointer, asked of the pair rather than of each: what the criterion owes a reader is
# that the records name the decision, and a citation in one of them is a reader sent there.
[[ -n "$(adr_pointer "$cycle $invariant")" ]] ||
  problems+=("neither $context_md's Cycle entry nor $claude_md's budget invariant names an ADR other than the superseded 0010, so nothing in either record points a reader at the decision that replaced one transform per leaf")

report "$name"

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

if [[ -z "${section// /}" ]]; then
  # Fail closed, the same way case 1 does: a renamed or emptied section is unreadable, not
  # silently right.
  problems+=("$skill_md has no '#### Refactor' section to read — what becomes of the leaf's NEW_STEP: lines could not be established")
else
  calls="$(grep -oE '\$s/add-ledger-step\.sh' <<<"$section" | grep -c '')"
  if [[ "$calls" -eq 0 ]]; then
    problems+=("$skill_md's Refactor section never runs add-ledger-step.sh, so the leaf's NEW_STEP: lines are narrated and nothing grows the plan — the triangulating step the leaf refused to write by hand is owed to nobody")
  elif [[ "$calls" -gt 1 ]]; then
    problems+=("$skill_md's Refactor section runs add-ledger-step.sh $calls times, so a step's NEW_STEP: values are inserted a call at a time and the growth budget is read once per value rather than once for the step")
  else
    added="$(win '\$s/add-ledger-step\.sh')"
    grep -qE 'new_step' <<<"$added" ||
      problems+=("$skill_md's Refactor section runs add-ledger-step.sh without saying the texts are the leaf's NEW_STEP: values, so what the inserted step says is left to judgement")
    grep -qE "after '?<step>" <<<"$added" ||
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

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
