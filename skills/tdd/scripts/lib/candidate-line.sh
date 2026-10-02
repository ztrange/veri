#!/usr/bin/env bash
# lib/candidate-line.sh — sourced, not run: defines `structural_candidate` and
# `test_only_candidate`.
#
# structural_candidate <line> — when <line> is `CANDIDATES: structural | <transform>`, sets
# STRUCTURAL_TRANSFORM to <transform> and returns 0; otherwise returns 1 and leaves it alone.
#
# test_only_candidate <line> — the same for `CANDIDATES: test-only | <transform>`, setting
# TEST_ONLY_TRANSFORM.
#
# hazard: inside [[ … =~ … ]] a backslashed `|` is undefined in an ERE, so `[|]` matches it.
structural_candidate() {
  [[ "$1" =~ ^CANDIDATES:[[:space:]]*structural[[:space:]]*[|][[:space:]]*(.*)$ ]] || return 1
  STRUCTURAL_TRANSFORM="${BASH_REMATCH[1]}"
}

test_only_candidate() {
  [[ "$1" =~ ^CANDIDATES:[[:space:]]*test-only[[:space:]]*[|][[:space:]]*(.*)$ ]] || return 1
  TEST_ONLY_TRANSFORM="${BASH_REMATCH[1]}"
}
