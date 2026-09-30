#!/usr/bin/env bash
# Unit tests for the files under skills/ — none of them may end a background process by a
# job spec. Like no-sigpipe-pipelines.test.sh and no-docs-reads.test.sh this suite has no
# script as its subject: its subject is the tree it is run in. Zero-dependency plain-shell
# asserts, same idiom as no-sigpipe-pipelines.test.sh.
#
# Why this exists (issue #424): a job spec names a row in the job table of the shell that
# started the process, and that table dies with the shell. Once it is gone the number means
# nothing, the child is reparented to PID 1, and nothing is left that knows its identity —
# so the kill reaches no one, and a redirection of its complaint to /dev/null makes that
# silent. Observed 2026-09-22 on this machine: ten orphaned busy-loops, all PPID 1, ~988% of
# CPU between them, twelve and thirteen hours old, quietly distorting every timing this
# repository measures. Two different shell snapshots were represented among them, so this is
# not one bad command but a shape that gets written more than once. `lib/background.sh` is
# the repair — it kills the pid it recorded, a system-wide name that works from any shell —
# and this suite is what stops the next site being written.
#
# Contract under test:
#   No file under skills/ ends a background process by a job spec. A file that does is
#   reported as `<file>:<line>` — the address, not the file, because that is what sends the
#   next author to the site. A site where the job spec is the point is exempted by name in
#   the table below, and only with the reason that says why; an entry carrying no reason
#   fails the run rather than silencing anything.
#
# Killing a background process is not the offence: killing it by a name that dies with the
# shell is. A check that refused every `kill` in the tree would be deleted by the first
# author it blocked, taking the real one with it — and `lib/background.sh`, the fix this
# issue shipped, would be its first victim. So a kill by a recorded pid is left alone.
#
# A comment is not a site: it runs nothing, and the prose here and in `lib/background.sh`
# discusses the shape at length. This suite reads itself along with the rest, which is the
# discipline it asks for: no line below spells the shape it looks for — the pattern is
# assembled from two halves, and a failure quotes the offending line rather than carrying
# one of its own.
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
  [skills/tdd/scripts/tests/skill-leaf-env.test.sh:441]="a step title's text, single-quoted, that the case hands a launch line as data (#437): the backticks around it are the character under test, and a fixed launch never runs it; an unfixed one runs it in a bash -c with no job table, where it reaches no process at all"
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
