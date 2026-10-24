"""In-process cases for veri/detach_leaf.py, the module detach-leaf.sh is a shim over."""
import importlib
import subprocess

import pytest

USAGE = "usage: detach-leaf.sh <cmd> [args…]\n"


@pytest.fixture
def detach_leaf():
    return importlib.import_module("veri.detach_leaf")


def test_main_refuses_no_argument_with_the_usage_line_and_launches_its_argv_once_returning_0_silently(
        monkeypatch, capsys, detach_leaf):
    launches = []

    class FakePopen:
        pid = 4242

        def __init__(self, args, **kwargs):
            launches.append(args)

    monkeypatch.setattr(subprocess, "Popen", FakePopen)

    code = detach_leaf.main([])
    assert (code, capsys.readouterr(), launches) == (2, ("", USAGE), [])

    code = detach_leaf.main(["true"])
    assert (code, capsys.readouterr(), launches) == (0, ("", ""), [["true"]])


def test_main_launches_with_stdin_devnull_inherited_stdout_stderr_and_fds_in_a_new_session_never_waiting(
        monkeypatch, detach_leaf):
    import signal

    launches, calls = [], []

    class FakePopen:
        pid = 4242

        def __init__(self, args, **kwargs):
            launches.append((args, kwargs))

        def __getattr__(self, name):
            if name in ("wait", "communicate", "poll", "kill", "terminate"):
                calls.append(name)
                return lambda *a, **k: None
            raise AttributeError(name)

    monkeypatch.setattr(subprocess, "Popen", FakePopen)

    assert detach_leaf.main(["true"]) == 0
    [(args, kwargs)] = launches
    launch = {key: kwargs.get(key, "unset") for key in
              ("stdin", "stdout", "stderr", "close_fds", "start_new_session", "shell", "executable")}
    assert (args, launch) == (["true"], {
        "stdin": subprocess.DEVNULL, "stdout": None, "stderr": None, "close_fds": False,
        "start_new_session": True, "shell": "unset", "executable": "unset"})

    dispositions = []
    monkeypatch.setattr(signal, "signal", lambda signum, handler: dispositions.append((signum, handler)))
    kwargs["preexec_fn"]()
    assert dict(dispositions) == {
        signal.SIGPIPE: signal.SIG_DFL, signal.SIGINT: signal.SIG_IGN,
        signal.SIGQUIT: signal.SIG_IGN, signal.SIGXFSZ: signal.SIG_DFL}
    assert calls == []


def test_main_launches_an_empty_command_an_option_and_awkward_arguments_as_given_parsing_no_option(
        monkeypatch, capsys, detach_leaf):
    launches = []

    class FakePopen:
        pid = 4242

        def __init__(self, args, **kwargs):
            launches.append(args)

    monkeypatch.setattr(subprocess, "Popen", FakePopen)

    for argv in ([""], ["--help"], ["cmd", "--x", "a b", ""]):
        launches.clear()
        code = detach_leaf.main(list(argv))
        assert (argv, code, capsys.readouterr(), launches) == (argv, 0, ("", ""), [argv])


def test_main_returns_2_naming_the_command_and_strerror_on_stderr_when_the_launch_raises_an_oserror(
        monkeypatch, capsys, detach_leaf):
    import errno
    import os

    for argv, error in (
            (["no-such-command", "a"], FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), "no-such-command")),
            (["./not-executable"], PermissionError(errno.EACCES, os.strerror(errno.EACCES), "./not-executable")),
            (["/tmp"], PermissionError(errno.EACCES, os.strerror(errno.EACCES), "/tmp"))):

        def raising_popen(args, raised=error, **kwargs):
            raise raised

        monkeypatch.setattr(subprocess, "Popen", raising_popen)
        code = detach_leaf.main(list(argv))
        assert (argv, code, capsys.readouterr()) == (
            argv, 2, ("", f"detach-leaf.sh: {argv[0]}: {error.strerror}\n"))


def test_main_writes_and_raises_no_resource_warning_when_its_launch_outlives_it_and_the_launch_is_dropped(
        monkeypatch, capsys, detach_leaf):
    import gc
    import os
    import signal
    import warnings

    pids = []

    class RecordingPopen(subprocess.Popen):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            pids.append(self.pid)

    monkeypatch.setattr(subprocess, "Popen", RecordingPopen)

    try:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            code = detach_leaf.main(["sleep", "60"])
            gc.collect()
    finally:
        for pid in pids:
            os.kill(pid, signal.SIGKILL)
            os.waitpid(pid, 0)

    out, err = capsys.readouterr()
    assert (code, len(pids), out, [line for line in err.splitlines() if "ResourceWarning" in line],
            [str(w.message) for w in caught if issubclass(w.category, ResourceWarning)]) == (0, 1, "", [], [])


