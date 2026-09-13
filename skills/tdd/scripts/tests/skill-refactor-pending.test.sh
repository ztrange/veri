#!/usr/bin/env bash
# Unit tests for how the conductor drives the refactor-pending mark — like
# skill-event-marks.test.sh and skill-suite-runs.test.sh this suite belongs to no single
# script: its subject is skills/tdd/SKILL.md, read as text, the way the session that
# follows it reads it.
# Zero-dependency plain-shell asserts, same idiom as skill-event-marks.test.sh.
#
# Why this exists (issue #116): `tick-ledger.sh --refactor-pending`,
# `next-pending-refactor.sh` and `clear-refactor-pending.sh` now exist, but a mark nobody
# writes and nobody clears records nothing. The conductor is prose, so the mark's whole
# lifetime lives in this document: Green's PASS is the only place it is ever written, the
# pin path is the one tick that must NOT write it (a pinned step has no refactor loop to
# wait for, so a mark there would leave the step pending for ever), and verify-refactor's
# PASS is the only place it is ever cleared. Get any one of the three wrong and the ledger
# stops answering the question the mark exists for — "is this ticked step tidied, or only
# green?" — which is the question a resumed conductor asks.
#
# Contract under test — the mark's writer, then its reader, one case each:
#   1. SKILL.md's Green PASS ticks with `tick-ledger.sh --refactor-pending`; the pin path's
#      tick carries no such flag; and the instruction that ends a step's cycle runs
#      `clear-refactor-pending.sh`, commits the cleared ledger, and only then mirrors the
#      step as done.
#   2. SKILL.md's Resume asks `next-pending-refactor.sh` before `next-unchecked.sh`, and the
#      branch it takes on a pending step resets what the killed leaf left uncommitted,
#      re-enters that step's refactor loop with the files of its green commit (the last
#      commit that changed the ledger) and the count of `refactor:` commits since it, then
#      runs verify-refactor — with the draft PR behind both scripts exiting 3.
#   3. SKILL.md's Draft PR step itself refuses to push or open the PR while
#      `git status --porcelain` is non-empty or `next-pending-refactor.sh` still finds a
#      pending step.
#   4. SKILL.md's script reference list — the section a session reads a script's contract
#      out of before it calls it — has an entry for each of the three, saying what it
#      prints (or, for the two that edit the ledger, the mark they write and strip) and
#      which exit codes it can answer with.
#
# Each half is asked of ONE instruction, the way skill-event-marks.test.sh asks for a mark
# beside the comment it mirrors: the clear and the commit that carries it belong in the
# same instruction as the mirror they precede, because a clear prescribed in some other
# section drifts away from the branch it belongs to the first time either is reworded — and
# a ledger whose mark is cleared on a different path than the one that ends the step is
# exactly the divergence this issue is about.
#
# Run: scripts/tests/skill-refactor-pending.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
# The suite sits at skills/<skill>/scripts/tests, so four levels up is the repo root.
ROOT="$(cd "$HERE/../../../.." && pwd)"
# The document twice, the way skill-suite-runs.test.sh names its two: the path as every
# problem message spells it, and the same path resolved for the readers below to open. One
# constant for each, so a message can never name a file the readers did not read — and so
# the resolving happens once rather than at each reader, which is the same reason
# `records_of` and `section_of` are each spelled once.
skill_md="skills/tdd/SKILL.md"
skill_path="$ROOT/$skill_md"

pass=0 fail=0

# report <name> — close a case whose probes collected into the `problems` array: an empty
# array is a pass, otherwise one FAIL line for the case and one indented line per problem,
# so the output says which end of the mark's lifetime broke rather than just that it did.
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
# is what lets a probe ask whether the branch that says "PASS" is the one that runs the
# command.
#
# Runs of whitespace collapse to one space as the record is closed, so a sentence wrapped
# across two lines still reads as one. Case is folded away last, because the sentences are
# the writer's.
#
# Both readers below end in it, the way skill-suite-runs.test.sh's readers both end in
# `plain`, so "what a record is" is spelled once. A second spelling would not fail — it
# would quietly answer a probe with records built by a grammar the other reader has since
# outgrown.
records_of() {
  awk '
    function flush() { if (rec != "") { gsub(/[[:space:]]+/, " ", rec); print rec } rec = "" }
    /^[0-9]+\. / || /^[[:space:]]*- / { flush(); rec = $0; next }
    /^[[:space:]]*$/ { flush(); next }
    rec == "" { rec = $0; next }
    { rec = rec " " $0 }
    END { flush() }' | tr '[:upper:]' '[:lower:]'
}

