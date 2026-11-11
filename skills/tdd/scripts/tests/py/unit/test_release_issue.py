"""In-process cases for release-issue.sh: a parked, bailed or preflight-refused issue goes back to the queue in one call."""
import importlib

import pytest


@pytest.fixture
def release(monkeypatch):
    """release_issue with every gh call faked; returns (module, calls, labels) — set labels[:] per case."""
    release_issue = importlib.import_module("veri.release_issue")
    github = release_issue.github
    calls, labels = [], []
    monkeypatch.setattr(github, "gh_issue_view", lambda number, field: calls.append(("view", number, field)) or ("" if field == "comments" else "\n".join(labels)))
    monkeypatch.setattr(github, "gh_label_ensure", lambda label: calls.append(("ensure", label)))
    monkeypatch.setattr(github, "gh_issue_add_label", lambda number, label: calls.append(("label", number, label)))
    monkeypatch.setattr(github, "gh_issue_remove_label", lambda number, label: calls.append(("unlabel", number, label)))
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
    monkeypatch.setattr(
        release_issue.github, "gh_issue_view",
        lambda number, field: "### ⛔ Preflight refused — requirements clash" if field == "comments" else "\n".join(labels))

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
    refusal = "### ⛔ Preflight refused — requirements clash"
    state = {"comments": refusal}

    def view(number, field):
        if field == "comments":
            if state["comments"] is None:
                raise release_issue.github.NoAnswer("")
            return state["comments"]
        return "\n".join(labels)

    monkeypatch.setattr(release_issue.github, "gh_issue_view", view)

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
        "comments unreadable": (3, False),
    }


def test_a_preflight_release_cut_short_by_a_silent_gh_is_finished_by_running_it_again_3627(release, run_cli, monkeypatch):
    release_issue, calls, labels = release
    labels[:] = ["bug", "taken:main"]
    silent = {"claim": True}
    monkeypatch.setattr(
        release_issue.github, "gh_issue_view",
        lambda number, field: "### ⛔ Preflight refused — requirements clash" if field == "comments" else "\n".join(labels))
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
    monkeypatch.setattr(
        release_issue.github, "gh_issue_view",
        lambda number, field: "### ⛔ Preflight refused — requirements clash" if field == "comments" else "\n".join(labels))

    code, out, err = run_cli(release_issue, ["3621"])

    assert code == 2
    assert writes(calls) == []
    assert "taken:mu" in err


def test_a_claimed_unopted_issue_with_only_other_comments_still_exits_3_and_nothing_is_written_3627(release, run_cli, monkeypatch):
    release_issue, calls, labels = release
    labels[:] = ["bug", "taken:main"]
    monkeypatch.setattr(
        release_issue.github, "gh_issue_view",
        lambda number, field: "### Plan\nstep 1 done" if field == "comments" else "\n".join(labels))

    code, out, err = run_cli(release_issue, ["3621"])

    assert code == 3
    assert writes(calls) == []
