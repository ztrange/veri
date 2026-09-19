#!/usr/bin/env bash
# Unit tests for harvest-usage.test.sh itself — how its cases 1 and 2 come by the leaf log
# they hand the harvester (issue #331).
# Zero-dependency plain-shell asserts, same idiom as hermetic-suites.test.sh.
#
# harvest-usage.test.sh needs a `.tdd/<leaf>.log` that a real run-leaf.sh assembled, because
# that writer appends the extracted result text after the stream, so the closing `result`
# record is never the log's last line. Nothing about that shape needs supervise.sh: its poll
# loop and its own unconditional harvest are not what those two cases ask about. So the suite
# launches run-leaf.sh directly, with its combined stdout/stderr in `.tdd/<leaf>.log`.
#
# Contract under test, observed by running harvest-usage.test.sh against a copy of the
# scripts whose supervise.sh, run-leaf.sh and harvest-usage.sh are tracers in front of the
# real ones:
#   supervise.sh                  → never launched.
#   run-leaf.sh                   → launched for `verify-refactor` and `develop-green`, against
#                                   a stub `CLAUDE_BIN`, with stdout AND stderr landing in
#                                   `.tdd/<leaf>.log` in its cwd.
#   verify-refactor's log         → holds a `result` record that is not its last line.
#   every harvest of that leaf    → reads a log byte-identical to the one run-leaf.sh left,
#                                   so no case hands the harvester a log written by hand.
#
# Run: scripts/tests/harvest-usage-launch.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
SCRIPTS="$HERE/.."
pass=0 fail=0

# report <name> — close a case whose probes collected into the `problems` array: an empty
# array is a pass, otherwise one FAIL line for the case and one indented line per problem.
report() {
  local name="$1"
  if [[ "${#problems[@]}" -eq 0 ]]; then
    pass=$((pass + 1))
  else
    fail=$((fail + 1))
    echo "FAIL - $name"
    printf '    %s\n' "${problems[@]}"
  fi
}

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
copy="$tmp/scripts"
trace="$tmp/trace"
mkdir -p "$copy/tests" "$trace"

