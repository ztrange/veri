#!/bin/sh
# test-ceiling.sh — measure the highest test-worker count this machine runs `make test` at with no case timeout: a shim
# over veri/ceiling.py (#4418, PRD 036.2). `make ceiling` is its one entry point; nothing in the procedure, no other
# make target and no CI job runs it, since one ramp is hours of full suites on a machine left idle for it.
#
# usage: test-ceiling.sh [--max <n>]
#          Runs `make test`'s full selection once per step, under the case timeouts `make test` applies
#          (VERI_PYTEST_TIMEOUT, timeout marks, PROCESS_CASE_TIMEOUT), at VERI_PYTEST_WORKERS=<w> for w = 2, 4, 6, …
#          up to the logical cores, or to <n>.
# Exit:    0 the ceiling, the top step with no case timeout, printed
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/ceiling.py" "$@"
