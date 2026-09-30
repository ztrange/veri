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
ROOT="$(cd "$HERE/../../../.." && pwd)"

skill_dir="skills/tdd-fix"
want_name="tdd-fix"
skill_md="$skill_dir/SKILL.md"

pass=0 fail=0

source "$HERE/lib/harness.sh"

have_skill_md() {
  [[ -f "$ROOT/$skill_md" ]] && return 0
  problems+=("want a SKILL.md at $skill_md, found none")
  return 1
}

frontmatter_name() {
  awk 'NR == 1 && $0 == "---" { inside = 1; next }
       inside && $0 == "---" { exit }
       inside && sub(/^name:[[:space:]]*/, "") { print; exit }' "$1"
}

fold_prose() {
  tr -d '*`' | tr '[:upper:]' '[:lower:]' | tr '\n' ' '
}

body_text() {
  awk 'NR == 1 && $0 == "---" { inside = 1; next }
       inside && $0 == "---" { inside = 0; body = 1; next }
       body { print }' "$1" | fold_prose
}

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

criteria_block() {
  awk '/^##[[:space:]]+Acceptance criteria[[:space:]]*$/ { seen = 1; next }
       seen && /^##[^#]/ { exit }
       seen { print }' <<<"$1" | fold_prose
}

have_body() {
  text="$(body_text "$ROOT/$skill_md")"
  [[ -n "${text// /}" ]] && return 0
  problems+=("$skill_md has no body after its frontmatter — the $1 could not be read")
  return 1
}

have_template() {
  template="$(issue_body_template "$ROOT/$skill_md")"
  [[ -n "$template" ]] && return 0
  problems+=("$skill_md quotes no issue body: no fenced block in it holds a '## What happened' line")
  return 1
}

says() {
  [[ "$text" =~ $1 ]] || problems+=("$2")
}

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

name="$skill_md's issue body writes one acceptance criterion per manifestation, each failing now and passing after the fix"
problems=()
if have_skill_md && have_template; then
  text="$(criteria_block "$template")"
  if [[ -z "${text// /}" ]]; then
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

name="$skill_md asks before starting the fix run and invokes /tdd only on yes"
problems=()
if have_skill_md && have_body "fix-run offer"; then
  says 'ask[^.]{0,120}(before|first)[^.]{0,120}(/tdd|fix run)|(before|first)[^.]{0,120}ask[^.]{0,120}(/tdd|fix run)' \
    "$skill_md never says it asks before starting the fix run"
  says 'only[^.]{0,80}yes|yes[^.]{0,80}only|if[^.]{0,40}yes|on a yes' \
    "$skill_md never says it invokes /tdd only on yes"
fi
report "$name"

name="README.md documents /$want_name beside /tdd, and $skill_dir ships no scripts"
problems=()
readme="README.md"
if [[ -f "$ROOT/$readme" ]]; then
  section="$(awk -v want="/$want_name" '
    /^##[^#]/ { if (found) exit; buf = "" }
    { buf = buf $0 "\n"; if (index($0, want)) found = 1 }
    END { if (found) printf "%s", buf }
  ' "$ROOT/$readme")"
  if [[ -z "$section" ]]; then
    problems+=("$readme never mentions /$want_name")
  else
    text="$(fold_prose <<<"$section")"
    says '/tdd[^-a-z]' \
      "$readme documents /$want_name in a section that never names /tdd"
    says 'bug' \
      "$readme never says /$want_name files a bug"
  fi
else
  problems+=("want a $readme at the repo root, found none")
fi
if [[ -d "$ROOT/$skill_dir" ]]; then
  shipped=()
  while IFS= read -r path; do
    [[ -n "$path" ]] && shipped+=("${path#"$ROOT/"}")
  done < <(find "$ROOT/$skill_dir" -mindepth 1 \
    \( -name '*.sh' -o \( -type d -name scripts \) -o \( -type f -perm -u+x \) \) 2>/dev/null)
  [[ "${#shipped[@]}" -eq 0 ]] ||
    problems+=("$skill_dir ships scripts and is meant to ship none: ${shipped[*]}")
fi
report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
