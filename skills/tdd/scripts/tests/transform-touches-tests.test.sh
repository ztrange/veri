#!/usr/bin/env bash
# Unit tests for scripts/transform-touches-tests.sh — rejects a refactor-kind transform whose
# commits change a test file (issue #499).
#
# A transform is one named refactoring: it moves structure and must not move the tests that
# pin the behaviour, or "the suite is still green" stops meaning "the behaviour is unchanged".
# A long refactor has no green commit, so the transform's range is the step's base sha to HEAD.
#
# Contract under test:
#   transform-touches-tests.sh <base-sha>, run inside the repository
#       → exit 1, naming the test file, when any commit in <base-sha>..HEAD changes one
#       → exit 0 when none does
#
# Run: scripts/tests/transform-touches-tests.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
TOUCHES="$HERE/../transform-touches-tests.sh"
source "$HERE/lib/harness.sh"

work="$(scratch_dir)"

git_q() { local repo="$1"; shift; git -C "$repo" -c user.name=veri -c user.email=veri@example.test "$@"; }

commit_all() {
  git_q "$1" add -A >/dev/null 2>&1
  git_q "$1" commit -q -m "$2" >/dev/null 2>&1
}

repo="$work/transform"
new_repo -b main "$repo" >/dev/null 2>&1
mkdir -p "$repo/src" "$repo/tests"
printf 'widget() { echo 1; }\n' > "$repo/src/widget.sh"
printf 'widget | grep 1\n' > "$repo/tests/widget.test.sh"
commit_all "$repo" "feat: widget"
base="$(git -C "$repo" rev-parse HEAD)"
printf 'widget() {\n  echo 1\n}\n' > "$repo/src/widget.sh"
commit_all "$repo" "refactor: reformat widget"
clean_out="$(cd "$repo" && "$TOUCHES" "$base" 2>&1)"; clean_code=$?
printf 'widget | grep -F 1\n' > "$repo/tests/widget.test.sh"
commit_all "$repo" "refactor: loosen the widget test"
printf 'widget() {\n  printf "1\\n"\n}\n' > "$repo/src/widget.sh"
commit_all "$repo" "refactor: printf in widget"
dirty_out="$(cd "$repo" && "$TOUCHES" "$base" 2>&1)"; dirty_code=$?
if [[ "$clean_code" == 0 && "$dirty_code" == 1 && "$dirty_out" == *"tests/widget.test.sh"* ]]; then ok; else
  no "transform range: production-only → exit 0; a test file changed → exit 1 naming it (clean code=$clean_code out=$clean_out; dirty code=$dirty_code out=$dirty_out)"
fi

bogus="0123456789abcdef0123456789abcdef01234567"
bad_out="$(cd "$repo" && "$TOUCHES" "$bogus" 2>&1)"; bad_code=$?
if [[ "$bad_code" == 2 && "$bad_out" == *"$bogus"* ]]; then ok; else
  no "unresolvable base-sha → exit 2 with a diagnostic naming it (code=$bad_code out=$bad_out)"
fi

finish
