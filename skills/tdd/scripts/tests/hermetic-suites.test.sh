#!/usr/bin/env bash
# Unit tests for the suites themselves — a suite that asserts a script's DEFAULT must not
# inherit an override for that default from the shell that ran it.
# Zero-dependency plain-shell asserts, same idiom as refactor-budget.test.sh.
#
# Why this exists (issue #87): an unattended run exports VERI_STUCK_RETRIES for its outer
# supervisor, the inner `make test` inherits it, and veri's own preflight then reads a red
# baseline on veri's own repo and refuses to start. A suite's answer must be a fact about
# the script, not about the caller's environment.
#
# Contract under test:
#   VERI_STUCK_RETRIES=0 supervise-retry.test.sh → exit 0, "1 passed, 0 failed",
#   exactly as with the variable unset.
#   VERI_MODEL=<x> leaf-model.test.sh → the same exit and the same stdout as a run with
#   the three model variables cleared.
#
# Run: scripts/tests/hermetic-suites.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
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

# same_answer <baseline arm> <baseline exit> <baseline stdout> <other exit> <other stdout> —
# the comparison every case below makes, once: the two arms agreed on their exit and on their
# stdout, and the baseline arm was green at all. `<baseline arm>` names the arm in the failure
# lines ("cleared", "no-lock"), since what makes an arm the baseline differs per case — a name
# the case cleared, or a lock it did not write.
#
# Asked as "the same answer both ways" rather than against a hardcoded count line, which is what
# case 1 below can do with a suite holding a single case: a suite that has several cases and will
# grow would fail a count spelled here for a case added there rather than for a leak. The baseline
# arm is also probed for being green at all, since two identically red runs agree on nothing worth
# pinning.
same_answer() {
  local baseline="$1" base_code="$2" base_out="$3" other_code="$4" other_out="$5"

  problems=()
  [[ "$base_code" == 0 ]] ||
    problems+=("the $baseline run is not green, so there is nothing to compare against: exit $base_code, stdout: $(printf '%q' "$base_out")")
  [[ "$other_code" == "$base_code" ]] ||
    problems+=("want the $baseline run's exit $base_code, got $other_code")
  [[ "$other_out" == "$base_out" ]] ||
    problems+=("want the $baseline run's stdout $(printf '%q' "$base_out"), got: $(printf '%q' "$other_out")")
}

# same_both_ways <suite> <cleared env setting…> -- <ambient env setting…> — run one suite twice
# as a child process, once with the names cleared and once with one of them carrying an ambient
# value, and compare the two arms with `same_answer`.
#
# The settings are forwarded to `env` verbatim, so `-u NAME` and `NAME=value` both reach it as
# themselves and the one under test stays where it is the point.
same_both_ways() {
  local suite="$1"; shift
  local arg seen=0
  local cleared=() ambient=()
  for arg in "$@"; do
    if [[ "$arg" == "--" ]]; then
      seen=1
    elif [[ "$seen" == 0 ]]; then
      cleared+=("$arg")
    else
      ambient+=("$arg")
    fi
  done

  local cleared_out cleared_code ambient_out ambient_code
  cleared_out="$(env "${cleared[@]}" "$HERE/$suite" 2>/dev/null)" && cleared_code=0 || cleared_code=$?
  ambient_out="$(env "${ambient[@]}" "$HERE/$suite" 2>/dev/null)" && ambient_code=0 || ambient_code=$?

  same_answer cleared "$cleared_code" "$cleared_out" "$ambient_code" "$ambient_out"
}

# 1. The contract above, probed by running the whole suite as a child process: the leak is
#    in how supervise-retry.test.sh spawns the supervisor, so only a real run of it walks
#    that path — there is nothing to assert in-process.
name="supervise-retry.test.sh: ambient VERI_STUCK_RETRIES=0 still gives 1 passed, 0 failed"
problems=()
out="$(VERI_STUCK_RETRIES=0 "$HERE/supervise-retry.test.sh" 2>/dev/null)" && code=0 || code=$?
[[ "$code" == 0 ]] ||
  problems+=("want exit 0, got $code")
[[ "$out" == *'1 passed, 0 failed'* ]] ||
  problems+=("want '1 passed, 0 failed' on stdout, got: $(printf '%q' "$out")")
report "$name"

