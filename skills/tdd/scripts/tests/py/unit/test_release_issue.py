"""In-process cases for release-issue.sh: a parked, bailed or preflight-refused issue goes back to the queue in one call."""
import importlib
import json
import subprocess

import pytest


@pytest.fixture
def release(monkeypatch, tmp_path):
    """release_issue with every gh call faked, run in <tmp_path> holding a `.tdd/` as a clone's; returns (module, calls,
    labels) — set labels[:] per case."""
    (tmp_path / ".tdd").mkdir()
    release_issue = importlib.import_module("veri.release_issue")
    github = release_issue.github
    calls, labels = [], []
    monkeypatch.setattr(github, "gh_issue_view", lambda number, field: calls.append(("view", number, field)) or ("" if field == "comments" else "\n".join(labels)))
    monkeypatch.setattr(github, "issue_comments", lambda number: calls.append(("view", number, "comments")) or [])
    monkeypatch.setattr(github, "gh_label_ensure", lambda label: calls.append(("ensure", label)))
    monkeypatch.setattr(github, "gh_issue_add_label", lambda number, label: calls.append(("label", number, label)))
    monkeypatch.setattr(github, "gh_issue_remove_label", lambda number, label: calls.append(("unlabel", number, label)))
    monkeypatch.setattr(importlib.import_module("veri.run_records"), "delete", lambda issue, cwd: None, raising=False)
    return release_issue, calls, labels


def writes(calls):
    return [call for call in calls if call[0] != "view"]


def test_a_parked_issue_gets_the_opt_in_back_and_loses_its_claim_and_the_parked_label_last(release, run_cli):
    release_issue, calls, labels = release
    labels[:] = ["bug", "priority", "taken:main", "parked"]

    code, out, err = run_cli(release_issue, ["3284"])

    assert (code, err) == (0, "")
    assert writes(calls) == [
        ("ensure", "ready-for-agent"),
        ("label", "3284", "ready-for-agent"),
        ("unlabel", "3284", "taken:main"),
        ("unlabel", "3284", "parked"),
        ("unlabel", "3284", "bailed"),
    ]


def test_a_released_run_has_origins_refs_veri_runs_n_deleted_and_a_delete_that_fails_is_one_stderr_line_not_an_exit_code(
        run_cli, monkeypatch, fake_processes, tmp_path):
    (tmp_path / ".tdd").mkdir()
    monkeypatch.chdir(tmp_path)
    module = importlib.import_module("veri.release_issue")
    github = module.github
    monkeypatch.setattr(github, "gh_issue_view", lambda number, field: "" if field == "comments" else "taken:main\nparked")
    for name in ("gh_label_ensure", "gh_issue_add_label", "gh_issue_remove_label"):
        monkeypatch.setattr(github, name, lambda *args: None)
    fake = fake_processes.answers({
        "git remote get-url origin": (0, "https://example.invalid/r.git\n", ""),
        "git push origin --delete refs/veri/runs/3284": (1, "", "fatal: unable to access origin\n"),
    })

    code, out, err = run_cli(module, ["3284"])

    assert (code, "git push origin --delete refs/veri/runs/3284" in fake.calls, len(err.splitlines()),
            "refs/veri/runs/3284" in err) == (0, True, 1, True)


def test_a_bailed_issue_is_released_the_same_way(release, run_cli):
    release_issue, calls, labels = release
    labels[:] = ["bug", "taken:main", "bailed"]

    code, out, err = run_cli(release_issue, ["3369"])

    assert code == 0
    assert ("label", "3369", "ready-for-agent") in calls
    assert ("unlabel", "3369", "taken:main") in calls
    assert writes(calls)[-2:] == [("unlabel", "3369", "parked"), ("unlabel", "3369", "bailed")]


def test_an_issue_neither_parked_nor_bailed_is_nothing_to_do_and_nothing_is_written(release, run_cli):
    release_issue, calls, labels = release
    labels[:] = ["bug", "taken:main"]

    code, out, err = run_cli(release_issue, ["3323"])

    assert code == 3
    assert writes(calls) == []
    assert "neither parked, bailed nor preflight-refused" in err


