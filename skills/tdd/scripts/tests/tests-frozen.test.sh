#!/usr/bin/env bash
# Unit tests for scripts/tests-frozen.sh — records a step's test files and later checks that
# none of them has changed.
#
# Contract under test:
#   tests-frozen.sh record <record-file> <test-file>...   → exit 0, writes the record
#   tests-frozen.sh check <record-file>
#       → exit 0, printing nothing on stdout, when every recorded file is byte-identical
#       → exit 1, one path per line on stdout, for each recorded file edited or deleted
#
# Run: scripts/tests/tests-frozen.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
FROZEN="$HERE/../tests-frozen.sh"
source "$HERE/lib/harness.sh"

work="$(scratch_dir)"
mkdir -p "$work/tests"
printf 'assert one\n' > "$work/tests/a.test.sh"
printf 'assert two\n' > "$work/tests/b.test.sh"
rec="$work/record"

rec_out="$(cd "$work" && "$FROZEN" record "$rec" tests/a.test.sh tests/b.test.sh 2>&1)"; rec_code=$?
chk_out="$(cd "$work" && "$FROZEN" check "$rec" 2>/dev/null)"; chk_code=$?
if [[ "$rec_code" == 0 && "$chk_code" == 0 && -z "$chk_out" ]]; then ok; else
  no "tests-frozen #1586: record then check on unchanged files → exit 0 with nothing on stdout (record=$rec_code/$rec_out check=$chk_code out=$chk_out)"
fi

printf 'assert three\n' > "$work/tests/c.test.sh"
rec3="$work/record3"
(cd "$work" && "$FROZEN" record "$rec3" tests/a.test.sh tests/b.test.sh tests/c.test.sh) > /dev/null 2>&1
printf 'assert one, weakened\n' > "$work/tests/a.test.sh"
rm -f "$work/tests/b.test.sh"
bad_out="$(cd "$work" && "$FROZEN" check "$rec3" 2>/dev/null)"; bad_code=$?
want="$(printf 'tests/a.test.sh\ntests/b.test.sh')"
if [[ "$bad_code" == 1 && "$bad_out" == "$want" ]]; then ok; else
  no "tests-frozen #1586: check names the edited and the deleted recorded file, one per line, exit 1 (code=$bad_code out=$bad_out)"
fi

finish
