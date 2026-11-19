#!/bin/sh
# test-ceiling.sh — measure the highest test-worker count this machine runs `make test` at with no case timeout: a shim
# over veri/ceiling.py (#4418, PRD 036.2). `make ceiling` is its one entry point; nothing in the procedure, no other
# make target and no CI job runs it, since one ramp is hours of full suites on a machine left idle for it.
#
# usage: test-ceiling.sh [--max <n>]
#          Runs `make test`'s full selection once per step, under the case timeouts `make test` applies
#          (VERI_PYTEST_TIMEOUT, timeout marks, PROCESS_CASE_TIMEOUT), at VERI_PYTEST_WORKERS=<w> for w = 2, 4, 6, …
#          up to the logical cores, or to <n>.
#          A case failing a step by its per-case timeout is re-run alone with one worker: passing alone, the timeout was
#          load and the ramp stops. Each step registers its workers under ~/.veri-pytest-legs and first waits while any
#          other live leg is registered. Exit 0 replaces ~/.veri-test-ceiling (VERI_TEST_CEILING_FILE) whole: the ceiling,
#          the date, the commit, the load average at start, one `<workers> <seconds> <timeouts>` line per step.
# Exit:    0 the ceiling, the top step with no case timeout, printed and recorded
#          1 a load timeout at 2 workers: "no ceiling of at least 2"
#          2 a bad argument, a case hung (timing out alone too) or failing other than by its timeout, named, or a suite
#            run exiting non-zero with no failed case recorded; 1 and 2 leave an earlier record unchanged
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/ceiling.py" "$@"
