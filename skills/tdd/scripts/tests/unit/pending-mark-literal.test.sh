#!/usr/bin/env bash
# Audits where the pending mark is spelled: of every `.sh` and `.py` file under
# skills/tdd/scripts/ outside tests/, only lib/ledger.sh may carry ` ⟂ refactor pending`,
# code and comments alike. Names each other file that does. And audits where the step-line
# pattern is spelled: lib/ledger.sh carries a box on one non-comment line, the one definition
# its readers and writers share. Names each line that does when more than one does. And audits
# that no other script or module (non-comment lines) and no line of SKILL.md spells a box —
# an escaped `\[` box or a `'[x]'` / `"- [x] "` / `"- [ ] "` literal. Names each file and line.
# Fast tier by its own usage count: git 0, python3 0, server 0, sleep 0.
#
# Run: scripts/tests/unit/pending-mark-literal.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
SCRIPTS="$(cd "$HERE/../.." && pwd)"
source "$HERE/../lib/harness.sh"
export LC_ALL=C

verdict() {
  if [[ -z "$problems" ]]; then
    ok
  else
    no "$1"
    printf '%s' "$problems"
  fi
}

mark=' ⟂ refactor pending'

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

problems=""
spellers="$(grep -nF -e '\[' -e '[x]' -e '[X]' -e '[ ]' "$SCRIPTS/lib/ledger.sh" \
  | grep -vE '^[0-9]+:[[:space:]]*#')"
count=0
[[ -n "$spellers" ]] && count="$(wc -l <<< "$spellers" | tr -d ' ')"
if [[ "$count" -ne 1 ]]; then
  problems+="    lib/ledger.sh spells a box on $count lines, expected 1:"$'\n'
  while IFS= read -r hit; do
    [[ -n "$hit" ]] && problems+="      lib/ledger.sh:$hit"$'\n'
  done <<< "$spellers"
fi
verdict "the step-line pattern is spelled on one line of lib/ledger.sh"

problems=""
box=(-e '\\\[\(?([ xX]|\[[^]]*\])\)?\\\]' -e "'\[x\]'" -e '"- \[[ x]\] "')
spellers="$( (cd "$SCRIPTS" && grep -rnE --include='*.sh' --include='*.py' "${box[@]}" .) \
  | sed 's|^\./||' | awk '$0 !~ /^tests\// && $0 !~ /^lib\/ledger\.sh:/' \
  | grep -vE '^[^:]+:[0-9]+:[[:space:]]*#')"
while IFS= read -r hit; do
  [[ -n "$hit" ]] && problems+="    ${hit%%:*}:$(cut -d: -f2 <<< "$hit") spells a box"$'\n'
done <<< "$spellers"
spellers="$(grep -nE "${box[@]}" "$SCRIPTS/../SKILL.md")"
while IFS= read -r hit; do
  [[ -n "$hit" ]] && problems+="    SKILL.md:${hit%%:*} spells a box"$'\n'
done <<< "$spellers"
verdict "no script or module but lib/ledger.sh, and no line of SKILL.md, spells a box"

finish
