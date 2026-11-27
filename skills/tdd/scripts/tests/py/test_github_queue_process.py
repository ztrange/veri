"""Real-git cases for veri/github_queue.py's `close-landed <tip-sha>` (PRD 033.6): a clone of a local bare origin whose
stack holds offline joins, each run's last commit carrying its `Veri-Joined: <pr-url> <branch>` trailer, landed on the
default branch under new shas by another clone, so the clone's own refs are behind origin's. GitHub's pull request
reads and issue comments are injected in-process; git runs for real."""
import importlib
import json
import re
import subprocess

import pytest

from repo_builder import commit_all, git, new_repo

PROCESS = "git against a local bare origin, from github-queue's module run in-process"
RUNS = (("11", ["docs: requirements for a unit, graded", "test: pin alpha", "feat: add alpha (#11)"]),
        ("12", ["test: pin bravo (#12)", "chore: regrade a unit", "feat: add bravo (#12)"]))


def pull_url(issue):
    return "https://github.com/owner/repo/pull/%d" % (int(issue) + 40)


def joined(issue):
    return "Veri-Joined: %s tdd/%s-a-run" % (pull_url(issue), issue)


def onto(sha):
    return "Veri-Joined-Onto: %s" % sha


def landed_world(tmp_path, runs=RUNS, trailers=None, held=(), before=(), after=None, unlanded=0):
    """The clone `work` of a bare origin whose default branch is trunk, its stack holding first each subject of
    <before> (a run joined online before the outage, no trailer), then <runs> ((issue, subjects) pairs), each run's
    last commit carrying the run's Veri-Joined trailer and the Veri-Joined-Onto trailer naming the stack's tip it was
    joined onto, or the trailer block <trailers> maps its (issue, index) to, each followed by the subjects <after> maps
    its issue to (a repair committed on the stack between two joins). A second clone first commits each subject of
    <held> on trunk (a held pull request merged before the landing), then lands the stack but its last <unlanded>
    commits on origin's trunk under new shas; `work` never fetches it. Returns (work, the stack's tip, [(issue, [(short sha, subject)])] as landed,
    origin's trunk tip)."""
    origin, work, lander = tmp_path / "origin.git", tmp_path / "work", tmp_path / "lander"
    new_repo(work, "trunk")
    commit_all(work, "docs: the base", **{".gitignore": ".tdd/\n"})
    subprocess.run(["git", "clone", "-q", "--bare", str(work), str(origin)], cwd=tmp_path, check=True)
    git(work, "remote", "add", "origin", str(origin))
    git(work, "fetch", "-q", "origin")
    git(work, "remote", "set-head", "origin", "trunk")
    git(work, "checkout", "-q", "-b", "stack")
    for index, subject in enumerate(before):
        commit_all(work, subject, **{"before-%d.txt" % index: "b\n"})
    for number, (issue, subjects) in enumerate(runs):
        base = git(work, "rev-parse", "HEAD")
        last = len(subjects) - 1
        for index, subject in enumerate(subjects):
            block = (trailers or {}).get((issue, index), joined(issue) + "\n" + onto(base) if index == last else "")
            commit_all(work, subject + ("\n\n" + block if block else ""), **{"f%d-%d.txt" % (number, index): "x\n"})
        for index, subject in enumerate((after or {}).get(issue, ())):
            commit_all(work, subject, **{"after-%d-%d.txt" % (number, index): "a\n"})
    tip = git(work, "rev-parse", "HEAD")
    subprocess.run(["git", "clone", "-q", str(origin), str(lander)], cwd=tmp_path, check=True)
    git(lander, "fetch", "-q", str(work), "stack:stack")
    for index, subject in enumerate(held):
        commit_all(lander, subject, **{"held-%d.txt" % index: "h\n"})
    git(lander, "-c", "user.name=lander", "cherry-pick", "trunk..stack~%d" % unlanded)
    git(lander, "push", "-q", "origin", "trunk")
    shown = [tuple(line.split("\t")) for line in
             git(lander, "log", "--reverse", "--format=%h%x09%s", "origin/trunk@{1}..trunk").splitlines()]
    landed, at = [], len(held) + len(before)
    for issue, subjects in runs:
        landed.append((issue, shown[at:at + len(subjects)]))
        at += len(subjects) + len((after or {}).get(issue, ()))
    return work, tip, landed, git(lander, "rev-parse", "trunk")


