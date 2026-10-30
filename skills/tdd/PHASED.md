A step listing `⟦phases: …⟧` runs no Red, Green or Refactor phase: it runs the phases it
lists, in order, one at a time. `$S/ledger-steps.sh next-phase < .tdd/issue-<n>.md` names the
next one, <phase>; record `git rev-parse HEAD` as that phase's base sha. Its developer leaf,
built by `build-develop-prompt.sh <phase> <spec-file> "<STEP>" '<test-cmd>'`, makes that
phase's change and commits it, which the phase's freeze check below must accept; then the blind verifier, `run-verdict.sh --step "<STEP>"
--fast-cmd '<fast-cmd>' <phase> <spec-file> <test-path> <base-sha>`, judges the diff from
that base sha. Both are launched through the supervisor and waited on as *Launching a leaf*
sets out, the leaf as `develop-<phase>` and the verifier as `verdict-<phase>`. On PASS, mark
the phase with `tick-ledger.sh --phase <phase> .tdd/issue-<n>.md "<STEP>"` and commit the
ledger with that phase's commit, then push, and go back to `next-phase` for the step's next
phase. On REJECT, revise under `REVISE_BUDGET` as `REVISE.md` sets out (when a verifier answers `REJECT`, `Read` `<base directory>/REVISE.md`). On exit 2,
**bail** as a system failure (`no-verdict`, see `<base directory>/BAIL.md`). Once `next-phase` exits 3 every listed phase is
marked, the step reads as done, and the loop goes back to `next-unchecked.sh`.

After a phase leaf's wait exits 0, `$S/suite-reported.sh develop-<phase>` runs before its verifier is
launched: exit 2 means no `SUITE:` line, so launch no verifier and **bail** as a system failure
with cause `report-missing` (`Read` `<base directory>/BAIL.md`).

The whole step spends one refactor of the budget, not one per phase: wherever
`refactor-budget.sh <count>` counts the transforms already landed, a phased step adds one to
`<count>` once its last phase is marked, however many phases it listed.

The freeze check runs on the developer leaf's commit, before the verifier. An expand, migrate
or contract-b commit runs `$S/transform-touches-tests.sh <base-sha>`: exit 1 rejects it, tests
being frozen there. A cover-new or contract-a commit runs `$S/production-frozen.sh <base-sha>`:
exit 1 rejects it, production being frozen there. Either rejection is revised as a REJECT is;
exit 2 **bails** as a system failure (see `<base directory>/BAIL.md`).

A cover-new phase adds cases that call the new interface directly, and its PASS is accepted
only once those cases pass against the expand commit and go red under a mutation of the new
interface's behaviour. A migrate phase does not start until the step's cover-new phase has
passed: `next-phase` never hands over migrate while a listed cover-new is unmarked.

A contract-a phase deletes the old interface's cases, each deletion proved by mutation parity
against a kept case; its PASS is accepted only by the mutation-parity gate `SKILL.md`'s
*Green* states for a `⟦replaces-case⟧` verify, run on that phase's pairs table.

Contract-b starts only once `$S/no-product-caller.sh <old-interface>` on the old
interface exits 0. Before it launches contract-b, the phase that deletes the interface, run it:
exit 1 names each product file still calling the old interface, so contract-b does not start and
the step **bails** as a process failure, the migrate phase having left a caller behind; exit 2
**bails** as a system failure (see `<base directory>/BAIL.md`). Contract-a starts on the migrate phase's PASS without the scan:
it removes the tests' routing to the old interface, not the interface, and a shim kept on
purpose is never scanned.

A contract phase that exhausts `REVISE_BUDGET` does not abandon the step: reset the contract
to its own base sha with `git reset --hard <base-sha>`, so the expand and migrate commits are
kept, and file the contract under the ledger's `## Owed steps`: append it as a plain bullet
under that trailing heading, adding the heading when the ledger has none, and mark the
contract phase owed with `tick-ledger.sh --phase-owed <phase> .tdd/issue-<n>.md "<STEP>"`, so
`next-phase` never hands it back; then commit the ledger and go back to `next-unchecked.sh`.
