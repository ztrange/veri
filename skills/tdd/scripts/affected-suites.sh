#!/usr/bin/env bash
# affected-suites.sh — print the suites one change affects, so a red or refactor leaf can run a
# narrow slice of `make test` instead of all of it (issue #337).
#
# Usage:   affected-suites.sh <base>..<head>
#
# Prints one suite path per line, sorted, with no duplicate.
set -euo pipefail

range="${1:?usage: affected-suites.sh <base>..<head>}"
scripts=skills/tdd/scripts

# A malformed range is a plumbing failure, not an answer. Without the `..` check a single
# revision reaches `git diff` as "against the working tree", which it answers happily.
[[ "$range" == *..* ]] ||
  { echo "affected-suites: '$range' is not a <base>..<head> range" >&2; exit 2; }
for rev in "${range%%..*}" "${range#*..}"; do
  git rev-parse --verify --quiet "$rev^{commit}" >/dev/null ||
    { echo "affected-suites: cannot resolve revision '$rev'" >&2; exit 2; }
done

# suite_of <path> — the suite a touched file affects: a suite is its own, a script's is the
# one named after it, under tests/ or tests/unit/.
suite_of() {
  local f="$1" name
  case "$f" in
    "$scripts"/tests/*.test.sh) echo "$f" ;;
    "$scripts"/*.sh)
      name="$(basename "$f" .sh)"
      if [[ -f "$scripts/tests/unit/$name.test.sh" ]]; then
        echo "$scripts/tests/unit/$name.test.sh"
      else
        echo "$scripts/tests/$name.test.sh"
      fi ;;
  esac
}

git diff --name-only "$range" | while IFS= read -r f; do suite_of "$f"; done | sort -u
