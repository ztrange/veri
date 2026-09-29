#!/usr/bin/env bash
# Unit test for projects/docs/build-walkthrough.py against its original, docs/build-walkthrough.py:
# the copy is behaviour-preserving, so both print the same page for the same tree. Plain-shell
# asserts, same idiom as the other suites under docs/tests/.
#
# Contract under test:
#   `python3 projects/docs/build-walkthrough.py --stdout` exits 0 and prints bytes identical to
#   `python3 docs/build-walkthrough.py --stdout`; a difference names the first differing line.
#
# Run: projects/docs/tests/copy-parity.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../.." && pwd)"
pass=0 fail=0

name="projects/docs/build-walkthrough.py --stdout prints the same page as docs/build-walkthrough.py --stdout"

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

python3 "$ROOT/docs/build-walkthrough.py" --stdout > "$tmp/original.html" 2> "$tmp/original.err"
original_rc=$?
python3 "$ROOT/projects/docs/build-walkthrough.py" --stdout > "$tmp/copy.html" 2> "$tmp/copy.err"
copy_rc=$?

problems=()
[[ "$original_rc" -eq 0 ]] || problems+=("docs/build-walkthrough.py --stdout: want exit 0, got $original_rc")
[[ "$copy_rc" -eq 0 ]] || problems+=("projects/docs/build-walkthrough.py --stdout: want exit 0, got $copy_rc: $(head -n 1 "$tmp/copy.err")")
if [[ "${#problems[@]}" -eq 0 ]] && ! cmp -s "$tmp/original.html" "$tmp/copy.html"; then
  problems+=("the two pages differ; first differing lines: $(diff "$tmp/original.html" "$tmp/copy.html" | head -n 4 | tr '\n' '|')")
fi

if [[ "${#problems[@]}" -eq 0 ]]; then
  pass=$((pass + 1))
else
  fail=$((fail + 1))
  echo "FAIL - $name"
  printf '    %s\n' "${problems[@]}"
fi

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
