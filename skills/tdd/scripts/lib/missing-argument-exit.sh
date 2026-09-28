#!/usr/bin/env bash
# lib/missing-argument-exit.sh — sourced, not run: defines `missing_argument_offender` and
# `bare_expansion_offenders`.
#
# missing_argument_offender <scripts-dir> <script> [args …] — run <script> with <args>, stdin
# from /dev/null and stdout discarded. Return 0 when it exits 2 with a usage line on stderr;
# otherwise print one offender line and return 1.
# bare_expansion_offenders <dir> — print one offender line per `${N:?…}` in a non-comment line
# of <dir>/*.sh, and return 1 when there is any.
#
# hazard: `${N:?…}` aborts the shell with status 1, not the 2 a missing argument owes.
missing_argument_offender() {
  local dir="$1" script="$2"; shift 2
  local code=0 err shown="$script${*:+ $*}"
  err="$("$dir/$script" "$@" 2>&1 >/dev/null </dev/null)" || code=$?
  if [[ "$code" != 2 ]]; then
    echo "$shown: want exit 2, got $code"
    return 1
  fi
  if [[ "$err" != *usage* ]]; then
    echo "$shown: exit 2 but no usage line on stderr: ${err:-<nothing on stderr>}"
    return 1
  fi
}

bare_expansion_offenders() {
  local dir="$1" found=0 file lineno text n
  for file in "$dir"/*.sh; do
    [[ -e "$file" ]] || continue
    while IFS=: read -r lineno text; do
      [[ "${text#"${text%%[![:space:]]*}"}" == '#'* ]] && continue
      [[ "$text" =~ \$\{([0-9]+):\? ]] || continue
      n="${BASH_REMATCH[1]}"
      echo "${file##*/}:$lineno: guards \$$n with a bare \${N:?…} expansion, which exits 1, not 2"
      found=1
    done < <(grep -nE '\$\{[0-9]+:\?' "$file")
  done
  (( found == 0 )) || return 1
}
