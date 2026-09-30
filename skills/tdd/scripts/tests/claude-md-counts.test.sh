#!/usr/bin/env bash
# Unit test for the sizes CLAUDE.md states for this skill — like hermetic-suites.test.sh
# and skill-identity.test.sh this suite belongs to no single script: its subject is the
# inventory of `skills/tdd/scripts/` and the two sentences that count it. Zero-dependency
# plain-shell asserts, same idiom, picked up by `make test`'s glob by existing.
#
# Why this exists (issue #161): CLAUDE.md is the first thing an agent reads, and it counts
# the tree twice — once in the opening paragraph ("plus <n> bash scripts it calls") and
# once in *Testing idiom* ("<n> files for <m> scripts"). Both numbers were written by hand
# and neither has anything to hold it to the directory it describes, so every issue that
# adds a script — this one adds `detach-leaf.sh` — leaves them one further behind. A count
# that is wrong is worse than no count: an agent told there are eighteen scripts has been
# given a number it can act on, and the twenty-five on disk mean it was told the tree is
# smaller than it is before it has opened a single file.
#
# Contract under test — every count CLAUDE.md states is the number of files on disk:
#   1. The opening paragraph's script count is `skills/tdd/scripts/*.sh`.
#   2. *Testing idiom*'s suite count is `skills/tdd/scripts/tests/*.test.sh`, and the
#      script count in the same sentence is `skills/tdd/scripts/*.sh` again.
#
# One criterion — the stated counts match the files — and so one case: three numbers, but
# a document whose intro and testing section disagreed about how many scripts there are
# would be exactly as wrong as one whose single number was stale, and a reader repairing
# either repairs them the same way. The case reports one problem per number so the output
# says which of the three is off and by what.
#
# A count is accepted in either spelling a sentence like these uses: the digits, or the
# English words CLAUDE.md currently writes them in. Which one the author reaches for is
# not this suite's business — that the number is right is.
#
# Run: scripts/tests/claude-md-counts.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"

claude_md="CLAUDE.md"
claude_path="$ROOT/$claude_md"

scripts_glob="skills/tdd/scripts/*.sh"
scripts_path="$ROOT/$scripts_glob"
suites_glob="skills/tdd/scripts/tests/*.test.sh"
suites_path="$ROOT/$suites_glob"
unit_glob="skills/tdd/scripts/tests/unit/*.test.sh"
unit_path="$ROOT/$unit_glob"

section_name="Testing idiom"

pass=0 fail=0

source "$HERE/lib/harness.sh"

unreadable() {
  problems+=("$1 — $2 could not be read")
}

readable() {
  if [[ -n "${1// /}" ]]; then return 0; fi
  unreadable "$2" "$3"
  return 1
}

nonempty() {
  if [[ "$2" -eq 0 ]]; then
    unreadable "no $1 matched $3" "the tree the counts describe"
  fi
}

how_many() {
  local f n=0
  for f in $1; do
    if [[ -f "$f" ]]; then n=$((n + 1)); fi
  done
  printf '%s' "$n"
}

ONES=(zero one two three four five six seven eight nine ten eleven twelve thirteen
      fourteen fifteen sixteen seventeen eighteen nineteen)
TENS=(twenty thirty forty fifty sixty seventy eighty ninety)

in_words() {
  local n="$1" t u
  if [[ "$n" -lt 20 ]]; then printf '%s' "${ONES[$n]}"; return; fi
  if [[ "$n" -ge 100 ]]; then return; fi
  t=$((n / 10 - 2))
  u=$((n % 10))
  if [[ "$u" -eq 0 ]]; then
    printf '%s' "${TENS[$t]}"
  else
    printf '%s-%s' "${TENS[$t]}" "${ONES[$u]}"
  fi
}

preamble() { awk '/^## / { exit } { print }' "$claude_path"; }

section() {
  awk -v want="$1" '/^## / { insec = (index($0, "## " want) == 1) } insec' "$claude_path"
}

flatten() { tr '\n' ' '; }

NUM='([0-9]+|[A-Za-z-]+)'

BEFORE='[^0-9A-Za-z-]'

