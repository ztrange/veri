#!/usr/bin/env bash
# Unit test for the step a verifier launch in skills/tdd/SKILL.md carries, read as text.
#
# Contract under test:
#   Every `verify.sh` call SKILL.md tells the conductor to run — the red, pin, green,
#   refactor, revise re-verify and resume launches — passes `--step "<STEP>"` before
#   verify.sh's positionals; and every one that can judge green — the green launch and the
#   revise re-verify, whose phase is `<phase>` — passes `--fast-cmd '<fast-cmd>'` after it.
#   A call is a line naming `verify.sh` with the spec file among its arguments; the script
#   inventory's `<red|green|refactor|pin|plan>` synopsis is not one.
#
# Run: skills/tdd/scripts/tests/skill-verify-step.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"

skill_md="skills/tdd/SKILL.md"
skill_path="$ROOT/$skill_md"

flag='--step "<STEP>"'

call_re="verify\.sh $flag( --fast-cmd '<fast-cmd>')? (red|green|refactor|pin|<phase>)"


source "$HERE/lib/harness.sh"
source "$HERE/lib/plain.sh"

verify_calls() {
  grep -nE 'verify\.sh.*(<spec-file>|\.tdd/issue-<n>-spec\.md)' "$skill_path" |
    grep -vF '<red|green|refactor|pin|plan>'
}

name="$skill_md passes $flag on every verify.sh call it tells the conductor to run"
problems=()

calls="$(verify_calls)"
if [[ -z "$calls" ]]; then
  problems+=("$skill_md has no verify.sh call naming a spec file — the calls this case is about could not be read")
else
  while IFS= read -r numbered; do
    [[ -n "$numbered" ]] || continue
    lineno="${numbered%%:*}"
    line="${numbered#*:}"
    [[ "$line" =~ $call_re ]] ||
      problems+=("$skill_md:$lineno does not pass $flag before verify.sh's positionals: $line")
  done <<< "$calls"
fi

report "$name"

fast_flag="--fast-cmd '<fast-cmd>'"
green_re="verify\.sh $flag( $fast_flag)? (green|<phase>) "
name="$skill_md passes $fast_flag on every verify.sh call that can judge green"
problems=()

if [[ -n "$calls" ]]; then
  while IFS= read -r numbered; do
    [[ -n "$numbered" ]] || continue
    lineno="${numbered%%:*}"
    line="${numbered#*:}"
    [[ "$line" =~ $green_re ]] || continue
    [[ "$line" == *"verify.sh $flag $fast_flag "* ]] ||
      problems+=("$skill_md:$lineno can judge green but does not pass $fast_flag: $line")
  done <<< "$calls"
fi

report "$name"

name="#1521: $skill_md has the conductor run unreplaced-cases.sh before verify-green and bail unreplaced-cases on exit 1"
problems=()
text="$(plain --join < "$skill_path")"
if [[ "$text" != *'unreplaced-cases.sh'* ]]; then
  problems+=("$skill_md never mentions unreplaced-cases.sh")
else
  text="${text#*unreplaced-cases.sh}"
  text="${text:0:1200}"
  says() { [[ "$text" =~ $1 ]] || problems+=("$2"); }
  says 'replaces-case' \
    "$skill_md's unreplaced-cases.sh guard never says it applies to a ⟦replaces-case⟧ step"
  says 'exit 1|exits 1|exit \*\*1' \
    "$skill_md's unreplaced-cases.sh guard never branches on exit 1"
  says 'cause=unreplaced-cases|cause `unreplaced-cases`' \
    "$skill_md's unreplaced-cases.sh guard never bails with cause unreplaced-cases"
  says '(without|never|not|before)[^.]{0,80}verify-green|verify-green[^.]{0,80}(not|never|without)' \
    "$skill_md's unreplaced-cases.sh guard never keeps verify-green from launching"
fi
report "$name"

finish
