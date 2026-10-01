#!/usr/bin/env bash
# A FIXTURE, not one of this repository's suites: ../../count-line-guard.test.sh hands it to
# `make test` on purpose, and nothing else runs it. It lives here rather than beside the
# real suites because `make test`'s glob is skills/tdd/scripts/tests/*.test.sh, which does
# not descend into a directory — so a file named *.test.sh is safe under fixtures/ and
# would not be one level up.
#
# What it is: a suite written in this repository's idiom that dies halfway and still exits
# 0, which is the shape issue #157 is about. Its second case reads a word out of what looks
# like command output and compares it as a number. Under `set -u`, bash evaluates the word
# `COMMENTARY` inside `[[ … -le … ]]` as a variable name, the name is unset, and the script
# is killed there — before its count line, and with the exit status of the command before
# the comparison rather than a failure. Every case after that point is silently skipped.
# That is how build-guards.test.sh ran 37 of its 54 cases until commit c4a6bdb.
#
# The EXIT trap is what makes the zero exit a property of this fixture instead of a
# property of the interpreter that happens to run it. On the bash 3.2 this repository
# develops against, the death above exits 0 on its own; what bash 5 on a Linux runner does
# with the same script is unverified (#157), and a fixture whose premise held on one
# interpreter only would pin the runner on one interpreter only.
set -uo pipefail
trap 'exit 0' EXIT

pass=0 fail=0

if [[ "veri" == "veri" ]]; then
  pass=$((pass + 1))
else
  fail=$((fail + 1))
  echo "FAIL - a word equals itself"
fi

read -r made budget <<< "COMMENTARY OWED:"
if [[ "$made" -le 3 ]]; then
  pass=$((pass + 1))
else
  fail=$((fail + 1))
  echo "FAIL - commentary owed is within budget"
fi

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
