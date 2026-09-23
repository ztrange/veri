# lib/background.sh — sourced, not run: defines `bg_start` and `bg_kill`, the one place a
# veri script or suite starts a background process and later ends it (issue #424).
#
# The shape this replaces is `cmd & … kill %1`. A job spec names a row in the JOB TABLE of
# the shell that started the process, and that table dies with the shell: once it is gone
# the number means nothing, the child is reparented to PID 1, and nothing is left that knows
# its identity. Observed 2026-09-22 on this machine: ten orphaned busy-loops, all PPID 1,
# ~988% of CPU between them, twelve and thirteen hours old, whose `kill %1 %2 … 2>/dev/null`
# had been evaluated in a context whose job table no longer held them — and the redirection
# swallowed the complaint. A pid is a system-wide name instead, so a kill that uses one works
# from any shell, including one that never started the process.
#
# `return`, never `exit`: this runs in the caller's own shell once sourced, so an `exit` here
# would tear the caller down where a refusal is meant to be an answer it reads.

# bg_start <record> <cmd> [args…] — run <cmd> in the background and append its pid to
# <record>, the file `bg_kill` later reads. `$!` is the pid of the child the shell just
# forked, asked for immediately, because a later `$!` is some other background command's.
bg_start() {
  local record="${1:?usage: bg_start <record> <cmd> [args...]}"
  shift
  "$@" &
  printf '%s\n' "$!" >> "$record"
}

# bg_kill <record> — kill every process <record> names. A pid whose process is already gone is
# not an error — the point of the call is that nothing recorded is left running.
bg_kill() {
  local record="${1:?usage: bg_kill <record>}" pid
  while read -r pid; do
    kill "$pid" 2>/dev/null || true
  done < "$record"
}
