#!/usr/bin/env bash
# supervise.sh — launch one leaf under a heartbeat + hard-timeout watchdog.
#
# This is the one choke point where stuck-detection policy lives (ADR-0002): every leaf is
# launched through here, never directly. The supervisor spawns the leaf in the background
# and watches it two ways:
#   * heartbeat — activity on the leaf's progress log within a window tells "slow but
#     working" from "hung". A leaf silent past the window is killed.
#   * hard timeout — a leaf that exceeds the time cap is killed even if still noisy.
# Both windows count only time the machine spent awake (issue #472). The clock is Python's
# time.monotonic(): on macOS that is mach_absolute_time(), which does not advance while the
# Mac is asleep, and on Linux it is CLOCK_MONOTONIC, which does not advance while the machine
# is suspended. The wall clock (`date +%s`) keeps running through a suspend, so an hour with
# the lid closed would read as an hour of silence and kill a leaf that never hung — the
# heartbeat slides by whatever the wall clock moved across one poll beyond this clock, and the
# hard timeout is measured on this clock alone.
# The heartbeat is the leaf's; a `verdict-<phase>` supervision is the wrapper around a
# verifier leaf that is already supervised under its own name, so it keeps only the hard
# timeout and never kills for a silence that is the wrapper's rather than the verifier's
# (issue #415 — the reasoning is where `heartbeat_watched` is set, below).
# A killed leaf is retried up to VERI_STUCK_RETRIES times (default 1) on a fresh attempt; if
# it still can't recover it is reported as `killed-stuck`, which the conductor turns into a
# clean bail — unless its log already holds the leaf's closing result record, in which case the
# kill landed on a finished process and the leaf's own outcome is reported instead (issue
# #212). A kill and a rendered verdict can coexist because the watchdog's only sensor for
# "the leaf is done" is the subshell's rc file, and the leaf's stream finishes before the
# subshell writes `.tdd/<name>.rc` — so between the last line of output and that file
# landing there is a window in which a finished leaf is indistinguishable from a silent
# one, and a kill is not proof that no answer was obtained.
#
# Usage:
#   supervise.sh <name> <cmd> [args...]
#
# The leaf's combined stdout+stderr is captured to `.tdd/<name>.log` (the progress log the
# heartbeat watches) and echoed to this script's stdout on completion, so a verifier leaf
# can be piped straight into parse-verdict.sh.
#
# Status: exit 0 success · 1 leaf-failure · 2 killed-stuck. A one-line status (with the
# kill cause) is written to stderr, and the same code is recorded in the completion file
# `.tdd/<name>.exit` on every path — so a leaf launched detached can be waited on by
# polling that file instead of by reading this script's stdout. The one exception is a leaf
# that recorded a code in that file itself, as the verifier's launch wrapper does with
# `verify.sh`'s verdict code: the leaf's own record is the answer and is left alone (#415).
#
# Three kinds of event are appended to the run's event log, `.tdd/events.jsonl` (issue #107,
# ADR-0014): one `launch` — the leaf's name, the command behind it, the model it runs on
# (empty when the run chose none) and the attempt its name encodes — one `retry` per
# relaunch, carrying the cause the watchdog killed the previous attempt for, and one `exit`
# — the 0/1/2 status above, the kill cause when there is one, and how many wall seconds the
# last attempt took. `launch` and `exit` are written once per supervision, not once per
# attempt: a second one would read as a second leaf, and the relaunch is `retry`'s to
# report. A name leaf-role.sh cannot read leaves no line at all, rather than one whose actor
# and attempt were invented.
#
# Tunables (env): VERI_HEARTBEAT silence window secs (default 180) · VERI_TIMEOUT hard cap
# secs (default 900) · VERI_POLL poll interval secs (default 1) · VERI_STUCK_RETRIES extra
# attempts after the first when a leaf is killed-stuck (default 1) · VERI_KILL_POLL the grace
# loop's poll interval secs when a kill is sent, before escalating to KILL (default 0.1, an
# internal knob like VERI_POLL rather than one SKILL.md documents) · VERI_MODEL /
# VERI_MODEL_DEVELOPER / VERI_MODEL_VERIFIER the model this leaf's role runs on, resolved
# through leaf-model.sh and exported to the leaf as VERI_LEAF_MODEL (all unset by default,
# which is no `--model` flag at all).
set -uo pipefail

