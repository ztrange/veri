"""In-process cases for veri/invisible_work.py, the module invisible-work.sh is a shim over."""
import importlib
import os
import subprocess
import sys

import pytest


def test_main_returns_2_with_empty_stdout_when_origin_is_unreachable_or_origin_head_is_unset(
        monkeypatch, tmp_path, capsys, fake_processes):
    invisible_work = importlib.import_module("veri.invisible_work")
    (tmp_path / "issues.json").write_text("[]")
    (tmp_path / "prs.json").write_text("[]")

    monkeypatch.delenv("VERI_GH_JSON", raising=False)
    unreachable_calls = fake_processes(
        lambda line, **_: (128 if line.startswith("git ls-remote --heads origin") else 0, "", ""))
    unreachable = invisible_work.main([])
    unreachable_out = capsys.readouterr()

    monkeypatch.setenv("VERI_GH_JSON", str(tmp_path))
    fake_processes(
        lambda line, **_: (128 if line.startswith("git symbolic-ref --short refs/remotes/origin/HEAD") else 0, "", ""))
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
        monkeypatch, tmp_path, capsys, fake_processes):
    invisible_work = importlib.import_module("veri.invisible_work")
    (tmp_path / "prs.json").write_text("[]")
    monkeypatch.setenv("VERI_GH_JSON", str(tmp_path))
    calls = fake_processes(lambda line, **_: (0, "", ""))

    code = invisible_work.main([])
    out = capsys.readouterr()

    assert (code, out.out) == (2, "")
    assert out.err.endswith(
        "invisible-work.sh: cannot read issues and PRs from gh (unauthenticated?)\n")
    assert [line for line in calls if line.startswith("gh")] == []


def test_main_reads_issues_and_prs_from_veri_gh_json_or_from_gh_list_falling_back_to_rest_pages(
        monkeypatch, tmp_path, capsys):
    monkeypatch.setenv("VERI_GH_DRIVER", "auto")
    invisible_work = importlib.import_module("veri.invisible_work")
    issues_rest = "repos/{owner}/{repo}/issues?state=all&per_page=100&page="
    pulls_rest = "repos/{owner}/{repo}/pulls?state=all&per_page=100&page="
    issue_list = ["gh", "issue", "list", "--state", "all", "--limit", "10000", "--json", "number,state"]
    pr_list = ["gh", "pr", "list", "--state", "all", "--limit", "10000", "--json", "headRefName,state"]
    git_answers = sweep_answers(
        "refs/remotes/origin/HEAD 1111\nrefs/remotes/origin/main 1111\n"
        "refs/remotes/origin/tdd/007-x aaaa\n",
        "refs/heads/main 1111\n")

    def fake_subprocess(gh_answers):
        calls = []

        def fake_run(args, **kwargs):
            args = [str(a) for a in args]
            line = " ".join([os.path.basename(args[0])] + args[1:])
            if os.path.basename(args[0]) == "gh":
                calls.append(["gh"] + args[1:])
                code, out = gh_answers.get(tuple(args[1:]), (0, ""))
            else:
                code, out = 0, ""
                for words, answer_code, answer_out in git_answers:
                    if all(word in line.split(" ") for word in words):
                        code, out = answer_code, answer_out
                        break
            text = kwargs.get("text") or kwargs.get("encoding") or kwargs.get("universal_newlines")
            return subprocess.CompletedProcess(args, code, out if text else out.encode(),
                                               "" if text else b"")

        monkeypatch.setattr(subprocess, "run", fake_run)
        return calls

    (tmp_path / "issues.json").write_text('[{"number": 7, "state": "OPEN"}]')
    (tmp_path / "prs.json").write_text("[]")
    monkeypatch.setenv("VERI_GH_JSON", str(tmp_path))
    fixture_calls = fake_subprocess({})
    fixture = invisible_work.main([])
    fixture_out = capsys.readouterr()

    monkeypatch.delenv("VERI_GH_JSON")
    rest_calls = fake_subprocess({
        tuple(issue_list[1:]): (1, ""),
        ("api", issues_rest + "1"): (0, "[]\n"),
        tuple(pr_list[1:]): (1, ""),
        ("api", pulls_rest + "1"): (0, '[{"head": {"ref": "other"}, "state": "open"}]\n'),
        ("api", pulls_rest + "2"): (0, "[]\n"),
    })
    rest = invisible_work.main([])
    rest_out = capsys.readouterr()

    monkeypatch.setenv("VERI_GH_JSON", "")
    failing_calls = fake_subprocess({
        tuple(issue_list[1:]): (1, ""),
        ("api", issues_rest + "1"): (1, ""),
    })
    failing = invisible_work.main([])
    failing_out = capsys.readouterr()

    assert (fixture, fixture_out.out, fixture_calls) == (
        0, "invariant 2 (no PR): tdd/007-x tip aaaa 2 commits ahead, issue #7 OPEN\n", [])
    assert (rest, rest_out.out, rest_calls) == (
        0,
        "invariant 2 (no PR): tdd/007-x tip aaaa 2 commits ahead, issue #7 unknown\n",
        [issue_list, ["gh", "api", issues_rest + "1"],
         pr_list, ["gh", "api", pulls_rest + "1"], ["gh", "api", pulls_rest + "2"]])
    assert (failing, failing_out.out, failing_calls) == (
        2, "", [issue_list, ["gh", "api", issues_rest + "1"]])
    assert failing_out.err.endswith(
        "invisible-work.sh: cannot read issues and PRs from gh (unauthenticated?)\n")


