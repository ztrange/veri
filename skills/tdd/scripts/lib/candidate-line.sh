#!/usr/bin/env bash
# lib/candidate-line.sh — sourced, not run: defines `structural_candidate`,
# `test_only_candidate` and `cosmetic_candidate`.
#
# structural_candidate <line> — when <line> is `CANDIDATES: structural | <transform>`, sets
# STRUCTURAL_TRANSFORM to <transform> and returns 0; otherwise returns 1 and leaves it alone.
#
# test_only_candidate <line> — the same for `CANDIDATES: test-only | <transform>`, setting
# TEST_ONLY_TRANSFORM.
#
# cosmetic_candidate <line> — the same for `CANDIDATES: cosmetic | <transform>`, setting
# COSMETIC_TRANSFORM.
#
# hazard: inside [[ … =~ … ]] a backslashed `|` is undefined in an ERE, so `[|]` matches it.
candidate_of_class() {
  [[ "$2" =~ ^CANDIDATES:[[:space:]]*$1[[:space:]]*[|][[:space:]]*(.*)$ ]]
}

structural_candidate() {
  candidate_of_class structural "$1" || return 1
  STRUCTURAL_TRANSFORM="${BASH_REMATCH[1]}"
}

test_only_candidate() {
  candidate_of_class test-only "$1" || return 1
  TEST_ONLY_TRANSFORM="${BASH_REMATCH[1]}"
}

cosmetic_candidate() {
  candidate_of_class cosmetic "$1" || return 1
  COSMETIC_TRANSFORM="${BASH_REMATCH[1]}"
}
