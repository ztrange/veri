# veri — working notes for agents

A Claude Code skill suite that solves one GitHub issue under strict TDD. The whole
product is `skills/tdd/`: a procedure (`SKILL.md`) Claude follows, plus the bash scripts
it calls. `invisible-work.sh` (#197) and `unreachable.sh` (#498) are maintenance utilities
the procedure never calls. `CONTEXT.md` is the glossary; its terms (conductor, leaf,
supervisor, verdict, ledger, bail) are used precisely everywhere.

## Commands

veri: fast tests: `make unit`
veri: all tests: `make test`

| | |
|---|---|
| `make test` | The full suite, and the baseline veri detects in its own repo: it must stay green, since a red baseline makes the conductor refuse to start. |
| `make install-dev` | Once per machine: creates the shared venv at `$VERI_VENV` (default `~/.veri-tools/venv`) and installs the pinned `requirements-dev.txt`. Idempotent, never activated; it prints the `export PATH=…` line for scripts that run `python3` from PATH. |
| `make docs` | Regenerates `docs/walkthrough.html`. Publishing it is by hand only (`gh workflow run pages.yml`); a merge never deploys. |
| `make install-hooks` | Once per clone: installs the `reference-transaction` hook that flags a tag the page does not list. Refuses to clobber a hook it does not recognise. |
| `make merge-gates` | Run before merging any PR, in its worktree on the rebased tip. Runs only the docs gates the diff against `origin/main` warrants: nothing for a README change, nothing for a change under `skills/` (#125), nothing for `docs/adr/` (#146), nothing for a `Makefile` change (#164); `docs-fresh` for a hand-edited page; `make docs-test` plus `docs-fresh` for anything else under `docs/` except `walkthrough.html` itself (#137). `VERI_GATES=all` forces both. |
| `make docs-fresh` | Rebuilds once and compares to the committed page. |
| `make docs-check` | The docs build guards still fire, and the committed page matches a fresh build. |

`docs-check` is not part of `make test` nor in CI, so docs lag never blocks a run. CI runs
`make test` only, on Linux only, with `timeout-minutes` on every job; never on a draft PR,
and a newer push cancels a PR's in-progress run (never on `main`).

**veri needs bash 5+** (`brew install bash` on a Mac): `make test`, `run-conductor.sh` and
`leaf-launchable.sh` refuse an older one (exit 2).

## The one trap

**`docs/walkthrough.html` is generated. Never edit it by hand** — edit its inputs, then `make docs`:

- prose, per-script commentary → `docs/wt/commentary.py` (chunks keyed by line range)
- source colouring → `docs/wt/bashlex.py` (four token classes, no more)
- bash reference entries → `docs/wt/primer.py`
- styling / tooltips → `docs/wt/style.css`, `docs/wt/app.js`

The build fails on a `{{p-id|…}}` naming a missing entry or a commentary chunk claiming lines
a script lacks; a line no chunk claims only prints `owed: <script> L<a>–<b>` and exits 0 (#125).

**All of this is the documentation lane's work, never a development run's** (#143): a `/tdd`
leaf or conductor whose test command is not a `make docs-*` target never edits the page or its
inputs, and `make docs` refuses it with exit 2 (it reads `VERI_TEST_CMD`).

## Exit codes are the API

Every script speaks these four codes and the conductor branches on them:

| | |
|---|---|
| `0` | success, or `PASS` |
| `1` | a clean negative — the leaf ran and failed, the verifier said `REJECT`. A real answer. |
| `2` | **no answer could be obtained** — killed-stuck, unparseable verdict, bad arguments |
| `3` | nothing to do — no unchecked step, no matching checkbox. Not an error. |

Never collapse 1 and 2: a process failure (the methodology spoke) is not a system failure
(the plumbing broke); `classify-bail.sh` labels bails by it.

## Versions are tags, and nothing else

A version is an annotated tag `vN.M` whose message is the capability, in the issue's words —
no `VERSION` file, no changelog. One merged feature/fix issue is one minor bump, cut by the
`merge` skill; docs, test and refactor PRs get no tag.

- **`git tag --sort=-v:refname`, never plain `sort`** — lexically `v0.9` outranks `v0.10`.
- **Backfilling needs `GIT_COMMITTER_DATE`**, or retro-cut tags claim today's date.
- **A regen commit at the tag isn't the fixpoint** (`unreleased` is `HEAD != latest tag`, #52,
  #53): `make docs && git commit`, then `make docs && git commit --amend --no-edit`, or
  `docs-check` goes red.

## Invariants worth not breaking

- **A run executes one skill snapshot.** `run-conductor.sh` pins the skill to the commit in
  `.tdd/issue-<n>-skill-commit` and refuses (exit 2) one the clone cannot resolve; only
  `VERI_NEW_SKILL=1` re-pins (a `skill-repin` event).
- **Every leaf is launched through `supervise.sh`**, never `run-leaf.sh` or `claude` directly:
  stuck detection lives only there.
- **The verifier is blind by construction.** No input of `build-verify-prompt.sh` can carry the
  developer's rationale, so it cannot leak; every input is checked against that, and none may be
  added that could. The `refactor` phase takes `<base-sha>` instead of the test id (#151),
  exit 2 unless it matches `^[0-9a-f]{7,40}$`, so it can carry only a hex commit name; the
  verifier reads `git diff <base-sha>..HEAD`, not commit messages.
- **The committed ledger is the source of truth** for done steps; the issue only mirrors it.
  A step's green tick appends `⟂ refactor pending`, removed only by its verify-refactor PASS,
  so a resumed run can tell green from finished.
- **Seven budgets on seven axes, never merged**: `VERI_STUCK_RETRIES` (liveness — no answer),
  `VERI_NO_VERDICT_RETRIES` (protocol compliance — finished without a `VERDICT:` line),
  `REVISE_BUDGET` (verdict — rejected), `VERI_REFACTOR_BUDGET` (cost — the transforms one
  refactor leaf may apply for the whole step; ADR-0017) and `VERI_STEP_GROWTH` (plan growth —
  max `⟦added⟧` steps per ledger; ADR-0022), never folded into the other four, and
  `VERI_SKILL_EDIT_BUDGET` (the attempts one `⟦skill-edit⟧` step's author may make), a sixth on an
  axis of its own, never folded into the other five, and `VERI_MISSING_REROUTE_BUDGET` (repeat
  missing reroutes per step), a seventh on an axis of its own: a missing test is not a rejected
  product, and `REVISE_BUDGET` would bail correct code. One knob over
  any two would make different failures one decision (ADR-0020). A bad `VERI_REFACTOR_BUDGET`
  is caught in preflight.
- **The developer's and the verifier's models are separate knobs**: `VERI_MODEL` (every leaf),
  `VERI_MODEL_DEVELOPER` (`develop-*`, `revise-*`), `VERI_MODEL_REVISE` (redo leaves:
  `revise-*`, `develop-exhausted`), `VERI_MODEL_VERIFIER` (`verify-*`) and
  `VERI_MODEL_CONDUCTOR` (the conductor); the narrower one wins. Unset, first-try developers
  and verifiers run on sonnet, redo leaves and the conductor on opus (an empty
  `VERI_MODEL_CONDUCTOR` counts as unset). A weaker verifier shows as a changed verdict
  distribution, a weaker developer as more revise cycles; one knob would hide which.
- **Selection is three bands, one sort key.** `solvable-issues.sh` lists `priority`-labelled
  issues first (`VERI_PRIORITY_LABEL`; set-but-empty is exit 2), then `bug`s, then the rest,
  each band ascending by number. The bands only reorder the solvable set, never enlarge it:
  open, opted in (`VERI_LABEL`), unblocked and unclaimed filter first, so `priority` alone
  never makes an issue takeable.
- **A walkthrough build asks git once per script, once per tag, and eight times besides**;
  `docs/tests/build-guards.test.sh` pins that budget. Ask `gitmeta._shipped()`'s table, never
  git per commit or per line.
- **A tag changes the page without a commit**, leaving `make docs-check` red until `make docs`.
  Deliberate: the hook only notices, and never rebuilds or commits.

## Testing idiom

Every suite is pytest, under `skills/tdd/scripts/tests/py/`; `make test` and `make unit` each run
one `pytest` invocation, and nothing under `tests/` ends in `.test.sh`. pytest's own exit code is
trusted: 0 only when every collected test passed, 5 when none were collected. The autouse
`hermetic_environment` fixture in `tests/py/conftest.py` makes a case hermetic from ambient `VERI_*`.
`make test TESTS="<pytest file or node id> …"` runs only those, in the same one invocation.

**`skills/tdd/scripts/tests/py/unit/` is the fast tier**, run by `make unit` and by `make test`.
Admission bar: about 100 ms per case, no git, network, servers, real waits (`sleep`), nested
suites, or script run as a subprocess.

**`make unit` and `make test` run pytest** over `skills/tdd/scripts/tests/py/`
(`make unit`: `tests/py/unit/` only), launched by `skills/tdd/scripts/veri/pytest_leg.py` on
`$VERI_VENV/bin/python3` (default `~/.veri-tools/venv`, from `make install-dev`; else PATH's
`python3`). Admission rule: no process but the interpreter. Each case times out at 30 s
(`VERI_PYTEST_TIMEOUT`, `@pytest.mark.timeout(n)`), a `process` case with no `timeout` mark of its own at 90 s
(`PROCESS_CASE_TIMEOUT` in `tests/py/conftest.py`), since load stretches a real process; an explicit mark wins; a wait inside a case bounds itself below `VERI_PYTEST_TIMEOUT` (30 s by default), or its failure path is unreachable because pytest-timeout fires first; the bytecode cache
(`PYTHONPYCACHEPREFIX`, at `VERI_PYCACHE`, default `${TMPDIR:-/tmp}/veri-pycache-<uid>`, which the Makefile and `shim-python.sh` both set when unset) persists between runs, and a manifest of source hashes keeps a changed module,
a same-second mutation included, from being served a stale `.pyc`: before importing, the leg drops
every `.pyc` the manifest does not vouch for, and pytest-rewritten and `.opt-N` files always
(#1127, #2054). A shim run outside `make` has no manifest, so `shim-python.sh` also sets `PYTHONDONTWRITEBYTECODE=1`
whenever it supplies the prefix itself: it reads what is there but never writes into it, so it cannot poison the cache (#2406).
A veri module run directly as `python3 <module>` takes the same prefix from `veri/pycache_prefix.py`, which its first line runs before any veri import. Cases run across pytest-xdist
workers: `make unit` 4 (each worker pays its own start-up); `make test` the cores other running
legs leave free (physical cores on macOS, the CPU-affinity count elsewhere), at least 1 (#2100): each leg registers its pid and count under
`~/.veri-pytest-legs` (`VERI_PYTEST_LEGS`), and a dead pid holds no share.
`VERI_PYTEST_WORKERS=<n>` overrides both, used as given; `1` runs serially (#2053). Three refusals, exit 2 before any
suite: pytest or pytest_timeout not importable (stderr names `make install-dev`), or Python
older than the 3.12 floor.

At most one full `make test` runs per machine (#2195): a second waits, naming the holder's pid and working tree on stderr,
before its suites start, so the wait counts toward no per-case timeout. The lock is an `flock` held for the whole run, so a dead
holder's lock is taken over; a run nested under the holder (`PYTEST_LEG_FULL_LOCK_HOLDER`) skips it, and neither `make unit` nor a
`make test TESTS=…` subset (`--subset`) ever waits. Release empties the lock file, so it names a pid only while held. By that rule a live holder that never releases blocks the waiter
without bound: the wait counts toward no timeout that could bail it, a supervised leaf's hard timeout and silence window included (#2380).
`VERI_TEST_LOCK=0` turns the lock off. A verifier's full run takes the lock like any other, and a verifier that breaks the lock code still cannot hang on it.

**Pytest case sizes** (#1259, #1513): an unmarked case is small — `git` and `python3` refuse
on its PATH (save `python3` on a `veri/` module). A case that starts a real process carries
`@pytest.mark.process("<boundary>")`; one that lists a repo directory outside its `tmp_path`
carries `@pytest.mark.tree_audit("<what it sweeps>")`. Collection refuses either without an
argument, and any unregistered mark. `make unit` deselects both; `make test` runs all. `gh`
and `curl` always refuse. Drive a ported script's CLI in-process with the
`run_cli(module, argv, stdin="", env=None, cwd=None)` fixture, which returns
`(code, stdout, stderr)`.

**A script ported to Python follows one convention; `status.sh` is the worked example**
(#634): its logic is a module of `skills/tdd/scripts/veri/`, and its `.sh` entry point a
`/bin/sh` shim that `exec`s `python3` on it — `$VERI_VENV/bin/python3` (default
`~/.veri-tools/venv/bin/python3`) when it meets the 3.12 floor (`VENV_FLOOR`), else the `python3` on PATH
when that does, else exit 2 naming each interpreter tried, its source and its version — holding no Python
source (no heredoc, no `python3 -c`). Its tests live in `tests/py/unit/test_<module>.py` (`tests/py/test_<module>.py`
when the guard names it), faking only process boundaries; its entry-point contract cases sit in
`tests/py/test_<module>_process.py`.

**A suite whose subject is the docs pipeline lives in `docs/tests/`, not here**, and runs by
existing (`make docs-test` globs it; #137). Per step, the red and refactor leaves run the
affected suites; `develop-green`, verify-green and verify-refactor run the fast tier plus the
affected suites; a revise leaf runs the tiers of the phase it redoes. `make test`, the
**full suite**, runs once per PR before the PR is readied, again per repair step a red result
appends (#539), and on the rebased tip if the Draft PR step rebased (#1026), so a docs suite
under its glob would tax every PR (ADR 0016). `docs/tests/suite-lanes.test.sh` pins the split.

Tests inject rather than wait on a real model or clock: `CLAUDE_BIN` swaps in a stub,
`VERI_HEARTBEAT` / `VERI_TOOL_IDLE` / `VERI_TIMEOUT` / `VERI_STUCK_RETRIES` shrink the supervisor's windows,
`VERI_FETCH_RETRY_SLEEP` the ref-lock retry — hence every tunable is read as `${VAR:-default}`.

**A suite asserts behaviour** — outputs, exit codes, files, events; never process counts,
fork counts or timings (observe those with `make profile`, report them in the PR body).
**No suite runs another suite.** When a call count is
the behaviour, the code calls one wrapper and the test swaps in an in-process spy, never a
PATH shim counting processes.

A guard or failure path never watched to fail is not tested: break it, see it go red, restore.

## `make test` on the development Mac

- Suite stubs are `#!/bin/sh`, and per-leaf helpers are functions sourced from `scripts/lib/`
  (#322, #323): Homebrew bash starts slowly.
- The `test` recipe gives every suite `LC_ALL=C`, `< /dev/null` and a symlink to the real
  `git` first on PATH; remote git is refused by
  `protocol.allow=never`, `gh`/`curl` by the plugin `pytest_leg.py` loads.
- The pytest leg pins `TMPDIR` to `/tmp` before it starts, so a local run's scratch matches CI's
  rather than the Mac's `/var/folders/…` (#2354): the leg's `veri-pytest-*` run dir, `--basetemp`
  and so every case's `tmp_path` live under `/tmp`, whatever `TMPDIR` the caller set. The pycache
  prefix is unaffected (the Makefile and `shim-python.sh` compute it from the host `TMPDIR` before
  the leg starts), as are the full-run lock and `~/.veri-pytest-legs`.
- macOS checks each new executable on its first run (~330 ms). Fix:
  `sudo spctl developer-mode enable-terminal`, enable the terminal under Privacy & Security →
  Developer Tools, restart it. A Claude desktop session is not covered; launch conductors
  from the enabled terminal.
- A speed issue states its acceptance criteria as behaviours only; quote `make profile`
  before and after in the PR body. CI's `timeout-minutes` is the only wall-clock gate.
