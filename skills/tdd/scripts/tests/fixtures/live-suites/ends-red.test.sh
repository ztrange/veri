#!/usr/bin/env bash
# A FIXTURE, not one of this repository's suites: ../../count-line-guard.test.sh hands it to
# `make test` on purpose, and nothing else runs it. It lives here rather than beside the
# real suites because `make test`'s glob is skills/tdd/scripts/tests/*.test.sh, which does
# not descend into a directory — so a file named *.test.sh is safe under fixtures/ and
# would not be one level up.
#
# What it is: a suite that fails the honest way, written in this repository's idiom — its
# one case fails, so it prints its FAIL line, reaches the count line it ends with saying so,
# and exits non-zero on the `[[ "$fail" -eq 0 ]]` every suite here ends with.
#
# Why this shape needs a fixture: the check added for #157 asks each suite for that count
# line, and this suite has one. A runner that had come to read the count line *instead of*
# the exit code — rather than as well as — would call this green, which is the ordinary way
# a test failure is reported and by far the more common of the two.
set -uo pipefail

pass=0 fail=0

if [[ "veri" == "something else" ]]; then
  pass=$((pass + 1))
else
  fail=$((fail + 1))
  echo "FAIL - a word equals a word it differs from"
fi

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
