"""A ratchet: test files that install their own fake on `subprocess` only shrink in number; new cases use fake_processes.

What counts as a local process fake is what a file DOES to the subprocess module, never what it names its function:
a call `setattr(<subprocess>, "run" | "Popen" | "check_output" | "check_call" | "call" | "getoutput" |
"getstatusoutput", <fake>)` (any receiver: `monkeypatch`, a `monkeypatch.context()` scope), where <subprocess> is the module
(`subprocess`) or a module's own reference to it (`status.subprocess`, `a.b.subprocess`); the same with a dotted string target
(`setattr("subprocess.run", <fake>)`, `setattr("status.subprocess.run", <fake>)`, an f-string `f"subprocess.{name}"`);
a setattr of `subprocess` whose attribute name is not a literal (a loop over names); `mock.patch` and `patch.object` of the
same targets; and a plain assignment `subprocess.run = <fake>`.
A fake that only replaces a module's OWN function (`update_veri.git`, `plan_reverify.git`, `status.run_captured`)
starts no process and is not a process fake: those files are not listed, however their fake is named. A function named
`fake_run` that no subprocess install uses does not count either. Not detected (a documented blind spot): an alias of the
module (`sp = subprocess`) and a `from subprocess import run` name patched on the importer. `conftest.py` holds the
fake_processes fixture itself and is the one file exempt.
"""
import pytest
from process_fake_detection import installs_a_subprocess_fake

# The test files (paths under tests/py, sorted, ONE per line) that still install their own fake on subprocess. Migrate a
# file to conftest's fake_processes (see its docstring) and delete its line: a listed file that no longer installs one
# fails the second case below. Entries may be removed, NEVER added: a new case answers its processes with
# fake_processes.answers(...), which matches a command line, records the call and fails an unexpected one loudly. One
# line per file keeps parallel migrations from conflicting. The reason says what the fake does, from the migration
# inventory; "not inventoried" marks a file found only once the audit counted installs rather than names.
FILES_WITH_A_LOCAL_PROCESS_FAKE = {
    "test_detach_leaf.py": "not inventoried",
    "test_event.py": "not inventoried",
    "test_issue_worktree_process.py": "8 cases put a fake in front of a real git (routed = subprocess.run / real_run passthrough)",
    "test_parallel_conductors.py": "git faked, the rest runs real; fake_processes has no passthrough and refuses Popen",
    "test_run_conductor_process.py": "os and subprocess boundary, sleep recorded",
    "test_run_leaf_process.py": "not inventoried",
    "test_skill_edit_step_process.py": "not inventoried",
    "test_solvable_issues_process.py": "one case (in_flight_2390) puts a recording fake in front of the real subprocess.run that starts a fake claude",
    "test_status_process.py": "worktree list faked, the rest real",
    "test_supervise_process.py": "not inventoried",
    "unit/test_dispatch.py": "not inventoried",
    "unit/test_dispatch_issue_states.py": "not inventoried",
    "unit/test_event_journal.py": "not inventoried",
    "unit/test_report_cache.py": "3 cases answer gh and pass git through to a real process (real_run)",
}

EXEMPT = ("conftest.py",)


def _files_installing_a_local_process_fake(tests_py_index):
    found = []
    for entry in tests_py_index:
        relative = _relative(entry.path)
        if relative not in EXEMPT and installs_a_subprocess_fake(entry.text):
            found.append(relative)
    return sorted(found)


def _relative(path):
    parts = path.parts
    return "/".join(parts[parts.index("py") + 1:])


@pytest.mark.parametrize("source", [
    'monkeypatch.setattr(subprocess, "run", lambda *a, **k: None)',
    'monkeypatch.setattr(subprocess, "Popen", Spy)',
    'monkeypatch.setattr(status.subprocess, "run", fake)',
    'monkeypatch.setattr(a.b.subprocess, "check_output", fake)',
    'scope.setattr(module.subprocess, "call", fake)',
    'monkeypatch.setattr("subprocess.run", fake)',
    'monkeypatch.setattr("status.subprocess.run", fake)',
    'monkeypatch.setattr(f"subprocess.{name}", refuse)',
    'for name in names:\n    monkeypatch.setattr(subprocess, name, refuse)',
    'mock.patch("subprocess.run", fake)',
    'patch.object(subprocess, "run", fake)',
    'subprocess.run = fake',
    'def rename_me(): pass\nmonkeypatch.setattr(subprocess, "run", rename_me)',
])
def test_a_replacement_installed_on_subprocess_is_a_local_process_fake(source):
    assert installs_a_subprocess_fake(source)


@pytest.mark.parametrize("source", [
    'def fake_git(*args): return args\nmonkeypatch.setattr(update_veri, "git", fake_git)',
    'def fake_run(argv): return 0\nmonkeypatch.setattr(status, "run_captured", fake_run)',
    'monkeypatch.setattr(subprocess.Popen, "__init__", checked)',
    'monkeypatch.setattr(subprocess, "CompletedProcess", fake)',
    'monkeypatch.setattr("subprocess.PIPE", None)',
    'monkeypatch.setattr("update_veri.subprocess_note", fake)',
    'subprocess.run(["git", "status"])',
    'fake_processes.answers({"git": (0, "", "")})',
])
def test_a_fake_that_starts_no_subprocess_install_is_not_a_local_process_fake(source):
    assert not installs_a_subprocess_fake(source)


@pytest.mark.tree_audit("skills/tdd/scripts/tests/py")
def test_no_test_file_outside_the_list_installs_its_own_fake_on_subprocess(tests_py_index):
    unlisted = [path for path in _files_installing_a_local_process_fake(tests_py_index)
                if path not in FILES_WITH_A_LOCAL_PROCESS_FAKE]

    assert not unlisted, (
        f"{unlisted} install their own fake on subprocess: use fake_processes.answers instead. "
        f"FILES_WITH_A_LOCAL_PROCESS_FAKE only shrinks, never add to it")


@pytest.mark.tree_audit("skills/tdd/scripts/tests/py")
def test_a_listed_file_that_no_longer_installs_a_fake_on_subprocess_is_removed_from_the_list(tests_py_index):
    found = _files_installing_a_local_process_fake(tests_py_index)
    gone = [path for path in FILES_WITH_A_LOCAL_PROCESS_FAKE if path not in found]

    assert not gone, f"{gone} no longer install a fake on subprocess: remove them from FILES_WITH_A_LOCAL_PROCESS_FAKE"


def test_the_list_is_sorted():
    paths = list(FILES_WITH_A_LOCAL_PROCESS_FAKE)

    assert paths == sorted(paths)