# instructions — the whole document as records.
instructions() {
  records_of < "$skill_path"
}

# section_of <heading> <closers-re> — the records of one section of the document: the lines
# after the one that is exactly <heading>, up to the next line matching <closers-re>, which
# is what says which headings end it. Both scoped readers below are this same slice, so it
# is spelled once here and only the two arguments differ — the same reason `records_of`
# above is one function rather than one per reader.
section_of() {
  awk -v heading="$1" -v closers="$2" \
    '$0 ~ closers { inside = ($0 == heading); next } inside' "$skill_path" | records_of
}

# resume_instructions — the records of the `## Resume` section. Scoped because the document
# asks `next-unchecked.sh` twice — once at the top of the cycle loop, once on the resume path
# — and it is only the second that this issue is about, so an unscoped read would answer with
# the wrong branch and, worse, let a Resume that says nothing at all pass on the cycle loop's
# wording. `### ` sub-headings survive the slice: the closers want "## " with the space.
resume_instructions() {
  section_of '## Resume' '^## '
}

# draft_pr_instructions — the records of the `### 4. Draft PR` section, which a heading of
# either level ends. Scoped for the same reason `resume_instructions` is — the document
# pushes a branch and names the PR on more than one path (Bailing pushes too; Resume points
# at this step) — and this criterion is about the step that does the pushing, not about the
# prose elsewhere that sends a run to it.
draft_pr_instructions() {
  section_of '### 4. Draft PR' '^## |^### '
}

# scripts_instructions — the records of the `## The scripts (this skill's `scripts/`
# directory)` section: the reference list, one bullet per script, that a session reads a
# script's contract out of before it calls it. Scoped for the same reason the two readers
# above are, and more sharply: every one of these scripts is *named* again further down, at
# the point the procedure runs it, and a call site is not documentation — it says what to
# run, never what comes back. An unscoped read would answer this criterion with those call
# sites and pass a reference list that never gained an entry at all.
scripts_instructions() {
  section_of '## The scripts (this skill'\''s `scripts/` directory)' '^## '
}

# records_from <reader> <nothing-to-read fact> — what one of the readers above yields, into
# the global `records`, and a zero return; or, when it yields nothing at all, one problem
# naming <fact> and a non-zero return, so the case that follows is skipped rather than run
# against an empty document.
#
# Fail closed, for the reason `reads` below does: an empty slice means the heading was
# renamed or its section emptied, and then not one probe of that case was tested — which must
# not read as a pass. All three cases open with it, so that rule is spelled once here instead
# of as three guards that could each drift from the others.
records_from() {
  records="$("$1")"
  [[ -n "$records" ]] && return 0
  problems+=("$2")
  return 1
}

# ordinal <regex> — the 1-based position, within the global `records`, of the first
# instruction matching <regex>, or 0 when none does. Position is what turns two independent
# "is it there?" probes into the one question a criterion about order asks: which of the two
# the document does first.
ordinal() {
  local n=0 line
  while IFS= read -r line; do
    n=$((n + 1))
    if [[ "$line" =~ $1 ]]; then printf '%s\n' "$n"; return 0; fi
  done <<< "$records"
  printf '0\n'
}

