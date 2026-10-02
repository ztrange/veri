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

counter_re='^[[:space:]]*pass=0[[:space:]]+fail=0'
declare -A COUNTER_EXEMPT=()

tree_grep() {
  local dir="$1"
  shift
  (cd "$dir" && shopt -s nullglob && grep -nE "$@" ./*.sh ./unit/*.sh) \
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
printf '%s\n' 'pass=0 fail=0' > "$plant/unit/harness.test.sh"
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
