"""In-process cases for veri/solvable_issues.py, the module solvable-issues.sh is a shim over."""
import errno
import importlib
import itertools
import json
import os
import pathlib
import re
import subprocess
import tempfile

import pytest

from conftest import fake_pid_file_ps
from test_run_conductor import fake_claude_exiting, past_the_guards, scratch_tmpdir

USAGE = "usage: solvable-issues.sh [--repo owner/name] [--not-running]\n"


@pytest.fixture(autouse=True)
def no_ambient_tunables(monkeypatch):
    for name in ("VERI_GH_JSON", "VERI_LABEL", "VERI_PRIORITY_LABEL"):
        monkeypatch.delenv(name, raising=False)


def conducting(monkeypatch, *numbers):
    """pid_file's ps answering every pid as a claude under run_conductor.py."""
    fake_pid_file_ps(monkeypatch)


@pytest.fixture
def conductor_process(request):
    """conductor_process(*numbers) starts a real process whose command line names run-conductor.sh <n> for each, returning its pid; killed at the end."""
    started = []

    def start(*numbers):
        claude = pathlib.Path(tempfile.mkdtemp(prefix="exp-claude-")) / "claude"
        claude.symlink_to("/bin/sh")
        parent = subprocess.Popen(["/bin/sh", "-c", 'exec 3<&0; "$1" -c "read x" <&3 3<&- & echo $!; wait', "run_conductor.py", str(claude)],
                                  stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        started.append(parent)
        return int(parent.stdout.readline())

    yield start
    for child in started:
        child.stdin.close()
        child.wait()
        child.stdout.close()


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


@pytest.mark.parametrize("argv", [["--not-running", "--not-running"], ["--repo", "--not-running", "o/n"]])
def test_main_refuses_a_repeated_not_running_or_one_between_repo_and_its_value_with_2_and_the_usage_line_alone_starting_no_process_1909(argv, monkeypatch, capsys, solvable_issues):
    started = no_process(monkeypatch)

    code = solvable_issues.main(argv)

    out, err = capsys.readouterr()
    assert (code, started, out, err) == (2, [], "", USAGE)


@pytest.mark.parametrize("argv", [["foo", "bar"], ["o/n", "--repo"]])
def test_main_refuses_two_words_not_starting_with_repo_with_2_and_the_usage_line_alone_starting_no_process_1909(argv, monkeypatch, capsys, solvable_issues):
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
    conducting(monkeypatch, 5)
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
            ["gh", "api", prefix + "/issues?state=open&per_page=100"],
            ["gh", "pr", "list", "--limit", "10000", "--json", "body,state", *scope],
            ["gh", "api", prefix + "/pulls?state=open&per_page=100"],
        ]

    observed = {}
    for argv in ([], ["--repo", "o/n"]):
        started = fake_gh_refusing_graphql(monkeypatch)
        solvable_issues.main(argv)
        capsys.readouterr()
        observed[tuple(argv)] = started

    assert observed == {
        (): reads(None),
        ("--repo", "o/n"): reads("o/n"),
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


@pytest.mark.parametrize("unreadable", ["issues.json", "prs.json"])
def test_solvable_returns_2_and_no_numbers_when_the_issue_or_pr_listing_is_not_readable_json(unreadable, tmp_path, monkeypatch, solvable_issues):
    fake_git_answering_nothing(monkeypatch)
    monkeypatch.setenv("VERI_GH_JSON", str(tmp_path))
    (tmp_path / "issues.json").write_text(json.dumps([opted_in(5)]))
    (tmp_path / "prs.json").write_text("[]")
    (tmp_path / unreadable).write_text("not json")

    assert solvable_issues.solvable("ready-for-agent") == (2, [])


def test_main_counts_an_issue_open_by_its_upper_cased_state_and_withholds_one_an_open_pr_closes(tmp_path, monkeypatch, capsys, solvable_issues):
    monkeypatch.setenv("VERI_GH_JSON", str(tmp_path))
    fake_git_answering_nothing(monkeypatch)
    stateless = opted_in(2)
    del stateless["state"]
    (tmp_path / "issues.json").write_text(json.dumps([
        dict(opted_in(1), state="open"), stateless, dict(opted_in(3), state="CLOSED"), opted_in(5),
        opted_in(10), opted_in(11), opted_in(12), opted_in(13), opted_in(14), opted_in(50)]))
    (tmp_path / "prs.json").write_text(json.dumps([
        {"state": "open", "body": "Closes #10"},
        {"state": "CLOSED", "body": "Closes #11"},
        {"state": "OPEN", "body": None},
        {"state": "OPEN", "body": "closes #12"},
        {"state": "OPEN", "body": "Fixes #13"},
        {"state": "OPEN", "body": "xCloses #14"},
        {"state": "OPEN", "body": "Closes #50"}]))

    code = solvable_issues.main([])

    out, err = capsys.readouterr()
    assert (code, out) == (0, "1\n5\n11\n12\n13\n14\n")

    (tmp_path / "issues.json").write_text(json.dumps([dict(opted_in(5), state=None)]))
    with pytest.raises(AttributeError):
        solvable_issues.main([])


def blocked_by(number, *refs):
    return dict(opted_in(number), body="## Blocked by\n\n" + "".join("- %s\n" % ref for ref in refs) + "\n## Notes\n\n#1\n")


def test_main_withholds_an_issue_blocked_by_an_open_fetched_issue_as_number_or_url_reading_other_repos_urls_only_under_repo(tmp_path, monkeypatch, capsys, solvable_issues):
    monkeypatch.setenv("VERI_GH_JSON", str(tmp_path))
    fake_git_answering_nothing(monkeypatch)
    (tmp_path / "issues.json").write_text(json.dumps([
        labelled(1, "other"), dict(labelled(2, "other"), state="CLOSED"),
        blocked_by(20, "#1"), blocked_by(21, "https://github.com/o/r/issues/1"), blocked_by(22, "#2"),
        blocked_by(23, "#99"), blocked_by(24, "#40"), blocked_by(25, "https://github.com/x/y/issues/1")]))
    (tmp_path / "prs.json").write_text(json.dumps([{"number": 40, "state": "OPEN", "body": "nothing"}]))

    observed = {}
    for argv in ([], ["--repo", "o/r"]):
        code = solvable_issues.main(argv)
        out, err = capsys.readouterr()
        observed[tuple(argv)] = (code, out)

    assert observed == {(): (0, "22\n23\n24\n"), ("--repo", "o/r"): (0, "22\n23\n24\n25\n")}


def dead_pid():
    pid = os.fork()
    if pid == 0:
        os._exit(0)
    os.waitpid(pid, 0)
    return pid


def test_main_reads_a_lock_under_the_main_tree_git_names_from_the_callers_directory_as_an_int_pid_that_is_alive(tmp_path, monkeypatch, capsys, solvable_issues):
    numbers = [10, 11, 12, 13, 14, 15, 18, 19, 20]
    (tmp_path / "issues.json").write_text(json.dumps([opted_in(n) for n in numbers]))
    (tmp_path / "prs.json").write_text("[]")
    monkeypatch.setenv("VERI_GH_JSON", str(tmp_path))
    pid = str(os.getpid())
    texts = {10: " %s \n" % pid, 11: "+" + pid, 12: pid[0] + "_" + pid[1:] if len(pid) > 1 else pid,
             14: "abc\n", 15: "%d\n" % dead_pid(), 18: pid + "\n"}
    conducting(monkeypatch, *texts)
    decoy = tmp_path / "decoy"
    for number, text in texts.items():
        lock = decoy / ".tdd" / "wt" / str(number) / ".tdd" / "conductor.pid"
        lock.parent.mkdir(parents=True)
        lock.write_text(text)
    (decoy / ".tdd" / "wt" / "13" / ".tdd" / "conductor.pid").mkdir(parents=True)
    caller = tmp_path / "caller"
    stray = caller / ".tdd" / "wt" / "19" / ".tdd" / "conductor.pid"
    stray.parent.mkdir(parents=True)
    stray.write_text(pid)
    monkeypatch.chdir(caller)
    calls = []

    def run(answer):
        def fake_run(args, *rest, **kwargs):
            if list(args) != ["git", "worktree", "list", "--porcelain"]:
                raise AssertionError("unexpected command: %r" % (args,))
            calls.append((kwargs.get("cwd") in (None, str(caller), caller), kwargs.get("stderr")))
            if isinstance(answer, BaseException):
                raise answer
            return subprocess.CompletedProcess(args, *answer)

        monkeypatch.setattr(subprocess, "run", fake_run)
        monkeypatch.setattr(subprocess, "Popen", fake_run)
        code = solvable_issues.main([])
        out, err = capsys.readouterr()
        return code, out

    unlocked = "".join("%d\n" % n for n in numbers)
    assert run((0, "worktree %s\nHEAD 0000000\n" % decoy, "")) == (0, "11\n12\n13\n14\n15\n19\n20\n")
    assert run((0, "%s\nHEAD 0000000\n" % decoy, "")) == (0, "11\n12\n13\n14\n15\n19\n20\n")
    assert run((128, "", "fatal: not a git repository\n")) == (0, unlocked)
    assert run((0, "", "")) == (0, unlocked)
    assert run(FileNotFoundError(2, "No such file or directory", "git")) == (0, unlocked)
    assert calls == [(True, subprocess.DEVNULL)] * 5


def test_main_sorts_survivors_by_priority_then_bug_band_then_number_never_widening_the_pool_and_returns_3_when_none_survive(tmp_path, monkeypatch, capsys, solvable_issues):
    monkeypatch.setenv("VERI_GH_JSON", str(tmp_path))
    fake_git_answering_nothing(monkeypatch)
    (tmp_path / "issues.json").write_text(json.dumps([
        opted_in(1), labelled(2, "ready-for-agent", "bug"), labelled(3, "ready-for-agent", "priority"),
        labelled(4, "priority", "bug"), dict(blocked_by(5, "#1"), labels=[{"name": "ready-for-agent"}, {"name": "priority"}]),
        labelled(6, "ready-for-agent", "bug"), dict(labelled(7, "ready-for-agent", "priority"), state="CLOSED"),
        labelled(8, "ready-for-agent", "bug", "priority"), labelled(9, "ready-for-agent", "urgent"), labelled(10, "urgent")]))
    (tmp_path / "prs.json").write_text(json.dumps([{"state": "OPEN", "body": "Closes #6"}]))

    observed = []
    for tunables in ({}, {"VERI_PRIORITY_LABEL": "urgent"}):
        for name, value in tunables.items():
            monkeypatch.setenv(name, value)
        code = solvable_issues.main([])
        out, err = capsys.readouterr()
        observed.append((code, out))
    monkeypatch.delenv("VERI_PRIORITY_LABEL")
    (tmp_path / "issues.json").write_text(json.dumps([
        labelled(4, "priority", "bug"), dict(labelled(7, "ready-for-agent", "priority"), state="CLOSED")]))
    code = solvable_issues.main([])
    out, err = capsys.readouterr()
    observed.append((code, out))

    assert observed == [(0, "3\n8\n2\n1\n9\n"), (0, "9\n2\n8\n1\n3\n"), (3, "")]


def cli_fixtures(tmp_path, monkeypatch, issues):
    """A VERI_GH_JSON directory holding `issues` and no PRs, a separate working directory, and git answering nothing."""
    fixtures, cwd = tmp_path / "fixtures", tmp_path / "cwd"
    fixtures.mkdir()
    cwd.mkdir()
    (fixtures / "issues.json").write_text(json.dumps(issues))
    (fixtures / "prs.json").write_text("[]")
    fake_git_answering_nothing(monkeypatch)
    return fixtures, cwd


def test_cli_lists_an_open_opted_in_unblocked_issue_run_from_its_own_cwd_returning_0_with_empty_stderr(tmp_path, monkeypatch, run_cli, solvable_issues):
    fixtures, cwd = cli_fixtures(tmp_path, monkeypatch, [opted_in(41)])

    answer = run_cli(solvable_issues, [], env={"VERI_GH_JSON": str(fixtures)}, cwd=cwd)

    assert answer == (0, "41\n", "")


def test_cli_with_the_label_tunable_unset_never_lists_an_issue_whose_only_label_extends_ready_for_agent(tmp_path, monkeypatch, run_cli, solvable_issues):
    fixtures, cwd = cli_fixtures(tmp_path, monkeypatch, [opted_in(62), labelled(63, "ready-for-agent:docs")])

    answer = run_cli(solvable_issues, [], env={"VERI_GH_JSON": str(fixtures)}, cwd=cwd)

    assert answer == (0, "62\n", "")


def test_cli_prints_issues_fetched_out_of_order_one_per_line_ascending(tmp_path, monkeypatch, run_cli, solvable_issues):
    fixtures, cwd = cli_fixtures(tmp_path, monkeypatch, [opted_in(12), opted_in(3), opted_in(7)])

    answer = run_cli(solvable_issues, [], env={"VERI_GH_JSON": str(fixtures)}, cwd=cwd)

    assert answer == (0, "3\n7\n12\n", "")


def test_cli_lists_an_issue_carrying_both_labels_under_the_default_label_and_under_the_docs_label(tmp_path, monkeypatch, run_cli, solvable_issues):
    fixtures, cwd = cli_fixtures(tmp_path, monkeypatch, [labelled(66, "ready-for-agent", "ready-for-agent:docs")])

    under_default = run_cli(solvable_issues, [], env={"VERI_GH_JSON": str(fixtures)}, cwd=cwd)
    under_docs = run_cli(solvable_issues, [], env={"VERI_GH_JSON": str(fixtures), "VERI_LABEL": "ready-for-agent:docs"}, cwd=cwd)

    assert (under_default, under_docs) == ((0, "66\n", ""), (0, "66\n", ""))


def test_cli_refuses_an_empty_label_tunable_with_2_nothing_on_stdout_and_a_diagnostic_on_stderr(tmp_path, monkeypatch, run_cli, solvable_issues):
    fixtures, cwd = cli_fixtures(tmp_path, monkeypatch, [opted_in(67), labelled(68, "ready-for-agent:docs")])

    answer = run_cli(solvable_issues, [], env={"VERI_GH_JSON": str(fixtures), "VERI_LABEL": ""}, cwd=cwd)

    assert answer == (2, "", "solvable-issues: VERI_LABEL is set but empty: name a label or leave it unset\n")


@pytest.mark.parametrize("state, listed", [("OPEN", "120\n"), ("CLOSED", "125\n")])
def test_cli_withholds_an_issue_blocked_by_a_github_issue_url_exactly_while_that_issue_is_open(state, listed, tmp_path, monkeypatch, run_cli, solvable_issues):
    fixtures, cwd = cli_fixtures(tmp_path, monkeypatch, [
        blocked_by(125, "https://github.com/ztrange/veri/issues/120"), dict(opted_in(120), state=state)])

    answer = run_cli(solvable_issues, [], env={"VERI_GH_JSON": str(fixtures)}, cwd=cwd)

    assert answer == (0, listed, "")


def test_cli_under_repo_never_reads_a_url_naming_another_repositorys_issue_as_a_blocker(tmp_path, monkeypatch, run_cli, solvable_issues):
    fixtures, cwd = cli_fixtures(tmp_path, monkeypatch, [
        blocked_by(131, "https://github.com/ztrange/veri-demo-node/issues/120"), opted_in(120)])

    answer = run_cli(solvable_issues, ["--repo", "ztrange/veri"], env={"VERI_GH_JSON": str(fixtures)}, cwd=cwd)

    assert answer == (0, "120\n131\n", "")


def test_cli_prints_a_bug_labelled_issue_ahead_of_a_lower_numbered_plain_one_each_band_ascending(tmp_path, monkeypatch, run_cli, solvable_issues):
    fixtures, cwd = cli_fixtures(tmp_path, monkeypatch, [
        opted_in(201), labelled(205, "ready-for-agent", "bug"), opted_in(202), labelled(203, "ready-for-agent", "bug")])

    answer = run_cli(solvable_issues, [], env={"VERI_GH_JSON": str(fixtures)}, cwd=cwd)

    assert answer == (0, "203\n205\n201\n202\n", "")


def test_cli_prints_a_priority_labelled_issue_ahead_of_a_lower_numbered_bug_and_one_carrying_both_in_the_priority_band(tmp_path, monkeypatch, run_cli, solvable_issues):
    fixtures, cwd = cli_fixtures(tmp_path, monkeypatch, [
        labelled(120, "ready-for-agent", "bug"), labelled(160, "bug", "ready-for-agent", "priority"),
        labelled(150, "priority", "ready-for-agent")])

    answer = run_cli(solvable_issues, [], env={"VERI_GH_JSON": str(fixtures)}, cwd=cwd)

    assert answer == (0, "150\n160\n120\n", "")


def test_cli_never_opts_in_an_issue_by_the_priority_label_alone(tmp_path, monkeypatch, run_cli, solvable_issues):
    fixtures, cwd = cli_fixtures(tmp_path, monkeypatch, [labelled(170, "priority"), opted_in(180)])

    answer = run_cli(solvable_issues, [], env={"VERI_GH_JSON": str(fixtures)}, cwd=cwd)

    assert answer == (0, "180\n", "")


def test_cli_never_lists_an_issue_carrying_a_taken_label_even_with_the_opt_in_label_while_an_opt_in_only_issue_is_listed(tmp_path, monkeypatch, run_cli, solvable_issues):
    fixtures, cwd = cli_fixtures(tmp_path, monkeypatch, [
        labelled(200, "ready-for-agent", "taken:main"), labelled(210, "ready-for-agent", "taken:mu"), opted_in(220)])

    answer = run_cli(solvable_issues, [], env={"VERI_GH_JSON": str(fixtures)}, cwd=cwd)

    assert answer == (0, "220\n", "")


def test_cli_never_lists_an_issue_labelled_parked_even_when_it_carries_the_opt_in_label(tmp_path, monkeypatch, run_cli, solvable_issues):
    fixtures, cwd = cli_fixtures(tmp_path, monkeypatch, [labelled(190, "ready-for-agent", "parked"), opted_in(200)])

    answer = run_cli(solvable_issues, [], env={"VERI_GH_JSON": str(fixtures)}, cwd=cwd)

    assert answer == (0, "200\n", "")


def test_cli_still_withholds_a_priority_or_bug_issue_that_is_blocked_claimed_or_closed(tmp_path, monkeypatch, run_cli, solvable_issues):
    fixtures, cwd = cli_fixtures(tmp_path, monkeypatch, [
        labelled(189), dict(blocked_by(190, "#189"), labels=[{"name": "ready-for-agent"}, {"name": "priority"}]),
        labelled(191, "ready-for-agent", "bug"), dict(labelled(192, "ready-for-agent", "priority"), state="CLOSED"),
        opted_in(195)])
    (fixtures / "prs.json").write_text(json.dumps([{"state": "OPEN", "body": "Closes #191\n"}]))

    answer = run_cli(solvable_issues, [], env={"VERI_GH_JSON": str(fixtures)}, cwd=cwd)

    assert answer == (0, "195\n", "")


def test_cli_refuses_an_empty_priority_label_tunable_with_2_and_a_diagnostic_and_unset_defaults_to_priority(tmp_path, monkeypatch, run_cli, solvable_issues):
    fixtures, cwd = cli_fixtures(tmp_path, monkeypatch, [opted_in(100), labelled(200, "ready-for-agent", "priority")])

    unset = run_cli(solvable_issues, [], env={"VERI_GH_JSON": str(fixtures)}, cwd=cwd)
    refused = run_cli(solvable_issues, [], env={"VERI_GH_JSON": str(fixtures), "VERI_PRIORITY_LABEL": ""}, cwd=cwd)

    assert (refused, unset) == (
        (2, "", "solvable-issues: VERI_PRIORITY_LABEL is set but empty: name a label or leave it unset\n"),
        (0, "200\n100\n", ""))


def test_cli_with_no_issue_carrying_a_band_label_prints_the_solvable_issues_ascending(tmp_path, monkeypatch, run_cli, solvable_issues):
    fixtures, cwd = cli_fixtures(tmp_path, monkeypatch, [
        opted_in(210), opted_in(208), opted_in(207), blocked_by(209, "#212"), labelled(211), labelled(212),
        dict(opted_in(213), state="CLOSED")])
    (fixtures / "prs.json").write_text(json.dumps([{"state": "OPEN", "body": "Closes #207\n"}]))

    answer = run_cli(solvable_issues, [], env={"VERI_GH_JSON": str(fixtures)}, cwd=cwd)

    assert answer == (0, "208\n210\n", "")


def fake_gh_paging(monkeypatch, issues, prs):
    """subprocess.run answering `gh issue list`/`gh pr list` with the first --limit items, 30 when none is given, and git with nothing."""
    def fake_run(args, *rest, **kwargs):
        args = list(args)
        if args[:4] == ["git", "worktree", "list", "--porcelain"]:
            return subprocess.CompletedProcess(args, 0, "", "")
        if args[:1] != ["gh"] or args[2:3] != ["list"] or args[1] not in ("issue", "pr"):
            raise AssertionError("unexpected command: %r" % (args,))
        limit = int(args[args.index("--limit") + 1]) if "--limit" in args else 30
        listing = issues if args[1] == "issue" else prs
        return subprocess.CompletedProcess(args, 0, json.dumps(listing[:limit]) + "\n", "")

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(subprocess, "Popen", fake_run)


def newest_first(numbers, overrides):
    return [overrides.get(n, labelled(n)) for n in numbers]


@pytest.mark.parametrize("issues, prs, answer", [
    (newest_first(range(140, 100, -1), {101: opted_in(101)}), [], (0, "101\n", "")),
    (newest_first(range(140, 100, -1), {140: blocked_by(140, "#101")}), [], (3, "", "")),
    ([opted_in(7)], [{"state": "OPEN", "body": "Closes #7" if i == 39 else "Closes #%d" % (1000 + i)} for i in range(40)],
     (3, "", "")),
], ids=["opted-in-issue", "open-blocker", "closes-pr"])
def test_cli_honours_an_item_older_than_ghs_default_page_of_30(issues, prs, answer, tmp_path, monkeypatch, run_cli, solvable_issues):
    fake_gh_paging(monkeypatch, issues, prs)

    assert run_cli(solvable_issues, [], env={"VERI_GH_DRIVER": "auto"}, cwd=tmp_path) == answer


REPO_ROOT = pathlib.Path(__file__).resolve().parents[5]


@pytest.mark.parametrize("doc", [REPO_ROOT / "CONTEXT.md"], ids=lambda doc: doc.name)
def test_doc_names_the_label_tunable_and_the_one_label_per_loop_use(doc):
    text = doc.read_text()

    assert ("VERI_LABEL" in text, bool(re.search(r"one[ -]label[ -]per[ -]loop", text, re.IGNORECASE))) == (True, True)


def test_main_repo_then_not_running_reads_that_repos_issues_and_omits_the_live_conductors_issue(monkeypatch, capsys, solvable_issues):
    monkeypatch.delenv("VERI_GH_JSON", raising=False)
    monkeypatch.setenv("VERI_GH_DRIVER", "auto")
    scripts = pathlib.Path(solvable_issues.__file__).resolve().parent.parent
    listing = "  1 /sbin/launchd\n 99 bash %s/run-conductor.sh 6\n" % scripts
    started = []

    def fake_run(args, *rest, **kwargs):
        args = list(args)
        if args[:4] == ["git", "worktree", "list", "--porcelain"]:
            return subprocess.CompletedProcess(args, 0, "", "")
        if args[0] == "ps":
            return subprocess.CompletedProcess(args, 0, listing, "")
        if args[:3] == ["gh", "issue", "list"]:
            started.append(args[args.index("--repo") + 1:] if "--repo" in args else None)
            return subprocess.CompletedProcess(args, 0, json.dumps([opted_in(5), opted_in(6), opted_in(7)]), "")
        if args[:3] == ["gh", "pr", "list"]:
            return subprocess.CompletedProcess(args, 0, "[]", "")
        raise AssertionError("unexpected command: %r" % (args,))

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(subprocess, "Popen", fake_run)

    code = solvable_issues.main(["--repo", "o/n", "--not-running"])

    out, err = capsys.readouterr()
    assert (code, out, started) == (0, "5\n7\n", [["o/n"]])


def test_shim_header_comment_names_both_blocker_spellings():
    shim = (REPO_ROOT / "skills" / "tdd" / "scripts" / "solvable-issues.sh").read_text().splitlines()[1:]
    header = "\n".join(itertools.takewhile(lambda line: line.startswith("#"), shim))

    assert ("#<n>" in header, bool(re.search(r"https://github\.com/\S*/issues/", header))) == (True, True)


@pytest.fixture
def plant_claim():
    """plant_claim(main_tree, number, pid) writes .tdd/wt/<number>/.tdd/conductor.pid under main_tree."""
    def plant(main_tree, number, pid):
        lock = main_tree / ".tdd" / "wt" / str(number) / ".tdd" / "conductor.pid"
        lock.parent.mkdir(parents=True)
        lock.write_text("%d\n" % pid)
    return plant


def test_cli_withholds_the_issue_whose_worktree_lock_holds_a_live_pid_and_lists_one_with_a_dead_pid_or_no_worktree(tmp_path, monkeypatch, run_cli, plant_claim, solvable_issues):
    fixtures, cwd = cli_fixtures(tmp_path, monkeypatch, [opted_in(170), opted_in(171), opted_in(172)])
    main_tree = tmp_path / "main-tree"
    plant_claim(main_tree, 170, os.getpid())
    plant_claim(main_tree, 171, dead_pid())
    conducting(monkeypatch, 170)
    fake_git_answering(monkeypatch, main_tree)

    answer = run_cli(solvable_issues, [], env={"VERI_GH_JSON": str(fixtures)}, cwd=cwd)

    assert answer == (0, "171\n172\n", "")


def test_cli_lists_again_a_bailed_runs_issue_whose_worktree_lock_holds_a_dead_pid_and_no_open_pr_closes(tmp_path, monkeypatch, run_cli, plant_claim, solvable_issues):
    fixtures, cwd = cli_fixtures(tmp_path, monkeypatch, [opted_in(173)])
    main_tree = tmp_path / "main-tree"
    plant_claim(main_tree, 173, dead_pid())
    fake_git_answering(monkeypatch, main_tree)

    answer = run_cli(solvable_issues, [], env={"VERI_GH_JSON": str(fixtures)}, cwd=cwd)

    assert answer == (0, "173\n", "")


def test_cli_keeps_out_an_issue_an_open_pr_closes_though_its_worktree_lock_holds_a_dead_pid_returning_3(tmp_path, monkeypatch, run_cli, plant_claim, solvable_issues):
    fixtures, cwd = cli_fixtures(tmp_path, monkeypatch, [opted_in(175)])
    (fixtures / "prs.json").write_text(json.dumps([
        {"state": "OPEN", "body": "Draft PR opened by a /tdd run that bailed.\n\nCloses #175\n"}]))
    main_tree = tmp_path / "main-tree"
    plant_claim(main_tree, 175, dead_pid())
    fake_git_answering(monkeypatch, main_tree)

    answer = run_cli(solvable_issues, [], env={"VERI_GH_JSON": str(fixtures)}, cwd=cwd)

    assert answer == (3, "", "")


@pytest.mark.process("git: a real repository whose worktree branch is pushed to a bare remote")
def test_cli_lists_an_issue_whose_branch_is_on_the_remote_with_no_open_pr_and_no_live_pid(tmp_path, run_cli, solvable_issues):
    def git(*args):
        return subprocess.run(["git", "-c", "user.name=veri", "-c", "user.email=veri@example.test", *args],
                              check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).stdout

    fixtures, repo, remote = tmp_path / "fixtures", tmp_path / "pushed", tmp_path / "pushed-remote.git"
    fixtures.mkdir()
    (fixtures / "issues.json").write_text(json.dumps([opted_in(191)]))
    (fixtures / "prs.json").write_text("[]")
    git("init", "-q", "-b", "main", str(repo))
    git("-C", str(repo), "commit", "-q", "--allow-empty", "-m", "initial")
    git("init", "-q", "--bare", str(remote))
    git("-C", str(repo), "remote", "add", "origin", str(remote))
    worktree = repo / ".tdd" / "wt" / "191"
    git("-C", str(repo), "worktree", "add", "-q", "-b", "tdd/191-slug", str(worktree), "main")
    git("-C", str(worktree), "push", "-q", "--set-upstream", "origin", "HEAD")

    on_remote = git("-C", str(repo), "ls-remote", "--heads", "origin", "tdd/191-slug")
    answer = run_cli(solvable_issues, [], env={"VERI_GH_JSON": str(fixtures)}, cwd=repo)

    assert (bool(on_remote), answer) == (True, (0, "191\n", ""))


def solvable_entry():
    lines = (REPO_ROOT / "CONTEXT.md").read_text().splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith("**Solvable**:"))
    end = next((i for i, line in enumerate(lines) if i > start and line.startswith("**")), len(lines))
    return "\n".join(lines[start + 1:end])


