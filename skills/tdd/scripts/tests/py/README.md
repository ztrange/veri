# tests/py: the map of the test side

For an agent about to add or change a test. The production half has its own map, [`../../veri/README.md`](../../veri/README.md);
the test-writing contract (admission bar, case sizes, timeouts, the venv) lives in the "Testing idiom" section of the root
[`CLAUDE.md`](../../../../../CLAUDE.md), and the pytest leg's internals are stated here, in *The pytest leg*. `unit/test_tests_py_readme.py` fails when a helper
module or a conftest fixture has no bullet below, or a bullet names one that does not exist.

## Tiers and marks

| Tier | Mark | May do | Timeout | `make unit` | `make test` |
|---|---|---|---|---|---|
| small | none | no process, no repo listing, no real wait; `git` and `python3` refuse on its PATH, `gh` and `curl` always refuse | 30 s (`VERI_PYTEST_TIMEOUT`) | runs it, if its file is in `unit/` | runs it |
| medium | `@pytest.mark.process("<boundary>")` | starts a real process (git, a shim, a stub `claude`); the argument names the boundary observed | 90 s (`PROCESS_CASE_TIMEOUT`) unless it carries its own `timeout` mark | deselects it | runs it |
| tree audit | `@pytest.mark.tree_audit("<what it sweeps>")` | lists the repository's own directories | 90 s, as above | deselects it | runs it |
| serial | `@pytest.mark.serial("<reason>")`, besides any of the above | must not run beside a parallel load | as its size | by the rule above | runs in the leg's second pass, alone |

- Collection refuses an unregistered mark and a `process`, `tree_audit` or `serial` mark without its argument
  (`case_size_guards.pytest_collection_modifyitems`).
- `make unit` runs `-m "not process and not tree_audit"` over `tests/py/unit/` only, its workers drawn from T, the leg's
  budget (*The pytest leg*); `make test` runs
  everything under `tests/py/` through `tests/leg/pytest_leg.py`: the non-`serial` cases, then a second pass over the `serial` ones
  only when one was collected; veri's tree holds none (`unit/test_no_serial_case.py` fails naming the file and line of any), so it is one pytest session.
