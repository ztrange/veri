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
# Each case seeds a throwaway scratch repo with only the marker files it is about:
# the script inspects files, it never runs the command, so no toolchain is needed.
# Sibling style: classify-bail.test.sh, ensure-run-state-ignored.test.sh.
#
# Run: scripts/tests/detect-test-command.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
DETECT="$HERE/../detect-test-command.sh"
source "$HERE/lib/harness.sh"
work="$(scratch_dir)"

detect() {  # detect <args...> -> runs the script, sets $out/$code
  out="$("$DETECT" "$@" 2>/dev/null)"
  code=$?
}

matched() { [[ "$code" == 0 ]] && [[ "$out" == "$want" ]]; }

note() { misread="$misread ($1: exit=$code want 0, stdout='$out' want '$want')"; }

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

want='make docs-test'
repo="$work/issue-inline-backticks"
body="$work/issue-inline-backticks-body.md"
mkdir -p "$repo"
printf 'test:\n\techo hi\n' > "$repo/Makefile"
printf '## Notes\n\n`docs/wt/app.js`, `docs/wt/style.css`. Test command: `make docs-test`. More prose.\n' > "$body"

detect --issue "$body" "$repo"

matched \
  && ok || no "a mid-line Test command: followed by a backtick span answers the span alone, dropping the prose on either side (exit=$code want 0, stdout='$out' want '$want')"

want='make docs-test'
repo="$work/issue-linestart-backticks"
body="$work/issue-linestart-backticks-body.md"
mkdir -p "$repo"
printf 'test:\n\techo hi\n' > "$repo/Makefile"
printf '## Notes\n\nTest command: `make docs-test`. `docs/walkthrough.html` is GENERATED — never hand-edit it.\n' > "$body"

detect --issue "$body" "$repo"

matched \
  && ok || no "a line starting Test command: followed by a backtick span answers the span alone, not the rest of the line (exit=$code want 0, stdout='$out' want '$want')"

misread=""
for shape in bare silent; do
  repo="$work/unwrap-untouched-$shape"
  body="$work/unwrap-untouched-$shape-body.md"
  mkdir -p "$repo"
  printf 'test:\n\techo hi\n' > "$repo/Makefile"
  case "$shape" in
    bare)
      printf '## Notes\n\nTest command: bin/run --all\n' > "$body"
      want='bin/run --all' ;;
    silent)
      printf '## Notes\n\nNothing here names a run command.\n' > "$body"
      want='make test' ;;
  esac

  detect --issue "$body" "$repo"

  matched || note "$shape"
done

[[ -z "$misread" ]] \
  && ok || no "a bare Test command: at line start still answers verbatim, and a body with no marker still falls through to the old precedence —$misread"

want='make docs-test'
misread=""
repo="$work/real-issue-bodies"
mkdir -p "$repo"
printf 'test:\n\techo hi\n' > "$repo/Makefile"

for n in 71 75 80 123; do
  detect --issue "$HERE/fixtures/detect-test-command/issue-$n.md" "$repo"

  matched || note "#$n"
done

[[ -z "$misread" ]] \
  && ok || no "the real bodies of #71, #75, #80 and #123 each answer make docs-test —$misread"

want='make test'
repo="$work/quoted-marker"
body="$work/quoted-marker-body.md"
mkdir -p "$repo/.veri"
printf '%s\n' 'bin/run-suite --all --strict' > "$repo/.veri/test-command"
printf '# Leaves run one suite instead of the full one\n\nSince #120 a leaf takes its command from the issue body: the `Test command:` line names it, and #131 made that line count mid-sentence.\n\n## Notes\n\nTest command: %s\n' "$want" > "$body"

detect --issue "$body" "$repo"

matched \
  && ok || no "a marker quoted inside a backtick span does not answer, and the later line stating it with make test does (exit=$code want 0, stdout='$out' want '$want')"

want='bin/run-suite --all --strict'
misread=""
repo="$work/only-quoted-marker"
mkdir -p "$repo/.veri"
printf '%s\n' "$want" > "$repo/.veri/test-command"

