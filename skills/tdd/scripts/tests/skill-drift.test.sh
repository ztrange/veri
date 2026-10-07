#!/usr/bin/env bash
# Tests for scripts/skill-drift.sh — the bail report's block naming the conductor-path changes
# that landed on the skill clone's ref since the run's pinned skill commit.
#
# Contract under test:
#   VERI_SKILL_COMMIT=<sha> VERI_SKILL_CLONE=<clone> VERI_SKILL_REF=<ref> skill-drift.sh
#     → prints `#### Skill drift since the pinned commit`, one `- #<N> — <subject> (<k> commits)`
#       line per trailing (#N), newest group first, then
#       `Resume with VERI_NEW_SKILL=1 to run on these.`, and exits 0.

set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
SKILL_DRIFT="$HERE/../skill-drift.sh"

source "$HERE/lib/harness.sh"

touch_commit() {
  local repo="$1" path="$2" subject="$3"
  mkdir -p "$repo/$(dirname "$path")"
  echo "$subject" >> "$repo/$path"
  git -C "$repo" add -A
  git -C "$repo" commit -q -m "$subject"
}

name="two (#12) commits and one later (#15) commit on skills/tdd/scripts/ after the pin list #15 before #12 with their counts, then the resume line, exit 0"
problems=()
tmp="$(scratch_dir)"
upstream="$tmp/upstream" clone="$tmp/clone"
new_repo -b main "$upstream"
touch_commit "$upstream" skills/tdd/scripts/run-leaf.sh "feat: the pinned skill (#9)"
pinned="$(git -C "$upstream" rev-parse HEAD)"
touch_commit "$upstream" skills/tdd/scripts/supervise.sh "fix: the supervisor's first window (#12)"
touch_commit "$upstream" skills/tdd/scripts/supervise.sh "fix: the supervisor's second window (#12)"
touch_commit "$upstream" skills/tdd/scripts/run-leaf.sh "feat: a leaf names its model (#15)"
git clone -q "$upstream" "$clone"
out="$(env -u VERI_SKILL_UNPINNED VERI_SKILL_COMMIT="$pinned" VERI_SKILL_CLONE="$clone" \
  VERI_SKILL_REF=refs/remotes/origin/main "$SKILL_DRIFT" 2>/dev/null)" && code=0 || code=$?
[[ "$code" == 0 ]] || problems+=("want exit 0, got $code")
[[ "$(head -n 1 <<<"$out")" == "#### Skill drift since the pinned commit" ]] ||
  problems+=("want the block's heading as its first line")
line15="$(grep -n -E '^- #15 — feat: a leaf names its model( \(#15\))? \(1 commits\)$' <<<"$out" | cut -d: -f1)"
line12="$(grep -n -E "^- #12 — fix: the supervisor's second window( \(#12\))? \(2 commits\)$" <<<"$out" | cut -d: -f1)"
[[ -n "$line15" ]] || problems+=("want a '- #15 — <subject> (1 commits)' line")
[[ -n "$line12" ]] || problems+=("want a '- #12 — <newest #12 subject> (2 commits)' line")
[[ -n "$line15" && -n "$line12" && "$line15" -lt "$line12" ]] || problems+=("want the #15 line before the #12 line")
[[ "$(tail -n 1 <<<"$out")" == "Resume with VERI_NEW_SKILL=1 to run on these." ]] ||
  problems+=("want 'Resume with VERI_NEW_SKILL=1 to run on these.' as the last line")
((${#problems[@]} == 0)) || problems+=("stdout was: $(printf '%q' "$out")")
report "$name"

name="commits after the pin touching only skills/tdd/scripts/tests/, docs/ or Makefile are not listed: the block says none., has no resume line, exit 0"
problems=()
tmp="$(scratch_dir)"
upstream="$tmp/upstream" clone="$tmp/clone"
new_repo -b main "$upstream"
touch_commit "$upstream" skills/tdd/scripts/run-leaf.sh "feat: the pinned skill (#9)"
pinned="$(git -C "$upstream" rev-parse HEAD)"
touch_commit "$upstream" skills/tdd/scripts/tests/run-leaf.test.sh "test: a leaf's case (#20)"
touch_commit "$upstream" docs/notes.md "docs: a note (#21)"
touch_commit "$upstream" Makefile "build: a recipe (#22)"
git clone -q "$upstream" "$clone"
out="$(env -u VERI_SKILL_UNPINNED VERI_SKILL_COMMIT="$pinned" VERI_SKILL_CLONE="$clone" \
  VERI_SKILL_REF=refs/remotes/origin/main "$SKILL_DRIFT" 2>/dev/null)" && code=0 || code=$?
[[ "$code" == 0 ]] || problems+=("want exit 0, got $code")
grep -x -F "Conductor-path changes on refs/remotes/origin/main since then: none." <<<"$out" > /dev/null ||
  problems+=("want 'Conductor-path changes on refs/remotes/origin/main since then: none.'")
! grep -E '^- ' <<<"$out" > /dev/null || problems+=("want no listed change")
! grep -F "Resume with VERI_NEW_SKILL=1" <<<"$out" > /dev/null || problems+=("want no resume line")
((${#problems[@]} == 0)) || problems+=("stdout was: $(printf '%q' "$out")")
report "$name"

finish
