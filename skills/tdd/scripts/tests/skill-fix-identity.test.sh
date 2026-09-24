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

# fold_prose — the normalisation every `says` match is made against, reading its prose on
# stdin: emphasis marks and backticks dropped, because `**optional**` and "optional" are the
# same word, the case folded, and the whole joined onto one line so a sentence split over a
# line break still reads as one. body_text and criteria_block both feed `says`, so they have
# to normalise identically — which they do by both ending in this one pipeline.
fold_prose() {
  tr -d '*`' | tr '[:upper:]' '[:lower:]' | tr '\n' ' '
}

# body_text <file> — everything after the frontmatter block, folded by fold_prose above. The
# frontmatter is excluded on purpose: a `description:` field is written for the harness's
# command picker, and it must not be able to answer for the procedure the session reads.
body_text() {
  awk 'NR == 1 && $0 == "---" { inside = 1; next }
       inside && $0 == "---" { inside = 0; body = 1; next }
       body { print }' "$1" | fold_prose
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

# criteria_block <template> — the lines under `## Acceptance criteria` in the quoted issue
# body, up to the next heading, folded by fold_prose the way body_text's prose is. The block
# is read out of the template rather than out of the surrounding prose because the template is
# what a session copies into `gh issue create`, and so it is the only place a criterion the
# skill writes can come from.
criteria_block() {
  awk '/^##[[:space:]]+Acceptance criteria[[:space:]]*$/ { seen = 1; next }
       seen && /^##[^#]/ { exit }
       seen { print }' <<<"$1" | fold_prose
}

# have_body <what> — true when the SKILL.md has prose after its frontmatter, left in `text`
# for the caller; otherwise it records that <what> could not be read. Cases 1 and 4 both read
# that prose and both have to fail closed on an empty body — an unread body must not read as
# a handful of passes — so the guard is written once and named by what the caller was after.
have_body() {
  text="$(body_text "$ROOT/$skill_md")"
  [[ -n "${text// /}" ]] && return 0
  problems+=("$skill_md has no body after its frontmatter — the $1 could not be read")
  return 1
}

# have_template — true when the SKILL.md quotes an issue body, left in `template` for the
# caller; otherwise it records the one problem that explains why nothing else could be read.
# Cases 2 and 3 both read that block and both fail the same way when it is missing, so the
# guard and its sentence live here once, the way have_skill_md's do.
have_template() {
  template="$(issue_body_template "$ROOT/$skill_md")"
  [[ -n "$template" ]] && return 0
  problems+=("$skill_md quotes no issue body: no fenced block in it holds a '## What happened' line")
  return 1
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
  if have_body intake; then
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
if have_skill_md && have_template; then
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
report "$name"

# 3. The criteria it writes are the shape veri can act on. A criterion is what the planner
#    turns into steps and what a blind verifier is judged against, so a bug filed with one
#    vague criterion covering three separate misbehaviours plans as one step that cannot go
#    green, and a criterion phrased as a wish ("the bug is fixed") gives the verifier nothing
#    to run. The criterion this case pins is the pair: one criterion per manifestation, each
#    in the reproduction-fails-now-and-passes-after-the-fix shape. Read, like case 2, out of
#    the template the SKILL.md quotes — prose about criteria is not what gets copied into the
#    issue.
name="$skill_md's issue body writes one acceptance criterion per manifestation, each failing now and passing after the fix"
problems=()
if have_skill_md && have_template; then
  text="$(criteria_block "$template")"
  if [[ -z "${text// /}" ]]; then
    # Fail closed, as case 1 does: an empty section means not one of the four claims
    # below was tested, which must not read as four passes.
    problems+=("$skill_md's issue body has nothing under '## Acceptance criteria'")
  else
    says '- \[ \]' \
      "$skill_md's issue body writes no '- [ ]' checkbox under '## Acceptance criteria'"
    says 'one[^.]{0,40}per manifestation|per manifestation' \
      "$skill_md's issue body never says one criterion per manifestation"
    says '(reproduction|repro)[^.]{0,80}fails[^.]{0,80}(current|today|now|unfixed)' \
      "$skill_md's issue body never says the reproduction fails on the current code"
    says 'passes[^.]{0,60}(after the fix|once fixed|when fixed)' \
      "$skill_md's issue body never says the reproduction passes after the fix"
  fi
fi
report "$name"

# 4. The labels it puts on the issue are what makes veri able to take it at all. `bug` is what
#    tells a reader — and `solvable-issues.sh`'s second band — that this is a defect rather than
#    a feature, and the opt-in label is the whole of the consent: `solvable-issues.sh:100` reads
#    `${VERI_LABEL:-ready-for-agent}`, so an issue without it is one veri never picks up, however
#    well it is written. The scope suffix is the same label narrowed — a user who names a scope
#    gets `ready-for-agent:<scope>`, not a second label — and the creation clause is the failure
#    path: `bug` is GitHub's own default label, so it is there until a repo removes it, and on the
#    repo that did, filing without creating it first is a `gh issue create` that fails rather than
#    an issue filed unlabelled. Read as prose, like case 1: the skill ships no scripts, so what
#    the session does about labels is only ever what its SKILL.md tells it to.
name="$skill_md labels the issue bug and the scope's opt-in label, creating bug where the repo lacks it"
problems=()
if have_skill_md && have_body labelling; then
  says 'labels?[^.]{0,120}bug' \
    "$skill_md never says the issue is labelled bug"
  says 'ready-for-agent[^.:]{0,80}default|default[^.]{0,80}ready-for-agent' \
    "$skill_md never says ready-for-agent is the opt-in label by default"
  says 'ready-for-agent:[^ ]*[^.]{0,100}scope|scope[^.]{0,100}ready-for-agent:' \
    "$skill_md never says a named scope makes the opt-in label ready-for-agent:<scope>"
  says 'creates?[^.]{0,120}bug label|bug label[^.]{0,120}(if|when)[^.]{0,80}(lacks|missing|absent|removed|no )|gh label create' \
    "$skill_md never says it creates the bug label where the repo lacks it"
fi
report "$name"

# 5. The fix run is a second decision, and it costs money. Filing is free; `/tdd <n>` spends a
#    conductor and a leaf per step, so a skill that rolls straight on from the filed issue into
#    the run has made that spend on the user's behalf without asking. The criterion is the pair:
#    the skill asks, once, before starting the fix run, and it invokes `/tdd` only when the
#    answer is yes — anything else leaves the issue filed and the run unstarted. Read as prose,
#    like cases 1 and 4: the skill ships no scripts, so the asking is only ever what its
#    SKILL.md tells the session to do.
name="$skill_md asks before starting the fix run and invokes /tdd only on yes"
problems=()
if have_skill_md && have_body "fix-run offer"; then
  says 'ask[^.]{0,120}(before|first)[^.]{0,120}(/tdd|fix run)|(before|first)[^.]{0,120}ask[^.]{0,120}(/tdd|fix run)' \
    "$skill_md never says it asks before starting the fix run"
  says 'only[^.]{0,80}yes|yes[^.]{0,80}only|if[^.]{0,40}yes|on a yes' \
    "$skill_md never says it invokes /tdd only on yes"
fi
report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
