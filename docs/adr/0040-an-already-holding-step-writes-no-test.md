# An already-holding step writes no test

A step whose criterion already holds at the start of the step no longer writes a test that drove
nothing. Its Red leaf first looks for existing tests that cover the criterion. When it finds them it
writes nothing and reports `AGAINST_UNMODIFIED: HOLDS` with `COVERING_TESTS:` naming 1 to 5 of
them; the conductor runs them with `holds-step.sh`, a blind verify-pin judges whether they cover the
criterion, and on PASS the step is ticked ` ⟂ retired already holds`. When none covers it, the leaf
writes one test, reports `PASSES`, and verify-pin judges that test on passing now, coverage and
quality, with no fail-at-base and no mutation. The unpinnable retire and `pin-reject-route.sh` are
deleted (PRD 044, 044.2). This supersedes the pin-test part of ADR-0012.

## Context

ADR-0012 made "already satisfied" a step outcome: the Red leaf wrote a test that passed against the
unmodified code, and verify-pin returned `PASS` only if the test also failed at the branch base under
a hand mutation the verifier applied. When the mutation stayed green, `pin-reject-route.sh` retired
the step as unpinnable, or, on a `missing` reroute, the run bailed as an unpinnable missing case.
ADR-0038 (044.1) already stopped recording that mutation; this ADR removes the demand itself.

In Beck's TDD a test is added while developing, or as a bug's repro. A test that passes from the
start drove nothing, and most pins covered behaviour an earlier step of the same run built and an
earlier test already pinned. Measured at `876b43e148`, with the owner's counts at `3b33e78b00`
(`specs/prd-044.md`, *Facts*):

- 2762 `test: pin` commits on `main`, against 2230 other `test: ` commits and 10815
  `feat`/`fix`/`refactor` commits.
- In a random sample of 30 `test: pin` commits, about 26 cover behaviour an earlier step of the
  same run built (12 solid by their recorded mutation, 16 weaker), 3 cover code older than the run
  (`70ff134368` #3455, `3c5de105cc` #2015, `9fbd059db1` #723), and 1 covers a bug already fixed
  (`d9c471c95f` #3565).
- Ledgers hold 133 unpinnable retires, 21 ` ⟂ retired already` lines and 4 re-pin steps.
- No pin test that caught a real regression was found.
- Issue hits, all / open / in a title: verify-pin 934 / 6 / 33, unpinnable 102 / 1 / 5.

## Decision

- **D1, an already-holding step writes no new test.** The developer names the existing tests that
  cover the criterion; a blind verifier, given the spec, the step and those tests, judges whether
  they cover it. The spec carries no developer rationale, and without it a term the issue defines
  elsewhere would be misread. On PASS the step is ticked as already holding.
- **D2, a bug criterion whose bug is already fixed** is handled as D1, falling to D3 when no
  existing test covers it.
- **D3, no existing test covers the criterion:** the developer writes one test, and the verifier
  judges it with no fail-at-base and no mutation. Tension accepted: such a test passes from the
  start, but it guards code that had no test.
- **D7, the Red leaf says it holds**, before writing a test. Found: it reports `HOLDS` with
  `COVERING_TESTS: <ids>` and writes nothing, and the conductor runs those cases, which must pass,
  before the verifier (`holds-step.sh`). Not found: it writes a test as before, and a `PASSES`
  takes D3.
- **D8, one phase:** the `pin` phase and `prompts/verify-pin.md`, rewritten, serve D1 and D3,
  taking 1 to 5 test ids, each a tracked path or `<path>::<node>`; anything else is exit 2, so the
  widened input stays an id list and carries no free text.
- **D9, blindness under D1:** the step's diff is empty (`holds-step.sh` exit 2 otherwise), so the
  named files carry none of the developer's argument, and the verifier reads the named tests at
  `HEAD`, since most pins cover behaviour an earlier step of the run built.
- **D10, the marker** is the existing ` ⟂ retired already holds`, written by
  `tick-ledger.sh --already-holds <reason-file> --case <id>` once per named test, the reason taken
  from the verifier's PASS, with the existing `🪦 Retired` comment.
- **D11, after D3:** PIN.md's PASS path stays (the `test: pin` commit, the `📌` comment, the
  criterion tick). verify-pin keeps passes-now and quality and drops fail-at-base and the mutation;
  a REJECT goes to the revise loop on `REVISE_BUDGET` alone.
- **D12, every other entry into verify-pin** (the `⟦replaces-case⟧` PASSES path, a `missing`
  reroute's added case, a revise of red that PASSES) uses the reduced verify-pin.
  `pin-reject-route.sh` is deleted with the unpinnable retire, its `--already-holds` fallback, the
  unpinnable missing-case bail cause and the unpinnable step event.
- **D13, smaller rules:** `pin` in `VERI_SKIP_VERIFY` still skips the verifier, and a `HOLDS` step
  then ticks on the named cases passing; the go-red-control exception (PN26) goes; verify-green
  states its mutation rule itself; the planner's fold rule keeps its exemption, worded "an
  already-holding step".
- **D14, a bug already fixed (D2):** the bug paragraph (`_verify-red-bug.md`) reaches the verifier,
  which judges that the named tests assert *Expected*; a D3 test still carries `#<n>` in its name.
- **Supersedes ADR-0012 in part:** a pin no longer owes a test that fails at the branch base under
  the verifier's mutation. ADR-0012's outcome stands: "already satisfied" is a step outcome with its
  own blind check, not a failure, and skips Green and Refactor.

## Considered options

- **A tick with nothing checked** (D1): rejected. The tick would rest on the developer's word alone.
- **Keep writing a test, only without fail-at-base or a mutation** (D1): rejected. It keeps adding a
  test that drove nothing where one already covers the criterion.
- **Always write the repro test for a fixed bug** (D2): rejected for the same reason; the repro is
  written only when no test asserts *Expected*.
- **A ⟦human-owed⟧ line reviewed by vmerge, or a `needs-user` bail, where no test covers it** (D3):
  rejected. Both put a human on a criterion the code already meets.
- **A new `cover` phase beside `pin`** (D8): rejected. One phase and one prompt serve both answers.
- **Reading the named tests at `--branch-base`** (D9): rejected. Most pins cover behaviour an earlier
  step of the same run built, which the branch base does not hold.
- **A new ` ⟂ already holds` mark and comment kind** (D10): rejected. The existing mark and the
  `🪦 Retired` comment already mean it.

## Consequences

- A step whose criterion already holds costs a verifier's read of the tests that cover it, instead
  of a new test, a hand mutation and a possible unpinnable retire.
- Where no test covers it, the one test written passes from the start and is not shown able to fail;
  coverage and quality, judged blind, are what stand behind it.
- A `HOLDS` step commits no test, so the suite gains nothing from it; the named tests were already
  there.
- #4739 "A verify-pin REJECT retired because the hand mutation stays green removes the step's Red
  test changes" is moot: no REJECT retires a step any more.