# The call this script accepts, spelled once: both refusals below quote it back, so a
# caller who dropped either required argument is shown the whole call, not half of it.
USAGE="usage: supervise.sh <name> <cmd> [args...]"

[[ -n "${1:-}" ]] || { echo "$USAGE" >&2; exit 2; }
name="$1"
shift
[[ $# -ge 1 ]] || { echo "supervise: missing <cmd>" >&2; echo "$USAGE" >&2; exit 2; }

HERE="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=lib/leaf-model.sh
source "$HERE/lib/leaf-model.sh"
# shellcheck source=lib/preserve.sh
source "$HERE/lib/preserve.sh"
# shellcheck source=lib/number-in.sh
source "$HERE/lib/number-in.sh"

heartbeat="${VERI_HEARTBEAT:-180}"
timeout="${VERI_TIMEOUT:-900}"
poll="${VERI_POLL:-1}"
retries="${VERI_STUCK_RETRIES:-1}"

# Whether the heartbeat above is one of this supervision's two sensors at all — it is, for a
# leaf, and it is not for the wrapper around a verifier (issue #415). `supervise.sh
# verdict-<phase>` watches SKILL.md's `bash -c "verify.sh … > .reason 2> .err; echo $? >
# .exit"`, and that wrapper sends every byte the verification produces to the reason and err
# files and to `.tdd/verify-<phase>.log`, where the `supervise.sh verify-<phase>` INSIDE
# verify.sh puts the leaf's own stream. So `.tdd/verdict-<phase>.log` — the only thing a
# heartbeat here can watch — stays empty however hard the verifier is working, and a window
# measured over that silence kills every verification that outlives it.
#
# The leaf itself is already supervised, under its own name and its own window, so the silence
# that matters is already measured in the one place stuck-detection policy lives (ADR-0002). A
# window here would be a SECOND one over the same verification — a second way to raise
# killed-stuck, blind to the signal the first one reads — which would make the fix for a
# stalled wait a new way to lose a working verification. What the wrapper is supervised for is
# a completion file on every path, so the wait can end (#415's stalled `wait-leaf.sh
# verdict-<phase>`), not a second stuck-detector; the hard timeout, which needs no progress to
# read, still bounds it.
heartbeat_watched=1
case "$name" in verdict-*) heartbeat_watched=0 ;; esac

# A malformed VERI_KILL_POLL is a misconfigured run, not a decision — the same fail-closed
# rule refactor-budget.sh applies to VERI_REFACTOR_BUDGET: a diagnostic on stderr and exit 2,
# never a silent fallback that would leave kill_tree either busy-looping or waiting far
# longer than intended. Unlike VERI_HEARTBEAT/VERI_TIMEOUT/VERI_POLL/VERI_STUCK_RETRIES above
# (whole seconds or counts, unvalidated since #12), this one accepts a fraction — the
# production default is 0.1s — so the pattern allows an optional decimal part.
kill_poll="${VERI_KILL_POLL:-0.1}"
if [[ ! "$kill_poll" =~ ^[0-9]+(\.[0-9]+)?$ ]]; then
  echo "supervise: VERI_KILL_POLL must be a non-negative number: $kill_poll" >&2
  exit 2
fi

mkdir -p .tdd
log=".tdd/$name.log"
rcfile=".tdd/$name.rc"
exitfile=".tdd/$name.exit"
pidfile=".tdd/$name.pid"

now() { date +%s; }

# Whole seconds of time the machine spent awake, from the executable VERI_AWAKE_CLOCK names —
# or, when it names none, from `awake_seconds` below (issue #472).
awake_clock="${VERI_AWAKE_CLOCK:-awake_seconds}"

# Python's time.monotonic() is mach_absolute_time() on macOS and CLOCK_MONOTONIC on Linux,
# and neither advances while the machine is suspended.
awake_seconds() { python3 -c 'import time; print(int(time.monotonic()))'; }

# Seconds-since-epoch of $1's last modification — the heartbeat sensor. There is no portable
# `stat`: GNU/coreutils spells it `stat -c %Y`, BSD/macOS spells it `stat -f %m`. The two
# must be tried one at a time, into a variable, with the answer validated — NOT chained with
# `||` inside one `$( )`. On GNU, `-f` is not a format flag at all; it means --file-system,
# so `stat -f %m FILE` reads `%m` as a second *filename* and prints a `  File: "…"` block to
# stdout for the real one before exiting non-zero. Chained, that block joins the fallback's
# digits in the same substitution and reaches the caller's `$(( ))`, where `set -u` kills the
# supervisor on the unset word `File`. Assigning each attempt separately overwrites instead
# of appending, and the digit test rejects anything that is not a plain count of seconds.
mtime_of() {
  local m
  m="$(stat -c %Y "$1" 2>/dev/null)" || m="$(stat -f %m "$1" 2>/dev/null)" || m=""
  # No readable mtime (neither spelling, or the log vanished) → report "just touched". The
  # heartbeat then never fires and the hard timeout, which needs only `date`, still bounds
  # the leaf. The opposite default (0) would read as decades of silence and kill every leaf.
  case "$m" in ''|*[!0-9]*) m="$(now)" ;; esac
  printf '%s\n' "$m"
}

