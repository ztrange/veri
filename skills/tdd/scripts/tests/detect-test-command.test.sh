#!/usr/bin/env bash
# Unit tests for scripts/detect-test-command.sh — prints the one command that runs the
# full suite of the repo at [repo-root] on stdout and exits 0; prints nothing and exits 3
# when it cannot decide (the conductor then asks the human).
#
# Contract under test (issues #39, #120):
#   detect-test-command.sh [--issue <body-file>] [repo-root]   (root default: .)
#   precedence, first match wins: the issue body's own `Test command:` line,
#   .veri/test-command override, npm/pnpm/yarn, make, pytest, go, cargo, unittest —
#   otherwise exit 3.
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

# detect <args...> -> sets $out to stdout and $code to the exit status. Every case needs
# both halves of the contract — what was printed *and* which of 0 / 3 was returned — and
# capturing them together is fiddly enough to be worth naming once: command substitution
# would otherwise leave $? describing the assignment, so `code=$?` has to come from the
# line immediately after it. stderr is dropped because no case asserts on it.
#
# The whole argument list is forwarded rather than a single repo root, because the script
# is called two ways: with the root alone, and with `--issue <body-file>` before it.
detect() {  # detect <args...> -> runs the script, sets $out/$code
  out="$("$DETECT" "$@" 2>/dev/null)"
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

# 0. an issue that names its own test command outranks everything, the override file
# included. `--issue <body-file>` hands the script the issue body the conductor has already
# read, and the first line of it matching `Test command:` is the answer, printed verbatim.
#
# The seeded repo arms every rule below it: a `.veri/test-command`, which until now beat
# every inference; a package.json with a test script; a Makefile with a test target. So an
# answer of the issue's command can only mean the body was consulted ahead of all three —
# on a repo with no markers, any of them could have been what answered instead.
#
# Two `Test command:` lines are seeded because the claim is about the *first*: a body that
# names the command again further down — in a note, a quotation, a later section — must not
# have the last mention win. The line that must answer carries flags no rule could ever
# infer, so any normalising or re-quoting of it shows up in stdout.
#
# The body is a file rather than the issue text on stdin because that is what the conductor
# has: it saves the issue body to `.tdd/issue-<n>.md` in preflight, and every leaf is
# launched with that path.
want='bin/docs-suite --only docs --strict'
repo="$work/issue-command"
body="$work/issue-command-body.md"
mkdir -p "$repo/.veri"
printf '%s\n' 'bin/run-suite --all --strict' > "$repo/.veri/test-command"
printf '{"scripts":{"test":"jest"}}\n' > "$repo/package.json"
printf 'test:\n\techo hi\n' > "$repo/Makefile"
printf '## Notes\n\nTest command: %s\n\nTest command: make other-test\n' "$want" > "$body"

detect --issue "$body" "$repo"

matched \
  && ok || no "--issue: the body's first Test command: line beats .veri/test-command and every inference, printed verbatim (exit=$code want 0, stdout='$out' want '$want')"

# 0b. the other half of rule 0: when the issue names no command, the rule steps aside and the
# answer is exactly the one veri gave before `--issue` existed. Case 0 says the line wins when
# it is there; this says nothing else moved when it is not — which is the half a fix can
# quietly get wrong, by answering "" for a silent body, or by exiting 3 once the body has been
# read, or by consuming the `--issue <file>` words and then reading the repo root out of the
# wrong argument.
#
# Three seeded repos, one case, because "today's precedence, unchanged" is a single claim and
# the only way to observe it is at each of its three outcomes: the override file still wins
# (a `.veri/test-command` with a package.json armed beside it), an inference still fires where
# there is no override (a Makefile `test:` target over a pytest.ini), and a repo with no marker
# at all still prints nothing and exits 3. A rule 0 that swallowed the answer would pass on
# one of the three and fail on the others.
#
# Each repo is asked twice, once per spelling the step names — `--issue <body-file>` with a
# body that carries no `Test command:` line, and no `--issue` at all — so the label in
# `misread` carries the argument form as well as the repo. The bare form is the pre-`--issue`
# baseline the `--issue` form must equal, and having both side by side is what makes a
# divergence between them legible.
#
# The body mentions a command only in prose. That is the near miss worth seeding: a rule that
# looked for the *command* anywhere in the body rather than for a line opening with the marker
# would answer `make docs-test` here, on an issue that never asked for it.
#
# `note` is not reused: it spells `want 0` into its wording, and the third repo's want is exit
# 3 with empty stdout. `matched` is likewise the answering half only, so both halves are
# asserted here against a per-repo `wantcode`, the way cases 4b and 8 assert theirs directly.
misread=""
body="$work/silent-body.md"
printf '## Notes\n\nNo line here names the run command; `make docs-test` appears in prose only.\n' > "$body"

for shape in override inference none; do
  repo="$work/silent-$shape"
  case "$shape" in
    override)
      mkdir -p "$repo/.veri"
      printf '%s\n' 'bin/run-suite --all --strict' > "$repo/.veri/test-command"
      printf '{"scripts":{"test":"jest"}}\n' > "$repo/package.json"
      want='bin/run-suite --all --strict' ; wantcode=0 ;;
    inference)
      mkdir -p "$repo"
      printf 'test:\n\techo hi\n' > "$repo/Makefile"
      : > "$repo/pytest.ini"
      want='make test' ; wantcode=0 ;;
    none)
      mkdir -p "$repo/src"
      printf '# demo\n\nRun the test suite however you like.\n' > "$repo/README.md"
      printf 'int main(void) { return 0; }\n' > "$repo/src/main.c"
      want='' ; wantcode=3 ;;
  esac

  detect --issue "$body" "$repo"
  [[ "$code" == "$wantcode" ]] && [[ "$out" == "$want" ]] \
    || misread="$misread ($shape, --issue: exit=$code want $wantcode, stdout='$out' want '$want')"

  detect "$repo"
  [[ "$code" == "$wantcode" ]] && [[ "$out" == "$want" ]] \
    || misread="$misread ($shape, no --issue: exit=$code want $wantcode, stdout='$out' want '$want')"
