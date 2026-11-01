"""In-process cases for veri/invisible_work.py, the module invisible-work.sh is a shim over."""
import importlib
import json
import os
import pathlib
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
    assert unreachable_out.err.splitlines()[-1] == "invisible-work.sh: cannot reach origin"
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


def test_main_exits_2_never_1_after_reaching_gh_when_its_rest_call_fails_with_a_network_error_a_404_or_a_5xx_under_a_gh_that_refuses_graphql(
        monkeypatch, run_cli, fake_processes):
    invisible_work = importlib.import_module("veri.invisible_work")
    monkeypatch.delenv("VERI_GH_JSON", raising=False)
    monkeypatch.delenv("VERI_GH_DRIVER", raising=False)
    refusal = "HTTP 403: GitHub GraphQL is not available from Claude Code sessions; use the REST API"
    exits = []

    for failure in ("error connecting to api.github.com",
                    "HTTP 404: Not Found (https://api.github.com/repos/o/r/issues/7)",
                    "HTTP 502: Bad Gateway"):
        def answer(line, failure=failure, **_):
            if not line.startswith("gh "):
                return 0, "", ""
            graphql = line.split()[1] in ("issue", "pr", "repo") or line.startswith("gh api graphql")
            return 1, "", refusal if graphql else failure

        calls = fake_processes(answer)
        code, out, _ = run_cli(invisible_work, [])
        exits.append((failure, code, out, any(line.startswith("gh api repos/") for line in calls)))

    assert exits == [(failure, 2, "", True) for failure in (
        "error connecting to api.github.com",
        "HTTP 404: Not Found (https://api.github.com/repos/o/r/issues/7)",
        "HTTP 502: Bad Gateway")]


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


def origin_answer(remote, ahead, local, worktrees=""):
    """A fake_processes answer for a repository whose origin/main is the default branch:
    <remote> maps origin's branches to tips, <ahead> each to its count ahead of origin/main,
    <local> each local branch to (tip, count origin lacks); <worktrees> is the porcelain list."""
    def answer(line, **_):
        words = line.split(" ")
        if words[:2] == ["git", "symbolic-ref"]:
            return 0, "origin/main\n", ""
        if words[:2] == ["git", "for-each-ref"] and words[-1] == "refs/remotes/origin/":
            return 0, "".join(f"refs/remotes/origin/{n} {t}\n" for n, t in sorted(remote.items())), ""
        if words[:2] == ["git", "for-each-ref"] and words[-1] == "refs/heads/":
            return 0, "".join(f"refs/heads/{n} {t}\n" for n, (t, _) in sorted(local.items())), ""
        if words[:3] == ["git", "worktree", "list"]:
            return 0, worktrees, ""
        if words[:3] == ["git", "rev-list", "--count"] and words[3].startswith("origin/main.."):
            return 0, f"{ahead[words[3].removeprefix('origin/main..refs/remotes/origin/')]}\n", ""
        if words[:3] == ["git", "rev-list", "--count"]:
            return 0, f"{local[words[3].removeprefix('refs/heads/')][1]}\n", ""
        if words[:2] == ["git", "show-ref"]:
            return (0 if words[-1].removeprefix("refs/remotes/origin/") in remote else 1), "", ""
        return 0, "", ""

    return answer


