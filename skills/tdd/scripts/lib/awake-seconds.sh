#!/usr/bin/env bash
# lib/awake-seconds.sh — sourced, not run: defines `awake_seconds`.
#
# awake_seconds — echo whole seconds of the system-wide awake clock.
awake_seconds() {
  python3 -c 'import time; print(int(time.clock_gettime(getattr(time, "CLOCK_UPTIME_RAW", time.CLOCK_MONOTONIC))))'
}