class Hub:
    """A fake GitHub: each pull request's read (merged, not merged, or no answer), each issue's comments, the posts."""

    def __init__(self, monkeypatch, merged=None, dead_pulls=(), dead_posts=False, garbled_pulls=()):
        self.github = importlib.import_module("github")
        self.queue = importlib.import_module("veri.github_queue")
        self.merged, self.dead_pulls, self.dead_posts = merged or {}, set(dead_pulls), dead_posts
        self.garbled_pulls = set(garbled_pulls)
        self.comments, self.posted = {}, []
        monkeypatch.setattr(self.github, "gh_api", self.gh_api)
        monkeypatch.setattr(self.github, "issue_comments", lambda number: list(self.comments.get(str(number), [])))
        monkeypatch.setattr(self.github, "gh_issue_comment", self.gh_issue_comment)
        monkeypatch.setattr(self.github, "trusted_comment", lambda comment: True)

    def gh_api(self, path, stderr=None):
        found = re.fullmatch(r"repos/owner/repo/pulls/(\d+)", path)
        assert found, path
        issue = str(int(found[1]) - 40)
        if issue in self.dead_pulls:
            return subprocess.CompletedProcess(["gh", "api", path], 1, '{"message": "Server Error"}', "HTTP 502")
        if issue in self.garbled_pulls:
            return subprocess.CompletedProcess(["gh", "api", path], 0, "<html>busy</html>", "")
        return subprocess.CompletedProcess(["gh", "api", path], 0, json.dumps(
            {"state": "closed", "merged": self.merged.get(issue, True)}), "")

    def gh_issue_comment(self, number, body):
        if self.dead_posts:
            raise self.github.NoAnswer("")
        self.posted.append((str(number), body))
        self.comments.setdefault(str(number), []).append({"body": body})
        return "https://x/%d" % len(self.posted)

    def bodies(self, issue):
        return [body for number, body in self.posted if number == issue]


def lists_exactly(body, commits, others):
    """<body> lists each (short sha, subject) of <commits> on one line, sha next to subject, and no sha of <others>."""
    lines = body.splitlines()
    for short, subject in commits:
        assert "- %s %s" % (short, subject) in lines, (short, subject, body)
    assert [short for short, _ in others if short in body] == [], body


@pytest.mark.process(PROCESS)
def test_4823_close_landed_lists_every_commit_of_one_joined_run_whatever_its_subjects(tmp_path, monkeypatch, run_cli):
    work, tip, landed, _ = landed_world(tmp_path, runs=RUNS[:1])
    hub = Hub(monkeypatch)

    code, out, err = run_cli(hub.queue, ["close-landed", tip], cwd=work)

    assert code == 0, err
    assert [number for number, _ in hub.posted] == ["11"], err
    body = hub.bodies("11")[0]
    assert body.startswith("### ✅ Landed\n"), body
    assert re.search(r"\n<!-- veri-queued [0-9a-f]+ -->$", body), body
    lists_exactly(body, landed[0][1], [])
    assert "docs: the base" not in body, body
    assert not (work / ".tdd" / "github-queue").exists()


@pytest.mark.process(PROCESS)
def test_4823_close_landed_gives_each_of_several_joined_runs_exactly_its_own_commits(tmp_path, monkeypatch, run_cli):
    runs = RUNS + (("13", ["fix: mend charlie (#13)", "docs: requirements for another unit, graded"]),)
    work, tip, landed, _ = landed_world(tmp_path, runs=runs)
    hub = Hub(monkeypatch)

    code, out, err = run_cli(hub.queue, ["close-landed", tip], cwd=work)

    assert code == 0, err
    assert [number for number, _ in hub.posted] == ["11", "12", "13"], err
    for issue, commits in landed:
        others = [commit for other, theirs in landed if other != issue for commit in theirs]
        lists_exactly(hub.bodies(issue)[0], commits, others)


@pytest.mark.process(PROCESS)
def test_4823_close_landed_lists_no_commit_trunk_gained_before_the_landing_in_any_runs_comment(
        tmp_path, monkeypatch, run_cli):
    held = ["fix: a held pull request merged first", "docs: another held one"]
    work, tip, landed, trunk = landed_world(tmp_path, held=held)
    hub = Hub(monkeypatch)

    code, out, err = run_cli(hub.queue, ["close-landed", tip], cwd=work)

    assert code == 0, err
    assert [number for number, _ in hub.posted] == ["11", "12"], err
    for issue, commits in landed:
        lists_exactly(hub.bodies(issue)[0], commits, [])
        assert [subject for subject in held if subject in hub.bodies(issue)[0]] == [], hub.bodies(issue)[0]


