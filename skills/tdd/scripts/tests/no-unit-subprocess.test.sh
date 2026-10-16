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
scripts_dir="$HERE/.."

source "$HERE/lib/harness.sh"

flat() { local s="$1"; printf '%s' "${s//$'\n'/\/}"; }

declare -A EXEMPT=(
)

problems=()
for key in "${!EXEMPT[@]}"; do
  [[ -n "${EXEMPT[$key]}" ]] || problems+=("exemption entry [$key] carries no reason")
done

names=()
for f in "$scripts_dir"/*.sh; do [[ -f "$f" ]] && names+=("${f##*/}"); done
script_list="$(IFS='|'; echo "${names[*]}")"

shopt -s nullglob
for f in "$HERE"/unit/*.test.sh; do
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
