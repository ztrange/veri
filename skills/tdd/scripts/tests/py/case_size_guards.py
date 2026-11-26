"""The admission guards of tests/py: the case-size rules every case runs under, the exemption tables they read
and the hook that refuses a mark it does not know.

conftest.py imports every name below, so a name keeps working as `conftest.<name>` and as `from conftest import <name>`,
and each autouse fixture stays registered through conftest.py (its place in the autouse order is unchanged)."""
import builtins
import io
import os
import pathlib
import shlex
import shutil
import signal
import subprocess
import sys
import tempfile

import pytest

from stub_script import write_stub

# Computed here as conftest.py computes them: this module cannot import conftest, which imports it.
SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
ROOT = SCRIPTS.parents[2]
# conftest.py holds hermetic_environment's guard wrappers; a frame in either file belongs to a guard, not to the caller.
GUARD_FILES = {__file__, os.path.join(os.path.dirname(__file__), "conftest.py")}


def register_markers(config):
    config.addinivalue_line("markers", "process(boundary): a medium case, naming the process boundary it observes")
    config.addinivalue_line("markers", "tree_audit(sweeps): a case that lists the repository's own directories, run by make test and not make unit")
    config.addinivalue_line("markers", "serial(reason): a case that must not run beside a full parallel load, naming why")


def pytest_collection_modifyitems(config, items):
    registered = {line.split(":")[0].split("(")[0].strip() for line in config.getini("markers")}
    unregistered = ["%s (%s)" % (item.nodeid, mark.name) for item in items
                    for mark in item.iter_markers() if mark.name not in registered]
    if unregistered:
        raise pytest.UsageError("unregistered mark: %s" % ", ".join(unregistered))
    for name, missing in (("process", "a boundary"), ("tree_audit", "a sweep"), ("serial", "a reason")):
        unnamed = [item.nodeid for item in items
                   if any(not mark.args or not str(mark.args[0]).strip() for mark in item.iter_markers(name))]
        if unnamed:
            raise pytest.UsageError("%s mark without %s: %s" % (name, missing, ", ".join(unnamed)))
    modules = {item.nodeid.split("/")[-1].split("::")[0]: item.module for item in items if isinstance(item, pytest.Function)}
    cases = set(modules) | {"%s::%s" % (name, attr) for name, module in modules.items() for attr in dir(module)}
    for label, table in (("permission-bits", PERMISSION_BITS_EXEMPT), ("system-location", SYSTEM_LOCATION_EXEMPT)):
        problems = exemption_problems(table, cases)
        if problems:
            raise pytest.UsageError("%s exemption table: %s" % (label, "; ".join(problems)))
    for label, table in (("starts-pytest", STARTS_PYTEST_EXEMPT), ("starts-git", STARTS_GIT_IN_REPOSITORY_EXEMPT),
                         ("below-floor", BELOW_FLOOR_INTERPRETER_EXEMPT)):
        problems = reasonless_problems(table)
        if problems:
            raise pytest.UsageError("%s exemption table: %s" % (label, "; ".join(problems)))
    default = max(PROCESS_CASE_TIMEOUT, config.getoption("timeout", None) or 0)
    for item in items:
        longer = item.get_closest_marker("process") is not None or item.get_closest_marker("tree_audit") is not None
        if longer and item.get_closest_marker("timeout") is None:
            item.add_marker(pytest.mark.timeout(default))


# A process case starts real processes, so machine load stretches it past the 30 s a small case gets (#2724, #2679).
PROCESS_CASE_TIMEOUT = 90


# supervise.sh checks a stub leaf's result once per VERI_POLL (default 1 s) and a stub finishes in ~0.1 s, so each
# supervised leaf in a case would otherwise sleep a second. A case that sets VERI_POLL keeps its own value.
SUPERVISOR_POLL = "0.1"


@pytest.fixture(autouse=True)
def process_case_supervisor_polls_sub_second(request, monkeypatch):
    """A process case that builds its child's env from scratch gets VERI_POLL too; an inherited env has it already."""
    if request.node.get_closest_marker("process") is None:
        return
    real = subprocess.Popen.__init__

    def polling(self, args, *rest, **kwargs):
        env = kwargs.get("env")
        # A case that deleted or changed the suite's VERI_POLL opted out: nothing is injected for it.
        if env is not None and "VERI_POLL" not in env and os.environ.get("VERI_POLL") == SUPERVISOR_POLL:
            kwargs["env"] = {**env, "VERI_POLL": SUPERVISOR_POLL}
        return real(self, args, *rest, **kwargs)

    monkeypatch.setattr(subprocess.Popen, "__init__", polling)


