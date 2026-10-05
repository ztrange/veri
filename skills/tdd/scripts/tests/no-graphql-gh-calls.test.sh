#!/usr/bin/env bash
# Unit tests for the tree — no `gh issue`, `gh pr` or `gh repo` call may be left in
# skills/tdd/SKILL.md or skills/tdd/scripts/*.sh, because each one goes through GitHub's
# GraphQL endpoint, which a Claude Code cloud session refuses. Like no-job-spec-kills.test.sh
# this suite has no script as its subject: its subject is the tree it is run in.
#
# Contract under test:
#   A call is reported as `<file>:<line>`. lib/github.sh is outside the scanned set, and is
#   where the ready-for-review route lives. A comment line in a script is not a call.
#
# Run: skills/tdd/scripts/tests/no-graphql-gh-calls.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"

GH_CALL='(^|[^[:alnum:]_.-])gh[[:space:]]+((issue|pr|repo)([[:space:]]|$)|auth[[:space:]]+status([^[:alnum:]_-]|$))'

source "$HERE/lib/harness.sh"

probe_no_graphql_call_is_left() {
  local hit file rest line text
  while IFS= read -r hit; do
    file="${hit%%:*}"
    rest="${hit#*:}"
    line="${rest%%:*}"
    text="${rest#*:}"
    [[ "$file" == *.sh && "$text" =~ ^[[:space:]]*# ]] && continue
    problems+=("$file:$line calls a gh subcommand that goes through GraphQL, which a Claude Code cloud session refuses: use gh api, or the helpers in skills/tdd/scripts/lib/github.sh: ${text//$'\n'/\/}")
  done < <(cd "$ROOT" && grep -nE -- "$GH_CALL" skills/tdd/SKILL.md skills/tdd/scripts/*.sh)
  return 0
}

name="no gh issue, pr or repo call is left in SKILL.md or scripts/*.sh"
problems=()

probe_no_graphql_call_is_left

report "$name"

plant_tree() {
  ROOT="$(scratch_dir)"
  mkdir -p "$ROOT/skills/tdd/scripts"
  printf '%s\n' '# Procedure' '' '- `gh auth status` succeeds.' > "$ROOT/skills/tdd/SKILL.md"
  printf '%s\n' '#!/usr/bin/env bash' 'gh auth status || exit 2' > "$ROOT/skills/tdd/scripts/planted.sh"
}

named_in_problems() {
  local problem
  for problem in ${problems+"${problems[@]}"}; do
    [[ "$problem" == "$1 "* ]] && { printf named; return; }
  done
  printf 'not named'
}

probe_a_planted_gh_auth_status() {
  local ROOT
  plant_tree
  problems=()
  probe_no_graphql_call_is_left
  planted_named="SKILL.md $(named_in_problems skills/tdd/SKILL.md:3);script $(named_in_problems skills/tdd/scripts/planted.sh:2);"
  printf '%s\n' '# Procedure' '' '- `gh api user` succeeds.' > "$ROOT/skills/tdd/SKILL.md"
  printf '%s\n' '#!/usr/bin/env bash' 'gh api user || exit 2' > "$ROOT/skills/tdd/scripts/planted.sh"
  problems=()
  probe_no_graphql_call_is_left
  planted_named+="clean ${#problems[@]}"
  problems=()
}

name="a gh auth status call planted in SKILL.md or a scripts/*.sh is named as <file>:<line>, and a tree holding none passes (#864)"
planted_named=""

probe_a_planted_gh_auth_status

expect_eq "$name" "SKILL.md named;script named;clean 0" "$planted_named"

finish