def test_main_reports_the_branches_on_origin_with_no_pr_and_the_local_branches_origin_lacks_and_leaves_out_the_rest(
        monkeypatch, tmp_path, run_cli, fake_processes):
    invisible_work = importlib.import_module("veri.invisible_work")
    monkeypatch.delenv("VERI_GH_DRIVER", raising=False)
    (tmp_path / "issues.json").write_text(
        '[{"number": 71, "title": "dashboard: version the commentary too", "labels": [],'
        ' "body": "", "state": "OPEN"}]')
    (tmp_path / "prs.json").write_text(
        '[{"headRefName": "tdd/72-a-run-whose-pr-is-open", "state": "OPEN", "body": "Closes #72"},'
        ' {"headRefName": "chore/pushed-already", "state": "OPEN", "body": ""},'
        ' {"headRefName": "tdd/4-supervised-leaves", "state": "MERGED", "body": "Closes #4"},'
        ' {"headRefName": "chore/test-runner", "state": "CLOSED", "body": ""},'
        ' {"headRefName": "tdd/5-merged-and-pruned", "state": "MERGED", "body": "Closes #5"},'
        ' {"headRefName": "chore/closed-and-pruned", "state": "CLOSED", "body": ""},'
        ' {"headRefName": "tdd/150-a-run-whose-pr-is-still-open", "state": "OPEN", "body": "Closes #150"}]')
    remote = {
        "HEAD": "1111", "main": "1111",
        "tdd/71-dashboard-version-the-commentary-too": "a71a", "tdd/999-an-issue-nobody-filed": "a999",
        "chore/nobody-opened-a-pr": "bbbb", "tdd/72-a-run-whose-pr-is-open": "a72a",
        "chore/pushed-already": "cccc", "tdd/4-supervised-leaves": "a4a4", "chore/test-runner": "dddd",
    }
    ahead = {"tdd/71-dashboard-version-the-commentary-too": 3, "tdd/999-an-issue-nobody-filed": 3,
             "chore/nobody-opened-a-pr": 1, "tdd/72-a-run-whose-pr-is-open": 2,
             "chore/pushed-already": 1, "tdd/4-supervised-leaves": 2, "chore/test-runner": 1}
    local = {
        "main": ("1111", 0), "chore/pushed-already": ("cccc", 0),
        "tdd/150-a-run-that-never-reached-origin": ("e150", 4), "tdd/170-a-run-checked-out-nowhere": ("e170", 1),
        "tdd/5-merged-and-pruned": ("e005", 2), "chore/closed-and-pruned": ("eeee", 1),
        "tdd/150-a-run-whose-pr-is-still-open": ("f150", 1),
    }

    calls = fake_processes(origin_answer(
        remote, ahead, local,
        "worktree /repo\nHEAD 1111\nbranch refs/heads/main\n\n"
        "worktree /wt/wt-150\nHEAD e150\nbranch refs/heads/tdd/150-a-run-that-never-reached-origin\n\n"))
    code, out, err = run_cli(invisible_work, [], env={"VERI_GH_JSON": str(tmp_path)})

    assert (code, out, err) == (
        0,
        "invariant 2 (no PR): chore/nobody-opened-a-pr tip bbbb 1 commits ahead\n"
        "invariant 2 (no PR): tdd/71-dashboard-version-the-commentary-too tip a71a 3 commits ahead,"
        " issue #71 OPEN\n"
        "invariant 2 (no PR): tdd/999-an-issue-nobody-filed tip a999 3 commits ahead, issue #999 unknown\n"
        "invariant 1 (not on origin): tdd/150-a-run-that-never-reached-origin tip e150"
        " 4 commits origin lacks, worktree /wt/wt-150\n"
        "invariant 1 (not on origin): tdd/150-a-run-whose-pr-is-still-open tip f150 1 commits origin lacks\n"
        "invariant 1 (not on origin): tdd/170-a-run-checked-out-nowhere tip e170 1 commits origin lacks\n",
        "")
    assert [line for line in calls if line.startswith("gh")] == []


def test_main_exits_2_with_empty_stdout_when_the_veri_gh_json_issues_json_is_not_json(
        monkeypatch, tmp_path, run_cli, fake_processes):
    invisible_work = importlib.import_module("veri.invisible_work")
    monkeypatch.delenv("VERI_GH_DRIVER", raising=False)
    (tmp_path / "issues.json").write_text("this is not JSON\n")
    (tmp_path / "prs.json").write_text("[]\n")

    fake_processes(origin_answer(
        {"HEAD": "1111", "main": "1111", "chore/nobody-opened-a-pr": "bbbb"},
        {"chore/nobody-opened-a-pr": 1}, {"main": ("1111", 0)}))
    code, out, _ = run_cli(invisible_work, [], env={"VERI_GH_JSON": str(tmp_path)})

    assert (code, out) == (2, "")


