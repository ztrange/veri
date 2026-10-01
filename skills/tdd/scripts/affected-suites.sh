#!/usr/bin/env bash
# affected-suites.sh — print the suites one change affects, so a red or refactor leaf can run a
# narrow slice of `make test` instead of all of it.
#
# Usage:   affected-suites.sh <base>..<head>
#
# Prints one suite path per line, sorted, with no duplicate.
set -euo pipefail

source "$(cd "$(dirname "$0")" && pwd)/lib/exit-contract.sh"

USAGE="usage: affected-suites.sh <base>..<head>"
require_args 1 "$@"
range="$1"
scripts=skills/tdd/scripts

# hazard: git diff reads a range with no `..` as a revision against the working tree.
[[ "$range" == *..* ]] || refuse "affected-suites: '$range' is not a <base>..<head> range"
for rev in "${range%%..*}" "${range#*..}"; do
  git rev-parse --verify --quiet "$rev^{commit}" >/dev/null ||
    refuse "affected-suites: cannot resolve revision '$rev'"
done

suites_naming() {
  local args=() p
  for p in "$@"; do args+=(-e "$p"); done
  grep -lF "${args[@]}" "$scripts"/tests/*.test.sh || true
}

suite_of() {
  local f="$1" name script
  case "$f" in
    CLAUDE.md|Makefile|skills/*/SKILL.md)
      suites_naming "\"$f\"" "/$f\"" ;;
    "$scripts"/tests/*.test.sh) echo "$f" ;;
    "$scripts"/tests/lib/harness.sh)
      grep -lE '^[[:space:]]*(source|\.)[[:space:]].*lib/harness\.sh"?[[:space:]]*$' \
        "$scripts"/tests/*.test.sh "$scripts"/tests/unit/*.test.sh || true ;;
    "$scripts"/tests/fixtures/*)
      suites_naming "${f#"$scripts"/tests/}" ;;
    "$scripts"/prompts/*.md)
      suites_naming "${f#"$scripts"/}" ;;
    "$scripts"/lib/*.sh)
      name="$(basename "$f")"
      for script in "$scripts"/*.sh; do
        if grep -qE "^[[:space:]]*(source|\.)[[:space:]].*lib/$name\"?[[:space:]]*(\\\\)?$" "$script"; then
          suite_of "$script"
        fi
      done ;;
    "$scripts"/*.sh)
      name="$(basename "$f" .sh)"
      if [[ -f "$scripts/tests/unit/$name.test.sh" ]]; then
        echo "$scripts/tests/unit/$name.test.sh"
      else
        echo "$scripts/tests/$name.test.sh"
      fi ;;
    .tdd/*)
      ;;
    *) return 1 ;;
  esac
}

files="$(git diff --name-only "$range")"
[[ -n "$files" ]] || exit 3

placed="" unplaced=""
while IFS= read -r f; do
  if suites="$(suite_of "$f")"; then
    if [[ -n "$suites" ]]; then placed+="$suites"$'\n'; fi
  else
    unplaced+="${unplaced:+,}$f"
  fi
done <<<"$files"

if [[ -n "$(git diff --name-only --diff-filter=AD "$range" -- \
             "$scripts/tests" ":(glob)$scripts/*.sh")" ]]; then
  placed+="$scripts/tests/claude-md-counts.test.sh"$'\n'
fi

if [[ -n "$unplaced" ]]; then
  printf 'affected-suites: no rule places %s; widening to every suite\n' "$unplaced" >&2
  for suite in "$scripts"/tests/*.test.sh "$scripts"/tests/unit/*.test.sh; do
    if [[ -f "$suite" ]]; then echo "$suite"; fi
  done | sort -u
else
  [[ -n "$placed" ]] || exit 3
  printf '%s' "$placed" | sort -u
fi
