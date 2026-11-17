"""In-process cases for the run-state labels veri keeps on an issue: `bailed` and `pr-ready`."""
import importlib

import pytest

DELETE_BAILED = ("gh", "api", "-X", "DELETE", "repos/{owner}/{repo}/issues/42/labels/bailed")
DELETE_PR_READY = ("gh", "api", "-X", "DELETE", "repos/{owner}/{repo}/issues/42/labels/pr-ready")
ADD_TAKEN_MAIN = ("gh", "api", "repos/{owner}/{repo}/issues/42/labels", "-f", "labels[]=taken:main")
ADD_BAILED = ("gh", "api", "repos/{owner}/{repo}/issues/42/labels", "-f", "labels[]=bailed")


def fake_gh(fake_processes, answer):
    """gh answered by <answer>(argv tuple) → (returncode, stdout, stderr); returns the argv tuples run."""
    calls = []

    def respond(line, **kwargs):
        argv = tuple(str(arg) for arg in fake.argvs[-1])
        calls.append(argv)
        return answer(argv)

    fake = fake_processes.answers({"": respond})
    return calls


@pytest.fixture
def github():
    return importlib.import_module("veri.github")


def test_gh_issue_remove_label_deletes_the_label_from_the_issue(github, fake_processes):
    calls = fake_gh(fake_processes, lambda args: (0, "", ""))

    github.gh_issue_remove_label("42", "bailed")

    assert calls == [DELETE_BAILED]


def test_gh_issue_remove_label_raises_no_answer_when_gh_refuses_the_delete(github, fake_processes):
    fake_gh(fake_processes, lambda args: (1, "", "HTTP 502: Bad Gateway\n"))

    with pytest.raises(github.NoAnswer):
        github.gh_issue_remove_label("42", "bailed")


def test_gh_issue_remove_label_returns_when_the_issue_does_not_carry_the_label(github, fake_processes):
    calls = fake_gh(fake_processes, lambda args: (1, "", "gh: Label does not exist (HTTP 404)\n"))

    github.gh_issue_remove_label("42", "bailed")

    assert calls == [DELETE_BAILED]


@pytest.fixture
def event():
    return importlib.import_module("veri.event")


def clone(tmp_path):
    (tmp_path / "clone" / ".git").mkdir(parents=True)
    (tmp_path / "clone" / ".git" / "config").write_text("[core]\n\tbare = false\n")
    return str(tmp_path / "clone")


def test_a_bail_event_labels_the_state_label_issue_bailed_and_takes_its_pr_ready_label_off(event, monkeypatch, tmp_path, fake_processes):
    monkeypatch.setenv("VERI_STATE_LABEL_ISSUE", "42")
    calls = fake_gh(fake_processes, lambda args: (0, "", ""))

    code = event.append(clone(tmp_path), {"issue": "42"}, "bail", ["cause=revise-exhausted"], ts=1700000000)

    assert (code, calls) == (0, [ADD_BAILED, DELETE_PR_READY])


def test_a_resume_event_takes_the_bailed_label_off_the_state_label_issue_and_re_claims_it_3460(event, monkeypatch, tmp_path, fake_processes):
    monkeypatch.setenv("VERI_STATE_LABEL_ISSUE", "42")
    monkeypatch.delenv("VERI_LABEL", raising=False)
    calls = fake_gh(fake_processes, lambda args: (0, "", ""))

    code = event.append(clone(tmp_path), {"issue": "42"}, "resume", [], ts=1700000000)

    assert (code, DELETE_BAILED in calls, ADD_TAKEN_MAIN in calls) == (0, True, True)


def test_a_resume_event_adds_the_lane_taken_label_and_takes_the_opt_in_label_off_a_released_issue_3460(event, monkeypatch, tmp_path, fake_processes):
    monkeypatch.setenv("VERI_STATE_LABEL_ISSUE", "42")
    monkeypatch.setenv("VERI_LABEL", "ready-for-agent")
    calls = fake_gh(fake_processes, lambda args: (0, "", ""))

    code = event.append(clone(tmp_path), {"issue": "42"}, "resume", [], ts=1700000000)

    delete_opt_in = ("gh", "api", "-X", "DELETE", "repos/{owner}/{repo}/issues/42/labels/ready-for-agent")
    assert (code, ADD_TAKEN_MAIN in calls, delete_opt_in in calls) == (0, True, True)


ADD_STOPPED = ("gh", "api", "repos/{owner}/{repo}/issues/42/labels", "-f", "labels[]=stopped")


