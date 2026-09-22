#!/usr/bin/env bash
# affected-suites.sh — print the suites one change affects, so a red or refactor leaf can run a
# narrow slice of `make test` instead of all of it (issue #337).
#
# Usage:   affected-suites.sh <base>..<head>
#
# Prints one suite path per line, sorted, with no duplicate.
set -euo pipefail

[[ -n "${1:-}" ]] || { echo "usage: affected-suites.sh <base>..<head>" >&2; exit 2; }
range="$1"
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
# that sources it. Returns 1 for a file no rule places.
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
    "$scripts"/prompts/*.md)
      # A suite names a prompt by its path under scripts/, as build-develop-prompt.test.sh does
      # "$HERE/../prompts/develop-reconcile.md".
      suites_naming "${f#"$scripts"/}" ;;
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
    .tdd/*)
      # Run state, not an input to any suite: the ledger is rewritten by every green commit, so
      # a range spanning one would otherwise fall through and widen the whole answer (#416).
      ;;
    *) return 1 ;;
  esac
}

# An empty diff is "nothing to do" (exit 3), not an empty answer.
files="$(git diff --name-only "$range")"
[[ -n "$files" ]] || exit 3

# One file no rule places widens the whole answer to every suite (fail-closed): a partial list
# would narrow the run to what the other rules happened to find.
placed="" unplaced=""
while IFS= read -r f; do
  if suites="$(suite_of "$f")"; then
    if [[ -n "$suites" ]]; then placed+="$suites"$'\n'; fi
  else
    # Accumulated already comma-joined: the list is only ever printed, never iterated.
    unplaced+="${unplaced:+,}$f"
  fi
done <<<"$files"

if [[ -n "$unplaced" ]]; then
  # Say which file widened the answer, so the next unplaced kind is visible rather than silent.
  printf 'affected-suites: no rule places %s; widening to every suite\n' "$unplaced" >&2
  for suite in "$scripts"/tests/*.test.sh "$scripts"/tests/unit/*.test.sh; do
    if [[ -f "$suite" ]]; then echo "$suite"; fi
  done | sort -u
else
  # Every changed file placed as affecting no suite (run state alone) is "nothing to do", the
  # same answer as an empty diff: an empty stdout would read to a leaf as an empty tier (#416).
  [[ -n "$placed" ]] || exit 3
  printf '%s' "$placed" | sort -u
fi
