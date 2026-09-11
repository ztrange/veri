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

# detect <repo-root> -> sets $out to stdout and $code to the exit status. Every case needs
# both halves of the contract — what was printed *and* which of 0 / 3 was returned — and
# capturing them together is fiddly enough to be worth naming once: command substitution
# would otherwise leave $? describing the assignment, so `code=$?` has to come from the
# line immediately after it. stderr is dropped because no case asserts on it.
detect() {  # detect <repo-root> -> runs the script, sets $out/$code
  out="$("$DETECT" "$1" 2>/dev/null)"
  code=$?
}

# matched -> true when the last detect() answered the contract: exit 0 and $want on
# stdout. Every case asserts those same two halves against those same two variables, so
# the pair is spelled out once here instead of at each call site — and a case that reads
# `matched && ok` says what it is checking, where the raw conjunction only said how.
matched() { [[ "$code" == 0 ]] && [[ "$out" == "$want" ]]; }

# note <label> -> appends one parenthesised note to $misread, saying which of a case's
# seeded repos answered wrong and what it answered instead. Three cases below seed several
# repos each and still report as one case, so each has to carry the label along with both
# halves of the mismatch; naming the wording once keeps those three notes identical, which
# is what makes them readable side by side when a case fails on more than one repo.
note() { misread="$misread ($1: exit=$code want 0, stdout='$out' want '$want')"; }

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

detect "$repo"

matched \
  && ok || no ".veri/test-command beats package.json and Makefile, printed verbatim (exit=$code want 0, stdout='$out' want '$want')"

# 2. a package.json carrying a scripts.test entry names the node runner, and which runner is
# decided by the lockfile lying beside it: bare → `npm test`, pnpm-lock.yaml → `pnpm test`,
# yarn.lock → `yarn test`. Three seeded repos, one case, because the three are one rule —
# the same marker file answered three ways depending on what else the repo committed. A
# runner chosen without consulting the lockfile passes the first sub-check and fails the
# other two, which is exactly the confusion worth catching.
#
# Nothing here needs node installed: the script reads files, it never runs the command it
# prints.
#
# The runner name is the whole of what varies — it names the repo, the lockfile to seed and,
# with ` test` appended, the expected stdout — so the loop mentions each one once and the
# three sub-checks stay one case: `misread` collects whichever runners answered wrong, and
# only a run that collected nothing passes.
misread=""
for runner in npm pnpm yarn; do
  want="$runner test"
  repo="$work/node-$runner"
  mkdir -p "$repo"
  printf '{"scripts":{"test":"jest"}}\n' > "$repo/package.json"
  case "$runner" in
    pnpm) printf 'lockfileVersion: 9.0\n' > "$repo/pnpm-lock.yaml" ;;
    yarn) printf '# yarn lockfile v1\n' > "$repo/yarn.lock" ;;
  esac

  detect "$repo"

  matched || note "$runner"
done

[[ -z "$misread" ]] \
  && ok || no "package.json scripts.test: bare → npm test, pnpm-lock.yaml → pnpm test, yarn.lock → yarn test —$misread"

# 3. a Makefile declaring a `test:` target names `make test` — and it does so even when the
# repo also carries a pytest marker, which is the half of this case worth seeding. The two
# markers together are the only way to observe the precedence: on a Makefile-only repo,
# `make test` on stdout says nothing about ordering, because no other rule was in the running.
#
# This is the reordering the issue calls for. Today's SKILL.md tries npm, pytest, make,
# unittest, so this repo would answer `pytest -q`; a repo that wrote a `test` target chose
# it deliberately — very often precisely to wrap the pytest invocation with whatever else
# the suite needs — so the target wins and pytest.ini is left to answer for repos that
# wrote no target at all.
#
# The pytest marker is a bare pytest.ini: an empty file is enough, since rule 4 keys on the
# file existing, not on anything inside it. No Makefile, no pytest and no python are needed
# to run this — the script reads the two filenames and never executes what it prints.
want='make test'
repo="$work/make-over-pytest"
mkdir -p "$repo"
printf 'test:\n\techo hi\n' > "$repo/Makefile"
: > "$repo/pytest.ini"

detect "$repo"

matched \
  && ok || no "Makefile with a test: target beats pytest.ini (exit=$code want 0, stdout='$out' want '$want')"

# 4. a python repo that declares pytest configuration names `pytest -q`. Two spellings are
# one rule — a bare `pytest.ini`, or a `pyproject.toml` carrying a `[tool.pytest` section —
# so they are two seeded repos inside one case, the same way the three node runners are.
# Either spelling is a repo saying "pytest runs here", and `-q` because the conductor reads
# the exit status, not the dots.
#
# The `pytest.ini` repo seeds an empty file on purpose: the rule keys on the filename, and a
# repo whose pytest settings all live in command-line flags or tox still commits the empty
# marker. The `pyproject.toml` repo needs the section header and nothing else, because
# pyproject.toml alone means only "this is a python project" — packaging metadata is no
# claim about the test runner — so it is the `[tool.pytest` section that has to be found
# inside the file. `ini_options` is the suffix real repos write, and including it checks the
# rule matches the prefix rather than demanding the whole bare header.
#
# Neither repo needs pytest or python installed: the script reads these two files and never
# runs the command it prints.
want='pytest -q'
misread=""
for marker in pytest.ini pyproject.toml; do
  repo="$work/py-$marker"
  mkdir -p "$repo"
  case "$marker" in
    pytest.ini)     : > "$repo/pytest.ini" ;;
    pyproject.toml) printf '[tool.pytest.ini_options]\naddopts = "-ra"\n' > "$repo/pyproject.toml" ;;
  esac

  detect "$repo"

  matched || note "$marker"
