#!/usr/bin/env bash
# Unit tests for where the /tdd-fix skill ships, what it calls itself, and what it asks the
# user for — like skill-identity.test.sh this suite belongs to no single script: its subject
# is a skill directory and the SKILL.md inside it, read as text, the way the session that
# follows it reads it.
# Zero-dependency plain-shell asserts, same idiom as skill-identity.test.sh.
#
# Why this exists (issue #111): filing a bug the way veri reads it is a second command, and
# the invocation name is the one thing every user touches — spelled in two places that must
# agree, the directory Claude Code loads the skill from and the `name:` field of its
# frontmatter. The other half of the same criterion is the intake: the one-line description
# is OPTIONAL, and what the skill does with it is ask only for what that line left out, in
# one short round. A skill that re-asks what the line already answered turns a one-line bug
# report into an interview, which is the cost ADR-0015 is about.
#
# Contract under test:
#   skills/tdd-fix/ is a directory, skills/tdd-fix/SKILL.md's frontmatter reads
#   `name: tdd-fix`, and its body says the description argument is optional, that it asks
#   only for what that line did not answer, and that it does so in one short round.
#
# Run: scripts/tests/skill-fix-identity.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
# The suite sits at skills/<skill>/scripts/tests, so four levels up is the repo root
# whichever name the skill holding it currently carries — the paths this case is about are
# spelled out in full below rather than derived from where this file happens to live.
ROOT="$(cd "$HERE/../../../.." && pwd)"

# The two halves of the identity, each written down exactly once: the directory Claude Code
# loads the skill from, and the command name its frontmatter must declare. Neither is derived
# from the other, so a half-finished rename — tree renamed, frontmatter not, or the reverse —
# still fails; and every message below quotes these rather than re-spelling them.
skill_dir="skills/tdd-fix"
want_name="tdd-fix"
skill_md="$skill_dir/SKILL.md"

pass=0 fail=0

# report <name> — close a case whose probes collected into the `problems` array: an empty
# array is a pass, otherwise one FAIL line for the case and one indented line per problem,
# so the output says which half of the contract broke rather than just that the case did.
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

# have_skill_md — true when the SKILL.md every case below reads exists; otherwise it records
# the one problem that explains why nothing else could be checked. Both cases need the same
# guard and the same sentence, so it is written down once here rather than at each of them.
have_skill_md() {
  [[ -f "$ROOT/$skill_md" ]] && return 0
  problems+=("want a SKILL.md at $skill_md, found none")
  return 1
}

# frontmatter_name <file> — the value of the first `name:` inside the leading `---` block,
# empty if the block or the field is missing. Only the first counts: the exit at the closing
# `---` stops a later `name:` in the prose from answering for it. Same helper, and the same
# reasoning, as skill-identity.test.sh's.
frontmatter_name() {
  awk 'NR == 1 && $0 == "---" { inside = 1; next }
       inside && $0 == "---" { exit }
       inside && sub(/^name:[[:space:]]*/, "") { print; exit }' "$1"
}