# 2. The same rule for the three model variables issue #171 adds, and the suite whose whole
#    subject is them: leaf-model.sh answers `sonnet` or nothing depending on VERI_MODEL,
#    VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER, so every case in leaf-model.test.sh that
#    asserts the unset contract — "no variable set prints NOTHING, and the `claude` command
#    line is byte-identical to today's" — is asserting it about whatever shell typed
#    `make test`, unless that suite clears the three names for itself.
#
#    One ambient name, VERI_MODEL, because it is the one that reaches BOTH roles: a leak of
#    the run-wide knob changes every probe in that suite, where a role variable could only
#    change half of them. The two role names are cleared in both arms so that a shell which
#    exported one cannot make the arms differ by something this case did not set.
#
#    leaf-model.test.sh (~0.3 s) and not supervise.test.sh, whose `sup_run_no_model` is the
#    other guard of the same rule: this file runs inside `make test`, which three leaves of
#    every step run, and supervising real leaves again as a child costs ~24 s of each of them
#    — the cost issue #171 exists to cut. That guard is left to the suite that owns it.
name="leaf-model.test.sh: an ambient VERI_MODEL gives the same exit and the same stdout as a cleared run"
same_both_ways leaf-model.test.sh \
  -u VERI_MODEL -u VERI_MODEL_DEVELOPER -u VERI_MODEL_VERIFIER \
  -- -u VERI_MODEL_DEVELOPER -u VERI_MODEL_VERIFIER VERI_MODEL=sonnet
report "$name"

# 3. The same rule for the label tunables issue #113 adds, and the suite that owns them:
#    solvable-issues.sh reads `${VERI_PRIORITY_LABEL:-priority}` to decide which band an issue
#    sorts in, so every case in solvable-issues.test.sh that asserts the DEFAULT band order is
#    asserting it about whatever shell typed `make test`, unless that suite clears the name for
#    itself. An operator steering a loop exports exactly this variable, and the inner `make
#    test` of a run on veri's own repository inherits it — the shape of #87 again.
#
#    The ambient value is `ready-for-agent` because it is the one label the fixtures actually
#    carry: a name no fixture mentions renames the band to something nothing is in, changes no
#    answer, and would make this case pass while the leak it exists for stayed open.
name="solvable-issues.test.sh: an ambient VERI_PRIORITY_LABEL gives the same exit and the same stdout as a cleared run"
same_both_ways solvable-issues.test.sh \
  -u VERI_PRIORITY_LABEL \
  -- VERI_PRIORITY_LABEL=ready-for-agent
report "$name"

# 4. The same rule for ambient state that is not an environment variable at all: the lock a run
#    in flight leaves at <main_tree>/.tdd/wt/<n>/.tdd/conductor.pid. solvable-issues.sh reads it
#    out of the MAIN working tree of the repository the SCRIPT runs in (#166), and the
#    band-ordering cases invoke the script in the suite's own cwd, so on a machine where veri is
#    solving one of the numbers those fixtures name the live lock answers a question the case only
#    asked of its fixture — the suite goes red for what the run itself did by claiming its issue
#    (#226).
#
#    Probed by cwd rather than by `env`, because this ambient value is a file in a repository
#    rather than a name in the environment: both arms run the suite inside a scratch repository
#    built here, and the arms differ only by the locks under it. Nothing is written into the
#    surrounding repository, so the case cannot itself become the ambient state it is about.
#
#    The numbers locked are 108, 117, 120 and 124, the ones the band-ordering fixtures carry: a
#    number no fixture names claims nothing, changes no answer, and would make this case pass
#    while the leak it exists for stayed open — the same trap case 3 records for its label. The
#    pid written is this suite's own, which is alive by construction, since `in_flight` is
#    fail-open and a stale lock would likewise change nothing.
name="solvable-issues.test.sh: a live conductor lock in the surrounding repository gives the same exit and the same stdout as a run with none"
lock_work="$(mktemp -d)"
trap 'rm -rf "$lock_work"' EXIT
git init -q -b main "$lock_work/no-lock" >/dev/null 2>&1
git init -q -b main "$lock_work/locked" >/dev/null 2>&1
for n in 108 117 120 124; do
  mkdir -p "$lock_work/locked/.tdd/wt/$n/.tdd"
  printf '%s\n' "$$" > "$lock_work/locked/.tdd/wt/$n/.tdd/conductor.pid"
done

unlocked_out="$(cd "$lock_work/no-lock" && "$HERE/solvable-issues.test.sh" 2>/dev/null)" && unlocked_code=0 || unlocked_code=$?
locked_out="$(cd "$lock_work/locked" && "$HERE/solvable-issues.test.sh" 2>/dev/null)" && locked_code=0 || locked_code=$?

same_answer no-lock "$unlocked_code" "$unlocked_out" "$locked_code" "$locked_out"
report "$name"

