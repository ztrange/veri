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

lib_copy_hits() {
  local dir="$1" suite line n copy='(^|[[:space:];&|(])(cp|ln)[[:space:]]'
  for suite in "$dir"/*.test.sh "$dir"/unit/*.test.sh; do
    [[ -f "$suite" ]] || continue
    n=0
    while IFS= read -r line; do
      n=$((n + 1))
      [[ "$line" =~ $copy ]] || continue
      [[ "$line" =~ skills/tdd/scripts/lib/[A-Za-z0-9_.-]+\.sh ]] || continue
      printf '    %s:%s copies an individual lib file\n' "${suite#"$dir"/}" "$n"
    done < "$suite"
  done
}

name="a suite that copies a script sourcing lib/exit-contract.sh into a scratch tree puts that lib there too"
problems=""
for suite in "$TESTS"/*.test.sh "$TESTS"/unit/*.test.sh; do
  grep -F 'exit-contract.sh' "$suite" > /dev/null && continue
  grep -E '(^|[[:space:]])cp[[:space:]]+-[A-Za-z]*R' "$suite" > /dev/null && continue
  grep -E '(^|[[:space:]])cp[[:space:]].*lib/\*\.sh' "$suite" > /dev/null && continue
  declare -A vars=()
  while IFS= read -r line; do
    [[ "$line" =~ ^[[:space:]]*([A-Za-z_][A-Za-z0-9_]*)=[\'\"]?([^\'\"]*)[\'\"]?[[:space:]]*$ ]] \
      && vars["${BASH_REMATCH[1]}"]="${BASH_REMATCH[2]}"
  done < "$suite"
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
got="$(lib_copy_hits "$plant" 2>&1)"
expect_eq "$name" \
  "$(printf '    %s copies an individual lib file\n' a.test.sh:3 unit/b.test.sh:2)" \
  "$got"

name="#749: the lib-copy guard names a cp or ln of an individual lib file that follows ;, &&, | or \$( with no space"
plant="$(scratch_dir)"
printf '%s\n' '#!/usr/bin/env bash' \
  'mkdir -p "$tree/lib";cp "$ROOT/skills/tdd/scripts/lib/exit-contract.sh" "$tree/lib/"' \
  'true&&ln -s "$ROOT/skills/tdd/scripts/lib/exit-contract.sh" "$tree/lib/"' \
  'echo x|cp "$ROOT/skills/tdd/scripts/lib/exit-contract.sh" "$tree/lib/"' \
  'out=$(cp "$ROOT/skills/tdd/scripts/lib/exit-contract.sh" "$tree/lib/")' > "$plant/d.test.sh"
got="$(lib_copy_hits "$plant" 2>&1)"
expect_eq "$name" \
  "$(printf '    %s copies an individual lib file\n' d.test.sh:2 d.test.sh:3 d.test.sh:4 d.test.sh:5)" \
  "$got"

finish
