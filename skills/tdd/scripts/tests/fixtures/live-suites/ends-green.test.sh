#!/usr/bin/env bash
# A FIXTURE, not one of this repository's suites: ../../count-line-guard.test.sh hands it to
# `make test` on purpose, and nothing else runs it. It lives here rather than beside the
# real suites because `make test`'s glob is skills/tdd/scripts/tests/*.test.sh, which does
# not descend into a directory — so a file named *.test.sh is safe under fixtures/ and
# would not be one level up.
#
# What it is: the ordinary shape, written in this repository's idiom — one case, it passes,
# the suite reaches the count line it ends with, reports nothing failed, and exits 0. Its
# sibling ends-red.test.sh is the same shape with the opposite answer.
#
# Why the ordinary shape needs a fixture at all: the runner grew a check for #157 that
# refuses a suite whose output does not end in its count line. A check that refuses
# everything would satisfy that criterion just as well as the right one does, and would
# take the whole repository down with it. This is the suite it must still let through.
set -uo pipefail

pass=0 fail=0

if [[ "veri" == "veri" ]]; then
  pass=$((pass + 1))
else
  fail=$((fail + 1))
  echo "FAIL - a word equals itself"
fi

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
