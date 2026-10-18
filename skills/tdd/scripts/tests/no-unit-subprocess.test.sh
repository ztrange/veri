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
  scan="$(awk -v scripts="$script_list" '
    BEGIN {
      n = split(scripts, arr, "|"); for (i = 1; i <= n; i++) is_script[arr[i]] = 1
      lead = "(^|\\$\\(|[;&|({])[ \t]*((if|then|elif|else|while|until|do|!)[ \t]+)*((bash|sh|env)[ \t]+)?(([A-Za-z_][A-Za-z0-9_]*=[^ \t]* +)*)"
    }
    function names_script(s,   tok) {
      while (match(s, /\/[a-z0-9-]+\.sh/)) {
        tok = substr(s, RSTART + 1, RLENGTH - 1)
        s = substr(s, RSTART + RLENGTH)
        if (tok in is_script) return 1
      }
      return 0
    }
    /^[ \t]*#/ { next }
    /^[ \t]*(source|\.)[ \t]/ { next }
    /^[ \t]*[A-Za-z_][A-Za-z0-9_]*=/ && $0 !~ /\$\(|`/ {
      rest = $0
      sub(/^[ \t]*[A-Za-z_][A-Za-z0-9_]*=("[^"]*"|\047[^\047]*\047|[^ \t]*)/, "", rest)
      if (rest !~ /^[ \t]*[^ \t#]/) {
        v = $0; sub(/^[ \t]*/, "", v); sub(/=.*/, "", v)
        if (names_script($0)) held[v] = 1
        next
      }
    }
    /^[ \t]*for[ \t]+[A-Za-z_][A-Za-z0-9_]*[ \t]+in[ \t].*\*\.sh/ {
      v = $0; sub(/^[ \t]*for[ \t]+/, "", v); sub(/[ \t].*/, "", v)
      held[v] = 1
    }
    {
      for (v in held)
        if ($0 ~ (lead "\"?\\$\\{?" v "([^A-Za-z0-9_]|$)")) { print FNR "\t" $0; next }
    }
    $0 ~ (lead "\"?[^ \t\"]*\\$[^ \t\"]*\\.sh\"?([ \t;&|)}]|$)") { print FNR "\t" $0; next }
    names_script($0) { print FNR "\t" $0 }
  ' "$f")" || problems+=("$suite: the awk scanner exited with exit status $?")
  while IFS=$'\t' read -r lineno text; do
    [[ -n "$lineno" ]] || continue
    problems+=("$suite:$lineno runs a script under skills/tdd/scripts/ as a subprocess, with no exemption recorded: $(flat "$text")")
  done <<< "$scan"
done

report "no suite under skills/tdd/scripts/tests/unit/ runs a script under skills/tdd/scripts/ as a subprocess outside the exemptions recorded here"

finish
