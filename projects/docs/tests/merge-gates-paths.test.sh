#!/usr/bin/env bash
# Unit test for projects/docs/merge-gates.sh: the copy judges paths under projects/docs/, not docs/.
# Plain-shell asserts, same idiom as the other suites under docs/tests/.
#
# Contract under test:
#   In a repo whose branch changed only projects/docs/walkthrough.html, VERI_GATES_PLAN=1 prints
#   the docs-fresh gate naming that path and no docs-test gate, and exits 0. A changed
#   projects/docs/wt/ file plans both gates. The docs-fresh gate runs projects/docs/check-walkthrough.py.
#
# Run: projects/docs/tests/merge-gates-paths.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
SCRIPT="$HERE/../merge-gates.sh"
pass=0 fail=0

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

# mkrepo <dir> <changed-path> <stub-check-walkthrough: 1|0>: a repo whose branch changed only <changed-path>.
mkrepo() {
  git init -q "$1"
  git -C "$1" config user.email t@example.com
  git -C "$1" config user.name t
  mkdir -p "$1/projects/docs/wt"
  echo one > "$1/$2"
  if [[ "$3" -eq 1 ]]; then
    printf 'open("%s/ran","w").write("x")\n' "$tmp" > "$1/projects/docs/check-walkthrough.py"
  fi
  git -C "$1" add -A
  git -C "$1" commit -q -m base
  git -C "$1" branch base
  echo two > "$1/$2"
  git -C "$1" commit -q -am change
}

report() {
  if [[ "${#problems[@]}" -eq 0 ]]; then
    pass=$((pass + 1))
  else
    fail=$((fail + 1))
    echo "FAIL - $name"
    printf '    %s\n' "${problems[@]}"
  fi
}

name="merge-gates.sh plans docs-fresh only for a changed projects/docs/walkthrough.html"
mkrepo "$tmp/r1" projects/docs/walkthrough.html 0
out="$(cd "$tmp/r1" && env -u VERI_GATES VERI_GATES_BASE=base VERI_GATES_PLAN=1 bash "$SCRIPT" 2>&1)"
rc=$?
problems=()
[[ "$rc" -eq 0 ]] || problems+=("want exit 0, got $rc")
[[ "$out" == *"docs-fresh"*"projects/docs/walkthrough.html"* ]] ||
  problems+=("want a docs-fresh line naming projects/docs/walkthrough.html; got: $out")
[[ "$out" != *"docs-test"* ]] || problems+=("want no docs-test gate; got: $out")
report

name="merge-gates.sh plans docs-test and docs-fresh for a changed projects/docs/wt/ file"
mkrepo "$tmp/r2" projects/docs/wt/app.js 0
out="$(cd "$tmp/r2" && env -u VERI_GATES VERI_GATES_BASE=base VERI_GATES_PLAN=1 bash "$SCRIPT" 2>&1)"
rc=$?
problems=()
[[ "$rc" -eq 0 ]] || problems+=("want exit 0, got $rc")
[[ "$out" == *"docs-test"*"projects/docs/wt/app.js"* ]] ||
  problems+=("want a docs-test line naming projects/docs/wt/app.js; got: $out")
[[ "$out" == *"docs-fresh"*"projects/docs/wt/app.js"* ]] ||
  problems+=("want a docs-fresh line naming projects/docs/wt/app.js; got: $out")
report

name="merge-gates.sh runs projects/docs/check-walkthrough.py for the docs-fresh gate"
mkrepo "$tmp/r3" projects/docs/walkthrough.html 1
out="$(cd "$tmp/r3" && env -u VERI_GATES VERI_GATES_BASE=base bash "$SCRIPT" 2>&1)"
rc=$?
problems=()
[[ "$rc" -eq 0 ]] || problems+=("want exit 0, got $rc; got: $out")
[[ -f "$tmp/ran" ]] || problems+=("want projects/docs/check-walkthrough.py to have run; got: $out")
report

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
