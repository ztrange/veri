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

root="$(fixture_root tail)"
S="$root/skills/tdd/scripts"
script "$S/helper.sh" '"$(dirname "$0")/run-leaf.sh" "$@"'
script "$S/run-leaf.sh" 'echo ran'
script "$S/leaf.sh" 'echo alone'
expect_listing "$root" leaf.sh \
  "an orphan whose name is the tail of a reached script's name is still listed"

root="$(fixture_root bounds)"
S="$root/skills/tdd/scripts"
script "$S/helper.sh" "$(printf 'kept.sh\n# xleaf.sh 2leaf.sh my_leaf.sh v2.leaf.sh leaf.shx leaf.sh2 leaf.sh_old leaf.sh-old')"
script "$S/kept.sh" 'echo kept'
script "$S/leaf.sh" 'echo alone'
expect_listing "$root" leaf.sh \
  "a name alone on its line is a mention; one glued to a letter, digit, _ or - on either side, or to a . before it, is not"

root="$(fixture_root kinds)"
S="$root/skills/tdd/scripts"
mkdir -p "$S/lib"
script "$S/helper.sh" 'echo helped'
printf '\nEach leaf follows `WORKER.md`.\n' >> "$root/skills/tdd/SKILL.md"
printf '# worker\n\nRun `$S/by-procedure.sh`.\n' > "$root/skills/tdd/WORKER.md"
printf 'test:\n\t@echo ok\n\ncheck:\n\tskills/tdd/scripts/by-make.sh\n' > "$root/Makefile"
script "$S/by-make.sh" '"$(dirname "$0")/chained-make.sh" "$@"'
script "$S/chained-make.sh" 'echo chained'
printf '#!/bin/sh\nskills/tdd/scripts/by-hook.sh\n' > "$root/docs/hooks/reference-transaction"
script "$S/by-hook.sh" 'source "$(dirname "$0")/lib/via-lib.sh"'
printf 'via_lib() { "$S/by-lib.sh"; }\n' > "$S/lib/via-lib.sh"
script "$S/by-procedure.sh" 'echo procedure'
script "$S/by-lib.sh" 'echo lib'
script "$S/orphan.sh" 'echo alone'
expect_listing "$root" orphan.sh \
  "a script reached only from a procedure file, only from a Makefile recipe, or only from a git hook, directly or through a chain of scripts or a sourced lib/ file, is not listed"

root="$(fixture_root no-hooks)"
S="$root/skills/tdd/scripts"
hooks="$root/docs"
hooks+=/hooks
rm -r "$hooks"
script "$S/helper.sh" 'echo helped'
script "$S/orphan.sh" 'echo alone'
expect_listing "$root" orphan.sh \
  "a repo with no git hooks directory is listed with nothing on stderr"

root="$(fixture_root no-lib)"
S="$root/skills/tdd/scripts"
script "$S/helper.sh" '"$(dirname "$0")/lib.sh" "$@"'
script "$S/lib.sh" 'echo lib'
script "$S/orphan.sh" 'echo alone'
expect_listing "$root" orphan.sh \
  "a repo with no lib/ directory is listed with nothing on stderr, even when a script is named lib.sh"

root="$(fixture_root dynamic)"
S="$root/skills/tdd/scripts"
script "$S/helper.sh" "$(printf 'for kind in red green; do\n  "$(dirname "$0")/build-$kind-prompt.sh" "$@"\ndone')"
script "$S/build-red-prompt.sh" 'echo red'
script "$S/build-green-prompt.sh" 'echo green'
script "$S/orphan.sh" 'echo alone'
expect_listing "$root" orphan.sh \
  "a script named only through a built path such as \"\$S/build-\$kind-prompt.sh\" is not listed"

root="$(fixture_root dynamic-braced)"
S="$root/skills/tdd/scripts"
script "$S/helper.sh" "$(printf 'for kind in red green; do\n  "$(dirname "$0")/build-${kind}-prompt.sh" "$@"\ndone')"
script "$S/build-red-prompt.sh" 'echo red'
script "$S/orphan.sh" 'echo alone'
expect_listing "$root" orphan.sh \
  "a script named only through a braced built path such as \"\$S/build-\${kind}-prompt.sh\" is not listed"