# precedes <first-re> <second-re> <no-first> <no-second> <out-of-order> — one problem when the
# global `records` do not do <first-re> before <second-re>, phrased as whichever of the three
# things went wrong: the first instruction is gone, the second is, or they have swapped.
#
# Two of the criteria below are this same claim — Resume asks `next-pending-refactor.sh`
# before `next-unchecked.sh`, and the Draft PR step checks the tree before it pushes — and
# both fail those same three ways, so the branching is spelled once here and only the three
# sentences differ at the call.
#
# The two absences are reported before the order is, and as their own problems, because a
# missing instruction has ordinal 0: compared as a position it reads as "comes first", which
# would let a document that dropped the check altogether pass the ordering probe.
precedes() {
  local first second
  first="$(ordinal "$1")"
  second="$(ordinal "$2")"
  if [[ "$first" -eq 0 ]]; then
    problems+=("$3")
  elif [[ "$second" -eq 0 ]]; then
    problems+=("$4")
  elif [[ "$first" -gt "$second" ]]; then
    problems+=("$5")
  fi
}

# reads <what it is> <anchor-regex>… — the first instruction of the global `records`
# matching every <anchor-regex>, into the global `instruction`; otherwise one problem naming
# <what it is> and a non-zero return. Reads as the sentence it fails with: `reads 'ticks
# the ledger'` asks for the instruction *that* ticks the ledger, and `says`/`denies` then
# probe what this left behind.
#
# Fail closed: a branch that has been reworded away is reported as unreadable rather than
# probed as an empty string, which would let "the instruction is gone" pass as "the
# instruction is right".
instruction=""
reads() {
  local what="$1" line re
  shift
  while IFS= read -r line; do
    for re in "$@"; do
      [[ "$line" =~ $re ]] || continue 2
    done
    instruction="$line"
    return 0
  done <<< "$records"
  problems+=("$skill_md has no instruction that $what — what that branch prescribes could not be read")
  return 1
}

# says <regex> <fact> / denies <regex> <fact> — one thing the `$instruction` just read must
# carry, or must not, written as the regex of any wording that would carry it; `fact` names
# it once when the probe is wrong.
says() {
  [[ "$instruction" =~ $1 ]] || problems+=("$2")
}
denies() {
  if [[ "$instruction" =~ $1 ]]; then problems+=("$2"); fi
}

# says_exit_codes <script> — the two codes a reference-list entry for either of the mark's
# two new scripts must name: 0, the answer, and 3, the *nothing to do* code this repository
# reserves for it. Both scripts answer with the same pair and both fail the same way without
# it — the conductor branches on the code, so a code nobody wrote down is a branch the
# session invents — which is why the pair is spelled once here and only the script's name
# differs at the two calls. `exits?` rather than `exit`, because the list writes it both ways.
says_exit_codes() {
  says 'exits? 0' \
    "$skill_md's entry for $1 never names exit 0, so nothing says what a call that did its work answers with, and the conductor is left inferring it from whether stdout came back empty"
  says 'exits? 3' \
    "$skill_md's entry for $1 never names exit 3, so the one code that is not an error — nothing matched, nothing pending — has no documented meaning and reads as the plumbing having broken"
}

# miss <fact> — one problem of the ordered probe below: <fact>, then the instruction it was
# read from, clipped, so the fix is an edit to a line already in front of you. Every miss
# quotes it, which is why the quoting lives here rather than at each of the three.
miss() {
  problems+=("$1: $(printf '%.130s' "$instruction")")
}

# says_clear_commit_mirror — the three things the `$instruction` just read must prescribe,
# and the order they must come in: clear the mark, commit the cleared ledger, and only then
# mirror the step to the issue. The order is the whole claim here, which is why this is not
# three `says` calls: each probe reads only what the one before it left — `rest` — and the
# first miss returns, because "and after that?" has no answer once the order is already
# broken.
says_clear_commit_mirror() {
  local rest="$instruction"
  if [[ ! "$rest" =~ clear-refactor-pending\.sh ]]; then
    miss "$skill_md never runs clear-refactor-pending.sh where a step's cycle completes, so the mark green wrote is never removed and every finished step reads as pending"
    return
  fi
  rest="${rest#*clear-refactor-pending.sh}"
  if [[ ! "$rest" =~ git[[:space:]].*commit ]]; then
    miss "$skill_md clears the mark but commits nothing after it, so the cleared ledger stays uncommitted and the next resume reads the committed one, which still says pending"
    return
  fi
  # Past the commit: what is left is what the document does once the cleared ledger is safe
  # on disk, and the mirror has to be in there rather than before it.
  rest="${rest#*commit}"
  [[ "$rest" =~ tick-issue-criterion\.sh ]] ||
    miss "$skill_md mirrors the step to the issue before the cleared ledger is committed, so a run killed in that window has an issue saying done over a ledger still saying pending"
}

