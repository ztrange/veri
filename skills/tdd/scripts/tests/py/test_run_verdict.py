"""In-process cases for veri/run_verdict.py, the module run-verdict.sh is a shim over."""
import importlib.util
import os
import shutil

import pytest

from conftest import SCRIPTS


def staged_module(scripts):
    """veri/run_verdict.py copied under <scripts>/veri/ and loaded from there, so the scripts
    directory it computes from its own path is <scripts>."""
    (scripts / "veri").mkdir(parents=True)
    copy = scripts / "veri" / "run_verdict.py"
    shutil.copy(SCRIPTS / "veri" / "run_verdict.py", copy)
    spec = importlib.util.spec_from_file_location("staged_run_verdict", copy)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("verifier", ["absent", "not executable"])
def test_main_without_an_executable_verify_sh_returns_2_names_it_and_never_execs(
        verifier, tmp_path, monkeypatch, capfd):
    scripts = tmp_path / "scripts"
    run_verdict = staged_module(scripts)
    if verifier == "not executable":
        (scripts / "verify.sh").write_text("#!/usr/bin/env bash\nexit 0\n")
    run = tmp_path / "run"
    (run / ".tdd").mkdir(parents=True)
    (run / ".tdd" / "verify-red.reason").write_text("an earlier step's reason\n")
    monkeypatch.chdir(run)
    calls = []
    monkeypatch.setattr(os, "execv", lambda path, args: calls.append((path, list(args))))

    code = run_verdict.main(["--step", "t", "red", "spec.md", "tests/x.test.sh", "case"])

    captured = capfd.readouterr()
    assert (code, calls, captured.err) == (
        2, [],
        f"run-verdict.sh: cannot start the verifier: {scripts}/verify.sh is missing or not executable\n")
    assert (run / ".tdd" / "verify-red.reason").read_text() == "an earlier step's reason\n"


def test_main_execs_verify_sh_once_with_argv_unchanged_and_without_a_tdd_leaves_fd_2_alone(
        tmp_path, monkeypatch):
    scripts = tmp_path / "scripts"
    run_verdict = staged_module(scripts)
    (scripts / "verify.sh").write_text("#!/usr/bin/env bash\nexit 0\n")
    (scripts / "verify.sh").chmod(0o755)
    run = tmp_path / "run"
    run.mkdir()
    monkeypatch.chdir(run)
    import signal
    import subprocess
    execs, dup2s, spawned = [], [], []
    monkeypatch.setattr(os, "execv", lambda path, args: execs.append((path, list(args))))
    monkeypatch.setattr(os, "dup2", lambda *a, **k: dup2s.append(a))
    monkeypatch.setattr(signal, "signal", lambda signum, handler: None)
    monkeypatch.setattr(subprocess, "Popen", lambda *a, **k: spawned.append(a))
    environ = dict(os.environ)
    title = "that shell's $HOME `job` \"spec\"\nsecond line"
    argv = ["--step", title, "red", "spec.md", "tests/x.test.sh", "case"]

    run_verdict.main(list(argv))

    verifier = f"{scripts}/verify.sh"
    assert (execs, dup2s, spawned, dict(os.environ), os.path.realpath(os.getcwd())) == (
        [(verifier, [verifier, *argv])], [], [], environ, os.path.realpath(run))


@pytest.mark.parametrize("argv, reason, target", [
    (["red", "spec.md", "tests/x.test.sh", "case"], "verify-red.reason", "file"),
    (["--step", "t", "red", "spec.md", "tests/x.test.sh", "case"], "verify-red.reason", "file"),
    (["red", "spec.md", "tests/x.test.sh", "case"], "verify-red.reason", "symlink"),
    (["red", "spec.md", "tests/x.test.sh", "case"], "verify-red.reason", "absent"),
    ([], "verify-.reason", "kept"),
])
def test_main_empties_the_phase_reason_file_in_place_before_the_exec_and_never_creates_one(
        argv, reason, target, tmp_path, monkeypatch):
    scripts = tmp_path / "scripts"
    run_verdict = staged_module(scripts)
    (scripts / "verify.sh").write_text("#!/usr/bin/env bash\nexit 0\n")
    (scripts / "verify.sh").chmod(0o755)
    run = tmp_path / "run"
    (run / ".tdd").mkdir(parents=True)
    monkeypatch.chdir(run)
    path = run / ".tdd" / reason
    held = path
    if target == "symlink":
        held = tmp_path / "elsewhere.reason"
        path.symlink_to(held)
    if target != "absent":
        held.write_text("an earlier step's reason\n")
        inode = held.stat().st_ino
    import signal
    seen = []
    monkeypatch.setattr(os, "execv", lambda path_, args: seen.append(
        held.read_text() if held.exists() else None))
    monkeypatch.setattr(os, "dup2", lambda *a, **k: None)
    monkeypatch.setattr(signal, "signal", lambda signum, handler: None)

    run_verdict.main(list(argv))

    if target == "absent":
        assert (seen, path.exists()) == ([None], False)
    elif target == "kept":
        assert (seen, held.stat().st_ino) == (["an earlier step's reason\n"], inode)
    else:
        assert (seen, held.stat().st_ino, path.is_symlink()) == (
            [""], inode, target == "symlink")


