"""In-process cases for veri/solvable_issues.py, the module solvable-issues.sh is a shim over."""
import importlib
import json
import os
import pathlib
import subprocess
import sys

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
for path in (SCRIPTS, SCRIPTS / "veri"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

USAGE = "usage: solvable-issues.sh [--repo owner/name]\n"


@pytest.fixture(autouse=True)
def no_ambient_tunables(monkeypatch):
    for name in ("VERI_GH_JSON", "VERI_LABEL", "VERI_PRIORITY_LABEL"):
        monkeypatch.delenv(name, raising=False)


@pytest.fixture
def solvable_issues():
    return importlib.import_module("veri.solvable_issues")


def no_process(monkeypatch):
    """subprocess.run and subprocess.Popen recording every command they are asked to start."""
    started = []

    def refuse(args, *rest, **kwargs):
        started.append(args)
        raise AssertionError("unexpected command: %r" % (args,))

    monkeypatch.setattr(subprocess, "run", refuse)
    monkeypatch.setattr(subprocess, "Popen", refuse)
    return started


@pytest.mark.parametrize("argv", [["--repo"], ["--repo", ""]])
def test_main_refuses_repo_with_no_value_or_an_empty_one_with_2_and_the_usage_line_alone_starting_no_process(argv, monkeypatch, capsys, solvable_issues):
    started = no_process(monkeypatch)

    code = solvable_issues.main(argv)

    out, err = capsys.readouterr()
    assert (code, started, out, err) == (2, [], "", USAGE)


def fake_git_answering_nothing(monkeypatch):
    """subprocess.run answering `git worktree list --porcelain` with nothing; any other command fails the case."""
    def fake_run(args, *rest, **kwargs):
        if list(args[:4]) != ["git", "worktree", "list", "--porcelain"]:
            raise AssertionError("unexpected command: %r" % (args,))
        return subprocess.CompletedProcess(args, 0, "", "")

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(subprocess, "Popen", fake_run)


def opted_in(number):
    return {"number": number, "title": "issue %d" % number, "state": "OPEN",
            "labels": [{"name": "ready-for-agent"}], "body": "## Blocked by\n\nNone.\n"}


def test_main_prints_two_open_opted_in_unblocked_issues_one_per_line_ascending_and_returns_0(tmp_path, monkeypatch, capsys, solvable_issues):
    (tmp_path / "issues.json").write_text(json.dumps([opted_in(5), opted_in(6)]))
    (tmp_path / "prs.json").write_text("[]")
    monkeypatch.setenv("VERI_GH_JSON", str(tmp_path))
    fake_git_answering_nothing(monkeypatch)

    code = solvable_issues.main([])

    out, err = capsys.readouterr()
    assert (code, out) == (0, "5\n6\n")


def fake_git_answering(monkeypatch, main_tree):
    """subprocess.run answering `git worktree list --porcelain` with `worktree <main_tree>`; any other command fails the case."""
    def fake_run(args, *rest, **kwargs):
        if list(args[:4]) != ["git", "worktree", "list", "--porcelain"]:
            raise AssertionError("unexpected command: %r" % (args,))
        return subprocess.CompletedProcess(args, 0, "worktree %s\nHEAD 0000000\nbranch refs/heads/main\n" % main_tree, "")

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(subprocess, "Popen", fake_run)


def test_main_withholds_the_issue_whose_lock_under_the_main_working_tree_git_names_holds_a_live_pid(tmp_path, monkeypatch, capsys, solvable_issues):
    (tmp_path / "issues.json").write_text(json.dumps([opted_in(5), opted_in(6)]))
    (tmp_path / "prs.json").write_text("[]")
    monkeypatch.setenv("VERI_GH_JSON", str(tmp_path))
    decoy = tmp_path / "decoy"
    lock = decoy / ".tdd" / "wt" / "5" / ".tdd" / "conductor.pid"
    lock.parent.mkdir(parents=True)
    lock.write_text("%d\n" % os.getpid())
    fake_git_answering(monkeypatch, decoy)

    code = solvable_issues.main([])

    out, err = capsys.readouterr()
    assert (code, out) == (0, "6\n")


def record_processes(monkeypatch):
    """subprocess.run and subprocess.Popen recording every command, answering each with nothing."""
    started = []

    def record(args, *rest, **kwargs):
        started.append(list(args))
        return subprocess.CompletedProcess(args, 0, "", "")

    monkeypatch.setattr(subprocess, "run", record)
    monkeypatch.setattr(subprocess, "Popen", record)
    return started


def labelled(number, *names):
    return dict(opted_in(number), labels=[{"name": name} for name in names])


def test_main_refuses_an_empty_label_tunable_and_opts_in_by_exact_label_name(tmp_path, monkeypatch, capsys, solvable_issues):
    (tmp_path / "prs.json").write_text("[]")
    monkeypatch.setenv("VERI_GH_JSON", str(tmp_path))
    unlabelled = opted_in(9)
    del unlabelled["labels"]
    (tmp_path / "issues.json").write_text(json.dumps([
        labelled(5, "ready-for-agent"), labelled(6, "Ready-For-Agent"), labelled(7, "other"),
        labelled(8, "ready-for-agent", "other"), unlabelled, labelled(10, "OTHER")]))
    refused = "solvable-issues: %s is set but empty: name a label or leave it unset\n"

    def run(argv, **tunables):
        for name in ("VERI_LABEL", "VERI_PRIORITY_LABEL"):
            if name in tunables:
                monkeypatch.setenv(name, tunables[name])
            else:
                monkeypatch.delenv(name, raising=False)
        started = record_processes(monkeypatch)
        code = solvable_issues.main(argv)
        out, err = capsys.readouterr()
        return code, started, out, err

    assert run([], VERI_LABEL="") == (2, [], "", refused % "VERI_LABEL")
    assert run([], VERI_PRIORITY_LABEL="") == (2, [], "", refused % "VERI_PRIORITY_LABEL")
    assert run([], VERI_LABEL="", VERI_PRIORITY_LABEL="") == (2, [], "", refused % "VERI_LABEL")
    assert run(["--repo"], VERI_LABEL="") == (2, [], "", USAGE)
    assert run([])[::2] == (0, "5\n8\n")
    assert run([], VERI_LABEL="other")[::2] == (0, "7\n8\n")

    (tmp_path / "issues.json").write_text(json.dumps([dict(opted_in(5), labels=None)]))
    with pytest.raises(TypeError):
        run([])
