#!/usr/bin/env bash
# Unit test: no suite under skills/tdd/scripts/tests/unit/ runs a script under
# skills/tdd/scripts/ as a subprocess.
#
# Contract under test:
#   A line of a unit-tier suite, outside a comment, that names a script directly under
#   skills/tdd/scripts/ by path (`/<name>.sh`) and is neither a `source`/`.` line nor a
#   variable assignment runs that script. An offender is reported as `<suite>:<line>`.
#   An exemption carries a reason.
#
# Run: skills/tdd/scripts/tests/no-unit-subprocess.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"
tests_dir="$HERE"
scripts_dir="$HERE/.."
[[ -d "$HERE/unit" ]] || tests_dir="$HERE"

source "$HERE/lib/harness.sh"

flat() { local s="$1"; printf '%s' "${s//$'\n'/\/}"; }

declare -A EXEMPT=(
  [classify-bail.test.sh]="runs its script through its CLI entry point today; it meets the bar or moves to tests/ in the step that makes this guard green over the real unit/"
  [clear-refactor-pending.test.sh]="runs its script through its CLI entry point today; it meets the bar or moves to tests/ in the step that makes this guard green over the real unit/"
  [comment-class.test.sh]="runs its script through its CLI entry point today; it meets the bar or moves to tests/ in the step that makes this guard green over the real unit/"
  [cover-outcome.test.sh]="runs its script through its CLI entry point today; it meets the bar or moves to tests/ in the step that makes this guard green over the real unit/"
  [criterion-finished.test.sh]="runs its script through its CLI entry point today; it meets the bar or moves to tests/ in the step that makes this guard green over the real unit/"
  [next-pending-refactor.test.sh]="runs its script through its CLI entry point today; it meets the bar or moves to tests/ in the step that makes this guard green over the real unit/"
  [next-unchecked.test.sh]="runs its script through its CLI entry point today; it meets the bar or moves to tests/ in the step that makes this guard green over the real unit/"
  [red-divergence.test.sh]="runs its script through its CLI entry point today; it meets the bar or moves to tests/ in the step that makes this guard green over the real unit/"
  [step-budget.test.sh]="runs its script through its CLI entry point today; it meets the bar or moves to tests/ in the step that makes this guard green over the real unit/"
  [step-cost.test.sh]="runs its script through its CLI entry point today; it meets the bar or moves to tests/ in the step that makes this guard green over the real unit/"
  [stop-requested.test.sh]="runs its script through its CLI entry point today; it meets the bar or moves to tests/ in the step that makes this guard green over the real unit/"
)

names=()
for f in "$scripts_dir"/*.sh; do [[ -f "$f" ]] && names+=("${f##*/}"); done
script_list="$(IFS='|'; echo "${names[*]}")"

problems=()
shopt -s nullglob
for f in "$tests_dir"/unit/*.test.sh; do
  suite="${f##*/}"
  [[ -n "${EXEMPT[$suite]+x}" ]] && continue
  while IFS=$'\t' read -r lineno text; do
    [[ -n "$lineno" ]] || continue
    problems+=("$suite:$lineno runs a script under skills/tdd/scripts/ as a subprocess, with no exemption recorded: $(flat "$text")")
  done < <(awk -v scripts="$script_list" '
    BEGIN { n = split(scripts, arr, "|"); for (i = 1; i <= n; i++) is_script[arr[i]] = 1 }
    /^[ \t]*#/ { next }
    /^[ \t]*(source|\.)[ \t]/ { next }
    /^[ \t]*[A-Za-z_][A-Za-z0-9_]*=/ && $0 !~ /\$\(|`/ { next }
    {
      rest = $0
      while (match(rest, /\/[a-z0-9-]+\.sh/)) {
        tok = substr(rest, RSTART + 1, RLENGTH - 1)
        rest = substr(rest, RSTART + RLENGTH)
        if (tok in is_script) { print FNR "\t" $0; break }
      }
    }
  ' "$f")
done

report "no suite under skills/tdd/scripts/tests/unit/ runs a script under skills/tdd/scripts/ as a subprocess outside the exemptions recorded here"

finish
