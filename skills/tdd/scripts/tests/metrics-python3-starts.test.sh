#!/usr/bin/env bash
# Unit tests for metrics.test.sh itself — how many python3 processes a run of it starts
# (issue #331). Like harvest-usage-launch.test.sh this suite's subject is another suite.
# Zero-dependency plain-shell asserts, same idiom as harvest-usage-launch.test.sh.
#
# metrics.test.sh probes each rendered report with python programs that share one prelude
# (`$PROBE_PRELUDE`). Started once per assertion, that prelude is compiled once per
# assertion; started once per case, once per case. The count is the observable, not a timer.
#
# Contract under test, observed by running metrics.test.sh against a copy of the scripts
# with a PATH-first `python3` that appends one line to a counter file before exec'ing the
# real interpreter:
#   metrics.test.sh → green, 21 cases, and at most 21 python3 starts of its own across the
#                     whole run.
#
# "Of its own": metrics.sh, the product script every case renders through, execs python3 once
# per call, and those forks are not the suite's to fold — the issue sets them apart. So in the
# copy metrics.sh is a wrapper that puts the original PATH back before exec'ing the real one,
# and only the starts the suite itself makes reach the counter.
#
# Run: scripts/tests/metrics-python3-starts.test.sh
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

# The copy: every top-level script and the sourced library, so metrics.test.sh's own `$HERE`
# still finds metrics.sh, plus the one suite under observation.
copy="$tmp/scripts"
mkdir -p "$copy/tests" "$copy/bin"
cp "$SCRIPTS"/*.sh "$copy/"
cp -R "$SCRIPTS/lib" "$copy/lib"
cp "$HERE/metrics.test.sh" "$copy/tests/"

real_python3="$(command -v python3)"
starts_log="$tmp/python3-starts"
: > "$starts_log"
cat > "$copy/bin/python3" <<SHIM
#!/bin/sh
printf 'python3\n' >> "$starts_log"
exec "$real_python3" "\$@"
SHIM
chmod +x "$copy/bin/python3"

mv "$copy/metrics.sh" "$copy/metrics.real.sh"
cat > "$copy/metrics.sh" <<WRAPPER
#!/bin/sh
PATH='$PATH' exec "\$(dirname "\$0")/metrics.real.sh" "\$@"
WRAPPER
chmod +x "$copy/metrics.sh"

# 1. The criterion: a whole run of metrics.test.sh starts python3 at most 21 times of its own —
#    one per case — with the suite still green on all 21 of its cases.
#      → the observed suite `21 passed, 0 failed`, and at most 21 lines in the counter.
name="metrics.test.sh's total python3 starts, counted by a PATH-first counting shim, are at most 21 — one per case"
problems=()

out="$(PATH="$copy/bin:$PATH" "$copy/tests/metrics.test.sh" 2>/dev/null)"
[[ "$out" == *'21 passed, 0 failed'* ]] ||
  problems+=("setup: want the observed suite green on its 21 cases, got: $(printf '%q' "$out")")
starts="$(wc -l < "$starts_log" | tr -d ' ')"
[[ "$starts" -gt 0 ]] ||
  problems+=("setup: want the counting shim to see python3 started at all, got 0")
[[ "$starts" -le 21 ]] ||
  problems+=("want at most 21 python3 starts across metrics.test.sh, got $starts")

report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