kill_tree() {
  kill -TERM -"$pid" 2>/dev/null || kill -TERM "$pid" 2>/dev/null
  # Brief grace, then make sure it is gone. The poll is real sleep, not the injected clock
  # supervise.test.sh stubs `date`/`stat` with: this loop polls `kill -0`, a real OS process
  # check, so jumping a fake clock would not make the kernel reap the child any sooner.
  # VERI_KILL_POLL (default 0.1, unchanged) is a test-only knob a suite exercising many
  # killed-stuck leaves can shrink instead of paying up to 5 x 0.1s of real sleep each time.
  for _ in 1 2 3 4 5; do kill -0 "$pid" 2>/dev/null || return 0; sleep "$kill_poll"; done
  kill -KILL -"$pid" 2>/dev/null || kill -KILL "$pid" 2>/dev/null
}

# The leaf's own outcome, read out of the closing `{"type":"result", …}` record its stream
# ends with: `success` or `failure` on stdout, or nothing and a non-zero status when the log
# holds no such record. This is the sensor behind the rule below — a leaf that finished is not
# a stuck one, whatever the heartbeat window said (issue #212).
#
# The whole file is scanned and the last record wins, the reading extract-result.sh and
# harvest-usage.sh already do and for their reason: the record is not the last line of the log
# it lives in, because run-leaf.sh appends the extracted result text after the stream. Lines
# that are not JSON objects are skipped rather than fatal, so a stub or a plain-text leaf
# simply has no record and the caller keeps the watchdog's verdict.
#
# `is_error` is the record's own word for how the leaf ended, so the mapping needs no table:
# it is the same true/false the leaf would have exited 1/0 on had it lived long enough to.
terminal_outcome() {
  python3 -c '
import json, sys

record = None
for line in open(sys.argv[1]):
    s = line.strip()
    if not s.startswith("{"):
        continue
    try:
        obj = json.loads(s)
    except ValueError:
        continue
    if isinstance(obj, dict) and obj.get("type") == "result":
        record = obj            # last result record wins
if record is None:
    sys.exit(1)
print("failure" if record.get("is_error") else "success")
' "$1"
}

