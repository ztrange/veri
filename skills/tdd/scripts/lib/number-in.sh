# lib/number-in.sh — sourced, not run: defines `number_in`, the one place a file is read as
# a recorded number (issue #415).
#
# Two callers, and they have to agree. `wait-leaf.sh` polls `.tdd/<name>.exit` and ends the
# wait only on what this accepts; `supervise.sh`, at the foot of a supervision, leaves a
# record its own leaf wrote in that same file alone only when this accepts it, and overwrites
# it with the supervisor's code otherwise. So the two are one decision — *is there an answer
# in this file?* — asked from both ends of a detached launch. Written out twice, a predicate
# widened on one side would have the supervisor preserve a record the wait then polls past to
# its deadline, or narrowed, have it destroy a verdict the wait would have accepted. That is
# the failure the deferral exists to prevent, so the predicate is not allowed to be a
# coincidence between two files.
#
# `return`, never `exit`: this runs in the caller's own shell.

# number_in <file> — echo the plain number on the file's first line, or fail when there is
# none. A file seen between its creation and its write reads back empty, and an empty read is
# not a number, so that case fails too and the caller keeps polling.
number_in() {
  local n=""
  [[ -f "$1" ]] || return 1
  read -r n < "$1" 2>/dev/null || true
  [[ "$n" =~ ^[0-9]+$ ]] || return 1
  printf '%s\n' "$n"
}
