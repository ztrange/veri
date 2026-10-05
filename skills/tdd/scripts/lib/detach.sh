#!/usr/bin/env bash
# lib/detach.sh — sourced, not run: defines `detach_exec`.
#
# detach_exec <cmd> [args…] — replace the calling process with <cmd>, run as the leader of a
# session of its own, with SIGPIPE at its default. Call it with `&`: the backgrounded
# subshell becomes <cmd>, so `$!` is <cmd>'s pid and the session leader's.
detach_exec() {
  exec python3 -c 'import os, signal, sys; signal.signal(signal.SIGPIPE, signal.SIG_DFL); os.setsid(); os.execvp(sys.argv[1], sys.argv[1:])' "$@"
}
