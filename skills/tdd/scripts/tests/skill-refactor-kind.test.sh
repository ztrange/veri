#!/usr/bin/env bash
# Unit tests for what skills/tdd/SKILL.md tells a refactor-kind run — an issue whose spec
# carries the `## Refactor` section capture-spec.sh writes for the `refactor` label — read
# as text.
#
# Contract under test:
#   1. SKILL.md's Scope & plan section tells a refactor-kind run to plan each step as one named
#      refactoring whose criterion is a shell predicate false before the step and true after it.
#   2. The develop-cover prompt and SKILL.md's Cover step — see case 2's comment.
#   3. SKILL.md's Cover step on `COVERED: no` — see case 3's comment.
#   4. SKILL.md's refactor-kind cycle, transform rejection and abandonment — see case 4's comment.
#   5. SKILL.md's Draft PR step titles a refactor-labelled run's PR refactor: — see case 5's comment.
#   6. SKILL.md's Cover step reads the report through cover-outcome.sh — see case 6's name.
#   7. SKILL.md reruns a type-only step's proof command after its transform — see case 7's name.
#   8. SKILL.md keeps a type-only step's proof command in a run file the conductor reruns — see
#      case 8's name.
#   9. SKILL.md's Scope & plan folds a deletion into the step that makes the code dead — see
#      case 9's name.
#  10. SKILL.md plans an interface change as one phased step and runs its phases — see case 10's
#      name.
#  11. SKILL.md rejects a phase's commit that breaks that phase's freeze — see case 11's name.
#  12. SKILL.md holds a phased step's contract back until no product caller remains — see case
#      12's name.
#  13. SKILL.md spends one refactor of the budget for a whole phased step — see case 13's name.
#  14. SKILL.md resets a contract phase that exhausts REVISE_BUDGET and files it as owed — see
#      case 14's name.
#  15. SKILL.md accepts a ⟦replaces-case⟧ step's Green only once mutation-parity.sh exits 0 — see
#      case 15's name.
#  16. SKILL.md accepts a contract-a phase only once mutation-parity.sh exits 0 — see case 16's
#      name.
#  17. SKILL.md puts mutation-parity.sh's report into the PR body, its owed rows under
#      ## Owed by a human — see case 17's name.
#  18. SKILL.md's Draft PR body template and its Green gate both carry mutation-parity.sh's
#      report — see case 18's name.
#  19. SKILL.md marks an exhausted contract phase owed with tick-ledger.sh --phase-owed before
#      committing the ledger — see case 19's name.
#
# Run: skills/tdd/scripts/tests/skill-refactor-kind.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"

skill_md="skills/tdd/SKILL.md"
skill_path="$ROOT/$skill_md"


source "$HERE/lib/harness.sh"
source "$HERE/lib/plain.sh"
source "$HERE/lib/window.sh"


section() {
  awk -v h="$1" \
    'index($0, h) == 1 { level = index(h, " ") - 1; inside = 1; next }
     inside && match($0, /^##+ /) && RLENGTH - 1 <= level { exit }
     inside' "$skill_path" |
    plain --join
}

plan_heading='### 2. Scope & plan'

skill_text="$(plain --join < "$skill_path")"

finish
