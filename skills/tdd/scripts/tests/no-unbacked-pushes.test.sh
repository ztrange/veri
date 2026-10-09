#!/usr/bin/env bash
# Unit test: every suite under skills/tdd/scripts/tests/ that invokes push-branch.sh sets
# VERI_PUSH_BACKOFF on that invocation, so no suite waits out the default backoff on wall time.
#
# Contract under test:
#   An invocation of push-branch.sh — by path, or through a variable assigned that path — with
#   no VERI_PUSH_BACKOFF= on the same command is reported as `<suite>:<line>`. An exemption
#   carries a reason. This suite dies under C7, once the last suite invoking push-branch.sh
#   is pytest.
#
# Run: skills/tdd/scripts/tests/no-unbacked-pushes.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"

source "$HERE/lib/harness.sh"

declare -A EXEMPT=(
  [push-backoff-guard.test.sh]="its push-branch.sh lines are the text of the suites it plants in a scratch tree, written with echo, not invocations"
)

name="every suite that invokes push-branch.sh sets VERI_PUSH_BACKOFF in its environment"
problems=()
push_invocations=0
for suite in "$HERE"/*.test.sh; do
  [[ -n "${EXEMPT[$(basename "$suite")]+x}" ]] && continue
  while IFS= read -r row; do
    case "$row" in
      invoked) push_invocations=$((push_invocations + 1)) ;;
      *) problems+=("$(basename "$suite"):$row invokes push-branch.sh without VERI_PUSH_BACKOFF in its environment, so a push to an unreachable origin waits the default backoff on wall time") ;;
    esac
  done < <(awk '
    BEGIN { assigns_script = "^[[:space:]]*(local[[:space:]]+)?[A-Za-z_][A-Za-z0-9_]*=.*/push-branch\\.sh[\"'"'"']?[[:space:]]*$" }
    NR == FNR {
      if ($0 ~ assigns_script) {
        v = $0
        sub(/^[[:space:]]*(local[[:space:]]+)?/, "", v)
        sub(/=.*/, "", v)
        vars[v] = 1
      }
      next
    }
    {
      if (!joining) start = FNR
      if ($0 ~ /\\$/) { cmd = cmd substr($0, 1, length($0) - 1) " "; joining = 1; next }
      cmd = cmd $0; joining = 0
      line = cmd; cmd = ""
      if (line ~ /^[[:space:]]*#/) next
      if (line ~ assigns_script) next
      invokes = (line ~ /\/push-branch\.sh"/)
      for (v in vars)
        if (index(line, "\"$" v "\"") || index(line, "${" v "}")) invokes = 1
      if (!invokes) next
      print "invoked"
      if (line !~ /VERI_PUSH_BACKOFF=/) print start
    }
  ' "$suite" "$suite")
done
[[ "$push_invocations" -gt 0 ]] ||
  problems+=("no suite here was recognised as invoking push-branch.sh, so nothing was checked")
report "$name"

finish
