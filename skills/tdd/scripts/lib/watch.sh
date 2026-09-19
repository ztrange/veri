# lib/watch.sh — sourced, not run: defines `watch_snapshot`, one poll pass of `make watch`
# (#340), and `watch_stat`, the stat wrapper that pass calls. The Makefile's `watch` recipe
# sources it, so it is POSIX sh, not bash: make runs recipes under /bin/sh.
#
# watch_stat — reads the NUL-separated tracked paths on stdin and prints one checksum line per
# file. One call per pass whatever the file count: xargs hands every path to one cksum rather
# than forking one per file, which is what keeps polling cheap enough to beat installing
# fswatch or entr.
watch_stat() {
  xargs -0 cksum 2>/dev/null
}

# watch_snapshot — prints the tree's state as the loop compares it: the tracked files
# (`git ls-files`, so an untracked scratch file never triggers a rerun) through `watch_stat`.
# Two passes print the same text exactly when no tracked file's content changed.
watch_snapshot() {
  git ls-files -z | watch_stat
}