def test_main_finds_the_phase_value_blind_past_leading_step_and_fast_cmd_pairs_as_the_library_says(
        tmp_path, monkeypatch):
    import signal
    import subprocess
    scripts = tmp_path / "scripts"
    run_verdict = staged_module(scripts)
    (scripts / "verify.sh").write_text("#!/usr/bin/env bash\nexit 0\n")
    (scripts / "verify.sh").chmod(0o755)
    run = tmp_path / "run"
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(os, "execv", lambda path, args: None)
    monkeypatch.setattr(os, "dup2", lambda *a, **k: None)
    monkeypatch.setattr(signal, "signal", lambda signum, handler: None)

    def emptied(argv):
        if run.exists():
            shutil.rmtree(run)
        (run / ".tdd").mkdir(parents=True)
        for word in {"", *argv}:
            (run / ".tdd" / f"verify-{word}.reason").write_text("an earlier step's reason\n")
        monkeypatch.chdir(run)
        run_verdict.main(list(argv))
        monkeypatch.chdir(tmp_path)
        return sorted(p.name for p in (run / ".tdd").glob("*.reason") if p.read_text() == "")

    tail = ["spec.md", "t.sh", "case"]
    found = {
        "fast-cmd pair": emptied(["--fast-cmd", "make unit", "red", *tail]),
        "empty step value": emptied(["--step", "", "red", *tail]),
        "option as a value": emptied(["--step", "--fast-cmd", "x", "red"]),
        "lone step": emptied(["--step"]),
        "step=": emptied(["--step=t", "red"]),
        "option after the phase": emptied(["red", "--step", "t", *tail]),
    }
    assert found == {
        "fast-cmd pair": ["verify-red.reason"],
        "empty step value": ["verify-red.reason"],
        "option as a value": ["verify-x.reason"],
        "lone step": [],
        "step=": ["verify---step=t.reason"],
        "option after the phase": ["verify-red.reason"],
    }

    library = SCRIPTS / "lib" / "verify-options.sh"
    words = ["--step", "--fast-cmd", "--steps", "-s", ""]
    by_library = {word: subprocess.run(
        ["bash", "-c", 'source "$1" && verify_takes_a_value "$2"', "bash", str(library), word],
        stdin=subprocess.DEVNULL).returncode == 0 for word in words}
    by_main = {word: emptied([word, "v", "red", *tail]) == ["verify-red.reason"] for word in words}
    assert by_main == by_library


