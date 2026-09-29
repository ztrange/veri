#!/usr/bin/env bash
# Audits where the pending mark is spelled: of every `.sh` and `.py` file under
# skills/tdd/scripts/ outside tests/, only lib/ledger.sh may carry ` ⟂ refactor pending`,
# code and comments alike. Names each other file that does.
#
# Admitted to the fast tier by its own usage count: git 0, python3 0, server 0, sleep 0.
#
# Run: scripts/tests/unit/pending-mark-literal.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
SCRIPTS="$(cd "$HERE/../.." && pwd)"
pass=0 fail=0
export LC_ALL=C

verdict() {
  if [[ -z "$problems" ]]; then
    pass=$((pass + 1))
  else
    fail=$((fail + 1)); echo "FAIL - $1"
    printf '%s' "$problems"
  fi
}

mark=' ⟂ refactor pending'

# 1. the mark is spelled in lib/ledger.sh and in no other script or module.
problems=""
carriers="$(cd "$SCRIPTS" && grep -rlF --include='*.sh' --include='*.py' -e "$mark" . \
  | sed 's|^\./||' | awk '$0 !~ /^tests\// && $0 != "lib/ledger.sh"' | sort)"
while IFS= read -r file; do
  [[ -n "$file" ]] && problems+="    $file carries the pending mark"$'\n'
done <<< "$carriers"
if ! grep -F -e "$mark" "$SCRIPTS/lib/ledger.sh" > /dev/null; then
  problems+="    lib/ledger.sh does not carry the pending mark"$'\n'
fi
verdict "the pending mark is spelled in lib/ledger.sh only"

echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
