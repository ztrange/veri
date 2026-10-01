#!/usr/bin/env bash
# Unit tests for how skills/tdd/SKILL.md answers a rejected push, read as text.
#
# Contract under test:
#   1. At both `push-branch.sh` call sites — Green's tick commit and verify-refactor's clear
#      commit — exit 1 sends the run to the reconcile leaf and exit 2 bails; the reconcile
#      instructions launch `develop-reconcile` through `supervise.sh`, re-run
#      `push-branch.sh`, check the ledger's ticks and `⟂ refactor pending` marks, and bail
#      with `reconcile-failed` otherwise; "exits 0 either way" is gone.
#
# Run: scripts/tests/skill-push-reconcile.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"
skill_md="skills/tdd/SKILL.md"
skill_path="$ROOT/$skill_md"


source "$HERE/lib/harness.sh"

plain() {
  tr -d '*`' | tr '[:upper:]' '[:lower:]'
}

records() {
  awk '
    function flush() { if (rec != "") { gsub(/[[:space:]]+/, " ", rec); print rec } rec = "" }
    /^[0-9]+\. / || /^[[:space:]]*- / { flush(); rec = $0; next }
    /^[[:space:]]*$/ { flush(); next }
    rec == "" { rec = $0; next }
    { rec = rec " " $0 }
    END { flush() }' "$skill_path" | plain
}

reconcile_section() {
  awk '/^#/ { inside = (tolower($0) ~ /reconcil/); next } inside' "$skill_path" \
    | plain | tr -s '[:space:]' ' '
}

name="both push-branch.sh call sites branch exit 1 to a supervised develop-reconcile leaf and exit 2 to a bail, the reconcile re-pushes and checks the ledger or bails reconcile-failed, and exits 0 either way is gone"
problems=()
all="$(records)"
if [[ -z "$all" ]]; then
  problems+=("$skill_md has no instructions to read — nothing could be checked")
else
  for site in 'tick-ledger\.sh --refactor-pending' 'clear-refactor-pending\.sh'; do
    rec="$(head -1 < <(grep -E "push-branch\.sh" <<<"$all" | grep -E -- "$site"))"
    if [[ -z "$rec" ]]; then
      problems+=("no instruction runs push-branch.sh beside $site — the call site could not be read")
      continue
    fi
    grep -qE 'exit 1' <<<"$rec" && grep -qE 'reconcile' <<<"$rec" \
      || problems+=("the push-branch.sh call beside $site does not send exit 1 to the reconcile leaf: $rec")
    grep -qE 'exit 2' <<<"$rec" && grep -qE 'bail' <<<"$rec" \
      || problems+=("the push-branch.sh call beside $site does not bail on exit 2: $rec")
  done

  grep -qE 'supervise\.sh develop-reconcile' <<<"$all" \
    || problems+=("no instruction launches develop-reconcile through supervise.sh")

  reconcile="$(grep -E 'reconcil' <<<"$all") $(reconcile_section)"
  for want in 'push-branch\.sh' 'ledger' '⟂ refactor pending' 'reconcile-failed' 'bail'; do
    grep -qE -- "$want" <<<"$reconcile" \
      || problems+=("the reconcile instructions never mention $want")
  done

  grep -qE 'exits 0 either way' <<<"$all" \
    && problems+=("$skill_md still says push-branch.sh exits 0 either way")
fi
report "$name"

finish
