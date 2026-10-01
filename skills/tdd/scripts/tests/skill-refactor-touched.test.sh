#!/usr/bin/env bash
# Unit test for how skills/tdd/SKILL.md computes the refactor loop's touched-files list —
# the bounds `build-develop-prompt.sh refactor` hands the leaf.
#
# Contract under test:
#   every `touched="$(…)"` line in SKILL.md, run in a repository whose HEAD is a green commit
#   that changed the ledger and two source files (with `$green` that commit and `$S` this
#   scripts directory) → exactly the two source files, in `git diff` order, read with a
#   comma or a newline as separator; there are two such lines, and each computes the list
#   through `$S/refactor-touched.sh`.
#
# Run: scripts/tests/skill-refactor-touched.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"
skill_md="skills/tdd/SKILL.md"
skill_path="$ROOT/$skill_md"
source "$HERE/lib/harness.sh"

work="$(scratch_dir)"

git_q() { local repo="$1"; shift; git -C "$repo" -c user.name=veri -c user.email=veri@example.test "$@"; }

name="$skill_md computes the refactor touched-files list through refactor-touched.sh in the cycle loop and in Resume, and both name only the green commit's source files"
problems=()

repo="$work/green"
new_repo -b main "$repo" >/dev/null 2>&1
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

if [[ "${#problems[@]}" -eq 0 ]]; then ok; else
  no "$name"
  printf '    %s\n' "${problems[@]}"
fi

finish