done

[[ -z "$misread" ]] \
  && ok || no "a body with no Test command: line, and no --issue at all, both leave today's precedence untouched: override file, then inferences, exit 3 —$misread"

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

# 4. a python repo that declares pytest configuration names `pytest -q`. The three spellings
# pytest documents are one rule — a bare `pytest.ini`, a `pyproject.toml` carrying a
# `[tool.pytest` section, or a `setup.cfg` carrying a `[tool:pytest]` one — so they are three
# seeded repos inside one case, the same way the three node runners are. Each spelling is a
# repo saying "pytest runs here", and `-q` because the conductor reads the exit status, not
# the dots.
#
# The `pytest.ini` repo seeds an empty file on purpose: the rule keys on the filename, and a
# repo whose pytest settings all live in command-line flags or tox still commits the empty
# marker. The other two need the section header and nothing else, because neither filename is
# a claim about the test runner on its own — both are packaging metadata any python project
# may carry — so the header has to be found inside the file. Each carries a second line under
# it, so the header is not also the last byte of the file. `ini_options` is the suffix real
# pyproject.toml repos write, and including it checks the rule matches the prefix rather than
# demanding the whole bare header; setup.cfg's header is pytest's own colon spelling for that
# file, `[tool:pytest]`, not the dot pyproject.toml uses.
#
# No repo here needs pytest or python installed: the script reads these three files and never
# runs the command it prints.
want='pytest -q'
misread=""
for marker in pytest.ini pyproject.toml setup.cfg; do
  repo="$work/py-$marker"
  mkdir -p "$repo"
  case "$marker" in
    pytest.ini)     : > "$repo/pytest.ini" ;;
    pyproject.toml) printf '[tool.pytest.ini_options]\naddopts = "-ra"\n' > "$repo/pyproject.toml" ;;
    setup.cfg)      printf '[tool:pytest]\naddopts = -ra\n' > "$repo/setup.cfg" ;;
  esac

  detect "$repo"

  matched || note "$marker"
done

[[ -z "$misread" ]] \
  && ok || no "pytest.ini, or pyproject.toml with a [tool.pytest section, or setup.cfg with a [tool:pytest] one, yields pytest -q —$misread"

# 4b. the other half of rule 4's setup.cfg spelling: a `setup.cfg` with no `[tool:pytest]`
# section is not a pytest marker, so the repo prints nothing and exits 3. The case above
# says the header is found; this one says the *filename* is not what answers. A rule that
# keyed on `setup.cfg` existing — the way it legitimately keys on `pytest.ini` existing —
# passes case 4 and fails here, and that is the confusion worth catching: setup.cfg is
# packaging metadata any python project may carry, whatever runs its suite.
#
# `[metadata]` is what such a repo really holds, and it is seeded with a key under it so
# the file is not merely a bare header. Nothing else is seeded: any other marker would be
# answered by another rule and the repo would never reach rule 4's verdict at all.
#
# Both halves are the opposite of `matched`'s — empty stdout, and 3 rather than 0 — so this
# asserts them directly, the same way case 8 does. 3 is "nothing to do", not an error: it
# is the conductor's cue to ask the human, which is the right outcome for a repo that never
# said pytest runs here.
repo="$work/setupcfg-no-pytest"
mkdir -p "$repo"
printf '[metadata]\nname = demo\n' > "$repo/setup.cfg"

detect "$repo"

[[ "$code" == 3 ]] && [[ -z "$out" ]] \
  && ok || no "a setup.cfg with no [tool:pytest] section prints nothing and exits 3 (exit=$code want 3, stdout='$out' want '')"

# 4c. the setup.cfg spelling sits where the rest of rule 4 sits, and the only way to observe
# that is to seed it against a neighbour on each side. Case 4 says a lone setup.cfg answers
# `pytest -q`; a lone repo says nothing about ordering, because no other rule was in the
# running. So: one repo pairs it with the rule above (a Makefile `test:` target, which must
# still win) and one pairs it with the rule below (a `go.mod`, which must still lose). Two
# seeded repos, one case, the same shape as the node runners and the three pytest spellings —
# "the new spelling changed no precedence" is a single claim about a single position.
#
# This is the half a fix can quietly get wrong: recognising setup.cfg in a rule of its own,
# placed before make or after go, passes case 4 and fails here. Both repos carry the header
# inside setup.cfg rather than the bare filename, since that is what case 4b established is
# required to make the claim at all.
#
# No Makefile, no go and no pytest are needed to run this: the script reads these filenames
# and the one header, and never executes the command it prints.
misread=""
for other in Makefile go.mod; do
  repo="$work/setupcfg-vs-$other"
  mkdir -p "$repo"
  printf '[tool:pytest]\naddopts = -ra\n' > "$repo/setup.cfg"
  case "$other" in
    Makefile) printf 'test:\n\techo hi\n' > "$repo/Makefile" ; want='make test' ;;
    go.mod)   : > "$repo/go.mod"                             ; want='pytest -q' ;;
  esac

  detect "$repo"

  matched || note "$other"
done

[[ -z "$misread" ]] \
  && ok || no "a [tool:pytest] setup.cfg loses to a Makefile test: target and beats go.mod —$misread"

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