for shape in quoted absent; do
  body="$work/only-quoted-marker-$shape-body.md"
  case "$shape" in
    quoted) phrase='the `Test command:` line names it' ;;
    absent) phrase='a line in its Notes names it' ;;
  esac
  printf '# Leaves run one suite instead of the full one\n\nSince #120 a leaf takes its command from the issue body: %s, and #131 made that line count mid-sentence.\n\n## Notes\n\nFiles: `skills/tdd/scripts/detect-test-command.sh`.\n' "$phrase" > "$body"

  detect --issue "$body" "$repo"

  matched || note "$shape"
done

[[ -z "$misread" ]] \
  && ok || no "a body whose only marker sits inside a backtick span falls through to the next rule, exactly as a body with no marker does —$misread"

want='make docs-test'
repo="$work/quoted-then-stated"
body="$work/quoted-then-stated-body.md"
mkdir -p "$repo"
printf 'test:\n\techo hi\n' > "$repo/Makefile"
printf '## Notes\n\nA leaf takes its command from the `Test command:` line, so: Test command: `%s`. More prose.\n' "$want" > "$body"

detect --issue "$body" "$repo"

matched \
  && ok || no "a line carrying a quoted marker and then a stated one answers the stated command (exit=$code want 0, stdout='$out' want '$want')"

want='make test'
repo="$work/quoted-docs-command"
body="$work/quoted-docs-command-body.md"
mkdir -p "$repo/.veri"
printf '%s\n' 'bin/run-suite --all --strict' > "$repo/.veri/test-command"
printf '# Rule 0 answers a development issue with its own suite\n\nA docs issue writes `Test command: make docs-test` in its Notes, so every leaf on it runs the docs suite. This issue is not a docs issue.\n\n## Notes\n\nFiles: `skills/tdd/scripts/detect-test-command.sh`.\n\nTest command: %s\n' "$want" > "$body"

detect --issue "$body" "$repo"

matched \
  && ok || no "a development issue quoting a docs issue's marker with make docs-test answers the make test its Notes state (exit=$code want 0, stdout='$out' want '$want')"

want='make test'
repo="$work/issue-144-body"
mkdir -p "$repo/.veri"
printf '%s\n' 'bin/run-suite --all --strict' > "$repo/.veri/test-command"

detect --issue "$HERE/fixtures/detect-test-command/issue-144.md" "$repo"

matched \
  && ok || no "#144's real body, whose line 3 quotes the marker and whose line 65 states it, answers make test (exit=$code want 0, stdout='$out' want '$want')"

want='bin/run-suite --all --strict'
repo="$work/override"
mkdir -p "$repo/.veri"
printf '%s\n' "$want" > "$repo/.veri/test-command"
printf '{"scripts":{"test":"jest"}}\n' > "$repo/package.json"
printf 'test:\n\techo hi\n' > "$repo/Makefile"

detect "$repo"

matched \
  && ok || no ".veri/test-command beats package.json and Makefile, printed verbatim (exit=$code want 0, stdout='$out' want '$want')"

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

want='make test'
repo="$work/make-over-pytest"
mkdir -p "$repo"
printf 'test:\n\techo hi\n' > "$repo/Makefile"
: > "$repo/pytest.ini"

detect "$repo"

matched \
  && ok || no "Makefile with a test: target beats pytest.ini (exit=$code want 0, stdout='$out' want '$want')"

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

repo="$work/setupcfg-no-pytest"
mkdir -p "$repo"
printf '[metadata]\nname = demo\n' > "$repo/setup.cfg"

detect "$repo"

[[ "$code" == 3 ]] && [[ -z "$out" ]] \
  && ok || no "a setup.cfg with no [tool:pytest] section prints nothing and exits 3 (exit=$code want 3, stdout='$out' want '')"

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

want='python3 -m unittest discover -q'
repo="$work/unittest-only"
mkdir -p "$repo/tests"
printf 'import unittest\n' > "$repo/tests/test_foo.py"

detect "$repo"

matched \
  && ok || no "a tests/ directory of test_*.py with no other marker yields python3 -m unittest discover -q (exit=$code want 0, stdout='$out' want '$want')"

repo="$work/no-markers"
mkdir -p "$repo/src"
printf '# demo\n\nRun the test suite however you like.\n' > "$repo/README.md"
printf 'int main(void) { return 0; }\n' > "$repo/src/main.c"