@pytest.mark.process("a detached bash writing past ulimit -f, observing its own status")
def test_main_launches_a_command_that_dies_of_sigxfsz_past_ulimit_f_rather_than_getting_efbig(
        tmp_path, run_cli, detach_leaf):
    import time

    status = tmp_path / "xfsz.status"
    script = tmp_path / "leaf.sh"
    script.write_text(
        '( ulimit -f 1; head -c 8192 /dev/zero > "$2" ) 2> /dev/null\n'
        'printf \'%s\\n\' "$?" > "$1.tmp"\n'
        'mv "$1.tmp" "$1"\n')

    answer = run_cli(detach_leaf, ["bash", str(script), str(status), str(tmp_path / "big")], cwd=tmp_path)

    deadline = time.monotonic() + 3
    while not status.exists() and time.monotonic() < deadline:
        time.sleep(0.02)
    assert (answer, status.read_text() if status.exists() else "never written") == ((0, "", ""), "153\n")


def appeared(path, patience=3):
    import time

    deadline = time.monotonic() + patience
    while not (path.exists() and path.stat().st_size) and time.monotonic() < deadline:
        time.sleep(0.02)
    return path.exists() and path.stat().st_size > 0


def alive(pid):
    import os

    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    return True


@pytest.mark.process("a detached sh and a nohup-launched sh in a forked launcher's process group, sent a TERM")
def test_main_launches_a_child_that_writes_its_completion_file_after_a_term_to_the_launchers_process_group_where_a_nohup_child_does_not(
        tmp_path, run_cli, detach_leaf):
    import os
    import signal
    import time

    go, answer = tmp_path / "go", tmp_path / "answer"
    detached_exit, detached_pid = tmp_path / "detached.exit", tmp_path / "detached.pid"
    control_exit, control_pid = tmp_path / "control.exit", tmp_path / "control.pid"
    leaf = tmp_path / "leaf.sh"
    leaf.write_text(
        'printf \'%s\\n\' "$$" > "$2"\n'
        'n=0\n'
        f'while [ ! -e "{go}" ] && [ "$n" -lt 150 ]; do sleep 0.02; n=$((n + 1)); done\n'
        'printf \'0\\n\' > "$1"\n')

    launcher = os.fork()
    if launcher == 0:
        try:
            os.setpgid(0, 0)
            signal.signal(signal.SIGTERM, signal.SIG_DFL)
            subprocess.Popen(["nohup", "sh", str(leaf), str(control_exit), str(control_pid)],
                             stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            answer.write_text(repr(run_cli(detach_leaf, ["sh", str(leaf), str(detached_exit), str(detached_pid)])))
            time.sleep(60)
        finally:
            os._exit(0)

    pids, launcher_gone = [], False
    try:
        launched = all(appeared(path) for path in (answer, detached_pid, control_pid))
        pids = [int(path.read_text()) for path in (detached_pid, control_pid) if appeared(path, 0)]
        alive_at_term = [alive(pid) for pid in pids]
        os.killpg(launcher, signal.SIGTERM)
        deadline = time.monotonic() + 3
        while not launcher_gone and time.monotonic() < deadline:
            launcher_gone = os.waitpid(launcher, os.WNOHANG)[0] == launcher
            time.sleep(0.02)
        deadline = time.monotonic() + 3
        while len(pids) == 2 and alive(pids[1]) and time.monotonic() < deadline:
            time.sleep(0.02)
        go.write_text("")
        appeared(detached_exit)
        control_alive = len(pids) == 2 and alive(pids[1])
    finally:
        for pid in pids:
            try:
                os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        try:
            os.killpg(launcher, signal.SIGKILL)
            os.waitpid(launcher, 0)
        except (ProcessLookupError, ChildProcessError):
            pass

    assert (launched, answer.read_text() if answer.exists() else "never answered", alive_at_term, launcher_gone,
            detached_exit.read_text() if detached_exit.exists() else "never written",
            control_alive, control_exit.exists()) == (True, repr((0, "", "")), [True, True], True, "0\n", False, False)


@pytest.mark.process("a detached bash whose pipeline writer dies of SIGPIPE")
def test_main_launches_a_writer_whose_reader_closes_early_that_dies_of_sigpipe_silently(
        tmp_path, run_cli, detach_leaf):
    status, err = tmp_path / "pipe-writer.status", tmp_path / "pipe-writer.err"
    script = tmp_path / "pipe-leaf.sh"
    script.write_text(
        'exec 2> "$2"\n'
        's="$(printf \'%070000d\' 0)"\n'
        'printf \'%s\\n\' x "$s" "$s" "$s" "$s" "$s" | { IFS= read -r _; }\n'
        'printf \'%s\\n\' "${PIPESTATUS[0]}" > "$1"\n')

    answer = run_cli(detach_leaf, ["bash", str(script), str(status), str(err)], cwd=tmp_path)

    assert (answer, status.read_text() if appeared(status) else "never written", err.read_text()) == (
        (0, "", ""), "141\n", "")


@pytest.mark.process("a detached sh writing a file")
def test_main_exits_0_silently_and_the_command_it_was_given_runs(tmp_path, run_cli, detach_leaf):
    ran = tmp_path / "launch-ran"

    answer = run_cli(detach_leaf, ["sh", "-c", 'printf ran > "$1"', "sh", str(ran)], cwd=tmp_path)

    assert (answer, ran.read_text() if appeared(ran) else "never written") == ((0, "", ""), "ran")


@pytest.mark.process("a detached bash reporting its signal dispositions, stdin and output fds")
def test_main_launches_a_command_seeing_int_quit_ignored_xfsz_pipe_default_stdin_eof_and_the_callers_stdout_stderr(
        tmp_path, run_cli, capfd, detach_leaf):
    import os

    seen = tmp_path / "dispositions.seen"
    probe = tmp_path / "dispositions-probe.sh"
    probe.write_text(
        'int_quit="$(python3 -c \'import signal; print(*[int(h) if isinstance(h, int) else "handler" '
        'for h in map(signal.getsignal, (signal.SIGINT, signal.SIGQUIT))])\')"\n'
        '( ulimit -f 1; head -c 8192 /dev/zero > "$2" ) 2> /dev/null\n'
        'xfsz=$?\n'
        'yes > >(head -n 1 > /dev/null)\n'
        'pipe=$?\n'
        'if IFS= read -r line; then stdin="read:$line"; else stdin="eof"; fi\n'
        "printf 'probe-stdout\\n'\n"
        "printf 'probe-stderr\\n' >&2\n"
        'printf \'%s\\n\' "int-quit=$int_quit" "xfsz-status=$xfsz" "pipe-status=$pipe" "stdin=$stdin" > "$1.tmp"\n'
        'mv "$1.tmp" "$1"\n')

    reader, writer = os.pipe()
    os.write(writer, b"caller-data\n")
    os.close(writer)
    saved = os.dup(0)
    os.dup2(reader, 0)
    os.close(reader)
    try:
        code, out, err = run_cli(detach_leaf, ["bash", str(probe), str(seen), str(tmp_path / "xfsz.big")], cwd=tmp_path)
    finally:
        os.dup2(saved, 0)
        os.close(saved)
    report = seen.read_text() if appeared(seen) else "never written"
    later = capfd.readouterr()

    assert (code, out + later.out, err + later.err, report) == (
        0, "probe-stdout\n", "probe-stderr\n",
        "int-quit=1 1\nxfsz-status=153\npipe-status=141\nstdin=eof\n")


@pytest.mark.process("detach-leaf.sh run through a symlink to the skill directory")
def test_a_run_through_a_symlink_to_the_skill_directory_launches_its_argv_in_the_callers_working_directory(tmp_path):
    import pathlib

    skill = pathlib.Path(__file__).resolve().parents[3]
    (tmp_path / "linked-skill").symlink_to(skill, target_is_directory=True)
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    wrote = "detach-leaf-symlink-cwd.%d" % id(tmp_path)

    ran = subprocess.run([str(tmp_path / "linked-skill" / "scripts" / "detach-leaf.sh"),
                          "sh", "-c", 'printf ran > "$1"', "sh", wrote],
                         cwd=elsewhere, stdin=subprocess.DEVNULL, capture_output=True, text=True)
    written = (elsewhere / wrote).read_text() if appeared(elsewhere / wrote) else "never written"
    beside = [str(path) for path in (skill / wrote, skill / "scripts" / wrote) if path.exists()]
    for path in beside:
        pathlib.Path(path).unlink()

    assert (ran.returncode, ran.stdout, ran.stderr, written, beside) == (0, "", "", "ran", [])