# Turn a kill that landed on a finished leaf into the leaf's own outcome — reading `$status`
# and `$reason`, and rewriting both. A no-op on any status but `killed-stuck`, and on a log
# `terminal_outcome` finds no record in, so the watchdog's verdict stands wherever the leaf
# really did go silent.
#
# A leaf whose stream already carried a terminal result record had answered before the
# watchdog reached it, so what was killed was a finished process and not a hung one. The code
# this supervision reports is then the leaf's own, not exit 2 (issue #212). The distinction is
# the load-bearing one in this codebase: exit 2 says no answer could be obtained and the
# conductor can only bail on it as a system failure, so a rendered verdict reported under that
# code makes every `no-verdict` bail in a run log unreadable — nothing in it tells "the
# verifier never answered" from "the verifier answered and we killed it".
#
# `reason` is cleared with the status, because it is the cause the `exit` mark and the status
# line report a kill under, and this supervision no longer reports one. What actually happened
# — a kill landing on a finished leaf — is said on its own line instead, since it is still
# worth a reader of .err knowing that the window was too tight for a leaf that worked.
recover_finished_leaf() {
  local outcome result_tmp
  [[ "$status" == "killed-stuck" ]] || return 0
  outcome="$(terminal_outcome "$log")" || return 0

  echo "supervise[$name]: killed after the leaf had already written its result ($reason) — reporting the leaf's own $outcome" >&2
  # The kill also cost the leaf run-leaf.sh's closing act: it appends the clean result text
  # after the raw stream, and a killed leaf never reaches that line. What survives in the log
  # is stream-json only, where the verdict is a `\n`-escaped string INSIDE a one-line
  # `{"type":"result", …}` object — and parse-verdict.sh matches `VERDICT:` at the start of a
  # line, so the text is present and unreadable. The recovery therefore owes the same append,
  # made with the same extract-result.sh, so this script's stdout (`cat "$log"` at the foot)
  # ends in a parseable verdict block exactly as a live leaf's would.
  #
  # Through a temp file because the reader and the writer would otherwise be the same path: a
  # redirection appending to `$log` truncates or races the read of it. A refusal leaves the log
  # as it was — the recovered status above is the answer this step owes, and a missing tail is
  # the caller's to notice, not a reason to turn a rendered verdict back into exit 2.
  result_tmp="$(mktemp)"
  if "$HERE/extract-result.sh" < "$log" > "$result_tmp" 2>/dev/null; then
    { printf '\n'; cat "$result_tmp"; } >> "$log"
  fi
  rm -f "$result_tmp"
  status="$outcome"; reason=""
}

# Run the leaf once on a fresh log/rc, watching for stuck/timeout. Sets three globals, and
# those three are its answers: status/reason, and `$secs` — how many awake seconds this attempt
# took, which the `exit` mark at the foot of this script reports. They are not `local` because
# a run's last attempt is what every line below reads. Everything else the watchdog needs is,
# so the list above is the whole of what this function says to the rest of the script: the
# launch stamps `$t0` (the subtraction below turns it into `secs`) and `$a0` (the awake
# clock's, the hard timeout's baseline), the loop's clock reading `$t` and its silence measure
# `$silence`, and `$rc`, the leaf's own raw exit code — which `status` already summarises into
# the vocabulary everything below speaks, so nothing down there reads the number itself.
# `$pid` is the one non-answer that must stay global anyway: `kill_tree` is a separate
# function and reads it.
attempt_once() {
  local t0 a0 t silence rc last_m seen_at m prev_t prev_a a asleep
  : > "$log"
  rm -f "$rcfile"

  # Both clocks are read before the leaf starts, one straight after the other: a leaf that
  # moves time before the second reading would otherwise land between them, and the awake
  # time it moved would read as time asleep (issue #472).
  t0="$(now)"
  a0="$("$awake_clock")"
  prev_t="$t0" prev_a="$a0"

  # Launch the leaf in its own process group (job-control monitor mode) so we can kill the
  # whole tree — including any grandchild like `sleep` — in one signal. A trailing rc file
  # marks natural completion without blocking the watch loop on `wait`.
  set -m
  ( "$@" >"$log" 2>&1; echo $? > "$rcfile" ) &
  pid=$!
  set +m

  status="" reason="" rc=0
  # The heartbeat's two readings must come off ONE clock. `now` and a file's mtime are two
  # (issue #300): `date +%s` counts whole seconds of this machine's wall clock, while the log's
  # mtime is whatever the filesystem stamped the leaf's last write with, and subtracting one
  # from the other reads every difference between them as silence — a scheduling delay landing
  # either side of a second boundary, a stamp a suite moved, a clock that stepped. So the
  # watchdog does not ask "how old is the log"; it asks "how long since I last SAW it change",
  # and both halves of that subtraction are `now`. The mtime is used only as the change
  # detector — any different value is a write, whatever it says about when — so its own scale
  # never reaches `$silence`.
  if (( heartbeat_watched )); then last_m="$(mtime_of "$log")"; seen_at="$t0"; fi
  # A suspended machine is not a silent leaf (issue #472): whatever the wall clock moved across
  # one poll beyond what the awake clock moved is time the machine spent asleep, and the
  # heartbeat window is slid forward by it so it does not count as silence. The hard timeout
  # needs no such slide: it is measured on the awake clock alone, from `$a0`. A negative gap is
  # slid too, unclamped: the two clocks are read a moment apart, so a whole-second tick can land
  # between them and one poll's gap is +1 and the next -1; summed, the gaps telescope to exactly
  # the wall time the awake clock did not see, where clamping each at zero would keep every +1.

  while :; do
    if [[ -f "$rcfile" ]]; then
      rc="$(cat "$rcfile" 2>/dev/null || echo 1)"
      if [[ "$rc" == "0" ]]; then status="success"; else status="failure"; fi
      break
    fi
    t="$(now)"
    a="$("$awake_clock")"
    asleep=$(( (t - prev_t) - (a - prev_a) ))
    seen_at=$(( ${seen_at:-0} + asleep ))
    prev_t="$t" prev_a="$a"
    if (( a - a0 >= timeout )); then
      status="killed-stuck"; reason="hard timeout ${timeout}s exceeded"; kill_tree; break
    fi
    if (( heartbeat_watched )); then
      m="$(mtime_of "$log")"
      if [[ "$m" != "$last_m" ]]; then last_m="$m"; seen_at="$t"; fi
      silence=$(( t - seen_at ))
      # Strict '>' for the one rounding the reading above still has: `silence` is a difference
      # of two whole-second `now` readings, so a sub-second gap straddling a second boundary
      # reads as a whole second of it. That must not kill an active or just-relaunched leaf at
      # exactly the window; a genuine hang keeps climbing past it and is still killed.
      if (( silence > heartbeat )); then
        status="killed-stuck"; reason="no heartbeat for ${silence}s (window ${heartbeat}s)"
        kill_tree; break
      fi
    fi
    sleep "$poll"
  done

  # A kill that landed on a leaf which had already answered is not a stuck one: the rule and
  # its reasons are `recover_finished_leaf`'s, above, and it is a no-op on every other status.
  recover_finished_leaf

  wait "$pid" 2>/dev/null || true
  # Stopped here rather than where the mark is written, so the count is the attempt's own
  # time and not that plus whatever the retry loop and the status line cost after it. Read
  # off the awake clock, like the hard timeout, so a suspend is not counted (issue #486).
  secs=$(( $("$awake_clock") - a0 ))
}