@pytest.mark.process(PROCESS)
def test_4823_close_landed_credits_a_run_only_the_commits_its_own_join_added(tmp_path, monkeypatch, run_cli):
    before = ["feat: a run joined online before the outage (#9)", "test: its pin (#9)"]
    repair = ["fix: a repair committed on the stack between two joins"]
    work, tip, landed, _ = landed_world(tmp_path, before=before, after={"11": repair})
    hub = Hub(monkeypatch)

    code, out, err = run_cli(hub.queue, ["close-landed", tip], cwd=work)

    assert code == 0, err
    assert [number for number, _ in hub.posted] == ["11", "12"], err
    for issue, commits in landed:
        body = hub.bodies(issue)[0]
        lists_exactly(body, commits, [])
        assert [subject for subject in before + repair if subject in body] == [], body


@pytest.mark.process(PROCESS)
def test_4823_close_landed_comments_on_no_run_whose_join_has_not_landed_yet(tmp_path, monkeypatch, run_cli):
    work, tip, landed, _ = landed_world(tmp_path, unlanded=len(RUNS[1][1]))
    hub = Hub(monkeypatch)

    code, out, err = run_cli(hub.queue, ["close-landed", tip], cwd=work)

    assert code == 0, err
    assert [number for number, _ in hub.posted] == ["11"], err
    lists_exactly(hub.bodies("11")[0], landed[0][1], [])


@pytest.mark.process(PROCESS)
def test_4823_close_landed_reads_the_landed_range_from_origins_default_branch_when_the_clone_is_behind(
        tmp_path, monkeypatch, run_cli):
    work, tip, landed, trunk = landed_world(tmp_path)
    assert git(work, "rev-parse", "origin/trunk") != trunk
    assert git(work, "rev-parse", "trunk") != trunk
    hub = Hub(monkeypatch)

    code, out, err = run_cli(hub.queue, ["close-landed", tip], cwd=work)

    assert code == 0, err
    for issue, commits in landed:
        lists_exactly(hub.bodies(issue)[0], commits, [])
    assert git(work, "rev-parse", "trunk") != trunk


@pytest.mark.process(PROCESS)
def test_4823_close_landed_reads_no_run_from_a_trailer_other_than_veri_joined(tmp_path, monkeypatch, run_cli):
    other = "Co-Authored-By: Someone <someone@example.test>\nVeri-Related: %s tdd/13-a-run" % pull_url("13")
    work, tip, landed, _ = landed_world(tmp_path, trailers={("11", 0): other})
    hub = Hub(monkeypatch)

    code, out, err = run_cli(hub.queue, ["close-landed", tip], cwd=work)

    assert code == 0, err
    assert [number for number, _ in hub.posted] == ["11", "12"], err
    for issue, commits in landed:
        lists_exactly(hub.bodies(issue)[0], commits, [])


@pytest.mark.process(PROCESS)
def test_4823_close_landed_posts_one_landed_comment_on_an_issue_two_veri_joined_trailers_name(
        tmp_path, monkeypatch, run_cli):
    runs = RUNS + (("11", ["fix: alpha again"]),)
    work, tip, landed, _ = landed_world(tmp_path, runs=runs)
    hub = Hub(monkeypatch)

    code, out, err = run_cli(hub.queue, ["close-landed", tip], cwd=work)

    assert code == 0, err
    assert [number for number, _ in hub.posted] == ["11", "12"], err
    lists_exactly(hub.bodies("11")[0], landed[0][1] + landed[2][1], landed[1][1])


@pytest.mark.process(PROCESS)
def test_4823_close_landed_names_a_run_whose_pull_request_is_not_merged_and_comments_on_the_others(
        tmp_path, monkeypatch, run_cli):
    work, tip, landed, _ = landed_world(tmp_path)
    hub = Hub(monkeypatch, merged={"11": False})

    code, out, err = run_cli(hub.queue, ["close-landed", tip], cwd=work)

    assert code == 0, err
    assert [number for number, _ in hub.posted] == ["12"], err
    assert "#11" in err and "not" in err and "merged" in err, err
    lists_exactly(hub.bodies("12")[0], landed[1][1], landed[0][1])


