"""In-process cases for veri/solvable_issues.py, the module solvable-issues.sh is a shim over."""
import collections.abc
import errno
import importlib
import itertools
import json
import os
import pathlib
import re
import pytest
from conftest import fake_pid_file_ps


USAGE = "usage: solvable-issues.sh [--repo owner/name] [--not-running]\n"


@pytest.fixture(autouse=True)
def no_ambient_tunables(monkeypatch):
    for name in ("VERI_GH_JSON", "VERI_LABEL", "VERI_PRIORITY_LABEL"):
        monkeypatch.delenv(name, raising=False)


def conducting(monkeypatch, *numbers):
    """pid_file's ps answering every pid as a claude under run_conductor.py."""
    fake_pid_file_ps(monkeypatch)


@pytest.fixture
def solvable_issues():
    return importlib.import_module("veri.solvable_issues")


class Argvs(collections.abc.Sequence):
    """The argv lists a fake_processes fake has recorded so far, read live: a helper hands one back before the code runs."""

    def __init__(self, fake):
        self.fake = fake

    def __len__(self):
        return len(self.fake.seen)

    def __getitem__(self, index):
        return self.fake.argvs[index]

    def __eq__(self, other):
        return self.fake.argvs == other


def no_process(fake_processes):
    """fake_processes refusing every command it is asked to start, and recording them."""
    return Argvs(fake_processes.answers({}))


@pytest.mark.parametrize("argv", [["--repo"], ["--repo", ""]])
def test_main_refuses_repo_with_no_value_or_an_empty_one_with_2_and_the_usage_line_alone_starting_no_process(fake_processes, argv, monkeypatch, capsys, solvable_issues):
    started = no_process(fake_processes)

    code = solvable_issues.main(argv)

    out, err = capsys.readouterr()
    assert (code, started, out, err) == (2, [], "", USAGE)


@pytest.mark.parametrize("argv", [["--not-running", "--not-running"], ["--repo", "--not-running", "o/n"]])
def test_main_refuses_a_repeated_not_running_or_one_between_repo_and_its_value_with_2_and_the_usage_line_alone_starting_no_process_1909(fake_processes, argv, monkeypatch, capsys, solvable_issues):
    started = no_process(fake_processes)

    code = solvable_issues.main(argv)

    out, err = capsys.readouterr()
    assert (code, started, out, err) == (2, [], "", USAGE)


@pytest.mark.parametrize("argv", [["foo", "bar"], ["o/n", "--repo"]])
def test_main_refuses_two_words_not_starting_with_repo_with_2_and_the_usage_line_alone_starting_no_process_1909(fake_processes, argv, monkeypatch, capsys, solvable_issues):
    started = no_process(fake_processes)

    code = solvable_issues.main(argv)

    out, err = capsys.readouterr()
    assert (code, started, out, err) == (2, [], "", USAGE)


def fake_git_answering_nothing(fake_processes):
    """subprocess.run answering `git worktree list --porcelain` with nothing; any other command fails the case."""
    def fake_run(line, *rest, **kwargs):
        args = fake.argvs[-1]
        if list(args[:4]) != ["git", "worktree", "list", "--porcelain"]:
            raise AssertionError("unexpected command: %r" % (args,))
        return (0, "", "")

    fake = fake_processes.answers({}, default=fake_run)


def opted_in(number):
    return {"number": number, "title": "issue %d" % number, "state": "OPEN", "author_association": "OWNER",
            "labels": [{"name": "ready-for-agent"}], "body": "## Blocked by\n\nNone.\n"}


def test_main_prints_two_open_opted_in_unblocked_issues_one_per_line_ascending_and_returns_0(fake_processes, tmp_path, monkeypatch, capsys, solvable_issues):
    (tmp_path / "issues.json").write_text(json.dumps([opted_in(5), opted_in(6)]))
    (tmp_path / "prs.json").write_text("[]")
    monkeypatch.setenv("VERI_GH_JSON", str(tmp_path))
    fake_git_answering_nothing(fake_processes)

    code = solvable_issues.main([])

    out, err = capsys.readouterr()
    assert (code, out) == (0, "5\n6\n")


def fake_git_answering(fake_processes, main_tree):
    """subprocess.run answering `git worktree list --porcelain` with `worktree <main_tree>`; any other command fails the case."""
    def fake_run(line, *rest, **kwargs):
        args = fake.argvs[-1]
        if list(args[:4]) != ["git", "worktree", "list", "--porcelain"]:
            raise AssertionError("unexpected command: %r" % (args,))
        return (0, "worktree %s\nHEAD 0000000\nbranch refs/heads/main\n" % main_tree, "")

    fake = fake_processes.answers({}, default=fake_run)


def test_main_withholds_the_issue_whose_lock_under_the_main_working_tree_git_names_holds_a_live_pid(fake_processes, tmp_path, monkeypatch, capsys, solvable_issues):
    (tmp_path / "issues.json").write_text(json.dumps([opted_in(5), opted_in(6)]))
    (tmp_path / "prs.json").write_text("[]")
    monkeypatch.setenv("VERI_GH_JSON", str(tmp_path))
    decoy = tmp_path / "decoy"
    lock = decoy / ".tdd" / "wt" / "5" / ".tdd" / "conductor.pid"
    lock.parent.mkdir(parents=True)
    lock.write_text("%d\n" % os.getpid())
    conducting(monkeypatch, 5)
    fake_git_answering(fake_processes, decoy)

    code = solvable_issues.main([])

    out, err = capsys.readouterr()
    assert (code, out) == (0, "6\n")


def record_processes(fake_processes):
    """fake_processes recording every command, answering each with nothing."""
    return Argvs(fake_processes.answers({}, default=(0, "", "")))


def labelled(number, *names):
    return dict(opted_in(number), labels=[{"name": name} for name in names])


def test_main_refuses_an_empty_label_tunable_and_opts_in_by_exact_label_name(fake_processes, tmp_path, monkeypatch, capsys, solvable_issues):
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
        started = record_processes(fake_processes)
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


def fake_gh_refusing_graphql(fake_processes):
    """subprocess.run refusing `gh issue list`/`gh pr list`, answering `gh api` with an empty page and git with nothing; records the gh commands."""
    started = []

    def fake_run(line, *rest, **kwargs):
        args = fake.argvs[-1]
        args = list(args)
        if args[:1] == ["gh"]:
            started.append(args)
            if args[1] == "api":
                return (0, "[]\n", "")
            return (1, "", "")
        if args[:4] == ["git", "worktree", "list", "--porcelain"]:
            return (0, "", "")
        raise AssertionError("unexpected command: %r" % (args,))

    fake = fake_processes.answers({}, default=fake_run)
    return started


@pytest.mark.parametrize("gh_json_dir", [None, ""])
def test_main_reads_issues_then_prs_through_gh_forwarding_repo_verbatim_and_falls_back_to_rest_paths(fake_processes, gh_json_dir, monkeypatch, capsys, solvable_issues):
    if gh_json_dir is not None:
        monkeypatch.setenv("VERI_GH_JSON", gh_json_dir)
    monkeypatch.setenv("VERI_GH_DRIVER", "auto")

    def reads(repo):
        scope = ["--repo", repo] if repo else []
        prefix = "repos/%s" % (repo or "{owner}/{repo}")
        return [
            ["gh", "api", prefix + "/issues?state=open&per_page=100"],
            ["gh", "pr", "list", "--limit", "10000", "--json", "body,state,headRefName,isDraft,isCrossRepository", *scope],
            ["gh", "api", prefix + "/pulls?state=open&per_page=100"],
        ]

    observed = {}
    for argv in ([], ["--repo", "o/n"]):
        started = fake_gh_refusing_graphql(fake_processes)
        solvable_issues.main(argv)
        capsys.readouterr()
        observed[tuple(argv)] = started

    assert observed == {
        (): reads(None),
        ("--repo", "o/n"): reads("o/n"),
    }


def fake_gh_refusing(fake_processes, refused):
    """subprocess.run failing every gh command whose argv holds a word in `refused`, answering the rest with an empty page and git with nothing; records the gh commands."""
    started = []

    def fake_run(line, *rest, **kwargs):
        args = fake.argvs[-1]
        args = list(args)
        if args[:1] == ["gh"]:
            started.append(args)
            if any(word in refused for word in args[1:3]) or any(word in args[-1] for word in refused):
                return (1, "", "")
            return (0, "[]\n", "")
        if args[:4] == ["git", "worktree", "list", "--porcelain"]:
            return (0, "", "")
        raise AssertionError("unexpected command: %r" % (args,))

    fake = fake_processes.answers({}, default=fake_run)
    return started


