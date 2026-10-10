#!/usr/bin/env bash
# Audits SKILL.md's script reference against each script's own usage line: for every
# `- `$S/<script> …`` entry, each `--` flag the script's first `# usage:` line names must
# appear in the entry's synopsis, the backticked text after `$S/`. Names the script and
# the flag when one does not. Likewise each verb — a literal subcommand word, or one
# alternative of an `a|b|c` choice — on any line of the usage block that invokes the script.
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

synopses() { grep -E '^ *- `\$S/' "$SKILL" | sed -E 's/^ *- `\$S\/([^`]*).*/\1/'; }
flags_of() { grep -oE -e '--[a-z][a-z0-9-]*' <<< "$1" | sort -u; }
usage_block() {
  awk 'found && (/^#[[:space:]]*$/ || !/^#/) { exit }
       tolower($0) ~ /^# *usage:/ { found = 1 }
       found { print }' "$1"
}

flag_problems() {
  local synopsis script usage entry_flags flag
  while IFS= read -r synopsis; do
    script="${synopsis%% *}"
    [[ -f "$SCRIPTS/$script" ]] || continue
    usage="$(usage_block "$SCRIPTS/$script")"
    entry_flags="$(flags_of "$synopsis")"
    while IFS= read -r flag; do
      [[ -z "$flag" ]] && continue
      grep -xF -e "$flag" <<< "$entry_flags" > /dev/null ||
        printf '    %s\n' "$script: $flag is in its usage line, not in SKILL.md's entry"
    done <<< "$(flags_of "$usage")"
  done <<< "$(synopses)"
}

problems="$(flag_problems)"
[[ -n "$problems" ]] && problems+=$'\n'
verdict "every --flag a script's usage line names is in its SKILL.md script-reference synopsis (#1432)"

scratch="$(scratch_dir)"
mkdir -p "$scratch/skill/scripts"
cat > "$scratch/skill/scripts/exp-two-line.sh" <<'STUB'
#!/bin/sh
# usage: exp-two-line.sh <n>
#        exp-two-line.sh --drop <n>
STUB
printf '%s\n' '- `$S/exp-two-line.sh <n>` — a fixture entry.' > "$scratch/skill/SKILL.md"
planted="$(SCRIPTS="$scratch/skill/scripts" SKILL="$scratch/skill/SKILL.md"; flag_problems)"
want="    exp-two-line.sh: --drop is in its usage line, not in SKILL.md's entry"
problems=""
grep -xF -e "$want" <<< "$planted" > /dev/null ||
  problems+="    want the line '$want', got: $(printf '%q' "$planted")"$'\n'
verdict "#1432: a --flag only on a later line of a script's usage block, missing from its SKILL.md entry, is named with its script"

usage_invocations() {
  local script="$1" line
  while IFS= read -r line; do
    [[ "$line" == "$script" || "$line" == "$script "* ]] && printf '%s\n' "$line"
  done <<< "$(usage_block "$SCRIPTS/$script" |
              sed -E -e 's/^# *([Uu]sage:)? *//' -e 's/^([A-Z_]+=[^ ]* +)*//')"
}
verbs_of() {
  sed -E -e "s/<[^>]*>//g" -e "s/'[^']*'//g" -e 's/"[^"]*"//g' -e 's/ #.*//' \
         -e 's/\([^)]*\)//g' -e 's/\[[^]|-][^]|]*\]//g' -e 's/[][]/ /g' <<< "${1#* }" |
    tr -s ' ' '\n' | grep -vE '^-' | tr '|' '\n' | grep -xE '[a-z][a-z0-9-]*' | sort -u
}

problems=""
while IFS= read -r synopsis; do
  script="${synopsis%% *}"
  [[ -f "$SCRIPTS/$script" ]] || continue
  entry_words="$(grep -oE '[a-z][a-z0-9-]*' <<< "$synopsis" | sort -u)"
  while IFS= read -r verb; do
    [[ -z "$verb" ]] && continue
    grep -xF -e "$verb" <<< "$entry_words" > /dev/null ||
      problems+="    $script: $verb is a verb in its usage line, not in SKILL.md's entry"$'\n'
  done <<< "$(while IFS= read -r line; do
                [[ -n "$line" ]] && verbs_of "$line"
              done <<< "$(usage_invocations "$script")" | sort -u)"
done <<< "$(synopses)"
verdict "every verb a script's usage line names is in its SKILL.md script-reference synopsis (#1432)"

finish