def fail_unbacked_push(request):
    pytest.fail("%s reached the push backoff without setting VERI_PUSH_BACKOFF" % request.node.nodeid, pytrace=False)


@pytest.fixture(autouse=True)
def case_waits_no_default_push_backoff(request, monkeypatch):
    import importlib

    module = importlib.import_module("push_branch")

    def guarded(args, *rest, _run=module.run, **kwargs):
        if args[0] == "sleep" and "VERI_PUSH_BACKOFF" not in os.environ:
            fail_unbacked_push(request)
        return _run(args, *rest, **kwargs)

    monkeypatch.setattr(module, "run", guarded)


# The real sleep and the log are written into the shim, not read from its environment: a process that passes on only
# an allow-list of names (run_leaf's leaf environment) drops REAL_SLEEP, and the shim's `exec ""` then made every
# `sleep` a leaf ran exit 126/127 within milliseconds (#4243).
SLEEP_SHIM_BODY = """second() { echo "$2"; }
set -f
case "$(second $(ps -o command= -p "$PPID"))" in
  */veri/push_branch.py) [ -n "${VERI_PUSH_BACKOFF+x}" ] || { echo "$0" >> %(log)s; exit 1; } ;;
esac
exec %(sleep)s "$@"
"""


def write_sleep_shim(path, real_sleep, log):
    """Write the push-backoff `sleep` shim to `path`, with `real_sleep` and `log` in its text, and return `path`."""
    return write_stub(path, SLEEP_SHIM_BODY % {"sleep": shlex.quote(str(real_sleep)), "log": shlex.quote(str(log))})


@pytest.fixture(autouse=True)
def process_case_waits_no_default_push_backoff(request, monkeypatch, tmp_path_factory):
    if request.node.get_closest_marker("process") is None:
        yield
        return
    shim_dir = tmp_path_factory.mktemp("push-backoff-guard")
    log = shim_dir / "reached"
    write_sleep_shim(shim_dir / "sleep", shutil.which("sleep"), log)
    monkeypatch.setenv("PUSH_BACKOFF_LOG", str(log))
    monkeypatch.setenv("PATH", str(shim_dir) + os.pathsep + os.environ.get("PATH", ""))
    yield
    if log.exists():
        fail_unbacked_push(request)


@pytest.fixture(autouse=True)
def process_case_children_do_not_inherit_ignored_signals(request):
    if request.node.get_closest_marker("process") is None:
        yield
        return
    ignored = []
    for number, handler in ((signal.SIGINT, signal.default_int_handler), (signal.SIGTERM, signal.SIG_DFL),
                            (signal.SIGHUP, signal.SIG_DFL)):
        if signal.getsignal(number) == signal.SIG_IGN:
            ignored.append(number)
            signal.signal(number, handler)
    yield
    for number in ignored:
        signal.signal(number, signal.SIG_IGN)


def at_or_under_root(path):
    return path == ROOT or ROOT in path.parents


def in_repository_outside(resolved, scratch):
    return at_or_under_root(resolved) and scratch != resolved and scratch not in resolved.parents


@pytest.fixture(autouse=True)
def unmarked_case_lists_no_repository_directory(request, monkeypatch, tmp_path):
    if request.node.get_closest_marker("tree_audit") is not None:
        for name in ("scandir", "listdir"):
            monkeypatch.setattr(os, name, getattr(getattr(os, name), "real", getattr(os, name)))
        return
    scratch = tmp_path.resolve()

    def checked(real):
        def lister(path="."):
            check(path)
            return real(path)

        lister.real = real
        return lister

    def check(path):
        try:
            listed = pathlib.Path(os.fsdecode(os.path.abspath(path))).resolve()
        except TypeError:
            return
        if in_repository_outside(listed, scratch) and listed.is_dir():
            raise AssertionError("%s lists the repository directory %s: mark it tree_audit" % (request.node.nodeid, listed))

    for name in ("scandir", "listdir"):
        monkeypatch.setattr(os, name, checked(getattr(os, name)))


