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

fixture_root() {
  local root="$work/$1"
  local hooks="$root/docs"
  hooks+=/hooks
  mkdir -p "$root/skills/tdd/scripts" "$hooks"
  printf 'test:\n\t@echo ok\n' > "$root/Makefile"
  printf '#!/bin/sh\nexit 0\n' > "$hooks/reference-transaction"
  echo "$root"
}

script() {
  printf '#!/usr/bin/env bash\n%s\n' "$2" > "$1"
  chmod +x "$1"
}

root="$(fixture_root orphans)"
S="$root/skills/tdd/scripts"
printf '# skill\n\nRun `$S/entry.sh <n>` to start.\n' > "$root/skills/tdd/SKILL.md"
script "$S/entry.sh" '"$(dirname "$0")/helper.sh" "$@"'
script "$S/helper.sh" 'echo helped'
script "$S/orphan-top.sh" '"$(dirname "$0")/orphan-leaf.sh" "$@"'
script "$S/orphan-leaf.sh" '"$(dirname "$0")/orphan-top.sh" --again'
expected="$(printf 'orphan-leaf.sh\norphan-top.sh')"
out="$("$UNREACHABLE" "$root" 2>&1)"; code=$?
got="$(printf '%s\n' "$out" | sed '/^$/d; s#.*/##' | sort)"
if [[ "$code" == 0 && "$got" == "$expected" ]]; then ok; else
  no "scripts reached by no entry point are listed, including an orphan whose only caller is another orphan (code=$code)"
  diff <(printf '%s\n' "$expected") <(printf '%s\n' "$got") | sed 's/^/    /'
fi

root="$(fixture_root cycle)"
S="$root/skills/tdd/scripts"
printf '# skill\n\nRun `$S/entry.sh <n>` to start.\n' > "$root/skills/tdd/SKILL.md"
script "$S/entry.sh" '"$(dirname "$0")/helper.sh" "$@"'
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

finish
