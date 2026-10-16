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

name="$skill_md plans an interface change as one step listing its phases and runs them in order, each as a developer leaf then a blind verifier, ticking the phase's mark with tick-ledger.sh --phase in its commit"
problems=()

plan_text="$(section "$plan_heading")"
if ! grep -E 'interface change' <<<"$plan_text" > /dev/null; then
  problems+=("$skill_md's '$plan_heading' section never names an interface change, so one is planned as ordinary Red/Green steps")
else
  grep -F '⟦phases:' <<<"$(window "$plan_text" 'interface change' 400)" > /dev/null ||
    problems+=("$skill_md's '$plan_heading' section names an interface change without planning it as one step listing ⟦phases: …⟧")
fi

loop_heading='### 3. The cycle loop'
loop_text="$(section "$loop_heading")"
if ! grep -F 'tick-ledger.sh --phase' <<<"$loop_text" > /dev/null; then
  problems+=("$skill_md's '$loop_heading' section never ticks a phase with tick-ledger.sh --phase, so a phased step's phases are never run")
else
  near="$(window "$loop_text" 'tick-ledger\.sh --phase' 900)"
  grep -F '⟦phases' <<<"$near" > /dev/null ||
    problems+=("$skill_md ticks tick-ledger.sh --phase without naming the ⟦phases: …⟧ step it runs")
  grep -E 'in order|ledger-steps\.sh next-phase' <<<"$near" > /dev/null ||
    problems+=("$skill_md never runs a phased step's listed phases in order")
  grep -F 'build-develop-prompt.sh' <<<"$near" > /dev/null ||
    problems+=("$skill_md never runs a phase as a developer leaf built by build-develop-prompt.sh")
  grep -F 'run-verdict.sh' <<<"$near" > /dev/null ||
    problems+=("$skill_md never follows a phase's developer leaf with a blind verifier through run-verdict.sh")
  grep -E 'commit' <<<"$near" > /dev/null ||
    problems+=("$skill_md never ties a phase's tick to that phase's commit")
fi

grep -F 'the run loop calls neither yet' <<<"$skill_text" > /dev/null &&
  problems+=("$skill_md still says the run loop calls neither tick-ledger.sh --phase nor ledger-steps.sh next-phase")
report "$name"

name="$skill_md rejects an expand, migrate or contract-b phase's commit that transform-touches-tests.sh exits 1 on, and a contract-a phase's commit that production-frozen.sh exits 1 on"
problems=()

phased_text="$(section '#### A `⟦phases')"
if [[ -z "${phased_text// /}" ]]; then
  problems+=("$skill_md has no '#### A \`⟦phases: …⟧\` step' subsection to read")
else
  if ! grep -F 'transform-touches-tests.sh' <<<"$phased_text" > /dev/null; then
    problems+=("$skill_md's phased step never runs transform-touches-tests.sh, so an expand, migrate or contract-b commit that edits a test file is accepted")
  else
    near="$(window "$phased_text" 'transform-touches-tests\.sh')"
    for phase in expand migrate contract-b; do
      grep -F "$phase" <<<"$near" > /dev/null ||
        problems+=("$skill_md runs transform-touches-tests.sh in the phased step without naming the $phase phase")
    done
    grep -E 'exit 1' <<<"$near" > /dev/null && grep -E 'reject' <<<"$near" > /dev/null ||
      problems+=("$skill_md never says transform-touches-tests.sh exit 1 rejects the phase's commit")
  fi
  if ! grep -F 'production-frozen.sh' <<<"$phased_text" > /dev/null; then
    problems+=("$skill_md's phased step never runs production-frozen.sh, so a contract-a commit that edits production code is accepted")
  else
    near="$(window "$phased_text" 'production-frozen\.sh')"
    grep -F 'contract-a' <<<"$near" > /dev/null ||
      problems+=("$skill_md runs production-frozen.sh in the phased step without naming the contract-a phase")
    grep -E 'exit 1' <<<"$near" > /dev/null && grep -E 'reject' <<<"$near" > /dev/null ||
      problems+=("$skill_md never says production-frozen.sh exit 1 rejects the contract-a commit")
  fi
