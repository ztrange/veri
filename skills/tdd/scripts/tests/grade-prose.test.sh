#!/usr/bin/env bash
# Tests for scripts/grade-prose.sh — grades one prose unit against its requirements list.
#
# Run: scripts/tests/grade-prose.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
GRADE="$HERE/../grade-prose.sh"
source "$HERE/lib/harness.sh"

work="$(scratch_dir)"
H='##'

cat > "$work/REQUIREMENTS.md" <<MD
$H unit.md

| ID | Requirement | Why |
|----|-------------|-----|
| A1 | Says one thing. | Because secret-one. |
| A2 | Says two things. | Since secret-two. |
MD
printf 'Unit body line alpha.\nUnit body line beta.\n' > "$work/unit.md"

bin="$work/bin"
mkdir -p "$bin"
claude_stub "$bin" "printf '%s\n' \"\$@\" > '$work/seen'; cat >> '$work/seen'"

(cd "$work" && CLAUDE_BIN="$bin/claude" "$GRADE" "$work/REQUIREMENTS.md" unit.md > /dev/null 2>&1)
seen="$(cat "$work/seen" 2> /dev/null)"
miss=""
for want in 'Unit body line alpha.' 'Unit body line beta.' 'A1' 'Says one thing.' 'A2' 'Says two things.'; do
  [[ "$seen" == *"$want"* ]] || miss+="[$want]"
done
leak=no
[[ "$seen" == *secret-one* || "$seen" == *secret-two* ]] && leak=yes
expect_eq "a whole-file unit's prompt carries the unit text and each requirement's ID and text, and no Why text" \
  "missing=;leak=no" "missing=$miss;leak=$leak"

out="$("$GRADE" 2> "$work/stderr")" && code=0 || code=$?
usage=no; [[ "$(cat "$work/stderr")" == usage:*grade-prose.sh* ]] && usage=yes
expect_eq "grade-prose.sh with no arguments exits 2 and prints its usage line on stderr" \
  $'2\nyes' "$code"$'\n'"$usage"

finish
