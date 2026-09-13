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
skill_md="skills/tdd/SKILL.md"

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
  records_of < "$ROOT/$skill_md"
}

# resume_instructions — the same records, but only those of the `## Resume` section: from
# that heading to the next `## ` one. Scoped because the document asks `next-unchecked.sh`
# twice — once at the top of the cycle loop, once on the resume path — and it is only the
# second that this issue is about, so an unscoped read would answer with the wrong branch
# and, worse, let a Resume that says nothing at all pass on the cycle loop's wording.
# `### ` sub-headings survive the slice: the pattern wants "## " with the space.
resume_instructions() {
  awk '/^## / { inside = ($0 == "## Resume"); next } inside' "$ROOT/$skill_md" | records_of
}

# draft_pr_instructions — the records of the `### 4. Draft PR` section: from that heading to
# the next heading of either level. Scoped for the same reason `resume_instructions` is — the
# document pushes a branch and names the PR on more than one path (Bailing pushes too; Resume
# points at this step) — and this criterion is about the step that does the pushing, not about
# the prose elsewhere that sends a run to it.
draft_pr_instructions() {
  awk '/^## / || /^### / { inside = ($0 == "### 4. Draft PR"); next } inside' \
    "$ROOT/$skill_md" | records_of
}

# ordinal <regex> — the 1-based position, within the global `records`, of the first
# instruction matching <regex>, or 0 when none does. Position is what turns two independent
# "is it there?" probes into the one question the criterion asks: which of the two scripts
# the resumed conductor consults first.
ordinal() {
  local n=0 line
  while IFS= read -r line; do
    n=$((n + 1))
    if [[ "$line" =~ $1 ]]; then printf '%s\n' "$n"; return 0; fi
  done <<< "$records"
  printf '0\n'
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
records="$(instructions)"
if [[ -z "$records" ]]; then
  # Fail closed: no records means the document was renamed or emptied and not one probe
  # below was tested, which must not read as a pass.
  problems+=("$skill_md has no instructions to read — the mark's lifetime could not be checked")
else
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
records="$(resume_instructions)"
if [[ -z "$records" ]]; then
  # Fail closed, as above: an empty slice means `## Resume` was renamed or emptied, and not
  # one probe below was tested.
  problems+=("$skill_md has no ## Resume section to read — what a resumed run does could not be checked")
else
  # The order of the two asks. A resume that asks for an unchecked step first starts the
  # next step's red phase with the previous step's refactor still unverified — which is the
  # bug, one step later.
  ask_pending="$(ordinal 'next-pending-refactor\.sh')"
  ask_unchecked="$(ordinal 'next-unchecked\.sh')"
  if [[ "$ask_pending" -eq 0 ]]; then
    problems+=("$skill_md's Resume never asks next-pending-refactor.sh, so a run interrupted inside a step's refactor loop reads that step's tick as done and walks straight to the PR")
  elif [[ "$ask_unchecked" -eq 0 ]]; then
    problems+=("$skill_md's Resume no longer asks next-unchecked.sh, so a resumed run has no next step to continue from")
  elif [[ "$ask_pending" -gt "$ask_unchecked" ]]; then
    problems+=("$skill_md's Resume asks next-unchecked.sh before next-pending-refactor.sh, so it opens the next step's red phase while the previous step's refactor is still unverified")
  fi

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
records="$(draft_pr_instructions)"
if [[ -z "$records" ]]; then
  # Fail closed, as above: an empty slice means `### 4. Draft PR` was renamed or emptied, and
  # not one probe below was tested.
  problems+=("$skill_md has no ### 4. Draft PR section to read — what guards the push could not be checked")
else
  # The gate comes before the push, or it is not a gate: a check made after the branch is
  # already on the remote cannot refuse anything.
  gate="$(ordinal 'git status --porcelain')"
  push="$(ordinal 'git push')"
  if [[ "$gate" -eq 0 ]]; then
    problems+=("$skill_md's Draft PR step never checks git status --porcelain, so the transform a killed refactor leaf left uncommitted is pushed into the PR with no verifier having seen it")
  elif [[ "$push" -eq 0 ]]; then
    problems+=("$skill_md's Draft PR step no longer pushes the branch, so there is nothing for the check to guard")
  elif [[ "$gate" -gt "$push" ]]; then
    problems+=("$skill_md's Draft PR step checks the tree only after git push, so the dirty worktree is already on the remote by the time anything notices")
  fi

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

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
