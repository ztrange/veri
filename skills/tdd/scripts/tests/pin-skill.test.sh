#!/usr/bin/env bash
# Unit tests for scripts/pin-skill.sh — the snapshot of the skill's `scripts/` directory a
# run takes once, at preflight, so no later `$S/…` call can read a script the primary clone
# has changed underneath it (issue #165).
#
# Why this exists: `~/.claude/skills/tdd` is a symlink into the primary clone, and the
# primary clone is not a fixed point — it stays on `main` and the `merge` skill pulls it
# after every landing. A conductor that resolves `$S` into that checkout follows SKILL.md
# prose from commit A while launching leaves out of scripts from commit B, and a leaf can
# read a file git is halfway through rewriting.
#
# Contract under test:
#   pin-skill.sh    run from the run's worktree, with no arguments
#     → copies <skill>/scripts/ to ./.tdd/skill/scripts/ (recursively — `prompts/` is in
#       there, and a prompt template changing under a run is half of what #165 is about)
#     → writes the skill repo's HEAD sha to ./.tdd/skill-commit
#     → prints the absolute path of ./.tdd/skill/scripts on stdout, exit 0
#     → on a second call — a resume — reuses the snapshot already there: the files and the
#       recorded sha stay the ones the run started on, not the clone's current HEAD.
#
# The skill under test is a *copy* of the real pin-skill.sh, planted in a throwaway git repo
# shaped like the primary clone (`skills/tdd/scripts/`). That is the only way to move the
# skill's HEAD between the two calls, which is the whole of the resume assertion — and it
# keeps the suite's answer a fact about the script rather than about this repository's
# current sha.
#
# Run: scripts/tests/pin-skill.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
PIN="$HERE/../pin-skill.sh"
# `pwd -P` (P for physical — every symlink on the path resolved) because macOS puts mktemp
# dirs behind /var -> /private/var, and the path the script prints will be resolved while
# the one we built the fixture from is not: a correct script would compare unequal.
work="$(cd "$(mktemp -d)" && pwd -P)"
trap 'rm -rf "$work"' EXIT
pass=0 fail=0

# report <name> — close a case whose probes collected into the `problems` array: an empty
# array is a pass, otherwise one FAIL line for the case and one indented line per problem,
# so the output names which half of the contract broke. Same idiom as
# claude-md-counts.test.sh and hermetic-suites.test.sh.
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

# git_q <repo> <args...> — git with an identity of its own, so the suite does not depend on
# whatever user.name/user.email the machine running it happens to carry (CI carries none).
git_q() { local repo="$1"; shift; git -C "$repo" -c user.name=veri -c user.email=veri@example.test "$@"; }

# holds <path> <want> <what> — one snapshotted file against the text it should carry.
# A missing file is its own problem rather than an empty string that happens to differ,
# because "the snapshot has no prompts/ in it" and "the template says the wrong thing" are
# repaired differently.
holds() {
  if [[ ! -f "$1" ]]; then
    problems+=("$3 is not there ($1)")
    return
  fi
  local got; got="$(cat "$1")"
  [[ "$got" == "$2" ]] || problems+=("$3 says '$got'; want '$2'")
}

# 1. The criterion. A skill repo shaped like the primary clone, a run directory beside it,
#    and the same call made twice with the clone moving on in between — which is the pull
#    the `merge` skill does while a conductor is mid-run.
name="pin-skill.sh: snapshots scripts/ into .tdd/skill/scripts, records the sha in .tdd/skill-commit, prints the snapshot path, and a resume reuses that snapshot rather than the clone's new HEAD"
problems=()

# Fail closed on the script itself being gone — but say so and carry on rather than
# returning early, so the output still shows which parts of the contract went unanswered
# instead of one line that could be read as the only thing wrong.
[[ -f "$PIN" ]] ||
  problems+=("pin-skill.sh is not in scripts/ — nothing to pin the skill with")

clone="$work/clone"
skill="$clone/skills/tdd"
mkdir -p "$skill/scripts/prompts"
cp "$PIN" "$skill/scripts/pin-skill.sh" 2>/dev/null
chmod +x "$skill/scripts/pin-skill.sh" 2>/dev/null
printf 'v1\n' > "$skill/scripts/marker.sh"
printf 'template v1\n' > "$skill/scripts/prompts/red.md"
git init -q -b main "$clone" >/dev/null 2>&1
git_q "$clone" add -A >/dev/null 2>&1
git_q "$clone" commit -q -m "the skill at v1" >/dev/null 2>&1
sha1="$(git -C "$clone" rev-parse HEAD 2>/dev/null)"

run="$work/run"
mkdir -p "$run"
want_path="$run/.tdd/skill/scripts"

out="$(cd "$run" && "$skill/scripts/pin-skill.sh" 2>/dev/null)" && code=0 || code=$?

[[ "$code" == 0 ]] ||
  problems+=("first call: exit $code, want 0")
[[ "$out" == "$want_path" ]] ||
  problems+=("first call: stdout '$out'; want the snapshot scripts path '$want_path'")
holds "$want_path/marker.sh" "v1" "the snapshotted marker.sh"
holds "$want_path/prompts/red.md" "template v1" "the snapshotted prompts/red.md"
holds "$run/.tdd/skill-commit" "$sha1" ".tdd/skill-commit"

# The primary clone lands a PR and pulls: same paths, different content, different HEAD.
printf 'v2\n' > "$skill/scripts/marker.sh"
printf 'template v2\n' > "$skill/scripts/prompts/red.md"
git_q "$clone" add -A >/dev/null 2>&1
git_q "$clone" commit -q -m "the skill at v2" >/dev/null 2>&1
sha2="$(git -C "$clone" rev-parse HEAD 2>/dev/null)"

# Guard the fixture itself: if the second commit did not move HEAD, the resume half below
# would pass against a clone that never changed — a green for the wrong reason.
[[ -n "$sha1" && -n "$sha2" && "$sha1" != "$sha2" ]] ||
  problems+=("fixture: the skill clone's HEAD did not move ('$sha1' then '$sha2')")

out2="$(cd "$run" && "$skill/scripts/pin-skill.sh" 2>/dev/null)" && code2=0 || code2=$?

[[ "$code2" == 0 ]] ||
  problems+=("resume: exit $code2, want 0")
[[ "$out2" == "$want_path" ]] ||
  problems+=("resume: stdout '$out2'; want the same snapshot scripts path '$want_path'")
holds "$want_path/marker.sh" "v1" "the snapshotted marker.sh after the clone moved to v2"
holds "$want_path/prompts/red.md" "template v1" "the snapshotted prompts/red.md after the clone moved to v2"
holds "$run/.tdd/skill-commit" "$sha1" ".tdd/skill-commit after the clone moved to v2"

report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
