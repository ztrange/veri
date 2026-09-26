# lib/appendable.sh — sourced, not run: defines `make_appendable`, the one place a file is made
# safe to `>>` onto (#102).
#
# Two callers write veri's ignore lines into a shared info/exclude that belongs to the caller:
# ensure-run-state-ignored.sh its three-line run-state rule, parallel-conductors.sh its `.tdd/*`
# before any conductor writes there. Both need exactly this, so it is written once: two copies
# could drift into disagreeing about the newline guard, and only one caller's append would then
# survive a file whose last line has no newline.
#
# `return`, never `exit`: this runs in the caller's own shell.

# make_appendable <file> — after this, a `>>` onto <file> starts a line of its own.
#
# That means two things. Its directory has to exist — git creates .git/info/exclude itself, so
# that only bites a git dir without `info/`, but `>>` cannot create a parent and would die under
# `set -e` rather than say so. And <file> has to end in a newline, or the append fuses its last
# line with the first appended one into a single line and destroys both: `$(...)` strips trailing
# newlines from what it captures, so a file already ending in one yields the empty string here,
# and a non-empty last byte is exactly the case that needs one added. -s keeps `tail` off a file
# that does not exist yet.
make_appendable() {
  mkdir -p "$(dirname "$1")"
  if [ -s "$1" ] && [ -n "$(tail -c 1 "$1")" ]; then
    echo "" >> "$1"
  fi
}
