#!/usr/bin/env bash
# Unit tests for `make watch` — a developer convenience that polls the tracked files
# and reruns `make unit` when one changes. Not a suite and not a gate.
#
# Contract under test:
#   make -n watch  → exits 0; `watch` is a phony target of its own, neither a prerequisite
#                    of test, unit or merge-gates nor depending on any of them. Read off
#                    make's own database (`make -np`), which prints recipes without running
#                    them, so no suite and no poll loop runs.
#   VERI_WATCH_INTERVAL → a value that is not a number of seconds exits 2 with a line on
#                    stderr naming the variable; unset, the loop sleeps 1 between passes.
#                    A stub `sleep` first on PATH records its argument and ends the loop by
#                    killing the shell that called it, so no real wait is ever taken.
#   a tracked file changes → the loop runs `make unit` once on its next pass, and not at
#                    all on a pass that finds nothing changed. Driven against a fixture repo
#                    with a stub sleep that counts passes and fabricates the changes.
#   one poll pass  → `watch_snapshot` (skills/tdd/scripts/lib/watch.sh) calls its stat
#                    wrapper `watch_stat` once, for 1 tracked file or 40. Pinned with an
#                    in-process spy: the library is sourced here and `watch_stat` replaced.
#   only `unit`    → every make the loop starts asks for `unit` and no other goal. A `make`
#                    wrapper passed as MAKE= logs each make's goals, and the case fails
#                    on any goal but `unit` — `test`, `merge-gates` or anything else.
#   the Makefile   → its comment on `make watch` calls it a developer convenience (or low
#                    priority), not part of `test`, that nothing gates on — as `profile`'s does.
#   the suite's lane → `make -n test` lists this suite and `make -n unit` does not: each
#                    target's roster read off its own expanded recipe, which runs nothing.
#
# Run: scripts/tests/watch.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"

source "$HERE/lib/harness.sh"

phony_rule() {
  awk -v t="$1:" '
    prev != "" && /^#  Phony target/ { print prev }
    { prev = ($1 == t) ? $0 : "" }
  ' <<< "$db"
}

prereqs() {
  phony_rule "$1" | sed 's/^[^:]*://' | tr ' ' '\n' | sed '/^$/d'
}

bounded() {
  "$@" &
  local watched=$! watchdog
  { /bin/sleep 30; kill -TERM "$watched"; } >/dev/null 2>&1 &
  watchdog=$!
  wait "$watched" 2>/dev/null
  kill "$watchdog" 2>/dev/null; wait "$watchdog" 2>/dev/null
}

name="make -n watch: its own .PHONY target, separate from test, unit and merge-gates"
problems=()
db="$(make --no-print-directory -np -C "$ROOT" watch 2>&1)" && code=0 || code=$?
[[ "$code" == 0 ]] ||
  problems+=("want make -n watch to exit 0, got $code: $(grep -m1 '\*\*\*' <<< "$db")")
[[ -n "$(phony_rule watch)" ]] || problems+=("no phony watch: entry in make's database")
for t in test unit merge-gates; do
  grep -qx "$t" < <(prereqs watch) && problems+=("watch depends on $t")
  grep -qx watch < <(prereqs "$t") && problems+=("$t depends on watch")
done
report "$name"

name="VERI_WATCH_INTERVAL: malformed exits 2 naming the variable, unset defaults to 1"
problems=()
scratch="$(scratch_dir)"
mkdir "$scratch/bin"
cat > "$scratch/bin/sleep" <<'STUB'
#!/bin/sh
printf '%s\n' "$1" >> "$SLEEP_LOG"
kill -TERM "$PPID"
STUB
chmod +x "$scratch/bin/sleep"
stubbed_watch() {
  SLEEP_LOG="$scratch/sleep.log" PATH="$scratch/bin:$PATH" \
    make --no-print-directory -s -C "$ROOT" watch
}
for bad in abc 1x; do
  err="$(VERI_WATCH_INTERVAL="$bad" stubbed_watch 2>&1 >/dev/null)" && code=0 || code=$?
  [[ "$code" == 2 ]] || problems+=("VERI_WATCH_INTERVAL='$bad': want exit 2, got $code")
  grep -q VERI_WATCH_INTERVAL <<< "$err" ||
    problems+=("VERI_WATCH_INTERVAL='$bad': stderr does not name the variable: ${err:-<empty>}")
