# A port moves coverage, and the old suite is the proof it moved

**Superseded in part by [ADR-0030](0030-tests-change-by-parallel-change-and-mutation-parity.md)**: the floor's "the `.sh` shim resolves" item is
replaced by one test over every shim. Its exit-code and bad-argument-stderr items stay per
script, as small in-process cases through `run_cli`, and are no longer bash cases. The
one-case-per-step `⟦replaces-case⟧` wording is replaced by the group step: one step may
replace a group of related cases of one suite.

PRD 008 (#537) ports every veri script from bash to Python 3 behind its `.sh` entry point.
A ported script's cases move from its bash suite into `tests/py/test_<script>.py`, where they
run in-process. This record fixes which bash cases survive a port, the floor every ported
script keeps whatever the rule says, and what proves a port held the script's contract. It is
a **port's** rule. ADR 0026's rule for a **refactor** is unchanged.

**Amended 2026-10-02**, before any port landed under it: the proof runs over **contract
cases** only, and **implementation cases** are replaced by pytest cases first (#634). Later
the same day, after #634 bailed again: an implementation case is one **about the ported
script, in any suite**, and the port issue lists them all as `⟦replaces-case⟧` criteria
before the port starts (#634, #671).

## Context

ADR 0026 lets a refactor delete a test only with its subject: never a case "that looks
redundant", never one a module's own suite now duplicates. A port is the opposite situation.
The subject stays — same name, same arguments, same stdout, stderr and exit codes — and the
coverage moves to a faster harness. Kept whole, every bash suite would still pay one process
per case after its script ported, and the port would buy nothing. Applied to a port, ADR 0026
would forbid exactly the deletion the port is for.

The two spikes that priced the move (#473 Python, #474 Go) each ported `parse-verdict.sh` and
`push-branch.sh`. Both held the CLI contract on 23 of 23 integration cases, unmodified, on the
first run, and both ran ~30 unit cases in-process at 0.18–0.19 s wall. The old suite run
unmodified against the new code was what showed the contract held.

The first port to try it hit a case no port can pass. #634 (PRD 008 R0b, porting `status.sh`)
parked on `tests/status.test.sh:452-470`, "finds the step through lib/ledger.sh's
ledger_steps, counting no checkbox of its own". It copies only `status.sh` and `lib/` into a
scratch directory and replaces the bash function `ledger_steps`. Once `status.sh` is a shim
over `veri/status.py`, nothing calls that function, so "the old suite, green and unmodified"
could not be met. The same wall stands across waves 2–3: the fast tier's documented pattern
sources a script or a `lib/` file and mocks its functions (`push-branch.test.sh` is the worked
example; `ledger`, `github` and `exit-contract` follow it), and six integration suites —
among them `metrics`, `orchestrate` and `status` — copy `lib/` into a scratch tree by hand.

The amended rule then met the same wall one suite over. #634 bailed on 2026-10-02 at its
final full `make test`: besides the port's own code fallout, failing cases in **other
scripts' suites** pinned `status.sh`'s bash internals. `tests/event-log.test.sh:97`, "run_activity
and scope_totals read the event log through lib/event_log.py's one parse and one
dollar/token sum, with status.sh's text and --json figures unchanged …", and
`tests/main-working-tree.test.sh:67`, "a shared lib/main-working-tree.sh defines
main_working_tree, and status.sh and solvable-issues.sh both resolve the main working tree
through it", assert which bash library `status.sh` sources. No correct port can pass them,
and a repair leaf may not change them. The rule had defined an implementation case by the
suite it sat in, so the port's plan never listed them.

The shim is the proxy of a refactoring by example. **Contract tests** pass through the proxy
unchanged; tests coupled to the implementation are the ones rewritten; new tests are written
against the ideal interface.

## Decision

### The survival rule

A bash case **survives** a port when its assertion reads something only a real process
boundary produces:

- git's or gh's own output text;
- a PATH stub observing a call;
- a signal or a kill;
- a detached process.

**Every other case is replaced** by the pytest case that asserts the same thing. The port's PR
body lists the pairs: each removed bash case beside the pytest case that replaces it.

### The floor

Whatever the survival rule says, every ported script keeps these bash cases:

- the `.sh` shim resolves when called from the symlinked skills directory;
- one case per exit code the script uses;
- its bad-argument stderr text.

These are the script's command-line contract, which SKILL.md, the Makefile and the hooks call.
A pytest case importing the module cannot observe any of them.

### Two kinds of case

A **contract case** runs the script through its `.sh` entry point and observes only its
arguments, stdin, environment, files, stdout, stderr, exit code and PATH stubs.

An **implementation case** of a script is defined by what it asserts about, not by where it
lives. A case in **any** suite is one when it sources the script or a `lib/` file it uses,
stubs or overrides a function inside either, or asserts on the script's source text or on
which bash library it sources. A case in `event-log.test.sh` that checks `status.sh` reads
the log through `lib/event_log.py` is an implementation case of `status.sh`.

### The proof

The proof that a port held the contract is **the old bash suite's contract cases, green with
their assertions unmodified, against the new code, before any case is cut.** The cut is a
later commit than that green run, so the history shows the contract cases passing against the
ported script. A port whose contract cases needed their assertions edited to go green changed
the contract, and is not a port.

**Implementation cases are replaced first.** Each is replaced by a pytest case asserting the
same behaviour, in its own commit before the port, and listed in the PR's pairs table. They
cannot be part of the proof: a function the shim no longer calls cannot be stubbed.

**A port finds them before it starts.** The port issue lists every implementation case of
the script across all suites, found by grepping the suites for the script's name, each as a
`⟦replaces-case⟧` criterion (#671): the ledger step that names one suite path and one case
by its exact name, whose Red is the replacing pytest case failing and whose Green deletes
that case and nothing else. Each replacing case asserts the same behaviour through the
module's entry point, in its own commit before the port.

**A miss is a planning miss.** A full-suite failure after a port, on a case that is an
implementation case of the ported script, means the issue's list was incomplete. It is
repaired with a `⟦replaces-case⟧` step, never by editing the case under a repair step: a
repair leaf that rewrote it would be cutting a case without a replacement on record.

**The setup allowance.** A contract case that copies a hand-picked set of scripts into a
scratch directory may add the `veri/` package to what it copies. Its assertions stay
byte-identical, so that commit's diff touches only copy lines.

### What a replacing pytest case may fake

A replacing pytest case calls the module's **entry point** — `main(argv)`, or the function the
shim calls — and fakes only **process boundaries**: subprocess, the clock, the environment,
files under `tmp_path`. It never patches a function of the module under test. That would
rebuild the coupling the implementation case had, one language over.

No guard suite enforces this yet. One is written when a port first breaks it, not before.

### ADR 0026 stands

ADR 0026's *When a refactor may delete a test* is unchanged. A refactor still deletes a test
only with its subject. The survival rule applies only to a change that ports a script from
bash to Python. It never lets a refactor drop a case because another suite duplicates it.

## Rejected

- **Keep every bash case.** The contract stays maximally covered, but every ported script
  keeps paying one process per case, and the port's speed gain never arrives.
- **Keep only the floor.** Drops the cases where only a real process can see the behaviour
  (git's text, a kill, a detached child). A mock in-process would assert what the mock says,
  not what the tool does.
- **Extend ADR 0026's rule to ports.** It would forbid the deletion a port exists for, and
  mixing the two would let a refactor claim a port's licence.
- **Keep bash-internal cases by keeping the stubbed function in bash.** The implementation
  case would pass unmodified, but the shim would call back into bash for it. That breaks bash
  calling Python once per invocation, and the convention that a shim holds no logic.
- **Patch the module's own functions in pytest.** The replacing case would mirror the old one
  line for line, and recreate the coupling to the implementation the port is removing.

## Consequences

- Each port issue under PRD 008 lists its implementation cases across all suites, as
  `⟦replaces-case⟧` criteria, before its run starts.
- Each port issue under PRD 008 cites this record. Its PR body carries the pairs table, and
  its history carries the implementation cases replaced, then the contract cases green before
  the cut.
- Before #633 there was no `tests/py/`. Its pytest leg in `make unit` and `make test` is what
  the replacing cases run under, and its admission rule for a pytest suite is "no process but
  the interpreter".
