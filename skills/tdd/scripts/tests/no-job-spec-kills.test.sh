#!/usr/bin/env bash
# Unit tests for the files under skills/ — none of them may end a background process by a
# job spec.
#
# Contract under test:
#   No file under skills/ ends a background process by a job spec, outside a comment.
#   An offender is reported as `<file>:<line>`. A site is exempted only by name in the
#   table below with a reason; an entry carrying no reason fails the run.
#   A kill by a recorded pid is not reported.
#
# Run: skills/tdd/scripts/tests/no-job-spec-kills.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"

SUBJECT='skills'

KILL_WORD='(^|[^[:alnum:]_.-])kill'
JOB_ARGS='([[:space:]]+[^%[:space:]]+)*[[:space:]]+'
JOB_SPEC='%[0-9]'
JOB_SPEC_KILL="$KILL_WORD$JOB_ARGS$JOB_SPEC"

declare -A EXEMPT=(
  [skills/tdd/scripts/tests/skill-leaf-env.test.sh:407]="a step title's text, single-quoted, that the case hands a launch line as data (#437): the backticks around it are the character under test, and a fixed launch never runs it; an unfixed one runs it in a bash -c with no job table, where it reaches no process at all"
)


source "$HERE/lib/harness.sh"

flat() { local s="$1"; printf '%s' "${s//$'\n'/\/}"; }

split_site() {
  local rest
  site_file="${1%%:*}"
  rest="${1#*:}"
  site_line="${rest%%:*}"
  site_text="${rest#*:}"
}

kill_lines() {
  local hit
  while IFS= read -r hit; do
    split_site "$hit"
    [[ "$site_text" =~ ^[[:space:]]*# ]] && continue
    printf '%s\n' "$hit"
  done < <(cd "$ROOT" && grep -rInE -- "$JOB_SPEC_KILL" "$SUBJECT")
  return 0
}

sites() {
  local hit
  while IFS= read -r hit; do
    split_site "$hit"
    [[ -n "${EXEMPT[$site_file:$site_line]:-}" ]] && continue
    printf '%s\n' "$hit"
  done < <(kill_lines)
  return 0
}

probe_no_file_kills_by_job_spec() {
  local site
  while IFS= read -r site; do
    split_site "$site"
    problems+=("$site_file:$site_line ends a background process by a job spec, which names it only in the job table of the shell that started it: once that shell is gone the kill reaches nobody and the process is left running, reparented to PID 1. Kill the pid it recorded instead — see skills/tdd/scripts/lib/background.sh: $(flat "$site_text")")
  done < <(sites)
  return 0
}

probe_every_exemption_carries_a_reason() {
  local key
  for key in "${!EXEMPT[@]}"; do
    [[ -n "${EXEMPT[$key]}" ]] && continue
    problems+=("the exemption entry [$key] carries no reason, so it exempts nothing: an entry is an exemption only when it says why a name that dies with the shell is the right one at that site")
  done
  return 0
}

name="no file under skills/ ends a background process by a job spec"
problems=()

probe_every_exemption_carries_a_reason
probe_no_file_kills_by_job_spec

report "$name"

probe_every_exemption_still_names_its_site() {
  local hit key
  local -A matched=()
  while IFS= read -r hit; do
    split_site "$hit"
    matched[$site_file:$site_line]=1
  done < <(kill_lines)
  for key in "${!EXEMPT[@]}"; do
    [[ -n "${matched[$key]:-}" ]] && continue
    [[ -e "$ROOT/${key%%:*}" ]] || continue
    problems+=("the exemption entry [$key] names a line that no longer ends a background process by a job spec, so it excuses nothing there: the site it was written for has moved, and its key must follow it")
  done
  return 0
}

name="every exemption names a line under skills/ that ends a background process by a job spec"
problems=()

probe_every_exemption_still_names_its_site

report "$name"

finish