def test_main_reads_both_documents_returning_2_on_no_answer_raising_on_a_missing_or_broken_one_and_joining_pages_without_prs(fake_processes, tmp_path, monkeypatch, capsys, solvable_issues):
    monkeypatch.setenv("VERI_GH_DRIVER", "auto")

    started = fake_gh_refusing(fake_processes, ("issue", "/issues"))
    code = solvable_issues.main([])
    out, err = capsys.readouterr()
    assert (code, out, [args for args in started if "pr" in args or any("/pulls" in word for word in args)]) == (2, "", [])

    fake_gh_refusing(fake_processes, ("pr", "/pulls"))
    code = solvable_issues.main([])
    out, err = capsys.readouterr()
    assert (code, out) == (2, "")

    fake_git_answering_nothing(fake_processes)
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
def test_solvable_returns_2_and_no_numbers_when_the_issue_or_pr_listing_is_not_readable_json(fake_processes, unreadable, tmp_path, monkeypatch, solvable_issues):
    fake_git_answering_nothing(fake_processes)
    monkeypatch.setenv("VERI_GH_JSON", str(tmp_path))
    (tmp_path / "issues.json").write_text(json.dumps([opted_in(5)]))
    (tmp_path / "prs.json").write_text("[]")
    (tmp_path / unreadable).write_text("not json")

    assert solvable_issues.solvable("ready-for-agent") == (2, [])


def test_main_counts_an_issue_open_by_its_upper_cased_state_and_withholds_one_an_open_pr_closes(fake_processes, tmp_path, monkeypatch, capsys, solvable_issues):
    monkeypatch.setenv("VERI_GH_JSON", str(tmp_path))
    fake_git_answering_nothing(fake_processes)
    stateless = opted_in(2)
    del stateless["state"]
    (tmp_path / "issues.json").write_text(json.dumps([
        dict(opted_in(1), state="open"), stateless, dict(opted_in(3), state="CLOSED"), opted_in(5),
        opted_in(10), opted_in(11), opted_in(12), opted_in(13), opted_in(14), opted_in(50)]))
    (tmp_path / "prs.json").write_text(json.dumps([
        {"isCrossRepository": False, "state": "open", "body": "Closes #10"},
        {"isCrossRepository": False, "state": "CLOSED", "body": "Closes #11"},
        {"isCrossRepository": False, "state": "OPEN", "body": None},
        {"isCrossRepository": False, "state": "OPEN", "body": "closes #12"},
        {"isCrossRepository": False, "state": "OPEN", "body": "Fixes #13"},
        {"isCrossRepository": False, "state": "OPEN", "body": "xCloses #14"},
        {"isCrossRepository": False, "state": "OPEN", "body": "Closes #50"}]))

    code = solvable_issues.main([])

    out, err = capsys.readouterr()
    assert (code, out) == (0, "1\n5\n11\n12\n13\n14\n")

    (tmp_path / "issues.json").write_text(json.dumps([dict(opted_in(5), state=None)]))
    with pytest.raises(AttributeError):
        solvable_issues.main([])


@pytest.mark.parametrize("association, printed", [
    ("OWNER", "5\n"), ("MEMBER", "5\n"), ("COLLABORATOR", "5\n"),
    ("CONTRIBUTOR", ""), ("FIRST_TIME_CONTRIBUTOR", ""), ("FIRST_TIMER", ""), ("NONE", ""),
])
def test_main_takes_an_opted_in_issue_only_when_its_author_is_owner_member_or_collaborator_3977(
        fake_processes, tmp_path, monkeypatch, capsys, solvable_issues, association, printed):
    # A stranger's issue carrying the opt-in label must not be selected (PRD 022.4, AU1): the rule is on the author.
    monkeypatch.setenv("VERI_GH_JSON", str(tmp_path))
    fake_git_answering_nothing(fake_processes)
    (tmp_path / "issues.json").write_text(json.dumps([dict(opted_in(5), author_association=association)]))
    (tmp_path / "prs.json").write_text("[]")

    solvable_issues.main([])

    assert capsys.readouterr().out == printed


def stranger(number, *labels):
    issue = dict(opted_in(number), author_association="NONE")
    issue["labels"] = issue["labels"] + [{"name": label} for label in labels]
    return issue


@pytest.mark.parametrize("env, label, printed", [({}, "author-read", "5\n6\n"), ({"VERI_AUTHOR_LABEL": "seen"}, "seen", "5\n6\n"),
                                                 ({"VERI_AUTHOR_LABEL": "seen"}, "author-read", "6\n")])
def test_main_takes_a_stranger_s_issue_carrying_the_label_veri_author_label_names_3977(
        fake_processes, tmp_path, monkeypatch, capsys, solvable_issues, env, label, printed):
    for name, value in env.items():
        monkeypatch.setenv(name, value)
    monkeypatch.setenv("VERI_GH_JSON", str(tmp_path))
    fake_git_answering_nothing(fake_processes)
    (tmp_path / "issues.json").write_text(json.dumps([stranger(5, label), opted_in(6)]))
    (tmp_path / "prs.json").write_text("[]")

    solvable_issues.main([])

    assert capsys.readouterr().out == printed


def adding(issue, *labels):
    return dict(issue, labels=issue["labels"] + [{"name": label} for label in labels])


def test_main_never_prints_a_stranger_s_priority_bug_and_prints_the_others_in_today_s_order_3977(
        fake_processes, tmp_path, monkeypatch, capsys, solvable_issues):
    monkeypatch.setenv("VERI_GH_JSON", str(tmp_path))
    fake_git_answering_nothing(fake_processes)
    (tmp_path / "issues.json").write_text(json.dumps([
        stranger(3, "priority", "bug"), opted_in(4), adding(opted_in(8), "bug"), adding(opted_in(9), "priority")]))
    (tmp_path / "prs.json").write_text("[]")

    code = solvable_issues.main([])

    assert (code, capsys.readouterr().out) == (0, "9\n8\n4\n")


def test_main_a_stranger_s_open_issue_still_blocks_the_issue_it_names_and_lends_it_its_band_3977(
        fake_processes, tmp_path, monkeypatch, capsys, solvable_issues):
    # Refusing one issue must never unblock another (AU4): #6 names #3 under Blocked by, #3 is open but refused; #3,
    # a priority bug blocked by #12, still lifts #12 into the first band.
    monkeypatch.setenv("VERI_GH_JSON", str(tmp_path))
    fake_git_answering_nothing(fake_processes)
    refused = adding(dict(blocked_by(3, "#12"), author_association="NONE"), "priority", "bug")
    (tmp_path / "issues.json").write_text(json.dumps([refused, blocked_by(6, "#3"), opted_in(10), opted_in(12)]))
    (tmp_path / "prs.json").write_text("[]")

    code = solvable_issues.main([])

    out, err = capsys.readouterr()
    assert (code, out, "#12 inherits priority bug from #3\n" in err) == (0, "12\n10\n", True)


def test_main_exits_3_with_empty_stdout_when_every_otherwise_solvable_issue_is_refused_3977(
        fake_processes, tmp_path, monkeypatch, capsys, solvable_issues):
    monkeypatch.setenv("VERI_GH_JSON", str(tmp_path))
    fake_git_answering_nothing(fake_processes)
    (tmp_path / "issues.json").write_text(json.dumps([stranger(3), stranger(4, "priority")]))
    (tmp_path / "prs.json").write_text("[]")

    code = solvable_issues.main([])

    assert (code, capsys.readouterr().out) == (3, "")


def skipped(number, association, label="author-read"):
    return ("solvable-issues: #%d skipped: its author is %s, not OWNER, MEMBER or COLLABORATOR; label it %s once read\n"
            % (number, association, label))


def test_main_prints_one_stderr_line_per_opted_in_issue_the_author_rule_alone_removes_3977(
        fake_processes, tmp_path, monkeypatch, capsys, solvable_issues):
    # #3 and #5 are removed by the author rule alone; #4 is a stranger's but also blocked, #7 not opted in, #8 taken.
    monkeypatch.setenv("VERI_GH_JSON", str(tmp_path))
    fake_git_answering_nothing(fake_processes)
    unopted = dict(stranger(7), labels=[])
    (tmp_path / "issues.json").write_text(json.dumps([
        stranger(3), dict(blocked_by(4, "#6"), author_association="CONTRIBUTOR"), dict(stranger(5), author_association="FIRST_TIMER"),
        opted_in(6), unopted, stranger(8, "taken:main")]))
    (tmp_path / "prs.json").write_text("[]")

    code = solvable_issues.main([])

    assert (code, capsys.readouterr()) == (0, ("6\n", skipped(3, "NONE") + skipped(5, "FIRST_TIMER")))


@pytest.mark.parametrize("labels, out, err", [((), "", skipped(5, "unknown")), (("author-read",), "5\n", "")])
def test_main_refuses_a_record_with_no_author_association_as_unknown_unless_it_carries_the_override_label_3977(
        fake_processes, tmp_path, monkeypatch, capsys, solvable_issues, labels, out, err):
    monkeypatch.setenv("VERI_GH_JSON", str(tmp_path))
    fake_git_answering_nothing(fake_processes)
    record = adding(opted_in(5), *labels)
    del record["author_association"]
    (tmp_path / "issues.json").write_text(json.dumps([record]))
    (tmp_path / "prs.json").write_text("[]")

    solvable_issues.main([])

    assert capsys.readouterr() == (out, err)


