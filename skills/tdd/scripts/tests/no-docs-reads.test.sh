#!/usr/bin/env bash
# Unit tests for the suites in this directory — a development suite must not reach into the
# generated-documentation tree.
#
# Contract under test:
#   No suite under this directory names a path in the documentation tree, except in a
#   comment or as fixture text it writes out (a redirect into its own file, no read verb).
#   An offender is reported with the suite and the offending line.
#   The same holds for every suite `make test` would run.
#
# Run: skills/tdd/scripts/tests/no-docs-reads.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"

ROOT="$(cd "$HERE/../../../.." && pwd)"

DOCS_DIR='docs'

DOCS_PATH="(^|[^[:alnum:]_.-])$DOCS_DIR/"

WRITES_OUT='>[[:space:]]*["'"'"'$]'

READ_VERB='(^|[^[:alnum:]_./-])(grep|egrep|fgrep|cat|sed|awk|head|tail|wc|cmp|diff|source|python3|python|bash)[[:space:]]'


source "$HERE/lib/harness.sh"

flat() { printf '%s' "$1" | tr '\n' '/'; }

exempt() {
  local text="$1"
  [[ "$text" =~ ^[[:space:]]*# ]] && return 0
  [[ "$text" =~ $WRITES_OUT ]] && ! [[ "$text" =~ $READ_VERB ]]
}

roster() { make -C "$ROOT" -n "$1" 2>&1 | grep -o '[^ ]*\.test\.sh' | sort -u; }

probe_no_suite_reaches_into_the_tree() {
  local f name hit lineno text
  for f in "$HERE"/*.test.sh; do
    [[ -e "$f" ]] || continue
    name="$(basename "$f")"
    while IFS= read -r hit; do
      lineno="${hit%%:*}"
      text="${hit#*:}"
      exempt "$text" && continue
      problems+=("$name:$lineno names a path in the generated-documentation tree outside a comment and outside fixture text, which puts that tree's prose on every leaf's critical path: $(flat "$text")")
    done < <(grep -nE "$DOCS_PATH" "$f")
  done
  return 0
}

name="no suite under skills/tdd/scripts/tests/ names a path in the generated-documentation tree outside a comment or fixture text"
problems=()

probe_no_suite_reaches_into_the_tree

report "$name"

probe_no_suite_the_target_runs_reaches_into_the_tree() {
  local rel hit lineno text
  local -a listed=()
  while IFS= read -r rel; do
    [[ -n "$rel" ]] || continue
    listed+=("$rel")
    while IFS= read -r hit; do
      lineno="${hit%%:*}"
      text="${hit#*:}"
      exempt "$text" && continue
      problems+=("$rel:$lineno names a path in the generated-documentation tree outside a comment and outside fixture text, so \`make test\` — the baseline preflight reads, the Green leaf runs and both blind verifiers run — opens that tree: $(flat "$text")")
    done < <(grep -nE "$DOCS_PATH" "$ROOT/$rel")
  done < <(roster test)
  [[ "${#listed[@]}" -gt 0 ]] ||
    problems+=("\`make -n test\` named no suite at all, so nothing was read: the roster this case asks about could not be obtained")
  return 0
}

name="no suite \`make test\` runs names a path in the generated-documentation tree outside a comment or fixture text"
problems=()

probe_no_suite_the_target_runs_reaches_into_the_tree

report "$name"

finish
