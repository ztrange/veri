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

# 7. The same rule for a remote rather than a name or a file (#258): since #251 run-conductor.sh
#    fetches `origin` in the clone its skill sits in before it pins, so a suite that launches the
#    script beside it fetches whatever origin this checkout has — the real repository, over the
#    network — and its answer then depends on the network and on what origin/main holds that day.
#    Every fetch-and-pin launch has to come from a fixture clone whose origin the case controls.
#
#    Probed by running each suite here that names run-conductor.sh, with a `git` on PATH in front
#    of the real one: a `fetch` in a repository whose origin is this checkout's own origin is
#    written to a log and refused rather than performed, so the probe itself never reaches the
#    network. The origin and the real git are written into the shim as text rather than passed in
#    the environment, since a case that severs its child's environment would otherwise hand the
#    shim an empty origin to compare against — and every repository with no origin matches that.
#    A sweep that selected no suite, or an origin this checkout does not have, would pass about
#    nothing, so both are probed.
name="no suite that names run-conductor.sh fetches this checkout's own origin"
problems=()
fetch_work="$(mktemp -d)"
trap 'rm -rf "$lock_work" "$every_work" "$fetch_work"' EXIT
own_origin="$(git -C "$HERE" remote get-url origin 2>/dev/null)"
real_git="$(command -v git)"
fetch_log="$fetch_work/fetches"
mkdir -p "$fetch_work/bin"
: > "$fetch_log"
{
  printf '#!/usr/bin/env bash\n'
  printf 'own_origin=%q real_git=%q fetch_log=%q\n' "$own_origin" "$real_git" "$fetch_log"
  cat <<'SHIM'
pre=()
for arg in "$@"; do
  if [[ "$arg" == fetch ]]; then
    url="$("$real_git" ${pre[@]+"${pre[@]}"} remote get-url origin 2>/dev/null)"
    if [[ -n "$own_origin" && "$url" == "$own_origin" ]]; then
      printf '%s\n' "git $* (cwd $PWD)" >> "$fetch_log"
      echo "git shim: refused a fetch of $own_origin" >&2
      exit 128
    fi
    break
  fi
  pre+=("$arg")
done
exec "$real_git" "$@"
SHIM
} > "$fetch_work/bin/git"
chmod +x "$fetch_work/bin/git"

