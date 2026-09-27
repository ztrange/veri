#!/usr/bin/env bash
# Unit tests for where the /tdd-candidates skill ships, what it calls itself, and what it says
# its job is — like skill-fix-identity.test.sh this suite belongs to no single script: its
# subject is a skill directory and the SKILL.md inside it, read as text, the way the session
# that follows it reads it.
# Zero-dependency plain-shell asserts, same idiom as skill-fix-identity.test.sh.
#
# Why this exists (issue #501): an architecture analysis ends in a list of candidates and
# stops; turning them into issues veri can take is a separate command. The invocation name is
# the one thing every user touches — spelled in two places that must agree, the directory
# Claude Code loads the skill from and the `name:` field of its frontmatter. The other half of
# the same criterion is the skill's scope: it shapes and files the candidates it is handed, and
# it does not survey, rank or judge them — that is the analysis's job, done elsewhere, and a
# filer that re-judges its input is a second analysis nobody asked for.
#
# Contract under test:
#   skills/tdd-candidates/ is a directory, skills/tdd-candidates/SKILL.md's frontmatter reads
#   `name: tdd-candidates`, and its body says it shapes and files candidates, and that it does
#   not survey, rank or judge them.
#
# Run: scripts/tests/skill-candidates-identity.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
# The suite sits at skills/<skill>/scripts/tests, so four levels up is the repo root.
ROOT="$(cd "$HERE/../../../.." && pwd)"

# The two halves of the identity, each written down exactly once: the directory Claude Code
# loads the skill from, and the command name its frontmatter must declare. Neither is derived
# from the other, so a half-finished rename still fails.
skill_dir="skills/tdd-candidates"
want_name="tdd-candidates"
skill_md="$skill_dir/SKILL.md"

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

# frontmatter_name <file> — the value of the first `name:` inside the leading `---` block,
# empty if the block or the field is missing. Same helper as skill-fix-identity.test.sh's.
frontmatter_name() {
  awk 'NR == 1 && $0 == "---" { inside = 1; next }
       inside && $0 == "---" { exit }
       inside && sub(/^name:[[:space:]]*/, "") { print; exit }' "$1"
}

# body_text <file> — everything after the frontmatter block, emphasis marks and backticks
# dropped, case folded and joined onto one line. The frontmatter is excluded on purpose: the
# `description:` field is written for the command picker and must not answer for the
# procedure the session reads.
body_text() {
  awk 'NR == 1 && $0 == "---" { inside = 1; next }
       inside && $0 == "---" { inside = 0; body = 1; next }
       body { print }' "$1" | tr -d '*`' | tr '[:upper:]' '[:lower:]' | tr '\n' ' '
}

# says <regex> <fact> — one thing the body has to carry; <fact> names it if nothing matches.
says() {
  [[ "$text" =~ $1 ]] || problems+=("$2")
}

# 1. The skill exists under the name a user types, and it says what its job is and is not.
#    Both halves are one criterion: a document under a directory Claude Code does not load is
#    not a command, and a command that surveys, ranks or judges is not the one this issue asks
#    for. Read as prose because prose is the whole of a SKILL.md.
name="$skill_md is the /$want_name skill and says it shapes and files candidates without surveying, ranking or judging them"
problems=()
[[ -d "$ROOT/$skill_dir" ]] ||
  problems+=("want a directory at $skill_dir, found none")
if [[ -f "$ROOT/$skill_md" ]]; then
  got="$(frontmatter_name "$ROOT/$skill_md")"
  [[ "$got" == "$want_name" ]] ||
    problems+=("$skill_md frontmatter: want name '$want_name', got $(printf '%q' "$got")")
  text="$(body_text "$ROOT/$skill_md")"
  if [[ -z "${text// /}" ]]; then
    # Fail closed: an unread body must not read as a pass.
    problems+=("$skill_md has no body after its frontmatter — its scope could not be read")
  else
    says 'shapes?[^.]{0,80}files?[^.]{0,80}candidates?|candidates?[^.]{0,80}shapes?[^.]{0,80}files?' \
      "$skill_md never says it shapes and files candidates"
    says '(not|never|no)[^.]{0,40}survey' \
      "$skill_md never says it does not survey"
    says '(not|never|no)[^.]{0,60}rank' \
      "$skill_md never says it does not rank"
    says '(not|never|no)[^.]{0,80}judge' \
      "$skill_md never says it does not judge"
  fi
else
  problems+=("want a SKILL.md at $skill_md, found none")
fi
report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
