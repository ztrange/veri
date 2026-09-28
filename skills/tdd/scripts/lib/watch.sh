#!/bin/sh
# lib/watch.sh — sourced, not run: defines `watch_stat` and `watch_snapshot`.
#
# watch_stat — read NUL-separated paths on stdin and print one checksum line per file.
# watch_snapshot — print `watch_stat` over the tracked files.
#
# hazard: the Makefile's `watch` recipe sources this under /bin/sh, so it is POSIX sh, not bash.
watch_stat() {
  xargs -0 cksum 2>/dev/null
}

watch_snapshot() {
  git ls-files -z | watch_stat
}
