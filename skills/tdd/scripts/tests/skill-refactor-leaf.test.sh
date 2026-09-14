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
# Contract under test — one leaf, then the three things the conductor asks of what it left:
#   SKILL.md's Refactor section launches ONE leaf for the step rather than one per
#   transform; before verify-refactor it asks `git status --porcelain` and refuses to go on
#   while the tree is dirty; it asks the subjects of the commits since the green commit and
#   refuses to go on when one of them is not a `refactor:`; and it counts those commits with
#   `git rev-list --count` and narrates the count against the budget, saying so when the
#   count is over it rather than leaving the overrun out.
#
# One criterion — the conductor launches one leaf and checks its result instead of
# producing it — and so one case. The probes are its parts: a document that launched one
# leaf and then walked into verify-refactor over a dirty tree would be exactly as wrong as
# one that still looped leaves, and a reader repairing either repairs the same section.
# `problems` says which part is missing.
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
  [[ "$section" =~ (one|a single)\ (refactor\ |developer\ |transform\ )?leaf ]] ||
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
    grep -qE 'refus|do(es)? not (go on|continue|proceed)|don.t (go on|continue)|not continue|bail' <<<"$dirty" ||
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
    grep -qE 'refus|do(es)? not (go on|continue|proceed)|don.t (go on|continue)|not continue|bail' <<<"$subjects" ||
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

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