detect "$repo"

[[ "$code" == 3 ]] && [[ -z "$out" ]] \
  && ok || no "a repo matching nothing prints nothing and exits 3 (exit=$code want 3, stdout='$out' want '')"

misread=""
body="$work/tier-issue-body.md"
printf '## Notes\n\nTest command: bin/issue-suite\n' > "$body"

for shape in override npm pnpm yarn make pytest.ini pyproject.toml setup.cfg go.mod Cargo.toml unittest issue; do
  repo="$work/untiered-$shape"
  mkdir -p "$repo"
  printf '# demo\n\nveri: fast tests: bin/fast-suite\nveri: all tests: bin/all-suite\n' > "$repo/CLAUDE.md"
  args=("$repo")
  case "$shape" in
    override)
      mkdir -p "$repo/.veri"
      printf '%s\n' 'bin/run-suite --all --strict' > "$repo/.veri/test-command"
      want='bin/run-suite --all --strict' ;;
    npm|pnpm|yarn)
      printf '{"scripts":{"test":"jest"}}\n' > "$repo/package.json"
      case "$shape" in
        pnpm) printf 'lockfileVersion: 9.0\n' > "$repo/pnpm-lock.yaml" ;;
        yarn) printf '# yarn lockfile v1\n' > "$repo/yarn.lock" ;;
      esac
      want="$shape test" ;;
    make)
      printf 'test:\n\techo hi\n' > "$repo/Makefile"
      want='make test' ;;
    pytest.ini)     : > "$repo/pytest.ini" ; want='pytest -q' ;;
    pyproject.toml) printf '[tool.pytest.ini_options]\naddopts = "-ra"\n' > "$repo/pyproject.toml" ; want='pytest -q' ;;
    setup.cfg)      printf '[tool:pytest]\naddopts = -ra\n' > "$repo/setup.cfg" ; want='pytest -q' ;;
    go.mod)         : > "$repo/go.mod" ; want='go test ./...' ;;
    Cargo.toml)     : > "$repo/Cargo.toml" ; want='cargo test' ;;
    unittest)
      mkdir -p "$repo/tests"
      printf 'import unittest\n' > "$repo/tests/test_foo.py"
      want='python3 -m unittest discover -q' ;;
    issue)
      printf 'test:\n\techo hi\n' > "$repo/Makefile"
      args=(--issue "$body" "$repo")
      want='bin/issue-suite' ;;
  esac

  detect "${args[@]}"

  matched || note "$shape"
done

[[ -z "$misread" ]] \
  && ok || no "no --tier: CLAUDE.md's veri: fast/all tests: lines leave every single-command answer as today —$misread"

repo="$work/untiered-markers-only"
mkdir -p "$repo"
printf '# demo\n\nveri: fast tests: bin/fast-suite\nveri: all tests: bin/all-suite\n' > "$repo/CLAUDE.md"

detect "$repo"

[[ "$code" == 3 ]] && [[ -z "$out" ]] \
  && ok || no "no --tier: a repo whose only markers are CLAUDE.md's veri: fast/all tests: lines prints nothing and exits 3 (exit=$code want 3, stdout='$out' want '')"

misread=""
repo="$work/tiered-both"
mkdir -p "$repo"
printf 'test:\n\techo hi\n' > "$repo/Makefile"
printf '# demo\n\nveri: fast tests: bin/fast-suite  --only "unit tier" -q\nveri: all tests: bin/all-suite  --every "suite there is" -v\n' > "$repo/CLAUDE.md"

for tier in fast all; do
  case "$tier" in
    fast) want='bin/fast-suite  --only "unit tier" -q' ;;
    all)  want='bin/all-suite  --every "suite there is" -v' ;;
  esac

  detect --tier "$tier" "$repo"

  matched || note "$tier"
done

[[ -z "$misread" ]] \
  && ok || no "--tier fast/all: both CLAUDE.md markers declared, each tier prints its own marker's command byte for byte —$misread"

