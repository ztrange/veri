"""In-process cases for veri/run_verdict.py, the module run-verdict.sh is a shim over."""
import importlib.util
import os
import pathlib
import shutil
import sys

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
for path in (SCRIPTS, SCRIPTS / "veri"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))


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
        return sorted(p.name for p in (run / ".tdd").iterdir() if p.read_text() == "")

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
