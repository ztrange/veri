#!/usr/bin/env bash
# Unit test for where skills/tdd/SKILL.md runs the issue's one structural pass (issue #503).
# Like skill-refactor-owed.test.sh this suite belongs to no single script: its subject is the
# procedure, read as text, the way the session that follows it reads it.
#
# Contract under test: the Draft PR step — reached when `next-unchecked.sh` exits 3 — before
# its `gh pr ready`, lists the recorded candidates with `refactor-owed.sh list`, builds one
# `build-develop-prompt.sh structural` prompt per candidate, bounds it to
# `refactor-touched.sh --issue`, and counts it against `refactor-budget.sh --issue`.
#
# Run: scripts/tests/skill-structural-pass.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
# The suite sits at skills/<skill>/scripts/tests, so four levels up is the repo root.
ROOT="$(cd "$HERE/../../../.." && pwd)"
skill_md="skills/tdd/SKILL.md"
skill_path="$ROOT/$skill_md"

pass=0 fail=0

report() {
  local name="$1"
  if [[ "${#problems[@]}" -eq 0 ]]; then
    pass=$((pass + 1))
  else
    fail=$((fail + 1))
    echo "FAIL - $name"
    printf '    %s\n' "${problems[@]}"
  fi
}

# require <needle> <text> <problem> — records <problem> when <text> does not hold <needle>.
require() {
  grep -F -- "$1" > /dev/null <<<"$2" || problems+=("$3")
}

# before_ready — the Draft PR section's lines up to its first `gh pr ready`, backticks and
# emphasis dropped and joined onto one line.
before_ready() {
  awk -v h='### 4. Draft PR' \
    'index($0, h) == 1 { inside = 1; next }
     inside && (/^#/ || /gh pr ready/) { exit }
     inside' "$skill_path" | tr -d '*`' | tr '\n' ' '
}
section="$(before_ready)"

name="$skill_md's Draft PR step runs one structural pass before gh pr ready: a structural leaf per refactor-owed.sh list candidate, bounded by refactor-touched.sh --issue, counted by refactor-budget.sh --issue"
problems=()

if [[ -z "${section// /}" ]]; then
  problems+=("$skill_md has no '### 4. Draft PR' section before a gh pr ready to read — where the structural pass runs could not be established")
else
  require 'refactor-owed.sh list' "$section" \
    "$skill_md's Draft PR step never runs refactor-owed.sh list before gh pr ready, so the recorded structural candidates are never taken up"
  require 'build-develop-prompt.sh structural' "$section" \
    "$skill_md's Draft PR step never builds a build-develop-prompt.sh structural prompt before gh pr ready, so no structural transform leaf is launched"
  require 'refactor-touched.sh --issue' "$section" \
    "$skill_md's Draft PR step never computes refactor-touched.sh --issue before gh pr ready, so the structural pass has no bounds"
  require 'refactor-budget.sh --issue' "$section" \
    "$skill_md's Draft PR step never asks refactor-budget.sh --issue before gh pr ready, so the structural pass has no budget"
fi

report "$name"

pass_text="${section#*one structural pass}"
touches_phrase='transform-touches-tests.sh <base-sha>'
verifier_phrase='transform verifier against <base-sha>'

name="$skill_md's structural pass checks each transform leaf's commits with transform-touches-tests.sh <base-sha> and has the blind transform verifier judge them against that base sha, one commit per transform"
problems=()

if [[ "$pass_text" == "$section" ]]; then
  problems+=("$skill_md's Draft PR step has no 'one structural pass' before gh pr ready — how its transforms are checked could not be established")
else
  require "$touches_phrase" "$pass_text" \
    "$skill_md's structural pass never runs transform-touches-tests.sh <base-sha> on a transform leaf's commits, so a structural transform that edits a test file is never rejected"
  require "$verifier_phrase" "$pass_text" \
    "$skill_md's structural pass never has the blind transform verifier judge a transform against its <base-sha>"
  require 'one commit per transform' "$pass_text" \
    "$skill_md's structural pass never says one commit per transform"
fi

report "$name"

# offset <needle> <text> — the byte offset of <needle>'s first occurrence in <text>, or -1.
offset() {
  local head="${2%%"$1"*}"
  if [[ "$head" == "$2" ]]; then echo -1; else echo "${#head}"; fi
}

name="$skill_md's structural pass runs transform-touches-tests.sh before the blind transform verifier, and both before the next candidate's structural leaf is launched"
problems=()

if [[ "$pass_text" == "$section" ]]; then
  problems+=("$skill_md's Draft PR step has no 'one structural pass' before gh pr ready — the order of its checks could not be established")
else
  touches="$(offset "$touches_phrase" "$pass_text")"
  verifier="$(offset "$verifier_phrase" "$pass_text")"
  next="$(offset 'before the next candidate' "$pass_text")"
  if [[ "$touches" -lt 0 || "$verifier" -lt 0 || "$next" -lt 0 ]]; then
    problems+=("$skill_md's structural pass is missing a phrase to order: transform-touches-tests.sh at $touches, transform verifier at $verifier, 'before the next candidate' at $next (-1 = absent)")
  elif [[ ! ( "$touches" -lt "$verifier" && "$verifier" -lt "$next" ) ]]; then
    problems+=("$skill_md's structural pass orders its checks wrongly: transform-touches-tests.sh at $touches, transform verifier at $verifier, 'before the next candidate' at $next — expected ascending")
  fi
fi

report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
