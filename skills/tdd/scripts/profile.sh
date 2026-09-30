#!/usr/bin/env bash
# profile.sh — say which of a suite's cases are the slow ones, measured rather than guessed.
#
# Sources each suite given into a `bash -c` that sets PS4 and `set -x` itself — bash run as
# uid 0 takes no PS4 from its environment — its trace sent to a file nothing else reads, every
# trace line stamped by PS4 with ${EPOCHREALTIME} (no subprocess, unlike `date +%s.%N`) and
# ${LINENO}. A case ends at each top-level assignment that raises `pass` or `fail` above its
# previous value — the two counters every suite in this tree keeps — so a case's cost is
# the trace time from the previous such boundary (or the suite's first stamp) to its own.
#
# Prints one line `<secs> <suite> case <n> L<a>-<b>` per case whose cost is at or above
# VERI_PROFILE_THRESHOLD (seconds, default 1), slowest first. Exit 0 whether or not any
# case crossed it. Exit 2 when no answer could be obtained: a threshold that is not a
# number of seconds, or a suite whose trace never raises `pass` or `fail`.
#
# Usage:   profile.sh <suite>...
set -euo pipefail

threshold="${VERI_PROFILE_THRESHOLD:-1}"
if [[ ! "$threshold" =~ ^[0-9]+(\.[0-9]+)?$ ]]; then
  echo "profile.sh: VERI_PROFILE_THRESHOLD must be a number of seconds, got '$threshold'" >&2
  exit 2
fi

trace="$(mktemp)"
trap 'rm -f "$trace"' EXIT

for suite in "$@"; do
  BASH_XTRACEFD=9 bash -c 'PS4='\''+${EPOCHREALTIME} ${LINENO} '\''; set -x; . "$0"' \
    "$suite" 9>"$trace" >/dev/null 2>&1 < /dev/null || true
  awk -v suite="$suite" -v threshold="$threshold" '
    /^\+\+[^+]/ {
      stamp = substr($1, 3)
      if (stamp != "" && start == "") start = stamp
      lineno = $2
      cmd = $3
      if (first == "") first = lineno
      if (NF == 3 && cmd ~ /^(pass|fail)=[0-9]+$/) {
        split(cmd, kv, "=")
        if (kv[2] + 0 > seen[kv[1]] + 0) {
          n++
          secs = stamp - start
          if (secs >= threshold + 0)
            printf "%.6f %s case %d L%d-%d\n", secs, suite, n, first, lineno
          start = stamp
          first = ""
        }
        seen[kv[1]] = kv[2]
      }
    }
    END {
      if (n == 0) {
        print "profile.sh: " suite ": no pass=/fail= increment in its trace" > "/dev/stderr"
        exit 2
      }
    }
  ' "$trace"
done | sort -rn
