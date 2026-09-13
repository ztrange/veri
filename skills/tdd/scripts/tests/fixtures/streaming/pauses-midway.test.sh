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
# the probe reading this fixture's output looks ten times a second, so seconds of slack buy
# nothing.
set -uo pipefail

PAUSE=2

pass=0 fail=0

# 1. A case that fails, because a FAIL line is what a suite in this repository actually
#    prints while it is still running — and seeing it then, rather than a minute later when
#    the suite is done, is what streaming the output is for.
fail=$((fail + 1))
echo "FAIL - a suite says something before it is finished"

sleep "$PAUSE"

# 2. A case that passes, after the wait, so the fixture is a suite that carried on rather
#    than one that stopped talking — the shape of the 70 s suite this is standing in for.
if [[ "veri" == "veri" ]]; then
  pass=$((pass + 1))
else
  fail=$((fail + 1))
  echo "FAIL - a word equals itself"
fi

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
