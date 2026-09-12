#!/usr/bin/env bash
# Unit tests for where the skill ships and what it calls itself — like
# hermetic-suites.test.sh this suite belongs to no single script: its subject is the
# skill directory that contains all of them.
# Zero-dependency plain-shell asserts, same idiom as hermetic-suites.test.sh.
#
# Why this exists (issue #105): the invocation name is the one thing every user touches,
# and it is spelled in two places that must agree — the directory Claude Code loads the
# skill from, and the `name:` field of its SKILL.md frontmatter, which is the command.
#
# Contracts under test:
#   skills/tdd/ is a directory, and skills/tdd/SKILL.md's frontmatter reads `name: tdd`.
#   No tracked file outside the two forwarding stubs still names the scripts directory
#   under the skill's old home — the build and test plumbing follows the skill when it moves.
#
# Run: scripts/tests/skill-identity.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
# The suite sits at skills/<skill>/scripts/tests, so four levels up is the repo root
# whichever name the skill currently carries — the path this case is about is then
# spelled out in full below rather than derived from where this file happens to live.
ROOT="$(cd "$HERE/../../../.." && pwd)"

# The two halves of the identity, each written down exactly once: the directory Claude Code
# loads the skill from, and the command name its frontmatter must declare. Neither is
# derived from the other, so a half-finished move — tree renamed, frontmatter not, or the
# reverse — still fails; and every message below quotes these rather than re-spelling them,
# so there is one place to edit if the skill is ever renamed again.
skill_dir="skills/tdd"
want_name="tdd"
# The frontmatter's file, named in the same terms as the directory: both paths in this suite
# are relative to $ROOT, and $ROOT is applied where they are used. Mixing the two bases — one
# variable relative, one already absolute — is what made the probes below read inconsistently.
skill_md="$skill_dir/SKILL.md"

pass=0 fail=0

# report <name> — close a case whose probes collected into the `problems` array: an empty
# array is a pass, otherwise one FAIL line for the case and one indented line per problem.
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

# 1. Both halves of the skill's identity, as one criterion: the directory it lives in and
#    the name its frontmatter declares. The frontmatter is the leading `---` block, and
#    only its first `name:` counts — the awk stops at the closing `---` so a later `name:`
#    in the prose cannot answer for it.
name="the skill ships at $skill_dir/ and its frontmatter reads name: $want_name"
problems=()
[[ -d "$ROOT/$skill_dir" ]] ||
  problems+=("want a directory at $skill_dir, found none")
if [[ -f "$ROOT/$skill_md" ]]; then
  # sub() edits $0 and returns how many replacements it made, so it doubles as the
  # "this line is the name field" test; print then emits what is left, the value.
  got="$(awk 'NR == 1 && $0 == "---" { inside = 1; next }
              inside && $0 == "---" { exit }
              inside && sub(/^name:[[:space:]]*/, "") { print; exit }' "$ROOT/$skill_md")"
  [[ "$got" == "$want_name" ]] ||
    problems+=("$skill_md frontmatter: want name '$want_name', got $(printf '%q' "$got")")
else
  problems+=("want a SKILL.md at $skill_md, found none")
fi
report "$name"

# The skill's former home, and the scripts directory inside it that the Makefile, the docs
# build and the demo fixtures used to point at. Assembled from two pieces on purpose: the
# probe below greps the whole repository for the joined string, so spelling it out here
# would make this file its own first offender.
old_skill_dir="skills/solve-issue"
old_scripts_dir="$old_skill_dir/scripts"
# The two files the move deliberately leaves behind under the old names, each a stub whose
# body forwards to /tdd. They are allowed to name the old home; nothing else is.
stubs=("$old_skill_dir/SKILL.md" "skills/solve-issues/SKILL.md")

# 2. The plumbing moved with the skill. Stated as the absence it has to produce rather than
#    as a list of files to check, so a path constant hiding somewhere this test never heard
#    of still counts: no tracked file names the old scripts directory except the stubs.
#    Tracked, via `git grep`, because the repository's content is what ships — and .tdd/ is
#    excluded because those ledgers are run state, quoting each issue's own words back
#    verbatim, including this one's.
name="no tracked file outside the two stubs still names $old_scripts_dir"
problems=()
# git grep exits 1 for "no matches", which is the pass here, and 2+ for a real failure —
# collapsing the two would turn a broken probe into a silent green.
hits="$(cd "$ROOT" && git grep --files-with-matches --fixed-strings -e "$old_scripts_dir")" &&
  code=0 || code=$?
if [[ "$code" -le 1 ]]; then
  while IFS= read -r f; do
    [[ -n "$f" ]] || continue
    case "$f" in .tdd/*) continue ;; esac
    for stub in "${stubs[@]}"; do
      [[ "$f" == "$stub" ]] && continue 2
    done
    problems+=("$f still names $old_scripts_dir")
  done <<< "$hits"
else
  problems+=("git grep failed with exit $code")
fi
report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
