#!/usr/bin/env bash
# Tests for scripts/unreachable.sh — lists each script under skills/tdd/scripts/ that no
# declared entry point reaches: SKILL.md and the procedure files it reads, the Makefile's
# targets, the git hooks under docs/hooks/.
#
# Contract under test:
#   unreachable.sh <repo-root> → exit 0, one unreachable script per line on stdout
#
# Run: scripts/tests/unreachable.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
UNREACHABLE="$HERE/../unreachable.sh"
source "$HERE/lib/harness.sh"
source "$HERE/../lib/background.sh"

work="$(scratch_dir)"

script() {
  printf '#!/usr/bin/env bash\n%s\n' "$2" > "$1"
  chmod +x "$1"
}

fixture_root() {
  local root="$work/$1"
  local hooks="$root/docs"
  hooks+=/hooks
  mkdir -p "$root/skills/tdd/scripts" "$hooks"
  printf 'test:\n\t@echo ok\n' > "$root/Makefile"
  printf '#!/bin/sh\nexit 0\n' > "$hooks/reference-transaction"
  printf '# skill\n\nRun `$S/entry.sh <n>` to start.\n' > "$root/skills/tdd/SKILL.md"
  script "$root/skills/tdd/scripts/entry.sh" '"$(dirname "$0")/helper.sh" "$@"'
  echo "$root"
}

expect_listing() {
  local root="$1" expected="$2" name="$3" out code got
  out="$("$UNREACHABLE" "$root" 2>&1)"; code=$?
  got="$(printf '%s\n' "$out" | sed '/^$/d; s#.*/##' | sort)"
  if [[ "$code" == 0 && "$got" == "$expected" ]]; then ok; else
    no "$name (code=$code)"
    diff <(printf '%s\n' "$expected") <(printf '%s\n' "$got") | sed 's/^/    /'
  fi
}

root="$(fixture_root orphans)"
S="$root/skills/tdd/scripts"
script "$S/helper.sh" 'echo helped'
script "$S/orphan-top.sh" '"$(dirname "$0")/orphan-leaf.sh" "$@"'
script "$S/orphan-leaf.sh" '"$(dirname "$0")/orphan-top.sh" --again'
expect_listing "$root" "$(printf 'orphan-leaf.sh\norphan-top.sh')" \
  "scripts reached by no entry point are listed, including an orphan whose only caller is another orphan"

root="$(fixture_root cycle)"
S="$root/skills/tdd/scripts"
script "$S/helper.sh" '"$(dirname "$0")/entry.sh" --again'
script "$S/orphan.sh" 'echo alone'
record="$work/cycle.pids"
bg_start "$record" "$UNREACHABLE" "$root" > "$work/cycle.out" 2>&1
pid="$(awk '{ print $1 }' "$record")"
for (( tick = 0; tick < 100; tick++ )); do
  kill -0 "$pid" 2>/dev/null || break
  sleep 0.1
done
if kill -0 "$pid" 2>/dev/null; then
  bg_kill "$record"
  no "reached scripts that call each other are visited once, so the listing finishes (still running after 10 s)"
else
  wait "$pid"; code=$?
  got="$(sed '/^$/d; s#.*/##' "$work/cycle.out" | sort)"
  if [[ "$code" == 0 && "$got" == "orphan.sh" ]]; then ok; else
    no "reached scripts that call each other are visited once, so the listing finishes (code=$code)"
    diff <(printf 'orphan.sh\n') <(printf '%s\n' "$got") | sed 's/^/    /'
  fi
fi

root="$(fixture_root make-target)"
S="$root/skills/tdd/scripts"
cp "$HERE/../../../../Makefile" "$root/Makefile"
cp "$UNREACHABLE" "$S/unreachable.sh"
cp -R "$HERE/../veri" "$S/veri"
script "$S/helper.sh" 'echo helped'
script "$S/orphan.sh" 'echo alone'
out="$(make --no-print-directory -s -C "$root" unreachable 2>&1)"; code=$?
got="$(printf '%s\n' "$out" | sed '/^$/d' | sort)"
name="make unreachable runs unreachable.sh over the repository it is run in and exits 0, so the check is itself reached from a declared entry point"
if [[ "$code" == 0 && "$got" == "orphan.sh" ]]; then ok; else
  no "$name (code=$code)"
  diff <(printf 'orphan.sh\n') <(printf '%s\n' "$got") | sed 's/^/    /'
fi

root="$(fixture_root linked)"
S="$root/skills/tdd/scripts"
script "$S/helper.sh" 'echo helped'
script "$S/orphan.sh" 'echo alone'
ln -s "$(cd "$HERE/../.." && pwd)" "$work/linked-skill"
mkdir -p "$work/elsewhere"
in_place="$("$UNREACHABLE" "$root" 2>&1)"; in_place_code=$?
linked="$(cd "$work/elsewhere" && "$work/linked-skill/scripts/unreachable.sh" "$root" 2>&1)"; linked_code=$?
if [[ "$linked" == "$in_place" && "$linked_code" -eq "$in_place_code" && "$in_place" == *"orphan.sh"* ]]; then ok; else
  no "unreachable.sh run through a symlink to the skill directory and from another working directory prints the same listing and exit code as when run in place"
  diff <(printf '%s\nexit %s\n' "$in_place" "$in_place_code") <(printf '%s\nexit %s\n' "$linked" "$linked_code") | sed 's/^/    /'
fi

out="$("$UNREACHABLE" 2> "$work/noarg.err")"; code=$?
err="$(cat "$work/noarg.err")"
name="unreachable.sh with no argument exits 2 with empty stdout and exactly its usage line on stderr"
if [[ "$code" == 2 && -z "$out" && "$err" == "usage: unreachable.sh <repo-root>" ]]; then ok; else
  no "$name (code=$code)"
  printf '    stdout: %s\n    stderr: %s\n' "$out" "$err"
fi

finish