@pytest.fixture(autouse=True)
def unmarked_case_reads_no_real_process_listing(request, monkeypatch):
    if request.node.get_closest_marker("process") is not None:
        return
    import importlib

    module = importlib.import_module("pid_file")
    real, run = module.conductors, module.subprocess.run

    def checked():
        if module.subprocess.run is run:
            raise AssertionError("%s reads the real process listing: fake pid_file.conductors or mark it process" % request.node.nodeid)
        return real()

    monkeypatch.setattr(module, "conductors", checked)


STARTS_PYTEST_EXEMPT = {
    "test_conftest.py::test_a_case_reading_a_cwd_relative_path_gives_the_same_outcome_started_from_the_repository_root_as_from_skills_tdd_scripts":
        "the pytest session started from two directories is the subject",
    "test_conftest.py::test_the_path_setup_case_gives_the_same_outcome_started_from_skills_tdd_scripts_with_a_relative_path_as_from_the_repository_root":
        "the pytest session started from two directories is the subject",
    "test_stale_bytecode_process.py::test_every_directly_runnable_module_keeps_its_bytecode_out_of_the_tree_2405":
        "pytest_leg.py run directly is one of the modules whose bytecode placement is the subject",
}


def case_tail(request):
    path, _, case = request.node.nodeid.partition("::")
    return path.split("/")[-1] + "::" + case


def exempt_from(tail, table):
    return tail in table or tail.split("::")[0] in table


RUNS_GIT_WITH_NO_CWD = "the module under test runs git with no cwd while the process works in the repository; the case fakes the process or reads only the recorded call"

STARTS_GIT_IN_REPOSITORY_EXEMPT = {
    "test_supervise_process.py": "supervise.py records the skill clone's own HEAD; the case only lets it run rev-parse HEAD there",
    "test_run_conductor_process.py": "run_conductor.py runs git -C <skill clone> and the cases fake every process, so the path only reaches the recorded call",
    "test_run_conductor_snapshot.py": "run_conductor.py runs git -C <skill clone> and the cases fake every process, so the path only reaches the recorded call",
    "test_rebase_onto_default_process.py::test_main_run_through_a_symlink_from_another_directory_rebases_the_callers_clone_and_never_the_skills_repository":
        "the skills repository's own HEAD is read to prove it was never rebased",
    "test_no_tracked_artifacts.py::test_no_file_under_a_nested_tdd_directory_is_tracked_598":
        "the repository's own tracked files are the subject",
    "test_no_tracked_artifacts.py::test_git_ignores_the_event_log_a_suite_run_writes_under_a_nested_tdd_directory_598":
        "the repository's own ignore rules are the subject",
    "test_prd_016_tracked_names_process.py::test_no_tracked_file_outside_specs_and_tdd_contains_veri_dash_a_renamed_skill_name":
        "the repository's own tracked files are the subject",
    "test_skill_identity_process.py::test_no_tracked_file_outside_the_two_stubs_still_names_the_old_scripts_dir":
        "the repository's own tracked files are the subject",
    "test_skill_identity_process.py::test_no_tracked_file_outside_the_two_stubs_names_either_old_command":
        "the repository's own tracked files are the subject",
    "test_refactor_budget_process.py::test_no_tracked_file_outside_the_docs_and_tdd_trees_states_3_as_the_veri_issue_refactor_budget_default":
        "the repository's own tracked files are the subject",
    "test_one_operator_role_process.py::test_no_tracked_file_outside_specs_adr_tdd_and_skills_tdd_names_vcoord_or_a_coordinator_4102":
        "the repository's own tracked files are the subject",
    "test_one_role_process.py::test_no_tracked_file_under_skills_tdd_outside_its_tests_names_the_retired_coord_role_4103":
        "the repository's own tracked files are the subject",
}


