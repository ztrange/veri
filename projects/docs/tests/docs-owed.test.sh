#!/usr/bin/env bash
# Unit test for projects/docs/docs-owed.sh: the copy reads its page, build and wt/ from projects/docs/.
# Plain-shell asserts, same idiom as the other suites under docs/tests/.
#
# Contract under test:
#   Run from a repo whose committed page is projects/docs/walkthrough.html and whose build is
#   projects/docs/build-walkthrough.py, docs-owed.sh prints the build's `owed:` gaps as
#   `commentary owed: <gap>` lines and exits 0.
#
# Run: projects/docs/tests/docs-owed.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
SCRIPT="$HERE/../docs-owed.sh"
pass=0 fail=0

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

report() {
  if [[ "${#problems[@]}" -eq 0 ]]; then
    pass=$((pass + 1))
  else
    fail=$((fail + 1))
    echo "FAIL - $name"
    printf '    %s\n' "${problems[@]}"
  fi
}

name="docs-owed.sh reports the gap projects/docs/build-walkthrough.py names, from the page at projects/docs/walkthrough.html"
repo="$tmp/r1"
git init -q "$repo"
git -C "$repo" config user.email t@example.com
git -C "$repo" config user.name t
mkdir -p "$repo/projects/docs/wt"
cp "$SCRIPT" "$repo/projects/docs/docs-owed.sh"
echo '<html></html>' > "$repo/projects/docs/walkthrough.html"
printf 'import sys\nsys.stderr.write("  owed: stub.sh L1\xe2\x80\x932\\n")\n' > "$repo/projects/docs/build-walkthrough.py"
printf 'SCRIPTS = []\n' > "$repo/projects/docs/wt/commentary.py"
git -C "$repo" add -A
git -C "$repo" commit -q -m base
out="$(cd "$repo" && bash projects/docs/docs-owed.sh 2>&1)"
rc=$?
problems=()
[[ "$rc" -eq 0 ]] || problems+=("want exit 0, got $rc; got: $out")
[[ "$out" == *"commentary owed: stub.sh L1"* ]] ||
  problems+=("want a 'commentary owed: stub.sh L1' line; got: $out")
report

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