fi
report "$name"

name="$skill_md starts a phased step's contract only once no-product-caller.sh on the old interface exits 0"
problems=()

phased_text="$(section '#### A `⟦phases')"
if [[ -z "${phased_text// /}" ]]; then
  problems+=("$skill_md has no '#### A \`⟦phases: …⟧\` step' subsection to read")
elif ! grep -F 'no-product-caller.sh' <<<"$phased_text" > /dev/null; then
  problems+=("$skill_md's phased step never runs no-product-caller.sh, so a contract phase starts while a product caller of the old interface remains")
else
  near="$(window "$phased_text" 'no-product-caller\.sh')"
  grep -F 'contract' <<<"$near" > /dev/null ||
    problems+=("$skill_md runs no-product-caller.sh in the phased step without tying it to the contract phase")
  grep -E 'old interface' <<<"$near" > /dev/null ||
    problems+=("$skill_md runs no-product-caller.sh in the phased step without saying it is run on the old interface")
  grep -E 'exit(s)? 0' <<<"$near" > /dev/null && grep -E 'only once|until|before' <<<"$near" > /dev/null ||
    problems+=("$skill_md never says the contract starts only once no-product-caller.sh exits 0")
  flat_text="$(tr '\n' ' ' <<<"$phased_text")"
  flat_near="$(window "$flat_text" 'no-product-caller\.sh' 600)"
  grep -F 'contract-b' <<<"$flat_near" > /dev/null ||
    problems+=("$skill_md does not name contract-b as the phase no-product-caller.sh gates (#1475)")
  ! grep -F 'before it launches contract-a or contract-b' <<<"$flat_near" > /dev/null ||
    problems+=("$skill_md still runs no-product-caller.sh before contract-a, which a kept shim can never pass (#1475)")
  grep -E "contract-a starts on the migrate phase's pass without the scan" <<<"$flat_near" > /dev/null ||
    problems+=("$skill_md never says contract-a starts on the migrate phase's PASS without the scan (#1475)")
fi
report "$name"

name="$skill_md spends one refactor of the budget for a whole phased step, not one per phase"
problems=()

phased_text="$(section '#### A `⟦phases')"
if [[ -z "${phased_text// /}" ]]; then
  problems+=("$skill_md has no '#### A \`⟦phases: …⟧\` step' subsection to read")
elif ! grep -E 'refactor-budget\.sh|VERI_(ISSUE_)?REFACTOR_BUDGET|refactor budget' <<<"$phased_text" > /dev/null; then
  problems+=("$skill_md's phased step never says what it spends of the refactor budget, so each phase may be counted as a refactor of its own")
else
  near="$(window "$phased_text" 'refactor-budget\.sh|VERI_(ISSUE_)?REFACTOR_BUDGET|refactor budget')"
  grep -E 'one refactor' <<<"$near" > /dev/null ||
    problems+=("$skill_md names the refactor budget in the phased step without saying the step spends one refactor of it")
  grep -E 'whole step|not one per phase' <<<"$near" > /dev/null ||
    problems+=("$skill_md never says the one refactor is for the whole phased step rather than one per phase")
fi
report "$name"

name="$skill_md resets a phased step's contract phase that exhausts REVISE_BUDGET to its own base sha, keeps the expand and migrate commits, and files the contract under ## Owed steps"
problems=()

phased_text="$(section '#### A `⟦phases')"
if [[ -z "${phased_text// /}" ]]; then
  problems+=("$skill_md has no '#### A \`⟦phases: …⟧\` step' subsection to read")
elif ! grep -F 'revise_budget' <<<"$phased_text" > /dev/null || ! grep -E 'exhaust' <<<"$phased_text" > /dev/null; then
  problems+=("$skill_md's phased step never says what happens when a contract phase exhausts REVISE_BUDGET, so the whole step is abandoned with it")