def test_main_refuses_an_empty_veri_author_label_with_2_and_refused_if_empty_s_line_3977(
        fake_processes, tmp_path, monkeypatch, capsys, solvable_issues):
    monkeypatch.setenv("VERI_AUTHOR_LABEL", "")
    monkeypatch.setenv("VERI_GH_JSON", str(tmp_path))
    fake_git_answering_nothing(fake_processes)
    (tmp_path / "issues.json").write_text(json.dumps([opted_in(6)]))
    (tmp_path / "prs.json").write_text("[]")

    code = solvable_issues.main([])

    assert (code, capsys.readouterr()) == (
        2, ("", "solvable-issues: VERI_AUTHOR_LABEL is set but empty: name a label or leave it unset\n"))


def test_main_claims_an_issue_only_by_an_open_pr_whose_head_is_in_this_repository_3973(fake_processes, tmp_path, monkeypatch, capsys, solvable_issues):
    # A stranger's fork PR saying Closes #7 must not take #7 off the queue (PRD 022.14, CL2); the same PR from a branch
    # of this repository claims it. Both shapes: gh pr list's isCrossRepository and REST head.repo against base.repo.
    monkeypatch.setenv("VERI_GH_JSON", str(tmp_path))
    fake_git_answering_nothing(fake_processes)
    (tmp_path / "issues.json").write_text(json.dumps([opted_in(n) for n in (7, 8, 9, 10, 11)]))
    here, fork = {"full_name": "o/r"}, {"full_name": "stranger/r"}
    (tmp_path / "prs.json").write_text(json.dumps([
        {"state": "OPEN", "body": "Closes #7", "headRefName": "fix/7", "isCrossRepository": True},
        {"state": "OPEN", "body": "Closes #8", "head": {"ref": "fix/8", "repo": fork}, "base": {"repo": here}},
        {"state": "OPEN", "body": "Closes #9", "head": {"ref": "fix/9", "repo": None}, "base": {"repo": here}},
        {"state": "OPEN", "body": "Closes #10", "headRefName": "fix/10", "isCrossRepository": False},
        {"state": "OPEN", "body": "Closes #11", "head": {"ref": "fix/11", "repo": here}, "base": {"repo": here}}]))

    code = solvable_issues.main([])

    out, err = capsys.readouterr()
    assert (code, out) == (0, "7\n8\n9\n")


def test_main_lists_a_released_issue_whose_only_open_pr_is_its_own_run_branch(fake_processes, tmp_path, monkeypatch, capsys, solvable_issues):
    # A bailed or parked run keeps its draft PR open (BL36); release-issue.sh restores the opt-in
    # label and drops the claim, and the resume continues that same branch and PR, so a PR on the
    # issue's own tdd/<n>- branch is no claim. Any other branch's PR still is.
    monkeypatch.setenv("VERI_GH_JSON", str(tmp_path))
    fake_git_answering_nothing(fake_processes)
    (tmp_path / "issues.json").write_text(json.dumps([opted_in(n) for n in (20, 21, 22, 23, 24)]))
    (tmp_path / "prs.json").write_text(json.dumps([
        {"isCrossRepository": False, "state": "OPEN", "body": "Closes #20", "headRefName": "tdd/20-check-earlier"},
        {"isCrossRepository": False, "state": "OPEN", "body": "Closes #21", "head": {"ref": "tdd/21-from-rest"}},
        {"isCrossRepository": False, "state": "OPEN", "body": "Closes #22", "headRefName": "fix/22-by-hand"},
        {"isCrossRepository": False, "state": "OPEN", "body": "Closes #23", "headRefName": "tdd/230-another-issue"},
        {"isCrossRepository": False, "state": "OPEN", "body": "Closes #24"}]))

    code = solvable_issues.main([])

    out, err = capsys.readouterr()
    assert (code, out) == (0, "20\n21\n")


def test_main_3460_withholds_an_issue_whose_own_run_branch_pr_is_ready_and_lists_one_whose_own_run_branch_pr_is_still_a_draft(fake_processes, tmp_path, monkeypatch, capsys, solvable_issues):
    monkeypatch.setenv("VERI_GH_JSON", str(tmp_path))
    fake_git_answering_nothing(fake_processes)
    (tmp_path / "issues.json").write_text(json.dumps([opted_in(n) for n in (30, 31)]))
    (tmp_path / "prs.json").write_text(json.dumps([
        {"isCrossRepository": False, "state": "OPEN", "body": "Closes #30", "headRefName": "tdd/30-done-run", "isDraft": False},
        {"isCrossRepository": False, "state": "OPEN", "body": "Closes #31", "headRefName": "tdd/31-released-run", "isDraft": True}]))

    code = solvable_issues.main([])

    out, err = capsys.readouterr()
    assert (code, out) == (0, "31\n")


def test_main_3460_withholds_an_issue_whose_rest_own_run_branch_pr_carries_draft_false(fake_processes, tmp_path, monkeypatch, capsys, solvable_issues):
    monkeypatch.setenv("VERI_GH_JSON", str(tmp_path))
    fake_git_answering_nothing(fake_processes)
    (tmp_path / "issues.json").write_text(json.dumps([opted_in(n) for n in (40, 41)]))
    (tmp_path / "prs.json").write_text(json.dumps([
        {"isCrossRepository": False, "state": "OPEN", "body": "Closes #40", "head": {"ref": "tdd/40-done-run"}, "draft": False},
        {"isCrossRepository": False, "state": "OPEN", "body": "Closes #41", "head": {"ref": "tdd/41-released-run"}, "draft": True}]))

    code = solvable_issues.main([])

    out, err = capsys.readouterr()
    assert (code, out) == (0, "41\n")


def blocked_by(number, *refs):
    return dict(opted_in(number), body="## Blocked by\n\n" + "".join("- %s\n" % ref for ref in refs) + "\n## Notes\n\n#1\n")


def test_main_withholds_an_issue_blocked_by_an_open_fetched_issue_as_number_or_url_reading_other_repos_urls_only_under_repo(fake_processes, tmp_path, monkeypatch, capsys, solvable_issues):
    monkeypatch.setenv("VERI_GH_JSON", str(tmp_path))
    fake_git_answering_nothing(fake_processes)
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


def test_main_sorts_survivors_by_priority_then_bug_band_then_number_never_widening_the_pool_and_returns_3_when_none_survive(fake_processes, tmp_path, monkeypatch, capsys, solvable_issues):
    monkeypatch.setenv("VERI_GH_JSON", str(tmp_path))
    fake_git_answering_nothing(fake_processes)
    (tmp_path / "issues.json").write_text(json.dumps([
        opted_in(1), labelled(2, "ready-for-agent", "bug"), labelled(3, "ready-for-agent", "priority"),
        labelled(4, "priority", "bug"), dict(blocked_by(5, "#10"), labels=[{"name": "ready-for-agent"}, {"name": "priority"}]),
        labelled(6, "ready-for-agent", "bug"), dict(labelled(7, "ready-for-agent", "priority"), state="CLOSED"),
        labelled(8, "ready-for-agent", "bug", "priority"), labelled(9, "ready-for-agent", "urgent"), labelled(10, "urgent")]))
    (tmp_path / "prs.json").write_text(json.dumps([{"isCrossRepository": False, "state": "OPEN", "body": "Closes #6"}]))

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

    assert observed == [(0, "8\n3\n2\n1\n9\n"), (0, "9\n2\n8\n1\n3\n"), (3, "")]


def cli_fixtures(tmp_path, fake_processes, issues):
    """A VERI_GH_JSON directory holding `issues` and no PRs, a separate working directory, and git answering nothing."""
    fixtures, cwd = tmp_path / "fixtures", tmp_path / "cwd"
    fixtures.mkdir()
    cwd.mkdir()
    (fixtures / "issues.json").write_text(json.dumps(issues))
    (fixtures / "prs.json").write_text("[]")
    fake_git_answering_nothing(fake_processes)
    return fixtures, cwd


def test_cli_lists_an_open_opted_in_unblocked_issue_run_from_its_own_cwd_returning_0_with_empty_stderr(fake_processes, tmp_path, monkeypatch, run_cli, solvable_issues):
    fixtures, cwd = cli_fixtures(tmp_path, fake_processes, [opted_in(41)])

    answer = run_cli(solvable_issues, [], env={"VERI_GH_JSON": str(fixtures)}, cwd=cwd)

    assert answer == (0, "41\n", "")


def test_cli_with_the_label_tunable_unset_never_lists_an_issue_whose_only_label_extends_ready_for_agent(fake_processes, tmp_path, monkeypatch, run_cli, solvable_issues):
    fixtures, cwd = cli_fixtures(tmp_path, fake_processes, [opted_in(62), labelled(63, "ready-for-agent:docs")])

    answer = run_cli(solvable_issues, [], env={"VERI_GH_JSON": str(fixtures)}, cwd=cwd)

    assert answer == (0, "62\n", "")


def test_cli_prints_issues_fetched_out_of_order_one_per_line_ascending(fake_processes, tmp_path, monkeypatch, run_cli, solvable_issues):
    fixtures, cwd = cli_fixtures(tmp_path, fake_processes, [opted_in(12), opted_in(3), opted_in(7)])

    answer = run_cli(solvable_issues, [], env={"VERI_GH_JSON": str(fixtures)}, cwd=cwd)

    assert answer == (0, "3\n7\n12\n", "")


