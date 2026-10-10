#!/usr/bin/env bash
# Unit tests for scripts/production-frozen.sh — rejects a range that changes production code
# while the production code is frozen.
#
# Contract under test:
#   production-frozen.sh <base-sha>, run inside the repository
#       → exit 1, naming each changed path that is not a test file by
#         transform-touches-tests.sh's rule, when any commit in <base-sha>..HEAD changes one
#
# Run: scripts/tests/production-frozen.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
FROZEN="$HERE/../production-frozen.sh"
source "$HERE/lib/harness.sh"

work="$(scratch_dir)"

git_q() { local repo="$1"; shift; git -C "$repo" -c user.name=veri -c user.email=veri@example.test "$@"; }

commit_all() {
  git_q "$1" add -A >/dev/null 2>&1
  git_q "$1" commit -q -m "$2" >/dev/null 2>&1
}

repo="$work/frozen"
new_repo -b main "$repo" >/dev/null 2>&1
mkdir -p "$repo/src" "$repo/tests" "$repo/pkg/contests"
printf 'widget() { echo 1; }\n' > "$repo/src/widget.sh"
printf 'widget | grep 1\n' > "$repo/tests/widget.test.sh"
printf 'entry\n' > "$repo/pkg/contests/entry.sh"
commit_all "$repo" "feat: widget"
base="$(git -C "$repo" rev-parse HEAD)"
printf 'widget | grep -F 1\n' > "$repo/tests/widget.test.sh"
printf 'widget() { printf "1\\n"; }\n' > "$repo/src/widget.sh"
commit_all "$repo" "test: loosen the widget test, and change widget"
printf 'entry two\n' > "$repo/pkg/contests/entry.sh"
commit_all "$repo" "chore: touch entry"
dirty_out="$(cd "$repo" && "$FROZEN" "$base" 2>&1)"; dirty_code=$?
if [[ "$dirty_code" == 1 && "$dirty_out" == *"src/widget.sh"* && "$dirty_out" == *"pkg/contests/entry.sh"* \
      && "$dirty_out" != *"tests/widget.test.sh"* ]]; then ok; else
  no "production-frozen range: production paths changed → exit 1 naming each, and not the test file (code=$dirty_code out=$dirty_out)"
fi

finish
