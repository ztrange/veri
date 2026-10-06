"""In-process cases for veri/preserve_attempt.py, the module preserve-attempt.sh is a shim over."""
import importlib
import os
import pathlib
import subprocess
import sys
import tempfile

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
for path in (SCRIPTS, SCRIPTS / "veri"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))


@pytest.fixture
def preserve_attempt():
    return importlib.import_module("veri.preserve_attempt")


def fake_processes(monkeypatch):
    """Every subprocess entry point recording each command as one line, its program by basename."""
    calls = []

    def record(args, *_, **__):
        calls.append(" ".join([os.path.basename(str(args[0]))] + [str(a) for a in args[1:]]))
        return subprocess.CompletedProcess(args, 0, "", "")

    for name in ("run", "Popen", "call", "check_call", "check_output"):
        monkeypatch.setattr(subprocess, name, record)
    return calls


def test_main_refuses_missing_or_empty_arguments_with_its_usage_line_and_no_git_call(
        monkeypatch, capsys, preserve_attempt):
    calls = fake_processes(monkeypatch)

    answers = []
    for argv in ([], ["409", "3", "develop-green"], ["409", "3", "develop-green", ""]):
        code = preserve_attempt.main(argv)
        captured = capsys.readouterr()
        answers.append((argv, code, captured.out, captured.err))

    usage = "usage: preserve-attempt.sh <issue> <step> <phase> <attempt> [<mark>]\n"
    assert calls == []
    assert answers == [
        ([], 2, "", usage),
        (["409", "3", "develop-green"], 2, "", usage),
        (["409", "3", "develop-green", ""], 2, "", usage),
    ]


def test_main_returns_2_when_commit_tree_exits_128_with_the_scratch_directory_gone_and_no_update_ref(
        monkeypatch, tmp_path, preserve_attempt):
    repo = tmp_path / "repo"
    repo.mkdir()
    scratch_parent = tmp_path / "tmp"
    scratch_parent.mkdir()
    monkeypatch.chdir(repo)
    monkeypatch.setenv("TMPDIR", str(scratch_parent))
    monkeypatch.setattr(tempfile, "tempdir", None)
    calls = []

    def fake_run(args, *_, **__):
        line = " ".join([os.path.basename(str(args[0]))] + [str(a) for a in args[1:]])
        calls.append(line)
        if line.startswith("git rev-parse --show-toplevel"):
            return subprocess.CompletedProcess(args, 0, f"{repo}\n", "")
        if line.startswith("git write-tree"):
            return subprocess.CompletedProcess(args, 0, "4b825dc642cb6eb9a060e54bf8d69288fbee4904\n", "")
        if line.startswith("git commit-tree"):
            return subprocess.CompletedProcess(args, 128, "", "")
        return subprocess.CompletedProcess(args, 0, "", "")

    monkeypatch.setattr(subprocess, "run", fake_run)

    code = preserve_attempt.main(["409", "3", "develop-green", "1"])

    update_refs = [line for line in calls if line.startswith("git update-ref")]
    assert (code, update_refs, sorted(os.listdir(scratch_parent))) == (2, [], [])


def test_main_returns_1_with_its_could_not_preserve_line_and_no_copy_when_update_ref_exits_128(
        monkeypatch, tmp_path, capsys, preserve_attempt):
    repo = tmp_path / "repo"
    (repo / ".tdd").mkdir(parents=True)
    (repo / ".tdd" / "develop-green.log").write_text("log\n")
    (repo / ".tdd" / "develop-green.out").write_text("out\n")
    monkeypatch.chdir(repo)

    def fake_run(args, *_, **__):
        line = " ".join([os.path.basename(str(args[0]))] + [str(a) for a in args[1:]])
        if line.startswith("git rev-parse --show-toplevel"):
            return subprocess.CompletedProcess(args, 0, f"{repo}\n", "")
        if line.startswith("git write-tree"):
            return subprocess.CompletedProcess(args, 0, "4b825dc642cb6eb9a060e54bf8d69288fbee4904\n", "")
        if line.startswith("git commit-tree"):
            return subprocess.CompletedProcess(args, 0, "1111111111111111111111111111111111111111\n", "")
        if line.startswith("git update-ref"):
            return subprocess.CompletedProcess(args, 128, None, None)
        return subprocess.CompletedProcess(args, 0, "", "")

    monkeypatch.setattr(subprocess, "run", fake_run)

    code = preserve_attempt.main(["409", "3", "develop-green", "1", "reject"])
    captured = capsys.readouterr()

    line = ("preserve-attempt.sh: could not preserve issue 409 step 3 develop-green attempt 1"
            " to refs/veri/attempts/409/3/develop-green-1")
    assert (code, captured.out, captured.err.splitlines()[-1:], (repo / ".tdd" / "attempts").exists()) == (
        1, "", [line], False)


def test_main_names_the_ref_by_the_ledger_index_ledger_steps_gives_the_step_past_prose_and_star_lines(
        monkeypatch, tmp_path, preserve_attempt):
    from veri.ledger import ledger_steps

    repo = tmp_path / "repo"
    (repo / ".tdd").mkdir(parents=True)
    step = "keep the leaf's output under refs/veri"
    ledger = (
        "# Plan for #409\n"
        f"Prose first: {step}, never the branch.\n"
        f"* [ ] {step}\n"
        "- [x] an earlier step ⟦criterion 1⟧\n"
        f"- [ ] {step} ⟦criterion 2⟧\n"
    )
    (repo / ".tdd" / "issue-409.md").write_text(ledger)
    monkeypatch.chdir(repo)
    update_refs = []

    def fake_run(args, *_, **__):
        line = " ".join([os.path.basename(str(args[0]))] + [str(a) for a in args[1:]])
        if line.startswith("git rev-parse --show-toplevel"):
            return subprocess.CompletedProcess(args, 0, f"{repo}\n", "")
        if line.startswith("git write-tree"):
            return subprocess.CompletedProcess(args, 0, "4b825dc642cb6eb9a060e54bf8d69288fbee4904\n", "")
        if line.startswith("git commit-tree"):
            return subprocess.CompletedProcess(args, 0, "1111111111111111111111111111111111111111\n", "")
        if line.startswith("git update-ref"):
            update_refs.append(str(args[2]))
        return subprocess.CompletedProcess(args, 0, "", "")

    monkeypatch.setattr(subprocess, "run", fake_run)

    code = preserve_attempt.main(["409", step, "develop-green", "1"])

    index = next(record[0] for record in ledger_steps(ledger) if step in record[6])
    assert (index, code, update_refs) == ("2", 0, ["refs/veri/attempts/409/2/develop-green-1"])