def test_cli_lists_an_issue_carrying_both_labels_under_the_default_label_and_under_the_docs_label(fake_processes, tmp_path, monkeypatch, run_cli, solvable_issues):
    fixtures, cwd = cli_fixtures(tmp_path, fake_processes, [labelled(66, "ready-for-agent", "ready-for-agent:docs")])

    under_default = run_cli(solvable_issues, [], env={"VERI_GH_JSON": str(fixtures)}, cwd=cwd)
    under_docs = run_cli(solvable_issues, [], env={"VERI_GH_JSON": str(fixtures), "VERI_LABEL": "ready-for-agent:docs"}, cwd=cwd)

    assert (under_default, under_docs) == ((0, "66\n", ""), (0, "66\n", ""))


def test_cli_refuses_an_empty_label_tunable_with_2_nothing_on_stdout_and_a_diagnostic_on_stderr(fake_processes, tmp_path, monkeypatch, run_cli, solvable_issues):
    fixtures, cwd = cli_fixtures(tmp_path, fake_processes, [opted_in(67), labelled(68, "ready-for-agent:docs")])

    answer = run_cli(solvable_issues, [], env={"VERI_GH_JSON": str(fixtures), "VERI_LABEL": ""}, cwd=cwd)

    assert answer == (2, "", "solvable-issues: VERI_LABEL is set but empty: name a label or leave it unset\n")


@pytest.mark.parametrize("state, listed", [("OPEN", "120\n"), ("CLOSED", "125\n")])
def test_cli_withholds_an_issue_blocked_by_a_github_issue_url_exactly_while_that_issue_is_open(fake_processes, state, listed, tmp_path, monkeypatch, run_cli, solvable_issues):
    fixtures, cwd = cli_fixtures(tmp_path, fake_processes, [
        blocked_by(125, "https://github.com/ztrange/veri/issues/120"), dict(opted_in(120), state=state)])

    answer = run_cli(solvable_issues, [], env={"VERI_GH_JSON": str(fixtures)}, cwd=cwd)

    assert answer == (0, listed, "")


def test_cli_under_repo_never_reads_a_url_naming_another_repositorys_issue_as_a_blocker(fake_processes, tmp_path, monkeypatch, run_cli, solvable_issues):
    fixtures, cwd = cli_fixtures(tmp_path, fake_processes, [
        blocked_by(131, "https://github.com/ztrange/veri-demo-node/issues/120"), opted_in(120)])

    answer = run_cli(solvable_issues, ["--repo", "ztrange/veri"], env={"VERI_GH_JSON": str(fixtures)}, cwd=cwd)

    assert answer == (0, "120\n131\n", "")


def test_cli_prints_a_bug_labelled_issue_ahead_of_a_lower_numbered_plain_one_each_band_ascending(fake_processes, tmp_path, monkeypatch, run_cli, solvable_issues):
    fixtures, cwd = cli_fixtures(tmp_path, fake_processes, [
        opted_in(201), labelled(205, "ready-for-agent", "bug"), opted_in(202), labelled(203, "ready-for-agent", "bug")])

    answer = run_cli(solvable_issues, [], env={"VERI_GH_JSON": str(fixtures)}, cwd=cwd)

    assert answer == (0, "203\n205\n201\n202\n", "")


def test_cli_prints_a_priority_bug_ahead_of_a_lower_numbered_priority_issue_and_that_ahead_of_a_lower_numbered_bug(fake_processes, tmp_path, monkeypatch, run_cli, solvable_issues):
    fixtures, cwd = cli_fixtures(tmp_path, fake_processes, [
        labelled(120, "ready-for-agent", "bug"), labelled(160, "bug", "ready-for-agent", "priority"),
        labelled(150, "priority", "ready-for-agent"), labelled(170, "bug", "ready-for-agent", "priority")])

    answer = run_cli(solvable_issues, [], env={"VERI_GH_JSON": str(fixtures)}, cwd=cwd)

    assert answer == (0, "160\n170\n150\n120\n", "")


def test_cli_lets_a_blocker_inherit_priority_bug_through_an_unlabelled_unopted_middle_issue_ahead_of_a_lower_numbered_priority_issue(fake_processes, tmp_path, monkeypatch, run_cli, solvable_issues):
    middle = {"number": 40, "title": "issue 40", "state": "OPEN", "labels": [], "body": "## Blocked by\n\n- #30\n"}
    held = dict(labelled(50, "bug", "priority", "ready-for-agent"), body="## Blocked by\n\n- #40\n")
    fixtures, cwd = cli_fixtures(tmp_path, fake_processes, [labelled(10, "priority", "ready-for-agent"), opted_in(30), middle, held])

    code, out, _ = run_cli(solvable_issues, [], env={"VERI_GH_JSON": str(fixtures)}, cwd=cwd)

    assert (code, out) == (0, "30\n10\n")


def test_cli_lets_an_opted_in_blocker_of_an_unopted_priority_bug_print_ahead_of_a_lower_numbered_priority_issue_and_a_bug(fake_processes, tmp_path, monkeypatch, run_cli, solvable_issues):
    held = dict(labelled(50, "bug", "priority"), body="## Blocked by\n\n- #30\n")
    fixtures, cwd = cli_fixtures(tmp_path, fake_processes, [
        labelled(10, "priority", "ready-for-agent"), labelled(20, "bug", "ready-for-agent"), opted_in(30), held])

    code, out, _ = run_cli(solvable_issues, [], env={"VERI_GH_JSON": str(fixtures)}, cwd=cwd)

    assert (code, out) == (0, "30\n10\n20\n")


def test_cli_lets_an_opted_in_blocker_of_only_a_priority_issue_print_after_a_higher_numbered_priority_bug_and_before_a_lower_numbered_bug(fake_processes, tmp_path, monkeypatch, run_cli, solvable_issues):
    held = dict(labelled(50, "priority"), body="## Blocked by\n\n- #30\n")
    fixtures, cwd = cli_fixtures(tmp_path, fake_processes, [
        labelled(20, "bug", "ready-for-agent"), opted_in(30), labelled(40, "bug", "priority", "ready-for-agent"), held])

    code, out, _ = run_cli(solvable_issues, [], env={"VERI_GH_JSON": str(fixtures)}, cwd=cwd)

    assert (code, out) == (0, "40\n30\n20\n")


def test_cli_keeps_an_opted_in_blocker_of_only_a_plain_bug_in_its_own_band_after_a_higher_numbered_bug(fake_processes, tmp_path, monkeypatch, run_cli, solvable_issues):
    held = dict(labelled(50, "bug"), body="## Blocked by\n\n- #30\n")
    fixtures, cwd = cli_fixtures(tmp_path, fake_processes, [opted_in(30), labelled(40, "bug", "ready-for-agent"), held])

    code, out, _ = run_cli(solvable_issues, [], env={"VERI_GH_JSON": str(fixtures)}, cwd=cwd)

    assert (code, out) == (0, "40\n30\n")


def test_cli_terminates_on_a_blocked_by_cycle_among_open_issues_printing_each_solvable_number_once(fake_processes, tmp_path, monkeypatch, run_cli, solvable_issues):
    loop_a = dict(labelled(60, "bug", "priority", "ready-for-agent"), body="## Blocked by\n\n- #61\n")
    loop_b = dict(labelled(61, "ready-for-agent"), body="## Blocked by\n\n- #60\n- #70\n")
    fixtures, cwd = cli_fixtures(tmp_path, fake_processes, [labelled(50, "ready-for-agent", "bug"), opted_in(70), loop_a, loop_b])

    code, out, _ = run_cli(solvable_issues, [], env={"VERI_GH_JSON": str(fixtures)}, cwd=cwd)

    assert (code, out) == (0, "70\n50\n")


def test_cli_leaves_a_low_risk_bug_to_its_number_among_the_plain_issues_ahead_of_it_only_a_priority_and_other_bugs(fake_processes, tmp_path, monkeypatch, run_cli, solvable_issues):
    fixtures, cwd = cli_fixtures(tmp_path, fake_processes, [
        opted_in(210), labelled(215, "ready-for-agent", "bug", "low-risk"), opted_in(220), labelled(225, "ready-for-agent", "bug"),
        labelled(230, "ready-for-agent", "bug", "low-risk", "priority"), labelled(205, "ready-for-agent", "low-risk")])

    answer = run_cli(solvable_issues, [], env={"VERI_GH_JSON": str(fixtures)}, cwd=cwd)

    assert answer == (0, "230\n225\n205\n210\n215\n220\n", "")


def test_cli_never_opts_in_an_issue_by_the_priority_label_alone(fake_processes, tmp_path, monkeypatch, run_cli, solvable_issues):
    fixtures, cwd = cli_fixtures(tmp_path, fake_processes, [labelled(170, "priority"), opted_in(180)])

    answer = run_cli(solvable_issues, [], env={"VERI_GH_JSON": str(fixtures)}, cwd=cwd)

    assert answer == (0, "180\n", "")


def test_cli_never_lists_an_issue_carrying_a_taken_label_even_with_the_opt_in_label_while_an_opt_in_only_issue_is_listed(fake_processes, tmp_path, monkeypatch, run_cli, solvable_issues):
    fixtures, cwd = cli_fixtures(tmp_path, fake_processes, [
        labelled(200, "ready-for-agent", "taken:main"), labelled(210, "ready-for-agent", "taken:mu"), opted_in(220)])

    answer = run_cli(solvable_issues, [], env={"VERI_GH_JSON": str(fixtures)}, cwd=cwd)

    assert answer == (0, "220\n", "")