# 5. The same lock, asked of EVERY number the fixtures in solvable-issues.test.sh name rather than
#    the four the report in #226 happened to catch. Case 4 pins the numbers a live run had claimed
#    on the day the leak was found; this one pins the rule underneath them — no case in that suite
#    reads a conductor lock outside a repository the case itself built — for the fixture numbers it
#    carries TODAY, which is the only list that stays true as cases are added.
#
#    The numbers are read out of the suite's own text, the way workflow-timeouts.test.sh reads
#    ci.yml as text (#99): a hand-kept list here would be one edit behind the next case that
#    invents a number, and the leak this case exists for reopens for exactly that number with the
#    case still green. A fixture number is a `"number": <n>` field, since that is the key the
#    VERI_GH_JSON fixtures use to say which issue they describe.
#
#    That derivation is itself probed — a pattern that matched nothing would lock nothing, make
#    both arms identical and report a pass about a machine that was never put under the condition.
#    It is the trap cases 3 and 4 record for their label and their numbers, one level up: here the
#    thing that can silently name nothing is the pattern rather than the value.
name="solvable-issues.test.sh: a live conductor lock for every number its own fixtures name gives the same exit and the same stdout as a run with none"
every_work="$(mktemp -d)"
trap 'rm -rf "$lock_work" "$every_work"' EXIT
git init -q -b main "$every_work/no-lock" >/dev/null 2>&1
git init -q -b main "$every_work/locked" >/dev/null 2>&1
fixture_numbers=($(sed -n 's/.*"number"[[:space:]]*:[[:space:]]*\([0-9][0-9]*\).*/\1/p' "$HERE/solvable-issues.test.sh" | sort -u))
for n in "${fixture_numbers[@]+"${fixture_numbers[@]}"}"; do
  mkdir -p "$every_work/locked/.tdd/wt/$n/.tdd"
  printf '%s\n' "$$" > "$every_work/locked/.tdd/wt/$n/.tdd/conductor.pid"
done

every_unlocked_out="$(cd "$every_work/no-lock" && "$HERE/solvable-issues.test.sh" 2>/dev/null)" && every_unlocked_code=0 || every_unlocked_code=$?
every_locked_out="$(cd "$every_work/locked" && "$HERE/solvable-issues.test.sh" 2>/dev/null)" && every_locked_code=0 || every_locked_code=$?

same_answer no-lock "$every_unlocked_code" "$every_unlocked_out" "$every_locked_code" "$every_locked_out"
[[ "${#fixture_numbers[@]}" -gt 0 ]] ||
  problems+=("no \"number\": <n> fixture was found in solvable-issues.test.sh, so no lock was written and the two arms cannot differ")
report "$name"