def test_issue_4081_a_stop_event_labels_the_state_label_issue_stopped(event, monkeypatch, tmp_path, fake_processes):
    monkeypatch.setenv("VERI_STATE_LABEL_ISSUE", "42")
    calls = fake_gh(fake_processes, lambda args: (0, "", ""))

    code = event.append(clone(tmp_path), {"issue": "42"}, "stop", ["mode=now", "at=green"], ts=1700000000)

    assert (code, calls) == (0, [ADD_STOPPED])


DELETE_STOPPED = ("gh", "api", "-X", "DELETE", "repos/{owner}/{repo}/issues/42/labels/stopped")


@pytest.mark.parametrize("name", ["start", "resume"])
def test_issue_4081_a_start_or_resume_event_takes_the_stopped_label_off_as_it_takes_bailed_off(event, fake_processes, name):
    calls = fake_gh(fake_processes, lambda args: (0, "", ""))

    event.state_labels(name.encode(), "42")

    assert (DELETE_BAILED in calls, DELETE_STOPPED in calls) == (True, True)


def test_a_bail_event_gh_refuses_to_label_still_writes_its_line_exits_0_and_names_the_refusal(event, monkeypatch, tmp_path, capsys, fake_processes):
    monkeypatch.setenv("VERI_STATE_LABEL_ISSUE", "42")
    fake_gh(fake_processes, lambda args: (1, "", "HTTP 502: Bad Gateway\n"))
    run = clone(tmp_path)

    code = event.append(run, {"issue": "42"}, "bail", ["cause=revise-exhausted"], ts=1700000000)

    lines = open(run + "/.tdd/events.jsonl").read().count("\n")
    assert (code, lines, capsys.readouterr().err) == (0, 1, "event: no answer from gh labelling #42's run state\n")


SHA = "b" * 40
HEAD_READ = ("gh", "api", "repos/{owner}/{repo}/pulls/7", "--jq", ".head.sha")
PORCELAIN = ("gh", "pr", "ready", "7")
ADD_PR_READY = ("gh", "api", "repos/{owner}/{repo}/issues/42/labels", "-f", "labels[]=pr-ready")


def test_pr_ready_labels_the_state_label_issue_pr_ready_once_github_marked_the_pr_ready(run_cli, fake_processes):
    pr_ready = importlib.import_module("veri.pr_ready")
    calls = fake_gh(fake_processes, lambda args: (0, SHA + "\n", "") if args == HEAD_READ else (0, "", ""))

    result = run_cli(pr_ready, ["7", SHA], env={"VERI_GH_DRIVER": "auto", "VERI_STATE_LABEL_ISSUE": "42"})

    assert (result, calls) == ((0, "", ""), [HEAD_READ, PORCELAIN, ADD_PR_READY])


def test_pr_ready_gh_refuses_to_label_still_exits_0_and_names_the_refusal(run_cli, fake_processes):
    pr_ready = importlib.import_module("veri.pr_ready")
    fake_gh(fake_processes, lambda args: {HEAD_READ: (0, SHA + "\n", ""), PORCELAIN: (0, "", "")}.get(args, (1, "", "")))

    result = run_cli(pr_ready, ["7", SHA], env={"VERI_GH_DRIVER": "auto", "VERI_STATE_LABEL_ISSUE": "42"})

    assert result == (0, "", "pr-ready.sh: no answer from gh labelling #42 pr-ready\n")


def test_park_issue_takes_the_bailed_label_off_the_issue_it_parks(run_cli, fake_processes):
    park_issue = importlib.import_module("veri.park_issue")
    calls = fake_gh(fake_processes, lambda args: (0, "{}", ""))

    result = run_cli(park_issue, ["42", "second bail", "a human reads the diff"])

    assert (result[0], DELETE_BAILED in calls) == (0, True)


def test_issue_4081_park_issue_in_a_repository_with_no_parked_label_exits_2_creates_no_label_and_posts_no_comment(run_cli, fake_processes):
    park_issue = importlib.import_module("veri.park_issue")
    missing = (1, "", "gh: Not Found (HTTP 404)\n")
    calls = fake_gh(fake_processes, lambda args: missing if args[-1].endswith("labels/parked") else (0, "{}", ""))

    code, out, err = run_cli(park_issue, ["42", "second bail", "a human reads the diff"])

    writes = [argv for argv in calls if "-f" in argv or "-F" in argv or "POST" in argv or "--body-file" in argv]
    assert (code, writes) == (2, []), calls
    assert "parked" in err, err
