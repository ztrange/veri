#!/usr/bin/env bash
# lib/exit-contract.sh — sourced, not run: defines `refuse`, `require_args` and `to_contract`.
#
# refuse [message] — print <message> (if given), then the caller's $USAGE, on stderr; exit 2.
# require_args <n> "$@" — refuse unless the first <n> arguments are present and non-empty;
#   return 0 otherwise.
# to_contract <code> — print <code> if it is 0, 1, 2 or 3, else 2.
#
# Sourcing it arms an EXIT trap: the sourcing script exits 2 for any code outside 0-3, unless
# the exit is a declared pass-through — its line directly preceded by `# pass-through: <why>`.
refuse() {
  if (( $# > 0 )); then
    printf '%s\n' "$1" >&2
  fi
  printf '%s\n' "$USAGE" >&2
  exit 2
}

require_args() {
  local n="$1" i
  shift
  for (( i = 1; i <= n; i++ )); do
    [[ -n "${!i:-}" ]] || refuse
  done
  return 0
}

to_contract() {
  case "$1" in
    0|1|2|3) printf '%s\n' "$1" ;;
    *) printf '2\n' ;;
  esac
}

declared_pass_through() {
  local cmd="$1" previous="" line
  while IFS= read -r line; do
    line="${line#"${line%%[![:space:]]*}"}"
    if [[ "$line" == "$cmd" && "$previous" == "# pass-through:"* ]]; then
      return 0
    fi
    previous="$line"
  done < "$0"
  return 1
}

end_in_contract() {
  if declared_pass_through "$2"; then
    exit "$1"
  fi
  exit "$(to_contract "$1")"
}

trap 'end_in_contract "$?" "$BASH_COMMAND"' EXIT