@pytest.fixture(autouse=True)
def case_starts_no_test_runner(request, monkeypatch):
    real = subprocess.Popen.__init__

    def is_pytest(words):
        names = [os.path.basename(os.fsdecode(w)) for w in words]
        if names[0] in ("pytest", "py.test", "pytest_leg.py"):
            return True
        if not names[0].startswith("python"):
            return False
        return names[1:2] == ["pytest_leg.py"] or any(a == "-m" and b == "pytest" for a, b in zip(names, names[1:], strict=False))

    def from_exempt_helper():
        frame = sys._getframe()
        while frame is not None:
            if frame.f_code.co_name == "child_pytest" and os.path.basename(frame.f_code.co_filename) == "test_conftest.py":
                return True
            frame = frame.f_back
        return False

    def is_suite(arg):
        parts = pathlib.PurePath(os.fsdecode(arg)).parts
        return bool(parts) and parts[-1].endswith(".test.sh") and "tests" in parts[:-1]

    def git_directory(words, cwd):
        if os.path.basename(os.fsdecode(words[0])) != "git":
            return None
        directory = os.fsdecode(cwd) if cwd is not None else None
        rest = [os.fsdecode(w) for w in words[1:]]
        if rest == ["--version"]:
            return None
        if directory is None:
            directory = os.getcwd()
        for flag, value in zip(rest, rest[1:], strict=False):
            if flag == "-C":
                directory = os.path.join(directory, value) if directory else value
        return directory

    def in_repository(directory):
        scratch = request.getfixturevalue("tmp_path").resolve()
        resolved = pathlib.Path(os.path.abspath(directory)).resolve()
        return in_repository_outside(resolved, scratch)

    def refuse_git_in_repository(args, kwargs):
        words = [args] if isinstance(args, (str, bytes, os.PathLike)) else list(args)
        if isinstance(args, str) and kwargs.get("shell"):
            words = shlex.split(args)
        command = " ".join(os.fsdecode(w) for w in words)
        directory = git_directory(words, kwargs.get("cwd")) if words else None
        tail = case_tail(request)
        if directory is not None and not exempt_from(tail, STARTS_GIT_IN_REPOSITORY_EXEMPT) and in_repository(directory):
            raise AssertionError("%s starts git against the repository the tests live in: %s (%s)" % (request.node.nodeid, directory, command))
        return words, command, tail

    def checked(self, args, *rest, **kwargs):
        words, command, tail = refuse_git_in_repository(args, kwargs)
        if words and (is_suite(words[0]) or (os.path.basename(os.fsdecode(words[0])) in ("bash", "sh") and any(is_suite(w) for w in words[1:]))):
            raise AssertionError("%s starts a bash suite: %s" % (request.node.nodeid, command))
        if words and is_pytest(words) and not from_exempt_helper() and tail not in STARTS_PYTEST_EXEMPT:
            raise AssertionError("%s starts pytest: %s" % (request.node.nodeid, command))
        return real(self, args, *rest, **kwargs)

    monkeypatch.setattr(subprocess.Popen, "__init__", checked)

    setattr_ = monkeypatch.setattr

    def refusing_git_in_repository(replacement):
        def run(args, *a, **kw):
            refuse_git_in_repository(args, kw)
            return replacement(args, *a, **kw)

        return run

    def guarded_setattr(target, name, *rest, **kwargs):
        if target == "subprocess.run" and callable(name):
            return setattr_(target, refusing_git_in_repository(name), *rest, **kwargs)
        value = rest[0] if rest else kwargs.get("value")
        if target is subprocess and name == "run" and callable(value):
            return setattr_(target, name, refusing_git_in_repository(value), *rest[1:], **{k: v for k, v in kwargs.items() if k != "value"})
        return setattr_(target, name, *rest, **kwargs)

    monkeypatch.setattr = guarded_setattr


BELOW_FLOOR_INTERPRETER_EXEMPT = {
    "test_bash_version_guard_process.py::test_on_a_real_python3_below_the_floor_first_on_path_usr_bin_python3_leaf_launchable_sh_refuses_with_exit_2_naming_the_floor_and_its_version":
        "the shim's refusal of a below-floor python3 on PATH is the subject",
    "test_shims_process.py::test_issue_2106_shim_with_both_python3s_below_the_floor_exits_2_without_its_module_naming_each_interpreter_its_source_and_version":
        "the shim's refusal of a below-floor venv and PATH python3 is the subject",
    "test_shims_process.py::test_issue_2106_shim_with_no_venv_python3_and_none_on_path_exits_2_naming_where_it_looked_for_each":
        "the shim's refusal when no python3 is found is the subject",
    "test_shims_process.py::test_issue_2106_shim_with_both_python3s_exiting_1_silently_exits_2_naming_each_interpreter_and_an_unknown_version":
        "the shim's refusal of interpreters reporting no version is the subject",
    "test_cloud_setup_process.py::test_its_shim_runs_its_module_on_a_python3_below_the_floor":
        "cloud-setup.sh running its module on a below-floor python3 is the subject",
}


