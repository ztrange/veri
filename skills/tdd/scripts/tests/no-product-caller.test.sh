#!/usr/bin/env bash
# Unit tests for scripts/no-product-caller.sh — answers whether a product caller of an old
# interface remains.
#
# Contract under test:
#   no-product-caller.sh <name>.sh, run inside the repository
#       → exit 1, printing file:line for each line of a product file that names it
#
# Run: scripts/tests/no-product-caller.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
CHECK="$HERE/../no-product-caller.sh"
source "$HERE/lib/harness.sh"

work="$(scratch_dir)"

repo="$work/callers"
new_repo -b main "$repo" >/dev/null 2>&1
mkdir -p "$repo/skills/tdd"
printf '# tdd\n\nRun:\n\n    scripts/old-thing.sh <base-sha>\n' > "$repo/skills/tdd/SKILL.md"
git -C "$repo" add -A >/dev/null 2>&1
git -C "$repo" commit -q -m "feat: skill" >/dev/null 2>&1
skill_out="$(cd "$repo" && "$CHECK" old-thing.sh 2>&1)"; skill_code=$?
if [[ "$skill_code" == 1 && "$skill_out" == *"skills/tdd/SKILL.md:5"* ]]; then ok; else
  no "no-product-caller: a skills/tdd/SKILL.md line names <name>.sh → exit 1 printing skills/tdd/SKILL.md:5 (code=$skill_code out=$skill_out)"
fi

finish