def test_main_prints_the_same_report_and_exit_code_over_three_rest_pages_with_repositories_id_refused_as_over_a_single_page_fixture(
        monkeypatch, tmp_path, run_cli, fake_processes):
    invisible_work = importlib.import_module("veri.invisible_work")
    monkeypatch.delenv("VERI_GH_DRIVER", raising=False)
    proxy = ("gh: Numeric-ID repository paths (repositories/{id}/...) are not supported through"
             " this proxy. Use repos/{owner}/{repo}/... endpoints instead. (HTTP 403)")
    late = "tdd/75-an-issue-on-the-last-page"
    opened = "chore/a-pr-on-the-last-page"
    closed = "chore/closed-on-page-two"

    def issue(number, state):
        return {"number": number, "title": "t", "labels": [], "body": "", "state": state}

    def pull(number, state, ref):
        return {"number": number, "state": state, "merged_at": None, "body": "", "head": {"ref": ref}}

    issue_pages = [[issue(70, "closed"), issue(71, "open")], [issue(72, "closed"), issue(73, "open")],
                   [issue(74, "closed"), issue(75, "open")]]
    pull_pages = [[pull(1, "closed", "chore/one"), pull(2, "open", "chore/two")],
                  [pull(3, "closed", closed), pull(4, "open", "chore/four")],
                  [pull(5, "open", opened), pull(6, "closed", "chore/six")]]
    remote = {"HEAD": "1111", "main": "1111", late: "a75a", opened: "bbbb", closed: "cccc"}
    ahead = {late: 2, opened: 1, closed: 1}
    git_answer = origin_answer(remote, ahead, {"main": ("1111", 0)})

    def serve(issues, pulls):
        def answer(line, **kwargs):
            words = line.split(" ")
            if words[0] != "gh":
                return git_answer(line, **kwargs)
            path = words[-1]
            if words[1] != "api" or "repositories/" in path:
                return 1, "", proxy
            pages = issues if "/issues?" in path else pulls
            page = int(path.rsplit("page=", 1)[1])
            body = json.dumps(pages[page - 1]) if page <= len(pages) else "[]"
            return 0, body + "\n", ""
        return answer

    fake_processes(serve(issue_pages, pull_pages))
    three = run_cli(invisible_work, [])
    flat = lambda pages: [[item for page in pages for item in page]]
    fake_processes(serve(flat(issue_pages), flat(pull_pages)))
    one = run_cli(invisible_work, [])

    want = f"invariant 2 (no PR): {late} tip a75a 2 commits ahead, issue #75 OPEN\n"
    assert one == (0, want, "")
    assert three == one


def test_main_prints_the_same_report_and_exit_code_for_issue_and_pr_documents_over_256_kib_as_for_small_ones(
        monkeypatch, tmp_path, run_cli, fake_processes):
    invisible_work = importlib.import_module("veri.invisible_work")
    monkeypatch.delenv("VERI_GH_DRIVER", raising=False)

    def write(directory, pad):
        directory.mkdir()
        (directory / "issues.json").write_text(json.dumps(
            [{"number": n, "title": f"issue {n}", "labels": [], "state": "OPEN", "body": pad}
             for n in range(40, 80)]))
        (directory / "prs.json").write_text(json.dumps(
            [{"headRefName": f"tdd/{n}-other", "state": "MERGED", "body": pad}
             for n in range(100, 140)]))
        return directory

    short = write(tmp_path / "short", "short")
    long = write(tmp_path / "long", "x" * 8192)
    fake_processes(origin_answer(
        {"HEAD": "1111", "main": "1111", "tdd/71-version-the-commentary": "a71a"},
        {"tdd/71-version-the-commentary": 2}, {"main": ("1111", 0)}))

    small = run_cli(invisible_work, [], env={"VERI_GH_JSON": str(short)})
    large = run_cli(invisible_work, [], env={"VERI_GH_JSON": str(long)})

    assert [(long / doc).stat().st_size > 262144 for doc in ("issues.json", "prs.json")] == [True, True]
    assert small == (
        0, "invariant 2 (no PR): tdd/71-version-the-commentary tip a71a 2 commits ahead, issue #71 OPEN\n", "")
    assert large == small


