#!/usr/bin/env bash
# Unit test for how this skill's scripts and suites ask "is this text blank?". Like
# no-docs-reads.test.sh this suite has no script as its subject: its subject is an idiom, read
# off every script beside it and every suite here. Zero-dependency plain-shell asserts.
#
# Why this exists: `[[ -z "${text// /}" ]]` — delete every space, then test for empty — is the
# obvious spelling, and in bash 3.2, the bash macOS ships, the substitution's cost grows much
# faster than the text: 0.44 s on 8 kB and 3.86 s on CLAUDE.md's 17.5 kB of records, measured on
# 2026-09-18. bash 5 on the CI runner does it in linear time, so CI never showed it. Three suites
# spent ~3.8 s each on this one line, and the idiom had spread to fourteen sites in eleven suites
# (~13 s of every `make test` on the development Mac). skill-conductor-launch.test.sh had already
# stepped around it for the same reason, and nothing stopped the next suite copying it back.
#
# The replacement is a glob, `[[ "$text" != *[!\ ]* ]]` — "holds no character but a space" —
# which answers exactly what the substitution answered (a newline or a tab still counts as
# content in both) and costs one pass.
#
# Contract under test:
#   No script beside this directory and no suite in it applies `${name// /}` — a pattern
#   substitution deleting spaces — in code. A comment naming the idiom is not a use of it.
#
# Run: skills/tdd/scripts/tests/no-quadratic-blank-check.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"

pass=0 fail=0

# The idiom as an ERE: `${`, a shell name, `// /}`. This file is skipped: it names the idiom
# as data — in its case title and its advice — and uses it nowhere.
IDIOM='\$\{[A-Za-z_][A-Za-z0-9_]*// /\}'

name="no script or suite blank-checks text with \${name// /}, which is quadratic in bash 3.2"
uses=""
for file in "$HERE"/../*.sh "$HERE"/*.test.sh; do
  [[ "$(basename "$file")" == "$(basename "$0")" ]] && continue
  while IFS= read -r hit; do
    line="${hit#*:}"
    [[ "$line" =~ ^[[:space:]]*# ]] && continue
    uses="$uses $(basename "$file"):${hit%%:*}"
  done < <(grep -nE "$IDIOM" "$file")
done
if [[ -z "$uses" ]]; then
  pass=$((pass + 1))
else
  fail=$((fail + 1))
  echo "FAIL - $name"
  echo "    spelled at:$uses — use [[ \"\$x\" != *[!\\ ]* ]] (blank) or [[ \"\$x\" == *[!\\ ]* ]] (not blank)"
fi

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
