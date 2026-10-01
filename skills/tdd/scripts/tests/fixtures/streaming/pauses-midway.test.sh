#!/usr/bin/env bash
# A FIXTURE, not one of this repository's suites: ../../count-line-guard.test.sh hands it to
# `make test` on purpose, and nothing else runs it. It lives here rather than beside the
# real suites because `make test`'s glob is skills/tdd/scripts/tests/*.test.sh, which does
# not descend into a directory — so a file named *.test.sh is safe under fixtures/ and
# would not be one level up.
#
# What it is: a suite that says something and then goes on working. Its first case fails and
# prints the FAIL line every suite here prints, then it waits, then it runs another case and
# ends the ordinary way — the `----` separator, the count line, an exit status. The wait is
# the whole point: it is a window in which a runner that shows each suite's lines as they are
# printed has already shown that FAIL line, and a runner that collects a suite's output and
# prints it once the suite is over has shown nothing.
#
# PAUSE is what every `make test` pays for that window, three times per TDD step, so it is as
# short as the observation can be made against rather than as long as would be comfortable:
# the probe reading this fixture's output looks fifty times a second, so seconds of slack buy
# nothing. 0.2s is not arbitrary: sleep guarantees AT LEAST that long (only ever more, under
# load — a busy runner cannot make this fixture pause less, so raising the floor cannot make
# the probe flaky), and count-line-guard.test.sh's own timer needs a floor comfortably below
# it to tell a streamed run from a buffered one — see that file for the exact margin.
set -uo pipefail

PAUSE=0.2

pass=0 fail=0

fail=$((fail + 1))
echo "FAIL - a suite says something before it is finished"

sleep "$PAUSE"

if [[ "veri" == "veri" ]]; then
  pass=$((pass + 1))
else
  fail=$((fail + 1))
  echo "FAIL - a word equals itself"
fi

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
