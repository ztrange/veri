#!/usr/bin/env bash
# Unit tests for the tree itself — no file a suite run writes may be tracked. Like
# no-job-spec-kills.test.sh this suite has no script as its subject: its subject is the
# tree it is run in.
#
# Contract under test:
#   No tracked file lives under a nested .tdd/ directory (the place a suite run writes its
#   event log). A file that does is reported by its path.
#
# Run: skills/tdd/scripts/tests/no-tracked-artifacts.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"

source "$HERE/lib/harness.sh"

tracked_artifacts() {
  git -C "$1" ls-files -z | tr '\0' '\n' | grep -E '/\.tdd/' || true
}

plant="$(scratch_dir)"
new_repo "$plant"
mkdir -p "$plant/pkg/.tdd"
echo '{}' > "$plant/pkg/.tdd/events.jsonl"
echo x > "$plant/keep.txt"
git -C "$plant" add -A
expect_eq "a planted tracked file under a nested .tdd/ is named by its path" \
  "pkg/.tdd/events.jsonl" "$(tracked_artifacts "$plant")"

clean="$(scratch_dir)"
new_repo "$clean"
echo x > "$clean/keep.txt"
git -C "$clean" add -A
expect_eq "a tree with no tracked artifact names nothing" "" "$(tracked_artifacts "$clean")"

name="no file under a nested .tdd/ directory is tracked (#598)"
problems=()

while IFS= read -r path; do
  [[ -n "$path" ]] || continue
  problems+=("$path is tracked, but a suite run writes it: untrack it (git rm --cached) and ignore the directory")
done < <(tracked_artifacts "$ROOT")

report "$name"

name="git ignores the event log a suite run writes under a nested .tdd/ directory (#598)"
problems=()

for path in skills/tdd/scripts/.tdd/events.jsonl skills/tdd/scripts/tests/.tdd/events.jsonl; do
  git -C "$ROOT" check-ignore -q "$path" \
    || problems+=("$path is not ignored, so a suite run leaves the tree dirty: ignore nested .tdd/ directories")
done

report "$name"

finish