def test_context_solvable_entry_names_the_conductor_pid_lock_and_a_live_holder_as_what_marks_a_run_in_flight():
    entry = solvable_entry()

    assert ("conductor.pid" in entry,
            bool(re.search(r"kill -0|alive|still running|live (conductor|process|run)", entry, re.IGNORECASE))) == (True, True)


def test_skill_preflight_never_writes_the_conductor_lock_itself_leaving_it_to_run_conductor_2249():
    preflight = (REPO_ROOT / "skills" / "tdd" / "PREFLIGHT.md").read_text()

    assert (bool(re.search(r'> *"?\.tdd/conductor\.pid', preflight)), "$PPID" in preflight,
            "run_conductor.py" in preflight) == (False, False, True)


def header_paragraphs():
    shim = (REPO_ROOT / "skills" / "tdd" / "scripts" / "solvable-issues.sh").read_text().splitlines()[1:]
    paragraphs, current = [], []
    for line in itertools.takewhile(lambda line: line.startswith("#"), shim):
        text = re.sub(r"^#\s?", "", line)
        if text.strip():
            current.append(text)
        elif current:
            paragraphs.append(" ".join(current))
            current = []
    if current:
        paragraphs.append(" ".join(current))
    return [paragraph.lower() for paragraph in paragraphs]