PATHLIB_SOURCE = os.path.splitext(pathlib.__file__)[0].removesuffix("__init__")


GUARD_WRAPPERS = {"checked", "checked_mkdir", "checked_os_open", "guarded_open", "guarded_mkdir", "guarded_os_open"}


def caller_outside_pathlib():
    frame = sys._getframe(2)
    while frame.f_code.co_filename.startswith(PATHLIB_SOURCE) or (
            frame.f_code.co_filename in GUARD_FILES and frame.f_code.co_name in GUARD_WRAPPERS):
        frame = frame.f_back
    return frame


PERMISSION_BITS_EXEMPT = {}


def reasonless_problems(table):
    return ["%s: exemption carries no reason" % entry for entry, reason in table.items() if not reason] + [
        "%s: whole-file exemption with the runs-git-with-no-cwd reason" % entry
        for entry, reason in table.items() if "::" not in entry and reason == RUNS_GIT_WITH_NO_CWD]


def exemption_problems(table, cases):
    problems = reasonless_problems(table)
    for entry in table:
        if entry not in cases:
            problems.append("%s: exemption names no existing case" % entry)
    return problems


@pytest.fixture(autouse=True)
def case_forces_no_failure_through_permission_bits(request, monkeypatch):
    real = os.chmod
    tail = case_tail(request)

    def checked(path, mode, *rest, **kwargs):
        frame = caller_outside_pathlib()
        if mode & 0o600 != 0o600 and not exempt_from(tail, PERMISSION_BITS_EXEMPT):
            raise AssertionError("%s takes permission bits off %s with chmod at %s:%d: uid 0 ignores them"
                                 % (request.node.nodeid, path, frame.f_code.co_filename, frame.f_lineno))
        return real(path, mode, *rest, **kwargs)

    monkeypatch.setattr(os, "chmod", checked)


SYSTEM_LOCATION_EXEMPT = {}


@pytest.fixture(autouse=True)
def case_expects_no_system_location_unreadable_or_unwritable(request, monkeypatch):
    real = io.open
    tail = case_tail(request)

    def system_location(path):
        resolved = os.path.abspath(path)
        for temp in ("/tmp", str(pathlib.PurePath(tempfile.gettempdir()))):
            if resolved == temp or resolved.startswith(temp.rstrip("/") + "/"):
                return False
        first, separator, _ = resolved.lstrip("/").partition("/")
        return bool(first) and (not separator or first in ("etc", "root", "proc"))

    def refuse_system_location(verb, path, frame):
        name = os.path.basename(frame.f_code.co_filename)
        if (isinstance(path, (str, bytes, os.PathLike)) and name.startswith(("test_", "conftest"))
                and system_location(os.fsdecode(path)) and not exempt_from(tail, SYSTEM_LOCATION_EXEMPT)):
            raise AssertionError("%s %s the system location %s at %s:%d: uid 0 ignores what makes it fail"
                                 % (request.node.nodeid, verb, os.fsdecode(path), frame.f_code.co_filename, frame.f_lineno))

    def checked(file, *rest, **kwargs):
        refuse_system_location("opens", file, caller_outside_pathlib())
        return real(file, *rest, **kwargs)

    real_mkdir = os.mkdir

    def checked_mkdir(path, *rest, **kwargs):
        refuse_system_location("creates", path, caller_outside_pathlib())
        return real_mkdir(path, *rest, **kwargs)

    real_os_open = os.open

    def checked_os_open(path, flags, *rest, **kwargs):
        if flags & os.O_CREAT:
            refuse_system_location("creates", path, caller_outside_pathlib())
        return real_os_open(path, flags, *rest, **kwargs)

    monkeypatch.setattr(io, "open", checked)
    monkeypatch.setattr(builtins, "open", checked)
    monkeypatch.setattr(os, "open", checked_os_open)
    monkeypatch.setattr(os, "mkdir", checked_mkdir)
