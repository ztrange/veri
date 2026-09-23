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

# The other two arguments the call carries, named once: the launcher is run from a directory
# holding these files, and the same names go on its command line, so a staged tree can never
# disagree with the call that points at it.
SPEC='spec.md'
TEST_PATH='suite.test.sh'

# The phase the call names, and the reason file that belongs to it — spelled once, because a
# case that seeded a reason file for one phase and launched another would be watching a file
# nothing in the run was ever going to touch, and would pass for that reason alone.
PHASE='red'
REASON=".tdd/verify-$PHASE.reason"

# The whole call, once. Every case launches with exactly this argv — a well-formed call in the
# documented shape, `--step <title> <phase> <spec> <test-path> <target>` — and they differ only
# in the tree they launch it over: a real verifier, one that cannot start, one watching the
# phase's reason file. Spelled at each call site, they could drift into asking about different
# calls, and one case's exit 2 would then be evidence about a call shape another never ran.
#
# The target test id is the one argument no case has anything to say about: the launcher passes
# it through untouched and every stub ignores it, so it is named for what it is rather than
# after whichever case was written first.
CALL=(--step "$STEP" "$PHASE" "$SPEC" "$TEST_PATH" a-target-test-id)

pass=0 fail=0

# launch <scripts-dir> <run-dir> [NAME=VALUE …] — run the launcher out of <scripts-dir>, from
# <run-dir> as its cwd, with the one call every case makes, and leave what it said in `out`
# and the status it handed its supervisor in `code`.
#
# Every case asks its question about that status or about what the launcher's own run left
# behind, so the three things that must not vary between them — the cwd, `${CALL[@]}` and the
# capture of stderr with stdout — are spelled here once. The environment is what genuinely
# differs: each stub reads the paths it records through from its own variables, and only the
# case that staged it knows them.
launch() {
  local scripts_dir="$1" run_dir="$2"
  shift 2
  out="$( cd "$run_dir" && env "$@" "$scripts_dir/$LAUNCHER_NAME" "${CALL[@]}" 2>&1 )" &&
    code=0 || code=$?
}

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

# copy_scripts_to <dir> — a copy of the real scripts directory at <dir>, which is where every
# case runs the launcher from: it resolves its verifier as a sibling, so what sits beside it
# is the whole of what a case controls.
#
# The directory is copied whole (its libs and prompts with it) rather than the launcher alone,
# because what a script here may reach for through its own directory is its business and not
# this suite's. Each case then replaces the ONE file it is about — `verify.sh` — leaving this
# function with no opinion on the verifier, which is what lets both cases share it.
copy_scripts_to() {
  local dir="$1" d
  mkdir -p "$dir" || return 1
  cp "$SCRIPTS"/*.sh "$dir"/ 2>/dev/null
  for d in lib prompts; do
    if [[ -d "$SCRIPTS/$d" ]]; then cp -R "$SCRIPTS/$d" "$dir/$d"; fi
  done
}

# install_stub <dir> — write this function's stdin into <dir> as the verifier the launcher
# will reach, and make it executable. Both stub-driven cases write a different script under
# the same name in the same way, and the name and the chmod are the part that has to agree:
# a stub written under another name is a verifier the launcher never runs, and one left
# unexecutable is case 2's fixture rather than a working verifier — either way the case would
# report on something other than what it asks about.
install_stub() {
  cat > "$1/$VERIFIER"
  chmod +x "$1/$VERIFIER"
}

# make_run_dir <dir> — the cwd a case launches from, holding the two files the call names and
# nothing else: the launcher's cwd needs whatever its arguments point at, and a `.tdd` for
# output the stub never writes would only suggest the verifier reports through one — the
# reason and exit files are the conductor's redirections, not verify.sh's own writes.
make_run_dir() {
  local dir="$1"
  rm -rf "$dir"
  mkdir -p "$dir" || return 1
  printf '# spec\n' > "$dir/$SPEC"
  printf '# test\n' > "$dir/$TEST_PATH"
}

# stage — build the tree the launcher runs in and leave the run's cwd in `run`, the recorded
# argv path in `argv_file`.
#
# The verifier is the stub, which is `#!/bin/sh` for the reason #322 gives — a stub is forked
# per case and bash 5 starts three times slower than sh.
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
  launch "$scripts" "$run" VERI_STUB_ARGV="$argv_file"

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

# stage_broken <state> — the same tree `stage` builds, minus a verifier the launcher can
# start: `missing` leaves no verify.sh at all, `unrunnable` leaves one the kernel refuses to
# execute. Both are "cannot start the verifier", which is the one thing the case asks about;
# a guard that only looked for the file would answer the first and not the second.
#
# Its own copy of the scripts directory and its own cwd, so the case says nothing about the
# tree case 1 ran in and answers even if that one never got staged.
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

# probe_unstartable_verifier_is_no_answer <state> <how it reads in a message> — stage the
# launcher over a verifier in that state, run it with an otherwise well-formed call, and read
# the status it hands its supervisor.
#
# Two claims, because the criterion makes two. **Never 1**: that is the code CLAUDE.md
# reserves for a real answer — the verifier ran and said REJECT — and a launch that never
# started one has no answer to report, so a conductor reading 1 here spends a revise attempt
# arguing with a working test, which is exactly what the #424 run did. **2**: the code for no
# answer obtained, the one `classify-bail.sh` turns into a system-failure label a human reads.
# The status is the observable: it is what `supervise.sh` records into
# `.tdd/verdict-<phase>.exit` and what `wait-leaf.sh` hands back.
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

# 2. A launcher that cannot start the verifier produced no answer, and says so with the code
#    reserved for that — never with the one that means the verifier spoke.
name="$LAUNCHER_NAME exits 2, and never 1, when it cannot start $VERIFIER"
problems=()
broken=""
broken_run=""

if probe_launcher_is_there; then
  probe_unstartable_verifier_is_no_answer missing "no $VERIFIER to start"
  probe_unstartable_verifier_is_no_answer unrunnable "a $VERIFIER it cannot execute"
fi
report "$name"

# The reason an earlier step left behind. On the #424 run the file under it was 23 minutes old
# and belonged to the step before, and a conductor reading the contract literally took it for
# this step's verdict. Its apostrophe is incidental here; what matters is that no byte of it
# may still be readable when the verifier runs.
STALE="REJECT: the previous step's test does not pin the criterion it names"

# stage_watching_reason — the tree case 3 runs in: a copy of the scripts directory whose
# verify.sh records what the phase's reason file held AT THE MOMENT IT RAN, and a cwd holding
# a `.tdd/` with that file already seeded stale.
#
# The record, not the file's final state, is what the case reads, because the criterion is
# about an ordering: cleared BEFORE the verifier runs. A launcher that truncated the file
# afterwards — or a stub whose own output happened to overwrite it — would leave a clean file
# behind and still have let the verifier see the previous step's reason.
#
# Its own copy and its own cwd, for the reason `stage_broken` has its own: the case must
# answer even if neither of the others got staged.
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

# probe_stale_reason_is_gone_before_the_verifier_runs — the criterion. Launch over the seeded
# tree and read the record the verifier left: it ran at all, and what it could see in the
# phase's reason file was nothing.
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

# 3. The reason file a previous step wrote is cleared before this verdict's verifier runs, so
#    no byte of it can come back as this step's answer.
name="$LAUNCHER_NAME clears $REASON before $VERIFIER runs, so an earlier step's reason cannot be read as this verdict"
problems=()
watching=""
watching_run=""
seen=""

if probe_launcher_is_there && stage_watching_reason; then
  probe_stale_reason_is_gone_before_the_verifier_runs
fi
report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
