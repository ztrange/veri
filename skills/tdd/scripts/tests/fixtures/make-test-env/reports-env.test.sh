#!/usr/bin/env bash
# Fixture for make-test-env.test.sh. It lives under fixtures/ so `make test`'s own glob never
# picks it up: only that suite runs it, and only through the recipe, as `make test TESTS=<this>`.
#
# It judges nothing. It writes down six facts about the environment the recipe ran it in —
# the locale, the resolved real git (still handed down as OFFLINE_REAL_GIT), what the `git` on
# PATH symlinks straight to, the GIT_EXEC_PATH and GIT_TEMPLATE_DIR it was given, and whether its stdin is /dev/null — one `key=value` line each to
# $PROBE_OUT, and reports a pass so the recipe itself stays green. Whether those facts are the
# right ones is the suite's question, asked of the file.
#
# stdin is compared to /dev/null by device and inode (`-ef`) rather than read from: a read with
# a timeout cannot tell "at end-of-file" from "open and silent" on bash 3.2, whose `read -t`
# returns 1 for both. The open-and-silent case is the one that matters — it is what left the
# stub claude's `cat` blocked for 28 minutes under a leaf's backgrounded `make test`.
set -uo pipefail

out="${PROBE_OUT:?PROBE_OUT names the file this fixture reports to}"
if [[ /dev/stdin -ef /dev/null ]]; then stdin=devnull; else stdin=inherited; fi
# git on PATH is a symlink straight to the resolved real binary now, not a bash wrapper —
# `readlink` (not `-f`, which BSD's build resolves differently) names its immediate target,
# which is what OFFLINE_REAL_GIT used to be handed to a shim for.
git_path="$(command -v git 2>/dev/null || echo '<none>')"
git_link_target="$(readlink "$git_path" 2>/dev/null || echo '<not-a-symlink>')"
{
  printf 'LC_ALL=%s\n' "${LC_ALL-<unset>}"
  printf 'OFFLINE_REAL_GIT=%s\n' "${OFFLINE_REAL_GIT-<unset>}"
  printf 'GIT_LINK_TARGET=%s\n' "$git_link_target"
  printf 'GIT_EXEC_PATH=%s\n' "${GIT_EXEC_PATH-<unset>}"
  printf 'GIT_TEMPLATE_DIR=%s\n' "${GIT_TEMPLATE_DIR-<unset>}"
  printf 'stdin=%s\n' "$stdin"
} > "$out"
echo "1 passed, 0 failed"