done
: > "$scratch/sleep.log"
( unset VERI_WATCH_INTERVAL; bounded stubbed_watch >/dev/null 2>&1 )
first_wait="$(head -n1 "$scratch/sleep.log")"
[[ "$first_wait" == 1 ]] ||
  problems+=("VERI_WATCH_INTERVAL unset: want the loop's first wait to be sleep 1, got '${first_wait:-no sleep at all}'")
rm -rf "$scratch"
report "$name"

name="make watch: reruns make unit once per detected change, never between changes"
problems=()
scratch="$(scratch_dir)"
fixture="$scratch/repo"
mkdir -p "$scratch/bin" "$fixture/skills/tdd/scripts/tests/unit" "$fixture/skills/tdd/scripts/lib"
cp "$ROOT/Makefile" "$fixture/Makefile"
cp "$ROOT"/skills/tdd/scripts/lib/*.sh "$fixture/skills/tdd/scripts/lib/"
cp "$ROOT/skills/tdd/scripts/run-suite.sh" "$fixture/skills/tdd/scripts/"
cp -R "$ROOT/skills/tdd/scripts/veri" "$fixture/skills/tdd/scripts/"
printf 'original\n' > "$fixture/tracked.txt"
cat > "$fixture/skills/tdd/scripts/tests/unit/probe.test.sh" <<'SUITE'
#!/bin/sh
cat "$WATCH_COUNT" >> "$UNIT_LOG"
echo "1 passed, 0 failed"
SUITE
chmod +x "$fixture/skills/tdd/scripts/tests/unit/probe.test.sh"
git -C "$fixture" init -q && git -C "$fixture" add -A
cat > "$scratch/bin/sleep" <<'STUB'
#!/bin/sh
n=$(( $(cat "$WATCH_COUNT") + 1 ))
echo "$n" > "$WATCH_COUNT"
case "$n" in
  2|4) printf 'change %s\n' "$n" > "$WATCH_FIXTURE/tracked.txt"
       touch -t "200${n}01010000" "$WATCH_FIXTURE/tracked.txt" ;;
  6) kill -TERM "$PPID" ;;
esac
STUB
chmod +x "$scratch/bin/sleep"
echo 0 > "$scratch/count"
: > "$scratch/unit.log"
bounded env WATCH_COUNT="$scratch/count" WATCH_FIXTURE="$fixture" UNIT_LOG="$scratch/unit.log" \
  PATH="$scratch/bin:$PATH" make --no-print-directory -s -C "$fixture" watch >/dev/null 2>&1
runs="$(tr '\n' ' ' < "$scratch/unit.log" | sed 's/ $//')"
[[ "$runs" == "2 4" ]] ||
  problems+=("want make unit to run once after each change (after sleeps 2 and 4), ran after sleeps: '${runs:-none}'")
rm -rf "$scratch"
report "$name"

name="make watch: one poll pass calls its stat wrapper exactly once, whatever the number of tracked files"
problems=()
lib="$ROOT/skills/tdd/scripts/lib/watch.sh"
scratch="$(scratch_dir)"
if [[ -f "$lib" ]]; then
  source "$lib"
else
  problems+=("no stat-wrapper library to source at ${lib#"$ROOT"/}")
fi
if declare -F watch_snapshot >/dev/null; then
  watch_stat() { printf 'call\n' >> "$scratch/spy.log"; }
  for n in 1 40; do
    fixture="$scratch/repo-$n"
    mkdir -p "$fixture"
    for ((i = 1; i <= n; i++)); do printf '%s\n' "$i" > "$fixture/f$i.txt"; done
    git -C "$fixture" init -q && git -C "$fixture" add -A
    : > "$scratch/spy.log"
    ( cd "$fixture" && watch_snapshot >/dev/null 2>&1 )
    calls="$(wc -l < "$scratch/spy.log" | tr -d ' ')"
    [[ "$calls" == 1 ]] ||
      problems+=("one poll pass over $n tracked files: want 1 watch_stat call, got $calls")
  done
  unset -f watch_stat watch_snapshot
else
  problems+=("no watch_snapshot function (one poll pass) defined by ${lib#"$ROOT"/}")
fi
rm -rf "$scratch"
report "$name"

name="make watch: never runs any make target besides unit"
problems=()
scratch="$(scratch_dir)"
fixture="$scratch/repo"
real_make="$(command -v make)"
mkdir -p "$scratch/bin" "$fixture/skills/tdd/scripts/tests/unit" "$fixture/skills/tdd/scripts/lib"
cp "$ROOT/Makefile" "$fixture/Makefile"
cp "$ROOT"/skills/tdd/scripts/lib/*.sh "$fixture/skills/tdd/scripts/lib/"
cp "$ROOT/skills/tdd/scripts/run-suite.sh" "$fixture/skills/tdd/scripts/"
cp -R "$ROOT/skills/tdd/scripts/veri" "$fixture/skills/tdd/scripts/"
printf 'original\n' > "$fixture/tracked.txt"
cat > "$fixture/skills/tdd/scripts/tests/unit/probe.test.sh" <<'SUITE'
#!/bin/sh
echo "1 passed, 0 failed"
SUITE
chmod +x "$fixture/skills/tdd/scripts/tests/unit/probe.test.sh"
git -C "$fixture" init -q && git -C "$fixture" add -A
cat > "$scratch/bin/make" <<STUB
#!/bin/sh
goals=""; skip=""
for a in "\$@"; do
  if [ -n "\$skip" ]; then skip=""; continue; fi
  case "\$a" in
    -C|-f|-I|-o|-W) skip=1 ;;
    -*|*=*) ;;
    *) goals="\$goals \$a" ;;
  esac
done
printf '%s\n' "\${goals# }" >> "\$MAKE_LOG"
exec "$real_make" "\$@"
STUB
chmod +x "$scratch/bin/make"
cat > "$scratch/bin/sleep" <<'STUB'
#!/bin/sh
n=$(( $(cat "$WATCH_COUNT") + 1 ))
echo "$n" > "$WATCH_COUNT"
case "$n" in
  2) printf 'change\n' > "$WATCH_FIXTURE/tracked.txt"
     touch -t 200201010000 "$WATCH_FIXTURE/tracked.txt" ;;
  4) kill -TERM "$PPID" ;;
esac
STUB
chmod +x "$scratch/bin/sleep"
echo 0 > "$scratch/count"
: > "$scratch/make.log"
bounded env WATCH_COUNT="$scratch/count" WATCH_FIXTURE="$fixture" MAKE_LOG="$scratch/make.log" \
  PATH="$scratch/bin:$PATH" "$real_make" --no-print-directory -s -C "$fixture" \
  MAKE="$scratch/bin/make" watch >/dev/null 2>&1
[[ -s "$scratch/make.log" ]] ||
  problems+=("the loop never ran a nested make after a change, so nothing was checked")
while IFS= read -r goals; do
  [[ "$goals" == unit ]] ||
    problems+=("want every make the loop runs to ask for unit only, one asked for: '${goals:-<default goal>}'")
done < "$scratch/make.log"
rm -rf "$scratch"
report "$name"

name="Makefile: comment header documents make watch as a low-priority developer convenience, like profile and docs"
problems=()
header="$(awk '
  /^# `make watch`/ { on = 1 }
  on && !/^#/ { exit }
  on { sub(/^# ?/, ""); printf "%s ", $0 }
' "$ROOT/Makefile")"
if [[ -z "$header" ]]; then
  problems+=("no comment paragraph opening '# \`make watch\`' in the Makefile")
else
  grep -qiE 'developer convenience|low priority' <<< "$header" ||
    problems+=("the make watch comment does not call it a developer convenience or low priority: $header")
  grep -q 'not part of `test`' <<< "$header" ||
    problems+=("the make watch comment does not say it is not part of \`test\`: $header")
  grep -q 'nothing gates on it' <<< "$header" ||
    problems+=("the make watch comment does not say nothing gates on it: $header")
fi
report "$name"

name="watch.test.sh: run by make test's glob, not by make unit's"
problems=()
roster() { make --no-print-directory -C "$ROOT" -n "$1" 2>&1 | grep -o '[^ ]*\.test\.sh' | sort -u; }
grep -qx 'skills/tdd/scripts/tests/watch.test.sh' < <(roster test) ||
  problems+=("make -n test does not list skills/tdd/scripts/tests/watch.test.sh")
in_unit="$(roster unit | grep '/watch\.test\.sh$')"
[[ -z "$in_unit" ]] || problems+=("make -n unit lists $in_unit; want it absent from the fast tier")
report "$name"

finish
