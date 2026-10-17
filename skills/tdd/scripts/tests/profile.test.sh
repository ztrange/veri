#!/usr/bin/env bash
# Unit tests for scripts/profile.sh — what `make profile` runs: every suite it is given,
# under `bash -x` with PS4='+${EPOCHREALTIME} ${LINENO} ', cut into cases at each
# top-level increment of `pass` or `fail`, and a report of the slowest cases.
#
# Contract under test:
#   profile.sh <suite>...  → one line `<secs> <suite> case <n> L<a>-<b>` per case at or
#                            above VERI_PROFILE_THRESHOLD (seconds, default 1), slowest
#                            first; exit 0 whether or not any case crossed.
#   make -n profile          → names every suite `make -n test` names, under the offline
#                              environment test's recipe gives them.
#
# Run: scripts/tests/profile.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/lib/harness.sh"
PROFILE="$HERE/../profile.sh"

scratch="$(scratch_dir)"

write_fixture() {
  fixture="$scratch/$1"
  cat > "$fixture"
  chmod +x "$fixture"
}

expect_line() {
  local rest="$1" want="$2"
  if [[ "$out" =~ ^([0-9]+(\.[0-9]+)?)\ (.*)$ && "${BASH_REMATCH[3]}" == "$rest" ]]; then
    awk -v s="${BASH_REMATCH[1]}" -v w="$want" 'BEGIN { exit !(s + 0 == w + 0) }' ||
      problems+=("want secs equal to $want, got $(printf '%q' "$out")")
  else
    problems+=("want exactly '<secs> $rest', got: $(printf '%q' "$out")")
  fi
}


finish
