"""In-process cases for veri/invisible_work.py, the module invisible-work.sh is a shim over."""
import importlib
import os
import pathlib
import subprocess
import sys

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


def fake_processes(monkeypatch, answer):
    """subprocess.run recording each command as one line, its program by basename;
    <answer>(line) -> exit code, with empty output."""
    calls = []

    def fake_run(args, **kwargs):
        line = " ".join([os.path.basename(str(args[0]))] + [str(a) for a in args[1:]])
        calls.append(line)
        code = answer(line)
        if kwargs.get("check") and code != 0:
            raise subprocess.CalledProcessError(code, args, "", "")
        empty = "" if kwargs.get("text") or kwargs.get("encoding") or kwargs.get("universal_newlines") else b""
        return subprocess.CompletedProcess(args, code, empty, empty)

    monkeypatch.setattr(subprocess, "run", fake_run)
    return calls


def test_main_returns_2_with_empty_stdout_when_origin_is_unreachable_or_origin_head_is_unset(
        monkeypatch, tmp_path, capsys):
    invisible_work = importlib.import_module("veri.invisible_work")
    (tmp_path / "issues.json").write_text("[]")
    (tmp_path / "prs.json").write_text("[]")

    monkeypatch.delenv("VERI_GH_JSON", raising=False)
    unreachable_calls = fake_processes(
        monkeypatch, lambda line: 128 if line.startswith("git ls-remote --heads origin") else 0)
    unreachable = invisible_work.main([])
    unreachable_out = capsys.readouterr()

    monkeypatch.setenv("VERI_GH_JSON", str(tmp_path))
    fake_processes(
        monkeypatch,
        lambda line: 128 if line.startswith("git symbolic-ref --short refs/remotes/origin/HEAD") else 0)
    unset_head = invisible_work.main([])
    unset_head_out = capsys.readouterr()

    assert (unreachable, unreachable_out.out, unset_head, unset_head_out.out) == (2, "", 2, "")
    assert unreachable_out.err.endswith("invisible-work.sh: cannot reach origin\n")
    assert [line for line in unreachable_calls if line.startswith("gh")] == []


def fake_git(monkeypatch, answers):
    """subprocess.run answering each git command from <answers>, a list of
    (words the command line holds, exit code, stdout); an unlisted command exits 0 silently."""
    def fake_run(args, **kwargs):
        line = " ".join([os.path.basename(str(args[0]))] + [str(a) for a in args[1:]])
        code, out = 0, ""
        for words, answer_code, answer_out in answers:
            if all(word in line.split(" ") for word in words):
                code, out = answer_code, answer_out
                break
        if kwargs.get("check") and code != 0:
            raise subprocess.CalledProcessError(code, args, out, "")
        text = kwargs.get("text") or kwargs.get("encoding") or kwargs.get("universal_newlines")
        return subprocess.CompletedProcess(args, code, out if text else out.encode(), "" if text else b"")

    monkeypatch.setattr(subprocess, "run", fake_run)


def sweep_answers(remotes, locals_):
    return [
        (["ls-remote"], 0, ""),
        (["symbolic-ref"], 0, "origin/main\n"),
        (["for-each-ref", "refs/remotes/origin/"], 0, remotes),
        (["for-each-ref", "refs/heads/"], 0, locals_),
        (["worktree", "list", "--porcelain"], 0,
         "worktree /repo\nHEAD 1111\nbranch refs/heads/main\n\n"
         "worktree /wt/with space \t\nHEAD cccc\nbranch refs/heads/feature\n\n"),
        (["rev-list", "--count", "origin/main..refs/remotes/origin/tdd/007-x"], 0, "2\n"),
        (["rev-list", "--count", "origin/main..refs/remotes/origin/zeta"], 0, "1\n"),
        (["rev-list", "--count", "refs/heads/feature"], 0, "3\n"),
        (["rev-list", "--count", "refs/heads/solo"], 0, "4\n"),
        (["show-ref", "refs/remotes/origin/main"], 0, ""),
        (["show-ref", "refs/remotes/origin/tdd/007-x"], 0, ""),
        (["show-ref"], 1, ""),
    ]


def test_main_prints_remote_findings_then_local_findings_and_returns_3_when_there_are_none(
        monkeypatch, tmp_path, capsys):
    invisible_work = importlib.import_module("veri.invisible_work")
    (tmp_path / "issues.json").write_text('[{"number": 7, "state": "open"}]')
    (tmp_path / "prs.json").write_text("[]")
    monkeypatch.setenv("VERI_GH_JSON", str(tmp_path))

    fake_git(monkeypatch, sweep_answers(
        "refs/remotes/origin/HEAD 1111\nrefs/remotes/origin/main 1111\n"
        "refs/remotes/origin/tdd/007-x aaaa\nrefs/remotes/origin/zeta bbbb\n",
        "refs/heads/feature cccc\nrefs/heads/main 1111\n"
        "refs/heads/solo dddd\nrefs/heads/tdd/007-x aaaa\n"))
    found = invisible_work.main([])
    found_out = capsys.readouterr()

    fake_git(monkeypatch, sweep_answers(
        "refs/remotes/origin/HEAD 1111\nrefs/remotes/origin/main 1111\n",
        "refs/heads/main 1111\n"))
    nothing = invisible_work.main([])
    nothing_out = capsys.readouterr()

    assert (found, found_out.out, nothing, nothing_out.out) == (
        0,
        "invariant 2 (no PR): tdd/007-x tip aaaa 2 commits ahead, issue #7 OPEN\n"
        "invariant 2 (no PR): zeta tip bbbb 1 commits ahead\n"
        "invariant 1 (not on origin): feature tip cccc 3 commits origin lacks, worktree /wt/with space\n"
        "invariant 1 (not on origin): solo tip dddd 4 commits origin lacks\n",
        3,
        "")


def test_main_returns_2_with_the_gh_diagnostic_when_a_veri_gh_json_fixture_is_missing(
        monkeypatch, tmp_path, capsys):
    invisible_work = importlib.import_module("veri.invisible_work")
    (tmp_path / "prs.json").write_text("[]")
    monkeypatch.setenv("VERI_GH_JSON", str(tmp_path))
    calls = fake_processes(monkeypatch, lambda line: 0)

    code = invisible_work.main([])
    out = capsys.readouterr()

    assert (code, out.out) == (2, "")
    assert out.err.endswith(
        "invisible-work.sh: cannot read issues and PRs from gh (unauthenticated?)\n")
    assert [line for line in calls if line.startswith("gh")] == []
