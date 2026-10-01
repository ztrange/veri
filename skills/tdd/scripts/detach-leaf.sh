#!/usr/bin/env bash
# detach-leaf.sh — launch a leaf into a session of its own and return at once.
#
# Usage:   detach-leaf.sh <cmd> [args…]
#
# This is the detach that `nohup … &` was not. `nohup` only makes the child ignore SIGHUP;
# it leaves the child in the PROCESS GROUP of the Bash call that launched it, so a harness
# that signals that group when the call ends takes the leaf with it. Observed 2026-09-12
# 23:43 UTC on a conductor: the Bash call came back `Exit code 144`, the verifier's
# `.tdd/verdict-red.exit` was never written, and `verify.sh red` was gone. A leaf killed that
# way writes no completion file, so `wait-leaf.sh` returns exit 3 forever and the conductor
# reads that as "still running".
#
# The move that survives it is `setsid`: the child becomes the leader of a new session, and
# so of a new process group, which a signal aimed at the launching call's group can no longer
# reach. macOS ships no `setsid` binary, so the call is python3's — already a dependency here
# (`event.sh`, `extract-result.sh`, `harvest-usage.sh` all exec it). `os.execvp` then replaces
# that python with the argv, so nothing of the shim is left in the process tree.
#
# `&`, not `exec`: the promise is that the launch RETURNS, and the caller then blocks on
# `wait-leaf.sh` in the foreground. Running the leaf in the foreground here would detach it
# perfectly well and still hang the Bash call that was supposed to come straight back.
set -uo pipefail

[[ $# -gt 0 ]] || { echo "usage: detach-leaf.sh <cmd> [args…]" >&2; exit 2; }

python3 -c 'import os, signal, sys; signal.signal(signal.SIGPIPE, signal.SIG_DFL); os.setsid(); os.execvp(sys.argv[1], sys.argv[1:])' "$@" &
