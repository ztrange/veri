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

# draft_pr_instructions — the records of the `### 4. Draft PR` section, which a heading of
# either level ends. Scoped, because the document pushes a branch on more than one path:
# *Bailing* pushes deliberately, and the cycle loop now pushes after every green commit.
# An unscoped read would answer this criterion with those, and fail a document that had
# done exactly what this step asks.
draft_pr_instructions() {
  awk -v heading='### 4. Draft PR' -v closers='^## |^### ' \
    '$0 ~ closers { inside = ($0 == heading); next } inside' "$skill_path" | records_of
}

# 1. The criterion, as one case: the step opens the PR for a branch that is already on the
#    remote. Both halves are asked of the same slice, and the opening half is asked first so
#    the case fails closed — a section emptied or renamed must not read as "it no longer
#    pushes". `git push` rather than the word "push": the step's first sub-step still refuses
#    to go on while there is nothing *fit* to push, and that refusal is #116's gate, not a
#    push. What this criterion is about is whether the step issues the command.
name="$skill_md's Draft PR step opens the PR against the already-pushed branch, with no push of its own"
problems=()

records="$(draft_pr_instructions)"
if [[ -z "$records" ]]; then
  problems+=("$skill_md has no ### 4. Draft PR section to read — whether the step still pushes could not be checked")
else
  grep -qF 'gh pr create' <<< "$records" ||
    problems+=("$skill_md's Draft PR step never runs gh pr create, so there is no PR being opened against the pushed branch at all")
  pushes="$(grep -F 'git push' <<< "$records" | head -1)"
  [[ -z "$pushes" ]] ||
    problems+=("$skill_md's Draft PR step still pushes the branch itself, so the procedure reads as though the branch reaches the remote only once the run is review-ready: $(printf '%.120s' "$pushes")")
fi
report "$name"

# pass_record <heading prefix> — the record of the PASS branch inside the `####` section
# whose heading STARTS WITH <heading prefix>, or nothing when there is no such section or
# no such branch in it. Scoped per section for the reason draft_pr_instructions is scoped:
# the document takes a PASS branch on five paths, and an unscoped read would let Red's
# answer for Green's. A literal prefix rather than the whole heading because both headings
# here carry trailing prose after an em dash; the prefix is what identifies them and is
# quotable in the message about not finding one.
pass_record() {
  awk -v h="$1" 'index($0, h) == 1 { inside = 1; next } /^#/ { inside = 0 } inside' "$skill_path" \
    | records_of | grep -E '^ *- \*\*pass' | head -1
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

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