CLAIMS = {
    "the-open-PR-as-the-claim-every-machine-sees": [
        r"closes #|pull request|open pr|draft pr",
        r"every machine|any machine|other machine|another machine|all machines|across machines|cross-machine|machine-independent",
        r"claim"],
    "the-lock-as-one-machines-worktree-guard": [
        r"conductor\.pid|pid lock|the lock|the pid", r"worktree", r"guard", r"same[- ]machine|one machine|machine-local|local"],
    "the-ADR-recording-the-decision": [r"adr[ -]?[0-9]{4}"],
}


@pytest.mark.parametrize("passage, records", [
    ("CONTEXT.md", lambda: [" ".join(solvable_entry().splitlines()).lower()]),
    ("solvable-issues.sh", header_paragraphs)], ids=["CONTEXT.md", "solvable-issues.sh"])
def test_passage_says_the_open_pr_is_the_claim_and_the_pid_lock_one_machines_worktree_guard_citing_its_adr(passage, records):
    texts = records()
    missing = [tag for tag, patterns in CLAIMS.items()
               if not any(all(re.search(pattern, text) for pattern in patterns) for text in texts)]

    assert missing == []


@pytest.mark.parametrize("driver", ["", "REST", "gql"])
def test_cli_with_an_unknown_gh_driver_starts_no_process_prints_nothing_and_returns_2_with_one_stderr_line_naming_the_variable_and_value(driver, tmp_path, run_cli, monkeypatch, solvable_issues):
    started = no_process(monkeypatch)

    code, out, err = run_cli(solvable_issues, [], env={"VERI_GH_DRIVER": driver}, cwd=tmp_path)

    assert (code, started, out, len(err.splitlines()), "VERI_GH_DRIVER" in err, "'%s'" % driver in err) == (2, [], "", 1, True, True)