- The leg and the plugins it loads by name (`network_guard`, `small_case_guard`, `private_tmp_path`, `serial_seen`) live in
  `skills/tdd/scripts/tests/leg/`, beside `tests/py/` and outside its rootdir, never in the product package `veri/` (#4051);
  the TMPDIR it pins is `veri/leg_tmpdir.py`'s `PINNED_TMPDIR`, which run-conductor's free-space check reads too.
  `make test TESTS="<file or node id> ..."` runs only those, in the same invocation. The leg's internals: *The pytest leg* below; the test-writing contract: root `CLAUDE.md`, "Testing idiom".
- **A file lives in `unit/` only if `tests/py/fast_tier_guard.py` names none of its calls** (a process start, a real wait),
  enforced both ways by `test_fast_tier_guard.py`. So `make unit` runs `tests/py/unit/` only, and placement is judged per FILE:
  one case that calls `subprocess` (or sleeps) keeps every small case beside it out of `make unit`, and they run only in
  `make test` and in a leaf's `changed` run. So a file with a process case is split: its small cases move to `unit/test_<name>.py`,
  its process cases to `test_<name>_process.py`. Measured 2026-11-15 with `-m "not process and not tree_audit"`: the 22 files
  directly under `tests/py/` that are not `*_process.py` hold 121 small cases that `make unit` does not run. Left unsplit on
  purpose: `test_profile.py` (audits its own location), `test_detach_leaf.py` (its small cases all install a fake `Popen`),
  `test_event.py` (the journal's owners'), `test_conftest.py` (tests the fixtures; its ids are pinned), `test_parallel_conductors.py`,
  two files with one or two small cases, and files that hold only tree audits or only process cases. What the split taught: an
  unmarked case that goes through a local fake in front of a real process is not small; it lives with the process half until
  its fake is replaced by `fake_processes`.
- A `unit/` file may still hold marked cases (they are deselected by `make unit`): the guard sees calls, not marks.
- A new test file that starts no process and lists no repo directory goes in `unit/`; otherwise beside this file, a
  process-starting suite as `test_<name>_process.py` (the established route, 137 such files).

## Helper modules

Directly under `tests/py/`, beside `conftest.py`; import them flat (`from repo_builder import new_repo`).

- `case_size_guards.py`: the admission guards (autouse fixtures that fail a small case which starts git or a test runner, lists a repo directory, forces a failure through permission bits ...), their exemption tables, `register_markers` and the collection hook; conftest imports every name, so `conftest.<name>` works.
- `dispatch_world.py`: `FakeWorld(*ticks, role_state=(), unreadable=False)`, a scripted in-memory adapter for `dispatch.World`; the keys a tick may carry are in its docstring.
- `event_roster.py`: `emitted_events()` (every event name emitted under `skills/`, found by scanning for the shell and in-process emit calls) and `documented_events(text)`; behind `unit/test_journal_event_roster.py`.
- `fast_tier_guard.py`: the fast tier's admission guard, `offences(root, exemptions)` names the lines of test files that start a process or wait; behind `test_fast_tier_guard.py`.
- `fed_history.py`: `FedHistory` and `feeder`, behind the `fed_history` fixture, and `FedCommits`, behind `fed_commits`: case_history's git queries answered from a table of named revisions (`ANSWERED`: `toplevel`, `has_rev`, `current_branch`, `text_at`, `cases_at`, `revisions`, `first_revision_with`, `changed_test_files`, `commit_of`, `step_commits`, `subject`), every query it does not answer failing the case by name.
- `leaf_waits.py`: `leaf_started(read_pid, sleep, clock)` and `leaf_left(pid, alive, sleep, clock)`, waits on a real leaf bounded far above load delay; `sleep` and `clock` are injected so a small case drives them.
- `pass_marker.py`: `write_pass_marker(root, step, head, tree="tree")` writes a check-earlier pass marker.
- `process_fake_detection.py`: `installs_a_subprocess_fake(source)`, which test source installs its own fake on `subprocess`; behind `unit/test_local_process_fakes.py`.
- `process_fakes.py`: the `fake_processes` implementation (`installer`, `FakePopen`, `FakeProcesses`); its module docstring is the interface of the fake.
- `repo_builder.py`: `new_repo(path, branch="main")` and `commit_all(repo, message, **files)`, throwaway real git repositories; the case carries `process("git ...")`. `new_repo` runs `git init` once per branch per worker and copies that template after (#3931): never `git init` in a case.
- `shim_audit.py`: `shim_problems`, `entry_bypass_problems`, `shim_source_problems` over `skills/tdd/scripts`; behind `test_shims.py`.
- `skill_sections.py`: `section(skill, heading)`, `heading_window`, `plain`, `has` ... read a heading's slice of SKILL.md-like prose with markup stripped.
- `stub_script.py`: `write_stub(path, body)` writes `#!/bin/sh\n` then `body`, sets mode 0755 and returns `path`: the one writer of a stub script a case puts in place of a real executable.
- `subsection_readers.py`: `Subsection` and `readers(...)`, which test cases still read one SKILL.md subsection by content; `stray_cases` (readers off the allow-list) and `lost_cases` (allow-list entries no longer reading); the engine of the readers audits.
- `tree_index.py`: `TestFile`, `VeriModules(directory)` (every `*.py` of one directory by stem: `names`, `path`, `text`, `tree`), `tests_py_index_of(root)`, `mentioned_names`.

## conftest fixtures

- `tests_py_index`: session; every `test_*.py` under `tests/py` as a `TestFile`, read and parsed once. An audit that sweeps test files reads this, never `rglob` (`unit/test_tree_index_guard.py`).
- `veri_modules_index`: session; `VeriModules` over `veri/`, the same rule for audits of the production package.
- `repo_templates_under_basetemp`: session, autouse; points `repo_builder.TEMPLATE_ROOT` at the worker's `--basetemp`, where `new_repo` keeps the template it copies.
- `process_case_shim_has_a_floor_interpreter`: autouse; a `process` case that launches a `.sh` shim fails unless a python3 at the 3.12 floor is reachable.
- `hermetic_environment`: autouse; clears ambient `VERI_*`, `CLAUDE_*`, `GH_*`, `GIT_*` and locale, sets `LC_ALL=C`, `VERI_HOME`, `VERI_VENV` and a per-case `TMPDIR`, and refuses a test that writes to the inherited `TMPDIR`.
- `run_cli`: `run_cli(module, argv, stdin="", env=None, cwd=None) -> (code, stdout, stderr)`; drives a ported module's `main` in-process.
- `frozen_heap`: freezes the garbage collector's heap for the case (`gc.freeze()`), so a pytest session it starts in-process does not walk everything the run has loaded in the five full collections pytest ends a session with.
- `fake_processes`: `fake_processes.answers({prefix: answer})`; fakes every way `subprocess` starts a process (see `process_fakes.py`).
- `fed_history`: `fed_history((name, subject, {path: text}), ..., root=tmp_path, branch="main")`; feeds case_history from those revisions, oldest first, HEAD the last, the work tree being the real `root` (see `fed_history.py`).
- `fed_commits`: `repo = fed_commits(root=tmp_path, branch="main")`; a git index and commit log over the work tree (`repo.add(*paths)`, `repo.commit(subject, all=False)` naming revisions c1, c2, ..., `repo.mv(source, target)`, `repo.head`), each commit fed to case_history through `fed_history`, and the check-earlier pass marker's git calls answered by `fake_processes` (work-tree hash `fed-tree`, HEAD `repo.head`).
- `events`: `events.records(directory)` reads `.tdd/events.jsonl` without `ts` and `awake`; `events.unappendable`, `events.refuse_event_sh()`.
- `listing`: `listing(answers)` puts a stub `gh` on PATH that answers the open-issue and PR listings (`conftest.serve_through_gh`).

Also importable from conftest as plain names (not fixtures): `SCRIPTS`, `ROOT`, `INTERPRETER_VENV`, `script(path, body)`,
`fixture_root(root)`, `live_conductor(monkeypatch, run_tdd, issue)`, `serve_listing`, `issues_listing`, `listed`,
`started_for_real`, `supervised` / `run_supervised`, `REAL_RUN`, `REAL_POPEN`, and the `case_size_guards` names.

## How do I fake ...

| ... | Use |
|---|---|
| a process (git, gh, any command) | `fake_processes.answers({"git rev-parse": (0, "sha\n", "")})`; see `process_fakes.py`. Never `monkeypatch.setattr(subprocess, ...)`: `unit/test_local_process_fakes.py` lists the few files still allowed one and only shrinks |
| a real git repository | `repo_builder.new_repo` / `commit_all` in a `process("git ...")` case; a bare repo, a remote or a worktree stays in the test file |
| the clock, a sleep, a poll | inject `sleep` and `clock` as `leaf_waits` does; shrink the supervisor's windows with `VERI_HEARTBEAT`, `VERI_TOOL_IDLE`, `VERI_TIMEOUT`, `VERI_STUCK_RETRIES`; a real wait in a small case is refused |
| a `claude` leaf | `CLAUDE_BIN` pointing at a stub script written with `conftest.script` |
| dispatch's world | `dispatch_world.FakeWorld(tick, ...)` handed to `dispatch.step` / `dispatch.main` |
| GitHub answers | in-process: `fake_processes.answers({"gh ": ...})`, or the production `github` module's intent functions faked at the module; with a real shim: the `listing` fixture, or `conftest.serve_listing` (`VERI_GH_JSON`) |
| the event journal | the `events` fixture; `events.refuse_event_sh()` for a journal that cannot be written |
| a live conductor, a pid file | `conftest.live_conductor(monkeypatch, run_tdd, issue)` |
| the environment | `monkeypatch.setenv`, or `run_cli(..., env={...})`; `hermetic_environment` already cleared the ambient `VERI_*` |
| a check-earlier pass marker | `pass_marker.write_pass_marker` |
| SKILL.md prose | read through `skill_sections`; a case reading one subsection by content is counted by `subsection_readers` |

## Audits that check a new test file

Run with `make test TESTS="skills/tdd/scripts/tests/py/<file> ..."`.

| Audit | Enforces |
|---|---|
| `test_fast_tier_guard.py` (with `fast_tier_guard.py`) | placement: a file the guard names stays out of `unit/`, a clean one lives in it |
| `unit/test_process_mark.py`, `unit/test_conftest_guards.py`, `case_size_guards` | marks carry their argument; an unmarked case starts no process, lists no repo directory, reads no process listing; exemption tables carry reasons |
| `unit/test_local_process_fakes.py` | no new file installs its own fake on `subprocess` |
| `unit/test_local_git_helpers.py` | no new test file defines a module-level `git`/`_git`; new cases use `repo_builder.git` |
| `unit/test_git_callers.py` | no new `veri/` module starts git other than through `veri/git.py`; `MODULES_RUNNING_GIT_DIRECTLY` only shrinks |
| `unit/test_local_stub_scripts.py` | no new file holds a `#!/bin/sh` string literal: a stub is written with `stub_script.write_stub` |
| `unit/test_tree_index_guard.py` | a `tree_audit` case reads test files and `veri/` through `tests_py_index` / `veri_modules_index`, never `rglob` or its own `ast.walk` |
| `unit/test_module_importers.py` | every helper module here has an importer besides its own suite |
| `unit/test_tests_py_readme.py` | every helper module and conftest fixture has a bullet above, and no bullet names a missing one |
| `unit/test_shims.py` | shell shims are the canonical `exec python3` form (for a new script, see "Adding a script" in the production README) |

## The pytest leg

`skills/tdd/scripts/tests/leg/pytest_leg.py` launches every `make unit` and `make test`. What a test author needs (case
sizes, timeouts, the admission bar) is in the root `CLAUDE.md`'s "Testing idiom"; what follows is the leg's own machinery.
Its two passes, and why `make test` on veri is one session, are in *Tiers and marks* above.

**Two passes.** When both passes run, the leg's output ends with one line totalling them,
`<named> named, <run> run, <passed> passed, <failed> failed across both passes`, not the second pass's `N deselected` line.
A `--subset` run handed a `-m` exits 1, printing `<n> unselected: named cases that neither pass ran (<targets>)`, when a named
target (file, directory or node id) holds cases its `-k` keeps of which neither pass ran one; a case its own `-m` or `-k`
deselects from a target that did run never counts (#3554). The serial pass is handed only the test files that hold a `serial`
case, as pass 1 recorded them (rootdir and ini file kept, so case ids read the same), and the totals line and every refusal
read as if it had collected everything; a target naming a case (`::`), or no record, leaves it collecting the whole selection.

**The idle window.** A per-case timeout cannot fire once no case runs, so a leg in which no case starts or reports for
`VERI_PYTEST_IDLE` seconds (default 1200, above the longest timeout mark, 900) ends itself (#4254): it writes its own threads'
stacks and, through SIGUSR1, each worker's to stderr, ends its workers (TERM, then KILL by pid after `VERI_PYTEST_TERM_GRACE`
seconds, default 5), prints one stderr line naming the idle time and the last case it saw, and exits 2; a leg sent TERM or
HUP ends its workers the same way and exits 128 + the signal's number without waiting on xdist's worker teardown. Either way it removes its `~/.veri-pytest-legs`
entry and releases the full-run lock first. A case may run silently for as long as its timeout, so a `VERI_PYTEST_TIMEOUT`
(or a timeout mark) above `VERI_PYTEST_IDLE` lets the idle window end a leg whose slow case is still running; keep the window
above every timeout.

**The run directory.** Each leg runs its cases under one `veri-pytest-*` run directory and removes it, the case
directories under it included, when it ends. `VERI_PYTEST_KEEP_RUN_DIR=1` (default `0`; any other value cleans up) leaves
that directory in place, its bytecode mirror still removed. CI's `make test` step sets it (#4855): a runner is discarded
after the job, and removing thousands of case directories after the last case was 8-13 s of the job's wall time. A leg
started inside a case still cleans up, since `hermetic_environment` clears ambient `VERI_*`.

**The bytecode cache** (`PYTHONPYCACHEPREFIX`, at `VERI_PYCACHE`, default `${TMPDIR:-/tmp}/veri-pycache-<uid>`, which the
Makefile sets when unset) persists between runs. `make test` and `make unit` create it with mode `0700` and refuse, exit 2
before any suite, one that is not a directory owned by the current user and writable by neither group nor others, a symlink
included, or whose parent group or others can write without the sticky bit, naming the path and the fix: remove it, or set
`VERI_PYCACHE`. A manifest of source hashes keeps a changed module, a same-second mutation included, from being served a
stale `.pyc`: before importing, the leg drops every `.pyc` the manifest does not vouch for by the hash of its source, and
`.opt-N` files always; a pytest-rewritten `.pyc` is vouched for like any other, recorded only when its header carries its
source's mtime and size and the source did not change after the run began (#1127, #2054). Sources a case creates under the
run's `veri-pytest-*` scratch directory leave their `.pyc` under that path mirrored in the prefix, so after a run the leg
removes the mirror of its own run directory, and the sweep of a dead run (pid no longer answering `kill 0`) removes that
run's mirror with its directory; a tree that does not resolve to exactly such a mirror inside the prefix, or whose run it
cannot prove dead, is left alone. A shim run has no manifest, so `shim-python.sh` clears the prefix and sets `PYTHONDONTWRITEBYTECODE=1`, and
`veri/pycache_prefix.py`, which a module's first line runs before any veri import, compiles veri's modules from source: the
run neither reads nor poisons a cache (#2406, #2439), while the standard library keeps its own `.pyc` files, since a prefix
would recompile them on every start. A veri module run directly as `python3 <module>` with bytecode writing on takes the
shared prefix from the same file, but only when it is a directory, not a symlink, owned by the current user and writable by
neither group nor others, in a parent group and others cannot write unless it has the sticky bit (as `/tmp` does), created
with mode `0700` when absent; otherwise it sets no prefix, compiles veri's modules from source and says why on stderr
(#3965). A `PYTHONPYCACHEPREFIX` the caller exported is honoured by the interpreter for the standard library before that
check can run, so the check covers veri's own modules and `make`'s guard covers a `make` run.

**The workers budget, T.** Every `make` leg on the machine, whoever ran it (a conductor's leaf, a lane, a review, a hand
`make`), counts its xdist workers against one budget, T: the ceiling `make ceiling` records on line 1 of
`~/.veri-test-ceiling` (`VERI_TEST_CEILING_FILE`) when that is a whole number of at least 2; with no such record (CI, a new
machine, a malformed or unreadable file) the physical cores on macOS, the CPU-affinity count elsewhere, never below 2, and
the leg says so in one stderr line naming the file and `make ceiling` (PRD 036.4).

- **The cap.** When a cap is set, T is min(that value, the cap on line 1 of `~/.veri-test-cap` (`VERI_TEST_CAP_FILE`)), a
  file the human writes and nothing in veri changes; one the leg cannot use (unreadable, or line 1 not a whole number of at
  least 2) is one stderr line and no cap, and a wait against the cap names the cap file (PRD 036.11).
- **A load timeout**, cases of two test files timing out within `VERI_LOAD_WINDOW` seconds (default 600) across the
  machine's legs, as each leg that claimed its workers appends them to `~/.veri-test-timeouts` (`VERI_TEST_TIMEOUTS_FILE`),
  lowers T by 2, never below 2, at most once per window, through `~/.veri-test-load` (`VERI_TEST_LOAD_FILE`): while it holds
  a whole number of at least 2, every leg's T is the lesser of that and its T without it, and nothing in veri raises it back
  but `make ceiling`'s exit 0, which removes the file, or the human removing it (PRD 036.7).
- **The lanes' needs.** While any lane's budget entry is unexpired, T is min(the ceiling or core fallback, lowered by the
  cap and a load timeout, the sum of the live lanes' needs), never below 2, each need max(N, live conductors) ×
  `VERI_CONDUCTOR_TEST_WORKERS` (default 2), written by `dispatch.sh` at each poll and by `role-state.sh dev set n`, and kept
  under `~/.veri-test-budget` (`VERI_TEST_BUDGET_DIR`) for `VERI_TEST_BUDGET_TTL` seconds (default 3600) after the last
  write; an expired, malformed or unreadable entry adds nothing, and a wait below the ceiling names each lane and its need
  (PRD 036.5). An `auto` lane's need (`n=auto`, PRD 036.6) is C, the capacity before this narrowing, so it never narrows T.
- A narrower T never ends or shrinks a running leg: it binds the next leg to start.

**The core wait.** Cases run across pytest-xdist workers out of T: `make unit` and a `make test TESTS=…` subset min(4, the
workers of T other running legs leave free) (each worker pays its own start-up; `make unit` hands the leg `--cap=4`, a
subset's `--subset` caps it at 4), a full `make test` every free worker (#2100), and a leg of any kind that finds fewer than
2 free waits instead of starting (PRD 036.1, 036.3, 036.4): it says so once on stderr, naming T and its source (the ceiling
record, the core fallback, or the cap file beside them), the workers in use and the pids holding them, writes the same wait
marker a full-run lock waiter writes (below), so a supervised leaf's hard timeout and silence window are frozen while it
waits (a marker it cannot write is one stderr line and the wait goes on unmarked; one already gone when the wait ends is no
error; TERM or HUP mid-wait removes it), and records the wait as a `core-wait` event with its seconds; a full run takes the
lock before it waits for cores.

**Leg registration.** Each leg registers its pid, count and start time under `~/.veri-pytest-legs` (`VERI_PYTEST_LEGS`), and
an entry holds a share only while its pid runs under that start time: a dead or reused pid, an entry with no start time (an
older leg's), a malformed one and one whose start time ps cannot read hold none, and only one whose pid is gone or proven
reused is removed. An entry carries line 3 `leaf` when the leg was claimed with `PYTEST_LEG_LOCK_WAIT_MARKER` set, a
supervised leaf's leg; W_other, the workers of the live entries without it, includes every 2-line entry (an older leg's
too, which errs low on an `auto` lane's N, the safe side), and is what `dispatch.sh` subtracts from T under `auto`.
`VERI_PYTEST_WORKERS=<n>` exported by the caller overrides both, used as given, never waiting,
registering or reading the record or the cap; `1` runs serially (#2053). A waiting leg also registers its wait, until it
starts, under `~/.veri-pytest-legs.waiting` (`VERI_PYTEST_WAITERS`): its pid's start time and the workers it waits for,
holding no share of T, read by the same start-time rule, and removed when it registers, exits or is ended by TERM or HUP.
`dispatch.sh` counts those entries at every poll and turns a queue growing across `VERI_QUEUE_POLLS` polls (default 3) into
one `queueing` notice (PRD 036.9).

**Refusals and escaping errors.** Three refusals, exit 2 before any suite: pytest or pytest_timeout not importable (stderr
names `make install-dev`), or Python older than the 3.12 floor. Any other error escaping the leg (registering it, taking the
full-run lock, checking or recording the bytecode cache) is one stderr line naming it, never a traceback, and exit 2, except
that a failing run keeps its exit 1.

**The full-run lock.** At most one full `make test` runs per machine (#2195): a second waits, naming the holder's pid and
working tree on stderr, before its suites start, so the wait counts toward no per-case timeout. The lock is an `flock` held
for the whole run, so a dead holder's lock is taken over; a run nested under the holder (`PYTEST_LEG_FULL_LOCK_HOLDER`) skips
it, and neither `make unit` nor a `make test TESTS=…` subset (`--subset`) ever waits on it. Release empties the lock file, so
it names a pid only while held. By that rule a live holder that never releases blocks the waiter without bound: the wait
counts toward no timeout that could bail it, a supervised leaf's hard timeout and silence window included (#2380). A waiting
leg marks its wait with a file naming its pid and start time; a supervisor ignores a marker whose waiter is no longer alive
under that start time, so its hard timeout and silence window run, while an empty marker (an older leg's) still freezes them
(#3989). `VERI_TEST_LOCK=0` turns the lock off. A verifier's full run takes the lock like any other, and a verifier that
breaks the lock code still cannot hang on it.
