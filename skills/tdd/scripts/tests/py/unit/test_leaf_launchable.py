"""In-process cases for veri/leaf_launchable.py, the module leaf-launchable.sh is a shim over."""
import importlib
import os
import subprocess
import tempfile

import pytest


@pytest.fixture
def leaf_launchable(monkeypatch, tmp_path):
    monkeypatch.setenv("VERI_BASH_MAJOR", "5")
    monkeypatch.setenv("VERI_PYTHON_VERSION", "3.12.0")
    monkeypatch.setenv("CLAUDE_BIN", "stub-claude")
    monkeypatch.setenv("TMPDIR", str(tmp_path))
    return importlib.import_module("veri.leaf_launchable")


def fake_probe(fake_processes, returncode):
    """subprocess answering the leaf probe with <returncode>; any other command fails the case."""
    return fake_processes.answers({"stub-claude --version": (returncode, "", "")}, exact=True)


def test_main_returns_0_silently_for_a_launching_probe_and_2_with_no_stdout_for_a_failing_one(
        capsys, leaf_launchable, fake_processes):
    answers = []
    fake_probe(fake_processes, 0)
    code = leaf_launchable.main([])
    captured = capsys.readouterr()
    answers.append((code, captured.out, captured.err))
    fake_probe(fake_processes, 1)
    code = leaf_launchable.main([])
    captured = capsys.readouterr()
    answers.append((code, captured.out))
    assert answers == [(0, "", ""), (2, "")]
    assert all(0 <= answer[0] <= 3 for answer in answers)


def test_an_unexpected_argument_is_refused_naming_it_with_the_usage_exit_2_and_the_probe_not_run(
        run_cli, leaf_launchable, fake_processes):
    fake = fake_probe(fake_processes, 0)

    assert run_cli(leaf_launchable, ["extra"]) == (
        2, "", f"leaf-launchable.sh: unexpected argument 'extra'\n{leaf_launchable.USAGE}\n")
    assert fake.calls == []


def test_main_returns_2_with_no_stdout_and_no_temp_file_left_over_a_probe_exiting_5_127_or_killed_by_a_signal(
        capsys, monkeypatch, tmp_path, leaf_launchable, fake_processes):
    monkeypatch.setattr(tempfile, "tempdir", str(tmp_path))
    answers = []
    for returncode in (5, 127, -9):
        fake_probe(fake_processes, returncode)
        code = leaf_launchable.main([])
        captured = capsys.readouterr()
        answers.append((returncode, code, captured.out, sorted(p.name for p in tmp_path.iterdir())))
    assert answers == [(5, 2, "", []), (127, 2, "", []), (-9, 2, "", [])]


def test_main_refuses_on_bash_before_the_python_floor_and_on_the_floor_before_the_probe_with_the_leaf_launchable_prefix(
        capsys, monkeypatch, tmp_path, leaf_launchable, fake_processes):
    monkeypatch.setenv("VERI_VENV", str(tmp_path / "no-venv"))
    monkeypatch.setenv("VERI_PYTHON_VERSION", "3.11.9")

    def missing(line, **kwargs):
        program = fake.argvs[-1][0]
        raise FileNotFoundError(2, "No such file or directory", program)

    fake = fake_processes.answers({"stub-claude": (0, "", "")}, default=missing)
    answers = []
    for major in ("3", "5"):
        monkeypatch.setenv("VERI_BASH_MAJOR", major)
        del fake.seen[:]
        code = leaf_launchable.main([])
        captured = capsys.readouterr()
        answers.append((code, captured.out, [line.split(";")[0] for line in captured.err.splitlines()],
                        [command for command in fake.argvs if command[0] == "stub-claude"]))
    assert answers == [
        (2, "", ["leaf-launchable: veri needs bash 5 or newer"], []),
        (2, "", ["leaf-launchable: veri needs Python 3.12 or newer"], []),
    ]


def test_main_probes_claude_bin_else_claude_once_with_stdin_inherited_stdout_discarded_stderr_to_a_removed_temp_file_and_returns_2_naming_an_oserror(
        capsys, monkeypatch, tmp_path, leaf_launchable, fake_processes):
    monkeypatch.setattr(tempfile, "tempdir", str(tmp_path))
    raised = []

    def spy(line, **kwargs):
        if raised:
            raise raised[0]
        return 0, "", ""

    fake = fake_processes.answers({}, default=spy)
    answers = []
    monkeypatch.delenv("CLAUDE_BIN")
    answers.append(leaf_launchable.main([]))
    monkeypatch.setenv("CLAUDE_BIN", "")
    answers.append(leaf_launchable.main([]))
    monkeypatch.setenv("CLAUDE_BIN", "stub-claude")
    answers.append(leaf_launchable.main([]))
    assert capsys.readouterr().err == ""
    blocks = []
    for error in (FileNotFoundError(2, "No such file or directory", "stub-claude"),
                  PermissionError(13, "Permission denied", "stub-claude")):
        raised[:] = [error]
        code = leaf_launchable.main([])
        captured = capsys.readouterr()
        blocks.append((code, captured.out, "    " + str(error) in captured.err.splitlines()))
    probe = (None, True, True)
    calls = []
    for argv, kwargs in fake.seen:
        stderr = kwargs.get("stderr")
        calls.append((list(argv), kwargs.get("stdin"), kwargs.get("stdout") == subprocess.DEVNULL,
                      stderr not in (None, subprocess.PIPE, subprocess.DEVNULL, subprocess.STDOUT)))
    assert calls == [(["claude", "--version"],) + probe, (["claude", "--version"],) + probe] + [
        (["stub-claude", "--version"],) + probe] * 3
    assert answers == [0, 0, 0]
    assert blocks == [(2, "", True), (2, "", True)]
    assert sorted(p.name for p in tmp_path.iterdir()) == []