done

[[ -z "$misread" ]] \
  && ok || no "pytest.ini, or pyproject.toml with a [tool.pytest section, yields pytest -q —$misread"

# 5. the two compiled stacks each name their toolchain's own runner: a `go.mod` yields
# `go test ./...`, a `Cargo.toml` yields `cargo test`. One case, two seeded repos, the same
# shape as the node runners and the two pytest spellings — two markers answering with two
# different commands is still one rule, "the manifest file names the stack's test runner".
#
# Both markers are the manifest at the repo root that its toolchain requires, so the
# filename alone is the whole claim and an empty file is enough to make it — unlike
# pyproject.toml above, neither name belongs to any other kind of project. `./...` is go's
# own spelling for "every package beneath here", without which `go test` would run only the
# root package and quietly skip the rest of the suite; `cargo test` already walks the whole
# crate, so it needs no argument.
#
# Neither repo needs go or rust installed: the script reads the two filenames and never
# runs the command it prints.
misread=""
for marker in go.mod Cargo.toml; do
  case "$marker" in
    go.mod)     want='go test ./...' ;;
    Cargo.toml) want='cargo test' ;;
  esac
  repo="$work/compiled-$marker"
  mkdir -p "$repo"
  : > "$repo/$marker"

  detect "$repo"

  matched || note "$marker"
done

[[ -z "$misread" ]] \
  && ok || no "go.mod yields go test ./..., Cargo.toml yields cargo test —$misread"

# 7. the last rule before giving up: a repo whose only sign of a suite is a `tests/`
# directory holding `test_*.py` names `python3 -m unittest discover -q`. This is the
# stdlib fallback for a python project that committed no runner configuration at all —
# no pytest.ini, no pyproject.toml, no Makefile — which is why the seeded repo carries
# the test file and nothing else: any other marker would have been answered by a rule
# above, and the repo would never reach this one.
#
# Unlike every rule before it, the marker is not a file at a known path but a *pattern*
# inside a directory, so the file is named `test_foo.py` rather than left as an empty
# `tests/` — `discover` finds cases by that filename pattern, and a `tests/` directory of
# fixtures or helpers is no claim that a suite lives there. Its contents are irrelevant:
# the script matches the name and never imports or runs the file.
#
# `python3` and not `python`, because `python` is absent on a modern macOS and ambiguous
# where it exists; `-m unittest discover` because there is no runner script to call; `-q`
# to match the other rules, the conductor reading the exit status rather than the dots.
want='python3 -m unittest discover -q'
repo="$work/unittest-only"
mkdir -p "$repo/tests"
printf 'import unittest\n' > "$repo/tests/test_foo.py"

detect "$repo"

matched \
  && ok || no "a tests/ directory of test_*.py with no other marker yields python3 -m unittest discover -q (exit=$code want 0, stdout='$out' want '$want')"

# 8. the fall-through: a repo that matches no rule at all prints nothing and exits 3. This
# is the one case that asserts the *other* half of the contract, so it cannot use
# `matched` — that helper spells out the answering half, exit 0 with $want on stdout, and
# here both halves are the opposite: empty stdout, and 3 rather than 0. 3 is "nothing to
# do", not an error, and the conductor branches on it by asking the human, so a script
# that failed with 1 or 2 here would be read as broken plumbing instead of an honest
# "I cannot tell".
#
# The seeded repo is not an empty directory on purpose. An empty one would pass against a
# script that had no rules at all, so it says nothing about the rules having been asked and
# having declined; a repo with real content and no marker does. Both files are near misses,
# each one a thing a rule could plausibly have keyed on and must not: `README.md` mentions
# the word test in prose, and `src/main.c` is source under a directory named for source —
# neither is a runner configuration, and neither is `tests/test_*.py`.
#
# Nothing is printed because stdout is what the conductor captures as the command: a
# diagnostic written there would be run as if it were one, which is why the script keeps
# any explanation on stderr and the case checks stdout is empty rather than merely not the
# command.
repo="$work/no-markers"
mkdir -p "$repo/src"
printf '# demo\n\nRun the test suite however you like.\n' > "$repo/README.md"
printf 'int main(void) { return 0; }\n' > "$repo/src/main.c"

detect "$repo"

[[ "$code" == 3 ]] && [[ -z "$out" ]] \
  && ok || no "a repo matching nothing prints nothing and exits 3 (exit=$code want 3, stdout='$out' want '')"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
