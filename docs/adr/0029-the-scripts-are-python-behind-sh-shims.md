# The scripts are Python behind `.sh` shims

PRD 008 (#537) moved every script under `skills/tdd/scripts/` from bash to Python. On `main`
at `6c697eb17` all 72 `*.sh` entry points are `/bin/sh` shims that `exec python3` on a module
under `skills/tdd/scripts/veri/`; the last port, `event.sh` (#1078), landed as v0.406. The PRD
decided the language, and its Children table said an ADR would close that decision with the
two spike PRs as its record. This is that record.

## Context

- **Two spikes priced the move.** #473 (Python) and #474 (Go) each ported `parse-verdict.sh`
  (pure text) and `push-branch.sh` (retries, backoff, git, a sibling call). Both held the CLI
  contract on 23 of 23 integration cases, unmodified, on the first run, and both ran ~30 unit
  cases in-process at 0.18–0.19 s wall. Neither spike won on speed or on contract fidelity.
  Both PRs were closed unmerged on 2026-09-28; they are kept as the record of the comparison.
- **Python was already a dependency.** Sixteen scripts and the docs build called `python3`
  before the port. Go was not on any machine that runs veri.
- **The entry points are called by name.** `skills/tdd/SKILL.md`, the `Makefile` and the git
  hooks invoke `skills/tdd/scripts/<name>.sh` with fixed arguments, and branch on its stdout,
  stderr and exit codes. A port that renamed an entry point, or changed any of those, would
  change every caller with it.

## Decision

### The language

The scripts are **Python 3, standard library only, floor 3.12** (`ubuntu-latest`'s
interpreter). Chosen over Go because it is already a dependency and needs no build step.
pytest is a development dependency of the test suites, not of the scripts.

### The seam

Each script's logic is a module in one package, `skills/tdd/scripts/veri/`. Its `.sh` entry
point is a **two-line `/bin/sh` shim** — the shebang and one `exec python3` on that module,
under the contract header — that keeps the entry point's **name, arguments, stdout, stderr
and exit codes** exactly as they were. Bash calls Python once per invocation, as a command.
Python calls tools (`git`, `gh`, `claude`, `sleep`) through `subprocess` directly, never
through a bash helper.

### Why a shim survives

A `.sh` entry point stays because **SKILL.md, the Makefile and the hooks call it by name**.
Removing it would move every one of those call sites onto `python3 -m veri.<module>` for no
gain in what veri can do, and would break the contract the old suites proved held.

A shim **holds no logic and no Python source**: no branch, no argument parsing, no heredoc fed
to `python3`, no `python3 -c` string. Everything it does is resolve its own directory and hand
`"$@"` to the module. Logic found in a shim is a port left unfinished.

### The test-deletion rule

Which bash cases a port deletes, which survive, and what proves a port held the contract are
ADR 0027's, and are not restated here.

## Rejected

Each of these is in #537's *Rejected* list, which holds the full reasoning:

- **Go (#474).** A build step, and a toolchain or a per-OS binary on every machine that runs
  veri.
- **A permanent bash core** for the launch chain and `event.sh`. Two idioms forever, to save
  ~45 s a run.
- **A long-lived Python process bash talks to.** A lifecycle and a protocol to save 45 ms per
  call, once per leaf.
- **Mocking git in integration suites.** git is the subject's environment there, and a PATH
  stub costs a bash start per call, more than git's own 8 ms.
- **Retiring the SKILL.md grep suites** as part of the port. They hold SKILL.md to the scripts
  until agent-graded requirements (#489) exist.
- **Parallel suites and a wall-clock gate.** PRD 003's rejections stand.
- **Keeping every bash case as a permanent oracle.** The port's speed gain becomes zero.

## Consequences

- A new script is written as a `veri/` module behind a `.sh` shim, never as bash logic.
- Its tests live in `tests/py/test_<module>.py`; its bash suite under `tests/` keeps only the
  contract cases ADR 0027 lets survive.
- The interpreter floor is enforced where a run begins: `run-conductor.sh` and
  `leaf-launchable.sh` refuse an interpreter below 3.12.
- Bash that remains is the 18 `lib/*.sh` files, the `*.test.sh` suites and the other helpers
  under `tests/`. None of it is an entry point.