# 6. The same rule for a window rather than a name (#242): push-branch.sh waits
#    `${VERI_PUSH_BACKOFF:-2}` seconds, doubled per retry, before each retry of an unreachable
#    remote, so a suite that runs it without the knob pays that wait on real wall time — 14 s
#    on every `make test` for the #191 case, which three leaves of every step run. The testing
#    idiom injects every window a test would otherwise wait on; this pins that for every suite
#    here that invokes the script, including ones not written yet.
#
#    Read as text, the way case 5 reads its fixture numbers: a command is a run of lines joined
#    by trailing backslashes and named by the line it starts on, and it invokes the script when
#    it expands a variable some assignment in that suite sets to a path ending in /push-branch.sh, or spells the
#    script's path in quotes. "In its environment" is a `VERI_PUSH_BACKOFF=` setting on that
#    command; an `-u` alone clears the name, it does not set it. A sweep that recognised no
#    invocation at all would pass about nothing, so that is probed too.
name="every suite that invokes push-branch.sh sets VERI_PUSH_BACKOFF in its environment"
problems=()
push_invocations=0
for suite in "$HERE"/*.test.sh; do
  while IFS= read -r row; do
    case "$row" in
      invoked) push_invocations=$((push_invocations + 1)) ;;
      *) problems+=("$(basename "$suite"):$row invokes push-branch.sh without VERI_PUSH_BACKOFF in its environment, so a push to an unreachable origin waits the default backoff on wall time") ;;
    esac
  done < <(awk '
    BEGIN { assigns_script = "^[[:space:]]*(local[[:space:]]+)?[A-Za-z_][A-Za-z0-9_]*=.*/push-branch\\.sh[\"'"'"']?[[:space:]]*$" }
    NR == FNR {
      if ($0 ~ assigns_script) {
        v = $0
        sub(/^[[:space:]]*(local[[:space:]]+)?/, "", v)
        sub(/=.*/, "", v)
        vars[v] = 1
      }
      next
    }
    {
      if (!joining) start = FNR
      if ($0 ~ /\\$/) { cmd = cmd substr($0, 1, length($0) - 1) " "; joining = 1; next }
      cmd = cmd $0; joining = 0
      line = cmd; cmd = ""
      if (line ~ /^[[:space:]]*#/) next
      if (line ~ assigns_script) next
      invokes = (line ~ /\/push-branch\.sh"/)
      for (v in vars)
        if (index(line, "\"$" v "\"") || index(line, "${" v "}")) invokes = 1
      if (!invokes) next
      print "invoked"
      if (line !~ /VERI_PUSH_BACKOFF=/) print start
    }
  ' "$suite" "$suite")
done
[[ "$push_invocations" -gt 0 ]] ||
  problems+=("no suite here was recognised as invoking push-branch.sh, so nothing was checked")
report "$name"

# 7 and 8, which asked which suites reach the network and whether one fetches this checkout's
#    own origin (#258), are gone: this suite now runs no other suite a second time for either
#    (#301). `make test` runs every suite once under the offline shims in tests/offline/, with a
#    per-suite reach log, and fails naming the suite and what it tried; count-line-guard pins both
#    — a fetch of a remote URL and a fetch of this checkout's own origin. Asking again here ran
#    about a third of the suites twice on every `make test`, for the same answer.
#
# 9. Probed by running a copy of this file in a scratch tree beside a stand-in for each kind of
#    script cases 7 and 8 selected on — one that fetches and pushes, named run-conductor.sh and
#    push-branch.sh — and one probe suite that names both and appends a line to a log each time it
#    runs. Cases 1 to 5 name their subjects by file, and the probe is none of them, so any line in
#    the log is a re-run by some other case. The copy is run with HERMETIC_RERUN_PROBE set, which
#    this case reads to skip itself in the child: the copy's own case 9 would otherwise copy the
#    copy, forever.
name="hermetic-suites.test.sh re-runs no suite for the offline or own-origin cases"
if [[ -z "${HERMETIC_RERUN_PROBE:-}" ]]; then
  problems=()
  rerun_work="$(mktemp -d)"
  trap 'rm -rf "$lock_work" "$every_work" "$rerun_work"' EXIT
  rerun_log="$rerun_work/runs"
  mkdir -p "$rerun_work/scripts/tests"
  : > "$rerun_log"
  # The stand-ins are named by a loop variable rather than spelled as paths, since case 6 reads a
  # quoted path ending in the push script's name as an invocation of it.
  for stand_in in "run-conductor:fetch origin main" "push-branch:push origin HEAD"; do
    printf '#!/usr/bin/env bash\ngit %s\n' "${stand_in#*:}" > "$rerun_work/scripts/${stand_in%%:*}.sh"
  done
  {
    printf '#!/usr/bin/env bash\n'
    printf '# Names run-conductor.sh and push-branch.sh, and runs neither.\n'
    printf 'printf "%%s\\n" ran >> %q\n' "$rerun_log"
    printf 'echo "1 passed, 0 failed"\n'
  } > "$rerun_work/scripts/tests/probe.test.sh"
  cp "$HERE/$(basename "$0")" "$rerun_work/scripts/tests/"
  chmod +x "$rerun_work/scripts/"*.sh "$rerun_work/scripts/tests/"*.test.sh
  HERMETIC_RERUN_PROBE=1 "$rerun_work/scripts/tests/$(basename "$0")" >/dev/null 2>&1
  reruns="$(wc -l < "$rerun_log" | tr -d ' ')"
  [[ "$reruns" == 0 ]] ||
    problems+=("$(basename "$0") ran probe.test.sh $reruns time(s), want 0: a suite that names a network-capable script was re-run")
  report "$name"
fi

# 9. The same rule for the one-shot re-pin instruction (#285): run-conductor.sh reads
#    `${VERI_NEW_SKILL:-}` to decide whether a resume keeps its recorded skill pin or takes the
#    clone's newer commit, so every case in run-conductor.test.sh that resumes without setting it
#    — "keep the recorded pin", "refuse an unresolvable one with exit 2" — is asserting it about
#    whatever shell typed `make test`, unless that suite clears the name for itself. A run resumed
#    with VERI_NEW_SKILL=1, the operator's documented way to take a newer skill, hands the name to
#    its leaves' `make test` — the shape of #87 again, observed on #200's resume.
name="run-conductor.test.sh: an ambient VERI_NEW_SKILL=1 gives the same exit and the same stdout as a cleared run"
same_both_ways run-conductor.test.sh \
  -u VERI_NEW_SKILL \
  -- VERI_NEW_SKILL=1
report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