def run_git(repo, *args):
    done = subprocess.run(
        ["git", "-C", str(repo), "-c", "user.name=veri", "-c", "user.email=veri@example.test", *args],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, check=True)
    return done.stdout


def ref_state(clone, origin):
    return (run_git(clone, "for-each-ref", "--format=clone %(refname) %(objectname) %(symref)")
            + run_git(clone, "worktree", "list", "--porcelain")
            + run_git(origin, "for-each-ref", "--format=origin %(refname) %(objectname) %(symref)")
            + "origin HEAD " + run_git(origin, "symbolic-ref", "HEAD"))


def seed_origin(src, origin):
    subprocess.run(["git", "init", "-q", "-b", "main", str(src)], check=True)
    run_git(src, "commit", "-q", "--allow-empty", "-m", "initial")
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(origin)], check=True)
    run_git(src, "remote", "add", "origin", str(origin))
    run_git(src, "push", "-q", "-u", "origin", "main")


@pytest.mark.process("real git: a clone, its origin and a linked worktree, whose refs are read before and after the run")
def test_main_writes_to_no_ref_so_the_refs_of_the_clone_and_of_origin_are_byte_identical_after_a_run(
        run_cli, tmp_path):
    invisible_work = importlib.import_module("veri.invisible_work")
    src, origin, clone = tmp_path / "src", tmp_path / "origin.git", tmp_path / "clone"
    seed_origin(src, origin)
    for branch in ("chore/nobody-opened-a-pr", "tdd/4-supervised-leaves", "chore/deleted-on-origin"):
        run_git(src, "checkout", "-q", "-b", branch, "main")
        run_git(src, "commit", "-q", "--allow-empty", "-m", "chore: work with no PR")
        run_git(src, "push", "-q", "origin", branch)
    subprocess.run(["git", "clone", "-q", str(origin), str(clone)], check=True)
    run_git(clone, "branch", "-q", "tdd/4-supervised-leaves", "origin/tdd/4-supervised-leaves")
    run_git(clone, "tag", "-a", "-m", "v0.1", "v0.1", "origin/main")
    run_git(clone, "worktree", "add", "-q", "-b", "tdd/150-never-pushed", str(tmp_path / "wt-150"), "origin/main")
    run_git(tmp_path / "wt-150", "commit", "-q", "--allow-empty", "-m", "feat: a step nobody pushed (#150)")
    run_git(src, "push", "-q", "origin", "--delete", "chore/deleted-on-origin")
    run_git(src, "checkout", "-q", "-b", "chore/pushed-after-the-fetch", "main")
    run_git(src, "commit", "-q", "--allow-empty", "-m", "chore: work the clone has not fetched")
    run_git(src, "push", "-q", "origin", "chore/pushed-after-the-fetch")
    (tmp_path / "gh").mkdir()
    (tmp_path / "gh" / "issues.json").write_text("[]\n")
    (tmp_path / "gh" / "prs.json").write_text(
        '[{"headRefName": "tdd/4-supervised-leaves", "state": "MERGED", "body": "Closes #4"}]\n')

    before = ref_state(clone, origin)
    code, out, _ = run_cli(invisible_work, [], env={"VERI_GH_JSON": str(tmp_path / "gh")}, cwd=clone)
    after = ref_state(clone, origin)

    assert code == 0
    assert "chore/nobody-opened-a-pr" in out and "tdd/150-never-pushed" in out
    assert after == before


def unpr_clone(tmp_path, branch, ahead):
    src, origin, clone = tmp_path / "src", tmp_path / "origin.git", tmp_path / "clone"
    seed_origin(src, origin)
    run_git(src, "checkout", "-q", "-b", branch)
    for i in range(1, ahead + 1):
        run_git(src, "commit", "-q", "--allow-empty", "-m", f"feat: step {i} of a run nobody can see (#71)")
    run_git(src, "push", "-q", "origin", branch)
    subprocess.run(["git", "clone", "-q", str(origin), str(clone)], check=True)
    gh = tmp_path / "gh"
    gh.mkdir()
    (gh / "issues.json").write_text(
        '[{"number": 71, "title": "dashboard: version the commentary too", "labels": [], "body": "", "state": "OPEN"}]\n')
    (gh / "prs.json").write_text("[]\n")
    return clone, origin, gh


