#!/usr/bin/env bash
# lib/missing-argument-exit.sh — sourced, not run: defines `stderr_of`, `usage_offender`, `missing_argument_offender`,
# `named_usage_offender`, `script_audit`, `prints_usage`, `missing_argument_audit`,
# `requires_argument`, `argument_audit` and `bare_expansion_offenders`.
#
# missing_argument_offender <scripts-dir> <script> [args …] — run <script> with <args>, stdin
# from /dev/null and stdout discarded. Return 0 when it exits 2 with a usage line on stderr;
# otherwise print one offender line and return 1.
# named_usage_offender <scripts-dir> <script> [args …] — as missing_argument_offender, and the
# stderr must also name <script>.
# missing_argument_audit <dir> — run every <dir>/*.sh whose source prints a usage line with no
# arguments; print one offender line per script that does not exit 2 with its own name on
# stderr, and return 1 when there is any.
# requires_argument <file> — return 0 when <file>'s usage line names a <…> outside […].
# argument_audit <dir> — run every <dir>/*.sh requires_argument admits with no arguments; print
# one offender line per script that does not exit 2 with a usage line naming it on stderr, and return 1
# when there is any.
# bare_expansion_offenders <dir> — print one offender line per `${N:?…}` in a non-comment line
# of <dir>/*.sh, and return 1 when there is any.
#
# hazard: `${N:?…}` aborts the shell with status 1, not the 2 a missing argument owes.
stderr_of() {  # stderr_of <cmd> [args …] — run <cmd> with stdin from /dev/null; print only its stderr
  "$@" 2>&1 >/dev/null </dev/null
}

usage_offender() {  # usage_offender <named 0|1> <scripts-dir> <script> [args …]
  local named="$1" dir="$2" script="$3"; shift 3
  local code=0 err shown="$script${*:+ $*}"
  err="$(stderr_of "$dir/$script" "$@")" || code=$?
  if [[ "$code" != 2 ]]; then
    echo "$shown: want exit 2, got $code"
    return 1
  fi
  if [[ "$err" != *usage* ]]; then
    echo "$shown: exit 2 but no usage line on stderr: ${err:-<nothing on stderr>}"
    return 1
  fi
  if (( named )) && [[ "$err" != *"$script"* ]]; then
    echo "$shown: usage line on stderr does not name it: $err"
    return 1
  fi
}

missing_argument_offender() {
  usage_offender 0 "$@"
}

named_usage_offender() {
  usage_offender 1 "$@"
}

script_audit() {  # script_audit <admits> <offender> <dir>
  local admits="$1" offender="$2" dir="$3" found=0 file
  for file in "$dir"/*.sh; do
    [[ -e "$file" ]] || continue
    "$admits" "$file" || continue
    "$offender" "$dir" "${file##*/}" || found=1
  done
  (( found == 0 )) || return 1
}

prints_usage() {
  grep -F 'usage:' "$1" > /dev/null
}

missing_argument_audit() {
  script_audit prints_usage named_usage_offender "$1"
}

requires_argument() {
  local usage
  usage="$(grep -m1 -oE 'usage: .*' "$1")" || return 1
  [[ "$(sed -E 's/\[[^]]*\]//g' <<< "$usage")" == *'<'*'>'* ]]
}

argument_audit() {
  script_audit requires_argument named_usage_offender "$1"
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
