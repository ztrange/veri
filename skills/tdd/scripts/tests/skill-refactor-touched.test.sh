#!/usr/bin/env bash
# Unit test for how skills/tdd/SKILL.md computes the refactor loop's touched-files list — the
# bounds `build-develop-prompt.sh refactor` hands the leaf (issue #167). Like
# skill-refactor-leaf.test.sh this suite belongs to no single script: its subject is the
# procedure, read as text, the way the session that follows it reads it.
#
# The step's green commit is the atomic tick-and-commit, so it always carries the ledger. A
# list computed straight from `git diff --name-only` names `.tdd/issue-<n>.md`, and a leaf
# told the ledger is in its bounds may reword a step line and break the substring
# clear-refactor-pending.sh matches on. refactor-touched.sh leaves `.tdd/` out, once; the
# procedure has to call it in BOTH places it computes the list — the cycle loop's first
# computation and Resume's recomputation from `$green` — or the two disagree.
#
# Contract under test:
#   every `touched="$(…)"` line in SKILL.md, run in a repository whose HEAD is a green commit
#   that changed the ledger and two source files (with `$green` that commit and `$S` this
#   scripts directory) → exactly the two source files, in `git diff` order; there are two
#   such lines, and each computes the list through `$S/refactor-touched.sh`.
#
# The lines are executed rather than only matched, so what is pinned is the list each place
# produces, not its spelling. The separator is read as a comma or a newline, as in
# refactor-touched.test.sh.
#
# Run: scripts/tests/skill-refactor-touched.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"
skill_md="skills/tdd/SKILL.md"
skill_path="$ROOT/$skill_md"
pass=0 fail=0

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

git_q() { local repo="$1"; shift; git -C "$repo" -c user.name=veri -c user.email=veri@example.test "$@"; }

name="$skill_md computes the refactor touched-files list through refactor-touched.sh in the cycle loop and in Resume, and both name only the green commit's source files"
problems=()

repo="$work/green"
git init -q -b main "$repo" >/dev/null 2>&1
mkdir -p "$repo/.tdd" "$repo/lib" "$repo/src"
printf -- '- [ ] a step\n' > "$repo/.tdd/issue-7.md"
git_q "$repo" add -A >/dev/null 2>&1
git_q "$repo" commit -q -m "plan: scope #7" >/dev/null 2>&1
printf 'zeta\n' > "$repo/src/zeta.sh"
printf 'alpha\n' > "$repo/lib/alpha.test.sh"
printf -- '- [x] a step ⟂ refactor pending\n' > "$repo/.tdd/issue-7.md"
git_q "$repo" add -A >/dev/null 2>&1
git_q "$repo" commit -q -m "feat: a step (#7)" >/dev/null 2>&1
expected="$(printf 'lib/alpha.test.sh\nsrc/zeta.sh')"

lines=()
while IFS= read -r l; do lines+=("$l"); done < <(grep -E '^[[:space:]]*touched="\$\(' "$skill_path" | sed 's/^[[:space:]]*//')

[[ "${#lines[@]}" -eq 2 ]] ||
  problems+=("$skill_md has ${#lines[@]} touched=\"\$(…)\" computations, expected 2 (cycle loop and Resume)")
for l in "${lines[@]}"; do
  [[ "$l" == *'$S/refactor-touched.sh'* ]] ||
    problems+=("$skill_md computes touched without \$S/refactor-touched.sh: $l")
  got="$(cd "$repo" && S="$ROOT/skills/tdd/scripts" green="$(git rev-parse HEAD)" bash -c "$l"$'\nprintf %s "$touched"' 2>&1)"
  got="$(printf '%s' "$got" | tr ',' '\n' | sed '/^$/d')"
  [[ "$got" == "$expected" ]] ||
    problems+=("$l → '$(printf '%s' "$got" | paste -sd, -)', expected '$(printf '%s' "$expected" | paste -sd, -)'")
done

if [[ "${#problems[@]}" -eq 0 ]]; then pass=$((pass + 1)); else
  fail=$((fail + 1))
  echo "FAIL - $name"
  printf '    %s\n' "${problems[@]}"
fi

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
