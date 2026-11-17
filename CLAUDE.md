# veri — working notes for agents

A Claude Code skill suite that solves one GitHub issue under strict TDD. The whole
product is `skills/tdd/`: a procedure (`SKILL.md`) Claude follows, plus the scripts it calls,
which are Python modules behind `/bin/sh` shims. `invisible-work.sh` (#197) and
`unreachable.sh` (#498) are maintenance utilities the procedure never calls. `CONTEXT.md` is the glossary; its terms (conductor, leaf,
supervisor, verdict, ledger, bail) are used precisely everywhere.
Two sections no leaf reads, "Versions are tags, and nothing else" and "`make test` on the
development Mac", live in [operator/MAINTAINING.md](operator/MAINTAINING.md).

## Commands

veri: fast tests: `make unit`
veri: all tests: `make test`
veri: one test file: `make test TESTS="$1"`

| | |
|---|---|
| `make test` | The full suite, and the baseline veri detects in its own repo: it must stay green, since a red baseline makes the conductor refuse to start. |
| `make unit` | The fast tier: `skills/tdd/scripts/tests/py/unit/` only, without the `process` and `tree_audit` cases. |
| `make install-dev` | Once per machine: creates the shared venv at `$VERI_VENV` (default `~/.veri-tools/venv`) and installs the hash-checked lock `requirements-dev.txt` (generated from `requirements-dev.in`, installed with `--require-hashes`). Idempotent, never activated; it prints the `export PATH=…` line for scripts that run `python3` from PATH. |
| `make profile` | Runs the suites `make test` runs and prints one line per case at or above `VERI_PROFILE_THRESHOLD` seconds, slowest first. Nothing gates on it. |
| `make unreachable` | Lists the scripts no declared entry point reaches, through `unreachable.sh`. |
| `make report` | Prints the `/vreport` figures, through `report.sh`. |
| `make watch` | Reruns `make unit` whenever a tracked file changes. Nothing gates on it. |
| `make run-finished ISSUE=<n>` | Says whether run `<n>` is safe to merge, through `run-finished.sh`. |
| `make ready-check` | Reports whether veri can run in this repository, through `ready-check.sh`. |

Operator sessions, and every subagent they brief, run with `$VERI_VENV/bin` (default
`~/.veri-tools/venv/bin`) first on PATH, since PATH's `python3` may lack pytest.

CI runs `make test` only, on Linux only, with `timeout-minutes` on every job; never on a draft PR,
and a newer push cancels a PR's in-progress run (never on `main`). It restores the bytecode cache the
last push to `main` saved; only such a push saves it.

**veri needs bash 5+** (`brew install bash` on a Mac): `make test`, `run-conductor.sh` and
`leaf-launchable.sh` refuse an older one (exit 2).

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

## Invariants worth not breaking

- **A run executes one skill snapshot.** `run-conductor.sh` pins the skill to the commit in
  `.tdd/issue-<n>-skill-commit` and refuses (exit 2) one the clone cannot resolve; only
  `VERI_NEW_SKILL=1`, or the `.tdd/issue-<n>-released` marker a successful `release-issue.sh <n>` leaves and the
  next launch consumes, re-pins (a `skill-repin` event). The snapshot is read-only, and a run stops (exit 2) when it
  changed since extraction: `supervise.sh` refuses the next launch, `run-conductor.sh` its exit.
- **Every leaf is launched through `supervise.sh`**, never `run-leaf.sh` or `claude` directly:
  stuck detection lives only there.
- **The verifier is blind by construction.** No input of `build-verify-prompt.sh` can carry the
  developer's rationale, so it cannot leak; every input is checked against that, and none may be
  added that could. The `refactor` phase takes `<base-sha>` instead of the test id (#151),
  exit 2 unless it matches `^[0-9a-f]{7,40}$`, so it can carry only a hex commit name; the
  verifier reads `git diff <base-sha>..HEAD`, not commit messages. `VERI_SKIP_VERIFY` (pinned per
  run, `plan` never) skips the named verifiers (ADR-0033).
- **The committed ledger is the source of truth** for done steps; the issue only mirrors it.
  A step's green tick appends `⟂ refactor pending`, removed only by its verify-refactor PASS,
  so a resumed run can tell green from finished.
- **Nine budgets on nine axes, never merged**: `VERI_STUCK_RETRIES` (liveness — no answer),
  `VERI_NO_VERDICT_RETRIES` (protocol compliance — finished without a `VERDICT:` line),
  `REVISE_BUDGET` (verdict — rejected), `VERI_REFACTOR_BUDGET` (cost — the transforms one
  refactor leaf may apply for the whole step; ADR-0017) and `VERI_STEP_GROWTH_PERCENT` (plan
  growth — max `⟦added⟧` steps per ledger, as a percent of the steps in the verified plan, rounded
  up; ADR-0022), never folded into the other four, and
  `VERI_SKILL_EDIT_BUDGET` (the attempts one `⟦skill-edit⟧` step's author may make), a sixth on an
  axis of its own, never folded into the other five, and `VERI_MISSING_REROUTE_BUDGET` (repeat
  missing reroutes per step), a seventh on an axis of its own: a missing test is not a rejected
  product, and `REVISE_BUDGET` would bail correct code, and `VERI_ADJUDICATE_BUDGET` (exit-2
  judgments per run, default 2; 0 keeps today's behaviour), an eighth on an axis of its own, never
  folded into the other seven, and `VERI_CI_FLAKE_RERUNS` (CI re-runs of a red head per run, default
  1; 0 keeps today's behaviour), a ninth on an axis of its own, never folded into the other eight: a
  flaky CI job is not a defect. One knob over
  any two would make different failures one decision (ADR-0020). A bad `VERI_REFACTOR_BUDGET`
  is caught in preflight.
- **The developer's and the verifier's models are separate knobs**: `VERI_MODEL` (every leaf),
  `VERI_MODEL_DEVELOPER` (`develop-*`, `revise-*`), `VERI_MODEL_REVISE` (redo leaves:
  `revise-*`, `develop-exhausted`), `VERI_MODEL_REVISE_GREEN` (`revise-green` only, so it beats
  `VERI_MODEL_REVISE` there), `VERI_MODEL_VERIFIER` (`verify-*`),
  `VERI_MODEL_ADJUDICATOR` (the `adjudicate` leaf; unset, it runs on opus) and
  `VERI_MODEL_CONDUCTOR` (the conductor); the narrower one wins. Unset, first-try developers
  and verifiers run on sonnet, redo leaves and the conductor on opus (an empty
  `VERI_MODEL_CONDUCTOR` counts as unset). A weaker verifier shows as a changed verdict
  distribution, a weaker developer as more revise cycles; one knob would hide which.
- **Selection is four bands, one sort key.** `solvable-issues.sh` lists `priority` `bug`s first,
  then the other `priority`-labelled issues (`VERI_PRIORITY_LABEL`; set-but-empty is exit 2), then `bug`s, then the rest,
  each band ascending by number. A `low-risk` bug counts as the rest, and `priority` outranks `low-risk`.
  An issue also inherits the band of every open issue that names it under `## Blocked by`,
  transitively, taking the better of its own band and the inherited one: blocking a `priority`
  `bug` puts it in the first band, blocking another `priority` issue in the second, and blocking
  a plain `bug` lifts nothing. The bands only reorder the solvable set, never enlarge it,
  inherited bands included: open, opted in (`VERI_LABEL`), written by an `OWNER`, `MEMBER` or `COLLABORATOR` or
  labelled `VERI_AUTHOR_LABEL` (default `author-read`) once read, unblocked and unclaimed filter first,
  so neither `priority` nor blocking a `priority` issue makes an issue takeable.
- **Refactor-owed items are issues titled `Refactor candidates left by #<n>`**, labelled `refactor`
  and `refactor-owed` and never opted in (no `VERI_LABEL`), so selection never takes them;
  `/vgroom --refactor-owed` reads them.
- **An issue labelled `legacy` is the legacy kind**, never also `refactor` (capture refuses both,
  exit 2): it runs Seam → Surround → Verify under `skills/tdd/LEGACY.md`, wrapping a region in
  black-box tests driven through a seam before any refactor touches it.

## Testing idiom

Every suite is pytest, under `skills/tdd/scripts/tests/py/`; `make test` and `make unit` each run
one `pytest` invocation, and nothing under `tests/` ends in `.test.sh`. pytest's own exit code is
trusted: 0 only when every collected test passed, 5 when none were collected. The autouse
`hermetic_environment` fixture in `tests/py/conftest.py` makes a case hermetic from ambient `VERI_*`.
It also sets `VERI_EVENT_STRICT=1`, so a case that writes an event `veri/event_table.py` does not allow
(an undeclared name or key, a missing required key, a value that breaks its key's declared format, or an empty value where none is allowed) gets exit 2 from `event.sh`/`event.mark`; a run's conductor never carries it.
`make test TESTS="<pytest file or node id> …"` runs only those, in the same one invocation.
The leg runs the non-`serial` cases, then a second pytest pass over the `serial` ones only when the first collected one; veri's own
tree holds no `serial` case (`unit/test_no_serial_case.py` names the file and line of any), so `make test` on veri is one pytest session. When both run, its output ends with one
line totalling them, `<named> named, <run> run, <passed> passed, <failed> failed across both passes`, not the second pass's
`N deselected` line. A `--subset` run handed a `-m` exits 1, printing `<n> unselected: named cases that neither pass ran (<targets>)`,
when a named target (file, directory or node id) holds cases its `-k` keeps of which neither pass ran one; a case its own
`-m` or `-k` deselects from a target that did run never counts (#3554). The serial pass is handed only the test files that hold a `serial` case, as pass 1 recorded them (rootdir and ini file kept, so case ids read the same), and the totals line and every refusal read as if it had collected everything; a target naming a case (`::`), or no record, leaves it collecting the whole selection.

**`skills/tdd/scripts/tests/py/unit/` is the fast tier**, run by `make unit` and by `make test`.
Admission bar: about 100 ms per case, no git, network, servers, real waits (`sleep`), nested
suites, or script run as a subprocess.

**`make unit` and `make test` run pytest** over `skills/tdd/scripts/tests/py/`
(`make unit`: `tests/py/unit/` only), launched by `skills/tdd/scripts/tests/leg/pytest_leg.py` on
`$VERI_VENV/bin/python3` (default `~/.veri-tools/venv`, from `make install-dev`; else PATH's
`python3`). Admission rule: no process but the interpreter. Each case times out at 30 s
(`VERI_PYTEST_TIMEOUT`, `@pytest.mark.timeout(n)`), a `process` case, or a `tree_audit` case, with no `timeout` mark of its own at 90 s
(`PROCESS_CASE_TIMEOUT` in `tests/py/conftest.py`), since load stretches a real process and a tree audit's cost scales with the whole tree; an explicit mark wins; a wait inside a case bounds itself below `VERI_PYTEST_TIMEOUT` (30 s by default), or its failure path is unreachable because pytest-timeout fires first. A per-case timeout cannot fire once no case runs, so a leg in which no case starts or reports for `VERI_PYTEST_IDLE` seconds (default 1200, above the longest timeout mark, 900) ends itself (#4254): it writes its own threads' stacks and, through SIGUSR1, each worker's to stderr, ends its workers (TERM, then KILL by pid after 5 s), prints one stderr line naming the idle time and the last case it saw, and exits 2; a leg sent TERM or HUP ends its workers the same way and exits 128 + the signal's number without waiting on xdist's worker teardown. Either way it removes its `~/.veri-pytest-legs` entry and releases the full-run lock first. A case may run silently for as long as its timeout, so a `VERI_PYTEST_TIMEOUT` (or a timeout mark) above `VERI_PYTEST_IDLE` lets the idle window end a leg whose slow case is still running; keep the window above every timeout. The bytecode cache
(`PYTHONPYCACHEPREFIX`, at `VERI_PYCACHE`, default `${TMPDIR:-/tmp}/veri-pycache-<uid>`, which the Makefile sets when unset) persists between runs
(`make test` and `make unit` create it with mode `0700` and refuse, exit 2 before any suite, one that is not a directory owned by the
current user and writable by neither group nor others, a symlink included, or whose parent group or others can write without the
sticky bit, naming the path and the fix: remove it, or set `VERI_PYCACHE`), and a manifest of source hashes keeps a changed module,
a same-second mutation included, from being served a stale `.pyc`: before importing, the leg drops
every `.pyc` the manifest does not vouch for by the hash of its source, and `.opt-N` files always; a pytest-rewritten `.pyc` is
vouched for like any other, recorded only when its header carries its source's mtime and size and the source did not change after the run began
(#1127, #2054). Sources a case creates under the run's `veri-pytest-*` scratch directory leave their `.pyc` under that path mirrored in the prefix, so after a run the leg removes the mirror of its own run directory, and the sweep of a dead run (pid no longer answering `kill 0`) removes that run's mirror with its directory; a tree that does not resolve to exactly such a mirror inside the prefix, or whose run it cannot prove dead, is left alone. A shim run has no manifest, so `shim-python.sh` clears the prefix and sets `PYTHONDONTWRITEBYTECODE=1`, and `veri/pycache_prefix.py`, which a module's first line runs before any veri import, compiles veri's modules from source: the run neither reads nor poisons a cache (#2406, #2439), while the standard library keeps its own `.pyc` files, since a prefix would recompile them on every start.
A veri module run directly as `python3 <module>` with bytecode writing on takes the shared prefix from the same file, but only when it is a
directory, not a symlink, owned by the current user and writable by neither group nor others, in a parent group and others cannot
write unless it has the sticky bit (as `/tmp` does), created with mode `0700` when absent; otherwise it sets no prefix, compiles veri's
modules from source and says why on stderr (#3965). A `PYTHONPYCACHEPREFIX` the caller exported is honoured by the interpreter for the
standard library before that check can run, so the check covers veri's own modules and `make`'s guard covers a `make` run. Cases run across pytest-xdist
workers: `make unit` 4 (each worker pays its own start-up); `make test` the cores other running
legs leave free (physical cores on macOS, the CPU-affinity count elsewhere), at least 1 (#2100): each leg registers its pid and count under
`~/.veri-pytest-legs` (`VERI_PYTEST_LEGS`), and a dead pid holds no share.
`VERI_PYTEST_WORKERS=<n>` overrides both, used as given; `1` runs serially (#2053). Three refusals, exit 2 before any
suite: pytest or pytest_timeout not importable (stderr names `make install-dev`), or Python
older than the 3.12 floor. Any other error escaping the leg (registering it, taking the full-run lock, checking or recording
the bytecode cache) is one stderr line naming it, never a traceback, and exit 2, except that a failing run keeps its exit 1.

At most one full `make test` runs per machine (#2195): a second waits, naming the holder's pid and working tree on stderr,
before its suites start, so the wait counts toward no per-case timeout. The lock is an `flock` held for the whole run, so a dead
holder's lock is taken over; a run nested under the holder (`PYTEST_LEG_FULL_LOCK_HOLDER`) skips it, and neither `make unit` nor a
`make test TESTS=…` subset (`--subset`) ever waits. Release empties the lock file, so it names a pid only while held. By that rule a live holder that never releases blocks the waiter
without bound: the wait counts toward no timeout that could bail it, a supervised leaf's hard timeout and silence window included (#2380).
A waiting leg marks its wait with a file naming its pid and start time; a supervisor ignores a marker whose waiter is no longer
alive under that start time, so its hard timeout and silence window run, while an empty marker (an older leg's) still freezes them (#3989).
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

Per step, the red and refactor leaves run the
affected suites; `develop-green`, verify-green and verify-refactor run the fast tier plus the
affected suites; a revise leaf runs the tiers of the phase it redoes. `make test`, the
**full suite**, runs once per PR before the PR is readied, again per repair step a red result
appends (#539), and on the rebased tip if the Draft PR step rebased (#1026) — unless
`rebased-tip-suite.sh` prints `ci`, the default where a workflow triggers on pull requests, which
leaves that tip's run to CI. Where `branch-suite.sh` prints `ci`, by the same default, the run before
readying is not made either: CI's run on the readied PR is the PR's full suite, and a red one gets
the one `⟦ci-repair⟧` step.

Tests inject rather than wait on a real model or clock: `CLAUDE_BIN` swaps in a stub,
`VERI_HEARTBEAT` / `VERI_TOOL_IDLE` / `VERI_TIMEOUT` / `VERI_STUCK_RETRIES` shrink the supervisor's windows,
`VERI_FETCH_RETRY_SLEEP` the ref-lock retry — hence every tunable is read as `${VAR:-default}`.

**A suite asserts behaviour** — outputs, exit codes, files, events; never process counts,
fork counts or timings (observe those with `make profile`, report them in the PR body).
**No suite runs another suite.** When a call count is
the behaviour, the code calls one wrapper and the test swaps in an in-process spy, never a
PATH shim counting processes.

A guard or failure path never watched to fail is not tested: break it, see it go red, restore.

## Graded prose

A `GRADED` file holds one line per graded unit, its fields split on a single space: the unit
path, the signature, the date, the grading id and the grader-template prefix. `grade-prose.sh`
writes the line when a grade PASSes; it is never written by hand. Since the fields are split on
single spaces, a heading unit's field writes each `%` as `%25` and each space as `%20`, and every
reader decodes it.

The signature is a sha256 over the unit's text, its requirement rows and the grader model (plus
the grader's effort level when `skills/tdd/grader.conf` sets one), so a change to any of them
makes the unit owe a grade, however unrelated the edit looks.

A unit's rows live in the `REQUIREMENTS.md` beside its `GRADED` file, under a heading naming the
unit (`## <unit path>`). A unit under `skills/<x>/` is signed in `skills/<x>/GRADED`; any other
unit in its own directory's `GRADED`.

A unit may be one section of a file, a heading unit named `<file>#<heading>`, with its rows under
`## <file>#<heading>` in the `REQUIREMENTS.md` beside the file. Its text is its own text: its
heading line and the lines after it, up to the next unfenced heading line of any level, so its
subsections are not in it. Once any tracked `REQUIREMENTS.md` lists a heading unit of a file, that
file's whole-file unit is split: it is shown to the grader and signed over its view instead of the
file's text. The view is the file's heading lines in order, then the text above the first heading
and the own text of every section no heading unit claims. So an edit inside a claimed section owes
only that section's unit, and an edit to a heading line still owes the whole-file unit.

`prose-owed.sh`, run by `make unit` and `make test`, exits 1 listing each unit that owes a grade
and each orphan `GRADED` line (one whose unit has no rows any more). A `⟦skill-edit⟧` step
regrades a unit.
