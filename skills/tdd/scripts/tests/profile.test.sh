#!/usr/bin/env bash
# Unit tests for scripts/profile.sh — what `make profile` runs: every suite it is given,
# under `bash -x` with PS4='+${EPOCHREALTIME} ${LINENO} ', cut into cases at each
# top-level increment of `pass` or `fail`, and a report of the cases whose trace time is
# at or above VERI_PROFILE_THRESHOLD (seconds, default 1), slowest first.
# Zero-dependency plain-shell asserts, same idiom as refactor-budget.test.sh.
#
# Contract under test (issue #329):
#   profile.sh <suite>...  → one line `<secs> <suite> case <n> L<a>-<b>` per case at or
#                            above the threshold; exit 0 whether or not any case crossed.
#
# No case here waits on a clock. A fixture suite fabricates its own timestamps: bash stops
# treating EPOCHREALTIME as special once it is unset, so after `unset EPOCHREALTIME` an
# ordinary assignment to it is what the next trace line's PS4 expands to. The one trace
# line a fixture cannot fabricate is its first — the `unset` itself, stamped with the real
# clock — so a fixture's case 1 runs from that real stamp to a fabricated one and comes
# out hugely negative; the cases a probe measures are the ones after it.
#
# Run: scripts/tests/profile.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
PROFILE="$HERE/../profile.sh"
pass=0 fail=0

scratch="$(mktemp -d)"
trap 'rm -rf "$scratch"' EXIT

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

# 1. a fixture whose case 2 spans 2.5 fabricated seconds and whose case 3 spans 0.25,
#    profiled at a threshold of 1: the report is one line, and it is case 2's. Case 1 is
#    the fixture's anchor (see the header) and must not be printed either.
name="threshold 1: the 2.5 s case is printed, the 0.25 s case is not"
problems=()
fixture="$scratch/two-cases.test.sh"
cat > "$fixture" <<'EOF'
unset EPOCHREALTIME
pass=0 fail=0
EPOCHREALTIME=100.000000
pass=$((pass + 1))
EPOCHREALTIME=102.500000
pass=$((pass + 1))
EPOCHREALTIME=102.750000
pass=$((pass + 1))
echo "$pass passed, $fail failed"
EOF
chmod +x "$fixture"
out="$(VERI_PROFILE_THRESHOLD=1 "$PROFILE" "$fixture" 2>/dev/null)" && code=0 || code=$?
[[ "$code" == 0 ]] || problems+=("want exit 0, got $code")
lines=()
[[ -z "$out" ]] || mapfile -t lines <<< "$out"
[[ "${#lines[@]}" -eq 1 && "${lines[0]}" == *" case 2 "* ]] ||
  problems+=("want exactly one line, naming case 2, got: $(printf '%q' "$out")")
[[ "$out" != *" case 3 "* ]] || problems+=("case 3 (0.25 s) was printed: $(printf '%q' "$out")")
report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