def test_a_preflight_refused_issue_is_released_to_the_queue_3627(release, run_cli, monkeypatch):
    release_issue, calls, labels = release
    labels[:] = ["bug", "taken:main"]
    serve_comments(monkeypatch, release_issue, labels, [authored("OWNER", REFUSAL, login="veri-operator")])

    code, out, err = run_cli(release_issue, ["3621"])

    assert (code, err) == (0, "")
    assert ("label", "3621", "ready-for-agent") in calls
    assert ("unlabel", "3621", "taken:main") in calls


def test_another_lanes_claim_is_refused_and_nothing_is_written(release, run_cli):
    release_issue, calls, labels = release
    labels[:] = ["bug", "taken:mu", "parked"]

    code, out, err = run_cli(release_issue, ["7"])

    assert code == 2
    assert writes(calls) == []
    assert "taken:mu" in err


def test_the_lane_comes_from_veri_label(release, run_cli, monkeypatch):
    release_issue, calls, labels = release
    monkeypatch.setenv("VERI_LABEL", "ready-for-agent:mu")
    labels[:] = ["taken:mu", "parked"]

    code, out, err = run_cli(release_issue, ["7"])

    assert code == 0
    assert ("label", "7", "ready-for-agent:mu") in calls
    assert ("unlabel", "7", "taken:mu") in calls


def test_no_answer_before_the_marker_comes_off_exits_2_and_leaves_the_marker(release, run_cli, monkeypatch):
    release_issue, calls, labels = release
    labels[:] = ["taken:main", "parked"]

    def refuse(number, label):
        if label.startswith("taken:"):
            raise release_issue.github.NoAnswer("")
        calls.append(("unlabel", number, label))

    monkeypatch.setattr(release_issue.github, "gh_issue_remove_label", refuse)

    code, out, err = run_cli(release_issue, ["7"])

    assert code == 2
    assert "no answer from gh" in err
    assert ("unlabel", "7", "parked") not in calls


def test_no_answer_reading_the_labels_exits_2_and_writes_nothing(release, run_cli, monkeypatch):
    release_issue, calls, labels = release

    def refuse(number, field):
        raise release_issue.github.NoAnswer("")

    monkeypatch.setattr(release_issue.github, "gh_issue_view", refuse)

    code, out, err = run_cli(release_issue, ["7"])

    assert code == 2
    assert writes(calls) == []


@pytest.mark.parametrize("argv", [[], ["7", "8"], ["x7"], ["0"], ["-1"]])
def test_bad_arguments_exit_2_and_call_nothing(release, run_cli, argv):
    release_issue, calls, labels = release

    code, out, err = run_cli(release_issue, argv)

    assert code == 2
    assert calls == []
    assert "usage: release-issue.sh <issue-number>" in err


def test_a_refusal_comment_alone_does_not_make_an_issue_preflight_refused_3627(release, run_cli, monkeypatch):
    release_issue, calls, labels = release
    refusal = [authored("OWNER", REFUSAL, login="veri-operator")]
    state = {"comments": refusal}

    def comments_of(number):
        if state["comments"] is None:
            raise release_issue.github.NoAnswer("")
        return state["comments"]

    monkeypatch.setattr(release_issue.github, "issue_comments", comments_of)

    outcomes = {}
    for name, label_set, comments in [
        ("refused", ["bug", "taken:main"], refusal),
        ("already opted in", ["bug", "taken:main", "ready-for-agent"], refusal),
        ("unclaimed", ["bug"], refusal),
        ("comments unreadable", ["bug", "taken:main"], None),
    ]:
        labels[:] = label_set
        state["comments"] = comments
        calls.clear()
        code, out, err = run_cli(release_issue, ["3621"])
        outcomes[name] = (code, writes(calls) != [])

    assert outcomes == {
        "refused": (0, True),
        "already opted in": (3, False),
        "unclaimed": (3, False),
        "comments unreadable": (2, False),
    }


