#!/usr/bin/env bash
# Unit tests for the suites in this directory — a suite that declares `pipefail` must not
# end a pipeline in a reader that exits early.
#
# Contract under test:
#   No suite under this directory that declares `pipefail` ends a pipeline in a reader that
#   leaves before EOF — a `grep` whose options carry `q`, or a `head`. An offender is
#   reported as `<suite>:<line>`. A site is exempted only by name in the table below with
#   a reason; an entry carrying no reason fails the run. A suite without `pipefail` is not
#   reported.
#   The same holds for every suite `make test` would run, `unit/` included.
#
# Run: skills/tdd/scripts/tests/no-sigpipe-pipelines.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"

ROOT="$(cd "$HERE/../../../.." && pwd)"

PIPEFAIL_DECL='^[[:space:]]*set[[:space:]].*pipefail'

GREP_READER='(grep|egrep|fgrep)([[:space:]]+-[A-Za-z]*)*[[:space:]]+-[A-Za-z]*q'
HEAD_READER='head([[:space:]]|$)'
READER="($GREP_READER|$HEAD_READER)"
PIPE_INTO_READER="(^|[^|])\\|[[:space:]]*[^|]*(^|[[:space:]])$READER"

WRAPPING_PIPE='(^|[^|])\|[[:space:]]*$'
READER_OPENS="^[[:space:]]*$READER"

declare -A EXEMPT=(
)


source "$HERE/lib/harness.sh"
source "$HERE/lib/exemption-reasons.sh"

flat() { local s="$1"; printf '%s' "${s//$'\n'/\/}"; }

declares_pipefail() { grep -Eq "$PIPEFAIL_DECL" "$1"; }

wrapped_sites() {
  local file="$1" hit lineno scan rc=0
  local -A ends_in_pipe=()
  scan="$(grep -nE "$WRAPPING_PIPE" "$file")" || { (( $? > 1 )) && rc=2; }
  while IFS= read -r hit; do
    [[ -n "$hit" ]] || continue
    ends_in_pipe["${hit%%:*}"]=1
  done <<< "$scan"
  scan="$(grep -nE "$READER_OPENS" "$file")" || { (( $? > 1 )) && rc=2; }
  while IFS= read -r hit; do
    [[ -n "$hit" ]] || continue
    lineno="${hit%%:*}"
    [[ -n "${ends_in_pipe[$((lineno - 1))]:-}" ]] || continue
    printf '%s\n' "$hit"
  done <<< "$scan"
  return "$rc"
}

loop_break_sites() {
  awk '
    /^[[:space:]]*#/ { next }
    { piped = /(^|[^|])\|[[:space:]]*(while|until)([[:space:]]|$)/ }
    piped || /^[[:space:]]*(while|until|for)([[:space:]]|$)/ {
      depth++; broke[depth] = 0
      fed[depth] = piped ? NR ":" $0 : ""
    }
    depth > 0 && /(^|[[:space:];&|])break([[:space:];]|$)/ { broke[depth] = 1 }
    depth > 0 && /(^[[:space:]]*|;[[:space:]]*)done([[:space:];]|$)/ {
      if (broke[depth] && fed[depth] != "") print fed[depth]
      else if (broke[depth] && /done[[:space:]]*<[[:space:]]*<\(/) print NR ":" $0
      depth--
    }
  ' "$1"
}

unexempted_sites() {
  local file="$1" name hit lineno text scan rc=0
  local -A seen=()
  name="$(basename "$file")"
  scan="$(grep -nE "$PIPE_INTO_READER" "$file")" || { (( $? > 1 )) && rc=2; }
  scan+=$'\n'"$(wrapped_sites "$file")" || rc=2
  scan+=$'\n'"$(loop_break_sites "$file")"
  declares_pipefail "$file" || return "$rc"
  while IFS= read -r hit; do
    [[ -n "$hit" ]] || continue
    lineno="${hit%%:*}"
    text="${hit#*:}"
    [[ "$text" =~ ^[[:space:]]*# ]] && continue
    [[ -n "${EXEMPT[$name:$lineno]:-}" ]] && continue
    [[ -n "${seen[$lineno]:-}" ]] && continue
    seen["$lineno"]=1
    printf '%s:%s\n' "$lineno" "$text"
  done <<< "$scan"
  return "$rc"
}

probe_no_pipefail_suite_ends_a_pipeline_in_an_early_exiting_reader() {
  local f name site sites
  for f in "$HERE"/*.test.sh; do
    [[ -e "$f" ]] || continue
    name="$(basename "$f")"
    sites="$(unexempted_sites "$f")" || grep_scanner_failed 2 "$name"
    while IFS= read -r site; do
      [[ -n "$site" ]] || continue
      problems+=("$name:${site%%:*} ends a pipeline in a reader that leaves before EOF, under a suite that declares pipefail, so the status asserted on is the writer's SIGPIPE rather than the reader's answer: $(flat "${site#*:}")")
    done <<< "$sites"
  done
  return 0
}


name="no suite under skills/tdd/scripts/tests/ that declares pipefail ends a pipeline in a reader that leaves before EOF"
problems=()

probe_every_exemption_carries_a_reason "an entry is an exemption only when it says why the reader's early exit is the point at that site"
probe_no_pipefail_suite_ends_a_pipeline_in_an_early_exiting_reader

report "$name"

roster() { make -C "$ROOT" -n "$1" 2>&1 | grep -o '[^ ]*\.test\.sh' | sort -u; }

probe_no_suite_the_target_runs_ends_a_pipeline_in_an_early_exiting_reader() {
  local rel site sites
  local -a listed=()
  while IFS= read -r rel; do
    [[ -n "$rel" ]] || continue
    listed+=("$rel")
    sites="$(unexempted_sites "$ROOT/$rel")" || grep_scanner_failed 2 "$rel"
    while IFS= read -r site; do
      [[ -n "$site" ]] || continue
      problems+=("$rel:${site%%:*} ends a pipeline in a reader that leaves before EOF, under a suite that declares pipefail, so \`make test\` — the baseline preflight reads, the Green leaf runs and both blind verifiers run — asserts on the writer's SIGPIPE rather than the reader's answer: $(flat "${site#*:}")")
    done <<< "$sites"
  done < <(roster test)
  [[ "${#listed[@]}" -gt 0 ]] ||
    echo "note: \`make -n test\` named no suite at all, so no roster was read: nothing this case could ask about"
  return 0
}

name="no suite \`make test\` runs that declares pipefail ends a pipeline in a reader that leaves before EOF"
problems=()

probe_no_suite_the_target_runs_ends_a_pipeline_in_an_early_exiting_reader

report "$name"

probe_no_recipe_ends_a_pipeline_in_an_early_exiting_reader() {
  local site sites
  sites="$(grep -nE "$PIPE_INTO_READER" "$ROOT/Makefile")" || grep_scanner_failed $? Makefile
  while IFS= read -r site; do
    [[ -n "$site" ]] || continue
    [[ -n "${EXEMPT[Makefile:${site%%:*}]:-}" ]] && continue
    problems+=("Makefile:${site%%:*} ends a pipeline in a reader that leaves before EOF, so the writer feeding it can die of SIGPIPE, complain and fail the recipe over an answer the reader already had: $(flat "${site#*:}")")
  done <<< "$sites"
  return 0
}

name="no Makefile recipe line ends a pipeline in a reader that leaves before EOF"
problems=()

probe_no_recipe_ends_a_pipeline_in_an_early_exiting_reader

report "$name"

finish
