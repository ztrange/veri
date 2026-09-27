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

# The body every case reads, read once: empty when the SKILL.md is missing, which each case
# reports on its own terms.
text=""
[[ -f "$ROOT/$skill_md" ]] && text="$(body_text "$ROOT/$skill_md")"

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

# 2. Criterion 1 of #501: handed candidates in the conversation, the skill files one GitHub
#    issue per module — not one per smell, since a single smell is one step and a run's fixed
#    overhead is too large to spend on one — and each issue's acceptance criteria are
#    structural predicates carrying a runnable check where one exists. Read as prose: the
#    procedure is the whole of what the session filing the issues follows.
name="$skill_md files one issue per module from conversation candidates, criteria as predicates with a runnable check"
problems=()
if [[ -f "$ROOT/$skill_md" ]]; then
  says 'candidates?[^.]{0,120}conversation|conversation[^.]{0,120}candidates?' \
    "$skill_md never says it takes the candidates from the conversation"
  says 'gh issue create' \
    "$skill_md never says how an issue is filed (gh issue create)"
  says 'one (github )?issue per module' \
    "$skill_md never says it files one issue per module"
  says '(not|never)[^.]{0,40}(one )?(issue )?per smell' \
    "$skill_md never says it does not file one issue per smell"
  says 'acceptance criteri(on|a)[^.]{0,120}predicates?|predicates?[^.]{0,120}acceptance criteri(on|a)' \
    "$skill_md never says the acceptance criteria are phrased as predicates"
  says 'structural predicates?' \
    "$skill_md never says the predicates are structural"
  says 'runnable check[^.]{0,80}where one exists|where one exists[^.]{0,80}runnable check' \
    "$skill_md never says each predicate carries a runnable check where one exists"
else
  problems+=("want a SKILL.md at $skill_md, found none")
fi
report "$name"

# 3. Criterion 2 of #501: handed the path to the analysis's HTML report instead of candidates
#    in the conversation — a cleared context has lost the list, and the report on disk is all
#    that is left of it — the skill reads the candidates from that file and files the same
#    issues it would have filed from the conversation. Read as prose, like case 2.
name="$skill_md reads the candidates from the analysis's HTML report path and files the same issues"
problems=()
if [[ -f "$ROOT/$skill_md" ]]; then
  says 'path[^.]{0,80}html report|html report[^.]{0,80}path' \
    "$skill_md never says it accepts the path to the analysis's HTML report"
  says 'reads?[^.]{0,60}candidates?[^.]{0,60}(report|file)|candidates?[^.]{0,40}from (the|that) (html )?(report|file)' \
    "$skill_md never says it reads the candidates from that file"
  says 'same issues?' \
    "$skill_md never says it files the same issues it would have filed from the conversation"
else
  problems+=("want a SKILL.md at $skill_md, found none")
fi
report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