# The three assignments every mark below is written under, read once. A refusal leaves this
# empty — a failed command substitution still assigns, the empty stdout the refusal printed
# — and that emptiness is the whole of "leaf_role could not read this name" for `mark`
# to test. leaf_role and leaf_model are functions now (lib/leaf-model.sh, sourced above,
# pulls in lib/leaf-role.sh too), called in place of the subprocesses this used to fork —
# the `$(...)` around each still forks a subshell to run in, so a refusal's `return 2`
# reaches this `||` exactly the way the old subprocess's `exit 2` did.
role="$(leaf_role "$name")" || role=""

# The model this leaf runs on, resolved here beside the role and from the same name (issue
# #171) — so the value the `launch` mark reports below is the one the launch itself was
# decided by, rather than a second reading of the environment that a caller could have
# changed in between. A refusal — leaf_model returns 2 on a value it can reject without a
# network — leaves this empty the way `role` is left empty above; a bad value is preflight's
# to stop, before any leaf.
model="$(leaf_model "$name")" || model=""

# Exported, because the leaf is a command this script does not build: `supervise.sh <name>
# <cmd> [args…]` is handed an argv and runs it verbatim, so the choice cannot be spliced into
# it as a flag without this script knowing which of its callers' command lines would accept
# one. The environment is the seam every leaf already inherits, and `run-leaf.sh` — the one
# place a `claude` command line is built — turns a non-empty value into `--model <value>` and
# an empty one into no flag at all. Empty is exported too rather than left unset, so a leaf
# cannot inherit a stale value from the conductor's own shell.
export VERI_LEAF_MODEL="$model"