misread=""
repo="$work/tiered-anywhere-quoted"
mkdir -p "$repo"
printf 'test:\n\techo hi\n' > "$repo/Makefile"
{
  printf '# demo\n\n'
  printf 'Leaves never read `veri: fast tests: bin/quoted-fast` as a declaration.\n'
  printf 'In this repo the fast tier is veri: fast tests: `bin/real-fast -q`. More prose.\n'
  printf 'Nor `veri: all tests: bin/quoted-all` either.\n'
  printf 'And the full suite is veri: all tests: `bin/real-all -v`. More prose.\n'
} > "$repo/CLAUDE.md"

for tier in fast all; do
  case "$tier" in
    fast) want='bin/real-fast -q' ;;
    all)  want='bin/real-all -v' ;;
  esac

  detect --tier "$tier" "$repo"

  matched || note "$tier"
done

[[ -z "$misread" ]] \
  && ok || no "--tier fast/all: a CLAUDE.md marker is recognised mid-line and one inside a backtick span is skipped, as the issue override marker is —$misread"

misread=""
repo="$work/tierless-claude-md"
mkdir -p "$repo"
printf 'test:\n\techo hi\n' > "$repo/Makefile"
printf '# demo\n\nThe fast tests and all tests are the same here.\n' > "$repo/CLAUDE.md"
repo="$work/tierless-no-claude-md"
mkdir -p "$repo/.veri"
printf '%s\n' 'bin/run-suite --all --strict' > "$repo/.veri/test-command"

for shape in claude-md no-claude-md; do
  case "$shape" in
    claude-md)    repo="$work/tierless-claude-md" ;    want='make test' ;;
    no-claude-md) repo="$work/tierless-no-claude-md" ; want='bin/run-suite --all --strict' ;;
  esac
  for tier in fast all; do
    detect --tier "$tier" "$repo"

    matched || note "$shape, $tier"
  done
done

[[ -z "$misread" ]] \
  && ok || no "--tier fast/all: with neither CLAUDE.md marker declared, both tiers print the single command the precedence chain picks —$misread"

repo="$work/tiered-all-only"
mkdir -p "$repo"
printf 'test:\n\techo hi\n' > "$repo/Makefile"
printf '# demo\n\nveri: all tests: bin/all-only-suite --every -v\n' > "$repo/CLAUDE.md"
want='make test'
detect --tier fast "$repo"
matched \
  && ok || no "--tier fast: with only CLAUDE.md's veri: all tests: declared, fast falls back to the single-command chain (exit=$code want 0, stdout='$out' want '$want')"

misread=""
body="$work/tiered-issue-body.md"
printf '## Notes\n\nTest command: bin/issue-suite --only "this run" -q\n' > "$body"
repo="$work/tiered-issue-both"
mkdir -p "$repo"
printf 'test:\n\techo hi\n' > "$repo/Makefile"
printf '# demo\n\nveri: fast tests: bin/fast-suite --unit -q\nveri: all tests: bin/all-suite --every -v\n' > "$repo/CLAUDE.md"
repo="$work/tiered-issue-all-only"
mkdir -p "$repo"
printf 'test:\n\techo hi\n' > "$repo/Makefile"
printf '# demo\n\nveri: all tests: bin/all-suite --every -v\n' > "$repo/CLAUDE.md"

for shape in both all-only; do
  repo="$work/tiered-issue-$shape"
  for tier in fast all; do
    case "$shape,$tier" in
      both,fast)     want='bin/fast-suite --unit -q' ;;
      all-only,fast) want='make test' ;;
      *,all)         want='bin/issue-suite --only "this run" -q' ;;
    esac

    detect --tier "$tier" --issue "$body" "$repo"

    matched || note "$shape, $tier"
  done
done

[[ -z "$misread" ]] \
  && ok || no "--tier all/fast with --issue: the issue's Test command: line answers all ahead of CLAUDE.md's veri: all tests:, while fast still answers from veri: fast tests: or the single-command chain —$misread"

misread=""
ROOT="$(cd "$HERE/../../../.." && pwd)"
for tier in fast all; do
  case "$tier" in
    fast) want='make unit' ;;
    all)  want='make test' ;;
  esac

  detect --tier "$tier" "$ROOT"

  matched || note "veri, $tier"
done

[[ -z "$misread" ]] \
  && ok || no "--tier fast/all: run against veri's own repo root, fast prints make unit and all prints make test, from veri's CLAUDE.md —$misread"

finish