# says_reset_reenter_verify — the four things the `$instruction` just read must prescribe for
# a step that comes back pending: throw away what the killed leaf left on disk, re-enter the
# refactor loop with its two inputs (the files of the step's green commit, and how many
# transforms already landed), and verify-refactor after it. `$anchor` is what the order is
# read against — the reset has to come before it and the verification after it — so its
# absence returns rather than probing two halves of a string that has no middle.
#
# It is spelled once, and used three times: to establish it is there, and to cut the
# instruction either side of it. A second spelling that drifted from the first would not
# fail — a `%%`/`#` whose pattern misses yields the whole string — it would silently make
# both halves the whole instruction, and the two ordered probes would then pass on any
# wording that merely mentions a reset and a verification anywhere.
says_reset_reenter_verify() {
  local before after
  local anchor='git diff --name-only'
  local reset_re='git (checkout|restore|reset|stash|clean)'
  local green_re='git log.*issue-<n>\.md'
  local verify_re='verify-refactor|verify\.sh refactor'
  if [[ ! "$instruction" =~ $anchor ]]; then
    miss "$skill_md's Resume re-enters no refactor loop for the pending step — nothing computes the files of its green commit, so the loop has no bounds to tidy within and the step is left green but never tidied"
    return
  fi
  before="${instruction%%$anchor*}"
  after="${instruction#*$anchor}"
  [[ "$before" =~ $reset_re ]] ||
    miss "$skill_md's Resume re-enters the refactor loop without first resetting the worktree, so the transform the killed leaf left uncommitted is carried into the resumed step and into the PR unverified"
  [[ "$instruction" =~ $green_re ]] ||
    miss "$skill_md's Resume never identifies the pending step's green commit as the last commit that changed the ledger, so the files it hands the refactor loop are some other commit's and the tidy-up is aimed at the wrong code"
  [[ "$instruction" =~ refactor: ]] ||
    miss "$skill_md's Resume hands the refactor loop no count of the \`refactor:\` commits already made for the step, so the budget restarts at 0 and an interrupted run can spend it twice over"
  [[ "$after" =~ $verify_re ]] ||
    miss "$skill_md's Resume re-enters the refactor loop but never runs verify-refactor after it, which is the check the interruption skipped in the first place"
}

# 1. One criterion — the mark is written at exactly one tick, withheld at the other, and
#    cleared where the step ends — and so one case. The three probes are one wiring: a mark
#    written and never cleared stalls every resumed run in a refactor loop, and a mark
#    cleared but never written leaves resume blind again, so the fix to any of them is one
#    edit to one document.
name="$skill_md ticks green with --refactor-pending, pins without it, and clears the mark before mirroring the step done"
problems=()
if records_from instructions \
    "$skill_md has no instructions to read — the mark's lifetime could not be checked"; then
  # Green's PASS — the only tick that writes the mark, because it is the only one a
  # refactor loop follows.
  if reads 'ticks the ledger and commits the code with a `feat:` commit' \
      'tick-ledger\.sh' 'feat:'; then
    says 'tick-ledger\.sh[[:space:]]+--refactor-pending' \
      "$skill_md's green PASS still ticks with plain \`tick-ledger.sh\`, so the step is recorded as done the moment it is green and a run interrupted in its refactor loop resumes with nothing left to do"
  fi

  # The pin path — a step with no production code has no refactor loop, so a mark written
  # here would never be cleared.
  if reads 'ticks the ledger and commits the pin with a `test: pin` commit' \
      'tick-ledger\.sh' 'test: pin'; then
    denies '--refactor-pending' \
      "$skill_md's pin path ticks with --refactor-pending, but a pinned step runs no refactor loop, so the mark it writes can never be cleared and resume would re-enter a loop that step never had"
  fi

  # verify-refactor's PASS — the only place the mark is cleared, and the clearing has to
  # land in a commit before the step is mirrored as done.
  if reads 'ends the cycle by posting the `### ✅ step done` comment' 'step done'; then
    says_clear_commit_mirror
  fi
