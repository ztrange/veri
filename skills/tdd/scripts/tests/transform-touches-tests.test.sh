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

nosuch_err="$work/nosuch.err"
nosuch_out="$(cd "$repo" && "$TOUCHES" nosuch 2>"$nosuch_err")"; nosuch_code=$?
nosuch_want="transform-touches-tests.sh: base-sha does not resolve to a commit: nosuch
usage: transform-touches-tests.sh <base-sha>"
if [[ "$nosuch_code" == 2 && -z "$nosuch_out" ]] && cmp -s <(printf '%s\n' "$nosuch_want") "$nosuch_err"; then ok; else
  no "base-sha nosuch → exit 2, nothing on stdout, stderr the refusal then the usage line (code=$nosuch_code out=$nosuch_out)"
  diff <(printf '%s\n' "$nosuch_want") "$nosuch_err"
fi

ln -s "$(cd "$HERE/../.." && pwd)" "$work/linked-skill"
LINKED="$work/linked-skill/scripts/transform-touches-tests.sh"
clean_base="$(git -C "$repo" rev-parse HEAD~1)"
in_place_dirty="$(cd "$repo" && "$TOUCHES" "$base" 2>&1)"; in_place_dirty_code=$?
in_place_clean="$(cd "$repo" && "$TOUCHES" "$clean_base" 2>&1)"; in_place_clean_code=$?
linked_dirty="$(cd "$repo" && "$LINKED" "$base" 2>&1)"; linked_dirty_code=$?
linked_clean="$(cd "$repo" && "$LINKED" "$clean_base" 2>&1)"; linked_clean_code=$?
if [[ "$linked_dirty_code" == 1 && "$linked_dirty" == *"tests/widget.test.sh"* && "$linked_clean_code" == 0 && -z "$linked_clean" \
      && "$linked_dirty" == "$in_place_dirty" && "$linked_dirty_code" == "$in_place_dirty_code" \
      && "$linked_clean" == "$in_place_clean" && "$linked_clean_code" == "$in_place_clean_code" ]]; then ok; else
  no "transform-touches-tests.sh run through a symlink to the skill directory and from another repository reads that repository and answers as when run in place"
  diff <(printf '%s\nexit %s\n%s\nexit %s\n' "$in_place_dirty" "$in_place_dirty_code" "$in_place_clean" "$in_place_clean_code") \
    <(printf '%s\nexit %s\n%s\nexit %s\n' "$linked_dirty" "$linked_dirty_code" "$linked_clean" "$linked_clean_code")
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

broken_repo="$work/broken"
new_repo -b main "$broken_repo" >/dev/null 2>&1
mkdir -p "$broken_repo/src"
printf 'a\n' > "$broken_repo/src/a.sh"
commit_all "$broken_repo" "feat: a"
broken_base="$(git -C "$broken_repo" rev-parse HEAD)"
printf 'b\n' > "$broken_repo/src/a.sh"
commit_all "$broken_repo" "refactor: b"
middle="$(git -C "$broken_repo" rev-parse HEAD)"
printf 'c\n' > "$broken_repo/src/a.sh"
commit_all "$broken_repo" "refactor: c"
rm -f "$broken_repo/.git/objects/${middle:0:2}/${middle:2}"
broken_out="$(cd "$broken_repo" && "$TOUCHES" "$broken_base" 2>/dev/null)"; broken_code=$?
if [[ "$broken_code" == 2 ]]; then ok; else
  no "#818: base-sha resolves but git log over base..HEAD fails on a missing commit object → exit 2, never 0 (code=$broken_code out=$broken_out)"
fi

finish
