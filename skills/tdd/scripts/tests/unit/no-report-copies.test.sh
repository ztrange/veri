#!/usr/bin/env bash
# Audits that no suite carries its own copy of what lib/harness.sh defines. Every file under
# tests/ and tests/unit/ that defines a function named `report` — the suites and
# tests/record-helpers.sh alike — is named, bar lib/harness.sh, the one definition they source;
# so is every one that defines `ok` or `no`, initialises `pass=0 fail=0` or prints its own
# count line, bar harness.test.sh, whose subject is the harness itself.
# Admitted to the fast tier by its own usage count: git 0, python3 0, server 0, sleep 0.
#
# Run: scripts/tests/unit/no-report-copies.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
TESTS="$(cd "$HERE/.." && pwd)"
export LC_ALL=C
source "$TESTS/lib/harness.sh"

sfx=.test.sh
counter_re='^[[:space:]]*(pass=0;?[[:space:]]+fail=0|pass="\$\{pass:-0\}")'
declare -A COUNTER_EXEMPT=(
  ["docs-read-guard$sfx:pass=0; fail=0"]="a planted suite's own counters, inside a heredoc"
  ["profile$sfx:pass=0; fail=0"]="a planted suite's own counters, inside a heredoc"
  ["skill-leaf-env$sfx:    pass=0; fail=0"]="a subshell reset around a probe"
)

