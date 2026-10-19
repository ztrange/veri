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

mkdir -p "$work/sec"
cat > "$work/sec/REQUIREMENTS.md" <<MD
$H doc.md#Middle

| ID | Requirement | Why |
|----|-------------|-----|
| B1 | Middle holds. | Because secret-b. |
MD
printf '# Top\nbefore-marker line.\n## Middle\nmiddle-marker line.\n### Inner\ninner-marker line.\n## Next\nafter-marker line.\n' > "$work/sec/doc.md"
rm -f "$work/seen"
(cd "$work/sec" && CLAUDE_BIN="$bin/claude" "$GRADE" "$work/sec/REQUIREMENTS.md" 'doc.md#Middle' > /dev/null 2>&1)
seen="$(cat "$work/seen" 2> /dev/null)"
got=""
for want in '## Middle' 'middle-marker' '### Inner' 'inner-marker'; do
  [[ "$seen" == *"$want"* ]] || got+="[missing $want]"
done
for not in '# Top' 'before-marker' '## Next' 'after-marker'; do
  [[ "$seen" == *"$not"* ]] && got+="[leaked $not]"
done
expect_eq "a section unit's prompt carries its text from its heading to the next heading of the same or higher level, and nothing else of the file" \
  "" "$got"

mkdir -p "$work/role/.tdd"
cp "$work/REQUIREMENTS.md" "$work/unit.md" "$work/role/"
(cd "$work/role" && CLAUDE_BIN="$bin/claude" "$GRADE" "$work/role/REQUIREMENTS.md" unit.md > /dev/null 2>&1)
actors="$(grep -F '"event": "launch"' "$work/role/.tdd/events.jsonl" 2> /dev/null | grep -o '"actor": *"[a-z]*"' | tr -d ' ' | sort -u | tr '\n' ' ')"
[[ -n "$actors" ]] || actors="$(grep -F '"event":"launch"' "$work/role/.tdd/events.jsonl" 2> /dev/null | grep -o '"actor": *"[a-z]*"' | tr -d ' ' | sort -u | tr '\n' ' ')"
expect_eq "the grader leaf's supervisor launch event names a grader role, never developer or verifier" \
  '"actor":"grader" ' "$actors"

conf="$HERE/../../grader.conf"
want_model="$(awk '/^[[:space:]]*(#|$)/ { next } !found { v = $0; sub(/^[^=]*=/, "", v); gsub(/^[[:space:]"]+|[[:space:]"]+$/, "", v); found = 1 } END { print v }' "$conf" 2> /dev/null)"
[[ -n "$want_model" ]] || want_model="(no model in skills/tdd/grader.conf)"
rm -f "$work/seen"
(cd "$work/role" && VERI_MODEL=exp-model-all VERI_MODEL_VERIFIER=exp-model-verifier CLAUDE_BIN="$bin/claude" "$GRADE" "$work/role/REQUIREMENTS.md" unit.md > /dev/null 2>&1)
got_model="$(grep -A1 -x -e '--model' "$work/seen" 2> /dev/null | tail -n 1)"
expect_eq "claude receives --model with grader.conf's value, whatever VERI_MODEL and VERI_MODEL_VERIFIER say" \
  "$want_model" "$got_model"

finish