def test_cli_never_lists_an_issue_labelled_parked_even_when_it_carries_the_opt_in_label(fake_processes, tmp_path, monkeypatch, run_cli, solvable_issues):
    fixtures, cwd = cli_fixtures(tmp_path, fake_processes, [labelled(190, "ready-for-agent", "parked"), opted_in(200)])

    answer = run_cli(solvable_issues, [], env={"VERI_GH_JSON": str(fixtures)}, cwd=cwd)

    assert answer == (0, "200\n", "")


def test_cli_never_lists_an_issue_labelled_draft_even_when_it_carries_the_opt_in_label(fake_processes, tmp_path, monkeypatch, run_cli, solvable_issues):
    fixtures, cwd = cli_fixtures(tmp_path, fake_processes, [labelled(190, "ready-for-agent", "draft"), opted_in(200)])

    answer = run_cli(solvable_issues, [], env={"VERI_GH_JSON": str(fixtures)}, cwd=cwd)

    assert answer == (0, "200\n", "")


def test_cli_still_withholds_a_priority_or_bug_issue_that_is_blocked_claimed_or_closed(fake_processes, tmp_path, monkeypatch, run_cli, solvable_issues):
    fixtures, cwd = cli_fixtures(tmp_path, fake_processes, [
        labelled(189), dict(blocked_by(190, "#189"), labels=[{"name": "ready-for-agent"}, {"name": "priority"}]),
        labelled(191, "ready-for-agent", "bug"), dict(labelled(192, "ready-for-agent", "priority"), state="CLOSED"),
        opted_in(195)])
    (fixtures / "prs.json").write_text(json.dumps([{"isCrossRepository": False, "state": "OPEN", "body": "Closes #191\n"}]))

    answer = run_cli(solvable_issues, [], env={"VERI_GH_JSON": str(fixtures)}, cwd=cwd)

    assert answer == (0, "195\n", "")


def test_cli_refuses_an_empty_priority_label_tunable_with_2_and_a_diagnostic_and_unset_defaults_to_priority(fake_processes, tmp_path, monkeypatch, run_cli, solvable_issues):
    fixtures, cwd = cli_fixtures(tmp_path, fake_processes, [opted_in(100), labelled(200, "ready-for-agent", "priority")])

    unset = run_cli(solvable_issues, [], env={"VERI_GH_JSON": str(fixtures)}, cwd=cwd)
    refused = run_cli(solvable_issues, [], env={"VERI_GH_JSON": str(fixtures), "VERI_PRIORITY_LABEL": ""}, cwd=cwd)

    assert (refused, unset) == (
        (2, "", "solvable-issues: VERI_PRIORITY_LABEL is set but empty: name a label or leave it unset\n"),
        (0, "200\n100\n", ""))


def test_cli_with_no_issue_carrying_a_band_label_prints_the_solvable_issues_ascending(fake_processes, tmp_path, monkeypatch, run_cli, solvable_issues):
    fixtures, cwd = cli_fixtures(tmp_path, fake_processes, [
        opted_in(210), opted_in(208), opted_in(207), blocked_by(209, "#212"), labelled(211), labelled(212),
        dict(opted_in(213), state="CLOSED")])
    (fixtures / "prs.json").write_text(json.dumps([{"isCrossRepository": False, "state": "OPEN", "body": "Closes #207\n"}]))

    answer = run_cli(solvable_issues, [], env={"VERI_GH_JSON": str(fixtures)}, cwd=cwd)

    assert answer == (0, "208\n210\n", "")


def fake_gh_paging(fake_processes, issues, prs):
    """subprocess.run answering the REST open-issue page with <issues>, `gh issue list`/`gh pr list` with the first --limit items, 30 when none is given, and git with nothing."""
    def fake_run(line, *rest, **kwargs):
        args = fake.argvs[-1]
        args = list(args)
        if args[:4] == ["git", "worktree", "list", "--porcelain"]:
            return (0, "", "")
        if args[:2] == ["gh", "api"] and args[2] == "repos/{owner}/{repo}/issues?state=open&per_page=100":
            return (0, json.dumps(issues) + "\n", "")
        if args[:1] != ["gh"] or args[2:3] != ["list"] or args[1] not in ("issue", "pr"):
            raise AssertionError("unexpected command: %r" % (args,))
        limit = int(args[args.index("--limit") + 1]) if "--limit" in args else 30
        listing = issues if args[1] == "issue" else prs
        return (0, json.dumps(listing[:limit]) + "\n", "")

    fake = fake_processes.answers({}, default=fake_run)


def newest_first(numbers, overrides):
    return [overrides.get(n, labelled(n)) for n in numbers]


@pytest.mark.parametrize("issues, prs, answer", [
    (newest_first(range(140, 100, -1), {101: opted_in(101)}), [], (0, "101\n", "")),
    (newest_first(range(140, 100, -1), {140: blocked_by(140, "#101")}), [], (3, "", "")),
    ([opted_in(7)], [{"isCrossRepository": False, "state": "OPEN", "body": "Closes #7" if i == 39 else "Closes #%d" % (1000 + i)} for i in range(40)],
     (3, "", "")),
], ids=["opted-in-issue", "open-blocker", "closes-pr"])
def test_cli_honours_an_item_older_than_ghs_default_page_of_30(fake_processes, issues, prs, answer, tmp_path, monkeypatch, run_cli, solvable_issues):
    fake_gh_paging(fake_processes, issues, prs)

    assert run_cli(solvable_issues, [], env={"VERI_GH_DRIVER": "auto"}, cwd=tmp_path) == answer


REPO_ROOT = pathlib.Path(__file__).resolve().parents[6]


def test_main_repo_then_not_running_reads_that_repos_issues_and_omits_the_live_conductors_issue(fake_processes, monkeypatch, capsys, solvable_issues):
    monkeypatch.delenv("VERI_GH_JSON", raising=False)
    monkeypatch.setenv("VERI_GH_DRIVER", "auto")
    scripts = pathlib.Path(solvable_issues.__file__).resolve().parent.parent
    listing = "  1 /sbin/launchd\n 99 bash %s/run-conductor.sh 6\n" % scripts
    started = []

    def fake_run(line, *rest, **kwargs):
        args = fake.argvs[-1]
        args = list(args)
        if args[:4] == ["git", "worktree", "list", "--porcelain"]:
            return (0, "", "")
        if args[0] == "ps":
            return (0, listing, "")
        if args[:2] == ["gh", "api"] and args[2].endswith("/issues?state=open&per_page=100"):
            started.append(args[2].split("/")[1:3])
            return (0, json.dumps([opted_in(5), opted_in(6), opted_in(7)]), "")
        if args[:3] == ["gh", "pr", "list"]:
            return (0, "[]", "")
        raise AssertionError("unexpected command: %r" % (args,))

    fake = fake_processes.answers({}, default=fake_run)

    code = solvable_issues.main(["--repo", "o/n", "--not-running"])

    out, err = capsys.readouterr()
    assert (code, out, started) == (0, "5\n7\n", [["o", "n"]])


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


def test_passage_says_the_open_pr_is_the_claim_and_the_pid_lock_one_machines_worktree_guard_citing_its_adr():
    texts = header_paragraphs()
    missing = [tag for tag, patterns in CLAIMS.items()
               if not any(all(re.search(pattern, text) for pattern in patterns) for text in texts)]

    assert missing == []


@pytest.mark.parametrize("driver", ["", "REST", "gql"])
def test_cli_with_an_unknown_gh_driver_starts_no_process_prints_nothing_and_returns_2_with_one_stderr_line_naming_the_variable_and_value(fake_processes, driver, tmp_path, run_cli, monkeypatch, solvable_issues):
    started = no_process(fake_processes)

    code, out, err = run_cli(solvable_issues, [], env={"VERI_GH_DRIVER": driver}, cwd=tmp_path)

    assert (code, started, out, len(err.splitlines()), "VERI_GH_DRIVER" in err, "'%s'" % driver in err) == (2, [], "", 1, True, True)


def test_cli_refuses_repo_with_no_value_with_2_nothing_on_stdout_and_stderr_exactly_the_usage_line(fake_processes, tmp_path, monkeypatch, run_cli, solvable_issues):
    fixtures, cwd = cli_fixtures(tmp_path, fake_processes, [])

    answer = run_cli(solvable_issues, ["--repo"], env={"VERI_GH_JSON": str(fixtures)}, cwd=cwd)

    assert answer == (2, "", USAGE)


def write_gh_fixtures(directory, issues):
    directory.mkdir()
    (directory / "issues.json").write_text(json.dumps(issues))
    (directory / "prs.json").write_text("[]")


ARG_MAX_STRLEN = 131072


def fake_git_refusing_long_arguments(fake_processes):
    """subprocess.run refusing any argument over 128 KiB the way Linux does, answering `git worktree list --porcelain` with nothing."""
    def fake_run(line, *rest, **kwargs):
        args = fake.argvs[-1]
        if any(len(str(arg)) > ARG_MAX_STRLEN for arg in args):
            raise OSError(errno.E2BIG, "Argument list too long")
        if list(args[:4]) != ["git", "worktree", "list", "--porcelain"]:
            raise AssertionError("unexpected command: %r" % (args,))
        return (0, "", "")

    fake = fake_processes.answers({}, default=fake_run)