@pytest.mark.process(PROCESS)
def test_4823_a_second_close_landed_over_the_same_tip_posts_nothing(tmp_path, monkeypatch, run_cli):
    work, tip, _, _ = landed_world(tmp_path)
    hub = Hub(monkeypatch)
    assert run_cli(hub.queue, ["close-landed", tip], cwd=work)[0] == 0
    first = list(hub.posted)

    code, out, err = run_cli(hub.queue, ["close-landed", tip], cwd=work)

    assert code == 0, err
    assert hub.posted == first, err
    assert not (work / ".tdd" / "github-queue").exists()

@pytest.mark.process(PROCESS)
def test_4823_a_second_close_landed_after_short_shas_lengthen_posts_nothing(tmp_path, monkeypatch, run_cli):
    work, tip, _, _ = landed_world(tmp_path)
    hub = Hub(monkeypatch)
    assert run_cli(hub.queue, ["close-landed", tip], cwd=work)[0] == 0
    first = list(hub.posted)
    git(work, "config", "core.abbrev", "12")

    code, out, err = run_cli(hub.queue, ["close-landed", tip], cwd=work)

    assert code == 0, err
    assert hub.posted == first, err


@pytest.mark.process(PROCESS)
def test_4823_close_landed_when_no_runs_pull_request_is_merged_and_nothing_is_queued_exits_3(
        tmp_path, monkeypatch, run_cli):
    work, tip, _, _ = landed_world(tmp_path)
    hub = Hub(monkeypatch, merged={"11": False, "12": False})

    code, out, err = run_cli(hub.queue, ["close-landed", tip], cwd=work)

    assert code == 3, err
    assert hub.posted == [], err
    assert "#11" in err and "#12" in err, err



@pytest.mark.process(PROCESS)
def test_4823_close_landed_whose_pull_request_read_gets_no_answer_names_the_run_and_exits_2(
        tmp_path, monkeypatch, run_cli):
    work, tip, landed, _ = landed_world(tmp_path)
    hub = Hub(monkeypatch, dead_pulls={"12"})

    code, out, err = run_cli(hub.queue, ["close-landed", tip], cwd=work)

    assert code == 2, err
    assert [number for number, _ in hub.posted] == ["11"], err
    assert "#12" in err and pull_url("12") in err, err


@pytest.mark.process(PROCESS)
def test_4823_close_landed_whose_replay_gets_no_answer_keeps_the_landed_comments_queued_and_exits_2(
        tmp_path, monkeypatch, run_cli):
    work, tip, _, _ = landed_world(tmp_path)
    hub = Hub(monkeypatch, dead_posts=True)

    code, out, err = run_cli(hub.queue, ["close-landed", tip], cwd=work)

    assert code == 2, err
    assert "stay queued" in err, err
    queued = [json.loads(line) for line in (work / ".tdd" / "github-queue").read_text().splitlines()]
    assert [(e["issue"], e["kind"]) for e in queued] == [("11", "landed"), ("12", "landed")], queued
    assert all(e["body"].startswith("### ✅ Landed\n") for e in queued), queued


@pytest.mark.process(PROCESS)
def test_4823_close_landed_whose_fetch_fails_queues_nothing_and_exits_2(tmp_path, monkeypatch, run_cli):
    work, tip, _, _ = landed_world(tmp_path)
    git(work, "remote", "set-url", "origin", str(tmp_path / "gone.git"))
    hub = Hub(monkeypatch)

    code, out, err = run_cli(hub.queue, ["close-landed", tip], cwd=work)

    assert code == 2, err
    assert "fetch" in err, err
    assert hub.posted == [] and not (work / ".tdd" / "github-queue").exists(), err


@pytest.mark.process(PROCESS)
def test_4823_close_landed_over_a_tip_git_cannot_read_queues_nothing_and_exits_2(tmp_path, monkeypatch, run_cli):
    work, _, _, _ = landed_world(tmp_path)
    hub = Hub(monkeypatch)

    code, out, err = run_cli(hub.queue, ["close-landed", "0" * 40], cwd=work)

    assert code == 2, err
    assert "cannot read %s..origin/trunk" % ("0" * 40) in err and "Traceback" not in err, err
    assert hub.posted == [] and not (work / ".tdd" / "github-queue").exists(), err


@pytest.mark.process(PROCESS)
def test_4823_close_landed_over_a_garbled_veri_joined_trailer_queues_nothing_and_exits_2(
        tmp_path, monkeypatch, run_cli):
    work, tip, _, _ = landed_world(tmp_path, trailers={("12", 2): "Veri-Joined: not a pull request"})
    hub = Hub(monkeypatch)

    code, out, err = run_cli(hub.queue, ["close-landed", tip], cwd=work)

    assert code == 2, err
    assert "not a pull request" in err, err
    assert hub.posted == [] and not (work / ".tdd" / "github-queue").exists(), err


