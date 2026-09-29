#!/usr/bin/env bash
# Unit test for skills/tdd/SKILL.md's account of the refactor leaf's report footer, held
# against the report lines the built refactor prompt asks for (issue #175). Like
# skill-refactor-leaf.test.sh this suite belongs to no single script: its subject is the
# procedure, read as text, the way the session that follows it reads it.
#
# It is a suite of its own, not a case of skill-refactor-leaf.test.sh, because it is the one
# check over that section that runs a script: flag-class-amendment-guard.test.sh and
# beyond-spec-narration-guard.test.sh copy skill-refactor-leaf.test.sh into a scratch tree
# holding only the documents it reads, and a case there that ran build-develop-prompt.sh would
# be red in that tree for a reason no plant put there.
#
# Contract under test — one criterion:
#   1. The Refactor section's account of the leaf's report footer names exactly the report
#      lines the built refactor prompt asks for — no line the prompt does not emit, none it
#      emits left out.
#
# Run: scripts/tests/skill-refactor-footer.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"

skill_md="skills/tdd/SKILL.md"
skill_path="$ROOT/$skill_md"

pass=0 fail=0

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

refactor_heading='#### Refactor'

refactor_lines() {
  awk -v h="$refactor_heading" \
    'index($0, h) == 1 { inside = 1; next } inside && /^#/ { exit } inside' "$skill_path"
}

unreadable_problem() {
  printf "%s has no '%s' section to read — %s" "$skill_md" "$refactor_heading" "$1"
}

name="$skill_md's Refactor section names exactly the report lines the built refactor prompt asks the leaf for"
problems=()

spec_tmp="$(mktemp)"
echo "spec" >"$spec_tmp"
emitted="$("$ROOT/skills/tdd/scripts/build-develop-prompt.sh" refactor "$spec_tmp" "step" "make test" "a.sh" |
  sed -nE 's/^([A-Z][A-Z_]+):.*/\1/p' | sort -u)"
rm -f "$spec_tmp"

footer="$(refactor_lines | awk '
  /^[[:space:]]*```/ { fenced = !fenced; next }
  !fenced && !found && index($0, "develop-refactor.out") { found = 1 }
  found && /^[0-9]+\. / { exit }
  found' | tr -d '*`' | tr '\n' ' ')"
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
