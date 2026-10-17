#!/usr/bin/env bash
# Unit tests for the workflow files under .github/workflows/, read as text the way GitHub
# Actions reads them.
#
# Contract under test:
#   .github/workflows/ci.yml, the `gates` job: `timeout-minutes: 8` at job level, and the
#   comment beside it names the 6-hour ceiling it protects against, cites the ~160-175 s the
#   job observably takes and the ~230 s it took while the docs gates ran in CI, says the 8 is
#   temporary, naming two issues whose landing did not bring the job back under it, and says
#   the budget assumes those gates stay out of CI.
#   .github/workflows/pages.yml, the `deploy` job: `timeout-minutes: 10` at job level, and
#   the comment beside it names the same 6-hour ceiling, cites the 11–23 s the job
#   observably takes, and says why its number is larger than the gates job's.
#   Every job in every workflow file declares a job-level `timeout-minutes`.
#   ci.yml's workflow-level `concurrency` cancels a PR's in-progress run on a newer push to
#   it, and never a push to main.
#
# Run: scripts/tests/workflow-timeouts.test.sh
set -uo pipefail

source "$(cd "$(dirname "$0")" && pwd)/lib/harness.sh"

finish
