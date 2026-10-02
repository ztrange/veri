# A port moves coverage, and the old suite is the proof it moved

PRD 008 (#537) ports every veri script from bash to Python 3 behind its `.sh` entry point.
A ported script's cases move from its bash suite into `tests/py/test_<script>.py`, where they
run in-process. This record fixes which bash cases survive a port, the floor every ported
script keeps whatever the rule says, and what proves a port held the script's contract. It is
a **port's** rule. ADR 0026's rule for a **refactor** is unchanged.

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

### The proof

The proof that a port held the contract is **the old bash suite, green and unmodified, against
the new code, before any case is cut.** The cut is a later commit than that green run, so the
history shows the old suite passing against the ported script. A port whose old suite needed
editing to go green changed the contract, and is not a port.

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

## Consequences

- Each port issue under PRD 008 cites this record. Its PR body carries the pairs table, and
  its history carries the old suite green before the cut.
- Before #633 there was no `tests/py/`. Its pytest leg in `make unit` and `make test` is what
  the replacing cases run under, and its admission rule for a pytest suite is "no process but
  the interpreter".
