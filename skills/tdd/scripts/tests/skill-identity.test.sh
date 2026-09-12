#!/usr/bin/env bash
# Unit tests for where the skill ships and what it calls itself — like
# hermetic-suites.test.sh this suite belongs to no single script: its subject is the
# skill directory that contains all of them.
# Zero-dependency plain-shell asserts, same idiom as hermetic-suites.test.sh.
#
# Why this exists (issue #105): the invocation name is the one thing every user touches,
# and it is spelled in two places that must agree — the directory Claude Code loads the
# skill from, and the `name:` field of its SKILL.md frontmatter, which is the command.
#
# Contract under test:
#   skills/tdd/ is a directory, and skills/tdd/SKILL.md's frontmatter reads `name: tdd`.
#
# Run: scripts/tests/skill-identity.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
# The suite sits at skills/<skill>/scripts/tests, so four levels up is the repo root
# whichever name the skill currently carries — the path this case is about is then
# spelled out in full below rather than derived from where this file happens to live.
ROOT="$(cd "$HERE/../../../.." && pwd)"
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

# 1. Both halves of the skill's identity, as one criterion: the directory it lives in and
#    the name its frontmatter declares. The frontmatter is the leading `---` block, and
#    only its first `name:` counts — the awk stops at the closing `---` so a later `name:`
#    in the prose cannot answer for it.
name="the skill ships at skills/tdd/ and its frontmatter reads name: tdd"
problems=()
[[ -d "$ROOT/skills/tdd" ]] ||
  problems+=("want a directory at skills/tdd, found none")
skill="$ROOT/skills/tdd/SKILL.md"
if [[ -f "$skill" ]]; then
  # sub() edits $0 and returns how many replacements it made, so it doubles as the
  # "this line is the name field" test; print then emits what is left, the value.
  got="$(awk 'NR == 1 && $0 == "---" { inside = 1; next }
              inside && $0 == "---" { exit }
              inside && sub(/^name:[[:space:]]*/, "") { print; exit }' "$skill")"
  [[ "$got" == "tdd" ]] ||
    problems+=("skills/tdd/SKILL.md frontmatter: want name 'tdd', got $(printf '%q' "$got")")
else
  problems+=("want a SKILL.md at skills/tdd, found none")
fi
report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