fi
report "$name"

# 2. One criterion — the mark's reader. Resume is the whole reason the mark is written, so
#    asking for it is only half the fix: the order of the two asks decides whether a pending
#    step is picked up at all, and what the pending branch prescribes decides whether the
#    step is actually finished or merely re-entered. Both are one case, because a Resume that
#    asks `next-pending-refactor.sh` and then does the wrong thing with the answer leaves the
#    run exactly where #116 found it — a PR opened over an unverified refactor.
name="$skill_md's Resume asks next-pending-refactor.sh before next-unchecked.sh, re-enters the pending step's refactor loop, and reaches the draft PR only when both exit 3"
problems=()
if records_from resume_instructions \
    "$skill_md has no ## Resume section to read — what a resumed run does could not be checked"; then
  # The order of the two asks. A resume that asks for an unchecked step first starts the
  # next step's red phase with the previous step's refactor still unverified — which is the
  # bug, one step later.
  precedes 'next-pending-refactor\.sh' 'next-unchecked\.sh' \
    "$skill_md's Resume never asks next-pending-refactor.sh, so a run interrupted inside a step's refactor loop reads that step's tick as done and walks straight to the PR" \
    "$skill_md's Resume no longer asks next-unchecked.sh, so a resumed run has no next step to continue from" \
    "$skill_md's Resume asks next-unchecked.sh before next-pending-refactor.sh, so it opens the next step's red phase while the previous step's refactor is still unverified"

  # The pending branch — what the resumed conductor does with a step that comes back green
  # but not tidied.
  if reads 'runs next-pending-refactor.sh on a resume' 'next-pending-refactor\.sh'; then
    says_reset_reenter_verify
  fi

  # The exit — the draft PR is where the interrupted run wrongly went, so it must now be
  # behind both scripts having nothing left to hand over.
  if reads 'sends a resumed run to the draft pr' 'draft pr'; then
    says 'next-pending-refactor\.sh' \
      "$skill_md sends a resumed run to the draft PR on next-unchecked.sh alone, so a ledger whose every step is ticked still reaches the PR with the last step's refactor unverified"
    says 'next-unchecked\.sh' \
      "$skill_md sends a resumed run to the draft PR without next-unchecked.sh having exited 3, so a run with steps still to do can reach the PR"
  fi
fi
report "$name"

# 3. One criterion — the gate on the way out, and so one case. Resume's last sub-step already
#    says a resumed run reaches the PR only when both scripts exit 3, but that is prose on one
#    path *into* this step; the cycle loop walks into it too, and what #116 actually found was
#    a worktree carrying a killed leaf's uncommitted transform. So the refusal has to live
#    where the push is: the Draft PR step asks both questions itself — is the tree clean, is
#    any step still only green — and stops before `git push` if either says otherwise.
name="$skill_md's Draft PR step refuses to push or open the PR while git status --porcelain is non-empty or next-pending-refactor.sh finds a pending step"
problems=()
if records_from draft_pr_instructions \
    "$skill_md has no ### 4. Draft PR section to read — what guards the push could not be checked"; then
  # The gate comes before the push, or it is not a gate: a check made after the branch is
  # already on the remote cannot refuse anything.
  precedes 'git status --porcelain' 'git push' \
    "$skill_md's Draft PR step never checks git status --porcelain, so the transform a killed refactor leaf left uncommitted is pushed into the PR with no verifier having seen it" \
    "$skill_md's Draft PR step no longer pushes the branch, so there is nothing for the check to guard" \
    "$skill_md's Draft PR step checks the tree only after git push, so the dirty worktree is already on the remote by the time anything notices"

  # What that gate asks, and what it does with the answer. Both conditions belong to the one
  # instruction: a run stopped here is stopped for the same reason either way — the PR would
  # otherwise carry work no verifier has passed.
  if reads 'checks the worktree is clean before the branch is pushed' 'git status --porcelain'; then
    says 'next-pending-refactor\.sh' \
      "$skill_md's Draft PR step checks only that the tree is clean, so a ledger whose last step is committed but still marked refactor-pending opens a PR with that step's refactor never verified"
    says 'refuse|do not push|does not push|stop|bail|must not|never' \
      "$skill_md's Draft PR step names the checks but never says they can stop it, so a non-empty status or a pending step is read as information and the push goes ahead anyway"
  fi
