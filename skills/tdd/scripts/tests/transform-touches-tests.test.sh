#!/usr/bin/env bash
# Unit tests for scripts/transform-touches-tests.sh — rejects a refactor-kind transform whose
# commits change a test file.
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

OWED="$HERE/../refactor-owed.sh"
agree_repo="$work/agree"
new_repo -b main "$agree_repo" >/dev/null 2>&1
printf 'seed\n' > "$agree_repo/README"
commit_all "$agree_repo" "chore: seed"
problems=()
for case_ in 'pkg/tests/fixture.sh:test' 'pkg/contests/entry.sh:not-test'; do
  path="${case_%:*}" want="${case_##*:}"
  base="$(git -C "$agree_repo" rev-parse HEAD)"
  mkdir -p "$agree_repo/$(dirname "$path")"
  printf 'x\n' > "$agree_repo/$path"
  commit_all "$agree_repo" "refactor: touch $path"
  (cd "$agree_repo" && "$TOUCHES" "$base" >/dev/null 2>&1); touches_code=$?
  touches_says=not-test
  [[ "$touches_code" == 1 ]] && touches_says=test

  owed_file="$work/owed-${want}.md"
  "$OWED" append "$owed_file" 'a step' "$path" <<'REPORT' >/dev/null 2>&1
CANDIDATES: structural | fold the two walks into one
REPORT
  "$OWED" list "$owed_file" >/dev/null 2>&1; list_code=$?
  owed_says=not-test
  [[ "$list_code" == 3 ]] && owed_says=test

  [[ "$touches_says" == "$want" && "$owed_says" == "$want" ]] ||
    problems+=("$path: want $want from both; transform-touches-tests.sh says $touches_says (exit $touches_code), refactor-owed.sh append says $owed_says (list exit $list_code)")
done
if [[ "${#problems[@]}" == 0 ]]; then ok; else
  no "transform-touches-tests.sh and refactor-owed.sh append agree on what a test file is: ${problems[*]}"
fi

finish