def test_a_preflight_release_cut_short_by_a_silent_gh_is_finished_by_running_it_again_3627(release, run_cli, monkeypatch):
    release_issue, calls, labels = release
    labels[:] = ["bug", "taken:main"]
    silent = {"claim": True}
    serve_comments(monkeypatch, release_issue, labels, [authored("OWNER", REFUSAL, login="veri-operator")])
    monkeypatch.setattr(release_issue.github, "gh_issue_add_label", lambda number, label: labels.append(label))

    def remove(number, label):
        if label == "taken:main" and silent["claim"]:
            raise release_issue.github.NoAnswer("")
        if label in labels:
            labels.remove(label)

    monkeypatch.setattr(release_issue.github, "gh_issue_remove_label", remove)

    first, _, _ = run_cli(release_issue, ["3621"])
    silent["claim"] = False
    code, out, err = run_cli(release_issue, ["3621"])

    assert first == 2
    assert (code, err) == (0, "")
    assert sorted(labels) == ["bug", "ready-for-agent"]


def test_a_preflight_refused_issue_claimed_by_another_lane_exits_2_and_nothing_is_written_3627(release, run_cli, monkeypatch):
    release_issue, calls, labels = release
    labels[:] = ["bug", "taken:mu"]
    serve_comments(monkeypatch, release_issue, labels, [authored("OWNER", REFUSAL, login="veri-operator")])

    code, out, err = run_cli(release_issue, ["3621"])

    assert code == 2
    assert writes(calls) == []
    assert "taken:mu" in err


def test_a_claimed_unopted_issue_with_only_other_comments_still_exits_3_and_nothing_is_written_3627(release, run_cli, monkeypatch):
    release_issue, calls, labels = release
    labels[:] = ["bug", "taken:main"]
    serve_comments(monkeypatch, release_issue, labels, [authored("OWNER", "### Plan\nstep 1 done", login="veri-operator")])

    code, out, err = run_cli(release_issue, ["3621"])

    assert code == 3
    assert writes(calls) == []


def test_a_preflight_refused_claim_is_released_through_the_real_rest_adapter_3687(run_cli, monkeypatch, tmp_path):
    (tmp_path / ".tdd").mkdir()  # a clone's, where the release marker goes
    release_issue = importlib.import_module("veri.release_issue")
    github = release_issue.github
    issue = "repos/{owner}/{repo}/issues/3241"
    comments = issue + "/comments"
    calls = []

    def fake_gh(*args, stderr=None):
        calls.append(args)
        out = "[]"
        if args == ("api", issue):
            out = json.dumps({"body": "## Problem\n\nthe body", "labels": [{"name": "taken:mu"}]})
        elif args[:2] == ("api", comments + "?per_page=100&page=1"):
            out = json.dumps([{"author_association": "OWNER", "user": {"login": "veri-operator"},
                               "body": "### ⛔ Preflight refused — requirements clash"}])
        return subprocess.CompletedProcess(args, 0, out, "")

    monkeypatch.setattr(github, "run_gh", fake_gh)
    monkeypatch.setattr(importlib.import_module("veri.run_records"), "delete", lambda issue, cwd: None)
    monkeypatch.setenv("VERI_LABEL", "ready-for-agent:mu")

    code, out, err = run_cli(release_issue, ["3241"])

    assert code == 0, err
    assert ("api", issue + "/labels", "-f", "labels[]=ready-for-agent:mu") in calls
    assert ("api", "-X", "DELETE", issue + "/labels/taken:mu") in calls


REFUSAL = "### ⛔ Preflight refused — requirements clash"


def authored(association, body, login="someone"):
    return {"author_association": association, "user": {"login": login}, "body": body}


