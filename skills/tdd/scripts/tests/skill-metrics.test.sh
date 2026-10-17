#!/usr/bin/env bash
# Unit tests for what skills/tdd/SKILL.md tells the conductor to do with the run's metrics
# report, at both of the run's endings, read as text.
#
# Contract under test:
#   SKILL.md's `### 4. Draft PR` step runs, in this order, `gh api …/pulls?head=` for the URL
#   of the PR the plan commit already opened, `event.sh done pr=<pr-url>`, `metrics.sh`, a
#   `metrics:` commit of `.tdd/issue-<n>-metrics.md`, `push-branch.sh`, and `gh api -X PATCH`,
#   which carries the `### 📊 Metrics` block into the PR body; the same block goes into the
#   final `✅ Done` comment; SKILL.md's `## Bailing` section commits the same file on the
#   pushed branch and puts the block on the `⛔ Bailed` comment.
#
# Run: scripts/tests/skill-metrics.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"

skill_md="skills/tdd/SKILL.md"
skill_path="$ROOT/$skill_md"


source "$HERE/lib/harness.sh"
source "$HERE/lib/fenced-lines.sh"

records_of() {
  awk '
    function flush() { if (rec != "") { gsub(/[[:space:]]+/, " ", rec); print rec } rec = "" }
    /^[0-9]+\. / || /^[[:space:]]*- / { flush(); rec = $0; next }
    /^[[:space:]]*$/ { flush(); next }
    rec == "" { rec = $0; next }
    { rec = rec " " $0 }
    END { flush() }' | tr '[:upper:]' '[:lower:]'
}

section_records() {
  awk -v h="$1" -v closers="$2" \
    '$0 ~ closers { inside = (index($0, h) == 1); next } inside' "$skill_path" | records_of
}

first_record_line() {
  local records="$1" n line
  shift
  n=0
  while IFS= read -r line; do
    n=$((n + 1))
    local s ok=1
    for s in "$@"; do
      [[ "$line" == *"$s"* ]] || { ok=0; break; }
    done
    [[ "$ok" -eq 0 ]] || { echo "$n"; return 0; }
  done <<< "$records"
  return 1
}

record_at() { sed -n "${2}p" <<< "$1"; }

pr_records="$(section_records '### 4. Draft PR' '^## |^### ')"
bail_records="$(section_records '## Bailing' '^## ')"

offset_of() {
  [[ "$1" == *"$2"* ]] || return 1
  local before="${1%%"$2"*}"
  echo "${#before}"
}

first_fenced_line() {
  local n rest
  while IFS=$'\t' read -r n rest; do
    [[ "$rest" == *"$1"* ]] && { echo "$n"; return 0; }
  done <<< "$(fenced_lines "$skill_path" '' '### 4. Draft PR')"
  return 1
}

pr_read='pulls?head='
pr_edit='gh api -X PATCH'

finish