# The copy: every top-level script and the sourced library, so each real script's own `$HERE`
# still finds its siblings, plus the one suite under observation.
cp "$SCRIPTS"/*.sh "$copy/"
cp -R "$SCRIPTS/lib" "$copy/lib"
cp "$HERE/harvest-usage.test.sh" "$copy/tests/"

for s in supervise run-leaf harvest-usage; do
  mv "$copy/$s.sh" "$copy/$s.real.sh"
done

# supervise.sh's tracer: one line per launch, then the real supervisor, so the observed suite
# runs exactly as it would untraced. The trace path is baked in (unquoted heredoc) rather than
# read from an environment the suite may not pass through.
cat > "$copy/supervise.sh" <<TRACER
#!/bin/sh
printf '%s\n' "\$*" >> "$trace/supervise"
exec "\$(dirname "\$0")/supervise.real.sh" "\$@"
TRACER

# run-leaf.sh's tracer: the real launcher, then a snapshot of every `.tdd/*.log` in its cwd
# (`pre`), then one line on STDERR, then a second snapshot (`post`). The line lands in the
# leaf's log only if the caller sent stderr there too; the `pre` copy is the log exactly as the
# real run-leaf.sh left it, so the last-line probe is not answered by the marker. The line
# starts with a newline because a cut-off leaf's log ends mid-line (extract-result.sh echoes
# the cut line back unterminated), and the marker must be a line of its own to be found.
cat > "$copy/run-leaf.sh" <<TRACER
#!/bin/sh
"\$(dirname "\$0")/run-leaf.real.sh" "\$@"
rc=\$?
snap="\$(mktemp -d "$trace/run-leaf.XXXXXX")"
mkdir "\$snap/pre" "\$snap/post"
pwd > "\$snap/cwd"
printf '%s\n' "\${CLAUDE_BIN:-}" > "\$snap/claude_bin"
cp .tdd/*.log "\$snap/pre/" 2>/dev/null
printf '\nrun-leaf-trace: stderr\n' >&2
cp .tdd/*.log "\$snap/post/" 2>/dev/null
exit \$rc
TRACER

# harvest-usage.sh's tracer: the leaf name and the log it is about to read, then the real one.
cat > "$copy/harvest-usage.sh" <<TRACER
#!/bin/sh
snap="\$(mktemp -d "$trace/harvest.XXXXXX")"
printf '%s\n' "\$1" > "\$snap/leaf"
cp ".tdd/\$1.log" "\$snap/log" 2>/dev/null
exec "\$(dirname "\$0")/harvest-usage.real.sh" "\$@"
TRACER
chmod +x "$copy/supervise.sh" "$copy/run-leaf.sh" "$copy/harvest-usage.sh"

# run_leaf_snap <leaf> — the first run-leaf.sh snapshot whose cwd held `.tdd/<leaf>.log`,
# or nothing.
run_leaf_snap() {
  local d
  for d in "$trace"/run-leaf.*; do
    [[ -f "$d/pre/$1.log" ]] && { printf '%s\n' "$d"; return; }
  done
}

# 1. The criterion, as one case: cases 1 and 2 of harvest-usage.test.sh launch their leaf
#    through a real run-leaf.sh with its combined output in `.tdd/<leaf>.log`, never through
#    supervise.sh, and the log the harvester reads is that one, record not last.
name="harvest-usage.test.sh cases 1 and 2 launch their leaf through run-leaf.sh directly, combined output in .tdd/<leaf>.log, never supervise.sh, and the harvester reads that log, whose result record is not its last line"
problems=()

out="$("$copy/tests/harvest-usage.test.sh" 2>/dev/null)" && code=0 || code=$?
[[ "$code" == 0 && "$out" == *'3 passed, 0 failed'* ]] ||
  problems+=("setup: want the observed suite green, got exit $code, stdout: $(printf '%q' "$out")")

if [[ -s "$trace/supervise" ]]; then
  problems+=("want supervise.sh never launched, got: $(printf '%q' "$(cat "$trace/supervise")")")
fi

for leaf in verify-refactor develop-green; do
  snap="$(run_leaf_snap "$leaf")"
  if [[ -z "$snap" ]]; then
    problems+=("$leaf: want a run-leaf.sh launch leaving .tdd/$leaf.log in its cwd, found none")
    continue
  fi
  [[ -n "$(cat "$snap/claude_bin")" ]] ||
    problems+=("$leaf: want run-leaf.sh launched against a stub CLAUDE_BIN, got none set")
  grep -q '^run-leaf-trace: stderr$' "$snap/post/$leaf.log" ||
    problems+=("$leaf: want run-leaf.sh's stderr in .tdd/$leaf.log too, not found there")
done

snap="$(run_leaf_snap verify-refactor)"
if [[ -n "$snap" ]]; then
  grep -q '"type":"result"' "$snap/pre/verify-refactor.log" ||
    problems+=("verify-refactor: want a result record in the log run-leaf.sh left, found none")
  last="$(grep -v '^[[:space:]]*$' "$snap/pre/verify-refactor.log" | tail -n 1)"
  [[ "$last" != *'"type":"result"'* ]] ||
    problems+=("verify-refactor: want the result record not to be the log's last line, it is")
  harvests=0
  for h in "$trace"/harvest.*; do
    [[ -f "$h/leaf" && "$(cat "$h/leaf")" == verify-refactor ]] || continue
    harvests=$((harvests + 1))
    cmp -s "$h/log" "$snap/post/verify-refactor.log" ||
      problems+=("verify-refactor: want every harvest to read the log run-leaf.sh wrote, one read a different file")
  done
  [[ "$harvests" -gt 0 ]] ||
    problems+=("verify-refactor: want at least one harvest of the leaf, got none")
fi

report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
