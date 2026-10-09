#!/usr/bin/env bash
# Unit tests for scripts/detect-test-command.sh — prints the one command that runs the
# full suite of the repo at [repo-root] on stdout and exits 0; prints nothing and exits 3
# when it cannot decide.
#
# Contract under test:
#   detect-test-command.sh [--issue <body-file>] [repo-root]   (root default: .)
#   precedence, first match wins: the issue body's own `Test command:` line,
#   .veri/test-command override, npm/pnpm/yarn, make, pytest, go, cargo, unittest —
#   otherwise exit 3.
#
# Run: scripts/tests/detect-test-command.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
DETECT="$HERE/../detect-test-command.sh"
source "$HERE/lib/harness.sh"
work="$(scratch_dir)"

detect() {  # detect <args...> -> runs the script, sets $out/$code
  out="$("$DETECT" "$@" 2>/dev/null)"
  code=$?
}

matched() { [[ "$code" == 0 ]] && [[ "$out" == "$want" ]]; }

want='bin/docs-suite --only docs --strict'
repo="$work/issue-command"
body="$work/issue-command-body.md"
mkdir -p "$repo/.veri"
printf '%s\n' 'bin/run-suite --all --strict' > "$repo/.veri/test-command"
printf '{"scripts":{"test":"jest"}}\n' > "$repo/package.json"
printf 'test:\n\techo hi\n' > "$repo/Makefile"
printf '## Notes\n\nTest command: %s\n\nTest command: make other-test\n' "$want" > "$body"

detect --issue "$body" "$repo"

matched \
  && ok || no "--issue: the body's first Test command: line beats .veri/test-command and every inference, printed verbatim (exit=$code want 0, stdout='$out' want '$want')"

repo="$work/no-markers"
mkdir -p "$repo/src"
printf '# demo\n\nRun the test suite however you like.\n' > "$repo/README.md"
printf 'int main(void) { return 0; }\n' > "$repo/src/main.c"

detect "$repo"

[[ "$code" == 3 ]] && [[ -z "$out" ]] \
  && ok || no "a repo matching nothing prints nothing and exits 3 (exit=$code want 3, stdout='$out' want '')"

misread=""
for flag in --tier --issue; do
  out="$("$DETECT" "$flag" 2>"$work/no-value-stderr")"; code=$?
  err="$(cat "$work/no-value-stderr")"
  [[ "$code" == 1 && -z "$out" && -z "$err" ]] \
    || misread="$misread ($flag: exit=$code want 1, stdout='$out' want '', stderr='$err' want '')"
done

[[ -z "$misread" ]] \
  && ok || no "--tier and --issue, each with no value, exit 1 with empty stdout and empty stderr —$misread"

repo="$work/linked-repo"
mkdir -p "$repo" "$work/elsewhere"
printf 'test:\n\techo hi\n' > "$repo/Makefile"
ln -s "$(cd "$HERE/../.." && pwd)" "$work/linked-skill"
in_place="$(cd "$repo" && "$DETECT" 2>&1)"; in_place_code=$?
linked="$(cd "$work/elsewhere" && "$work/linked-skill/scripts/detect-test-command.sh" "$repo" 2>&1)"; linked_code=$?
if [[ "$linked" == "$in_place" && "$linked_code" -eq "$in_place_code" && "$in_place" == "make test" ]]; then ok; else
  no "detect-test-command.sh run through a symlink to the skill directory and from another working directory prints the same command and exit code as when run in place"
  diff <(printf '%s\nexit %s\n' "$in_place" "$in_place_code") <(printf '%s\nexit %s\n' "$linked" "$linked_code")
fi

repo="$work/issue-names-fast-tier"
body="$work/issue-names-fast-tier-body.md"
mkdir -p "$repo"
printf '# notes\n\nveri: fast tests: `make unit`\nveri: all tests: `make test`\n' > "$repo/CLAUDE.md"
printf '## Notes\n\nTest command: make unit\n' > "$body"
fast="$("$DETECT" --tier fast --issue "$body" "$repo" 2>/dev/null)"
want='make test'

detect --tier all --issue "$body" "$repo"

[[ "$fast" == 'make unit' ]] && matched \
  && ok || no "--tier all: an issue whose Test command: equals the fast tier's command prints CLAUDE.md's veri: all tests: command (fast='$fast' want 'make unit', exit=$code want 0, stdout='$out' want '$want')"

finish