tree_grep() {
  local dir="$1"
  shift
  (cd "$dir" && shopt -s nullglob && grep -HnE "$@" ./*.sh ./unit/*.sh) \
    | grep -v '^\./unit/harness\.test\.sh:'
}

counter_hits() {
  local hits hit file rest lineno text
  hits="$(tree_grep "$1" -e "$counter_re")"
  while IFS= read -r hit; do
    [[ -n "$hit" ]] || continue
    file="${hit%%:*}"
    file="${file#./}"
    rest="${hit#*:}"
    lineno="${rest%%:*}"
    text="${rest#*:}"
    [[ -n "${COUNTER_EXEMPT["$file:$text"]-}" ]] && continue
    printf '    %s:%s carries its own harness scaffolding\n' "$file" "$lineno"
  done <<< "$hits"
}

scaffolding_hits() {
  local hits hit file rest
  hits="$(tree_grep "$1" \
    -e '^[[:space:]]*(function[[:space:]]+)?(ok|no)[[:space:]]*\(\)' \
    -e '^[[:space:]]*(echo|printf)[[:space:]].*\$(\{pass\}|pass)[^"]* passed, .*failed')"
  while IFS= read -r hit; do
    [[ -n "$hit" ]] || continue
    file="${hit%%:*}"
    rest="${hit#*:}"
    printf '    %s:%s carries its own harness scaffolding\n' "${file#./}" "${rest%%:*}"
  done <<< "$hits"
  counter_hits "$1"
}

HOISTED=(win window windows plain section_end frontmatter_name first_record record_number fenced_lines need_claude_md_records probe_every_exemption_carries_a_reason verdict)
GUARD_ONLY=verdict
GUARD_SUITES=" count-line-guard$sfx prompt-test-tiers$sfx unit/missing-argument-exit$sfx unit/emitted-text$sfx unit/pending-mark-literal$sfx "

hoisted_copy_hits() {
  local names hits hit file rest def
  names="$(IFS='|'; printf '%s' "${HOISTED[*]}")"
  hits="$(tree_grep "$1" -e "^[[:space:]]*(function[[:space:]]+)?($names)[[:space:]]*\(\)")"
  while IFS= read -r hit; do
    [[ -n "$hit" ]] || continue
    file="${hit%%:*}"
    rest="${hit#*:}"
    def="${rest#*:}"
    def="${def#"${def%%[![:space:]]*}"}"
    def="${def#function}"
    def="${def#"${def%%[![:space:]]*}"}"
    def="${def%%[[:space:](]*}"
    file="${file#./}"
    [[ "$def" == "$GUARD_ONLY" && "$GUARD_SUITES" != *" $file "* ]] && continue
    printf '    %s:%s defines %s()\n' "$file" "${rest%%:*}" "$def"
  done <<< "$hits"
}

name="no suite defines its own report, and lib/harness.sh defines it"
problems=""
copies="$(cd "$TESTS" && grep -nE '^[[:space:]]*(function[[:space:]]+)?report[[:space:]]*\(\)' \
  ./*.sh ./unit/*.sh)"
while IFS= read -r hit; do
  [[ -n "$hit" ]] || continue
  file="${hit%%:*}"
  rest="${hit#*:}"
  problems+="    ${file#./}:${rest%%:*} defines report()"$'\n'
done <<< "$copies"
if ! grep -E '^report[[:space:]]*\(\)' "$TESTS/lib/harness.sh" > /dev/null; then
  problems+="    lib/harness.sh does not define report()"$'\n'
fi
if [[ -z "$problems" ]]; then
  ok
else
  no "$name"
  printf '%s' "$problems"
fi

name="no suite defines its own ok/no, initialises its own counters or prints its own count line"
problems="$(scaffolding_hits "$TESTS")"
if [[ -z "$problems" ]]; then
  ok
else
  no "$name"
  printf '%s\n' "$problems"
fi

name="#595: a counter-initialisation hit is admitted only by an entry naming its file, matching its text and carrying a reason"
plant="$(scratch_dir)"
printf '%s\n' '#!/usr/bin/env bash' 'x=1' 'pass=0 fail=0' 'x=2' 'pass=0 fail=0  # probe' > "$plant/a.test.sh"
printf '%s\n' '#!/usr/bin/env bash' 'pass=0 fail=0' > "$plant/b.test.sh"
printf '%s\n' 'pass=0 fail=0' > "$plant/c.test.sh"
printf '%s\n' 'pass=0 fail=0' > "$plant/d.test.sh"
mkdir -p "$plant/unit"
printf '%s\n' 'pass=0 fail=0' > "$plant/unit/harness$sfx"
got="$(
  declare -A COUNTER_EXEMPT=(
    ["a.test.sh:pass=0 fail=0"]="a planted suite's own counters"
    ["c.test.sh:pass=0 fail=0"]=""
    ["d.test.sh:1"]="keyed by number, not text"
  )
  counter_hits "$plant" 2>&1
)"
expect_eq "$name" \
  "$(printf '    %s carries its own harness scaffolding\n' a.test.sh:5 b.test.sh:2 c.test.sh:1 d.test.sh:1)" \
  "$got"

name="#595: a tree with no counter-initialisation hit is reported clean"
plant="$(scratch_dir)"
printf '%s\n' '#!/usr/bin/env bash' 'x=1' > "$plant/a.test.sh"
got="$(declare -A COUNTER_EXEMPT=(); counter_hits "$plant" 2>&1)"
expect_eq "$name" "" "$got"

name="#595: the counter audit names the file and line of pass=0; fail=0, pass=\"\${pass:-0}\" and pass=0 fail=0"
plant="$(scratch_dir)"
printf '%s\n' '#!/usr/bin/env bash' 'pass=0; fail=0' > "$plant/a.test.sh"
printf '%s\n' '#!/usr/bin/env bash' 'x=1' 'pass="${pass:-0}"' > "$plant/b.test.sh"
printf '%s\n' '#!/usr/bin/env bash' 'pass=0 fail=0' > "$plant/c.test.sh"
got="$(declare -A COUNTER_EXEMPT=(); counter_hits "$plant" 2>&1)"
expect_eq "$name" \
  "$(printf '    %s carries its own harness scaffolding\n' a.test.sh:2 b.test.sh:3 c.test.sh:2)" \
  "$got"

name="#595: the tree audit admits a counter-initialisation hit only through the COUNTER_EXEMPT table"
plant="$(scratch_dir)"
mkdir -p "$plant/unit"
printf '%s\n' '#!/usr/bin/env bash' 'pass=0 fail=0' > "$plant/a.test.sh"
printf '%s\n' '#!/usr/bin/env bash' 'pass=0 fail=0' > "$plant/b.test.sh"
printf '%s\n' '#!/usr/bin/env bash' 'x=1' > "$plant/unit/c.test.sh"
got="$(
  declare -A COUNTER_EXEMPT=(["a.test.sh:pass=0 fail=0"]="a planted suite's own counters")
  scaffolding_hits "$plant" 2>&1
)"
expect_eq "$name" "    b.test.sh:2 carries its own harness scaffolding" "$got"

name="#595: model-knobs-recorded$sfx carries no counter-initialisation line and no exemption names it"
got="$(declare -A COUNTER_EXEMPT=(); counter_hits "$TESTS" 2>&1 | grep -F "model-knobs-recorded$sfx:")"
for key in "${!COUNTER_EXEMPT[@]}"; do
  [[ "$key" == model-knobs-recorded$sfx:* ]] && got+=$'\n'"    COUNTER_EXEMPT names $key"
done
expect_eq "$name" "" "$got"

name="#595: the widened audit flags neither lib/harness.sh nor unit/harness$sfx"
got="$(
  declare -A COUNTER_EXEMPT=()
  scaffolding_hits "$TESTS" 2>&1 | grep -E '(lib/harness\.sh|unit/harness\.test\.sh):'
)"
expect_eq "$name" "" "$got"

name="#704: a suite under tests/ or tests/unit/ that defines win, window or windows is named by <suite>:<line>"
plant="$(scratch_dir)"
mkdir -p "$plant/unit" "$plant/lib"
printf '%s\n' '#!/usr/bin/env bash' 'win() {' '  windows "$1" x' '}' > "$plant/a.test.sh"
printf '%s\n' '#!/usr/bin/env bash' 'x=1' 'window() { :; }' 'function windows() { :; }' \
  '  function window() { :; }' > "$plant/unit/b.test.sh"
printf '%s\n' '#!/usr/bin/env bash' 'got="$(windows "$text" x)"' > "$plant/c.test.sh"
printf '%s\n' 'windows() { :; }' > "$plant/lib/window.sh"
got="$(hoisted_copy_hits "$plant" 2>&1)"
expect_eq "$name" \
  "$(printf '    %s\n' 'a.test.sh:2 defines win()' 'unit/b.test.sh:3 defines window()' \
    'unit/b.test.sh:4 defines windows()' 'unit/b.test.sh:5 defines window()')" \
  "$got"

name="#704: a tree with no suite defining win, window or windows is reported clean"
plant="$(scratch_dir)"
printf '%s\n' '#!/usr/bin/env bash' 'got="$(windows "$text" x)"' > "$plant/a.test.sh"
got="$(hoisted_copy_hits "$plant" 2>&1)"
expect_eq "$name" "" "$got"

name="#704: a suite or record-helpers.sh that defines plain is named by <file>:<line>"
plant="$(scratch_dir)"
mkdir -p "$plant/unit" "$plant/lib"
printf '%s\n' '#!/usr/bin/env bash' "plain() { tr -d '*\`' | tr '[:upper:]' '[:lower:]'; }" \
  > "$plant/record-helpers.sh"
printf '%s\n' '#!/usr/bin/env bash' 'x=1' 'plain() {' "  tr -d '*\`' | tr '\n' ' '" '}' \
  > "$plant/unit/a.test.sh"
printf '%s\n' '#!/usr/bin/env bash' 'got="$(plain < "$f")"' > "$plant/b.test.sh"
printf '%s\n' 'plain() { :; }' > "$plant/lib/plain.sh"
got="$(hoisted_copy_hits "$plant" 2>&1)"
expect_eq "$name" \
  "$(printf '    %s\n' 'record-helpers.sh:2 defines plain()' 'unit/a.test.sh:3 defines plain()')" \
  "$got"

name="#704: a suite under tests/ or tests/unit/ that defines section_end is named by <suite>:<line>"
plant="$(scratch_dir)"
mkdir -p "$plant/unit" "$plant/lib"
printf '%s\n' '#!/usr/bin/env bash' 'section_end() {' '  echo 1' '}' > "$plant/a.test.sh"
printf '%s\n' '#!/usr/bin/env bash' 'x=1' '  function section_end() { :; }' > "$plant/unit/b.test.sh"
printf '%s\n' '#!/usr/bin/env bash' 'end="$(section_end "$f" 3)"' > "$plant/c.test.sh"
printf '%s\n' 'section_end() { :; }' > "$plant/lib/section-end.sh"
got="$(hoisted_copy_hits "$plant" 2>&1)"
expect_eq "$name" \
  "$(printf '    %s\n' 'a.test.sh:2 defines section_end()' 'unit/b.test.sh:3 defines section_end()')" \
  "$got"

name="#704: a suite that defines frontmatter_name is named by <suite>:<line>"
plant="$(scratch_dir)"
mkdir -p "$plant/lib"
printf '%s\n' '#!/usr/bin/env bash' 'frontmatter_name() {' '  echo x' '}' > "$plant/a.test.sh"
printf '%s\n' 'frontmatter_name() { :; }' > "$plant/lib/frontmatter-name.sh"
got="$(hoisted_copy_hits "$plant" 2>&1)"
expect_eq "$name" "    a.test.sh:2 defines frontmatter_name()" "$got"

name="#704: a suite that defines first_record or record_number is named by <suite>:<line>"
plant="$(scratch_dir)"
mkdir -p "$plant/unit" "$plant/lib"
printf '%s\n' '#!/usr/bin/env bash' 'first_record() {' '  head -1' '}' > "$plant/a.test.sh"
printf '%s\n' '#!/usr/bin/env bash' 'x=1' 'record_number() { :; }' > "$plant/unit/b.test.sh"
printf '%s\n' 'first_record() { :; }' 'record_number() { :; }' > "$plant/lib/first-record.sh"
got="$(hoisted_copy_hits "$plant" 2>&1)"
expect_eq "$name" \
  "$(printf '    %s\n' 'a.test.sh:2 defines first_record()' 'unit/b.test.sh:3 defines record_number()')" \
  "$got"

name="#704: a suite that defines fenced_lines is named by <suite>:<line>"
plant="$(scratch_dir)"
mkdir -p "$plant/unit" "$plant/lib"
printf '%s\n' '#!/usr/bin/env bash' 'fenced_lines() {' '  awk 1' '}' > "$plant/a.test.sh"
printf '%s\n' '#!/usr/bin/env bash' 'x=1' '  function fenced_lines() { :; }' > "$plant/unit/b.test.sh"
printf '%s\n' '#!/usr/bin/env bash' 'got="$(fenced_lines x)"' > "$plant/c.test.sh"
printf '%s\n' 'fenced_lines() { :; }' > "$plant/lib/fenced-lines.sh"
got="$(hoisted_copy_hits "$plant" 2>&1)"
expect_eq "$name" \
  "$(printf '    %s\n' 'a.test.sh:2 defines fenced_lines()' 'unit/b.test.sh:3 defines fenced_lines()')" \
  "$got"

name="#704: a suite that defines need_claude_md_records is named by <suite>:<line>"
plant="$(scratch_dir)"
mkdir -p "$plant/unit" "$plant/lib"
printf '%s\n' '#!/usr/bin/env bash' 'need_claude_md_records() {' '  return 0' '}' > "$plant/a.test.sh"
printf '%s\n' '#!/usr/bin/env bash' 'x=1' '  function need_claude_md_records() { :; }' \
  > "$plant/unit/b.test.sh"
printf '%s\n' '#!/usr/bin/env bash' '  need_claude_md_records || return' > "$plant/c.test.sh"
printf '%s\n' 'need_claude_md_records() { :; }' > "$plant/lib/claude-md-records.sh"
got="$(hoisted_copy_hits "$plant" 2>&1)"
expect_eq "$name" \
  "$(printf '    %s\n' 'a.test.sh:2 defines need_claude_md_records()' \
    'unit/b.test.sh:3 defines need_claude_md_records()')" \
  "$got"

name="#704: a suite that defines probe_every_exemption_carries_a_reason is named by <suite>:<line>"
plant="$(scratch_dir)"
mkdir -p "$plant/unit" "$plant/lib"
printf '%s\n' '#!/usr/bin/env bash' 'probe_every_exemption_carries_a_reason() {' '  return 0' '}' \
  > "$plant/a.test.sh"
printf '%s\n' '#!/usr/bin/env bash' 'x=1' '  function probe_every_exemption_carries_a_reason() { :; }' \
  > "$plant/unit/b.test.sh"
printf '%s\n' '#!/usr/bin/env bash' 'probe_every_exemption_carries_a_reason' > "$plant/c.test.sh"
printf '%s\n' 'probe_every_exemption_carries_a_reason() { :; }' > "$plant/lib/exemption-reasons.sh"
got="$(hoisted_copy_hits "$plant" 2>&1)"
expect_eq "$name" \
  "$(printf '    %s\n' 'a.test.sh:2 defines probe_every_exemption_carries_a_reason()' \
    'unit/b.test.sh:3 defines probe_every_exemption_carries_a_reason()')" \
  "$got"

name="#704: a guard suite that defines verdict is named by <suite>:<line>"
plant="$(scratch_dir)"
mkdir -p "$plant/unit" "$plant/lib"
printf '%s\n' '#!/usr/bin/env bash' 'verdict() {' '  ok' '}' > "$plant/count-line-guard.test.sh"
printf '%s\n' '#!/usr/bin/env bash' 'x=1' '  function verdict() { :; }' > "$plant/unit/emitted-text.test.sh"
printf '%s\n' '#!/usr/bin/env bash' 'verdict "$name"' > "$plant/prompt-test-tiers.test.sh"
printf '%s\n' 'verdict() { :; }' > "$plant/lib/verdict.sh"
got="$(hoisted_copy_hits "$plant" 2>&1)"
expect_eq "$name" \
  "$(printf '    %s\n' 'count-line-guard.test.sh:2 defines verdict()' \
    'unit/emitted-text.test.sh:3 defines verdict()')" \
  "$got"

name="#704: no suite under tests/ or tests/unit/ defines its own copy of a helper hoisted into tests/lib/"
problems="$(hoisted_copy_hits "$TESTS")"
if [[ -z "$problems" ]]; then
  ok
else
  no "$name"
  printf '%s\n' "$problems"
fi

name="no suite builds its own scratch directory, exit trap or tmp git repository"
problems=""
copies="$(cd "$TESTS" && grep -nE \
  -e 'mktemp[ ]-d' \
  -e '^[[:space:]]*trap[[:space:]].*EXIT' \
  -e 'git[ ]init' \
  ./*.sh ./unit/*.sh | grep -v '^\./unit/harness\.test\.sh:')"
while IFS= read -r hit; do
  [[ -n "$hit" ]] || continue
  file="${hit%%:*}"
  rest="${hit#*:}"
  problems+="    ${file#./}:${rest%%:*} builds its own scratch instead of the harness's"$'\n'
done <<< "$copies"
if [[ -z "$problems" ]]; then
  ok
else
  no "$name"
  printf '%s' "$problems"
fi

finish