else
  near="$(window "$phased_text" 'exhaust')"
  grep -F 'contract' <<<"$near" > /dev/null ||
    problems+=("$skill_md says what an exhausted REVISE_BUDGET does in the phased step without tying it to the contract phase")
  grep -E 'reset' <<<"$near" > /dev/null && grep -E '(its own|that phase.s|the contract.s) base' <<<"$near" > /dev/null ||
    problems+=("$skill_md never says the exhausted contract phase is reset to its own base sha")
  grep -F 'expand' <<<"$near" > /dev/null && grep -F 'migrate' <<<"$near" > /dev/null && grep -E 'kept|keep' <<<"$near" > /dev/null ||
    problems+=("$skill_md never says the expand and migrate commits are kept when the contract is reset")
  grep -F '## owed steps' <<<"$near" > /dev/null ||
    problems+=("$skill_md never says the exhausted contract is filed under the ledger's ## Owed steps")
fi
report "$name"

name="$skill_md accepts a ⟦replaces-case⟧ group step's Green only once the conductor's own run of mutation-parity.sh on that step's pairs table exits 0"
problems=()

green_text="$(section '#### Green')"
if [[ -z "${green_text// /}" ]]; then
  problems+=("$skill_md has no '#### Green' subsection to read")
elif ! grep -F 'mutation-parity.sh' <<<"$green_text" > /dev/null; then
  problems+=("$skill_md's Green step never runs mutation-parity.sh, so a ⟦replaces-case⟧ step's Green is accepted on the developer leaf's own pairs table")
else
  near="$(window "$green_text" 'mutation-parity\.sh')"
  grep -F 'replaces-case' <<<"$near" > /dev/null ||
    problems+=("$skill_md runs mutation-parity.sh in the Green step without tying it to a ⟦replaces-case⟧ step")
  grep -F 'pairs table' <<<"$near" > /dev/null ||
    problems+=("$skill_md runs mutation-parity.sh in the Green step without saying it is run on the step's pairs table")
  grep -E 'exit(s)? 0' <<<"$near" > /dev/null && grep -E 'only once|until|before' <<<"$near" > /dev/null ||
    problems+=("$skill_md never says the Green is accepted only once mutation-parity.sh exits 0")
fi
report "$name"

name="$skill_md accepts a phased step's contract-a phase only once the conductor's own run of mutation-parity.sh on that phase's pairs table exits 0"
problems=()

phased_text="$(section '#### A `⟦phases')"
if [[ -z "${phased_text// /}" ]]; then
  problems+=("$skill_md has no '#### A \`⟦phases: …⟧\` step' subsection to read")
elif ! grep -F 'mutation-parity.sh' <<<"$phased_text" > /dev/null; then
  problems+=("$skill_md's phased step never runs mutation-parity.sh, so a contract-a phase is accepted on the developer leaf's own pairs table")
else
  near="$(window "$phased_text" 'mutation-parity\.sh')"
  grep -F 'contract-a' <<<"$near" > /dev/null ||
    problems+=("$skill_md runs mutation-parity.sh in the phased step without tying it to the contract-a phase")
  grep -F 'pairs table' <<<"$near" > /dev/null ||
    problems+=("$skill_md runs mutation-parity.sh in the phased step without saying it is run on the phase's pairs table")
  grep -E 'exit(s)? 0' <<<"$near" > /dev/null && grep -E 'only once|until|before' <<<"$near" > /dev/null ||
    problems+=("$skill_md never says the contract-a phase is accepted only once mutation-parity.sh exits 0")
fi
report "$name"

name="$skill_md puts mutation-parity.sh's report into the PR body as the pairs table, and each row it reports owed under ## Owed by a human"
problems=()

parity_near="$(windows "$skill_text" 'mutation-parity\.sh' 400 | grep -F 'pr body')"
if [[ -z "$parity_near" ]]; then
  problems+=("$skill_md never puts mutation-parity.sh's report into the PR body, so the pairs table a reviewer reads is the developer leaf's own")
