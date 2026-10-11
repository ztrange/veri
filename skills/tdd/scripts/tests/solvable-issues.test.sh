#!/usr/bin/env bash
# Unit tests for scripts/solvable-issues.sh — the selection layer. Given a repo's issues
# and open PRs, print the numbers of the issues veri may take right now, one per line, and
# exit 0; print nothing and exit 3 when there are none.
#
# Contract under test:
#   solvable-issues.sh [--repo owner/name]
#   VERI_GH_JSON=<dir>   read <dir>/issues.json and <dir>/prs.json instead of shelling out
#                        to gh, in the shape of
#                          gh issue list --json number,title,labels,body,state
#                          gh pr list    --json body,state
#   VERI_LABEL=<name>    the opt-in label to select on, default `ready-for-agent`. Set but
#                        empty is exit 2.
#
# Run: scripts/tests/solvable-issues.test.sh
set -uo pipefail
unset VERI_GH_DRIVER

HERE="$(cd "$(dirname "$0")" && pwd)"
SOLVABLE="$HERE/../solvable-issues.sh"
REPO_ROOT="$(cd "$HERE/../../../.." && pwd)"
source "$HERE/lib/harness.sh"
work="$(scratch_dir)"

no_claims="$work/no-claims"
new_repo -b main "$no_claims" >/dev/null 2>&1
cd "$no_claims" || exit 2

fixture() {  # fixture <name> -> path
  local dir="$work/$1"
  mkdir -p "$dir"
  printf '[]\n' > "$dir/prs.json"
  echo "$dir"
}

run() {  # run <fixture-dir> [script args…]; sets $out and $code
  local fixture="$1"; shift
  out="$(cd "$no_claims" && VERI_GH_JSON="$fixture" "$SOLVABLE" "$@" 2>/dev/null)" && code=0 || code=$?
}

label_run() {  # label_run <fixture-dir> <env setting…>; sets $out and $code
  local fixture="$1"; shift
  out="$(cd "$no_claims" && env "$@" VERI_GH_JSON="$fixture" "$SOLVABLE" 2>/dev/null)" && code=0 || code=$?
}

refused_run() {  # refused_run <fixture-dir> <env setting…>; sets $refused_out/$refused_err/$refused_code
  local fixture="$1"; shift
  refused_out="$fixture/refused.out" refused_err="$fixture/refused.err"
  env "$@" VERI_GH_JSON="$fixture" "$SOLVABLE" >"$refused_out" 2>"$refused_err" \
    && refused_code=0 || refused_code=$?
}

finish
