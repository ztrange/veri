#!/usr/bin/env bash
# Fixture for make-test-env.test.sh. It lives under fixtures/ so `make test`'s own glob never
# picks it up: only that suite runs it, and only through the recipe, as `make test TESTS=<this>`.
#
# It judges nothing. It writes down three facts about the environment the recipe ran it in —
# the locale, the git the offline shim forwards to, and whether its stdin is /dev/null — one
# `key=value` line each to $PROBE_OUT, and reports a pass so the recipe itself stays green.
# Whether those facts are the right ones is the suite's question, asked of the file.
#
# stdin is compared to /dev/null by device and inode (`-ef`) rather than read from: a read with
# a timeout cannot tell "at end-of-file" from "open and silent" on bash 3.2, whose `read -t`
# returns 1 for both. The open-and-silent case is the one that matters — it is what left the
# stub claude's `cat` blocked for 28 minutes under a leaf's backgrounded `make test`.
set -uo pipefail

out="${PROBE_OUT:?PROBE_OUT names the file this fixture reports to}"
if [[ /dev/stdin -ef /dev/null ]]; then stdin=devnull; else stdin=inherited; fi
{
  printf 'LC_ALL=%s\n' "${LC_ALL-<unset>}"
  printf 'OFFLINE_REAL_GIT=%s\n' "${OFFLINE_REAL_GIT-<unset>}"
  printf 'stdin=%s\n' "$stdin"
} > "$out"
echo "1 passed, 0 failed"
