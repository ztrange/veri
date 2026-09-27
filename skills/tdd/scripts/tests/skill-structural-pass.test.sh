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
  grep -F 'refactor-owed.sh list' > /dev/null <<<"$section" ||
    problems+=("$skill_md's Draft PR step never runs refactor-owed.sh list before gh pr ready, so the recorded structural candidates are never taken up")
  grep -F 'build-develop-prompt.sh structural' > /dev/null <<<"$section" ||
    problems+=("$skill_md's Draft PR step never builds a build-develop-prompt.sh structural prompt before gh pr ready, so no structural transform leaf is launched")
  grep -F 'refactor-touched.sh --issue' > /dev/null <<<"$section" ||
    problems+=("$skill_md's Draft PR step never computes refactor-touched.sh --issue before gh pr ready, so the structural pass has no bounds")
  grep -F 'refactor-budget.sh --issue' > /dev/null <<<"$section" ||
    problems+=("$skill_md's Draft PR step never asks refactor-budget.sh --issue before gh pr ready, so the structural pass has no budget")
fi

report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
