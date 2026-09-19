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

# suites_naming <pattern>... — every suite whose source contains one of the fixed strings.
suites_naming() {
  local args=() p
  for p in "$@"; do args+=(-e "$p"); done
  grep -lF "${args[@]}" "$scripts"/tests/*.test.sh || true
}

# suite_of <path> — the suites a touched file affects: a suite is its own, a script's is the
# one named after it, under tests/ or tests/unit/, and a lib file's are those of every script
# that sources it.
suite_of() {
  local f="$1" name script
  case "$f" in
    CLAUDE.md|Makefile|skills/*/SKILL.md)
      # A guard suite names its document as a whole quoted path, as model-knobs-recorded does
      # claude_md="CLAUDE.md", or at the end of one, as count-line-guard does "$ROOT/Makefile".
      suites_naming "\"$f\"" "/$f\"" ;;
    "$scripts"/tests/*.test.sh) echo "$f" ;;
    "$scripts"/tests/fixtures/*)
      # A suite references a fixture by its path under tests/, as count-line-guard does
      # "$HERE/fixtures/silent-death/…".
      suites_naming "${f#"$scripts"/tests/}" ;;
    "$scripts"/lib/*.sh)
      # A sourcing script names the lib file on a `source` line, as event.sh does
      # `source "$HERE/lib/json-escape.sh"`; a comment naming it is not a dependency.
      name="$(basename "$f")"
      for script in "$scripts"/*.sh; do
        if grep -qE "^[[:space:]]*(source|\.)[[:space:]].*lib/$name\"?[[:space:]]*$" "$script"; then
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
  esac
}

# An empty diff is "nothing to do" (exit 3), not an empty answer.
files="$(git diff --name-only "$range")"
[[ -n "$files" ]] || exit 3

while IFS= read -r f; do suite_of "$f"; done <<<"$files" | sort -u
