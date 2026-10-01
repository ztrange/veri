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
  [run-conductor.test.sh:34]="a line of the POSIX-sh stub \`claude\` the suite writes in a heredoc, not of the suite: that shell sets no pipefail, so the sed's SIGPIPE is never a status anything reads, and bash's process substitution is not available there to repair it with"
)


source "$HERE/lib/harness.sh"

flat() { local s="$1"; printf '%s' "${s//$'\n'/\/}"; }

declares_pipefail() { grep -Eq "$PIPEFAIL_DECL" "$1"; }

wrapped_sites() {
  local file="$1" hit lineno
  local -A ends_in_pipe=()
  while IFS= read -r hit; do
    ends_in_pipe["${hit%%:*}"]=1
  done < <(grep -nE "$WRAPPING_PIPE" "$file")
  while IFS= read -r hit; do
    lineno="${hit%%:*}"
    [[ -n "${ends_in_pipe[$((lineno - 1))]:-}" ]] || continue
    printf '%s\n' "$hit"
  done < <(grep -nE "$READER_OPENS" "$file")
  return 0
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
  local file="$1" name hit lineno text
  local -A seen=()
  declares_pipefail "$file" || return 0
  name="$(basename "$file")"
  while IFS= read -r hit; do
    lineno="${hit%%:*}"
    text="${hit#*:}"
    [[ "$text" =~ ^[[:space:]]*# ]] && continue
    [[ -n "${EXEMPT[$name:$lineno]:-}" ]] && continue
    [[ -n "${seen[$lineno]:-}" ]] && continue
    seen["$lineno"]=1
    printf '%s:%s\n' "$lineno" "$text"
  done < <(grep -nE "$PIPE_INTO_READER" "$file"; wrapped_sites "$file"; loop_break_sites "$file")
  return 0
}

probe_no_pipefail_suite_ends_a_pipeline_in_an_early_exiting_reader() {
  local f name site
  for f in "$HERE"/*.test.sh; do
    [[ -e "$f" ]] || continue
    name="$(basename "$f")"
    while IFS= read -r site; do
      problems+=("$name:${site%%:*} ends a pipeline in a reader that leaves before EOF, under a suite that declares pipefail, so the status asserted on is the writer's SIGPIPE rather than the reader's answer: $(flat "${site#*:}")")
    done < <(unexempted_sites "$f")
  done
  return 0
}

probe_every_exemption_carries_a_reason() {
  local key
  for key in "${!EXEMPT[@]}"; do
    [[ -n "${EXEMPT[$key]}" ]] && continue
    problems+=("the exemption entry [$key] carries no reason, so it exempts nothing: an entry is an exemption only when it says why the reader's early exit is the point at that site")
  done
  return 0
}

name="no suite under skills/tdd/scripts/tests/ that declares pipefail ends a pipeline in a reader that leaves before EOF"
problems=()

probe_every_exemption_carries_a_reason
probe_no_pipefail_suite_ends_a_pipeline_in_an_early_exiting_reader

report "$name"

roster() { make -C "$ROOT" -n "$1" 2>&1 | grep -o '[^ ]*\.test\.sh' | sort -u; }

probe_no_suite_the_target_runs_ends_a_pipeline_in_an_early_exiting_reader() {
  local rel site
  local -a listed=()
  while IFS= read -r rel; do
    [[ -n "$rel" ]] || continue
    listed+=("$rel")
    while IFS= read -r site; do
      problems+=("$rel:${site%%:*} ends a pipeline in a reader that leaves before EOF, under a suite that declares pipefail, so \`make test\` — the baseline preflight reads, the Green leaf runs and both blind verifiers run — asserts on the writer's SIGPIPE rather than the reader's answer: $(flat "${site#*:}")")
    done < <(unexempted_sites "$ROOT/$rel")
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
  local site
  while IFS= read -r site; do
    [[ -n "${EXEMPT[Makefile:${site%%:*}]:-}" ]] && continue
    problems+=("Makefile:${site%%:*} ends a pipeline in a reader that leaves before EOF, so the writer feeding it can die of SIGPIPE, complain and fail the recipe over an answer the reader already had: $(flat "${site#*:}")")
  done < <(grep -nE "$PIPE_INTO_READER" "$ROOT/Makefile")
  return 0
}

name="no Makefile recipe line ends a pipeline in a reader that leaves before EOF"
problems=()

probe_no_recipe_ends_a_pipeline_in_an_early_exiting_reader

report "$name"

probe_count_line_check_lets_its_writer_finish() {
  local check scratch status
  if [[ ! -e "$ROOT/Makefile" ]]; then
    echo "note: no Makefile at $ROOT, so no count-line check was run: nothing this case could ask about"
    return 0
  fi
  check="$(awk '/tail -n 1 "\$\$suite_out"/ { print; if ((getline nxt) > 0) print nxt; exit }' "$ROOT/Makefile")"
  if [[ -z "$check" ]]; then
    problems+=("no count-line check reading \"\$\$suite_out\" through tail was found in the Makefile, so the criterion went unasked")
    return 0
  fi
  eval "$(make -s -C "$ROOT" count-line-guard)"
  check="${check//$'\\\n'/ }"
  check="${check%%||*}"
  check="${check//\$\$/\$}"
  check="${check//\$(COUNT_LINE)/$COUNT_LINE}"
  scratch="$(scratch_dir)"
  cat > "$scratch/tail" <<'STUB'
#!/bin/sh
printf '13 passed, 0 failed\n'
if dd if=/dev/zero bs=65536 count=16 2>/dev/null; then echo finished > "$STUB_MARK"; else echo cut > "$STUB_MARK"; fi
STUB
  chmod 755 "$scratch/tail"
  STUB_MARK="$scratch/mark" PATH="$scratch:$PATH" suite_out=/dev/null sh -c "$check"
  status=$?
  [[ "$status" -eq 0 ]] ||
    problems+=("the count-line check exited $status over a writer whose first line is a count line: $(flat "$check")")
  [[ "$(cat "$scratch/mark" 2>/dev/null)" == finished ]] ||
    problems+=("the count-line check's writer was cut off mid-write ($(cat "$scratch/mark" 2>/dev/null || echo 'no mark')), so its reader left before EOF: $(flat "$check")")
  rm -rf "$scratch"
  return 0
}

name="make test's count-line check reads the suite's last line to EOF, so its writer is never cut off (#524)"
problems=()

probe_count_line_check_lets_its_writer_finish

report "$name"

finish
