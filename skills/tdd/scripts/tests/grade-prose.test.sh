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

mkdir -p "$work/nover/scripts"
for f in "$HERE"/../*; do
  [[ "$(basename "$f")" == grade-prose.sh ]] && cp "$f" "$work/nover/scripts/" || ln -s "$f" "$work/nover/scripts/$(basename "$f")"
done
echo 'model=sonnet' > "$work/nover/grader.conf"
rm -f "$work/ran"
claude_stub "$bin" "touch '$work/ran'"
(cd "$work/role" && CLAUDE_BIN="$bin/claude" "$work/nover/scripts/grade-prose.sh" "$work/role/REQUIREMENTS.md" unit.md > /dev/null 2> "$work/nover/stderr")
code=$?
diag=no; [[ -s "$work/nover/stderr" ]] && diag=yes
launched=no; [[ -e "$work/ran" ]] && launched=yes
expect_eq "a grader.conf model that names no version exits 2 with a diagnostic on stderr and never launches claude" \
  "2;diag=yes;launched=no" "$code;diag=$diag;launched=$launched"

claude_stub "$bin" "printf 'Some analysis first.\nBEGIN GRADES\nA1: PASS — says one thing\nA2: PASS — says two things\nVERDICT: PASS\nEND GRADES\n'"
(cd "$work/role" && CLAUDE_BIN="$bin/claude" "$GRADE" "$work/role/REQUIREMENTS.md" unit.md > /dev/null 2>&1)
expect_eq "a reply whose final GRADES block has one PASS line per requirement in list order and VERDICT: PASS exits 0" \
  "0" "$?"

claude_stub "$bin" "printf 'Analysis.\nBEGIN GRADES\nA1: PASS — says one thing\nA2: FAIL — says three things instead\nVERDICT: REJECT\nEND GRADES\n'"
out="$(cd "$work/role" && CLAUDE_BIN="$bin/claude" "$GRADE" "$work/role/REQUIREMENTS.md" unit.md 2> /dev/null)" && code=0 || code=$?
names_fail=no; grep -F 'A2' <<< "$out" | grep -F 'says three things instead' > /dev/null && names_fail=yes
expect_eq "a reply whose final GRADES block has a FAIL line and VERDICT: REJECT exits 1 and prints each failing ID with its reason on stdout" \
  "1;names_fail=yes" "$code;names_fail=$names_fail"

claude_stub "$bin" "printf 'A1: FAIL — I first thought this failed.\nBEGIN GRADES\nA1: PASS — says one thing\nA2: PASS — says two things\nVERDICT: PASS\nEND GRADES\n'"
out="$(cd "$work/role" && CLAUDE_BIN="$bin/claude" "$GRADE" "$work/role/REQUIREMENTS.md" unit.md 2> /dev/null)" && code=0 || code=$?
printed=no; grep -F 'FAIL' <<< "$out" > /dev/null && printed=yes
expect_eq "a FAIL line in the free analysis above a final all-PASS GRADES block with VERDICT: PASS exits 0 and prints no FAIL line" \
  "0;printed=no" "$code;printed=$printed"

claude_stub "$bin" "printf 'Analysis only, no block.\nVERDICT: PASS\n'"
(cd "$work/role" && CLAUDE_BIN="$bin/claude" "$GRADE" "$work/role/REQUIREMENTS.md" unit.md > /dev/null 2> "$work/err-noblock")
code_noblock=$?
claude_stub "$bin" "printf 'BEGIN GRADES\nA1: PASS — one\nA2: PASS — two\nVERDICT: PASS\nEND GRADES\nTrailing words.\n'"
(cd "$work/role" && CLAUDE_BIN="$bin/claude" "$GRADE" "$work/role/REQUIREMENTS.md" unit.md > /dev/null 2> "$work/err-trailing")
code_trailing=$?
named_noblock=no; grep -F 'BEGIN GRADES' "$work/err-noblock" > /dev/null && named_noblock=yes
named_trailing=no; grep -iF 'after END GRADES' "$work/err-trailing" > /dev/null && named_trailing=yes
expect_eq "a reply with no BEGIN GRADES block, or with text after END GRADES, exits 2 and names that defect on stderr" \
  "2;2;noblock=yes;trailing=yes" "$code_noblock;$code_trailing;noblock=$named_noblock;trailing=$named_trailing"

claude_stub "$bin" "cat > '$work/seen-prompt'"
(cd "$work/role" && CLAUDE_BIN="$bin/claude" "$GRADE" "$work/role/REQUIREMENTS.md" unit.md > /dev/null 2>&1)
sp="$(cat "$work/seen-prompt" 2> /dev/null)"
g5=""
for want in 'BEGIN GRADES' 'END GRADES' 'PASS|FAIL' 'VERDICT: PASS' 'VERDICT: REJECT'; do
  [[ "$sp" == *"$want"* ]] || g5+="[missing $want]"
done
before_verdict="${sp%VERDICT: REJECT*}"
after_verdict="${sp#"$before_verdict"}"
[[ "$after_verdict" == *'END GRADES'* ]] || g5+="[VERDICT not inside the block before END GRADES]"
expect_eq "the prompt tells the grader to end with a BEGIN GRADES block of PASS|FAIL lines and a VERDICT line inside it before END GRADES" \
  "" "$g5"

claude_stub "$bin" "printf 'BEGIN GRADES\nA1: PASS — one\nA2: PASS — two\nEND GRADES\nVERDICT: PASS\n'"
(cd "$work/role" && CLAUDE_BIN="$bin/claude" "$GRADE" "$work/role/REQUIREMENTS.md" unit.md > /dev/null 2> "$work/err-late-verdict")
code_late=$?
named_late=no; grep -iF 'after END GRADES' "$work/err-late-verdict" > /dev/null && named_late=yes
expect_eq "a reply whose VERDICT line comes after END GRADES exits 2 and names the text after END GRADES on stderr" \
  "2;late=yes" "$code_late;late=$named_late"

claude_stub "$bin" "printf 'BEGIN GRADES\nA1: PASS — one\nVERDICT: PASS\nEND GRADES\n'"
(cd "$work/role" && CLAUDE_BIN="$bin/claude" "$GRADE" "$work/role/REQUIREMENTS.md" unit.md > /dev/null 2> "$work/err-missing")
code_missing=$?
claude_stub "$bin" "printf 'BEGIN GRADES\nA1: PASS — one\nA2: PASS — two\nA3: PASS — three\nVERDICT: PASS\nEND GRADES\n'"
(cd "$work/role" && CLAUDE_BIN="$bin/claude" "$GRADE" "$work/role/REQUIREMENTS.md" unit.md > /dev/null 2> "$work/err-extra")
code_extra=$?
claude_stub "$bin" "printf 'BEGIN GRADES\nA2: PASS — two\nA1: PASS — one\nVERDICT: PASS\nEND GRADES\n'"
(cd "$work/role" && CLAUDE_BIN="$bin/claude" "$GRADE" "$work/role/REQUIREMENTS.md" unit.md > /dev/null 2> "$work/err-reorder")
code_reorder=$?
named_missing=no; grep -iF 'missing' "$work/err-missing" | grep -F 'A2' > /dev/null && named_missing=yes
named_extra=no; grep -iF 'extra' "$work/err-extra" | grep -F 'A3' > /dev/null && named_extra=yes
named_reorder=no; grep -iF 'order' "$work/err-reorder" > /dev/null && named_reorder=yes
expect_eq "a final GRADES block with a missing, an extra or a reordered requirement ID exits 2 and names that defect on stderr" \
  "2;2;2;missing=yes;extra=yes;reorder=yes" "$code_missing;$code_extra;$code_reorder;missing=$named_missing;extra=$named_extra;reorder=$named_reorder"

claude_stub "$bin" "printf 'BEGIN GRADES\nA1: PASS — one\nA2: FAIL — two\nVERDICT: PASS\nEND GRADES\n'"
(cd "$work/role" && CLAUDE_BIN="$bin/claude" "$GRADE" "$work/role/REQUIREMENTS.md" unit.md > /dev/null 2> "$work/err-pass-fail")
code_pass_fail=$?
claude_stub "$bin" "printf 'BEGIN GRADES\nA1: PASS — one\nA2: PASS — two\nVERDICT: REJECT\nEND GRADES\n'"
(cd "$work/role" && CLAUDE_BIN="$bin/claude" "$GRADE" "$work/role/REQUIREMENTS.md" unit.md > /dev/null 2> "$work/err-reject-pass")
code_reject_pass=$?
named_pass_fail=no; grep -iF 'disagree' "$work/err-pass-fail" > /dev/null && named_pass_fail=yes
named_reject_pass=no; grep -iF 'disagree' "$work/err-reject-pass" > /dev/null && named_reject_pass=yes
expect_eq "a reply whose VERDICT line disagrees with its grade lines exits 2 and names the disagreement on stderr" \
  "2;2;pass_fail=yes;reject_pass=yes" "$code_pass_fail;$code_reject_pass;pass_fail=$named_pass_fail;reject_pass=$named_reject_pass"

finish