def serve_comments(monkeypatch, release_issue, labels, comments):
    """gh answering <labels> and the issue's comments <comments> (REST records), on both comment routes."""
    github = release_issue.github
    monkeypatch.setattr(github, "authenticated_login", lambda: "veri-operator")
    monkeypatch.setattr(github, "issue_comments", lambda number: comments)
    monkeypatch.setattr(github, "gh_issue_view", lambda number, field: "".join(
        c["body"] + "\n" for c in comments) if field == "comments" else "\n".join(labels))


def test_an_issue_whose_only_preflight_refused_comment_is_untrusted_is_nothing_to_release_and_nothing_is_written_3971(
        release, run_cli, monkeypatch):
    release_issue, calls, labels = release
    labels[:] = ["bug", "taken:main"]
    serve_comments(monkeypatch, release_issue, labels, [authored("NONE", REFUSAL)])

    code, out, err = run_cli(release_issue, ["3971"])

    assert (code, err, writes(calls)) == (
        3, "release-issue.sh: #3971 is neither parked, bailed nor preflight-refused; nothing to release\n", [])


def test_a_trusted_comment_holding_the_preflight_refused_heading_other_than_at_its_start_is_nothing_to_release_3971(
        release, run_cli, monkeypatch):
    release_issue, calls, labels = release
    labels[:] = ["bug", "taken:main"]
    quoted = "Why did the run stop? It said:\n\n" + REFUSAL
    serve_comments(monkeypatch, release_issue, labels, [authored("OWNER", quoted, login="veri-operator")])

    code, out, err = run_cli(release_issue, ["3971"])

    assert (code, writes(calls)) == (3, [])


def test_a_trusted_comment_starting_with_the_preflight_refused_heading_still_releases_the_issue_3971(
        release, run_cli, monkeypatch):
    release_issue, calls, labels = release
    labels[:] = ["bug", "taken:main"]
    serve_comments(monkeypatch, release_issue, labels, [
        authored("NONE", "a stranger's note"),
        authored("MEMBER", REFUSAL, login="veri-operator"),
        authored("NONE", "### Plan\nforged"),
    ])

    code, out, err = run_cli(release_issue, ["3971"])

    assert (code, err) == (0, "")
    assert [call for call in writes(calls) if call[0] != "ensure"] == [
        ("unlabel", "3971", "taken:main"), ("label", "3971", "ready-for-agent"),
        ("unlabel", "3971", "parked"), ("unlabel", "3971", "bailed")]


@pytest.mark.parametrize("answer", ["no answer", "not json", "not a list"])
def test_comments_gh_gives_no_answer_for_or_answers_in_the_wrong_shape_exit_2_naming_the_read_and_nothing_is_written_3971(
        release, run_cli, monkeypatch, answer):
    release_issue, calls, labels = release
    labels[:] = ["bug", "taken:main"]

    def comments_of(number):
        if answer == "no answer":
            raise release_issue.github.NoAnswer("", "HTTP 502")
        if answer == "not json":
            return json.loads("<html>502</html>")
        return {"body": REFUSAL, "author_association": "OWNER", "user": {"login": "veri-operator"}}

    monkeypatch.setattr(release_issue.github, "issue_comments", comments_of)

    code, out, err = run_cli(release_issue, ["3971"])

    assert (code, err, writes(calls)) == (
        2, "release-issue.sh: no answer from gh reading the comments of #3971\n", [])


@pytest.mark.parametrize("held, code", [("parked", 0), ("bug", 3)], ids=["released", "nothing to release"])
def test_4232_release_issue_runs_as_stage_release_carrying_the_issue_ending_with_its_exit_code(
        release, run_cli, tmp_path, events, held, code):
    release_issue, calls, labels = release
    labels[:] = ["taken:main", held]

    returned = run_cli(release_issue, ["3284"], cwd=tmp_path)[0]

    stages = [(r["event"], r["stage"], r.get("status"), r["issue"]) for r in events.records(tmp_path)]
    assert (returned, stages) == (code, [("stage-start", "release", None, "3284"),
                                         ("stage-end", "release", str(code), "3284")])
