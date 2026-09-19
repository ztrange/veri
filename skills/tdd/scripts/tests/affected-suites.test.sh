#!/usr/bin/env bash
# Unit tests for scripts/affected-suites.sh — prints the suites one change affects, so a red or
# refactor leaf can run a narrow slice of `make test` instead of all of it (issue #337).
#
# Contract under test:
#   affected-suites.sh <base>..<head>, run inside the repository
#                       → exit 0, and one suite path per line, sorted, with no duplicate.
#
# Every case builds a fixture tree of its own shaped like this repository's
# `skills/tdd/scripts/`, so the answer never depends on the suites the repository `make test`
# was typed in happens to have.
#
# Run: scripts/tests/affected-suites.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
AFFECTED="$HERE/../affected-suites.sh"
pass=0 fail=0
ok() { pass=$((pass + 1)); }
no() { fail=$((fail + 1)); echo "FAIL - $1"; }

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

# git_q <repo> <args…> — git with a fixed identity, so a commit does not depend on the
# user.name/user.email of the machine running the suite (CI carries none).
git_q() { local repo="$1"; shift; git -C "$repo" -c user.name=veri -c user.email=veri@example.test "$@"; }

# commit_all <repo> <message> — stage everything in <repo> and commit it.
commit_all() {
  git_q "$1" add -A >/dev/null 2>&1
  git_q "$1" commit -q -m "$2" >/dev/null 2>&1
}

# new_repo <name> -> path — a repository of the case's own under $work.
new_repo() {
  local dir="$work/$1"
  git init -q -b main "$dir" >/dev/null 2>&1
  echo "$dir"
}

# 1. a resolvable range → one suite per line, sorted, no duplicate. The range touches
#    wolf.sh and its own suite, so both name tests/wolf.test.sh and a list that kept every
#    answer would carry it twice; and zulu.sh, whose suite is under tests/unit/, so the diff
#    order (wolf before zulu) puts tests/wolf.test.sh ahead of tests/unit/zulu.test.sh, which
#    sorts first.
repo="$(new_repo sorted)"
s="$repo/skills/tdd/scripts"
mkdir -p "$s/tests/unit"
printf 'wolf\n' > "$s/wolf.sh"
printf 'zulu\n' > "$s/zulu.sh"
printf '# wolf suite\n' > "$s/tests/wolf.test.sh"
printf '# zulu suite\n' > "$s/tests/unit/zulu.test.sh"
commit_all "$repo" "base"
base="$(git -C "$repo" rev-parse HEAD)"
printf 'wolf 2\n' > "$s/wolf.sh"
printf 'zulu 2\n' > "$s/zulu.sh"
printf '# wolf suite 2\n' > "$s/tests/wolf.test.sh"
commit_all "$repo" "head"
head="$(git -C "$repo" rev-parse HEAD)"
expected="$(printf 'skills/tdd/scripts/tests/unit/zulu.test.sh\nskills/tdd/scripts/tests/wolf.test.sh')"
out="$(cd "$repo" && "$AFFECTED" "$base..$head" 2>/dev/null)"; code=$?
if [[ "$code" == 0 && "$out" == "$expected" ]]; then ok; else
  no "resolvable range → one suite per line, sorted, no duplicate (code=$code)"
  diff <(printf '%s\n' "$expected") <(printf '%s\n' "$out") | sed 's/^/    /'
fi

# 2. a malformed argument → exit 2 and a diagnostic on stderr. Three shapes: a single
#    revision with no `..` (which git diff alone would read as "against the working tree"
#    and answer happily), and a range whose base or head git cannot resolve.
repo="$(new_repo malformed)"
mkdir -p "$repo/skills/tdd/scripts"
printf 'wolf\n' > "$repo/skills/tdd/scripts/wolf.sh"
commit_all "$repo" "base"
head="$(git -C "$repo" rev-parse HEAD)"
bad=""
for arg in "$head" "$head..no-such-rev" "no-such-rev..$head"; do
  err="$(cd "$repo" && "$AFFECTED" "$arg" 2>&1 >/dev/null)"; code=$?
  if [[ "$code" != 2 || -z "$err" ]]; then
    bad="${arg/$head/<head>}: code=$code, stderr=${err:-<empty>}"
    break
  fi
