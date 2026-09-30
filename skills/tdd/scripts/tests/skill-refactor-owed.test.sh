#!/usr/bin/env bash
# Unit test for how skills/tdd/SKILL.md carries a step's structural leftovers out of its
# refactor loop. Like skill-refactor-leaf.test.sh and skill-suite-runs.test.sh this suite
# belongs to no single script: its subject is the procedure, read as text, the way the
# session that follows it reads it. Zero-dependency plain-shell asserts, same idiom, picked
# up by `make test`'s glob by existing.
#
# Why this exists (issue #359, part of #354): `refactor-owed.sh` now exists and its own
# suite pins both verbs, but a script the conductor is never told to run records nothing.
# When a step's refactor stops with structural candidates left, the only place they are
# written is `.tdd/develop-refactor.out`, which the next step overwrites — so by the draft
# PR every step's leftovers but the last are gone. The conductor is prose, so whether they
# survive is decided here and nowhere else.
#
# Contract under test — one criterion, one case: SKILL.md's Refactor section runs
# `refactor-owed.sh append` on the refactor leaf's own report, into the run's owed file and
# under the step, and the file rides the commit that clears that step's refactor-pending
# mark. The two halves are one criterion because either alone records nothing that lasts:
# an append whose file is never committed is lost with the worktree, and a commit of a file
# nothing ever appends to is a commit of nothing.
#
# Each probe accepts any wording that carries its fact — how the document phrases it is the
# writer's — but the file and the report are asked of the text AROUND the append call rather
# than of the section at large, which already names `.tdd/develop-refactor.out` for the
# leaf's own launch and would answer for a document that appends from anywhere.
#
# Run: scripts/tests/skill-refactor-owed.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"

skill_md="skills/tdd/SKILL.md"
skill_path="$ROOT/$skill_md"

pass=0 fail=0

source "$HERE/lib/harness.sh"

plain() {
  tr -d '*`' | tr '[:upper:]' '[:lower:]'
}

refactor_section() {
  awk -v h='#### Refactor' \
    'index($0, h) == 1 { inside = 1; next } inside && /^#/ { exit } inside' "$skill_path" |
    plain | tr '\n' ' '
}
section="$(refactor_section)"

# hazard: BSD grep refuses an interval bound over 255.
win() {
  head -1 < <(grep -oE ".{0,250}$1.{0,250}" <<<"$section")
}

name="$skill_md's Refactor section appends the step's structural leftovers to the run's owed file and commits that file with the step's refactor-pending clear"
problems=()

if [[ -z "${section// /}" ]]; then
  problems+=("$skill_md has no '#### Refactor' section to read — whether a step's structural leftovers are recorded anywhere could not be established")
else
  append="$(win 'refactor-owed\.sh append')"
  if [[ -z "$append" ]]; then
    problems+=("$skill_md's Refactor section never runs refactor-owed.sh append, so a step's structural leftovers live only in .tdd/develop-refactor.out and are gone as soon as the next step overwrites it")
  else
    grep -qE 'issue-[^ ]*refactor-owed\.md' <<<"$append" ||
      problems+=("$skill_md's Refactor section runs refactor-owed.sh append without naming the run's .tdd/issue-<n>-refactor-owed.md file, so where a resumed run should find the leftovers it already recorded is left to judgement")
    grep -qE 'develop-refactor\.out' <<<"$append" ||
      problems+=("$skill_md's Refactor section runs refactor-owed.sh append without feeding it the refactor leaf's report, so the candidates it is supposed to record have no source")
    grep -qE '<step>' <<<"$append" ||
      problems+=("$skill_md's Refactor section runs refactor-owed.sh append without the step, so a run's leftovers pile up with nothing saying which step owes which")
  fi

  cleared="$(win 'clear-refactor-pending\.sh')"
  if [[ -z "$cleared" ]]; then
    problems+=("$skill_md's Refactor section never clears the refactor-pending mark, so the commit the owed file is supposed to ride does not exist to be read for")
  else
    grep -qE 'refactor-owed' <<<"$cleared" ||
      problems+=("$skill_md's Refactor section commits the cleared ledger without saying the owed file goes with it, so what append wrote stays uncommitted and dies with the worktree")
    grep -qE 'commit' <<<"$cleared" ||
      problems+=("$skill_md's Refactor section clears the refactor-pending mark without committing anything there, so neither the clear nor the owed file survives a resume")
  fi
fi

report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