def test_cli_refuses_repo_with_no_value_with_2_nothing_on_stdout_and_stderr_exactly_the_usage_line(tmp_path, monkeypatch, run_cli, solvable_issues):
    fixtures, cwd = cli_fixtures(tmp_path, monkeypatch, [])

    answer = run_cli(solvable_issues, ["--repo"], env={"VERI_GH_JSON": str(fixtures)}, cwd=cwd)

    assert answer == (2, "", USAGE)


def write_gh_fixtures(directory, issues):
    directory.mkdir()
    (directory / "issues.json").write_text(json.dumps(issues))
    (directory / "prs.json").write_text("[]")


def git_in(*args):
    return subprocess.run(["git", "-c", "user.name=veri", "-c", "user.email=veri@example.test", *args],
                          check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).stdout


@pytest.mark.process("git and solvable-issues.sh: a linked worktree's run through a symlink to the skill directory")
def test_cli_run_through_a_symlink_to_the_skill_directory_from_a_linked_worktree_answers_as_in_place_withholding_the_issue_locked_under_the_main_tree(tmp_path, run_cli, plant_claim, conductor_process, solvable_issues):
    fixtures, repo, linked, link = tmp_path / "fixtures", tmp_path / "repo", tmp_path / "linked", tmp_path / "skill-link"
    write_gh_fixtures(fixtures, [opted_in(5), opted_in(6)])
    git_in("init", "-q", "-b", "main", str(repo))
    git_in("-C", str(repo), "commit", "-q", "--allow-empty", "-m", "initial")
    git_in("-C", str(repo), "worktree", "add", "-q", "-b", "linked", str(linked), "main")
    plant_claim(repo, 5, conductor_process(5))
    link.symlink_to(REPO_ROOT / "skills" / "tdd", target_is_directory=True)

    in_place = run_cli(solvable_issues, [], env={"VERI_GH_JSON": str(fixtures)}, cwd=linked)
    through_link = subprocess.run([str(link / "scripts" / "solvable-issues.sh")], cwd=linked, text=True,
                                  env=dict(os.environ, VERI_GH_JSON=str(fixtures)),
                                  stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    assert (in_place, (through_link.returncode, through_link.stdout, through_link.stderr)) == ((0, "6\n", ""), (0, "6\n", ""))


ARG_MAX_STRLEN = 131072


def fake_git_refusing_long_arguments(monkeypatch):
    """subprocess.run refusing any argument over 128 KiB the way Linux does, answering `git worktree list --porcelain` with nothing."""
    def fake_run(args, *rest, **kwargs):
        if any(len(str(arg)) > ARG_MAX_STRLEN for arg in args):
            raise OSError(errno.E2BIG, "Argument list too long")
        if list(args[:4]) != ["git", "worktree", "list", "--porcelain"]:
            raise AssertionError("unexpected command: %r" % (args,))
        return subprocess.CompletedProcess(args, 0, "", "")

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(subprocess, "Popen", fake_run)


def test_cli_reads_an_issues_document_over_256_kib_to_the_same_answer_as_short_bodies_under_a_128_kib_argument_limit(tmp_path, monkeypatch, run_cli, solvable_issues):
    def issues(pad):
        return [dict(opted_in(n), labels=[{"name": "ready-for-agent"}] if n % 2 == 0 else [],
                     body="## What to build\n\n" + pad + "\n\n## Blocked by\n\nNone.\n") for n in range(1, 41)]

    short, long, cwd = tmp_path / "short", tmp_path / "long", tmp_path / "cwd"
    for fixtures, pad in ((short, "short"), (long, "x" * 8192)):
        write_gh_fixtures(fixtures, issues(pad))
    cwd.mkdir()
    fake_git_refusing_long_arguments(monkeypatch)
    want = (0, "".join("%d\n" % n for n in range(2, 41, 2)), "")

    answers = [run_cli(solvable_issues, [], env={"VERI_GH_JSON": str(fixtures)}, cwd=cwd) for fixtures in (short, long)]

    assert ((long / "issues.json").stat().st_size > 262144, answers) == (True, [want, want])


def numbers_this_files_fixtures_name():
    text = pathlib.Path(__file__).read_text()
    return sorted({int(a or b) for a, b in re.findall(r'(?:opted_in|labelled|blocked_by)\((\d+)|"number": (\d+)', text)})


@pytest.mark.process("git: a surrounding repository whose main tree holds live conductor locks")
def test_cli_answer_is_unchanged_by_live_conductor_locks_under_the_surrounding_repository_for_unrelated_numbers_and_every_number_this_file_names(tmp_path, monkeypatch, run_cli, plant_claim, conductor_process, solvable_issues):
    unrelated, named = [108, 117, 120, 124], numbers_this_files_fixtures_name()
    fixtures, cwd = tmp_path / "fixtures", tmp_path / "no-claims"
    write_gh_fixtures(fixtures, [opted_in(n) for n in sorted(set(unrelated + named))])
    git_in("init", "-q", "-b", "main", str(cwd))
    surroundings = {"surrounding-unrelated": unrelated, "surrounding-every": named}
    conductor = conductor_process(*unrelated, *named)
    for name, numbers in surroundings.items():
        git_in("init", "-q", "-b", "main", str(tmp_path / name))
        for n in numbers:
            plant_claim(tmp_path / name, n, conductor)

    def answers():
        run = run_cli(solvable_issues, [], env={"VERI_GH_JSON": str(fixtures)}, cwd=cwd)
        monkeypatch.delenv("VERI_PRIORITY_LABEL", raising=False)
        label_run = run_cli(solvable_issues, [], env={"VERI_GH_JSON": str(fixtures)}, cwd=cwd)
        return {"run": run, "label_run": label_run}

    no_lock = answers()
    under = {}
    for name in surroundings:
        monkeypatch.chdir(tmp_path / name)
        under[name] = answers()

    assert (bool(named), no_lock["run"][0], bool(no_lock["run"][1]), under) == (
        True, 0, True, {name: no_lock for name in surroundings})


def rest_page(request, items):
    """The page of `items` a `gh api` listing request path asks for: filtered by its state, sorted by its direction, cut by its per_page and page."""
    params = dict(pair.split("=") for pair in request.partition("?")[2].split("&"))
    items = [item for item in items if params["state"] == "all" or item["state"].lower() == params["state"]]
    items.sort(key=lambda item: item["number"], reverse=params.get("direction", "desc") == "desc")
    size, page = int(params["per_page"]), int(params.get("page", 1))
    return items[(page - 1) * size:page * size]


def fake_gh_api_shifting(monkeypatch, listings):
    """subprocess.run answering `gh api <path>` from `listings` (endpoint -> items), closing the first item a listing serves once its first page has gone out; records the gh api paths and answers git with nothing."""
    requests, closed = [], {}

    def fake_run(args, *rest, **kwargs):
        args = list(args)
        if args[:4] == ["git", "worktree", "list", "--porcelain"]:
            return subprocess.CompletedProcess(args, 0, "", "")
        if args[:2] != ["gh", "api"] or len(args) != 3:
            raise AssertionError("unexpected command: %r" % (args,))
        requests.append(args[2])
        endpoint = args[2].partition("?")[0].rsplit("/", 1)[1]
        shut = closed.setdefault(endpoint, set())
        served = rest_page(args[2], [dict(item, state="closed") if item["number"] in shut else item for item in listings[endpoint]])
        if served and not shut:
            shut.add(served[0]["number"])
        return subprocess.CompletedProcess(args, 0, json.dumps(served) + "\n", "")

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(subprocess, "Popen", fake_run)
    return requests


@pytest.mark.parametrize("endpoint", ["issues", "pulls"])
def test_cli_reads_the_open_listing_in_one_request_under_100_open_items_and_the_grow_only_listing_at_100_or_more_even_as_pages_shift(endpoint, tmp_path, monkeypatch, run_cli, solvable_issues):
    prefix = "repos/{owner}/{repo}/%s" % endpoint
    open_page, grow_only = prefix + "?state=open&per_page=100", prefix + "?state=all&sort=created&direction=asc&per_page=100&page=%d"

    def answer(count):
        if endpoint == "issues":
            listings = {"issues": [opted_in(n) if 1 < n < count else labelled(n) for n in range(1, count + 1)], "pulls": []}
            solvable = range(2, count)
        else:
            claim = {40: 230, 100: 250, 130: 205}[count]
            listings = {"issues": [opted_in(n) for n in range(1, 11)],
                        "pulls": [{"number": n, "state": "open", "body": "Closes #5" if n == claim else "Tidies something."}
                                  for n in range(201, 201 + count)]}
            solvable = [n for n in range(1, 11) if n != 5]
        requests = fake_gh_api_shifting(monkeypatch, listings)
        code, out, err = run_cli(solvable_issues, [], cwd=tmp_path)
        return (code, out, err, [path for path in requests if path.startswith(prefix)]), "".join("%d\n" % n for n in solvable)

    observed = {count: answer(count) for count in (40, 100, 130)}

    assert {count: got for count, (got, _) in observed.items()} == {
        40: (0, observed[40][1], "", [open_page]),
        100: (0, observed[100][1], "", [open_page, grow_only % 1, grow_only % 2]),
        130: (0, observed[130][1], "", [open_page, grow_only % 1, grow_only % 2, grow_only % 3]),
    }
    assert [len(wanted.splitlines()) for _, wanted in observed.values()] == (
        [38, 98, 128] if endpoint == "issues" else [9, 9, 9])


def fake_gh_refusing_graphql_serving_rest(monkeypatch, listings):
    """subprocess.run failing `gh issue`/`gh pr` with the 403 and answering `gh api repos/{owner}/{repo}/<endpoint>?...` a page at a time from `listings` (endpoint -> items); git answers nothing."""
    def fake_run(args, *rest, **kwargs):
        args = list(args)
        if args[:4] == ["git", "worktree", "list", "--porcelain"]:
            return subprocess.CompletedProcess(args, 0, "", "")
        if args[:1] != ["gh"]:
            raise AssertionError("unexpected command: %r" % (args,))
        if args[1] in ("issue", "pr", "repo"):
            return subprocess.CompletedProcess(args, 1, "", "HTTP 403: GitHub GraphQL is not available from Claude Code sessions\n")
        if args[1] != "api" or len(args) != 3 or not args[2].startswith("repos/{owner}/{repo}/"):
            raise AssertionError("unexpected command: %r" % (args,))
        served = rest_page(args[2], listings[args[2].partition("?")[0].rsplit("/", 1)[1]])
        return subprocess.CompletedProcess(args, 0, json.dumps(served) + "\n", "")

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(subprocess, "Popen", fake_run)


def test_cli_against_a_gh_that_refuses_graphql_with_the_403_and_answers_rest_under_repos_owner_repo_a_page_at_a_time_prints_the_same_issue_numbers_and_exit_code_with_empty_stderr_across_more_than_one_100_item_page(tmp_path, monkeypatch, run_cli, solvable_issues):
    issues = [labelled(100 + k) for k in range(110)] + [
        opted_in(70), dict(opted_in(71), body="## Blocked by\n\n#72\n"), labelled(72), opted_in(73),
        dict(opted_in(74), labels=[{"name": "ready-for-agent"}, {"name": "priority"}])]
    pulls = [{"number": 1 + k, "state": "OPEN", "body": ""} for k in range(105)] + [
        {"number": 900, "state": "OPEN", "body": "Draft PR opened by a /tdd run.\n\nCloses #73\n"}]
    fake_gh_refusing_graphql_serving_rest(monkeypatch, {"issues": issues, "pulls": pulls})

    answer = run_cli(solvable_issues, [], env={"VERI_GH_DRIVER": "auto"}, cwd=tmp_path)

    assert answer == (0, "74\n70\n", "")


def test_main_not_running_omits_the_issue_with_a_live_conductor_from_this_skill_path_and_keeps_the_rest_in_order(tmp_path, monkeypatch, capsys, solvable_issues):
    (tmp_path / "issues.json").write_text(json.dumps([opted_in(5), opted_in(6), opted_in(7)]))
    (tmp_path / "prs.json").write_text("[]")
    monkeypatch.setenv("VERI_GH_JSON", str(tmp_path))
    scripts = pathlib.Path(solvable_issues.__file__).resolve().parent.parent
    listing = "  1 /sbin/launchd\n 99 bash %s/run-conductor.sh 6\n" % scripts

    def fake_run(args, *rest, **kwargs):
        if list(args[:4]) == ["git", "worktree", "list", "--porcelain"]:
            return subprocess.CompletedProcess(args, 0, "", "")
        if args[0] == "ps":
            return subprocess.CompletedProcess(args, 0, listing, "")
        raise AssertionError("unexpected command: %r" % (args,))

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(subprocess, "Popen", fake_run)

    code = solvable_issues.main(["--not-running"])

    out, err = capsys.readouterr()
    assert (code, out) == (0, "5\n7\n")


def test_main_not_running_keeps_the_issue_whose_live_conductor_started_from_a_different_skill_path(tmp_path, monkeypatch, capsys, solvable_issues):
    (tmp_path / "issues.json").write_text(json.dumps([opted_in(5), opted_in(6), opted_in(7)]))
    (tmp_path / "prs.json").write_text("[]")
    monkeypatch.setenv("VERI_GH_JSON", str(tmp_path))
    listing = "  1 /sbin/launchd\n 99 bash /tmp/skill-copy/scripts/run-conductor.sh 6\n"

    def fake_run(args, *rest, **kwargs):
        if list(args[:4]) == ["git", "worktree", "list", "--porcelain"]:
            return subprocess.CompletedProcess(args, 0, "", "")
        if args[0] == "ps":
            return subprocess.CompletedProcess(args, 0, listing, "")
        raise AssertionError("unexpected command: %r" % (args,))

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(subprocess, "Popen", fake_run)

    code = solvable_issues.main(["--not-running"])

    out, err = capsys.readouterr()
    assert (code, out) == (0, "5\n6\n7\n")


def test_main_without_not_running_still_lists_the_issue_with_a_live_conductor_from_this_skill_path(tmp_path, monkeypatch, capsys, solvable_issues):
    (tmp_path / "issues.json").write_text(json.dumps([opted_in(5), opted_in(6), opted_in(7)]))
    (tmp_path / "prs.json").write_text("[]")
    monkeypatch.setenv("VERI_GH_JSON", str(tmp_path))
    scripts = pathlib.Path(solvable_issues.__file__).resolve().parent.parent
    listing = "  1 /sbin/launchd\n 99 bash %s/run-conductor.sh 6\n" % scripts

    def fake_run(args, *rest, **kwargs):
        if list(args[:4]) == ["git", "worktree", "list", "--porcelain"]:
            return subprocess.CompletedProcess(args, 0, "", "")
        if args[0] == "ps":
            return subprocess.CompletedProcess(args, 0, listing, "")
        raise AssertionError("unexpected command: %r" % (args,))

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(subprocess, "Popen", fake_run)

    code = solvable_issues.main([])

    out, err = capsys.readouterr()
    assert (code, out) == (0, "5\n6\n7\n")


def test_main_not_running_omits_the_issue_whose_conductor_is_the_python_interpreter_running_run_conductor_py_from_this_skill_path(tmp_path, monkeypatch, capsys, solvable_issues):
    (tmp_path / "issues.json").write_text(json.dumps([opted_in(5), opted_in(6), opted_in(7)]))
    (tmp_path / "prs.json").write_text("[]")
    monkeypatch.setenv("VERI_GH_JSON", str(tmp_path))
    scripts = pathlib.Path(solvable_issues.__file__).resolve().parent.parent
    listing = "  1 /sbin/launchd\n 99 /usr/bin/python3 %s/veri/run_conductor.py 6\n" % scripts

    def fake_run(args, *rest, **kwargs):
        if list(args[:4]) == ["git", "worktree", "list", "--porcelain"]:
            return subprocess.CompletedProcess(args, 0, "", "")
        if args[0] == "ps":
            return subprocess.CompletedProcess(args, 0, listing, "")
        raise AssertionError("unexpected command: %r" % (args,))

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(subprocess, "Popen", fake_run)

    code = solvable_issues.main(["--not-running"])

    out, err = capsys.readouterr()
    assert (code, out) == (0, "5\n7\n")


def test_main_not_running_returns_3_with_empty_stdout_when_every_solvable_issue_has_a_live_conductor_from_this_skill_path(tmp_path, monkeypatch, capsys, solvable_issues):
    (tmp_path / "issues.json").write_text(json.dumps([opted_in(5), opted_in(6)]))
    (tmp_path / "prs.json").write_text("[]")
    monkeypatch.setenv("VERI_GH_JSON", str(tmp_path))
    scripts = pathlib.Path(solvable_issues.__file__).resolve().parent.parent
    listing = "  1 /sbin/launchd\n 98 bash %s/run-conductor.sh 5\n 99 bash %s/run-conductor.sh 6\n" % (scripts, scripts)

    def fake_run(args, *rest, **kwargs):
        if list(args[:4]) == ["git", "worktree", "list", "--porcelain"]:
            return subprocess.CompletedProcess(args, 0, "", "")
        if args[0] == "ps":
            return subprocess.CompletedProcess(args, 0, listing, "")
        raise AssertionError("unexpected command: %r" % (args,))

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(subprocess, "Popen", fake_run)

    code = solvable_issues.main(["--not-running"])

    out, err = capsys.readouterr()
    assert (code, out) == (3, "")


def test_main_not_running_then_repo_reads_that_repos_issues_and_omits_the_live_conductors_issue(monkeypatch, capsys, solvable_issues):
    monkeypatch.delenv("VERI_GH_JSON", raising=False)
    monkeypatch.setenv("VERI_GH_DRIVER", "auto")
    scripts = pathlib.Path(solvable_issues.__file__).resolve().parent.parent
    listing = "  1 /sbin/launchd\n 99 bash %s/run-conductor.sh 6\n" % scripts
    started = []

    def fake_run(args, *rest, **kwargs):
        args = list(args)
        if args[:4] == ["git", "worktree", "list", "--porcelain"]:
            return subprocess.CompletedProcess(args, 0, "", "")
        if args[0] == "ps":
            return subprocess.CompletedProcess(args, 0, listing, "")
        if args[:3] == ["gh", "issue", "list"]:
            started.append(args[args.index("--repo") + 1:] if "--repo" in args else None)
            return subprocess.CompletedProcess(args, 0, json.dumps([opted_in(5), opted_in(6), opted_in(7)]), "")
        if args[:3] == ["gh", "pr", "list"]:
            return subprocess.CompletedProcess(args, 0, "[]", "")
        raise AssertionError("unexpected command: %r" % (args,))

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(subprocess, "Popen", fake_run)

    code = solvable_issues.main(["--not-running", "--repo", "o/n"])

    out, err = capsys.readouterr()
    assert (code, out, started) == (0, "5\n7\n", [["o/n"]])


def _not_running_with(tmp_path, monkeypatch, capsys, solvable_issues, issues, live):
    (tmp_path / "issues.json").write_text(json.dumps(issues))
    (tmp_path / "prs.json").write_text("[]")
    monkeypatch.setenv("VERI_GH_JSON", str(tmp_path))
    scripts = pathlib.Path(solvable_issues.__file__).resolve().parent.parent
    listing = "  1 /sbin/launchd\n" + "".join(
        " %d /usr/bin/python3 %s/veri/run_conductor.py %d\n" % (100 + n, scripts, n) for n in live)

    def fake_run(args, *rest, **kwargs):
        if list(args[:4]) == ["git", "worktree", "list", "--porcelain"]:
            return subprocess.CompletedProcess(args, 0, "", "")
        if args[0] == "ps":
            return subprocess.CompletedProcess(args, 0, listing, "")
        raise AssertionError("unexpected command: %r" % (args,))

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(subprocess, "Popen", fake_run)
    code = solvable_issues.main(["--not-running"])
    return code, capsys.readouterr().out


def test_main_not_running_omits_a_multi_digit_issue_whose_conductor_is_live_and_keeps_the_issue_its_digits_start_with(tmp_path, monkeypatch, capsys, solvable_issues):
    assert _not_running_with(tmp_path, monkeypatch, capsys, solvable_issues,
                             [opted_in(17), opted_in(1719)], [1719]) == (0, "17\n")


def test_main_not_running_keeps_the_priority_bug_rest_order_of_the_issues_it_does_not_omit(tmp_path, monkeypatch, capsys, solvable_issues):
    def labelled(number, *names):
        issue = opted_in(number)
        issue["labels"] += [{"name": name} for name in names]
        return issue

    issues = [opted_in(1), labelled(8, "bug"), labelled(9, "priority"), opted_in(4), labelled(3, "bug"), labelled(2, "priority")]
    assert _not_running_with(tmp_path, monkeypatch, capsys, solvable_issues, issues, [9, 4]) == (0, "2\n3\n8\n1\n")


def test_main_not_running_1875_keeps_issue_17_listed_for_a_live_conductor_whose_argument_is_17x(tmp_path, monkeypatch, capsys, solvable_issues):
    (tmp_path / "issues.json").write_text(json.dumps([opted_in(17), opted_in(18)]))
    (tmp_path / "prs.json").write_text("[]")
    monkeypatch.setenv("VERI_GH_JSON", str(tmp_path))
    scripts = pathlib.Path(solvable_issues.__file__).resolve().parent.parent
    listing = "  1 /sbin/launchd\n 99 /usr/bin/python3 %s/veri/run_conductor.py 17x\n" % scripts

    def fake_run(args, *rest, **kwargs):
        if list(args[:4]) == ["git", "worktree", "list", "--porcelain"]:
            return subprocess.CompletedProcess(args, 0, "", "")
        if args[0] == "ps":
            return subprocess.CompletedProcess(args, 0, listing, "")
        raise AssertionError("unexpected command: %r" % (args,))

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(subprocess, "Popen", fake_run)

    code = solvable_issues.main(["--not-running"])

    out, err = capsys.readouterr()
    assert (code, out) == (0, "17\n18\n")


def test_main_not_running_1875_keeps_issue_17_listed_for_a_live_conductor_whose_path_has_extra_leading_components(tmp_path, monkeypatch, capsys, solvable_issues):
    (tmp_path / "issues.json").write_text(json.dumps([opted_in(17), opted_in(18)]))
    (tmp_path / "prs.json").write_text("[]")
    monkeypatch.setenv("VERI_GH_JSON", str(tmp_path))
    scripts = pathlib.Path(solvable_issues.__file__).resolve().parent.parent
    listing = "  1 /sbin/launchd\n 99 /usr/bin/python3 /x%s/veri/run_conductor.py 17\n" % scripts

    def fake_run(args, *rest, **kwargs):
        if list(args[:4]) == ["git", "worktree", "list", "--porcelain"]:
            return subprocess.CompletedProcess(args, 0, "", "")
        if args[0] == "ps":
            return subprocess.CompletedProcess(args, 0, listing, "")
        raise AssertionError("unexpected command: %r" % (args,))

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(subprocess, "Popen", fake_run)

    code = solvable_issues.main(["--not-running"])

    out, err = capsys.readouterr()
    assert (code, out) == (0, "17\n18\n")


def test_main_not_running_1875_omits_the_issue_whose_conductor_started_through_a_symlink_to_this_skill_directory_and_keeps_one_from_a_different_real_directory(tmp_path, monkeypatch, capsys, solvable_issues):
    (tmp_path / "issues.json").write_text(json.dumps([opted_in(5), opted_in(6), opted_in(7)]))
    (tmp_path / "prs.json").write_text("[]")
    monkeypatch.setenv("VERI_GH_JSON", str(tmp_path))
    scripts = pathlib.Path(solvable_issues.__file__).resolve().parent.parent
    linked = tmp_path / "skills" / "tdd"
    linked.parent.mkdir()
    linked.symlink_to(scripts)
    elsewhere = tmp_path / "other" / "scripts"
    (elsewhere / "veri").mkdir(parents=True)
    listing = ("  1 /sbin/launchd\n"
               " 98 /usr/bin/python3 %s/veri/run_conductor.py 6\n"
               " 99 /usr/bin/python3 %s/veri/run_conductor.py 7\n") % (linked, elsewhere)

    def fake_run(args, *rest, **kwargs):
        if list(args[:4]) == ["git", "worktree", "list", "--porcelain"]:
            return subprocess.CompletedProcess(args, 0, "", "")
        if args[0] == "ps":
            return subprocess.CompletedProcess(args, 0, listing, "")
        raise AssertionError("unexpected command: %r" % (args,))

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(subprocess, "Popen", fake_run)

    code = solvable_issues.main(["--not-running"])

    out, err = capsys.readouterr()
    assert (code, out) == (0, "5\n7\n")


@pytest.mark.parametrize("argv", [["--repo", "o/n", "--not-running", "extra"], ["--not-running", "--repo", "o/n", "extra"]])
def test_main_1875_refuses_an_unknown_extra_argument_beside_not_running_with_2_and_the_usage_line_alone_reading_no_issue(argv, monkeypatch, capsys, solvable_issues):
    started = no_process(monkeypatch)

    code = solvable_issues.main(argv)

    out, err = capsys.readouterr()
    assert (code, started, out, err) == (2, [], "", USAGE)


def test_main_refuses_any_argument_but_repo_and_not_running_with_2_and_the_usage_line_alone_starting_no_process_bug_1909(monkeypatch, capsys, solvable_issues):
    started = no_process(monkeypatch)

    for argv in (["foo"], ["1875"], ["--repo", "o/n", "--not-runing"], ["--repo=x"], ["--repo", "o/n", "--repo", "x/y"]):
        code = solvable_issues.main(argv)

        out, err = capsys.readouterr()
        assert (argv, code, started, out, err) == (argv, 2, [], "", USAGE)


def test_in_flight_2253_is_false_when_the_lock_pid_answers_kill_0_but_neither_it_nor_its_parent_is_that_issues_conductor(tmp_path, monkeypatch, solvable_issues):
    lock = tmp_path / ".tdd" / "wt" / "7" / ".tdd" / "conductor.pid"
    lock.parent.mkdir(parents=True)
    lock.write_text("%d\n" % os.getpid())
    fake_pid_file_ps(monkeypatch, conductor=False)

    assert solvable_issues.in_flight(str(tmp_path), 7) is False


def test_in_flight_2253_is_true_when_the_lock_pid_answers_kill_0_and_its_command_line_is_that_issues_conductor(tmp_path, monkeypatch, solvable_issues):
    lock = tmp_path / ".tdd" / "wt" / "7" / ".tdd" / "conductor.pid"
    lock.parent.mkdir(parents=True)
    lock.write_text("%d\n" % os.getpid())
    fake_pid_file_ps(monkeypatch)

    assert solvable_issues.in_flight(str(tmp_path), 7) is True


def test_in_flight_2320_is_true_when_the_lock_pid_answers_kill_0_and_every_ps_read_fails(tmp_path, monkeypatch, solvable_issues):
    lock = tmp_path / ".tdd" / "wt" / "7" / ".tdd" / "conductor.pid"
    lock.parent.mkdir(parents=True)
    lock.write_text("4242\n")
    monkeypatch.setattr(os, "kill", lambda pid, signal: None)
    monkeypatch.setattr(subprocess, "run", lambda argv, *a, **k: subprocess.CompletedProcess(argv, 1, stdout="", stderr=""))

    assert solvable_issues.in_flight(str(tmp_path), 7) is True


def test_in_flight_reads_a_fresh_run_whose_worktree_did_not_exist_at_launch_as_in_flight_while_its_conductor_runs_issue_2390(
        tmp_path, monkeypatch, run_cli, solvable_issues):
    past_the_guards(monkeypatch)
    monkeypatch.delenv("VERI_NEW_SKILL", raising=False)
    scratch_tmpdir(tmp_path, monkeypatch)
    run_conductor = importlib.import_module("veri.run_conductor")
    import github
    monkeypatch.setattr(github, "gh_issue_view", lambda number, field: "## Problem\n\nA fresh run.\n")
    fake_claude_exiting(monkeypatch, 0, 0)
    conducting(monkeypatch, 4242)
    answer, seen = subprocess.run, []

    def fake_git(base, *args, **kwargs):
        resolved = args == ("rev-parse", "HEAD")
        out = "1111111111111111111111111111111111111111\n" if resolved else ""
        return subprocess.CompletedProcess(args, 0 if resolved else 2, out if kwargs.get("text") else out.encode(), b"")

    monkeypatch.setattr(run_conductor, "git", fake_git)
    cwd = tmp_path / "cwd"
    cwd.mkdir()

    def reading_the_claim_while_running(args, *rest, **kwargs):
        if list(args)[:1] == ["fake-claude"]:
            if kwargs.get("preexec_fn") is not None:
                kwargs["preexec_fn"]()
            seen.append(solvable_issues.in_flight(str(cwd), 4242))
        return answer(args, *rest, **kwargs)

    monkeypatch.setattr(subprocess, "run", reading_the_claim_while_running)
    assert not (cwd / ".tdd" / "wt" / "4242").exists()

    code, _, err = run_cli(run_conductor, ["4242"], cwd=cwd)

    assert (code, seen, err) == (0, [True], "")


def test_main_not_running_omits_the_issue_2388_whose_live_run_conductor_py_has_a_run_directory_here_with_no_events_and_no_conductor_pid(tmp_path, monkeypatch, capsys, solvable_issues):
    (tmp_path / "issues.json").write_text(json.dumps([opted_in(5), opted_in(6), opted_in(7)]))
    (tmp_path / "prs.json").write_text("[]")
    monkeypatch.setenv("VERI_GH_JSON", str(tmp_path))
    main_tree = tmp_path / "main"
    (main_tree / ".tdd" / "wt" / "6" / ".tdd").mkdir(parents=True)
    listing = "  1 /sbin/launchd\n 99 /usr/bin/python3 /tmp/skill-copy/scripts/veri/run_conductor.py 6\n"

    def fake_run(args, *rest, **kwargs):
        if list(args[:4]) == ["git", "worktree", "list", "--porcelain"]:
            return subprocess.CompletedProcess(args, 0, "worktree %s\n" % main_tree, "")
        if args[0] == "ps":
            return subprocess.CompletedProcess(args, 0, listing, "")
        raise AssertionError("unexpected command: %r" % (args,))

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(subprocess, "Popen", fake_run)

    code = solvable_issues.main(["--not-running"])

    out, err = capsys.readouterr()
    assert (code, out) == (0, "5\n7\n")


def test_main_not_running_keeps_the_issue_2388_whose_live_run_conductor_py_has_no_run_directory_here(tmp_path, monkeypatch, capsys, solvable_issues):
    (tmp_path / "issues.json").write_text(json.dumps([opted_in(5), opted_in(6), opted_in(7)]))
    (tmp_path / "prs.json").write_text("[]")
    monkeypatch.setenv("VERI_GH_JSON", str(tmp_path))
    main_tree = tmp_path / "main"
    (main_tree / ".tdd" / "wt").mkdir(parents=True)
    listing = "  1 /sbin/launchd\n 99 /usr/bin/python3 /tmp/other-repo/scripts/veri/run_conductor.py 6\n"

    def fake_run(args, *rest, **kwargs):
        if list(args[:4]) == ["git", "worktree", "list", "--porcelain"]:
            return subprocess.CompletedProcess(args, 0, "worktree %s\n" % main_tree, "")
        if args[0] == "ps":
            return subprocess.CompletedProcess(args, 0, listing, "")
        raise AssertionError("unexpected command: %r" % (args,))

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(subprocess, "Popen", fake_run)

    code = solvable_issues.main(["--not-running"])

    out, err = capsys.readouterr()
    assert (code, out) == (0, "5\n6\n7\n")