# The skill's own commit, resolved once per supervision and exported so every mark below
# carries it in `skill_commit` — what that key is for, and why a run needs it at all, is
# event.sh's header (issue #165). What is this script's to say is where the sha is asked of:
# `$HERE`, the directory the running scripts live in, and not the cwd, which is the issue's
# worktree. The two are different repositories' HEADs, and the one a reader needs is the code
# that ran. Exported rather than passed through `mark`'s `env` line, which is leaf-role.sh's
# output verbatim and stays that.
#
# A skill installed from something other than a clone has no sha to give, and there the
# resolution spells its absence as the literal `unknown` rather than leaving the key empty:
# a reader of a log full of shas cannot tell an unresolvable commit from a writer that was
# handed nothing. The default covers both ways git declines — a refusal (no repository) and
# an empty answer — because the key's promise is a value, not an exit code.
#
# A skill run from run-conductor.sh's pinned snapshot is no clone either, but its commit is
# known: the launch exports it as VERI_SKILL_COMMIT (issue #251), and that is the answer
# when git has none of its own.
skill_commit="$(git -C "$HERE" rev-parse HEAD 2>/dev/null)" || skill_commit=""
export VERI_SKILL_COMMIT="${skill_commit:-${VERI_SKILL_COMMIT:-unknown}}"

# mark <event> [key=value …] — append one line to the run's event log (issue #107,
# ADR-0014), or nothing at all. Both marks below go through here, so what the two have in
# common is said once rather than in each:
#
#   * `$role` is deliberately unquoted — it is the `VERI_ACTOR=… VERI_PHASE=… VERI_ATTEMPT=…`
#     line leaf-role.sh prints for `env` to word-split into event.sh's environment, which is
#     the calling convention that script documents.
#   * a name leaf-role.sh cannot read refuses with its own diagnostic on stderr and empty
#     stdout, and then nothing is logged at all: a line whose actor and attempt were invented
#     would be worse than the absent one a reader is already told to tolerate.
mark() {
  [[ -n "$role" ]] || return 0
  # shellcheck disable=SC2086  -- intentional word-split of leaf_role's assignments
  env $role "$HERE/event.sh" "$@"
}

# One leaf owns a worktree at a time (issue #471). In #446 `verify-green` was launched while
# `revise-green-1` was still running, and the two wrote one tree at once: `.tdd/<name>.pid`
# only answers for a leaf of this name, and SKILL.md removes it before every launch. So every
# supervision also records itself in `.tdd/leaf.owner` — `<pid> <name>`, a file no launch
# recipe removes — and a launch finding a live pid there is refused with exit 2, since no
# answer can be obtained from a leaf that would share its tree. A record whose process is gone
# refuses nothing: `kill -0` sends no signal and answers only whether the pid exists.
#
# A `verdict-<phase>` supervision reads the record but never writes it: it is the wrapper
# around the `verify-<phase>` supervision verify.sh launches inside it, and that one is the
# leaf; a record written here would have the verifier refused by its own wrapper.
#
# A `conductor-<n>` supervision reads the record but never writes it (#102): parallel-conductors.sh
# launches several from one checkout at once, and each conductor's leaves work in that issue's
# own worktree `.tdd/wt/<n>`, never in the tree this supervision runs from — so the conductors
# share no tree for the record to guard, and a record written by one would have the next refused.
ownerfile=".tdd/leaf.owner"
owns_tree="$heartbeat_watched"
case "$name" in conductor-*) owns_tree=0 ;; esac
if [[ -s "$ownerfile" ]]; then
  read -r owner_pid owner_name < "$ownerfile"
  if kill -0 "$owner_pid" 2>/dev/null; then
    echo "supervise: refusing to launch $name: leaf ${owner_name:-?} (pid $owner_pid) is still alive in this worktree" >&2
    exit 2
  fi
fi
[[ "$owns_tree" == 0 ]] || printf '%s %s\n' "$$" "$name" > "$ownerfile"

# The run's `launch` mark, carrying the keys the header lists. Written here because this is
# the one choke point every leaf goes through: a log missing one is a leaf nothing recorded
# starting, and every key the mark carries is either what this script was handed — the name,
# the argv — or what it resolved from that above. `$*` joins argv with a single space, the
# spelling event.sh's header quotes for a `cmd=` payload.
#
# Once per supervision, not once per attempt — which is what its place here shows: outside
# the loop below, so a retried attempt passes it by. That attempt is the `retry` mark's to
# report, and a second `launch` would read as a second leaf.
#
# `model=` is written on every launch, empty when the run chose none: event.sh's rule for
# context keys is that an absent key and a chosen-nothing key must not look alike, and a
# per-model cost comparison joins verdicts and revise counts on exactly this field.
mark launch name="$name" cmd="$*" model="$model"