intro_claim=".*$BEFORE$NUM bash scripts.*"
idiom_claim=".*$BEFORE$NUM files for $NUM scripts.*"
unit_claim=".*${BEFORE}plus $NUM [A-Za-z ]*under .unit..*"

claimed() {
  head -1 < <(sed -nE "s/$2/\\$3/p" <<< "$1")
}

check() {
  local what="$1" claimed="$2" n="$3" words
  if [[ -z "$claimed" ]]; then
    unreadable "$claude_md states no $what" "the sentence that counts them"
    return
  fi
  claimed="$(tr '[:upper:]' '[:lower:]' <<< "$claimed")"
  words="$(in_words "$n")"
  if [[ "$claimed" != "$n" ]] && [[ -z "$words" || "$claimed" != "$words" ]]; then
    problems+=("$claude_md says the $what is '$claimed'; there are $n on disk")
  fi
}

present() {
  if [[ ! -f "$ROOT/$1" ]]; then
    problems+=("$1 is not in the tree whose count $claude_md states")
  fi
}

moved_by() {
  local what="$1" claimed="$2" n="$3" words
  shift 3
  local before="$(( n - $# ))" added
  if [[ "$#" -eq 1 ]]; then
    added="$1"
  else
    added="$(printf '%s, ' "${@:1:$#-1}")"
    added="${added%, } and ${!#}"
  fi
  if [[ -z "$claimed" ]]; then
    unreadable "$claude_md states no $what" "the sentence that counts them"
    return
  fi
  claimed="$(tr '[:upper:]' '[:lower:]' <<< "$claimed")"
  words="$(in_words "$before")"
  if [[ "$claimed" == "$before" ]] || [[ -n "$words" && "$claimed" == "$words" ]]; then
    problems+=("$claude_md says the $what is '$claimed' — the count of the tree without $added")
  fi
}

moved_with() {
  local script="$1" suite="$2"
  present "$script"
  present "$suite"
  if [[ "${#problems[@]}" -ne 0 ]]; then return 1; fi
  if readable "$intro" "$claude_md has no prose above its first '## ' heading" "the opening paragraph's script count"; then
    moved_by "opening paragraph's script count" "$(claimed "$intro" "$intro_claim" 1)" "$n_scripts" "$script"
  fi
  if readable "$idiom" "$claude_md has no '## $section_name' section" "the suite and script counts it states"; then
    moved_by "*$section_name* suite count" "$(claimed "$idiom" "$idiom_claim" 1)" "$n_suites" "$suite"
    moved_by "*$section_name* script count" "$(claimed "$idiom" "$idiom_claim" 2)" "$n_scripts" "$script"
  fi
}

name="$claude_md's stated script and suite counts match the scripts and suites on disk"
problems=()

n_scripts="$(how_many "$scripts_path")"
n_suites="$(how_many "$suites_path")"

nonempty script "$n_scripts" "$scripts_glob"
nonempty suite "$n_suites" "$suites_glob"

intro="$(preamble | flatten)"
idiom="$(section "$section_name" | flatten)"

if readable "$intro" "$claude_md has no prose above its first '## ' heading" "the opening paragraph's script count"; then
  check "opening paragraph's script count" "$(claimed "$intro" "$intro_claim" 1)" "$n_scripts"
fi

if readable "$idiom" "$claude_md has no '## $section_name' section" "the suite and script counts it states"; then
  check "*$section_name* suite count" "$(claimed "$idiom" "$idiom_claim" 1)" "$n_suites"
  check "*$section_name* script count" "$(claimed "$idiom" "$idiom_claim" 2)" "$n_scripts"
fi

report "$name"

name="$claude_md's counts moved with refactor-triage.sh and its suite"
problems=()

moved_with "skills/tdd/scripts/refactor-triage.sh" "skills/tdd/scripts/tests/refactor-triage.test.sh"

report "$name"

name="$claude_md's counts moved with run-conductor.sh and its suites"
problems=()

conductor_script="skills/tdd/scripts/run-conductor.sh"
conductor_suites=(
  "skills/tdd/scripts/tests/run-conductor.test.sh"
  "skills/tdd/scripts/tests/skill-conductor-launch.test.sh"
)

present "$conductor_script"
for suite in "${conductor_suites[@]}"; do present "$suite"; done

if [[ "${#problems[@]}" -eq 0 ]]; then
  if readable "$intro" "$claude_md has no prose above its first '## ' heading" "the opening paragraph's script count"; then
    moved_by "opening paragraph's script count" "$(claimed "$intro" "$intro_claim" 1)" "$n_scripts" "$conductor_script"
  fi

  if readable "$idiom" "$claude_md has no '## $section_name' section" "the suite and script counts it states"; then
    moved_by "*$section_name* suite count" "$(claimed "$idiom" "$idiom_claim" 1)" "$n_suites" "${conductor_suites[@]}"
    moved_by "*$section_name* script count" "$(claimed "$idiom" "$idiom_claim" 2)" "$n_scripts" "$conductor_script"
  fi
fi

report "$name"

name="$claude_md's unit-tier suite count matches the unit suites on disk, including push-branch.sh's"
problems=()

unit_suite="skills/tdd/scripts/tests/unit/push-branch.test.sh"

present "$unit_suite"
n_unit="$(how_many "$unit_path")"
nonempty "unit suite" "$n_unit" "$unit_glob"

if [[ "${#problems[@]}" -eq 0 ]]; then
  if readable "$idiom" "$claude_md has no '## $section_name' section" "the unit suite count it states"; then
    check "*$section_name* unit suite count" "$(claimed "$idiom" "$unit_claim" 1)" "$n_unit"
  fi
fi

report "$name"

name="$claude_md's counts moved with invisible-work.sh and its suite, and its prose names the script the procedure does not call"
problems=()

if moved_with "skills/tdd/scripts/invisible-work.sh" "skills/tdd/scripts/tests/invisible-work.test.sh"; then
  if [[ -n "${intro// /}" && "$intro" != *"invisible-work.sh"* ]]; then
    problems+=("$claude_md's opening paragraph counts '<n> bash scripts it calls' without naming invisible-work.sh, a script the procedure never calls")
  fi
fi

report "$name"

name="$claude_md's stated script and suite counts are unchanged once the solve-issue stubs are gone"
problems=()

for stub in "skills/solve-issue" "skills/solve-issues"; do
  if [[ -e "$ROOT/$stub" ]]; then
    problems+=("$stub/ is still in the tree; the stubs this case counts without are not gone")
  fi
done

if [[ "${#problems[@]}" -eq 0 ]]; then
  nonempty script "$n_scripts" "$scripts_glob"
  nonempty suite "$n_suites" "$suites_glob"
  if readable "$intro" "$claude_md has no prose above its first '## ' heading" "the opening paragraph's script count"; then
    check "opening paragraph's script count" "$(claimed "$intro" "$intro_claim" 1)" "$n_scripts"
  fi
  if readable "$idiom" "$claude_md has no '## $section_name' section" "the suite and script counts it states"; then
    check "*$section_name* suite count" "$(claimed "$idiom" "$idiom_claim" 1)" "$n_suites"
    check "*$section_name* script count" "$(claimed "$idiom" "$idiom_claim" 2)" "$n_scripts"
  fi
fi

report "$name"

name="$claude_md's counts moved with the Stopping section's suite"
problems=()

stopping_suite="skills/tdd/scripts/tests/skill-stopping.test.sh"

present "$stopping_suite"

if [[ "${#problems[@]}" -eq 0 ]]; then
  if readable "$idiom" "$claude_md has no '## $section_name' section" "the suite count it states"; then
    moved_by "*$section_name* suite count" "$(claimed "$idiom" "$idiom_claim" 1)" "$n_suites" "$stopping_suite"
  fi
fi

report "$name"

name="$claude_md's counts moved with orchestrate.sh and its suite"
problems=()

moved_with "skills/tdd/scripts/orchestrate.sh" "skills/tdd/scripts/tests/orchestrate.test.sh"

report "$name"

name="$claude_md's counts moved with rebase-onto-default.sh and its suite"
problems=()

moved_with "skills/tdd/scripts/rebase-onto-default.sh" "skills/tdd/scripts/tests/rebase-onto-default.test.sh"

report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