def test_cli_reads_an_issues_document_over_256_kib_to_the_same_answer_as_short_bodies_under_a_128_kib_argument_limit(fake_processes, tmp_path, monkeypatch, run_cli, solvable_issues):
    def issues(pad):
        return [dict(opted_in(n), labels=[{"name": "ready-for-agent"}] if n % 2 == 0 else [],
                     body="## What to build\n\n" + pad + "\n\n## Blocked by\n\nNone.\n") for n in range(1, 41)]

    short, long, cwd = tmp_path / "short", tmp_path / "long", tmp_path / "cwd"
    for fixtures, pad in ((short, "short"), (long, "x" * 8192)):
        write_gh_fixtures(fixtures, issues(pad))
    cwd.mkdir()
    fake_git_refusing_long_arguments(fake_processes)
    want = (0, "".join("%d\n" % n for n in range(2, 41, 2)), "")

    answers = [run_cli(solvable_issues, [], env={"VERI_GH_JSON": str(fixtures)}, cwd=cwd) for fixtures in (short, long)]

    assert ((long / "issues.json").stat().st_size > 262144, answers) == (True, [want, want])


def rest_page(request, items):
    """The page of `items` a `gh api` listing request path asks for: filtered by its state, sorted by its direction, cut by its per_page and page."""
    params = dict(pair.split("=") for pair in request.partition("?")[2].split("&"))
    items = [item for item in items if params["state"] == "all" or item["state"].lower() == params["state"]]
    items.sort(key=lambda item: item["number"], reverse=params.get("direction", "desc") == "desc")
    size, page = int(params["per_page"]), int(params.get("page", 1))
    return items[(page - 1) * size:page * size]


def fake_gh_api_shifting(fake_processes, listings):
    """subprocess.run answering `gh api <path>` from `listings` (endpoint -> items), closing the first item a listing serves once its first page has gone out; records the gh api paths and answers git with nothing."""
    requests, closed = [], {}

    def fake_run(line, *rest, **kwargs):
        args = fake.argvs[-1]
        args = list(args)
        if args[:4] == ["git", "worktree", "list", "--porcelain"]:
            return (0, "", "")
        if args[:2] != ["gh", "api"] or len(args) != 3:
            raise AssertionError("unexpected command: %r" % (args,))
        requests.append(args[2])
        endpoint = args[2].partition("?")[0].rsplit("/", 1)[1]
        shut = closed.setdefault(endpoint, set())
        served = rest_page(args[2], [dict(item, state="closed") if item["number"] in shut else item for item in listings[endpoint]])
        if served and not shut:
            shut.add(served[0]["number"])
        return (0, json.dumps(served) + "\n", "")

    fake = fake_processes.answers({}, default=fake_run)
    return requests


@pytest.mark.parametrize("endpoint", ["issues", "pulls"])
def test_cli_reads_the_open_listing_in_one_request_under_100_open_items_and_the_grow_only_listing_at_100_or_more_even_as_pages_shift(fake_processes, endpoint, tmp_path, monkeypatch, run_cli, solvable_issues):
    prefix = "repos/{owner}/{repo}/%s" % endpoint
    open_page, grow_only = prefix + "?state=open&per_page=100", prefix + "?state=all&sort=created&direction=asc&per_page=100&page=%d"

    def answer(count):
        if endpoint == "issues":
            listings = {"issues": [opted_in(n) if 1 < n < count else labelled(n) for n in range(1, count + 1)], "pulls": []}
            solvable = range(2, count)
        else:
            claim = {40: 230, 100: 250, 130: 205}[count]
            listings = {"issues": [opted_in(n) for n in range(1, 11)],
                        "pulls": [{"number": n, "isCrossRepository": False, "state": "open", "body": "Closes #5" if n == claim else "Tidies something."}
                                  for n in range(201, 201 + count)]}
            solvable = [n for n in range(1, 11) if n != 5]
        requests = fake_gh_api_shifting(fake_processes, listings)
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


def fake_gh_refusing_graphql_serving_rest(fake_processes, listings):
    """subprocess.run failing `gh issue`/`gh pr` with the 403 and answering `gh api repos/{owner}/{repo}/<endpoint>?...` a page at a time from `listings` (endpoint -> items); git answers nothing."""
    def fake_run(line, *rest, **kwargs):
        args = fake.argvs[-1]
        args = list(args)
        if args[:4] == ["git", "worktree", "list", "--porcelain"]:
            return (0, "", "")
        if args[:1] != ["gh"]:
            raise AssertionError("unexpected command: %r" % (args,))
        if args[1] in ("issue", "pr", "repo"):
            return (1, "", "HTTP 403: GitHub GraphQL is not available from Claude Code sessions\n")
        if args[1] != "api" or len(args) != 3 or not args[2].startswith("repos/{owner}/{repo}/"):
            raise AssertionError("unexpected command: %r" % (args,))
        served = rest_page(args[2], listings[args[2].partition("?")[0].rsplit("/", 1)[1]])
        return (0, json.dumps(served) + "\n", "")

    fake = fake_processes.answers({}, default=fake_run)


@pytest.mark.parametrize("driver", ["rest", "auto", "graphql"])
def test_cli_reads_each_issue_s_author_association_under_every_gh_driver_3977(
        fake_processes, monkeypatch, run_cli, solvable_issues, driver):
    # gh issue list --json offers no association field: read the issue listing over REST whatever the driver, so the
    # author rule has its fact; a record that truly lacks it is still refused as unknown.
    monkeypatch.setenv("VERI_GH_DRIVER", driver)
    monkeypatch.delenv("VERI_GH_JSON", raising=False)
    nameless = opted_in(7)
    del nameless["author_association"]
    rest = [opted_in(5), dict(opted_in(6), author_association="NONE"), nameless]
    graphql = [{key: value for key, value in issue.items() if key != "author_association"} for issue in rest]

    def fake_run(line, *more, **kwargs):
        args = list(fake.argvs[-1])
        if args[:4] == ["git", "worktree", "list", "--porcelain"]:
            return (0, "", "")
        if args[:3] == ["gh", "issue", "list"]:
            return (0, json.dumps(graphql), "")
        if args[:3] == ["gh", "pr", "list"]:
            return (0, "[]", "")
        if args[:2] == ["gh", "api"] and "/issues?" in args[2]:
            return (0, json.dumps(rest), "")
        if args[:2] == ["gh", "api"] and "/pulls?" in args[2]:
            return (0, "[]", "")
        raise AssertionError("unexpected command: %r" % (args,))

    fake = fake_processes.answers({}, default=fake_run)

    code, out, err = run_cli(solvable_issues, [])

    assert (code, out, err) == (0, "5\n", skipped(6, "NONE") + skipped(7, "unknown"))


def test_cli_against_a_gh_that_refuses_graphql_with_the_403_and_answers_rest_under_repos_owner_repo_a_page_at_a_time_prints_the_same_issue_numbers_and_exit_code_with_empty_stderr_across_more_than_one_100_item_page(fake_processes, tmp_path, monkeypatch, run_cli, solvable_issues):
    issues = [labelled(100 + k) for k in range(110)] + [
        opted_in(70), dict(opted_in(71), body="## Blocked by\n\n#72\n"), labelled(72), opted_in(73),
        dict(opted_in(74), labels=[{"name": "ready-for-agent"}, {"name": "priority"}])]
    pulls = [{"number": 1 + k, "state": "OPEN", "body": ""} for k in range(105)] + [
        {"number": 900, "isCrossRepository": False, "state": "OPEN", "body": "Draft PR opened by a /tdd run.\n\nCloses #73\n"}]
    fake_gh_refusing_graphql_serving_rest(fake_processes, {"issues": issues, "pulls": pulls})

    answer = run_cli(solvable_issues, [], env={"VERI_GH_DRIVER": "auto"}, cwd=tmp_path)

    assert answer == (0, "74\n70\n", "")


def test_main_not_running_omits_the_issue_with_a_live_conductor_from_this_skill_path_and_keeps_the_rest_in_order(fake_processes, tmp_path, monkeypatch, capsys, solvable_issues):
    (tmp_path / "issues.json").write_text(json.dumps([opted_in(5), opted_in(6), opted_in(7)]))
    (tmp_path / "prs.json").write_text("[]")
    monkeypatch.setenv("VERI_GH_JSON", str(tmp_path))
    scripts = pathlib.Path(solvable_issues.__file__).resolve().parent.parent
    listing = "  1 /sbin/launchd\n 99 bash %s/run-conductor.sh 6\n" % scripts

    def fake_run(line, *rest, **kwargs):
        args = fake.argvs[-1]
        if list(args[:4]) == ["git", "worktree", "list", "--porcelain"]:
            return (0, "", "")
        if args[0] == "ps":
            return (0, listing, "")
        raise AssertionError("unexpected command: %r" % (args,))

    fake = fake_processes.answers({}, default=fake_run)

    code = solvable_issues.main(["--not-running"])

    out, err = capsys.readouterr()
    assert (code, out) == (0, "5\n7\n")