# body_text <file> — everything after the frontmatter block, normalised: emphasis marks and
# backticks dropped, because `**optional**` and "optional" are the same word, the case folded,
# and the whole joined onto one line so a sentence split over a line break still reads as one.
# The frontmatter is excluded on purpose: a `description:` field is written for the harness's
# command picker, and it must not be able to answer for the procedure the session reads.
body_text() {
  awk 'NR == 1 && $0 == "---" { inside = 1; next }
       inside && $0 == "---" { inside = 0; body = 1; next }
       body { print }' "$1" | tr -d '*`' | tr '[:upper:]' '[:lower:]' | tr '\n' ' '
}

# issue_body_template <file> — the first fenced block that carries a "## What happened" line:
# the issue body the skill tells the session to hand `gh issue create`, quoted verbatim rather
# than described, so this case reads the headings the way GitHub will receive them. Prints
# nothing when no such block exists. Unlike body_text above it normalises nothing: a heading
# is the literal line the conductor's spec capture looks for, so case and spacing count.
issue_body_template() {
  awk '
    /^[[:space:]]*```/ {
      if (inside) { if (found) { printf "%s", buf; exit } ; inside = 0; next }
      inside = 1; buf = ""; found = 0; next
    }
    inside {
      buf = buf $0 "\n"
      if ($0 ~ /^##[[:space:]]+What happened[[:space:]]*$/) found = 1
    }
  ' "$1"
}

# says <regex> <fact> — one thing the body has to carry, written as the regex of any wording
# that would carry it; <fact> names it once if nothing matches.
says() {
  [[ "$text" =~ $1 ]] || problems+=("$2")
}

# 1. The skill exists under the name a user types, and its intake is the one the criterion
#    describes. Both halves are one criterion: a document with the right words under a
#    directory Claude Code does not load is not a command, and a command that interviews the
#    user is not the one this issue asks for. The intake is read as prose because prose is
#    the whole of a SKILL.md — there is no script here to test, the skill ships none.
name="$skill_md is the /$want_name skill and asks only for what the optional description left out, in one short round"
problems=()
[[ -d "$ROOT/$skill_dir" ]] ||
  problems+=("want a directory at $skill_dir, found none")
if have_skill_md; then
  got="$(frontmatter_name "$ROOT/$skill_md")"
  [[ "$got" == "$want_name" ]] ||
    problems+=("$skill_md frontmatter: want name '$want_name', got $(printf '%q' "$got")")
  text="$(body_text "$ROOT/$skill_md")"
  if [[ -z "${text// /}" ]]; then
    # Fail closed: an empty body means not one claim below was tested, which must not read
    # as three passes.
    problems+=("$skill_md has no body after its frontmatter — the intake could not be read")
  else
    says 'description[^.]{0,80}optional|optional[^.]{0,80}description|omit[^.]{0,80}description' \
      "$skill_md never says the one-line description is optional"
    says '(only|just)[^.]{0,100}(left out|did not answer|didn.t answer|missing|unanswered)|(left out|did not answer|didn.t answer|unanswered)[^.]{0,100}(only|just)' \
      "$skill_md never says it asks only for what the description left out"
    says 'one[^.]{0,40}round|single[^.]{0,40}round|one[^.]{0,40}question|no essay' \
      "$skill_md never says the asking is one short round"
  fi
fi
report "$name"

# 2. The body it files is the one the conductor can read. `capture-spec.sh` copies the issue's
#    text into the spec a leaf is given, and the planner reads headings out of it, so the six
#    headings and their order are the interface between the two commands — a bug filed under
#    "## Repro" is a bug veri cannot pick up. Asserted against the template the SKILL.md quotes
#    rather than against prose about it, because the template is what a session copies; and
#    asserted as the exact list, in order, so a seventh heading is a failure too — "exactly the
#    six" is the criterion, not "at least the six". `## Blocked by` holding `None.` is part of
#    the same fact: the section exists so a reader sees there is nothing blocking, and an empty
#    one says something different from `None.`.
name="$skill_md quotes an issue body carrying exactly the six headings the conductor reads, with Blocked by holding None."
problems=()
want_headings='## What happened
## Expected
## Steps to reproduce
## Environment
## Acceptance criteria
## Blocked by'
if have_skill_md; then
  template="$(issue_body_template "$ROOT/$skill_md")"
  if [[ -z "$template" ]]; then
    problems+=("$skill_md quotes no issue body: no fenced block in it holds a '## What happened' line")
  else
    got_headings="$(grep '^##[^#]' <<<"$template" || true)"
    if [[ "$got_headings" != "$want_headings" ]]; then
      problems+=("$skill_md's issue body has the wrong headings:")
      problems+=("  want: $(printf '%s' "$want_headings" | tr '\n' '/')")
      problems+=("  got:  $(printf '%s' "$got_headings" | tr '\n' '/')")
    fi
    blocked="$(awk '/^##[[:space:]]+Blocked by[[:space:]]*$/ { seen = 1; next }
                    seen && NF { print; exit }' <<<"$template")"
    [[ "$blocked" == "None." ]] ||
      problems+=("$skill_md's issue body: want 'None.' under '## Blocked by', got $(printf '%q' "$blocked")")
  fi
fi
report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
