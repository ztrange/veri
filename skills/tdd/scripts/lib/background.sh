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
# A kill that is never issued is the other half of the same incident, and it leaves no trace
# at all: the starting shell exits, the child is reparented to PID 1, and the only shell that
# ever knew what it was is gone. So `bg_start` also arms an EXIT trap that says so on the
# starting shell's own stderr, naming the pid and the command — the survivor is then a line
# someone can act on rather than a process nobody can name.
#
# `return`, never `exit`: this runs in the caller's own shell once sourced, so an `exit` here
# would tear the caller down where a refusal is meant to be an answer it reads.

# The record files this shell has started something into, read by the EXIT trap below. A
# record is added once, so a shell that starts two processes into one file still reports each
# survivor once.
_bg_records=()

# _bg_report_survivors — one line on stderr per recorded process still running. Called from
# the EXIT trap `bg_start` arms, so it runs in the shell that did the starting, which is the
# last moment anything knows what the pid was.
_bg_report_survivors() {
  local record pid cmd
  for record in ${_bg_records+"${_bg_records[@]}"}; do
    [[ -r "$record" ]] || continue
    while read -r pid cmd; do
      if kill -0 "$pid" 2>/dev/null; then
        printf 'background process still running at exit: pid %s started by %s (kill it: kill %s)\n' \
          "$pid" "$cmd" "$pid" >&2
      fi
    done < "$record"
  done
}

# bg_start <record> <cmd> [args…] — run <cmd> in the background and append its pid and the
# command to <record>, the file `bg_kill` later reads. `$!` is the pid of the child the shell
# just forked, asked for immediately, because a later `$!` is some other background command's.
bg_start() {
  local record="${1:?usage: bg_start <record> <cmd> [args...]}"
  shift
  "$@" &
  printf '%s %s\n' "$!" "$*" >> "$record"
  _bg_remember "$record"
}

# _bg_remember <record> — add <record> to the list the EXIT trap reads, at most once, and arm
# that trap the first time this shell has anything to report. Once is the whole point: a shell
# that started two processes into one record would otherwise read it twice at exit and name
# every survivor in it twice over.
_bg_remember() {
  local known
  for known in ${_bg_records+"${_bg_records[@]}"}; do
    [[ "$known" == "$1" ]] && return 0
  done
  _bg_records+=("$1")
  trap _bg_report_survivors EXIT
}

# bg_kill <record> — kill every process <record> names. A pid whose process is already gone is
# not an error — the point of the call is that nothing recorded is left running.
bg_kill() {
  local record="${1:?usage: bg_kill <record>}" pid
  while read -r pid _; do
    kill "$pid" 2>/dev/null || true
  done < "$record"
}