def test_main_prints_the_failed_probe_diagnostic_byte_identical_to_the_bash_script_indenting_its_stderr_as_bytes_split_on_newline_only(
        capfdbinary, leaf_launchable, fake_processes):
    def answering(said):
        def fake_call(line, **kwargs):
            stderr = kwargs["stderr"]
            os.write(stderr if isinstance(stderr, int) else stderr.fileno(), said)
            return 1, "", ""

        fake_processes.answers({}, default=fake_call)

    header = (b"leaf-launchable: the leaf binary (stub-claude) could not be launched, so every leaf of this run"
              b" would die at launch. It said:\n")
    closing = ("Run the conductor from a plain shell instead — the supported invocation is:\n"
               "    claude -p \"/tdd <issue-number>\"\n"
               "veri does not work around this itself: a guard of this kind names a risk the binary is refusing"
               " to take, and taking it silently on the operator's behalf would put that risk on them without"
               " their knowledge.\n").encode("utf-8")
    answers = []
    for said in (b"", b"one\r\ntwo\n\n\xff three\n", b"last line\nno newline"):
        answering(said)
        code = leaf_launchable.main([])
        captured = capfdbinary.readouterr()
        answers.append((code, captured.out, captured.err))
    assert answers == [
        (2, b"", header + closing),
        (2, b"", header + b"    one\r\n    two\n    \n    \xff three\n" + closing),
        (2, b"", header + b"    last line\n    no newline" + closing),
    ]


def test_main_prints_the_full_failed_probe_diagnostic_naming_the_binary_as_given_and_the_oserror_for_a_binary_not_found_or_not_executable(
        capfdbinary, monkeypatch, leaf_launchable, fake_processes):
    monkeypatch.setenv("CLAUDE_BIN", "missing/stub claude")

    def raising(error):
        fake_processes.answers({}, default=error)

    header = (b"leaf-launchable: the leaf binary (missing/stub claude) could not be launched, so every leaf of this"
              b" run would die at launch. It said:\n")
    closing = ("Run the conductor from a plain shell instead — the supported invocation is:\n"
               "    claude -p \"/tdd <issue-number>\"\n"
               "veri does not work around this itself: a guard of this kind names a risk the binary is refusing"
               " to take, and taking it silently on the operator's behalf would put that risk on them without"
               " their knowledge.\n").encode("utf-8")
    answers = []
    for error in (FileNotFoundError(2, "No such file or directory", "missing/stub claude"),
                  PermissionError(13, "Permission denied", "missing/stub claude")):
        raising(error)
        code = leaf_launchable.main([])
        captured = capfdbinary.readouterr()
        answers.append((code, captured.out, captured.err))
    assert answers == [
        (2, b"", header + b"    [Errno 2] No such file or directory: 'missing/stub claude'\n" + closing),
        (2, b"", header + b"    [Errno 13] Permission denied: 'missing/stub claude'\n" + closing),
    ]


def test_run_cli_refusing_a_binary_that_cannot_launch_starts_nothing_but_the_probe_and_leaves_no_file(
        monkeypatch, tmp_path, run_cli, leaf_launchable, fake_processes):
    work = tmp_path / "work"
    work.mkdir()
    monkeypatch.setattr(tempfile, "tempdir", str(tmp_path))

    def fake_call(line, **kwargs):
        os.write(kwargs["stderr"].fileno(), b"Error: cannot be launched here.\n")
        return 1, "", ""

    fake = fake_processes.answers({"stub-claude --version": fake_call}, exact=True)
    code, out, err = run_cli(leaf_launchable, [], cwd=str(work))
    assert (code, out, fake.argvs) == (2, "", [["stub-claude", "--version"]])
    assert "    Error: cannot be launched here.\n" in err and 'claude -p "/tdd <issue-number>"' in err
    assert sorted(p.name for p in tmp_path.iterdir()) == ["work"]
    assert list(work.iterdir()) == []
