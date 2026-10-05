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


def fake_gh_refusing_graphql(monkeypatch):
    """subprocess.run refusing `gh issue list`/`gh pr list`, answering `gh api` with an empty page and git with nothing; records the gh commands."""
    started = []

    def fake_run(args, *rest, **kwargs):
        args = list(args)
        if args[:1] == ["gh"]:
            started.append(args)
            if args[1] == "api":
                return subprocess.CompletedProcess(args, 0, "[]\n", "")
            return subprocess.CompletedProcess(args, 1, "", "")
        if args[:4] == ["git", "worktree", "list", "--porcelain"]:
            return subprocess.CompletedProcess(args, 0, "", "")
        raise AssertionError("unexpected command: %r" % (args,))

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(subprocess, "Popen", fake_run)
    return started


@pytest.mark.parametrize("gh_json_dir", [None, ""])
def test_main_reads_issues_then_prs_through_gh_forwarding_repo_verbatim_and_falls_back_to_rest_paths(gh_json_dir, monkeypatch, capsys, solvable_issues):
    if gh_json_dir is not None:
        monkeypatch.setenv("VERI_GH_JSON", gh_json_dir)
    monkeypatch.setenv("VERI_GH_DRIVER", "auto")

    def reads(repo):
        scope = ["--repo", repo] if repo else []
        prefix = "repos/%s" % (repo or "{owner}/{repo}")
        return [
            ["gh", "issue", "list", "--limit", "10000", "--json", "number,title,labels,body,state", *scope],
            ["gh", "api", prefix + "/issues?page=1"],
            ["gh", "pr", "list", "--limit", "10000", "--json", "body,state", *scope],
            ["gh", "api", prefix + "/pulls?page=1"],
        ]

    observed = {}
    for argv in ([], ["--repo", "o/n"], ["--repo", "o/n", "--repo", "x/y"], ["--repo=x"], ["foo"]):
        started = fake_gh_refusing_graphql(monkeypatch)
        solvable_issues.main(argv)
        capsys.readouterr()
        observed[tuple(argv)] = started

    assert observed == {
        (): reads(None),
        ("--repo", "o/n"): reads("o/n"),
        ("--repo", "o/n", "--repo", "x/y"): reads("o/n"),
        ("--repo=x",): reads(None),
        ("foo",): reads(None),
    }


def fake_gh_refusing(monkeypatch, refused):
    """subprocess.run failing every gh command whose argv holds a word in `refused`, answering the rest with an empty page and git with nothing; records the gh commands."""
    started = []

    def fake_run(args, *rest, **kwargs):
        args = list(args)
        if args[:1] == ["gh"]:
            started.append(args)
            if any(word in refused for word in args[1:3]) or any(word in args[-1] for word in refused):
                return subprocess.CompletedProcess(args, 1, "", "")
            return subprocess.CompletedProcess(args, 0, "[]\n", "")
        if args[:4] == ["git", "worktree", "list", "--porcelain"]:
            return subprocess.CompletedProcess(args, 0, "", "")
        raise AssertionError("unexpected command: %r" % (args,))

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(subprocess, "Popen", fake_run)
    return started


def test_main_reads_both_documents_returning_2_on_no_answer_raising_on_a_missing_or_broken_one_and_joining_pages_without_prs(tmp_path, monkeypatch, capsys, solvable_issues):
    monkeypatch.setenv("VERI_GH_DRIVER", "auto")

    started = fake_gh_refusing(monkeypatch, ("issue", "/issues"))
    code = solvable_issues.main([])
    out, err = capsys.readouterr()
    assert (code, out, [args for args in started if "pr" in args or any("/pulls" in word for word in args)]) == (2, "", [])

    fake_gh_refusing(monkeypatch, ("pr", "/pulls"))
    code = solvable_issues.main([])
    out, err = capsys.readouterr()
    assert (code, out) == (2, "")

    fake_git_answering_nothing(monkeypatch)
    monkeypatch.setenv("VERI_GH_JSON", str(tmp_path))
    (tmp_path / "prs.json").write_text("[]")
    with pytest.raises(FileNotFoundError):
        solvable_issues.main([])

    (tmp_path / "issues.json").write_text("not json")
    with pytest.raises(json.JSONDecodeError):
        solvable_issues.main([])

    (tmp_path / "issues.json").write_text("[]")
    (tmp_path / "prs.json").write_text("not json")
    with pytest.raises(json.JSONDecodeError):
        solvable_issues.main([])
    capsys.readouterr()

    (tmp_path / "prs.json").write_text("[]\n[]\n")
    pull = dict(opted_in(7), pull_request={"url": "https://api.github.com/repos/o/n/pulls/7"})
    (tmp_path / "issues.json").write_text(json.dumps([opted_in(5)]) + "\n" + json.dumps([opted_in(5), pull, opted_in(6)]) + "\n")
    code = solvable_issues.main([])
    out, err = capsys.readouterr()
    assert (code, out) == (0, "5\n5\n6\n")