@pytest.mark.process("invisible-work.sh run through a symlink to the skill directory from a subdirectory of a real clone")
def test_main_prints_the_same_report_stderr_and_exit_code_through_a_symlink_to_the_skill_directory_from_a_subdirectory_as_in_place(
        run_cli, tmp_path):
    invisible_work = importlib.import_module("veri.invisible_work")
    local_only = "tdd/150-a-run-that-never-reached-origin"
    clone, _, gh = unpr_clone(tmp_path, "tdd/71-dashboard-version-the-commentary-too", 2)
    run_git(clone, "checkout", "-q", "-b", local_only, "main")
    run_git(clone, "commit", "-q", "--allow-empty", "-m", "feat: a step nobody pushed (#150)")
    run_git(clone, "checkout", "-q", "main")
    (clone / "sub" / "dir").mkdir(parents=True)
    (tmp_path / "linked-skill").symlink_to(
        pathlib.Path(invisible_work.__file__).resolve().parents[2], target_is_directory=True)

    in_place = run_cli(invisible_work, [], env={"VERI_GH_JSON": str(gh)}, cwd=clone)
    linked = subprocess.run([str(tmp_path / "linked-skill" / "scripts" / "invisible-work.sh")],
                            cwd=clone / "sub" / "dir", env={**os.environ, "VERI_GH_JSON": str(gh)},
                            stdin=subprocess.DEVNULL, capture_output=True, text=True)

    assert in_place[0] == 0 and local_only in in_place[1]
    assert (linked.returncode, linked.stdout, linked.stderr) == in_place


@pytest.mark.process("real git: a clone whose refs/remotes/origin/HEAD is deleted, resolved from its origin")
def test_main_prints_the_same_report_and_exit_code_with_no_origin_head_ref_as_when_it_is_set(run_cli, tmp_path):
    invisible_work = importlib.import_module("veri.invisible_work")
    branch = "tdd/71-dashboard-version-the-commentary-too"
    clone, _, gh = unpr_clone(tmp_path, branch, 3)

    set_code, set_out, set_err = run_cli(invisible_work, [], env={"VERI_GH_JSON": str(gh)}, cwd=clone)
    run_git(clone, "config", "remote.origin.followRemoteHEAD", "never")
    run_git(clone, "symbolic-ref", "--delete", "refs/remotes/origin/HEAD")
    unset_code, unset_out, unset_err = run_cli(invisible_work, [], env={"VERI_GH_JSON": str(gh)}, cwd=clone)

    assert (set_code, branch in set_out) == (0, True), set_err
    assert (unset_code, unset_out) == (set_code, set_out), unset_err


@pytest.mark.process("real git: a clone with no refs/remotes/origin/HEAD whose origin's HEAD is detached")
def test_main_exits_2_naming_refs_remotes_origin_head_when_neither_the_ref_nor_the_remote_names_a_default(
        run_cli, tmp_path):
    invisible_work = importlib.import_module("veri.invisible_work")
    clone, origin, gh = unpr_clone(tmp_path, "tdd/71-dashboard-version-the-commentary-too", 1)
    run_git(clone, "config", "remote.origin.followRemoteHEAD", "never")
    run_git(clone, "symbolic-ref", "--delete", "refs/remotes/origin/HEAD")
    run_git(origin, "update-ref", "--no-deref", "HEAD", run_git(origin, "rev-parse", "refs/heads/main").strip())

    code, out, err = run_cli(invisible_work, [], env={"VERI_GH_JSON": str(gh)}, cwd=clone)

    assert code == 2, (out, err)
    assert "refs/remotes/origin/HEAD" in err