def test_main_keeps_the_report_rules_of_the_embedded_program_and_raises_on_a_malformed_answer(
        monkeypatch, tmp_path, capsys):
    invisible_work = importlib.import_module("veri.invisible_work")
    monkeypatch.setenv("VERI_GH_JSON", str(tmp_path))
    fake_git(monkeypatch, [
        (["rev-list", "--count", "origin/main..refs/remotes/origin/closed-pr"], 0, "5\n"),
        (["rev-list", "--count", "origin/main..refs/remotes/origin/merged-pr"], 0, "6\n"),
        (["rev-list", "--count", "refs/heads/done"], 0, "7\n"),
        (["rev-list", "--count", "refs/heads/gone"], 0, "8\n"),
    ] + sweep_answers(
        "refs/remotes/origin/HEAD 1111\nrefs/remotes/origin/closed-pr eeee\n"
        "refs/remotes/origin/main 1111\nrefs/remotes/origin/merged-pr ffff\n"
        "refs/remotes/origin/tdd/007-x aaaa\nrefs/remotes/origin/zeta bbbb\n",
        "refs/heads/done 9999\nrefs/heads/feature cccc\nrefs/heads/gone 8888\n"
        "refs/heads/main 1111\nrefs/heads/solo dddd\nrefs/heads/tdd/007-x aaaa\n"))

    (tmp_path / "issues.json").write_text('[{"number": 7, "state": "closed"}]')
    (tmp_path / "prs.json").write_text(
        '[{"head": {"ref": "closed-pr"}, "state": "closed"},'
        ' {"headRefName": "merged-pr", "state": "MERGED"},'
        ' {"head": {"ref": "done"}, "state": "closed"},'
        ' {"headRefName": "gone", "state": "MERGED"}]')
    swept = invisible_work.main(["--help"])
    swept_out = capsys.readouterr()

    assert (swept, swept_out.out) == (
        0,
        "invariant 2 (no PR): tdd/007-x tip aaaa 2 commits ahead, issue #7 CLOSED\n"
        "invariant 2 (no PR): zeta tip bbbb 1 commits ahead\n"
        "invariant 1 (not on origin): feature tip cccc 3 commits origin lacks, worktree /wt/with space\n"
        "invariant 1 (not on origin): solo tip dddd 4 commits origin lacks\n")

    malformed = [
        ("not json", "[]"),
        ('[{"number": 7}]', "[]"),
        ("[]", '{"headRefName": "zeta", "state": "OPEN"}'),
    ]
    for issues, prs in malformed:
        (tmp_path / "issues.json").write_text(issues)
        (tmp_path / "prs.json").write_text(prs)
        with pytest.raises(Exception):
            invisible_work.main([])