fi
report "$name"

# 4. One criterion — the three scripts the mark's lifetime runs through are documented where
#    a session goes to look a script up, and so one case. Cases 1–3 pin the *call sites*:
#    which branch runs which script. A call site says what to run and never what comes back,
#    and all three of these are branched on — `next-pending-refactor.sh` exiting 3 is what
#    sends a resumed run to the PR, `clear-refactor-pending.sh` exiting 3 says the step it
#    was told to clear is not in the ledger, `tick-ledger.sh` exiting 3 says the green commit
#    ticked nothing. So an entry that omits a code is worse than a missing entry: a missing
#    one is noticed, whereas a half-written one has the session invent a meaning for the code
#    it meets. One case, because the three entries are one list and any fix to them is one
#    edit to it.
name="$skill_md's script reference list documents tick-ledger.sh --refactor-pending, next-pending-refactor.sh and clear-refactor-pending.sh, each with what it prints and its exit codes"
problems=()
if records_from scripts_instructions \
    "$skill_md has no ## The scripts section to read — what the reference list documents could not be checked"; then
  # Every anchor below is the entry's own opening — `- \`$S/<script>` — rather than the bare
  # script name, so a passing mention inside some other entry can never be read as the entry
  # itself, which is the same distinction `scripts_instructions` draws against the call sites.

  # tick-ledger.sh — the writer. Its entry already documents the plain tick, so what the flag
  # owes the list is the second thing that one write does: the flag's own name, the mark it
  # appends (spelled, because that literal is what the reader matches on), and the code a
  # ledger with no matching step answers with either way.
  if reads 'documents tick-ledger.sh in the script reference list' \
      '^- .\$s/tick-ledger\.sh'; then
    says '--refactor-pending' \
      "$skill_md's entry for tick-ledger.sh never mentions --refactor-pending, so the flag the green commit must tick with is invisible to a session that reads the list to find out how to tick"
    says '⟂ refactor pending' \
      "$skill_md's entry for tick-ledger.sh never spells the mark the flag appends, so nothing connects that write to the \`⟂ refactor pending\` string next-pending-refactor.sh matches, and either side can be reworded without the other noticing"
    says 'exits? 3' \
      "$skill_md's entry for tick-ledger.sh never names exit 3, so a green commit whose substring matched no unchecked step looks like it ticked, and the step is committed as green with no mark and no tick"
  fi

  # next-pending-refactor.sh — the reader, and the only one of the three whose answer is on
  # stdout, so its entry owes what that answer is as well as the two codes.
  if reads 'documents next-pending-refactor.sh in the script reference list' \
      '^- .\$s/next-pending-refactor\.sh'; then
    says 'prints?[^.]*step' \
      "$skill_md's entry for next-pending-refactor.sh never says it prints the pending step, so a resumed conductor is not told that stdout is the step to re-enter the refactor loop on"
    says_exit_codes 'next-pending-refactor.sh'
  fi

  # clear-refactor-pending.sh — the eraser. Nothing on stdout, so what its entry owes instead
  # is which mark it takes off, and that it does so in the ledger itself.
  if reads 'documents clear-refactor-pending.sh in the script reference list' \
      '^- .\$s/clear-refactor-pending\.sh'; then
    says '⟂ refactor pending' \
      "$skill_md's entry for clear-refactor-pending.sh never spells the mark it removes, so the list documents an eraser without saying what it erases and nothing ties it to the flag that wrote the mark"
    says 'strip|remove|drop|clear|delete' \
      "$skill_md's entry for clear-refactor-pending.sh never says it takes the mark off the step, so what the script does to the ledger is left to be guessed from its name"
    says_exit_codes 'clear-refactor-pending.sh'
  fi
fi
report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
