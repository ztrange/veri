# tests/py: the map of the test side

For an agent about to add or change a test. The production half has its own map, [`../../veri/README.md`](../../veri/README.md);
the policy (admission bar, timeouts, the pytest leg, the venv) lives in the "Testing idiom" section of the root
[`CLAUDE.md`](../../../../../CLAUDE.md) and is linked here, not restated. `unit/test_tests_py_readme.py` fails when a helper
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
- `make unit` runs `-m "not process and not tree_audit"` over `tests/py/unit/` only, on at most 4 of the free workers
  of T, the leg's budget (`--cap=4`, Makefile `unit:`; a `make test TESTS=…` subset is capped at 4 too); `make test` runs
  everything under `tests/py/` through `tests/leg/pytest_leg.py`: the non-`serial` cases, then a second pass over the `serial` ones
  only when one was collected; veri's tree holds none (`unit/test_no_serial_case.py`), so it is one pytest session.
- The leg and the plugins it loads by name (`network_guard`, `small_case_guard`, `private_tmp_path`, `serial_seen`) live in
  `skills/tdd/scripts/tests/leg/`, beside `tests/py/` and outside its rootdir, never in the product package `veri/` (#4051);
  the TMPDIR it pins is `veri/leg_tmpdir.py`'s `PINNED_TMPDIR`, which run-conductor's free-space check reads too.
  `make test TESTS="<file or node id> ..."` runs only those, in the same invocation. Policy: root `CLAUDE.md`, "Testing idiom".
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
- `leave_receipt`: `leave_receipt(ledger, repo=None)` writes a pin-recheck-ok receipt beside a ledger and, in-process, fakes `git()` to answer its sha.

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
| a pin-recheck receipt | `leave_receipt`; a check-earlier marker: `pass_marker.write_pass_marker` |
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