# This supervisor's own pid, recorded before any leaf is launched (issue #173), so
# wait-leaf.sh can tell a supervisor that died without writing `$exitfile` from one still
# watching a slow leaf. `$$` rather than `$BASHPID`: this is the top-level shell.
echo $$ > "$pidfile"

# The completion file is cleared here, before any leaf runs, so that a record found in it at
# the foot of this script can only be one this supervision's leaf wrote — which is what the
# write down there defers to (issue #415). A file left under this name by an earlier
# supervision would otherwise be read as this leaf's own answer.
rm -f "$exitfile"

# A supervisor sent TERM, INT or HUP must still leave an answer (issue #173). The leaf runs in
# a process group of its own (`set -m` in attempt_once), so the signal never reaches it: the
# handler takes the leaf's tree down with `kill_tree`, then records 2 in the completion file —
# no answer could be obtained — so a detached wait ends instead of polling forever. KILL
# cannot be trapped; wait-leaf.sh's liveness check is what covers that one.
on_signal() {
  [[ -z "${pid:-}" ]] || kill_tree
  printf '2\n' > "$exitfile"
  exit 2
}
trap on_signal TERM INT HUP

# The evidence a killed-stuck attempt leaves behind, kept before the next one destroys it
# (issue #409). `attempt_once` truncates `.tdd/<name>.log` at its top, and the tree a killed
# leaf produced is never committed to the work branch — a green commit lands only after
# verify-green PASSes — so between a kill and the relaunch is the only moment either exists.
# This is the one place both can be caught: the kill is decided here and the retry loop is
# this script's own.
#
# `stuck` is the mark, the word the issue's list of troubles uses for this one, and it ends
# the names of the copies so a reader pairs them with the `retry`/`exit` event that carries
# the same cause. The attempt number is the supervisor's own count of tries, not the one the
# leaf's NAME carries (`revise-green-2`): two attempts of one supervision share that name, so
# filing both under it would have the second overwrite the first — which is the loss this is
# here to prevent.
#
# A no-op on every other status, so an untroubled leaf costs nothing, and on a run with no
# issue/step in its environment or no HEAD to hang a commit off, which is what the suites'
# bare temporary directories are. Those three tests are this script's alone; what happens once
# they pass — the snapshot, the copies, and the rule that a failed preservation is said on
# stderr and dropped rather than allowed to change what this supervision reports, the way
# harvest-usage.sh's failure is — is `preserve_attempt`'s, shared with verify.sh's own
# troubled-step branch (lib/preserve.sh).
preserve_killed_attempt() {
  local attempt="$1"
  [[ "$status" == "killed-stuck" ]] || return 0
  [[ -n "${VERI_ISSUE:-}" && -n "${VERI_STEP:-}" ]] || return 0
  git rev-parse --verify -q HEAD >/dev/null 2>&1 || return 0
  preserve_attempt "supervise[$name]" "$VERI_ISSUE" "$VERI_STEP" "$name" "$attempt" stuck
}

# First attempt plus up to $retries extra attempts. A normal result (success/failure)
# short-circuits; only killed-stuck is retried.
tries=0
while :; do
  attempt_once "$@"
  # Before the loop decides anything: on the relaunch path this runs while the killed
  # attempt's log and tree are still on disk, and on the last attempt it is the final
  # killed-stuck one being kept. One call site rather than two, because the two are the same
  # act at two moments.
  preserve_killed_attempt "$(( tries + 1 ))"
  [[ "$status" == "killed-stuck" ]] || break
  (( tries >= retries )) && break
  tries=$(( tries + 1 ))
  # The `retry` mark (issue #107, ADR-0014). It carries the watchdog's own diagnosis of why
  # the attempt just killed had to be abandoned, which nothing else in the run can say: the
  # status line at the foot of this script reports the LAST attempt's reason, so a leaf that
  # recovered reports none at all. Written beside the human-readable line that already says
  # the same thing to stderr, so the two cannot drift apart.
  mark retry cause="$reason"
  echo "supervise[$name]: retry $tries/$retries after killed-stuck" >&2
