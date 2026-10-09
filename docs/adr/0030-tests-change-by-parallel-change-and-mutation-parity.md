# Tests change by Parallel Change, and redundancy is measured by mutation parity

PRD 009 (#1229) moves veri's tests from bash suites to in-process pytest. Its decision 4 fixes
how an interface and its tests change together without code and tests changing in one commit,
and when a test may be deleted because it is redundant. Its decision 2 changes ADR 0027's
per-script floor. This record carries those two decisions and the operator's 2026-10-09
amendment: one `⟦replaces-case⟧` step may replace a group of related cases. Decisions 1, 3,
5 and 6 stay in the PRD.

## Context

- **Beck, *Test-Driven Development: By Example* (2002).** A test is deleted when it adds
  neither **confidence** nor **communication**; a redundant test is a candidate. The refactor
  step keeps the bar green throughout.
- **Beck, *Test Desiderata* (2019).** Twelve properties traded against one another. Those in
  play here are **fast**, **isolated**, **deterministic**, **behavioural** (a test fails when
  behaviour changes) and **structure-insensitive** (a test does not fail when only structure
  changes).
- **Beck, *Tidy First?* (2023).** Structure changes and behaviour changes go in separate
  commits, and preferably separate PRs.
- **Fowler / Sato, *Parallel Change*.** To change an interface: **expand** (add the new one
  beside the old, and proxy the old onto it), **migrate** (move callers one at a time), then
  **contract** (delete the old). The build stays green at every step.
- **Meszaros, *xUnit Test Patterns*, and the common practice of refactoring tests.** When a
  test changes, the production code is frozen and acts as the test's safety net, the mirror of
  a code refactor. A rewritten test is trusted only after it has been seen to fail against
  broken code.

Read against these, veri was right in two places and stricter than Beck in one:

- **Right:** a refactor transform may not touch a test file (`transform-touches-tests.sh`,
  `SKILL.md:795`): code and its tests never change in the same step.
- **Right:** ADR 0026 lets a test die with its subject.
- **Stricter:** ADR 0026's *When a refactor may delete a test* (`:184-191`) forbids deleting
  a test "that looks redundant", or one "a module's own suite now duplicates". The rule exists
  because a model's judgement that a case is redundant cannot be trusted. It has cost bails.

Two further rules would block PRD 009's ports:

- **ADR 0027's floor** keeps three bash cases per ported script — the shim resolves from the
  symlinked skills directory, one case per exit code, the bad-argument stderr text — on the
  ground that a pytest case importing the module cannot observe them. Since PRD 008 every one
  of the 72 scripts is a shim over a module with `main(argv)`, so one test covers every shim,
  and `run_cli` drives exit codes and stderr in-process.
- **One `⟦replaces-case⟧` step replaced one case** (ADR 0027 `:104-108`). C4a–d would have
  been about 38, 59, 46 and 65 steps, ~$700 at ~$3.50 a step.

## Decision

### One step per interface, in three phases

Changing an interface and its tests is **one ledger step per interface**, run as up to three
phases: **expand**, **migrate** and **contract**. Contract is split in two: **(a) migrate the
tests**, then **(b) remove the proxy**, because the proxy is production code and the tests are
not.

| phase | changes | frozen | proof |
|---|---|---|---|
| **expand** | production: the new interface is added and the old one becomes a **proxy** onto it | tests (`transform-touches-tests.sh`, as today) | the old tests green, unmodified |
| **migrate** | production: product callers move to the new interface, one per commit | tests | the old tests still green, through the proxy |
| **contract (a): migrate tests** | tests: each test of the old interface is rewritten against the new one, or deleted | production (the mirror of `transform-touches-tests.sh`) | mutation parity, below |
| **contract (b): remove the proxy** | production: the proxy is deleted | tests | the suite green, so no test depended on the proxy |

- **Each phase is green, verified, and carries its own ledger mark**, the way `⟂ refactor
  pending` marks a ticked step today. A resumed run starts at the next unmarked phase. The
  whole step counts as **one** refactor against the budgets.
- **Contract starts only when no product caller of the old interface remains**, shown by a
  static check. Product callers are `SKILL.md`, the Makefile, the hooks and `veri/`; tests do
  not count.
- **A contract phase that exhausts `REVISE_BUDGET` resets only itself.** Expand and migrate
  stay, since they landed green on their own and a proxy left in place is harmless, and the
  contract is filed as owed.
- **Empty phases are skipped.** Moving a CLI suite from a process to `main(argv)` changes no
  interface, so it is contract (a) alone, with no proxy to remove.

### Mutation parity proves contract (a)

1. The developer leaf proposes **one mutation per row of the pairs table**: the behaviour the
   old case pins, broken one way.
2. Each mutation is applied and the old and new cases run. A mutation is **valid** only when
   both hold:
   - the old case goes red;
   - at least one other case in that suite stays green, so a syntax error or an import crash
     does not count.
3. A valid mutation must turn the **new** case red too.
4. **A deleted case is either dead or redundant.**
   - *Dead:* its only subject was the proxy. This is ADR 0026's rule, kept.
   - *Redundant:* its valid mutation is caught by a named kept case. This is Beck's "adds no
     confidence", made checkable, and it replaces ADR 0026's "never one that looks redundant".
5. **No valid mutation within the revise budget** means the old case pins nothing breakable.
   It goes to the human as an owed decision, never an automatic deletion.
6. **The PR body carries the pairs table:** each old case, its replacement or the reason it
   died, and the mutation that proved it.

### A `⟦replaces-case⟧` step replaces a group

One `⟦replaces-case⟧` step may replace a **group** of related cases of one suite, about a
dozen at most. It names one suite path and each case by its exact name. Its Red is the
replacing pytest cases failing; its Green deletes exactly the named cases and no other. One
case is a group of one, so the single-case form stays valid.

Mutation parity proves every case in the group. Until C3 makes the conductor run the probe,
that proof is carried by the PR body's pairs table: per named case, the mutation that turned
the old case red and the replacing case red. C3 replaces the table's proof with the
conductor's own run.

### The shim floor is one test for all 72

ADR 0027's per-script floor case "the shim resolves from the symlinked skills directory" is
replaced by one test over every shim: a small test reads every `.sh` under `scripts/` and
checks it is the canonical shim naming an existing module, and a medium test executes one shim
through the symlinked skills directory. The floor's other two items, one case per exit code and
the bad-argument stderr text, stay per script, as small in-process cases through `run_cli`,
and are no longer bash cases.

## Rejected

- **Keep ADR 0026's rule.** Every redundant case would survive its port, and the distrust it
  encodes is answered better by measuring than by forbidding.
- **Let the model judge redundancy.** The reason ADR 0026's rule exists.
- **Change code and its tests in one step.** Neither side would be frozen to act as the
  other's safety net.
- **One step per phase.** Each phase is not a refactor on its own; counted separately they
  would spend three refactors' budget on one interface's change.
- **Delete a case with no valid mutation automatically.** A case that pins nothing breakable
  may still communicate; that is a human's call.
- **Keep one case per `⟦replaces-case⟧` step.** ~$700 for C4a–d with no gain in proof, since
  mutation parity still covers every case.

## Consequences

- ADR 0026's deletion rule and ADR 0027's shim floor and one-case-per-step wording are
  superseded in part by this record.
- Until C3 lands, the phased step, its marks, the "no product caller" check, the
  production-frozen check and the conductor-run mutation probe exist only here; a
  `⟦replaces-case⟧` group step's parity is the pairs table's.
- C4's ports are planned as group steps of about a dozen cases each.
