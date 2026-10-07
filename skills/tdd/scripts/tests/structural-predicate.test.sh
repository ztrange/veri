#!/usr/bin/env bash
# Tests for scripts/structural-predicate.sh — the check a structural-pass candidate's
# predicate must pass before a transform leaf is launched for it.
#
# Contract under test:
#   structural-predicate.sh <record> reads a predicate leaf's report on stdin and, when its
#   `PREDICATE:` command fails against the current tree, writes that command to <record>.
#
# Run: scripts/tests/structural-predicate.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
SP="$HERE/../structural-predicate.sh"

source "$HERE/lib/harness.sh"

name="#691 a PREDICATE: command that fails on the current tree is written to <record>, exit 0"
problems=()
tree="$(scratch_dir)"
record="$tree/predicate"
predicate="test -e lib/shared-opening.md"
code=0
(cd "$tree" && "$SP" "$record" >/dev/null 2>&1 <<REPORT) || code=$?
Read the candidate and the files it names.
PREDICATE: $predicate
REPORT
[[ "$code" == 0 ]] ||
  problems+=("want exit 0 from structural-predicate.sh, got $code")
if [[ ! -f "$record" ]]; then
  problems+=("structural-predicate.sh wrote no record at $record")
else
  [[ "$(cat "$record")" == "$predicate" ]] ||
    problems+=("record holds '$(cat "$record")', want the reported command '$predicate'")
fi
report "$name"

name="#691 a PREDICATE: command that already succeeds on the current tree exits 1 and writes no record"
problems=()
tree="$(scratch_dir)"
record="$tree/predicate"
touch "$tree/shared-opening.md"
code=0
(cd "$tree" && "$SP" "$record" >/dev/null 2>&1 <<REPORT) || code=$?
Read the candidate and the files it names.
PREDICATE: test -e shared-opening.md
REPORT
[[ "$code" == 1 ]] ||
  problems+=("want exit 1 from structural-predicate.sh, got $code")
[[ ! -e "$record" ]] ||
  problems+=("structural-predicate.sh wrote a record at $record for a predicate already true")
report "$name"

name="#691 PREDICATE: NONE exits 3 and a report with no PREDICATE: line exits 2, neither writing a record"
problems=()
tree="$(scratch_dir)"
record="$tree/predicate"
code=0
(cd "$tree" && "$SP" "$record" >/dev/null 2>&1 <<REPORT) || code=$?
No command can tell this candidate's transform apart from the tree as it is.
PREDICATE: NONE
REPORT
[[ "$code" == 3 ]] ||
  problems+=("PREDICATE: NONE: want exit 3 from structural-predicate.sh, got $code")
[[ ! -e "$record" ]] ||
  problems+=("PREDICATE: NONE: structural-predicate.sh wrote a record at $record")
rm -f "$record"
code=0
(cd "$tree" && "$SP" "$record" >/dev/null 2>&1 <<REPORT) || code=$?
Read the candidate and the files it names.
REPORT
[[ "$code" == 2 ]] ||
  problems+=("no PREDICATE: line: want exit 2 from structural-predicate.sh, got $code")
[[ ! -e "$record" ]] ||
  problems+=("no PREDICATE: line: structural-predicate.sh wrote a record at $record")
report "$name"

name="#691 PREDICATE: NONE — <why>, the form the predicate prompt asks for, exits 3 and writes no record"
problems=()
tree="$(scratch_dir)"
record="$tree/predicate"
code=0
(cd "$tree" && "$SP" "$record" >/dev/null 2>&1 <<REPORT) || code=$?
Read the candidate and the files it names.
PREDICATE: NONE — the transform only renames prose, and no command can tell it apart
REPORT
[[ "$code" == 3 ]] ||
  problems+=("want exit 3 from structural-predicate.sh, got $code")
[[ ! -e "$record" ]] ||
  problems+=("structural-predicate.sh wrote a record at $record for PREDICATE: NONE — <why>")
report "$name"

name="#691 PREDICATE: NONE followed directly by a dash or a colon exits 3 and writes no record"
problems=()
tree="$(scratch_dir)"
record="$tree/predicate"
for line in "PREDICATE: NONE—no command can tell the transform apart" \
            "PREDICATE: NONE: no command can tell the transform apart"; do
  rm -f "$record"
  code=0
  (cd "$tree" && "$SP" "$record" >/dev/null 2>&1 <<REPORT) || code=$?
Read the candidate and the files it names.
$line
REPORT
  [[ "$code" == 3 ]] ||
    problems+=("$line: want exit 3 from structural-predicate.sh, got $code")
  [[ ! -e "$record" ]] ||
    problems+=("$line: structural-predicate.sh wrote a record at $record")
done
report "$name"

name="structural-predicate.sh with no argument exits 2, prints nothing on stdout, writes nothing, and puts exactly its usage line on stderr"
problems=()
tree="$(scratch_dir)"
out="$(scratch_dir)"
code=0
(cd "$tree" && "$SP" >"$out/stdout" 2>"$out/stderr" </dev/null) || code=$?
[[ "$code" == 2 ]] ||
  problems+=("want exit 2 from structural-predicate.sh with no argument, got $code")
[[ ! -s "$out/stdout" ]] ||
  problems+=("want nothing on stdout, got '$(cat "$out/stdout")'")
[[ "$(cat "$out/stderr")" == "usage: structural-predicate.sh <record>" && "$(wc -l < "$out/stderr")" -eq 1 ]] ||
  problems+=("want exactly 'usage: structural-predicate.sh <record>' on stderr, got '$(cat "$out/stderr")'")
[[ -z "$(ls -A "$tree")" ]] ||
  problems+=("structural-predicate.sh wrote into its working directory: $(ls -A "$tree")")
report "$name"

finish
