#!/bin/sh
# supervise.sh — launch one leaf under a heartbeat + hard-timeout watchdog: a shim over veri/supervise.py.
#
# This is the one choke point where stuck-detection policy lives (ADR-0002): every leaf is
# launched through here, never directly. The supervisor spawns the leaf in the background
# and watches it two ways:
#   * heartbeat — activity on the leaf's progress log within a window tells "slow but
#     working" from "hung". A leaf silent past the window is killed.
#   * hard timeout — a leaf that exceeds the time cap is killed even if still noisy.
# Both windows count only time the machine spent awake. The clock is Python's
# clock_gettime(CLOCK_UPTIME_RAW), else the monotonic clock (CLOCK_MONOTONIC): on macOS that is mach_absolute_time(), which does not advance while the
# Mac is asleep, and on Linux it is CLOCK_MONOTONIC, which does not advance while the machine
# is suspended. The wall clock (`date +%s`) keeps running through a suspend, so an hour with
# the lid closed would read as an hour of silence and kill a leaf that never hung — the
# heartbeat slides by whatever the wall clock moved across one poll beyond this clock, and the
# hard timeout is measured on this clock alone.
# The heartbeat is the leaf's; a `verdict-<phase>` supervision is the wrapper around a
# verifier leaf that is already supervised under its own name, so it keeps only the hard
# timeout and never kills for a silence that is the wrapper's rather than the verifier's
# (the reasoning is where `watched` is set in veri/supervise.py).
# A killed leaf is retried up to VERI_STUCK_RETRIES times (default 1) on a fresh attempt; if
# it still can't recover it is reported as `killed-stuck`, which the conductor turns into a
# clean bail — unless its log already holds the leaf's closing result record, in which case the
# kill landed on a finished process and the leaf's own outcome is reported instead.
# A kill and a rendered verdict can coexist because the watchdog's only sensor for
# "the leaf is done" is its `sh -c` wrapper's rc file, and the leaf's stream finishes before the
# wrapper writes `.tdd/<name>.rc` — so between the last line of output and that file
# landing there is a window in which a finished leaf is indistinguishable from a silent
# one, and a kill is not proof that no answer was obtained.
#
# usage: supervise.sh <name> <cmd> [args...]
#
# The leaf's combined stdout+stderr is captured to `.tdd/<name>.log` (the progress log the
# heartbeat watches) and echoed to this script's stdout on completion, so a verifier leaf
# can be piped straight into parse-verdict.sh.
#
# Status: exit 0 success · 1 leaf-failure · 2 killed-stuck, or a leaf that exited 2 itself.
# A one-line status (with the kill cause) is written to stderr, and the same code is recorded
# in the completion file `.tdd/<name>.exit` on every path — so a leaf launched detached can
# be waited on by polling that file instead of by reading this script's stdout. The one
# exception is a leaf that recorded a code in that file itself, as the verifier's launch
# wrapper does with `verify.sh`'s verdict code: the leaf's own record is the answer and is
# left alone.
#
# Three kinds of event are appended to the run's event log, `.tdd/events.jsonl` (ADR-0014):
# one `launch` — the leaf's name, the command behind it, the model it runs on
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
exec python3 "$(dirname "$0")/veri/supervise.py" "$@"