root="$(fixture_root dynamic-md)"
S="$root/skills/tdd/scripts"
printf '# skill\n\nRun `$S/entry.sh <n>`, then read `prompts/develop-$phase.md`.\n' > "$root/skills/tdd/SKILL.md"
printf 'Run `$S/target.sh`.\n' > "$root/skills/tdd/develop-red.md"
script "$S/helper.sh" 'echo helped'
script "$S/target.sh" 'echo target'
script "$S/orphan.sh" 'echo alone'
expect_listing "$root" orphan.sh \
  "a procedure file named only through a built path such as prompts/develop-\$phase.md is read, so the script it names is not listed"

root="$(fixture_root test-only)"
S="$root/skills/tdd/scripts"
mkdir -p "$S/tests"
script "$S/helper.sh" 'echo helped'
script "$S/tested.sh" 'echo tested'
script "$S/tests/tested.test.sh" '"$(dirname "$0")/../tested.sh"'
script "$S/orphan.sh" 'echo alone'
before="$(cd "$root" && find . -type f -exec cksum {} + | sort)"
out="$("$UNREACHABLE" "$root" 2>&1)"; code=$?
after="$(cd "$root" && find . -type f -exec cksum {} + | sort)"
got="$(printf '%s\n' "$out" | sed '/^$/d' | sort)"
expected="$(printf 'orphan.sh\ntest-only: tested.sh')"
name="a script whose only caller is its own test suite is listed as test-only, apart from the unreachable ones, and no file is deleted or modified"
if [[ "$code" == 0 && "$got" == "$expected" && "$before" == "$after" ]]; then ok; else
  no "$name (code=$code)"
  diff <(printf '%s\n' "$expected") <(printf '%s\n' "$got") | sed 's/^/    /'
  diff <(printf '%s\n' "$before") <(printf '%s\n' "$after") | sed 's/^/    tree: /'
fi

root="$(fixture_root promised)"
S="$root/skills/tdd/scripts"
script "$S/helper.sh" 'echo "${VERI_READ:-1}"'
printf '\nSet `VERI_READ` to tune it, or `VERI_UNREAD` to skip it.\n' >> "$root/skills/tdd/SKILL.md"
mkdir -p "$S/lib"
script "$S/lib/knobs.sh" ': "${VERI_LIBREAD:-1}"'
printf '# notes\n\nRun `helper.sh` or `ghost.sh`; `VERI_READ`, `VERI_LIBREAD` and `VERI_GHOST` are knobs.\n' > "$root/CLAUDE.md"
printf 'Its suite is `helper.test.sh`; a leaf runs `"$S/build-$kind-prompt.sh"`.\n' >> "$root/CLAUDE.md"
expect_listing "$root" "$(printf 'promised-unread: VERI_GHOST\npromised-unread: VERI_UNREAD\npromised-unread: ghost.sh' | sort)" \
  "a VERI_* knob or a script name SKILL.md or CLAUDE.md promises and no script reads, or that does not exist, is listed as promised-unread"

root="$(fixture_root unpromised)"
rm "$root/skills/tdd/SKILL.md"
expect_listing "$root" "entry.sh" \
  "with neither SKILL.md nor CLAUDE.md there is nothing promised, so stdin is never read as a promise" \
  <<< 'Set `VERI_FROM_STDIN` or run `ghost.sh`.'

root="$(fixture_root nolib)"
S="$root/skills/tdd/scripts"
script "$S/helper.sh" 'echo helped'
printf '# notes\n\n`VERI_GHOST` is a knob.\n' > "$root/CLAUDE.md"
expect_listing "$root" "promised-unread: VERI_GHOST" \
  "a scripts tree with no lib/ is searched for knobs without an error for the missing directory"

finish