@pytest.mark.parametrize("argv, tdd, stderr_file", [
    (["red", "spec.md", "tests/x.test.sh", "case"], "directory", "existing"),
    (["red", "spec.md", "tests/x.test.sh", "case"], "directory", "absent"),
    (["--step", "t", "red", "spec.md", "tests/x.test.sh", "case"], "symlink", "existing"),
    ([], "directory", "absent"),
    (["red", "spec.md", "tests/x.test.sh", "case"], "absent", "absent"),
])
def test_main_files_fd_2_under_tdd_verify_phase_stderr_appending_with_mode_0o666_before_the_exec(
        argv, tdd, stderr_file, tmp_path, monkeypatch):
    import signal
    scripts = tmp_path / "scripts"
    run_verdict = staged_module(scripts)
    (scripts / "verify.sh").write_text("#!/usr/bin/env bash\nexit 0\n")
    (scripts / "verify.sh").chmod(0o755)
    run = tmp_path / "run"
    run.mkdir()
    if tdd == "directory":
        (run / ".tdd").mkdir()
    elif tdd == "symlink":
        (tmp_path / "held").mkdir()
        (run / ".tdd").symlink_to(tmp_path / "held")
    filed = run / ".tdd" / "verify-red.stderr"
    if stderr_file == "existing":
        filed.write_text("an earlier verdict's stderr\n")
        filed.chmod(0o644)
    monkeypatch.chdir(run)
    spare = os.open(os.devnull, os.O_WRONLY)
    real_dup2 = os.dup2
    dup2s, open_at_exec = [], []

    def dup2(fd, fd2, inheritable=True):
        dup2s.append((fd, fd2, inheritable))
        return real_dup2(fd, spare, inheritable)

    def execv(path, args):
        for fd, _, _ in dup2s:
            try:
                os.fstat(fd)
                open_at_exec.append(fd)
            except OSError:
                pass

    monkeypatch.setattr(os, "dup2", dup2)
    monkeypatch.setattr(os, "execv", execv)
    monkeypatch.setattr(signal, "signal", lambda signum, handler: None)
    umask = os.umask(0o027)
    try:
        run_verdict.main(list(argv))
    finally:
        os.umask(umask)
    os.write(spare, b"this verdict's stderr\n")
    os.close(spare)

    if tdd == "absent" or not argv:
        assert (dup2s, filed.exists()) == ([], False)
    else:
        earlier = "an earlier verdict's stderr\n" if stderr_file == "existing" else ""
        mode = 0o644 if stderr_file == "existing" else 0o640
        assert ([(fd2, inheritable) for _, fd2, inheritable in dup2s], open_at_exec,
                filed.read_text() if filed.exists() else None,
                filed.stat().st_mode & 0o777 if filed.exists() else None) == (
            [(2, True)], [], earlier + "this verdict's stderr\n", mode)


@pytest.mark.parametrize("argv, unopenable, line", [
    (["a/b", "spec.md", "tests/x.test.sh", "case"], None,
     "run-verdict.sh: .tdd/verify-a/b.stderr: No such file or directory\n"),
    (["red", "spec.md", "tests/x.test.sh", "case"], "stderr directory",
     "run-verdict.sh: .tdd/verify-red.stderr: Is a directory\n"),
    (["red", "spec.md", "tests/x.test.sh", "case"], "reason",
     "run-verdict.sh: .tdd/verify-red.reason: Permission denied\n"),
])
def test_main_names_a_filing_or_reason_file_it_cannot_open_on_the_original_stderr_and_still_execs(
        argv, unopenable, line, tmp_path, monkeypatch, capfd):
    import builtins
    import errno
    import signal
    scripts = tmp_path / "scripts"
    run_verdict = staged_module(scripts)
    (scripts / "verify.sh").write_text("#!/usr/bin/env bash\nexit 0\n")
    (scripts / "verify.sh").chmod(0o755)
    run = tmp_path / "run"
    (run / ".tdd").mkdir(parents=True)
    if unopenable == "stderr directory":
        (run / ".tdd" / "verify-red.stderr").mkdir()
    reason = os.path.join(".tdd", "verify-red.reason")
    if unopenable == "reason":
        (run / ".tdd" / "verify-red.reason").write_text("an earlier step's reason\n")
    monkeypatch.chdir(run)
    real_os_open, real_open = os.open, builtins.open

    def refused(path):
        if unopenable == "reason" and os.path.normpath(os.fspath(path)) == reason:
            raise PermissionError(errno.EACCES, os.strerror(errno.EACCES), os.fspath(path))

    def os_open(path, *a, **k):
        refused(path)
        return real_os_open(path, *a, **k)

    def open_(file, *a, **k):
        if isinstance(file, (str, bytes, os.PathLike)):
            refused(file)
        return real_open(file, *a, **k)

    execs, dup2s = [], []
    monkeypatch.setattr(os, "open", os_open)
    monkeypatch.setattr(builtins, "open", open_)
    monkeypatch.setattr(os, "execv", lambda path, args: execs.append((path, list(args))))
    monkeypatch.setattr(os, "dup2", lambda *a, **k: dup2s.append(a))
    monkeypatch.setattr(signal, "signal", lambda signum, handler: None)

    run_verdict.main(list(argv))

    verifier = f"{scripts}/verify.sh"
    captured = capfd.readouterr()
    assert (captured.err, execs) == (line, [(verifier, [verifier, *argv])])
    if unopenable != "reason":
        assert dup2s == []


