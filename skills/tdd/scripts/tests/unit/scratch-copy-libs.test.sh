#!/usr/bin/env bash
# Audits that no suite copies a script into a scratch tree without the lib it cannot start
# without. A `cp` line under tests/ or tests/unit/ that names a script under scripts/ which
# sources lib/exit-contract.sh — by a literal path or through the suite's own variable
# assignments — is named, unless the suite also puts lib/exit-contract.sh in the tree: by
# naming it, by copying a directory whole with `cp -R`, or by copying `lib/*.sh`.
# A suite that plants another suite (its GUARD=) copies every tests/lib file that suite sources.
# Admitted to the fast tier by its own usage count: git 0, python3 0, server 0, sleep 0.
#
# Run: scripts/tests/unit/scratch-copy-libs.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
TESTS="$(cd "$HERE/.." && pwd)"
SCRIPTS="$(cd "$TESTS/.." && pwd)"
export LC_ALL=C
source "$TESTS/lib/harness.sh"
source "$TESTS/lib/verdict.sh"

needs_contract() {
  [[ -f "$SCRIPTS/$1" ]] && grep -E '^(source|\.)[[:space:]].*lib/exit-contract\.sh' "$SCRIPTS/$1" > /dev/null
}

read_vars() {
  local line cd_pwd='^[[:space:]]*([A-Za-z_][A-Za-z0-9_]*)="\$\(cd "(.*)" && pwd\)([^"]*)"[[:space:]]*$'
  while IFS= read -r line; do
    [[ "$line" =~ $cd_pwd ]] && vars["${BASH_REMATCH[1]}"]="${BASH_REMATCH[2]}${BASH_REMATCH[3]}" && continue
    [[ "$line" =~ ^[[:space:]]*([A-Za-z_][A-Za-z0-9_]*)=[\'\"]?([^\'\"]*)[\'\"]?[[:space:]]*$ ]] \
      && vars["${BASH_REMATCH[1]}"]="${BASH_REMATCH[2]}"
  done < "$1"
}

expand() {
  local text="$1" pass var
  for pass in 1 2 3; do
    for var in "${!vars[@]}"; do
      text="${text//\$\{$var\}/${vars[$var]}}"
      text="${text//\$$var/${vars[$var]}}"
    done
  done
  printf '%s' "$text"
}

names_script_lib() {
  local rest="$1"
  [[ "$rest" =~ skills/tdd/scripts/lib/[A-Za-z0-9_.-]+\.sh ]] && return 0
  while [[ "$rest" =~ /lib/([A-Za-z0-9_.-]+\.sh)(.*)$ ]]; do
    rest="${BASH_REMATCH[2]}"
    [[ -f "$SCRIPTS/lib/${BASH_REMATCH[1]}" ]] && return 0
  done
  return 1
}

lib_copy_hits() {
  local dir="$1" suite line n before quotes copy='(^|[[:space:];&|(`{])(cp|ln)[[:space:]]'
  for suite in "$dir"/*.test.sh "$dir"/unit/*.test.sh "$dir"/lib/*.sh; do
    [[ -f "$suite" ]] || continue
    local -A vars=()
    read_vars "$suite"
    n=0
    while IFS= read -r line; do
      n=$((n + 1))
      [[ "$line" =~ $copy ]] || continue
      before="${line%%"${BASH_REMATCH[0]}"*}"
      quotes="${before//[^\']/}"
      (( ${#quotes} % 2 == 0 )) || continue
      names_script_lib "$(expand "${line#"$before"}")" || continue
      printf '    %s:%s copies an individual lib file\n' "${suite#"$dir"/}" "$n"
    done < "$suite"
  done
}

expect_hits() {
  local plant="$1"
  shift
  expect_eq "$name" "$(printf '    %s copies an individual lib file\n' "$@")" "$(lib_copy_hits "$plant" 2>&1)"
}

name="a suite that copies a script sourcing lib/exit-contract.sh into a scratch tree puts that lib there too"
problems=""
for suite in "$TESTS"/*.test.sh "$TESTS"/unit/*.test.sh; do
  grep -F 'exit-contract.sh' "$suite" > /dev/null && continue
  grep -E '(^|[[:space:]])cp[[:space:]]+-[A-Za-z]*R' "$suite" > /dev/null && continue
  grep -E '(^|[[:space:]])cp[[:space:]].*lib/\*\.sh' "$suite" > /dev/null && continue
  declare -A vars=()
  read_vars "$suite"
  n=0
  while IFS= read -r line; do
    n=$((n + 1))
    [[ "$line" =~ (^|[[:space:]])cp[[:space:]] ]] || continue
    rest="$(expand "$line")"
    while [[ "$rest" =~ (^|[/\"\' ])([A-Za-z0-9_.-]+\.sh)(.*)$ ]]; do
      rest="${BASH_REMATCH[3]}"
      hit="    ${suite#"$TESTS"/}:$n copies ${BASH_REMATCH[2]} without lib/exit-contract.sh"$'\n'
      [[ "$problems" == *"$hit"* ]] && continue
      needs_contract "${BASH_REMATCH[2]}" && problems+="$hit"
    done
  done < "$suite"
  unset vars
done
verdict "$name"

name="a suite that copies run-suite.sh into a scratch tree copies skills/tdd/scripts/veri/ beside it, or is named <suite>:<line>"
problems=""
for suite in "$TESTS"/*.test.sh "$TESTS"/unit/*.test.sh; do
  declare -A vars=()
  read_vars "$suite"
  sites="" has_veri=""
  n=0
  while IFS= read -r line; do
    n=$((n + 1))
    [[ "$line" =~ (^|[[:space:]])(cp|ln)[[:space:]] ]] || continue
    rest="$(expand "$line")"
    [[ "$rest" =~ scripts/veri/?\*?[\"\']?[[:space:]] ]] && has_veri=1
    [[ "$rest" == *run-suite.sh* ]] && sites+="    ${suite#"$TESTS"/}:$n copies run-suite.sh without veri/"$'\n'
  done < "$suite"
  [[ -n "$has_veri" ]] || problems+="$sites"
  unset vars
done
verdict "$name"

name="a suite that plants a suite into a scratch tree copies every tests/lib file that suite sources"
problems=""
for suite in "$TESTS"/*.test.sh "$TESTS"/unit/*.test.sh; do
  [[ "$(< "$suite")" =~ GUARD=\'skills/tdd/scripts/tests/([A-Za-z0-9_.-]+\.test\.sh)\' ]] || continue
  planted="${BASH_REMATCH[1]}"
  [[ -f "$TESTS/$planted" ]] || continue
  copies="$(grep -E '(^|[[:space:]])cp[[:space:]]' "$suite")"
  grep -E '^(source|\.)[[:space:]].*lib/guard-plant\.sh' "$suite" > /dev/null \
    && copies+=$'\n'"$(grep -E '(^|[[:space:]])cp[[:space:]]' "$TESTS/lib/guard-plant.sh")"
  grep -E '(lib|LIB)"?/\*\.sh' <<< "$copies" > /dev/null && continue
  grep -E '(lib|LIB)"?/harness\.sh' <<< "$copies" > /dev/null || continue
  while IFS= read -r lib; do
    grep -E "(lib|LIB)\"?/$lib" <<< "$copies" > /dev/null \
      || problems+="    ${suite#"$TESTS"/} plants $planted without lib/$lib"$'\n'
  done < <(sed -nE 's#^(source|\.)[[:space:]]+"\$HERE/lib/([A-Za-z0-9_.-]+\.sh)".*#\2#p' "$TESTS/$planted")
done
verdict "$name"

name="#749: the lib-copy guard names <suite>:<line> for a cp or ln of an individual lib file, never for lib/*.sh or the lib dir"
plant="$(scratch_dir)"
mkdir -p "$plant/unit"
printf '%s\n' '#!/usr/bin/env bash' 'mkdir -p "$tree/lib"' \
  'cp "$ROOT/skills/tdd/scripts/lib/exit-contract.sh" "$tree/lib/"' > "$plant/a.test.sh"
printf '%s\n' '#!/usr/bin/env bash' 'ln -s "$ROOT/skills/tdd/scripts/lib/exit-contract.sh" "$tree/lib/exit-contract.sh"' \
  > "$plant/unit/b.test.sh"
printf '%s\n' '#!/usr/bin/env bash' 'cp "$ROOT"/skills/tdd/scripts/lib/*.sh "$tree/lib/"' \
  'cp -R "$ROOT/skills/tdd/scripts/lib" "$tree/"' > "$plant/c.test.sh"
expect_hits "$plant" a.test.sh:3 unit/b.test.sh:2

name="#749: the lib-copy guard names a cp or ln of an individual lib file that follows ;, &&, | or \$( with no space"
plant="$(scratch_dir)"
printf '%s\n' '#!/usr/bin/env bash' \
  'mkdir -p "$tree/lib";cp "$ROOT/skills/tdd/scripts/lib/exit-contract.sh" "$tree/lib/"' \
  'true&&ln -s "$ROOT/skills/tdd/scripts/lib/exit-contract.sh" "$tree/lib/"' \
  'echo x|cp "$ROOT/skills/tdd/scripts/lib/exit-contract.sh" "$tree/lib/"' \
  'out=$(cp "$ROOT/skills/tdd/scripts/lib/exit-contract.sh" "$tree/lib/")' > "$plant/d.test.sh"
expect_hits "$plant" d.test.sh:2 d.test.sh:3 d.test.sh:4 d.test.sh:5

name="#749: the lib-copy guard names a cp or ln of an individual lib file opened by a backtick or a { with no space"
plant="$(scratch_dir)"
printf '%s\n' '#!/usr/bin/env bash' \
  'out=`cp "$ROOT/skills/tdd/scripts/lib/exit-contract.sh" "$tree/lib/"`' \
  '{ln -s "$ROOT/skills/tdd/scripts/lib/exit-contract.sh" "$tree/lib/"; }' > "$plant/e.test.sh"
expect_hits "$plant" e.test.sh:2 e.test.sh:3

name="#749: the lib-copy guard names a cp of an individual lib file made through the suite's own variable assignment"
plant="$(scratch_dir)"
printf '%s\n' '#!/usr/bin/env bash' \
  'cp "$ROOT/skills/tdd/scripts/lib/exit-contract.sh" "$tree/lib/"' \
  'GUARD_LIB="$ROOT/skills/tdd/scripts/lib/count-line-guard.sh"' \
  'cp "$GUARD_LIB" "$tree/lib/"' > "$plant/f.test.sh"
expect_hits "$plant" f.test.sh:2 f.test.sh:4

name="#749: the lib-copy guard names a tests/lib helper's cp of an individual lib file, never a printf, sed or cat rewrite into a lib path"
plant="$(scratch_dir)"
mkdir -p "$plant/lib"
printf '%s\n' '#!/usr/bin/env bash' \
  'copy_one() {' \
  '  cp "$ROOT/skills/tdd/scripts/lib/exit-contract.sh" "$1/lib/"' \
  '}' > "$plant/lib/copy-one.sh"
printf '%s\n' '#!/usr/bin/env bash' \
  'printf "%s\n" "x() { :; }" > "$tree/skills/tdd/scripts/lib/ledger.sh"' \
  'sed "s/a/b/" "$ROOT/skills/tdd/scripts/lib/count-line-guard.sh" > "$tree/skills/tdd/scripts/lib/count-line-guard.sh"' \
  'cat "$ROOT/skills/tdd/scripts/lib/exit-contract.sh" > "$tree/skills/tdd/scripts/lib/exit-contract.sh"' \
  > "$plant/g.test.sh"
expect_hits "$plant" lib/copy-one.sh:3

name="#749: the lib-copy guard names a cp or ln of an individual lib file reached by a relative path, never a copy of a tests/lib file"
plant="$(scratch_dir)"
printf '%s\n' '#!/usr/bin/env bash' \
  'cp "$HERE/../lib/exit-contract.sh" "$tree/lib/"' \
  'cp "$(dirname "$X")/lib/exit-contract.sh" "$tree/lib/"' \
  'ln -s "$SCRIPTS/lib/exit-contract.sh" "$tree/lib/"' \
  'cp "$HERE/lib/harness.sh" "$tree/tests/lib/"' > "$plant/h.test.sh"
expect_hits "$plant" h.test.sh:2 h.test.sh:3 h.test.sh:4

name="#749: the lib-copy guard names a cp of an individual lib file whose variable is assigned \"\$(cd \"<dir>\" && pwd)/<name>.sh\""
plant="$(scratch_dir)"
mkdir -p "$plant/lib"
printf '%s\n' '#!/usr/bin/env bash' \
  'ONE_LIB="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../lib" && pwd)/exit-contract.sh"' \
  'cp "$ONE_LIB" "$1/skills/tdd/scripts/lib/"' > "$plant/lib/copy-via-cd.sh"
expect_hits "$plant" lib/copy-via-cd.sh:3

name="#749: the lib-copy guard reads only a cp's own arguments, never a lib named earlier on its line or a cp inside a single-quoted string"
plant="$(scratch_dir)"
printf '%s\n' '#!/usr/bin/env bash' \
  'LIB="$ROOT/skills/tdd/scripts/lib/background.sh"' \
  '( source "$LIB" && cp "$record" "$kept" )' \
  "cp_line='  cp \"\$ROOT/skills/tdd/scripts/lib/exit-contract.sh\" \"\$tree/lib/\"'" \
  "  'cp \"\$ROOT/skills/tdd/scripts/lib/exit-contract.sh\" \"\$tree/lib/\"' > \"\$plant/x.test.sh\"" \
  'source "$LIB"; cp "$LIB" "$tree/lib/"' > "$plant/i.test.sh"
expect_hits "$plant" i.test.sh:6

name="#749: the real tree passes the lib-copy guard: no suite or tests/lib helper copies an individual lib file"
expect_eq "$name" "" "$(lib_copy_hits "$TESTS" 2>&1)"

finish
