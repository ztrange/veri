#!/usr/bin/env bash
# supervise.sh — launch one leaf under a heartbeat + hard-timeout watchdog.
#
# This is the one choke point where stuck-detection policy lives (ADR-0002): every leaf is
# launched through here, never directly. The supervisor spawns the leaf in the background
# and watches it two ways:
#   * heartbeat — activity on the leaf's progress log within a window tells "slow but
#     working" from "hung". A leaf silent past the window is killed.
#   * hard timeout — a leaf that exceeds the wall-clock cap is killed even if still noisy.
# A killed leaf is retried up to VERI_STUCK_RETRIES times (default 1) on a fresh attempt; if
# it still can't recover it is reported as `killed-stuck`, which the conductor turns into a
# clean bail.
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
# polling that file instead of by reading this script's stdout.
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
# attempts after the first when a leaf is killed-stuck (default 1) · VERI_MODEL /
# VERI_MODEL_DEVELOPER / VERI_MODEL_VERIFIER the model this leaf's role runs on, resolved
# through leaf-model.sh and exported to the leaf as VERI_LEAF_MODEL (all unset by default,
# which is no `--model` flag at all).
set -uo pipefail

name="${1:?usage: supervise.sh <name> <cmd> [args...]}"
shift
[[ $# -ge 1 ]] || { echo "supervise: missing <cmd>" >&2; exit 2; }

HERE="$(cd "$(dirname "$0")" && pwd)"

heartbeat="${VERI_HEARTBEAT:-180}"
timeout="${VERI_TIMEOUT:-900}"
poll="${VERI_POLL:-1}"
retries="${VERI_STUCK_RETRIES:-1}"

mkdir -p .tdd
log=".tdd/$name.log"
rcfile=".tdd/$name.rc"
exitfile=".tdd/$name.exit"

now() { date +%s; }

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
  # brief grace, then make sure it is gone
  for _ in 1 2 3 4 5; do kill -0 "$pid" 2>/dev/null || return 0; sleep 0.1; done
  kill -KILL -"$pid" 2>/dev/null || kill -KILL "$pid" 2>/dev/null
}

# Run the leaf once on a fresh log/rc, watching for stuck/timeout. Sets three globals, and
# those three are its answers: status/reason, and `$secs` — how many wall seconds this attempt
# took, which the `exit` mark at the foot of this script reports. They are not `local` because
# a run's last attempt is what every line below reads. Everything else the watchdog needs is,
# so the list above is the whole of what this function says to the rest of the script: the
# launch stamp `$t0` (the loop's hard-timeout baseline, and the subtraction below turns it
# into `secs`), the loop's clock reading `$t` and its silence measure `$silence`, and `$rc`,
# the leaf's own raw exit code — which `status` already summarises into the vocabulary
# everything below speaks, so nothing down there reads the number itself. `$pid` is the one
# non-answer that must stay global anyway: `kill_tree` is a separate function and reads it.
attempt_once() {
  local t0 t silence rc
  : > "$log"
  rm -f "$rcfile"

  # Launch the leaf in its own process group (job-control monitor mode) so we can kill the
  # whole tree — including any grandchild like `sleep` — in one signal. A trailing rc file
  # marks natural completion without blocking the watch loop on `wait`.
  set -m
  ( "$@" >"$log" 2>&1; echo $? > "$rcfile" ) &
  pid=$!
  set +m

  t0="$(now)"
  status="" reason="" rc=0

  while :; do
    if [[ -f "$rcfile" ]]; then
      rc="$(cat "$rcfile" 2>/dev/null || echo 1)"
      if [[ "$rc" == "0" ]]; then status="success"; else status="failure"; fi
      break
    fi
    t="$(now)"
    if (( t - t0 >= timeout )); then
      status="killed-stuck"; reason="hard timeout ${timeout}s exceeded"; kill_tree; break
    fi
    silence=$(( t - $(mtime_of "$log") ))
    # Strict '>' so the whole-second clock's ±1s over-read at a second boundary (see the
    # slow-leaf note in supervise.test.sh) can't spuriously kill an active/just-relaunched
    # leaf; a genuine hang keeps climbing past the window and is still killed.
    if (( silence > heartbeat )); then
      status="killed-stuck"; reason="no heartbeat for ${silence}s (window ${heartbeat}s)"
      kill_tree; break
    fi
    sleep "$poll"
  done

  wait "$pid" 2>/dev/null || true
  # Stopped here rather than where the mark is written, so the count is the attempt's own
  # wall time and not that plus whatever the retry loop and the status line cost after it.
  secs=$(( $(now) - t0 ))
}

# The three assignments every mark below is written under, read once. A refusal leaves this
# empty — a failed command substitution still assigns, the empty stdout the refusal printed
# — and that emptiness is the whole of "leaf-role.sh could not read this name" for `mark`
# to test.
role="$("$HERE/leaf-role.sh" "$name")" || role=""

# The model this leaf runs on, resolved here beside the role and from the same name (issue
# #171) — so the value the `launch` mark reports below is the one the launch itself was
# decided by, rather than a second reading of the environment that a caller could have
# changed in between. A refusal — leaf-model.sh exits 2 on a value it can reject without a
# network — leaves this empty the way `role` is left empty above; a bad value is preflight's
# to stop, before any leaf.
model="$("$HERE/leaf-model.sh" "$name")" || model=""

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
VERI_SKILL_COMMIT="$(git -C "$HERE" rev-parse HEAD 2>/dev/null)"
export VERI_SKILL_COMMIT="${VERI_SKILL_COMMIT:-unknown}"

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
  # shellcheck disable=SC2086  -- intentional word-split of leaf-role.sh's assignments
  env $role "$HERE/event.sh" "$@"
}

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

# First attempt plus up to $retries extra attempts. A normal result (success/failure)
# short-circuits; only killed-stuck is retried.
tries=0
while :; do
  attempt_once "$@"
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
# code, not the leaf's raw one — the watchdog's kill cause, and the wall seconds the last
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
printf '%s\n' "$ec" > "$exitfile"
exit "$ec"
