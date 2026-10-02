#!/usr/bin/env bash
# Unit tests for the scripts whose module exists under veri/ — none of them may hold Python
# source.
#
# Contract under test:
#   A script skills/tdd/scripts/<name>.sh whose module veri/<module>.py exists (an underscore
#   in the module is a hyphen in the script) feeds python3 no heredoc and no -c string,
#   outside a comment. An offender is reported as `<script>:<line>`. A script with no module
#   under veri/ is not read.
#
# Run: skills/tdd/scripts/tests/no-python-in-ported-scripts.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"

SCRIPTS='skills/tdd/scripts'

PYTHON_SOURCE='(^|[^[:alnum:]_.-])python3([[:space:]].*)?(<<|[[:space:]]-c([[:space:]]|$))'

source "$HERE/lib/harness.sh"

flat() { local s="$1"; printf '%s' "${s//$'\n'/\/}"; }

ported_scripts() {
  local module script
  for module in "$ROOT/$SCRIPTS"/veri/*.py; do
    module="$(basename "$module" .py)"
    script="$SCRIPTS/${module//_/-}.sh"
    [[ -f "$ROOT/$script" ]] && printf '%s\n' "$script"
  done
  return 0
}

probe_no_ported_script_holds_python() {
  local script hit line text
  while IFS= read -r script; do
    while IFS= read -r hit; do
      line="${hit%%:*}"
      text="${hit#*:}"
      [[ "$text" =~ ^[[:space:]]*# ]] && continue
      problems+=("$script:$line feeds python3 Python source, but its module exists under $SCRIPTS/veri/: move the program into that module and call it once, as a command: $(flat "$text")")
    done < <(grep -nE -- "$PYTHON_SOURCE" "$ROOT/$script")
  done < <(ported_scripts)
  return 0
}

name="no script whose module exists under veri/ holds Python source"
problems=()
probe_no_ported_script_holds_python
report "$name"

finish
