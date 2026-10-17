#!/usr/bin/env bash
# Unit test for where skills/tdd/SKILL.md runs the issue's one structural pass, read as
# text.
#
# Contract under test: the Draft PR step — reached when `next-unchecked.sh` exits 3 — before
# its `gh pr ready`, lists the recorded candidates with `refactor-owed.sh list`, builds one
# `build-develop-prompt.sh structural` prompt per candidate, bounds it to
# `refactor-touched.sh --issue`, and counts it against `refactor-budget.sh --issue`.
#
# Run: scripts/tests/skill-structural-pass.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"
skill_md="skills/tdd/SKILL.md"
skill_path="$ROOT/$skill_md"
draft_pr='### 4. Draft PR'


source "$HERE/lib/harness.sh"

require() {
  grep -F -- "$1" > /dev/null <<<"$2" || problems+=("$3")
}

before_ready() {
  awk -v h="$draft_pr" \
    'index($0, h) == 1 { inside = 1; next }
     inside && (/^#/ || /gh_pr_ready/) { exit }
     inside' "$skill_path" | tr -d '*`' | tr '\n' ' '
}
section="$(before_ready)"

pass_text="${section#*one structural pass}"
squeezed="$(tr -s ' ' <<<"$pass_text")"
touches_phrase='transform-touches-tests.sh <base-sha>'
verifier_phrase='transform verifier against <base-sha>'

missing_pass() {
  [[ "$pass_text" == "$section" ]] || return 1
  problems+=("$skill_md's Draft PR step has no 'one structural pass' before gh pr ready — $1 could not be established")
}

offset() {
  local head="${2%%"$1"*}"
  if [[ "$head" == "$2" ]]; then echo -1; else echo "${#head}"; fi
}

finish
