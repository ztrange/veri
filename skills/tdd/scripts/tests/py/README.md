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
- `make unit` runs `-m "not process and not tree_audit"` over `tests/py/unit/` only (Makefile `unit:`); `make test` runs
  everything under `tests/py/` through `veri/pytest_leg.py`, in two passes: the non-`serial` cases, then the `serial` ones.
  `make test TESTS="<file or node id> ..."` runs only those, in the same invocation. Policy: root `CLAUDE.md`, "Testing idiom".
- **A file lives in `unit/` only if `veri/fast_tier_guard.py` names none of its calls** (a process start, a real wait),
  enforced both ways by `test_fast_tier_guard.py`. So `make unit` runs `tests/py/unit/` only, and placement is judged per FILE:
  one case that calls `subprocess` (or sleeps) keeps every small case beside it out of `make unit`, and they run only in
  `make test` and as affected suites. The cost, measured 2026-11-15 with `-m "not process and not tree_audit"` over
  `tests/py/` outside `unit/`: 1,364 small cases in 51 files do not run in `make unit` (46 non-`_process` files hold 1,352
  of them, e.g. `test_metrics.py`, `test_run_conductor.py`, `test_supervise.py`), against 4,496 that do. This is the current
  rule, not a verdict: the owner's standing target is a fast `make unit`, and growing the tier (moving a file's lone process
  case to a `<name>_process.py` sibling, then `git mv` the file into `unit/`) is his decision. Do not move a file on your own.
- A `unit/` file may still hold marked cases (they are deselected by `make unit`): the guard sees calls, not marks.
- A new test file that starts no process and lists no repo directory goes in `unit/`; otherwise beside this file, a
  process-starting suite as `test_<name>_process.py` (the established route, 105 such files).

## Helper modules

Directly under `tests/py/`, beside `conftest.py`; import them flat (`from repo_builder import new_repo`).

- `case_size_guards.py`: the admission guards (autouse fixtures that fail a small case which starts git or a test runner, lists a repo directory, forces a failure through permission bits ...), their exemption tables, `register_markers` and the collection hook; conftest imports every name, so `conftest.<name>` works.
- `dispatch_world.py`: `FakeWorld(*ticks, role_state=(), unreadable=False)`, a scripted in-memory adapter for `dispatch.World`; the keys a tick may carry are in its docstring.
- `leaf_waits.py`: `leaf_started(read_pid, sleep, clock)` and `leaf_left(pid, alive, sleep, clock)`, waits on a real leaf bounded far above load delay; `sleep` and `clock` are injected so a small case drives them.
- `pass_marker.py`: `write_pass_marker(root, step, head, tree="tree")` writes a check-earlier pass marker.
- `process_fake_detection.py`: `installs_a_subprocess_fake(source)`, which test source installs its own fake on `subprocess`; behind `unit/test_local_process_fakes.py`.
- `process_fakes.py`: the `fake_processes` implementation (`installer`, `FakePopen`, `FakeProcesses`); its module docstring is the interface of the fake.
- `repo_builder.py`: `new_repo(path, branch="main")` and `commit_all(repo, message, **files)`, throwaway real git repositories; the case carries `process("git ...")`.
- `shim_audit.py`: `shim_problems`, `entry_bypass_problems`, `shim_source_problems` over `skills/tdd/scripts`; behind `test_shims.py`.
- `skill_sections.py`: `section(skill, heading)`, `heading_window`, `plain`, `has` ... read a heading's slice of SKILL.md-like prose with markup stripped.
- `subsection_readers.py`: `Subsection` and `readers(...)`, which test cases still read one SKILL.md subsection by content; the engine of the readers audits.
- `tree_index.py`: `TestFile`, `VeriModules(directory)` (every `*.py` of one directory by stem: `names`, `path`, `text`, `tree`), `tests_py_index_of(root)`, `mentioned_names`.

## conftest fixtures

- `tests_py_index`: session; every `test_*.py` under `tests/py` as a `TestFile`, read and parsed once. An audit that sweeps test files reads this, never `rglob` (`unit/test_tree_index_guard.py`).
- `veri_modules_index`: session; `VeriModules` over `veri/`, the same rule for audits of the production package.
- `process_case_shim_has_a_floor_interpreter`: autouse; a `process` case that launches a `.sh` shim fails unless a python3 at the 3.12 floor is reachable.
- `hermetic_environment`: autouse; clears ambient `VERI_*`, `CLAUDE_*`, `GH_*`, `GIT_*` and locale, sets `LC_ALL=C`, `VERI_HOME`, `VERI_VENV` and a per-case `TMPDIR`, and refuses a test that writes to the inherited `TMPDIR`.
- `run_cli`: `run_cli(module, argv, stdin="", env=None, cwd=None) -> (code, stdout, stderr)`; drives a ported module's `main` in-process.
- `fake_processes`: `fake_processes.answers({prefix: answer})`; fakes every way `subprocess` starts a process (see `process_fakes.py`).
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
| `test_fast_tier_guard.py` (with `veri/fast_tier_guard.py`) | placement: a file the guard names stays out of `unit/`, a clean one lives in it |
| `unit/test_process_mark.py`, `unit/test_conftest_guards.py`, `case_size_guards` | marks carry their argument; an unmarked case starts no process, lists no repo directory, reads no process listing; exemption tables carry reasons |
| `unit/test_local_process_fakes.py` | no new file installs its own fake on `subprocess` |
| `unit/test_tree_index_guard.py` | a `tree_audit` case reads test files and `veri/` through `tests_py_index` / `veri_modules_index`, never `rglob` or its own `ast.walk` |
| `unit/test_module_importers.py` | every helper module here has an importer besides its own suite |
| `unit/test_tests_py_readme.py` | every helper module and conftest fixture has a bullet above, and no bullet names a missing one |
| `unit/test_shims.py` | shell shims are the canonical `exec python3` form (for a new script, see "Adding a script" in the production README) |