def fake_git_passing_stderr(monkeypatch, answers):
    """fake_git, with each answer also carrying git's stderr, written to sys.stderr unless the
    caller redirected it: a list of (words the command line holds, exit code, stdout, stderr)."""
    def fake_run(args, **kwargs):
        line = " ".join([os.path.basename(str(args[0]))] + [str(a) for a in args[1:]])
        code, out, err = 0, "", ""
        for words, answer_code, answer_out, answer_err in answers:
            if all(word in line.split(" ") for word in words):
                code, out, err = answer_code, answer_out, answer_err
                break
        if "stderr" not in kwargs:
            sys.stderr.write(err)
        text = kwargs.get("text") or kwargs.get("encoding") or kwargs.get("universal_newlines")
        return subprocess.CompletedProcess(args, code, out if text else out.encode(), "" if text else b"")

    monkeypatch.setattr(subprocess, "run", fake_run)


def test_main_resolves_the_default_branch_from_each_ls_remote_shape_when_origin_head_is_unset(
        monkeypatch, tmp_path, capsys):
    invisible_work = importlib.import_module("veri.invisible_work")
    (tmp_path / "issues.json").write_text("[]")
    (tmp_path / "prs.json").write_text("[]")
    monkeypatch.setenv("VERI_GH_JSON", str(tmp_path))

    def answers(symref_code, symref_out, symref_err):
        return [
            (["ls-remote", "--symref", "origin", "HEAD"], symref_code, symref_out, symref_err),
            (["ls-remote", "--heads", "origin"], 0, "", ""),
            (["symbolic-ref", "--short", "refs/remotes/origin/HEAD"], 128, "",
             "fatal: ref refs/remotes/origin/HEAD is not a symbolic ref\n"),
            (["for-each-ref", "refs/remotes/origin/"], 0,
             "refs/remotes/origin/trunk 1111\nrefs/remotes/origin/zeta bbbb\n", ""),
            (["for-each-ref", "refs/heads/"], 0, "refs/heads/trunk 1111\n", ""),
            (["rev-list", "--count", "origin/trunk..refs/remotes/origin/zeta"], 0, "1\n", ""),
            (["show-ref", "refs/remotes/origin/trunk"], 0, "", ""),
            (["show-ref"], 1, "", ""),
        ]

    fake_git_passing_stderr(monkeypatch, answers(
        0, "ref: refs/heads/trunk\tHEAD\n1111111111111111111111111111111111111111\tHEAD\n", ""))
    symref = invisible_work.main([])
    symref_out = capsys.readouterr()

    fake_git_passing_stderr(monkeypatch, answers(
        0, "1111111111111111111111111111111111111111\tHEAD\n", ""))
    no_symref = invisible_work.main([])
    no_symref_out = capsys.readouterr()

    fake_git_passing_stderr(monkeypatch, answers(
        128, "", "fatal: unable to access 'https://example.invalid/repo.git/': Could not resolve host\n"))
    unreachable = invisible_work.main([])
    unreachable_out = capsys.readouterr()

    assert (symref, symref_out.out, symref_out.err) == (
        0, "invariant 2 (no PR): zeta tip bbbb 1 commits ahead\n", "")
    assert (no_symref, no_symref_out.out, no_symref_out.err) == (
        2, "",
        "invisible-work.sh: no refs/remotes/origin/HEAD and origin names no default branch\n")
    assert (unreachable, unreachable_out.out, unreachable_out.err) == (
        2, "",
        "fatal: unable to access 'https://example.invalid/repo.git/': Could not resolve host\n"
        "invisible-work.sh: no refs/remotes/origin/HEAD and origin names no default branch\n")
