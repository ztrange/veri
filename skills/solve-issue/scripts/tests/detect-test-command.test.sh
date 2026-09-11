#!/usr/bin/env bash
# Unit tests for scripts/detect-test-command.sh — prints the one command that runs the
# full suite of the repo at [repo-root] on stdout and exits 0; prints nothing and exits 3
# when it cannot decide (the conductor then asks the human).
#
# Contract under test (issue #39):
#   detect-test-command.sh [repo-root]   (default: the current directory)
#   precedence, first match wins: .veri/test-command override, npm/pnpm/yarn, make,
#   pytest, go, cargo, unittest — otherwise exit 3.
#
# Each case seeds a throwaway `mktemp -d` repo with only the marker files it is about:
# the script inspects files, it never runs the command, so no toolchain is needed.
# Sibling style: classify-bail.test.sh, ensure-run-state-ignored.test.sh.
#
# Run: scripts/tests/detect-test-command.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
DETECT="$HERE/../detect-test-command.sh"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
pass=0 fail=0
ok() { pass=$((pass + 1)); }
no() { fail=$((fail + 1)); echo "FAIL - $1"; }

# 1. the .veri/test-command override wins over every inference, and its line is printed
# verbatim. The repo is seeded so that *both* of the highest-precedence inferences would
# otherwise fire (package.json with a test script → `npm test`; Makefile with a test
# target → `make test`), so a stdout of the override line can only mean the override was
# consulted first, not that inference happened to agree. The command itself is one no
# rule could ever infer — flags and all — so any normalising or re-quoting shows up.
#
# One name for the command, used to seed the file and to check stdout: "verbatim" is the
# claim, so the bytes written in and the bytes expected out must be the same bytes.
want='bin/run-suite --all --strict'
repo="$work/override"
mkdir -p "$repo/.veri"
printf '%s\n' "$want" > "$repo/.veri/test-command"
printf '{"scripts":{"test":"jest"}}\n' > "$repo/package.json"
printf 'test:\n\techo hi\n' > "$repo/Makefile"

out="$("$DETECT" "$repo" 2>/dev/null)" && code=0 || code=$?

{ [[ "$code" == 0 ]] && [[ "$out" == "$want" ]]; } \
  && ok || no ".veri/test-command beats package.json and Makefile, printed verbatim (exit=$code want 0, stdout='$out' want '$want')"

# 2. a package.json carrying a scripts.test entry names the node runner, and which runner is
# decided by the lockfile lying beside it: bare → `npm test`, pnpm-lock.yaml → `pnpm test`,
# yarn.lock → `yarn test`. Three seeded repos, one case, because the three are one rule —
# the same marker file answered three ways depending on what else the repo committed. A
# runner chosen without consulting the lockfile passes the first sub-check and fails the
# other two, which is exactly the confusion worth catching.
#
# Nothing here needs node installed: the script reads files, it never runs the command it
# prints. `out=$(...) && code=0 || code=$?` is the sibling idiom for capturing stdout and a
# non-zero exit together — command substitution alone would abort the assignment's status.
for runner in npm pnpm yarn; do
  repo="$work/node-$runner"
  mkdir -p "$repo"
  printf '{"scripts":{"test":"jest"}}\n' > "$repo/package.json"
done
printf 'lockfileVersion: 9.0\n' > "$work/node-pnpm/pnpm-lock.yaml"
printf '# yarn lockfile v1\n' > "$work/node-yarn/yarn.lock"

npm_out="$("$DETECT" "$work/node-npm" 2>/dev/null)" && npm_code=0 || npm_code=$?
pnpm_out="$("$DETECT" "$work/node-pnpm" 2>/dev/null)" && pnpm_code=0 || pnpm_code=$?
yarn_out="$("$DETECT" "$work/node-yarn" 2>/dev/null)" && yarn_code=0 || yarn_code=$?

{ [[ "$npm_code" == 0 ]]  && [[ "$npm_out"  == "npm test" ]] \
  && [[ "$pnpm_code" == 0 ]] && [[ "$pnpm_out" == "pnpm test" ]] \
  && [[ "$yarn_code" == 0 ]] && [[ "$yarn_out" == "yarn test" ]]; } \
  && ok || no "package.json scripts.test: bare → npm test, pnpm-lock.yaml → pnpm test, yarn.lock → yarn test (bare exit=$npm_code stdout='$npm_out', pnpm exit=$pnpm_code stdout='$pnpm_out', yarn exit=$yarn_code stdout='$yarn_out')"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
