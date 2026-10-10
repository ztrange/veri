#!/usr/bin/env bash
# Audits SKILL.md's script reference against each script's own usage line: for every
# `- `$S/<script> …`` entry, each `--` flag the script's first `# usage:` line names must
# appear in the entry's synopsis, the backticked text after `$S/`. Names the script and
# the flag when one does not.
# Fast tier by its own usage count: git 0, python3 0, server 0, sleep 0.
#
# Run: scripts/tests/unit/skill-reference-usage.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
SCRIPTS="$(cd "$HERE/../.." && pwd)"
SKILL="$SCRIPTS/../SKILL.md"
source "$HERE/../lib/harness.sh"
source "$HERE/../lib/verdict.sh"
export LC_ALL=C

flags_of() { grep -oE -e '--[a-z][a-z0-9-]*' <<< "$1" | sort -u; }

problems=""
while IFS= read -r synopsis; do
  script="${synopsis%% *}"
  [[ -f "$SCRIPTS/$script" ]] || continue
  usage="$(grep -m1 -iE '^# *usage:' "$SCRIPTS/$script")"
  entry_flags="$(flags_of "$synopsis")"
  while IFS= read -r flag; do
    [[ -z "$flag" ]] && continue
    grep -xF -e "$flag" <<< "$entry_flags" > /dev/null ||
      problems+="    $script: $flag is in its usage line, not in SKILL.md's entry"$'\n'
  done <<< "$(flags_of "$usage")"
done <<< "$(grep -E '^ *- `\$S/' "$SKILL" | sed -E 's/^ *- `\$S\/([^`]*).*/\1/')"
verdict "every --flag a script's usage line names is in its SKILL.md script-reference synopsis (#1432)"

finish