def test_main_not_running_keeps_the_issue_whose_live_conductor_started_from_a_different_skill_path(fake_processes, tmp_path, monkeypatch, capsys, solvable_issues):
    (tmp_path / "issues.json").write_text(json.dumps([opted_in(5), opted_in(6), opted_in(7)]))
    (tmp_path / "prs.json").write_text("[]")
    monkeypatch.setenv("VERI_GH_JSON", str(tmp_path))
    listing = "  1 /sbin/launchd\n 99 bash /tmp/skill-copy/scripts/run-conductor.sh 6\n"

    def fake_run(line, *rest, **kwargs):
        args = fake.argvs[-1]
        if list(args[:4]) == ["git", "worktree", "list", "--porcelain"]:
            return (0, "", "")
        if args[0] == "ps":
            return (0, listing, "")
        raise AssertionError("unexpected command: %r" % (args,))

    fake = fake_processes.answers({}, default=fake_run)

    code = solvable_issues.main(["--not-running"])

    out, err = capsys.readouterr()
    assert (code, out) == (0, "5\n6\n7\n")


def test_main_without_not_running_still_lists_the_issue_with_a_live_conductor_from_this_skill_path(fake_processes, tmp_path, monkeypatch, capsys, solvable_issues):
    (tmp_path / "issues.json").write_text(json.dumps([opted_in(5), opted_in(6), opted_in(7)]))
    (tmp_path / "prs.json").write_text("[]")
    monkeypatch.setenv("VERI_GH_JSON", str(tmp_path))
    scripts = pathlib.Path(solvable_issues.__file__).resolve().parent.parent
    listing = "  1 /sbin/launchd\n 99 bash %s/run-conductor.sh 6\n" % scripts

    def fake_run(line, *rest, **kwargs):
        args = fake.argvs[-1]
        if list(args[:4]) == ["git", "worktree", "list", "--porcelain"]:
            return (0, "", "")
        if args[0] == "ps":
            return (0, listing, "")
        raise AssertionError("unexpected command: %r" % (args,))

    fake = fake_processes.answers({}, default=fake_run)

    code = solvable_issues.main([])

    out, err = capsys.readouterr()
    assert (code, out) == (0, "5\n6\n7\n")


def test_main_not_running_omits_the_issue_whose_conductor_is_the_python_interpreter_running_run_conductor_py_from_this_skill_path(fake_processes, tmp_path, monkeypatch, capsys, solvable_issues):
    (tmp_path / "issues.json").write_text(json.dumps([opted_in(5), opted_in(6), opted_in(7)]))
    (tmp_path / "prs.json").write_text("[]")
    monkeypatch.setenv("VERI_GH_JSON", str(tmp_path))
    scripts = pathlib.Path(solvable_issues.__file__).resolve().parent.parent
    listing = "  1 /sbin/launchd\n 99 /usr/bin/python3 %s/veri/run_conductor.py 6\n" % scripts

    def fake_run(line, *rest, **kwargs):
        args = fake.argvs[-1]
        if list(args[:4]) == ["git", "worktree", "list", "--porcelain"]:
            return (0, "", "")
        if args[0] == "ps":
            return (0, listing, "")
        raise AssertionError("unexpected command: %r" % (args,))

    fake = fake_processes.answers({}, default=fake_run)

    code = solvable_issues.main(["--not-running"])

    out, err = capsys.readouterr()
    assert (code, out) == (0, "5\n7\n")


def test_main_not_running_returns_3_with_empty_stdout_when_every_solvable_issue_has_a_live_conductor_from_this_skill_path(fake_processes, tmp_path, monkeypatch, capsys, solvable_issues):
    (tmp_path / "issues.json").write_text(json.dumps([opted_in(5), opted_in(6)]))
    (tmp_path / "prs.json").write_text("[]")
    monkeypatch.setenv("VERI_GH_JSON", str(tmp_path))
    scripts = pathlib.Path(solvable_issues.__file__).resolve().parent.parent
    listing = "  1 /sbin/launchd\n 98 bash %s/run-conductor.sh 5\n 99 bash %s/run-conductor.sh 6\n" % (scripts, scripts)

    def fake_run(line, *rest, **kwargs):
        args = fake.argvs[-1]
        if list(args[:4]) == ["git", "worktree", "list", "--porcelain"]:
            return (0, "", "")
        if args[0] == "ps":
            return (0, listing, "")
        raise AssertionError("unexpected command: %r" % (args,))

    fake = fake_processes.answers({}, default=fake_run)

    code = solvable_issues.main(["--not-running"])

    out, err = capsys.readouterr()
    assert (code, out) == (3, "")


def test_main_not_running_then_repo_reads_that_repos_issues_and_omits_the_live_conductors_issue(fake_processes, monkeypatch, capsys, solvable_issues):
    monkeypatch.delenv("VERI_GH_JSON", raising=False)
    monkeypatch.setenv("VERI_GH_DRIVER", "auto")
    scripts = pathlib.Path(solvable_issues.__file__).resolve().parent.parent
    listing = "  1 /sbin/launchd\n 99 bash %s/run-conductor.sh 6\n" % scripts
    started = []

    def fake_run(line, *rest, **kwargs):
        args = fake.argvs[-1]
        args = list(args)
        if args[:4] == ["git", "worktree", "list", "--porcelain"]:
            return (0, "", "")
        if args[0] == "ps":
            return (0, listing, "")
        if args[:2] == ["gh", "api"] and args[2].endswith("/issues?state=open&per_page=100"):
            started.append(args[2].split("/")[1:3])
            return (0, json.dumps([opted_in(5), opted_in(6), opted_in(7)]), "")
        if args[:3] == ["gh", "pr", "list"]:
            return (0, "[]", "")
        raise AssertionError("unexpected command: %r" % (args,))

    fake = fake_processes.answers({}, default=fake_run)

    code = solvable_issues.main(["--not-running", "--repo", "o/n"])

    out, err = capsys.readouterr()
    assert (code, out, started) == (0, "5\n7\n", [["o", "n"]])


def _not_running_with(tmp_path, fake_processes, monkeypatch, capsys, solvable_issues, issues, live):
    (tmp_path / "issues.json").write_text(json.dumps(issues))
    (tmp_path / "prs.json").write_text("[]")
    monkeypatch.setenv("VERI_GH_JSON", str(tmp_path))
    scripts = pathlib.Path(solvable_issues.__file__).resolve().parent.parent
    listing = "  1 /sbin/launchd\n" + "".join(
        " %d /usr/bin/python3 %s/veri/run_conductor.py %d\n" % (100 + n, scripts, n) for n in live)

    def fake_run(line, *rest, **kwargs):
        args = fake.argvs[-1]
        if list(args[:4]) == ["git", "worktree", "list", "--porcelain"]:
            return (0, "", "")
        if args[0] == "ps":
            return (0, listing, "")
        raise AssertionError("unexpected command: %r" % (args,))

    fake = fake_processes.answers({}, default=fake_run)
    code = solvable_issues.main(["--not-running"])
    return code, capsys.readouterr().out


def test_main_not_running_omits_a_multi_digit_issue_whose_conductor_is_live_and_keeps_the_issue_its_digits_start_with(fake_processes, tmp_path, monkeypatch, capsys, solvable_issues):
    assert _not_running_with(tmp_path, fake_processes, monkeypatch, capsys, solvable_issues,
                             [opted_in(17), opted_in(1719)], [1719]) == (0, "17\n")


def test_main_not_running_keeps_the_priority_bug_rest_order_of_the_issues_it_does_not_omit(fake_processes, tmp_path, monkeypatch, capsys, solvable_issues):
    def labelled(number, *names):
        issue = opted_in(number)
        issue["labels"] += [{"name": name} for name in names]
        return issue

    issues = [opted_in(1), labelled(8, "bug"), labelled(9, "priority"), opted_in(4), labelled(3, "bug"), labelled(2, "priority")]
    assert _not_running_with(tmp_path, fake_processes, monkeypatch, capsys, solvable_issues, issues, [9, 4]) == (0, "2\n3\n8\n1\n")


def test_main_not_running_1875_keeps_issue_17_listed_for_a_live_conductor_whose_argument_is_17x(fake_processes, tmp_path, monkeypatch, capsys, solvable_issues):
    (tmp_path / "issues.json").write_text(json.dumps([opted_in(17), opted_in(18)]))
    (tmp_path / "prs.json").write_text("[]")
    monkeypatch.setenv("VERI_GH_JSON", str(tmp_path))
    scripts = pathlib.Path(solvable_issues.__file__).resolve().parent.parent
    listing = "  1 /sbin/launchd\n 99 /usr/bin/python3 %s/veri/run_conductor.py 17x\n" % scripts

    def fake_run(line, *rest, **kwargs):
        args = fake.argvs[-1]
        if list(args[:4]) == ["git", "worktree", "list", "--porcelain"]:
            return (0, "", "")
        if args[0] == "ps":
            return (0, listing, "")
        raise AssertionError("unexpected command: %r" % (args,))

    fake = fake_processes.answers({}, default=fake_run)

    code = solvable_issues.main(["--not-running"])

    out, err = capsys.readouterr()
    assert (code, out) == (0, "17\n18\n")