done
if [[ -z "$bad" ]]; then ok; else
  no "malformed argument → exit 2 with a diagnostic ($bad)"
fi

# 3. a range whose diff is empty → exit 3 and nothing on stdout: nothing changed is "nothing
#    to do", not an error and not an empty answer. The head is a real commit of its own, made
#    with --allow-empty, so the range is two distinct revisions git resolves and only the diff
#    between them is empty.
repo="$(new_repo empty)"
mkdir -p "$repo/skills/tdd/scripts/tests"
printf 'wolf\n' > "$repo/skills/tdd/scripts/wolf.sh"
printf '# wolf suite\n' > "$repo/skills/tdd/scripts/tests/wolf.test.sh"
commit_all "$repo" "base"
base="$(git -C "$repo" rev-parse HEAD)"
git_q "$repo" commit -q --allow-empty -m "head" >/dev/null 2>&1
head="$(git -C "$repo" rev-parse HEAD)"
out="$(cd "$repo" && "$AFFECTED" "$base..$head" 2>/dev/null)"; code=$?
if [[ "$code" == 3 && -z "$out" ]]; then ok; else
  no "empty diff → exit 3 and prints nothing (code=$code, stdout=${out:-<empty>})"
fi

# 4. rule 1: a change to a script under skills/tdd/scripts/ → exactly its own suite. The tree
#    also holds a second script with a suite of its own, untouched, so an answer that listed
#    every suite, or the neighbour's, would not pass for "exactly that suite".
repo="$(new_repo rule1)"
s="$repo/skills/tdd/scripts"
mkdir -p "$s/tests"
printf 'foo\n' > "$s/foo.sh"
printf 'bar\n' > "$s/bar.sh"
printf '# foo suite\n' > "$s/tests/foo.test.sh"
printf '# bar suite\n' > "$s/tests/bar.test.sh"
commit_all "$repo" "base"
base="$(git -C "$repo" rev-parse HEAD)"
printf 'foo 2\n' > "$s/foo.sh"
commit_all "$repo" "head"
head="$(git -C "$repo" rev-parse HEAD)"
expected="skills/tdd/scripts/tests/foo.test.sh"
out="$(cd "$repo" && "$AFFECTED" "$base..$head" 2>/dev/null)"; code=$?
if [[ "$code" == 0 && "$out" == "$expected" ]]; then ok; else
  no "rule 1: a change to scripts/foo.sh prints exactly tests/foo.test.sh (code=$code)"
  diff <(printf '%s\n' "$expected") <(printf '%s\n' "$out") | sed 's/^/    /'
fi

# 5. rule 1 via tests/unit/: a change to a script whose suite lives under tests/unit/ → that
#    unit suite, not a tests/<script>.test.sh that does not exist. A neighbour script with a
#    suite under tests/ is left untouched, so the answer must be the unit suite alone.
repo="$(new_repo rule1-unit)"
s="$repo/skills/tdd/scripts"
mkdir -p "$s/tests/unit"
printf 'foo\n' > "$s/foo.sh"
printf 'bar\n' > "$s/bar.sh"
printf '# foo unit suite\n' > "$s/tests/unit/foo.test.sh"
printf '# bar suite\n' > "$s/tests/bar.test.sh"
commit_all "$repo" "base"
base="$(git -C "$repo" rev-parse HEAD)"
printf 'foo 2\n' > "$s/foo.sh"
commit_all "$repo" "head"
head="$(git -C "$repo" rev-parse HEAD)"
expected="skills/tdd/scripts/tests/unit/foo.test.sh"
out="$(cd "$repo" && "$AFFECTED" "$base..$head" 2>/dev/null)"; code=$?
if [[ "$code" == 0 && "$out" == "$expected" ]]; then ok; else
  no "rule 1 via tests/unit/: a change to scripts/foo.sh prints exactly tests/unit/foo.test.sh (code=$code)"
  diff <(printf '%s\n' "$expected") <(printf '%s\n' "$out") | sed 's/^/    /'
fi

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