def test_main_resets_sigpipe_and_sigxfsz_to_sig_dfl_before_the_exec(tmp_path, monkeypatch):
    import signal
    scripts = tmp_path / "scripts"
    run_verdict = staged_module(scripts)
    (scripts / "verify.sh").write_text("#!/usr/bin/env bash\nexit 0\n")
    (scripts / "verify.sh").chmod(0o755)
    run = tmp_path / "run"
    run.mkdir()
    monkeypatch.chdir(run)
    dispositions = {signal.SIGPIPE: signal.SIG_IGN, signal.SIGXFSZ: signal.SIG_IGN}
    at_exec = []

    def signal_(signum, handler):
        previous = dispositions.get(signum, signal.SIG_DFL)
        dispositions[signum] = handler
        return previous

    monkeypatch.setattr(signal, "signal", signal_)
    monkeypatch.setattr(os, "dup2", lambda *a, **k: None)
    monkeypatch.setattr(os, "execv", lambda path, args: at_exec.append(
        (dispositions[signal.SIGPIPE], dispositions[signal.SIGXFSZ])))

    run_verdict.main(["red", "spec.md", "tests/x.test.sh", "case"])

    assert at_exec == [(signal.SIG_DFL, signal.SIG_DFL)]


@pytest.mark.parametrize("environ, at_exec", [
    ({"VERI_SHIM_SET_COERCE": "1", "PYTHONCOERCECLOCALE": "0"}, (None, None)),
    ({"PYTHONCOERCECLOCALE": "1"}, (None, "1")),
])
def test_main_drops_the_shims_coerce_guard_and_marker_before_the_exec_and_keeps_a_callers_own(
        environ, at_exec, tmp_path, monkeypatch):
    import signal
    scripts = tmp_path / "scripts"
    run_verdict = staged_module(scripts)
    (scripts / "verify.sh").write_text("#!/usr/bin/env bash\nexit 0\n")
    (scripts / "verify.sh").chmod(0o755)
    run = tmp_path / "run"
    run.mkdir()
    monkeypatch.chdir(run)
    monkeypatch.delenv("VERI_SHIM_SET_COERCE", raising=False)
    monkeypatch.delenv("PYTHONCOERCECLOCALE", raising=False)
    for name, value in environ.items():
        monkeypatch.setenv(name, value)
    seen = []
    monkeypatch.setattr(signal, "signal", lambda signum, handler: None)
    monkeypatch.setattr(os, "dup2", lambda *a, **k: None)
    monkeypatch.setattr(os, "execv", lambda path, args: seen.append(
        (os.environ.get("VERI_SHIM_SET_COERCE"), os.environ.get("PYTHONCOERCECLOCALE"))))

    run_verdict.main(["red", "spec.md", "tests/x.test.sh", "case"])

    assert seen == [at_exec]


@pytest.mark.parametrize("raised", ["ENOEXEC", "EACCES", "ENOENT", "not an OSError"])
def test_main_retries_an_enoexec_exec_under_bash_returns_2_for_any_other_exec_failure_and_wraps_nothing(
        raised, tmp_path, monkeypatch, capfd):
    import errno
    import signal
    scripts = tmp_path / "scripts"
    run_verdict = staged_module(scripts)
    (scripts / "verify.sh").write_text("exit 0\n")
    (scripts / "verify.sh").chmod(0o755)
    run = tmp_path / "run"
    run.mkdir()
    monkeypatch.chdir(run)
    verifier = f"{scripts}/verify.sh"
    argv = ["--step", "t", "red", "spec.md", "tests/x.test.sh", "case"]
    error = (RuntimeError("not an exec failure") if raised == "not an OSError"
             else OSError(getattr(errno, raised), os.strerror(getattr(errno, raised)), verifier))
    execvps = []

    def execv(path, args):
        raise error

    monkeypatch.setattr(os, "execv", execv)
    monkeypatch.setattr(os, "execvp", lambda file, args: execvps.append((file, list(args))))
    monkeypatch.setattr(os, "dup2", lambda *a, **k: None)
    monkeypatch.setattr(signal, "signal", lambda signum, handler: None)

    if raised == "not an OSError":
        with pytest.raises(RuntimeError):
            run_verdict.main(list(argv))
        assert execvps == []
        return
    code = run_verdict.main(list(argv))

    captured = capfd.readouterr()
    if raised == "ENOEXEC":
        assert (execvps, captured.err) == ([("bash", ["bash", verifier, *argv])], "")
    else:
        assert (code, execvps, captured.err) == (
            2, [],
            f"run-verdict.sh: cannot start the verifier: {verifier}: {os.strerror(getattr(errno, raised))}\n")
