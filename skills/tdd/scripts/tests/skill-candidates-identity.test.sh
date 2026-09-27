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

# not_filed — the words that say the skill files nothing for a candidate, near enough to a
# verb of filing that the sentence is about filing it.
not_filed='(not|never|nothing)[^.]{0,20}files?'

# says_near <a> <b> <gap> <fact> — the body has <a> and <b> in one sentence, at most <gap>
# characters apart, in either order.
says_near() {
  says "$1[^.]{0,$3}$2|$2[^.]{0,$3}$1" "$4"
}

# has_skill_md — true when the SKILL.md exists; otherwise records that as the case's problem,
# so each case reports a missing file in the same words and reads nothing further.
has_skill_md() {
  [[ -f "$ROOT/$skill_md" ]] && return 0
  problems+=("want a SKILL.md at $skill_md, found none")
  return 1
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
if has_skill_md; then
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
fi
report "$name"

# 2. Criterion 1 of #501: handed candidates in the conversation, the skill files one GitHub
#    issue per module — not one per smell, since a single smell is one step and a run's fixed
#    overhead is too large to spend on one — and each issue's acceptance criteria are
#    structural predicates carrying a runnable check where one exists. Read as prose: the
#    procedure is the whole of what the session filing the issues follows.
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

# 3. Criterion 2 of #501: handed the path to the analysis's HTML report instead of candidates
#    in the conversation — a cleared context has lost the list, and the report on disk is all
#    that is left of it — the skill reads the candidates from that file and files the same
#    issues it would have filed from the conversation. Read as prose, like case 2.
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

# 4. Criterion 3 of #501: every issue the skill files ends its body with a final
#    `Test command:` line — the line veri reads to know how to run the issue's tests — and
#    lists under `## Blocked by` only real blockers, since veri reads every #N there as one
#    and would hold the issue back for a mere reference. Read as prose, like case 2.
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

# 5. Criterion 4 of #501: a candidate with no checkable predicate — nothing about the tree
#    that is true or false and a check could settle — is not filed, since an issue whose
#    criteria no verifier can hold the code against is one veri cannot finish; and the skill
#    says which candidate it skipped and why, so a silent drop never reads as a complete
#    filing. Read as prose, like case 2.
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

# 6. Criterion 5 of #501: re-running the skill over candidates it has already filed files no
#    duplicate — a second pass after a cleared context, or over the same report, is the
#    normal way the skill gets re-run, and a queue holding the same module twice is two runs
#    spent on one piece of work. So before filing, it looks among the repository's existing
#    issues for one it already filed for that candidate, and files nothing when one is there.
#    Read as prose, like case 2.
name="$skill_md looks for an issue it already filed for a candidate and files no duplicate on a re-run"
problems=()
if has_skill_md; then
  says_near '(re-?runs?|again|second (run|pass))' 'duplicates?' 120 \
    "$skill_md never says a re-run files no duplicate"
  says 'gh (issue list|search issues)' \
    "$skill_md never says how it finds the issues it already filed (gh issue list or gh search issues)"
  says_near '(already filed|already exists?|existing issue)' "$not_filed" 120 \
    "$skill_md never says a candidate whose issue already exists is not filed again"
fi
report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
