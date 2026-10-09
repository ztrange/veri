# Three modules under the entry points: the ledger grammar, the test harness, the exit contract

**Superseded in part by [ADR-0030](0030-tests-change-by-parallel-change-and-mutation-parity.md)**: the deletion rule in *When a refactor may delete
a test* no longer forbids deleting a redundant test. A test is redundant when that is
measured, by mutation parity, never when it "looks redundant".

veri's target structure is its 64 scripts kept as **entry points** over a small number of
deep modules. This record names the first three: the **ledger grammar**, the **test harness**
and the **exit contract**. For each it gives the one-line responsibility, the interface a caller
must know and the existing code that moves in. It also fixes the one condition under which a
refactor may delete a test, and says what is deliberately not a module. The vocabulary is the
`codebase-design` skill's: a *module* is anything with an interface and an implementation; its
*interface* is everything a caller must know, invariants and error modes included; *depth* is
behaviour per unit of interface learned.

## Context

PRD 007 (#491) makes a long refactor a run kind. Its extraction issues — #495 (ledger), #496
(harness), #497 (exit contract) — and its dead-code sweep #498 all need an agreed destination
before the moves start, and PRD 007 decided that destination is recorded first. The survey
behind this record (2026-09-27) found:

- **The ledger grammar is re-spelled at 11 sites in 9 spellings, one of them Python.** They
  disagree at the edges: only `preserve-attempt.sh:62` and `metrics.sh:304` accept `[X]`;
  `status.sh:23` and `add-ledger-step.sh:31` accept no indent while the rest accept any; the
  awk writers `tick-criterion.sh:17` and `clear-refactor-pending.sh:32` accept a tab after the
  dash, which no reader does; `criterion-finished.sh:16` puts the criterion number into a regex
  unescaped. `SKILL.md:1316` carries an inline copy of `next-unchecked.sh:23-24`. The mark
  `⟂ refactor pending` is a literal in 4 scripts, the path `.tdd/issue-<n>.md` in 5. None of
  the disagreements bites yet: none of the 198 ledgers in `.tdd/` has an indented or `[X]`
  step. The same grammar also ticks the GitHub issue body (`tick-issue-criterion.sh` →
  `tick-criterion.sh`).
- **The harness is copied into all 147 suites.** Every one initialises `pass=0 fail=0` and
  ends in the count line; `report` is defined 97 times, 92 of them byte-identical; the `ok`/`no`
  pair 21 times; about ten bespoke `check()` functions each take a different argument order.
  84 suites call `mktemp -d` and 64 register their own `trap … EXIT`. Only
  `tests/record-helpers.sh` (#225) is shared, by four suites. And a suite-owned trap is not
  safe today: `bg_start` (`lib/background.sh:64`) runs `trap _bg_report_survivors EXIT`,
  replacing whatever EXIT trap its shell had, so `workqueue.test.sh` — trap at `:28`,
  `bg_start` at `:412` — leaves its scratch directory behind on every run. Observed, not
  inferred.
- **The exit contract's edges are hand-built five ways.** "Missing argument → usage on stderr →
  exit 2" is written as `[[ -n "${1:-}" ]] || { echo "usage: …" >&2; exit 2; }` in 23 scripts,
  through a `USAGE=` variable in 8, a lowercase `usage=` in 3, a local `refuse()`/`usage()` in
  4 and a `name: usage:` prefix in 4; about 23 scripts print no usage at all. The audit
  (`tests/unit/missing-argument-exit.test.sh`) reads a hand-kept roster of 26 scripts and misses
  11 that print usage. About nine sites hand on a foreign exit code unexamined — `run-leaf.sh:86`
  (`claude`'s), `timed-test-run.sh:59` and `run-suite.sh:67` (the target's test command's; a
  failing `make` exits 2), `tick-ledger.sh:46` among them.

## Decision

### What this extends in PRD 003

PRD 003 (#335) and its worked example `push-branch.sh` (#339) already fix that a script's logic
lives in sourceable functions behind a main guard; CLAUDE.md records it under "Testing idiom".
That stands as it is. This record adds only what a **module** needs beyond a script:

- A module is a file under a `lib/` directory, **sourced, not run**, and its header says so in
  those words. It has **no main guard** and no command-line contract; the entry points that
  source it own those.
- A module's functions **`return`, never `exit`** — they run in the caller's shell, as
  `lib/leaf-role.sh`'s header already argues. The exit contract's `refuse` is the one named
  exception, below, and its header says why.
- A module has **its own suite in the unit tier**, testing through its interface — the seam
  callers and tests share. A caller's suite keeps testing the caller.
- A module replaces its copies in the order #495 fixes: expand (the module exists beside the
  copies), migrate (callers source it, one per commit), contract (the last copy goes).

### The ledger grammar — `skills/tdd/scripts/lib/ledger.sh`

**Responsibility:** the one place a step line of a plan checklist is read or written, whether
the document is a ledger or the issue body mirroring it.

**Interface:**

| | |
|---|---|
| `ledger_path <n>` | prints `.tdd/issue-<n>.md` |
| `ledger_steps` | stdin → one tab-separated record per step, in document order: `index  state  kind  pending  added  criterion  text` |
| `ledger_tick <matcher> [pending]` | stdin → stdout: ticks the first open step whose line contains `<matcher>`; with `pending`, appends ` ⟂ refactor pending` in the same write |
| `ledger_clear_pending <matcher>` | stdin → stdout: removes the mark from the first ticked step containing `<matcher>` |
| `ledger_add_step <text> <k>` | stdin → stdout: appends `- [ ] <text> ⟦added⟧ ⟦criterion k⟧` after the last step |

What a caller must know:

- **The document is a stream, not a path.** Every function but `ledger_path` reads stdin, so
  the same code serves the committed ledger and an issue body fetched from GitHub.
- **Read leniently, write canonically.** A step line is any indent, a dash, whitespace, and a
  box of `[ ]`, `[x]` or `[X]`. A writer always emits `- [x]` lowercase, a mark separated by one
  space, marks in the order SKILL.md's plan format shows. A line with no box — the `## Owed
  steps` section's `- text` lines, headings, prose — is not a step and passes through untouched.
- **The record is the interface.** `index` is 1-based over step lines only. `state` is `open`
  or `done`; `kind` is `step`, `full-suite` or `human-owed`; `pending` and `added` are `0`/`1`;
  `criterion` is `k` or empty; `text` is the step's text with its marks removed, and is last so
  it may hold anything. Adding a field is a change every reader sees, so it is a decision, not
  a tweak. Readers in other languages — `metrics.sh`'s Python — read these records, never the
  markdown.
- **A writer changes at most one line** and leaves every other byte as it was.
- **Error modes:** `3` when no step matches (nothing to do, as `tick-criterion.sh` answers
  today); `2` on a missing argument; never `1`, since no ledger question has a clean negative.

**Moves in:** the step patterns of `next-unchecked.sh:23-24`, `tick-criterion.sh:17-18`,
`clear-refactor-pending.sh:20,32,35`, `criterion-finished.sh:16-19`,
`next-pending-refactor.sh:17-18`, `preserve-attempt.sh:62`, `metrics.sh:304`, `status.sh:23-24`
and `add-ledger-step.sh:31,37-39,47,53-54`; the mark literal of `tick-ledger.sh:20`; the path
spellings in `metrics.sh:158`, `preserve-attempt.sh:83`, `status.sh:189`,
`ensure-run-state-ignored.sh:28` (and `dashboard_endpoints.py:122-124` through the records or
the path, whichever it needs). `SKILL.md:1316`'s inline copy becomes a call to a script. The
scripts themselves stay: each becomes its argument check plus a call.

### The test harness — `skills/tdd/scripts/tests/lib/harness.sh`

**Responsibility:** the scaffolding every suite repeats — counters, failure lines, the count
line, scratch space, cleanup and the two fixtures most suites build by hand.

**Interface:**

| | |
|---|---|
| (on source) | sets `pass=0 fail=0` and `problems=()`, and installs the suite's one EXIT trap |
| `ok` / `no <name> [detail…]` | count a pass; count a fail and print `FAIL - <name>` |
| `report <name>` | close a case over `problems`: empty is a pass, otherwise one FAIL line and one indented line per problem — as the 92 identical copies do today |
| `expect_eq <name> <expected> <actual>` | pass on equality, otherwise FAIL and the indented diff |
| `scratch_dir` | prints a new temporary directory, registered for deletion at exit |
| `on_exit <cmd…>` | registers any other cleanup |
| `new_repo <dir>` | an initialised git repository with a fixed identity; what it holds is the caller's |
| `claude_stub <dir> <body>` | writes an executable `#!/bin/sh` stub at `<dir>/claude`, for `CLAUDE_BIN` |
| `finish` | prints `----` and `<n> passed, <m> failed`, returns non-zero if anything failed |

What a caller must know:

- **`finish` is the suite's last command, called explicitly.** Never from a trap: a suite that
  dies partway must not reach its count line, which is the whole of #157's guard.
- **The harness owns the EXIT trap.** A suite never writes `trap … EXIT`; it registers with
  `scratch_dir` or `on_exit`. The bug above is why.
- **Sourcing runs nothing but bash.** No `git`, no `mktemp`, no process until a function is
  called, so a unit-tier suite can source it under `make unit`'s shims. `new_repo` is for
  `tests/` suites only.
- **Primitives only.** A suite's bespoke `check()` stays in the suite, rebuilt on these.
- **The harness reads and sets no `VERI_*` variable**; each suite's isolation from ambient
  tunables stays where it is, and `hermetic-suites.test.sh` still pins it.

`tests/record-helpers.sh` is split: its `report` goes into the harness; `plain`, `says`,
`bullet` and `records` stay there, for the docs-record suites only, and it sources the harness.
A suite under `docs/tests/` may source the harness; none is required to.

**Moves in:** the 97 `report`, 21 `ok`/`no`, the counter initialisation and closing count line
of all 147 suites, the diff-on-failure idiom (8 sites), the `mktemp -d` + `trap` pairs (84/64),
the `new_repo` copies (6) and the `claude` stub heredocs (about 10).

### The exit contract — `skills/tdd/scripts/lib/exit-contract.sh`

**Responsibility:** the edges of CLAUDE.md's four-code contract — refusing a bad call, and
handing on a code that came from elsewhere.

**Interface:**

| | |
|---|---|
| `USAGE` | set by the sourcing script: its own usage line |
| `refuse [message]` | prints `message` if given, then `$USAGE`, on stderr, and **exits 2** |
| `require_args <n> "$@"` | `refuse`s unless the first `n` arguments are present and non-empty |
| `to_contract <code>` | prints `code` if it is 0–3, otherwise `2` |
| `# pass-through: <why>` | the marker a site carries when handing on a foreign code unmapped *is* its contract |

What a caller must know:

- **`refuse` exits.** It is the one module function that does, because a refusal that returns
  can be forgotten — a site missing `|| return` would carry on past it. A unit suite calls a
  script's `main` in a subshell, as `push-branch.sh`'s already does.
- **Every `exit` of a variable either maps or declares.** `exit "$(to_contract "$rc")"`, or
  `exit "$rc"` with a `# pass-through:` line saying why — e.g. `timed-test-run.sh`, whose caller
  asks for the test command's own status. Handing on another veri script's code is in-contract
  and still takes the marker. A site whose foreign codes mean something else in veri —
  `claude` exiting 1 is a plumbing failure, not a methodology one — maps them at that site;
  that mapping is #497's work at `run-leaf.sh`, not a table in the module.
- **The audits find their own subjects.** The missing-argument audit covers every script whose
  source prints usage, not a roster; a second audit fails any `exit "$var"` or `exit $?` with
  neither `to_contract` nor the marker.

`lib/missing-argument-exit.sh` stays what it is — the audit's judge, used by suites, not by
scripts.

**Moves in:** the five refusal idioms above (23 + 8 + 3 + 4 + 4 sites) and the nine
pass-through sites.

### When a refactor may delete a test

Only with its subject. When a symbol is deleted as unreachable, a **suite**, a single **case**,
or a **roster or exemption row** dies with it if and only if **every** assertion in it is about
that symbol. A suite or case that asserts anything else as well is never deleted under a
refactor: the removal is reported instead, and it becomes its own issue with its own predicate.
No other test is deleted under a refactor — not one that "looks redundant", not one a module's
own suite now duplicates.

Removing duplicated **helper definitions** from suites (#496) deletes no test: no case and no
assertion goes.

### What is not a module

| | Why |
|---|---|
| `SKILL.md` | PRD 007 rejected splitting it: prose cannot be refactored as safely as code. |
| The 64 top-level scripts | Entry points — SKILL.md, the Makefile and the hooks call them by name, so their command-line contract is fixed. Each is a thin adapter from its arguments to the modules. |
| Prompt text in `build-*-prompt.sh` heredocs | What a model reads is behaviour (PRD 007's comment class 3); reshaping it is not a refactor. |
| The docs pipeline, `docs/wt/*.py` | The documentation lane's, which a development run never touches (#143). |
| The other 13 files in `scripts/lib/` | Already sourced functions under PRD 003. This record neither renames nor folds them; an issue may, with its own evidence. |

### Rejected

- **Ledger: exported regex constants.** The spelling moves to one place but every caller still
  composes it and chooses its own tolerance, and awk and Python cannot read a bash variable
  without plumbing.
- **Ledger: one function per operation, mirroring the scripts.** Deep enough, but the Python
  copy in `metrics.sh` stays a second spelling kept in step by hand.
- **Ledger: strict reading.** It turns a hand-edited `[X]` into a step that silently stops
  counting, for no gain — no ledger uses the variants.
- **Harness: absorbing the bespoke `check()`s.** Ten signatures that each serve one or two
  suites — a shallow interface.
- **Harness: the count line from an EXIT trap.** It prints on a partway death too.
- **Exit contract: a declarative argument parser.** The framework PRD 007 and #496 rule out;
  flag handling already differs per script (`lib/verify-options.sh`).
- **Exit contract: `refuse` returns 2.** Keeps the library rule unbroken, at the cost of every
  call site, and a forgotten `|| return` continues past a refusal.
- **Exit contract: one generic map for every pass-through.** Wrong where a foreign `1` is
  veri's `2`. **Per-source tables** are precise but grow a table per source for nine sites.

## Consequences

- #495, #496, #497 and #498 lose their `Blocked by` on #492 when this lands.
- `affected-suites.sh:49` maps only `scripts/lib/*.sh` to the suites that source it, so a
  change to `tests/lib/harness.sh` would select no suite. #496 either runs the whole tier on a
  harness change or teaches that rule the new directory.
- `bg_start` must chain onto its shell's EXIT trap rather than replace it; that is a fix to
  `lib/background.sh` in its own right, since `orchestrate.sh` uses it too, and the harness's
  own trap depends on it.
- **Open:** the event log (`event.sh`, `lib/event_log.py`) is a plausible fourth module. No
  issue asks for it, so it is not decided here.
