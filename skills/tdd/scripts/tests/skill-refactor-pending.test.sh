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
# Contract under test (this step only):
#   SKILL.md's Green PASS ticks with `tick-ledger.sh --refactor-pending`; the pin path's
#   tick carries no such flag; and the instruction that ends a step's cycle runs
#   `clear-refactor-pending.sh`, commits the cleared ledger, and only then mirrors the step
#   as done.
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

# instructions — the document's numbered steps, bullets and paragraphs, one per line and
# lowercased. A record runs from a `N. ` or a `- ` (indented or not) in column one, or from
# the first line after a blank, up to the next such line or the next blank; a fenced
# command block inside a bullet is part of that bullet's record, which is what lets a probe
# ask whether the branch that says "PASS" is the one that runs the command.
#
# Runs of whitespace collapse to one space as the record is closed, so a sentence wrapped
# across two lines still reads as one. Case is folded away last, because the sentences are
# the writer's.
instructions() {
  awk '
    function flush() { if (rec != "") { gsub(/[[:space:]]+/, " ", rec); print rec } rec = "" }
    /^[0-9]+\. / || /^[[:space:]]*- / { flush(); rec = $0; next }
    /^[[:space:]]*$/ { flush(); next }
    rec == "" { rec = $0; next }
    { rec = rec " " $0 }
    END { flush() }' "$ROOT/$skill_md" | tr '[:upper:]' '[:lower:]'
}

# reads <what it is> <anchor-regex>… — the first instruction of the global `records`
# matching every <anchor-regex>, into the global `text`; otherwise one problem naming
# <what it is> and a non-zero return. Reads as the sentence it fails with: `reads 'ticks
# the ledger'` asks for the instruction *that* ticks the ledger, and `says`/`denies` then
# probe what this left behind.
#
# Fail closed: a branch that has been reworded away is reported as unreadable rather than
# probed as an empty string, which would let "the instruction is gone" pass as "the
# instruction is right".
text=""
reads() {
  local what="$1" line re
  shift
  while IFS= read -r line; do
    for re in "$@"; do
      [[ "$line" =~ $re ]] || continue 2
    done
    text="$line"
    return 0
  done <<< "$records"
  problems+=("$skill_md has no instruction that $what — what that branch prescribes could not be read")
  return 1
}

# says <regex> <fact> / denies <regex> <fact> — one thing the instruction in `$text` must
# carry, or must not, written as the regex of any wording that would carry it; `fact` names
# it once when the probe is wrong.
says() {
  [[ "$text" =~ $1 ]] || problems+=("$2")
}
denies() {
  if [[ "$text" =~ $1 ]]; then problems+=("$2"); fi
}

# miss <fact> — one problem of the ordered probe below: <fact>, then the instruction it was
# read from, clipped, so the fix is an edit to a line already in front of you. Every miss
# quotes it, which is why the quoting lives here rather than at each of the three.
miss() {
  problems+=("$1: $(printf '%.130s' "$text")")
}

# says_clear_commit_mirror — the three things the instruction in `$text` must prescribe, and
# the order they must come in: clear the mark, commit the cleared ledger, and only then
# mirror the step to the issue. The order is the whole claim here, which is why this is not
# three `says` calls: each probe reads only what the one before it left — `rest` — and the
# first miss returns, because "and after that?" has no answer once the order is already
# broken.
says_clear_commit_mirror() {
  local rest="$text"
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

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