@pytest.mark.process(PROCESS)
@pytest.mark.parametrize("block", ["", "\nVeri-Joined-Onto: HEAD~1", "\nVeri-Joined-Onto: " + "a" * 40])
def test_4823_close_landed_over_a_join_without_a_readable_veri_joined_onto_queues_nothing_and_exits_2(
        tmp_path, monkeypatch, run_cli, block):
    work, tip, _, _ = landed_world(tmp_path, trailers={("12", 2): joined("12") + block})
    hub = Hub(monkeypatch)

    code, out, err = run_cli(hub.queue, ["close-landed", tip], cwd=work)

    assert code == 2, err
    assert "feat: add bravo (#12)" in err and "Veri-Joined-Onto" in err and "Traceback" not in err, err
    assert hub.posted == [] and not (work / ".tdd" / "github-queue").exists(), err


@pytest.mark.process(PROCESS)
def test_4823_close_landed_over_a_range_with_no_joined_run_posts_nothing_and_exits_3(tmp_path, monkeypatch, run_cli):
    work, tip, _, _ = landed_world(tmp_path, trailers={("11", 2): "", ("12", 2): ""})
    hub = Hub(monkeypatch)

    code, out, err = run_cli(hub.queue, ["close-landed", tip], cwd=work)

    assert code == 3, err
    assert "no Veri-Joined commit" in err, err
    assert hub.posted == [], err


@pytest.mark.process(PROCESS)
def test_4823_close_landed_given_a_second_argument_exits_2_with_the_usage(tmp_path, monkeypatch, run_cli):
    work, tip, _, _ = landed_world(tmp_path)
    hub = Hub(monkeypatch)

    code, out, err = run_cli(hub.queue, ["close-landed", tip, tip], cwd=work)

    assert code == 2, err
    assert "usage: github-queue.sh" in err and "close-landed <tip-sha>" in err, err
    assert hub.posted == [], err


@pytest.mark.process(PROCESS)
def test_4823_close_landed_whose_pull_request_read_is_not_json_names_the_run_and_exits_2(
        tmp_path, monkeypatch, run_cli):
    work, tip, _, _ = landed_world(tmp_path)
    hub = Hub(monkeypatch, garbled_pulls={"11"})

    code, out, err = run_cli(hub.queue, ["close-landed", tip], cwd=work)

    assert code == 2, err
    assert [number for number, _ in hub.posted] == ["12"], err
    assert "#11" in err and pull_url("11") in err, err


@pytest.mark.process(PROCESS)
def test_4823_close_landed_over_a_commit_with_two_veri_joined_trailers_queues_nothing_and_exits_2(
        tmp_path, monkeypatch, run_cli):
    work, tip, _, _ = landed_world(tmp_path, trailers={("12", 2): joined("12") + "\n" + joined("13")})
    hub = Hub(monkeypatch)

    code, out, err = run_cli(hub.queue, ["close-landed", tip], cwd=work)

    assert code == 2, err
    assert "feat: add bravo (#12)" in err, err
    assert hub.posted == [] and not (work / ".tdd" / "github-queue").exists(), err


@pytest.mark.process(PROCESS)
def test_4823_close_landed_when_origins_default_branch_cannot_be_told_queues_nothing_and_exits_2(
        tmp_path, monkeypatch, run_cli):
    work, tip, _, _ = landed_world(tmp_path)
    git(tmp_path / "origin.git", "symbolic-ref", "HEAD", "refs/heads/gone")
    git(work, "remote", "set-head", "origin", "-d")
    hub = Hub(monkeypatch)

    code, out, err = run_cli(hub.queue, ["close-landed", tip], cwd=work)

    assert code == 2, err
    assert "default branch" in err, err
    assert hub.posted == [] and not (work / ".tdd" / "github-queue").exists(), err


@pytest.mark.process(PROCESS)
def test_4823_close_landed_given_a_tip_that_is_not_a_hex_commit_name_exits_2_with_the_usage(
        tmp_path, monkeypatch, run_cli):
    work, _, _, _ = landed_world(tmp_path)
    hub = Hub(monkeypatch)

    code, out, err = run_cli(hub.queue, ["close-landed", "--all"], cwd=work)

    assert code == 2, err
    assert "usage: github-queue.sh" in err, err
    assert hub.posted == [], err