done

case "$status" in
  success)      ec=0 ;;
  failure)      ec=1 ;;
  killed-stuck) ec=2 ;;
  *)            ec=2; status="killed-stuck"; reason="${reason:-unknown}" ;;
esac

# The leaf's own closing accounting, harvested here rather than asked for in the conductor's
# prose (issue #163): this script owns `.tdd/$name.log` and is the choke point every leaf goes
# through, so a harvest written here cannot be missing from the leaves prose forgot — which is
# the shape of the bug #163 reports, where harvest-usage.sh existed for a whole release and no
# run ever called it. Once per supervision, after the last attempt, for the same reason the
# `launch` and `exit` marks are: the log it reads is the last attempt's. Ahead of the `exit`
# block below rather than inside it, so that block stays the one thing it is — the status line,
# the payload the mark carries, and the mark — with nothing between the array and its only
# reader.
#
# Its status is discarded — a log with no closing record (a killed leaf) is its exit 3, and it
# already says so on stderr — because this script's answer is the leaf's 0/1/2, measured above
# and written below. A broken harvester must not turn a passing leaf into a bail. Its stdout
# goes to stderr for the same reason `cat "$log"` below is the last word on this script's own:
# that stream is piped straight into parse-verdict.sh.
"$HERE/harvest-usage.sh" "$name" >&2 || true

# The `exit` mark (issue #107, ADR-0014), beside the human-readable status line that says the
# same thing to stderr, so the two cannot drift apart. It carries the three things only this
# script holds at this moment: the 0/1/2 of the exit-code contract — this supervisor's own
# code, not the leaf's raw one — the watchdog's kill cause, and the awake seconds the last
# attempt took, which is the `$secs` attempt_once measured for it. That duration is the first
# anything in a run records, so no reader can recover it by subtracting two other marks.
# `cause=` is passed only when there is one: what a run with no kill would put there is a
# fiction, and an absent key reads as the absence it is.
echo "supervise[$name]: $status${reason:+ — $reason}" >&2
# The payload is assembled in an array rather than spliced in with an unquoted `${reason:+…}`:
# the kill cause carries spaces ("no heartbeat for 3s (window 2s)"), so that expansion would
# word-split it into four arguments, and the three without an `=` would land in the JSON under
# keys that are whole phrases. The array is never empty, so quoting it is enough on its own —
# an empty one expanded under `set -u` is an error on the bash 3.2 this suite still runs on.
payload=(status="$ec")
[[ -z "$reason" ]] || payload+=(cause="$reason")
payload+=(secs="$secs")
mark exit "${payload[@]}"
cat "$log"
# The completion file: this supervisor's OWN status code, on every path including
# killed-stuck (where the leaf's subshell never gets to write `.tdd/<name>.rc` at all).
# A leaf launched detached is waited on by polling this, so it must carry the 0/1/2 of the
# exit-code contract rather than the leaf's raw code that `.rc` records.
#
# Unless the leaf recorded a code in it first (issue #415). A verifier is launched as a
# wrapper that runs `verify.sh` and writes ITS exit code to this very file — SKILL.md's
# `supervise.sh verdict-<phase> bash -c "… ; echo \$? > .tdd/verdict-<phase>.exit"` — and that
# code is the verdict the conductor branches on: 1 a REJECT to revise, 2 a verdict nothing
# could be parsed from. The wrapper's own status is `echo`'s, which is 0 whatever the verifier
# said, so overwriting the record here would hand every rejected verification on as a pass.
# The file was cleared before the leaf was launched, so a record present now is this leaf's.
# It stands only when `number_in` accepts it, which is wait-leaf.sh's own test for an answer
# (lib/number-in.sh, shared with it for that reason): a truncated or garbled record is no
# answer at all, and a wait left polling one to its deadline is the failure this file exists
# to prevent. Its stdout is discarded — only the verdict on the record is wanted here, not the
# record, which is already where it belongs.
number_in "$exitfile" >/dev/null || printf '%s\n' "$ec" > "$exitfile"
exit "$ec"