def test_main_not_running_1875_keeps_issue_17_listed_for_a_live_conductor_whose_path_has_extra_leading_components(fake_processes, tmp_path, monkeypatch, capsys, solvable_issues):
    (tmp_path / "issues.json").write_text(json.dumps([opted_in(17), opted_in(18)]))
    (tmp_path / "prs.json").write_text("[]")
    monkeypatch.setenv("VERI_GH_JSON", str(tmp_path))
    scripts = pathlib.Path(solvable_issues.__file__).resolve().parent.parent
    listing = "  1 /sbin/launchd\n 99 /usr/bin/python3 /x%s/veri/run_conductor.py 17\n" % scripts

    def fake_run(line, *rest, **kwargs):
        args = fake.argvs[-1]
        if list(args[:4]) == ["git", "worktree", "list", "--porcelain"]:
            return (0, "", "")
        if args[0] == "ps":
            return (0, listing, "")
        raise AssertionError("unexpected command: %r" % (args,))

    fake = fake_processes.answers({}, default=fake_run)

    code = solvable_issues.main(["--not-running"])

    out, err = capsys.readouterr()
    assert (code, out) == (0, "17\n18\n")


def test_main_not_running_1875_omits_the_issue_whose_conductor_started_through_a_symlink_to_this_skill_directory_and_keeps_one_from_a_different_real_directory(fake_processes, tmp_path, monkeypatch, capsys, solvable_issues):
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

    def fake_run(line, *rest, **kwargs):
        args = fake.argvs[-1]
        if list(args[:4]) == ["git", "worktree", "list", "--porcelain"]:
            return (0, "", "")
        if args[0] == "ps":
            return (0, listing, "")
        raise AssertionError("unexpected command: %r" % (args,))

    fake = fake_processes.answers({}, default=fake_run)

    code = solvable_issues.main(["--not-running"])

    out, err = capsys.readouterr()
    assert (code, out) == (0, "5\n7\n")


@pytest.mark.parametrize("argv", [["--repo", "o/n", "--not-running", "extra"], ["--not-running", "--repo", "o/n", "extra"]])
def test_main_1875_refuses_an_unknown_extra_argument_beside_not_running_with_2_and_the_usage_line_alone_reading_no_issue(fake_processes, argv, monkeypatch, capsys, solvable_issues):
    started = no_process(fake_processes)

    code = solvable_issues.main(argv)

    out, err = capsys.readouterr()
    assert (code, started, out, err) == (2, [], "", USAGE)


def test_main_refuses_any_argument_but_repo_and_not_running_with_2_and_the_usage_line_alone_starting_no_process_bug_1909(fake_processes, monkeypatch, capsys, solvable_issues):
    started = no_process(fake_processes)

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


def test_in_flight_2320_is_true_when_the_lock_pid_answers_kill_0_and_every_ps_read_fails(fake_processes, tmp_path, monkeypatch, solvable_issues):
    lock = tmp_path / ".tdd" / "wt" / "7" / ".tdd" / "conductor.pid"
    lock.parent.mkdir(parents=True)
    lock.write_text("4242\n")
    monkeypatch.setattr(os, "kill", lambda pid, signal: None)
    fake_processes.answers({}, default=(1, "", ""))

    assert solvable_issues.in_flight(str(tmp_path), 7) is True


def test_main_not_running_omits_the_issue_2388_whose_live_run_conductor_py_has_a_run_directory_here_with_no_events_and_no_conductor_pid(fake_processes, tmp_path, monkeypatch, capsys, solvable_issues):
    (tmp_path / "issues.json").write_text(json.dumps([opted_in(5), opted_in(6), opted_in(7)]))
    (tmp_path / "prs.json").write_text("[]")
    monkeypatch.setenv("VERI_GH_JSON", str(tmp_path))
    main_tree = tmp_path / "main"
    (main_tree / ".tdd" / "wt" / "6" / ".tdd").mkdir(parents=True)
    listing = "  1 /sbin/launchd\n 99 /usr/bin/python3 /tmp/skill-copy/scripts/veri/run_conductor.py 6\n"

    def fake_run(line, *rest, **kwargs):
        args = fake.argvs[-1]
        if list(args[:4]) == ["git", "worktree", "list", "--porcelain"]:
            return (0, "worktree %s\n" % main_tree, "")
        if args[0] == "ps":
            return (0, listing, "")
        raise AssertionError("unexpected command: %r" % (args,))

    fake = fake_processes.answers({}, default=fake_run)

    code = solvable_issues.main(["--not-running"])

    out, err = capsys.readouterr()
    assert (code, out) == (0, "5\n7\n")


def test_main_not_running_keeps_the_issue_2388_whose_live_run_conductor_py_has_no_run_directory_here(fake_processes, tmp_path, monkeypatch, capsys, solvable_issues):
    (tmp_path / "issues.json").write_text(json.dumps([opted_in(5), opted_in(6), opted_in(7)]))
    (tmp_path / "prs.json").write_text("[]")
    monkeypatch.setenv("VERI_GH_JSON", str(tmp_path))
    main_tree = tmp_path / "main"
    (main_tree / ".tdd" / "wt").mkdir(parents=True)
    listing = "  1 /sbin/launchd\n 99 /usr/bin/python3 /tmp/other-repo/scripts/veri/run_conductor.py 6\n"

    def fake_run(line, *rest, **kwargs):
        args = fake.argvs[-1]
        if list(args[:4]) == ["git", "worktree", "list", "--porcelain"]:
            return (0, "worktree %s\n" % main_tree, "")
        if args[0] == "ps":
            return (0, listing, "")
        raise AssertionError("unexpected command: %r" % (args,))

    fake = fake_processes.answers({}, default=fake_run)

    code = solvable_issues.main(["--not-running"])

    out, err = capsys.readouterr()
    assert (code, out) == (0, "5\n6\n7\n")


def test_cli_names_on_stderr_one_line_per_inherited_band_blocker_and_none_for_an_issue_in_its_own_band(fake_processes, tmp_path, monkeypatch, run_cli, solvable_issues):
    held = dict(labelled(50, "bug", "priority"), body="## Blocked by\n\n- #30\n")
    fixtures, cwd = cli_fixtures(tmp_path, fake_processes, [labelled(10, "priority", "ready-for-agent"), opted_in(30), held])

    answer = run_cli(solvable_issues, [], env={"VERI_GH_JSON": str(fixtures)}, cwd=cwd)

    assert answer == (0, "30\n10\n", "#30 inherits priority bug from #50\n")


def test_cli_does_not_lift_a_blocker_of_a_closed_priority_bug_and_names_no_inheritance_on_stderr(fake_processes, tmp_path, monkeypatch, run_cli, solvable_issues):
    closed = dict(labelled(21, "bug", "priority"), state="CLOSED", body="## Blocked by\n\n- #20\n")
    fixtures, cwd = cli_fixtures(tmp_path, fake_processes, [labelled(10, "priority", "ready-for-agent"), opted_in(20), closed])

    answer = run_cli(solvable_issues, [], env={"VERI_GH_JSON": str(fixtures)}, cwd=cwd)

    assert answer == (0, "10\n20\n", "")


def test_cli_names_on_stderr_the_priority_band_for_a_blocker_of_only_a_priority_non_bug(fake_processes, tmp_path, monkeypatch, run_cli, solvable_issues):
    held = dict(labelled(50, "priority"), body="## Blocked by\n\n- #30\n")
    fixtures, cwd = cli_fixtures(tmp_path, fake_processes, [opted_in(30), held])

    answer = run_cli(solvable_issues, [], env={"VERI_GH_JSON": str(fixtures)}, cwd=cwd)

    assert answer == (0, "30\n", "#30 inherits priority from #50\n")


def test_main_4110_lists_a_released_refactor_issue_once_its_coverage_issue_closes_its_draft_pr_still_open_and_not_while_it_is_open(
        fake_processes, tmp_path, monkeypatch, capsys, solvable_issues):
    # The labels release-covered.sh leaves on #60 (release-issue.sh's: opt-in back, claim and bailed gone), its
    # bailed run's draft PR still open on its own run branch, and the block coverage-blocker.sh wrote naming #77.
    monkeypatch.setenv("VERI_GH_JSON", str(tmp_path))
    fake_git_answering_nothing(fake_processes)
    released = dict(opted_in(60), labels=[{"name": "refactor"}, {"name": "ready-for-agent"}], body="## Blocked by\n\n- #77\n")
    covering = dict(opted_in(77), title="Cover the behaviour #60 refactors", labels=[{"name": "legacy"}, {"name": "taken:main"}])
    (tmp_path / "prs.json").write_text(json.dumps([
        {"isCrossRepository": False, "state": "OPEN", "body": "Closes #60", "headRefName": "tdd/60-extract-parser", "isDraft": True}]))
    listed = {}
    for state in ("OPEN", "CLOSED"):
        (tmp_path / "issues.json").write_text(json.dumps([released, dict(covering, state=state)]))
        code = solvable_issues.main([])
        listed[state] = (code, capsys.readouterr().out)

    assert listed == {"OPEN": (3, ""), "CLOSED": (0, "60\n")}
