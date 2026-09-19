#!/usr/bin/env bash
# Unit tests for the `unit` target in this repository's Makefile — the fast tier. Like
# make-test-env.test.sh and count-line-guard.test.sh this suite has no script as its
# subject: its subject is which suites a make target runs. Zero-dependency plain-shell
# asserts, same idiom as the rest of this directory.
#
# Why this exists (issue #336): every suite here ran in one tier, so a one-line change to a
# script paid the whole `make test` for a check that only needed the suites asserting pure
# logic. `make unit` is the faster loop, and it is only faster if it runs the suites under
# skills/tdd/scripts/tests/unit/ and nothing from the flat directory beside it.
#
# Contract under test:
#   1. `make -n unit` names only suites matching skills/tdd/scripts/tests/unit/*.test.sh —
#      and every one of them on disk, so an empty roster over a populated directory is a
#      failure rather than a vacuous pass.
#
# The roster is read off `make -n`, which expands the target's list and runs nothing, the
# same idiom as no-docs-reads.test.sh's roster helper: running `make unit` to find out
# what it runs would cost the run it is asking about.
#
# Run: skills/tdd/scripts/tests/unit-tier.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
# The suite sits at skills/<skill>/scripts/tests, so four levels up is the repo root.
ROOT="$(cd "$HERE/../../../.." && pwd)"

# The fast tier's directory, repo-relative — what a roster line says and what the failure
# messages quote.
UNIT_DIR='skills/tdd/scripts/tests/unit'

pass=0 fail=0

# report <name> — close a case whose probes collected into the `problems` array: an empty
# array is a pass, otherwise one FAIL line for the case and one indented line per problem.
report() {
  local name="$1"
  if [[ "${#problems[@]}" -eq 0 ]]; then
    pass=$((pass + 1))
  else
    fail=$((fail + 1))
    echo "FAIL - $name"
    printf '    %s\n' "${problems[@]}"
  fi
}

# flat <text> — one line of it, for a failure message: newlines become slashes.
flat() { printf '%s' "$1" | tr '\n' '/'; }

# 1. `make -n unit` names only the fast tier's suites, and all of them.
name="make -n unit lists only suites matching $UNIT_DIR/*.test.sh"
problems=()

recipe="$(make --no-print-directory -n -C "$ROOT" unit 2>&1)" && code=0 || code=$?
if [[ "$code" != 0 ]]; then
  problems+=("make -n unit exited $code: $(flat "$recipe")")
else
  listed="$(printf '%s\n' "$recipe" | grep -o '[^ ]*\.test\.sh' | sort -u)"
  while IFS= read -r rel; do
    [[ -n "$rel" ]] || continue
    [[ "$rel" =~ ^$UNIT_DIR/[^/]+\.test\.sh$ ]] ||
      problems+=("make -n unit names $rel, which is not under $UNIT_DIR/")
  done <<< "$listed"
  for f in "$ROOT/$UNIT_DIR"/*.test.sh; do
    [[ -e "$f" ]] || continue
    rel="$UNIT_DIR/$(basename "$f")"
    grep -qxF "$rel" <<< "$listed" ||
      problems+=("make -n unit does not name $rel, which is on disk under $UNIT_DIR/")
  done
fi

report "$name"

echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
