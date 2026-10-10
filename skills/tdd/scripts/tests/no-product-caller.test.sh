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

others="$work/other-callers"
new_repo -b main "$others" >/dev/null 2>&1
mkdir -p "$others/skills/tdd/scripts/veri" "$others/skills/tdd-fix" "$others/skills/tdd-candidates" "$others/docs/hooks"
printf '# tdd\n' > "$others/skills/tdd/SKILL.md"
printf '# tdd-fix\n\n    scripts/old-thing.sh\n' > "$others/skills/tdd-fix/SKILL.md"
printf '# tdd-candidates\nscripts/old-thing.sh\n' > "$others/skills/tdd-candidates/SKILL.md"
printf 'test:\n\t@true\nold:\n\tscripts/old-thing.sh\n' > "$others/Makefile"
printf '#!/bin/sh\nscripts/old-thing.sh "$@"\n' > "$others/docs/hooks/reference-transaction"
printf 'import sys\n\n\nCALL = "old-thing.sh"\n' > "$others/skills/tdd/scripts/veri/caller.py"
git -C "$others" add -A >/dev/null 2>&1
git -C "$others" commit -q -m "feat: callers" >/dev/null 2>&1
others_out="$(cd "$others" && "$CHECK" old-thing.sh 2>&1)"; others_code=$?
if [[ "$others_code" == 1 \
  && "$others_out" == *"skills/tdd-fix/SKILL.md:3"* \
  && "$others_out" == *"skills/tdd-candidates/SKILL.md:2"* \
  && "$others_out" == *"Makefile:4"* \
  && "$others_out" == *"docs/hooks/reference-transaction:2"* \
  && "$others_out" == *"skills/tdd/scripts/veri/caller.py:4"* ]]; then ok; else
  no "no-product-caller: a line naming <name>.sh in the other product files → exit 1 printing each file:line (code=$others_code out=$others_out)"
fi

binary="$work/binary-caller"
new_repo -b main "$binary" >/dev/null 2>&1
mkdir -p "$binary/skills/tdd/scripts/veri/__pycache__"
printf '# tdd\n' > "$binary/skills/tdd/SKILL.md"
printf '\377\376\nold-thing.sh\n' > "$binary/skills/tdd/scripts/veri/__pycache__/caller.cpython-312.pyc"
binary_out="$(cd "$binary" && "$CHECK" old-thing.sh 2>&1)"; binary_code=$?
if [[ "$binary_code" == 1 && "$binary_out" == *"skills/tdd/scripts/veri/__pycache__/caller.cpython-312.pyc:2"* ]]; then ok; else
  no "no-product-caller: a non-UTF-8 file under veri/ naming <name>.sh → exit 1 printing its file:line (code=$binary_code out=$binary_out)"
fi

finish
