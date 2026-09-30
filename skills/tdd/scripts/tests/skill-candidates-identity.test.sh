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
ROOT="$(cd "$HERE/../../../.." && pwd)"

skill_dir="skills/tdd-candidates"
want_name="tdd-candidates"
skill_md="$skill_dir/SKILL.md"


source "$HERE/lib/harness.sh"

frontmatter_name() {
  awk 'NR == 1 && $0 == "---" { inside = 1; next }
       inside && $0 == "---" { exit }
       inside && sub(/^name:[[:space:]]*/, "") { print; exit }' "$1"
}

body_text() {
  awk 'NR == 1 && $0 == "---" { inside = 1; next }
       inside && $0 == "---" { inside = 0; body = 1; next }
       body { print }' "$1" | tr -d '*`' | tr '[:upper:]' '[:lower:]' | tr '\n' ' '
}

says() {
  [[ "$text" =~ $1 ]] || problems+=("$2")
}

not_filed='(not|never|nothing)[^.]{0,20}files?'

paged_lookup='gh api --paginate[^.]{0,80}/issues'

says_near() {
  says "$1[^.]{0,$3}$2|$2[^.]{0,$3}$1" "$4"
}

has_skill_md() {
  [[ -f "$ROOT/$skill_md" ]] && return 0
  problems+=("want a SKILL.md at $skill_md, found none")
  return 1
}

text=""
[[ -f "$ROOT/$skill_md" ]] && text="$(body_text "$ROOT/$skill_md")"

name="$skill_md is the /$want_name skill and says it shapes and files candidates without surveying, ranking or judging them"
problems=()
[[ -d "$ROOT/$skill_dir" ]] ||
  problems+=("want a directory at $skill_dir, found none")
if has_skill_md; then
  got="$(frontmatter_name "$ROOT/$skill_md")"
  [[ "$got" == "$want_name" ]] ||
    problems+=("$skill_md frontmatter: want name '$want_name', got $(printf '%q' "$got")")
  if [[ -z "${text// /}" ]]; then
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
fi
report "$name"

name="$skill_md files one issue per module from conversation candidates, criteria as predicates with a runnable check"
problems=()
if has_skill_md; then
  says_near 'candidates?' 'conversation' 120 \
    "$skill_md never says it takes the candidates from the conversation"
  says 'gh issue create' \
    "$skill_md never says how an issue is filed (gh issue create)"
  says 'one (github )?issue per module' \
    "$skill_md never says it files one issue per module"
  says '(not|never)[^.]{0,40}(one )?(issue )?per smell' \
    "$skill_md never says it does not file one issue per smell"
  says_near 'acceptance criteri(on|a)' 'predicates?' 120 \
    "$skill_md never says the acceptance criteria are phrased as predicates"
  says 'structural predicates?' \
    "$skill_md never says the predicates are structural"
  says_near 'runnable check' 'where one exists' 80 \
    "$skill_md never says each predicate carries a runnable check where one exists"
fi
report "$name"

name="$skill_md reads the candidates from the analysis's HTML report path and files the same issues"
problems=()
if has_skill_md; then
  says_near 'path' 'html report' 80 \
    "$skill_md never says it accepts the path to the analysis's HTML report"
  says 'reads?[^.]{0,60}candidates?[^.]{0,60}(report|file)|candidates?[^.]{0,40}from (the|that) (html )?(report|file)' \
    "$skill_md never says it reads the candidates from that file"
  says 'same issues?' \
    "$skill_md never says it files the same issues it would have filed from the conversation"
fi
report "$name"

name="$skill_md ends every issue with a final Test command: line and lists only real blockers under ## Blocked by"
problems=()
if has_skill_md; then
  says '(ends?|final|last)[^.]{0,80}test command:|test command:[^.]{0,80}(final|last) line' \
    "$skill_md never says each issue ends with a final Test command: line"
  says '## blocked by' \
    "$skill_md never says the issue carries a ## Blocked by section"
  says 'only real blockers?|real blockers? only' \
    "$skill_md never says it lists only real blockers there"
fi
report "$name"

name="$skill_md files nothing for a candidate with no checkable predicate and says which it skipped and why"
problems=()
if has_skill_md; then
  says '(no|without)[^.]{0,40}checkable predicates?' \
    "$skill_md never names a candidate with no checkable predicate"
  says_near 'checkable predicates?' "$not_filed" 120 \
    "$skill_md never says a candidate with no checkable predicate is not filed"
  says '(names?|says?|which)[^.]{0,80}skipped|skipped[^.]{0,80}(by name|which)' \
    "$skill_md never says it names which candidate it skipped"
  says_near 'skipped' '(why|reason)' 120 \
    "$skill_md never says why a candidate was skipped"
fi
report "$name"

name="$skill_md looks for an issue it already filed for a candidate and files no duplicate on a re-run"
problems=()
if has_skill_md; then
  says_near '(re-?runs?|again|second (run|pass))' 'duplicates?' 120 \
    "$skill_md never says a re-run files no duplicate"
  says_near '(already filed|already exists?|existing issue)' "$not_filed" 120 \
    "$skill_md never says a candidate whose issue already exists is not filed again"
fi
report "$name"

name="$skill_md recognises an already-filed candidate by a marker in the issue body, not by its title"
problems=()
if has_skill_md; then
  says_near '(marker|identifier)' 'body' 120 \
    "$skill_md never says each filed issue carries an identity marker in its body"
  says_near '(search|look|find|match)[a-z]*' '(marker|identifier)' 120 \
    "$skill_md never says the re-run looks for that marker"
  says_near '(not|never)[^.]{0,40}(depend|rely|rest)[a-z]*' 'title' 80 \
    "$skill_md never says the already-filed check does not depend on the issue title"
fi
report "$name"

name="$skill_md finds an already-filed marker however many issues the repository holds"
problems=()
if has_skill_md; then
  if [[ "$text" =~ --limit[[:space:]=]+[0-9]+ ]]; then
    problems+=("$skill_md caps the already-filed lookup at a fixed count: ${BASH_REMATCH[0]}")
  fi
  says "$paged_lookup" \
    "$skill_md never lists the existing issues page by page, uncapped (gh api --paginate over the issues endpoint)"
  says '(however many|no matter how many|regardless of how many)[^.]{0,40}issues?' \
    "$skill_md never says the lookup finds the marker however many issues the repository holds"
fi
report "$name"

finish
