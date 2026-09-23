#!/usr/bin/env bash
# Tests for scripts/run-verdict.sh — the verdict launcher, the one command a conductor runs
# under `supervise.sh verdict-<phase>` in place of the `bash -c "…"` string SKILL.md spelled
# out for months (#426).
#
# Why it exists: every documented verifier launch inlined the step's own title into a
# SINGLE-QUOTED argument inside a DOUBLE-QUOTED `bash -c` command string —
# `… bash -c "$S/verify.sh --step '<STEP>' red …"` — so a title carrying an apostrophe closed
# that `'…'` early and the shell never recovered:
#
#     bash: -c: unexpected EOF while looking for matching `''
#
# That is not a syntax curiosity. On the #424 run the failed launch still wrote `1` into
# `.tdd/verdict-red.exit`, and `1` is the code CLAUDE.md reserves for a real answer — the
# verifier said REJECT — so the conductor spent a revise attempt arguing with a working test.
# A launcher script is what takes the title out of shell text and into argv, where an
# apostrophe is a character like any other: the caller passes it as one argument, and it
# arrives at `verify.sh` as one argument, never re-parsed by a second shell on the way.
#
# Contract under test, this suite's one criterion:
#   Run as `run-verdict.sh --step <title> <phase> <spec> <test-path> <target>` with a <title>
#   containing an apostrophe, it runs its sibling `verify.sh` and that title reaches it whole,
#   as a single argument, byte-identical to the one it was given.
#
# The call shape is verify.sh's own, deliberately: the launcher stands where `verify.sh` used
# to stand on the command line, so a reader comparing the launch line against the verifier's
# usage sees the same arguments in the same order rather than a second convention to learn.
#
# Driven against a STUB verify.sh (no claude, no leaf, no supervisor): the launcher resolves
# its verifier as a sibling, so the case runs a copy of the scripts directory whose verify.sh
# records the argv it was handed, one argument per line, and returns a reason. What the
# assertion reads is that record — the arguments the verifier was actually called with —
# which is the observable the criterion names. Nothing here waits on time, a network or a
# model.
#
# Run: scripts/tests/run-verdict.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
SCRIPTS="$(cd "$HERE/.." && pwd)"

# The launcher's own name, once — the way VERIFIER below names the verifier's — and the paths
# built from it: the repository-relative one a failure message quotes, and the resolved one the
# probes look for. Built rather than spelled at each use so no message can name a file the
# probes did not look for, and so the staged copy the run invokes is that same name again.
LAUNCHER_NAME='run-verdict.sh'
LAUNCHER="skills/tdd/scripts/$LAUNCHER_NAME"
LAUNCHER_PATH="$SCRIPTS/$LAUNCHER_NAME"

# The verifier the launcher is supposed to reach, named once: the stub is written under this
# name, and the failure messages spell it.
VERIFIER='verify.sh'

# The step title under test. A real ledger line, in the repository's own voice, carrying the
# one character that broke the old launch — the apostrophe in "shell's". It is the fixture and
# the expected value at once: what the launcher is given is what the verifier must receive.
STEP="A background process is killed by the pid recorded when it started, never by that shell's own job spec"

pass=0 fail=0

# report <name> — close a case whose probes collected into the `problems` array: an empty
# array is a pass, otherwise one FAIL line for the case and one indented line per problem, so
# the output says which half of the contract broke rather than just that the case did. Same
# idiom as claude-md-counts.test.sh.
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

# flat <text> — one line of it, for a failure message: newlines become slashes so a recorded
# argv or a launcher's whole output quoted inside an indented problem line stays one line.
flat() { local s="$1"; printf '%s' "${s//$'\n'/\/}"; }

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

# probe_launcher_is_there — the premise every probe below rests on, and the one that answers
# while the launcher does not exist yet. Returns non-zero so the case stops here rather than
# reporting on a run it never made.
probe_launcher_is_there() {
  [[ -f "$LAUNCHER_PATH" ]] || {
    problems+=("there is no verdict launcher at $LAUNCHER, so a step title still reaches $VERIFIER through a bash -c command string and an apostrophe in it kills the launch")
    return 1
  }
  [[ -x "$LAUNCHER_PATH" ]] || {
    problems+=("$LAUNCHER is not executable, so a conductor cannot launch it under the supervisor")
    return 1
  }
}

# stage — build the tree the launcher runs in and leave the run's cwd in `run`, the recorded
# argv path in `argv_file`.
#
# The scripts directory is copied whole (its libs and prompts with it) rather than the
# launcher alone, because what a script here may reach for through its own directory is its
# business and not this suite's; the ONE file that is not the real thing is `verify.sh`, which
# is replaced by the stub. The stub is `#!/bin/sh` for the reason #322 gives — a stub is
# forked per case and bash 5 starts three times slower than sh.
stage() {
  scripts="$work/scripts"
  mkdir -p "$scripts" || return 1
  cp "$SCRIPTS"/*.sh "$scripts"/ 2>/dev/null
  for d in lib prompts; do
    if [[ -d "$SCRIPTS/$d" ]]; then cp -R "$SCRIPTS/$d" "$scripts/$d"; fi
  done

  argv_file="$work/verifier.argv"
  cat > "$scripts/$VERIFIER" <<'STUB'
#!/bin/sh
# Stub verifier: record the argv handed to it, one argument per line, and answer like a
# verifier that passed — what this case reads is the record, not the verdict.
for a in "$@"; do printf '%s\n' "$a"; done > "$VERI_STUB_ARGV"
printf 'the test pins the criterion and fails for the reason it names\n'
STUB
  chmod +x "$scripts/$VERIFIER"

  run="$work/run"
  mkdir -p "$run/.tdd"
  printf '# spec\n' > "$run/spec.md"
  printf '# test\n' > "$run/suite.test.sh"
}

# probe_title_reaches_the_verifier — the criterion. The launcher is run with the title as one
# argument, and what it did with it is read off the verifier's own recorded argv: the verifier
# ran at all, and exactly one of the arguments it received is the title, byte for byte.
#
# "Exactly one, byte for byte" is the whole of the claim. A title that arrived split across
# arguments, truncated at the apostrophe, or carrying the quotes a second shell left on it is
# a title the verifier cannot match against the ledger line it names — and a launch that died
# in the shell before `verify.sh` ran leaves no record at all, which is the first branch here.
probe_title_reaches_the_verifier() {
  local out code matches
  rm -f "$argv_file"
  out="$( cd "$run" && VERI_STUB_ARGV="$argv_file" "$scripts/$LAUNCHER_NAME" \
            --step "$STEP" red spec.md suite.test.sh case-1 2>&1 )" && code=0 || code=$?

  [[ -f "$argv_file" ]] || {
    problems+=("$LAUNCHER never reached $VERIFIER with the title \"$STEP\" — it exited $code and said: $(flat "$out")")
    return
  }

  matches="$(grep -cFx -- "$STEP" "$argv_file")"
  [[ "$matches" == 1 ]] ||
    problems+=("$VERIFIER received the title as $matches of its arguments, want exactly 1 byte-identical to \"$STEP\"; it was called with: $(flat "$(cat "$argv_file")")")
}

# 1. One criterion — a step title carrying an apostrophe reaches the verifier intact — and so
#    one case.
name="$LAUNCHER_NAME runs $VERIFIER with the step title as an argument, so an apostrophe in it survives the launch"
problems=()
scripts=""
run=""
argv_file=""

if probe_launcher_is_there && stage; then
  probe_title_reaches_the_verifier
fi
report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
