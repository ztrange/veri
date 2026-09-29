#!/usr/bin/env bash
# Unit test for projects/docs/CLAUDE.md: the docs project's working notes name projects/docs/ paths.
# Plain-shell asserts, same idiom as the other suites under docs/tests/.
#
# Contract under test:
#   projects/docs/CLAUDE.md exists and carries the one trap (walkthrough.html is generated, edited
#   through wt/commentary.py), the docs command rows (make -C projects/docs docs, test, fresh,
#   check) and the docs-suite rules, all written for projects/docs/ paths — none of them still
#   names a bare docs/ path.
#
# Run: projects/docs/tests/claude-md.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
NOTES="$HERE/../CLAUDE.md"
pass=0 fail=0

name="projects/docs/CLAUDE.md carries the trap and the docs command rows, all naming projects/docs/ paths"

problems=()
if [[ ! -f "$NOTES" ]]; then
  problems+=("CLAUDE.md: missing")
else
  for want in \
    'projects/docs/walkthrough.html' \
    'projects/docs/wt/commentary.py' \
    'make -C projects/docs docs' \
    'make -C projects/docs test' \
    'make -C projects/docs fresh' \
    'make -C projects/docs check' \
    'projects/docs/tests/'; do
    grep -F -- "$want" "$NOTES" > /dev/null || problems+=("CLAUDE.md: never names '$want'")
  done
  bare="$(grep -nE '(^|[^/A-Za-z-])docs/(wt|tests|walkthrough|build-walkthrough|check-walkthrough|docs-owed|merge-gates)' "$NOTES")"
  [[ -z "$bare" ]] || problems+=("CLAUDE.md: still names a bare docs/ path: $bare")
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
