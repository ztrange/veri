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

LAUNCHER_NAME='run-verdict.sh'
LAUNCHER="skills/tdd/scripts/$LAUNCHER_NAME"
LAUNCHER_PATH="$SCRIPTS/$LAUNCHER_NAME"

VERIFIER='verify.sh'

STEP="A background process is killed by the pid recorded when it started, never by that shell's own job spec"

SPEC='spec.md'
TEST_PATH='suite.test.sh'

PHASE='red'
REASON=".tdd/verify-$PHASE.reason"

CALL=(--step "$STEP" "$PHASE" "$SPEC" "$TEST_PATH" a-target-test-id)


launch() {
  local scripts_dir="$1" run_dir="$2"
  shift 2
  out="$( cd "$run_dir" && env "$@" "$scripts_dir/$LAUNCHER_NAME" "${CALL[@]}" 2>&1 )" &&
    code=0 || code=$?
}

source "$HERE/lib/harness.sh"

flat() { local s="$1"; printf '%s' "${s//$'\n'/\/}"; }

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

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

copy_scripts_to() {
  local dir="$1" d
  mkdir -p "$dir" || return 1
  cp "$SCRIPTS"/*.sh "$dir"/ 2>/dev/null
  for d in lib prompts; do
    if [[ -d "$SCRIPTS/$d" ]]; then cp -R "$SCRIPTS/$d" "$dir/$d"; fi
  done
}

install_stub() {
  cat > "$1/$VERIFIER"
  chmod +x "$1/$VERIFIER"
}

make_run_dir() {
  local dir="$1"
  rm -rf "$dir"
  mkdir -p "$dir" || return 1
  printf '# spec\n' > "$dir/$SPEC"
  printf '# test\n' > "$dir/$TEST_PATH"
}

stage() {
  scripts="$work/scripts"
  copy_scripts_to "$scripts" || return 1

  argv_file="$work/verifier.argv"
  install_stub "$scripts" <<'STUB'
#!/bin/sh
# Stub verifier: record the argv handed to it, one argument per line, and answer like a
# verifier that passed — what this case reads is the record, not the verdict.
for a in "$@"; do printf '%s\n' "$a"; done > "$VERI_STUB_ARGV"
printf 'the test pins the criterion and fails for the reason it names\n'
STUB

  run="$work/run"
  make_run_dir "$run"
}

probe_title_reaches_the_verifier() {
  local out code matches
  rm -f "$argv_file"
  launch "$scripts" "$run" VERI_STUB_ARGV="$argv_file"

  [[ -f "$argv_file" ]] || {
    problems+=("$LAUNCHER never reached $VERIFIER with the title \"$STEP\" — it exited $code and said: $(flat "$out")")
    return
  }

  matches="$(grep -cFx -- "$STEP" "$argv_file")"
  [[ "$matches" == 1 ]] ||
    problems+=("$VERIFIER received the title as $matches of its arguments, want exactly 1 byte-identical to \"$STEP\"; it was called with: $(flat "$(cat "$argv_file")")")
}

name="$LAUNCHER_NAME runs $VERIFIER with the step title as an argument, so an apostrophe in it survives the launch"
problems=()
scripts=""
run=""
argv_file=""

if probe_launcher_is_there && stage; then
  probe_title_reaches_the_verifier
fi
report "$name"

stage_broken() {
  local state="$1"
  broken="$work/broken"
  rm -rf "$broken"
  copy_scripts_to "$broken" || return 1

  case "$state" in
    missing)   rm -f "$broken/$VERIFIER" ;;
    unrunnable) printf '#!/bin/sh\nexit 0\n' > "$broken/$VERIFIER"; chmod -x "$broken/$VERIFIER" ;;
  esac

  broken_run="$work/broken-run"
  make_run_dir "$broken_run"
}

probe_unstartable_verifier_is_no_answer() {
  local state="$1" how="$2" out code
  stage_broken "$state" || {
    problems+=("could not stage a tree with $how")
    return
  }

  launch "$broken" "$broken_run"

  [[ "$code" != 1 ]] ||
    problems+=("with $how, $LAUNCHER exited 1 — the code for a verdict the verifier gave, from a verifier that never ran; it said: $(flat "$out")")
  [[ "$code" == 2 ]] ||
    problems+=("with $how, $LAUNCHER exited $code, want 2 — the code for no answer obtained; it said: $(flat "$out")")
  return 0
}

name="$LAUNCHER_NAME exits 2, and never 1, when it cannot start $VERIFIER"
problems=()
broken=""
broken_run=""

if probe_launcher_is_there; then
  probe_unstartable_verifier_is_no_answer missing "no $VERIFIER to start"
  probe_unstartable_verifier_is_no_answer unrunnable "a $VERIFIER it cannot execute"
fi
report "$name"

STALE="REJECT: the previous step's test does not pin the criterion it names"

stage_watching_reason() {
  watching="$work/watching"
  rm -rf "$watching"
  copy_scripts_to "$watching" || return 1

  seen="$work/reason-seen"
  rm -f "$seen"
  install_stub "$watching" <<'STUB'
#!/bin/sh
# Stub verifier: copy the phase's reason file, as it stands now, into the record this case
# reads — an unreadable or absent file records as nothing, which is the same answer as a
# cleared one and the answer this case wants.
cat "$VERI_STUB_REASON" > "$VERI_STUB_SEEN" 2>/dev/null || : > "$VERI_STUB_SEEN"
printf 'the test pins the criterion and fails for the reason it names\n'
STUB

  watching_run="$work/watching-run"
  make_run_dir "$watching_run" || return 1
  mkdir -p "$watching_run/$(dirname "$REASON")" || return 1
  printf '%s\n' "$STALE" > "$watching_run/$REASON"
}

probe_stale_reason_is_gone_before_the_verifier_runs() {
  local out code
  launch "$watching" "$watching_run" \
    VERI_STUB_SEEN="$seen" VERI_STUB_REASON="$watching_run/$REASON"

  [[ -f "$seen" ]] || {
    problems+=("$LAUNCHER never reached $VERIFIER, so the case says nothing about $REASON — it exited $code and said: $(flat "$out")")
    return
  }

  [[ ! -s "$seen" ]] ||
    problems+=("when $VERIFIER ran, $REASON still held the previous step's reason: $(flat "$(cat "$seen")") — want it cleared before the verifier starts, so nothing left there can be read as this verdict")
}

name="$LAUNCHER_NAME clears $REASON before $VERIFIER runs, so an earlier step's reason cannot be read as this verdict"
problems=()
watching=""
watching_run=""
seen=""

if probe_launcher_is_there && stage_watching_reason; then
  probe_stale_reason_is_gone_before_the_verifier_runs
fi
report "$name"

finish