launchers=()
for suite in "$HERE"/*.test.sh; do
  [[ "$suite" == "$HERE/$(basename "$0")" ]] && continue
  grep -q 'run-conductor\.sh' "$suite" && launchers+=("$suite")
done
[[ -n "$own_origin" ]] ||
  problems+=("this checkout has no origin, so there is no own origin a fetch could reach and nothing was checked")
[[ "${#launchers[@]}" -gt 0 ]] ||
  problems+=("no suite here names run-conductor.sh, so nothing was run")
for suite in ${launchers[@]+"${launchers[@]}"}; do
  : > "$fetch_log"
  PATH="$fetch_work/bin:$PATH" "$suite" >/dev/null 2>&1
  while IFS= read -r fetched; do
    problems+=("$(basename "$suite") fetched this checkout's own origin: $fetched")
  done < "$fetch_log"
done
report "$name"

# 8. The whole of #258's promise rather than the one remote case 7 names: `make test` passes with
#    the network unreachable. Every suite that exercises a script which can reach the network is
#    run here with the network cut off, and has to come back green and never have tried.
#
#    "Can reach the network" is read as text, the way cases 5 and 6 read theirs: a script beside
#    this directory whose uncommented lines run a remote git verb (fetch, pull, push, clone,
#    ls-remote), `gh` or `curl`; a suite exercises it when its text names that script. A hand-kept
#    list would be one script behind the next one that learns to fetch. Every other suite runs no
#    such script, so running the whole roster again here would double what `make test` costs the
#    three leaves of every step for suites that cannot answer differently offline.
#
#    Cut off twice over. `git`, `gh` and `curl` on PATH in front of the real ones: a remote git verb
#    whose target is a URL rather than a path on this filesystem, and any `gh` or `curl` at all, is
#    written to a log and refused with exit 128, so the probe never reaches the network. A suite that
#    stubs `gh` itself puts its stub in front of these, which is the stub the suite meant. And
#    http.proxy and HTTP(S)_PROXY point at a port nothing listens on, for anything that gets past
#    the shims. A selection that found no script, or no suite, would pass about nothing, so both are
#    probed.
name="every suite exercising a network-capable script passes with the network unreachable, and never tries it"
problems=()
offline_work="$(mktemp -d)"
trap 'rm -rf "$lock_work" "$every_work" "$fetch_work" "$offline_work"' EXIT
offline_log="$offline_work/reaches"
mkdir -p "$offline_work/bin"
: > "$offline_log"
{
  printf '#!/usr/bin/env bash\n'
  printf 'real_git=%q offline_log=%q\n' "$real_git" "$offline_log"
  cat <<'SHIM'
remote_url() { [[ "$1" =~ ^[A-Za-z][A-Za-z0-9+.-]*:// || "$1" =~ ^[^/:]+@[^/:]+: ]]; }
pre=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    fetch|pull|push|clone|ls-remote)
      verb="$1"; target=""
      for arg in "${@:2}"; do
        [[ "$arg" == -* ]] && continue
        target="$arg"; break
      done
      [[ -z "$target" ]] && target=origin
      url="$target"
      if ! remote_url "$url"; then
        url="$("$real_git" ${pre[@]+"${pre[@]}"} remote get-url "$target" 2>/dev/null || printf '%s' "$target")"
      fi
      if remote_url "$url"; then
        printf '%s\n' "git $verb $url (cwd $PWD)" >> "$offline_log"
        echo "git shim: network unreachable ($url)" >&2
        exit 128
      fi
      break ;;
    -C|-c|--git-dir|--work-tree) pre+=("$1" "$2"); shift 2; continue ;;
    -*) pre+=("$1"); shift; continue ;;
    *) break ;;
  esac
done
exec "$real_git" ${pre[@]+"${pre[@]}"} "$@"
SHIM
} > "$offline_work/bin/git"
for tool in gh curl; do
  {
    printf '#!/usr/bin/env bash\n'
    printf 'offline_log=%q\n' "$offline_log"
    printf 'printf "%%s\\n" "%s $* (cwd $PWD)" >> "$offline_log"\n' "$tool"
    printf 'echo "%s shim: network unreachable" >&2\nexit 128\n' "$tool"
  } > "$offline_work/bin/$tool"
done
chmod +x "$offline_work/bin/git" "$offline_work/bin/gh" "$offline_work/bin/curl"

net_scripts=()
for script in "$HERE"/../*.sh; do
  grep -qE '^[^#]*git[^#]*[[:space:]](fetch|pull|push|clone|ls-remote)([[:space:]]|$)|^[^#]*(^|[[:space:]])(gh|curl)[[:space:]]' "$script" &&
    net_scripts+=("$(basename "$script")")
done
offline_suites=()
for suite in "$HERE"/*.test.sh; do
  [[ "$suite" == "$HERE/$(basename "$0")" ]] && continue
  for script in ${net_scripts[@]+"${net_scripts[@]}"}; do
    if grep -qF "$script" "$suite"; then offline_suites+=("$suite"); break; fi
  done
done
[[ "${#net_scripts[@]}" -gt 0 ]] ||
  problems+=("no script beside this directory was recognised as reaching the network, so nothing was selected")
[[ "${#offline_suites[@]}" -gt 0 ]] ||
  problems+=("no suite here names a network-capable script, so nothing was run")
for suite in ${offline_suites[@]+"${offline_suites[@]}"}; do
  : > "$offline_log"
  offline_out="$(PATH="$offline_work/bin:$PATH" \
    GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=http.proxy GIT_CONFIG_VALUE_0=http://127.0.0.1:1 \
    HTTP_PROXY=http://127.0.0.1:1 HTTPS_PROXY=http://127.0.0.1:1 \
    "$suite" 2>/dev/null)" && offline_code=0 || offline_code=$?
  [[ "$offline_code" == 0 ]] ||
    problems+=("$(basename "$suite") offline: want exit 0, got $offline_code; last line: $(printf '%q' "$(printf '%s\n' "$offline_out" | tail -n 1)")")
  while IFS= read -r reached; do
    problems+=("$(basename "$suite") tried the network: $reached")
  done < "$offline_log"
done
report "$name"

# 9. The same rule for ambient state that is neither a name nor a file: how busy the machine is
#    (#200). supervise-retry.test.sh recovers a leaf on its second attempt under a 1-second
#    heartbeat window, and a preflight `make test` run beside several live conductors bailed on
#    exactly that attempt being killed as stuck (`code=2`) on a tree that was green a minute later.
#    A suite's answer must not depend on what else the CPU is doing when it runs.
#
#    Probed by running the suite beside N busy-loop processes, N being four per online CPU so the
#    load outnumbers the cores on any machine that runs this. The loops are this case's children
#    and killed before the report, so no other case runs under them. That they were still alive
#    when the suite finished is probed too: a loop that died at once would load nothing and make
#    this a pass about an idle machine.
name="supervise-retry.test.sh: the recovered attempt still gives 1 passed, 0 failed beside a busy-loop per CPU four times over"
problems=()
cpus="$(getconf _NPROCESSORS_ONLN 2>/dev/null)"
case "$cpus" in ''|*[!0-9]*) cpus=4 ;; esac
busy_pids=()
trap 'kill "${busy_pids[@]+"${busy_pids[@]}"}" 2>/dev/null; rm -rf "$lock_work" "$every_work" "$fetch_work" "$offline_work"' EXIT
for ((i = 0; i < cpus * 4; i++)); do
  ( while :; do :; done ) &
  busy_pids+=("$!")
done
loaded_out="$(env -u VERI_STUCK_RETRIES "$HERE/supervise-retry.test.sh" 2>/dev/null)" && loaded_code=0 || loaded_code=$?
for pid in "${busy_pids[@]}"; do
  kill -0 "$pid" 2>/dev/null ||
    problems+=("busy loop $pid was gone before the suite finished, so the machine was not loaded as claimed")
done
kill "${busy_pids[@]}" 2>/dev/null
wait "${busy_pids[@]}" 2>/dev/null
busy_pids=()
[[ "$loaded_code" == 0 ]] ||
  problems+=("want exit 0 under load, got $loaded_code")
[[ "$loaded_out" == *'1 passed, 0 failed'* ]] ||
  problems+=("want '1 passed, 0 failed' on stdout under load, got: $(printf '%q' "$loaded_out")")
report "$name"

# 8. The same load, answered by margin rather than by one lucky run (#200): case 7 shows the
#    recovered attempt passing beside busy loops once, which a window only just wide enough
#    passes as often as not. This pins the width. The window the suite hands supervise.sh must
#    exceed the recovered attempt's first output by at least 5 s, and exceed today's 1-second
#    window by no more than 5 s — the first attempt is killed only once that window has passed
#    in silence, so every second added to it is a second added to every `make test`.
#
#    Observed rather than read as text: the suite is copied into a scratch tree whose
#    `../supervise.sh` is a recorder. It writes down the VERI_HEARTBEAT it was given, wraps the
#    leaf so each attempt logs how many seconds passed before its first line, and execs the real
#    supervisor, so the suite still runs end to end. Seconds, because that is the clock
#    supervise.sh measures silence with. An attempt log that never reached a second attempt
#    would measure nothing, so that is probed too.
name="supervise-retry.test.sh: its heartbeat window leaves at least 5 s over the recovered attempt's first output, and adds no more than 5 s to the suite"
problems=()
margin_work="$(mktemp -d)"
trap 'kill "${busy_pids[@]+"${busy_pids[@]}"}" 2>/dev/null; rm -rf "$lock_work" "$every_work" "$margin_work"' EXIT
mkdir -p "$margin_work/tree/tests" "$margin_work/log"
cp "$HERE/supervise-retry.test.sh" "$margin_work/tree/tests/"
cat > "$margin_work/tree/supervise.sh" <<SHIM
#!/usr/bin/env bash
log="$margin_work/log"
printf '%s\n' "\${VERI_HEARTBEAT-unset}" > "\$log/heartbeat"
name="\$1"; shift
cat > "\$log/wrap" <<'WRAP'
#!/usr/bin/env bash
log="\$1"; shift
n=\$(( \$(cat "\$log/attempts" 2>/dev/null || echo 0) + 1 )); echo "\$n" > "\$log/attempts"
start=\$(date +%s)
"\$@" | { seen=0; while IFS= read -r line; do
  [[ "\$seen" == 1 ]] || { echo "\$n \$(( \$(date +%s) - start ))" >> "\$log/first-output"; seen=1; }
  printf '%s\n' "\$line"; done; }
exit "\${PIPESTATUS[0]}"
WRAP
chmod +x "\$log/wrap"
exec "$HERE/../supervise.sh" "\$name" "\$log/wrap" "\$log" "\$@"
SHIM
chmod +x "$margin_work/tree/supervise.sh"
margin_out="$(env -u VERI_STUCK_RETRIES -u VERI_HEARTBEAT "$margin_work/tree/tests/supervise-retry.test.sh" 2>/dev/null)" && margin_code=0 || margin_code=$?
window="$(cat "$margin_work/log/heartbeat" 2>/dev/null)"
recovered="$(awk '$1 > 1 { d = $2 } END { print d }' "$margin_work/log/first-output" 2>/dev/null)"
[[ "$margin_code" == 0 && "$margin_out" == *'1 passed, 0 failed'* ]] ||
  problems+=("want the suite green through the recorder, got exit $margin_code, stdout: $(printf '%q' "$margin_out")")
case "$window" in ''|*[!0-9]*) problems+=("want a whole-second VERI_HEARTBEAT handed to supervise.sh, got: $(printf '%q' "$window")") ; window="" ;; esac
[[ -n "$recovered" ]] ||
  problems+=("no second attempt wrote a first line, so there is no recovered attempt to measure a margin over")
if [[ -n "$window" && -n "$recovered" ]]; then
  [[ $((window - recovered)) -ge 5 ]] ||
    problems+=("want at least 5 s of margin, got a ${window}s window over a first output after ${recovered}s (margin $((window - recovered))s)")
fi
if [[ -n "$window" ]]; then
  [[ $((window - 1)) -le 5 ]] ||
    problems+=("want the window no more than 5 s wider than the 1 s it replaces, got ${window}s (+$((window - 1))s per make test)")
fi
report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