else
  grep -F 'pairs table' <<<"$parity_near" > /dev/null ||
    problems+=("$skill_md puts mutation-parity.sh's report into the PR body without saying it is the pairs table")
  grep -E 'rows? (it|mutation-parity\.sh) reports? owed' <<<"$parity_near" > /dev/null &&
    grep -F '## owed by a human' <<<"$parity_near" > /dev/null ||
    problems+=("$skill_md never puts a row mutation-parity.sh reports owed into the PR body under ## Owed by a human")
fi
report "$name"

name="$skill_md's Draft PR step puts the conductor's mutation-parity.sh report into the PR body template as the pairs table and its owed rows under ## Owed by a human, and the ⟦replaces-case⟧ Green gate says the same of its run's report"
problems=()

pr_text="$(section '### 4. Draft PR')"
body_template="$(grep -oE 'gh api -x patch [^"]*-f title="[^"]*" -f body="[^"]*"' <<<"$pr_text")"
if [[ -z "$body_template" ]]; then
  problems+=("$skill_md's Draft PR step has no gh api -X PATCH … -f body= template to read")
elif ! grep -F 'mutation-parity.sh' <<<"$body_template" > /dev/null; then
  problems+=("$skill_md's Draft PR body template never includes mutation-parity.sh's report, so the PR body a reviewer reads carries no pairs table the conductor checked")
else
  near="$(window "$body_template" 'mutation-parity\.sh')"
  grep -F 'pairs table' <<<"$near" > /dev/null ||
    problems+=("$skill_md's Draft PR body template includes mutation-parity.sh's report without saying it is the pairs table")
  grep -E 'owed' <<<"$near" > /dev/null && grep -F '## owed by a human' <<<"$near" > /dev/null ||
    problems+=("$skill_md's Draft PR body template never puts mutation-parity.sh's owed rows under ## Owed by a human")
fi

green_text="$(section '#### Green')"
green_near="$(windows "$green_text" 'mutation-parity\.sh' 400 | grep -F 'pr body')"
if [[ -z "$green_near" ]]; then
  problems+=("$skill_md's ⟦replaces-case⟧ Green gate never says its mutation-parity.sh report goes into the PR body")
else
  grep -F 'pairs table' <<<"$green_near" > /dev/null ||
    problems+=("$skill_md's ⟦replaces-case⟧ Green gate puts mutation-parity.sh's report into the PR body without saying it is the pairs table")
  grep -E 'owed' <<<"$green_near" > /dev/null && grep -F '## owed by a human' <<<"$green_near" > /dev/null ||
    problems+=("$skill_md's ⟦replaces-case⟧ Green gate never puts a row its report owes under ## Owed by a human")
fi
report "$name"

name="$skill_md marks an exhausted contract phase owed with tick-ledger.sh --phase-owed <phase> before committing the ledger, so next-phase never hands the owed contract back (#1410)"
problems=()

phased_text="$(section '#### A `⟦phases')"
near="$(window "$phased_text" 'exhaust' 700)"
if [[ -z "${near// /}" ]]; then
  problems+=("$skill_md's phased step has no exhausted-contract paragraph to read")
elif ! grep -F 'tick-ledger.sh --phase-owed <phase>' <<<"$near" > /dev/null; then
  problems+=("$skill_md's exhausted-contract paragraph never marks the contract phase owed with tick-ledger.sh --phase-owed <phase>, so next-phase hands the owed contract back")
else
  before_commit="${near%%commit the ledger*}"
  [[ "$before_commit" != "$near" ]] && grep -F 'tick-ledger.sh --phase-owed' <<<"$before_commit" > /dev/null ||
    problems+=("$skill_md's exhausted-contract paragraph marks the contract phase owed only after committing the ledger, so the commit carries no mark")
fi
report "$name"

finish
