#!/usr/bin/env bash
# Unit tests for where skills/tdd/SKILL.md asks whether a run can still afford to finish,
# read as text.
#
# Contract under test:
#   1. The cycle loop (`### 3. The cycle loop`, up to `### 4.`) calls `$S/run-affordable.sh`
#      after the step's ledger commit (`chore: refactor verified …`), with the count
#      `next-unchecked.sh` implies — which leaves out the `⟦full-suite⟧` and `⟦human-owed⟧`
#      lines that script skips; on exit 1 the run parks, and the park's comment carries
#      spent, steps remaining, the median, the projection, the ceiling, and the two answers —
#      raise `VERI_RUN_BUDGET` and resume, or split the issue.
#   2. The same step boundary — from the call to the next verdict bullet (`- **REJECT`) — also
#      says what its exit 3 does (no full step done yet, so no median: carry on) and what its
#      exit 2 does (no answer could be obtained).
#   3. The park on exit 1 — up to the exit 2 answer — says it is not a bail and that
#      `classify-bail.sh` is not called on it.
#
# Run: scripts/tests/skill-run-affordable.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"
skill_md="skills/tdd/SKILL.md"
skill_path="$ROOT/$skill_md"


source "$HERE/lib/harness.sh"
source "$HERE/lib/plain.sh"


cycle_loop() {
  awk '/^### 3\. The cycle loop/ { inside = 1; next } /^### 4\./ { inside = 0 } inside' "$skill_path"
}

loop="$(cycle_loop)"
call_at="$(grep -n -m1 '\$S/run-affordable\.sh' <<<"$loop" | cut -d: -f1)"
after_call=""
[[ -n "$call_at" ]] && after_call="$(sed -n "${call_at},\$p" <<<"$loop")"

finish
