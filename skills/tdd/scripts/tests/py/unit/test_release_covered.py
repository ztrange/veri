"""In-process cases for veri/release_covered.py, the module release-covered.sh is a shim over (#4110)."""
import importlib
import json

import pytest

COVERING = "repos/{owner}/{repo}/issues/77"
REFACTOR = "repos/{owner}/{repo}/issues/60"


@pytest.fixture
def world(tmp_path, monkeypatch, fake_processes):
    """release_covered with its two issue reads answered at the gh process boundary from <records> (a path → answer
    table: a dict is served as JSON, a tuple as (code, stdout, stderr)) and release-issue.sh's label writes faked;
    returns (module, records, writes)."""
    (tmp_path / ".tdd").mkdir()
    monkeypatch.chdir(tmp_path)
    module = importlib.import_module("veri.release_covered")
    github = importlib.import_module("veri.github")
    records, writes = {}, []

    def read(line, **kwargs):
        path = line.split()[-1]
        answer = records.get(path, (1, "", "gh: Not Found (HTTP 404)\n"))
        return answer if isinstance(answer, tuple) else (0, json.dumps(answer), "")

    fake_processes.answers({"gh api repos/": read})
    monkeypatch.setattr(github, "gh_issue_view", lambda number, field: "" if field == "comments" else "\n".join(
        label["name"] for label in records[REFACTOR]["labels"]))
    monkeypatch.setattr(github, "issue_comments", lambda number: [])
    monkeypatch.setattr(github, "gh_label_ensure", lambda label: writes.append(("ensure", label)))
    monkeypatch.setattr(github, "gh_issue_add_label", lambda number, label: writes.append(("label", number, label)))
    monkeypatch.setattr(github, "gh_issue_remove_label", lambda number, label: writes.append(("unlabel", number, label)))
    monkeypatch.setattr(importlib.import_module("veri.run_records"), "delete", lambda issue, cwd: None)
    return module, records, writes


def issue(title, state="open", labels=()):
    return {"title": title, "state": state, "labels": [{"name": name} for name in labels]}


def test_4110_a_closed_coverage_issue_releases_its_bailed_refactor_issue_as_release_issue_does_and_prints_it(world, run_cli):
    module, records, writes = world
    records[COVERING] = issue("Cover the behaviour #60 refactors", "closed", ("legacy",))
    records[REFACTOR] = issue("Extract the parser", "open", ("refactor", "taken:main", "bailed"))

    code, out, err = run_cli(module, ["77"])

    assert (code, out, writes) == (0, "released #60\n", [
        ("ensure", "ready-for-agent"), ("label", "60", "ready-for-agent"), ("unlabel", "60", "taken:main"),
        ("unlabel", "60", "parked"), ("unlabel", "60", "bailed")])


@pytest.mark.parametrize("covering, refactor", [
    (issue("Cover the behaviour of #60"), issue("x", "open", ("bailed", "taken:main"))),
    (issue("Cover the behaviour #60 refactors twice"), issue("x", "open", ("bailed", "taken:main"))),
    (issue("Cover the behaviour #60 refactors"), issue("x", "closed", ("bailed", "taken:main"))),
    (issue("Cover the behaviour #60 refactors"), issue("x", "open", ("parked", "taken:main"))),
], ids=["another shape", "a longer title", "refactor issue closed", "refactor issue not bailed"])
def test_4110_exits_3_writing_no_label_when_the_title_has_another_shape_or_the_refactor_issue_is_closed_or_not_bailed(
        world, run_cli, covering, refactor):
    module, records, writes = world
    records[COVERING], records[REFACTOR] = covering, refactor

    code, out, err = run_cli(module, ["77"])

    assert (code, out, writes) == (3, "", [])


@pytest.mark.parametrize("which", ["covering", "refactor"])
@pytest.mark.parametrize("answer", [(1, "", "HTTP 502 Bad Gateway\n"), (0, "not json", ""), (0, "[]", "")],
                         ids=["no answer", "not json", "not an object"])
def test_4110_exits_2_writing_no_label_when_gh_gives_no_answer_reading_either_issue(world, run_cli, which, answer):
    module, records, writes = world
    records[COVERING] = issue("Cover the behaviour #60 refactors", "closed")
    records[REFACTOR] = issue("x", "open", ("bailed", "taken:main"))
    records[COVERING if which == "covering" else REFACTOR] = answer

    code, out, err = run_cli(module, ["77"])

    assert (code, out, writes, "no answer" in err) == (2, "", [], True)


def test_4110_exits_2_when_release_issue_exits_2(world, run_cli, monkeypatch):
    module, records, writes = world
    records[COVERING] = issue("Cover the behaviour #60 refactors", "closed")
    records[REFACTOR] = issue("x", "open", ("bailed", "taken:other"))

    code, out, err = run_cli(module, ["77"])

    assert (code, out, writes, "another lane's claim" in err) == (2, "", [], True)


@pytest.mark.parametrize("argv", [[], ["77", "78"], ["x77"], ["0"], [""]])
def test_4110_bad_arguments_exit_2_with_the_usage_line_and_no_gh_call(world, run_cli, argv):
    module, records, writes = world

    code, out, err = run_cli(module, argv)

    assert (code, out, err, writes) == (2, "", "usage: release-covered.sh <issue-number>\n", [])
