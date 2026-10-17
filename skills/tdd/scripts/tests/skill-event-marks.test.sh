#!/usr/bin/env bash
# Unit tests for the conductor's own marks in the run's event log, as skills/tdd/SKILL.md
# prescribes them, read as text.
#
# Contract under test:
#   For each of the conductor's seven marks — step-start, step-done, pin, revise, bail,
#   done, resume — SKILL.md prescribes an `event.sh <mark>` call in the same instruction
#   as the issue comment that mark mirrors. `step-start` has no comment of its own (a step
#   begins where `next-unchecked.sh` hands one over), so its anchor is that command.
#
# Run: scripts/tests/skill-event-marks.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"
skill_md="skills/tdd/SKILL.md"


source "$HERE/lib/harness.sh"

instructions() {
  awk '
    function flush() { if (rec != "") { gsub(/[[:space:]]+/, " ", rec); print rec } rec = "" }
    /^[0-9]+\. / || /^[[:space:]]*- / { flush(); rec = $0; next }
    /^[[:space:]]*$/ { flush(); next }
    rec == "" { rec = $0; next }
    { rec = rec " " $0 }
    END { flush() }' "$ROOT/$skill_md" | tr '[:upper:]' '[:lower:]'
}

calls_event() {
  [[ "$1" =~ event\.sh[[:space:]]+"$2"([^a-z0-9-]|$) ]]
}

at_over_budget() {
  [[ "$1" =~ event\.sh\ "$2".*[[:space:]]at=over-budget([[:space:]]|$) ]]
}

cost_check_at() {
  grep -m1 -nE "^#### The step's cost check" "$ROOT/$skill_md" | cut -d: -f1
}

exit_bullet_after() {
  awk -v from="$1" -v n="$2" 'NR > from && index($0, "- **exit " n " ") == 1 { print NR; exit }' "$ROOT/$skill_md"
}

cost_bullet_at() {
  local section_at
  section_at="$(cost_check_at)"
  [[ -z "$section_at" ]] || exit_bullet_after "$section_at" "$1"
}

cost_branch() {
  local from to=""
  from="$(cost_bullet_at "$1")"
  [[ -z "$from" ]] || to="$(exit_bullet_after "$from" "$2")"
  [[ -z "$to" ]] || echo "$from $to"
}

insertion_re='\$s/add-ledger-step\.sh'

have_records() {
  [[ -n "$records" ]] && return 0
  problems+=("$skill_md has no instructions to read — $1 could not be checked")
  return 1
}

mark() {
  local event="$1" what="$2" line re anchored=""
  shift 2
  while IFS= read -r line; do
    for re in "$@"; do
      [[ "$line" =~ $re ]] || continue 2
    done
    [[ -n "$anchored" ]] || anchored="$line"
    calls_event "$line" "$event" && { marked="$line"; return 0; }
  done <<< "$records"
  if [[ -z "$anchored" ]]; then
    problems+=("$skill_md no longer $what — where \`event.sh $event\` belongs could not be read")
  else
    problems+=("$skill_md $what but calls no \`event.sh $event\` beside it: $(printf '%.130s' "$anchored")")
  fi
}

comment_mark() {
  local event="$1" heading="$2"
  shift 2
  mark "$event" "posts the \`$heading\` comment" "$@" 'comment'
}

refactor_mark() {
  mark refactor 'posts the `### 🛠️ Refactor` comment' '### [^ ]+ refactor( |`|$)' 'post' 'rev-list --count'
}

refactor_call() {
  [[ "$marked" =~ (event\.sh[[:space:]]+refactor([^a-z0-9-][^\`]*)?) ]]
  call="${BASH_REMATCH[1]}"
}

finish
