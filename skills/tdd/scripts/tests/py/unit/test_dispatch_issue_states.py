"""In-process case for dispatch.issue_states, the one github read behind dispatch's stall check."""
import importlib
import json


def test_issue_states_answers_open_and_closed_for_every_named_issue_from_one_github_read_issue_3551(monkeypatch):
    dispatch = importlib.import_module("veri.dispatch")
    reads = []

    def gh_issue_list(*args):
        reads.append(args)
        return json.dumps([{"number": 2517, "state": "CLOSED"}, {"number": 2483, "state": "CLOSED"},
                           {"number": 3551, "state": "OPEN"}])

    monkeypatch.setattr(dispatch.github, "gh_issue_list", gh_issue_list)

    states = dispatch.issue_states(["2517", "2483", "3551"])

    assert (states, len(reads)) == ({"2517": "CLOSED", "2483": "CLOSED", "3551": "OPEN"}, 1)


def test_issue_states_reads_closed_issues_beyond_the_default_page_and_omits_an_unlisted_one_issue_3551(monkeypatch):
    dispatch = importlib.import_module("veri.dispatch")
    everything = [{"number": n, "state": "OPEN" if n % 2 else "CLOSED"} for n in range(1, 601)]

    def gh_issue_list(*args):
        option = dict(zip(args[::2], args[1::2]))
        listed = [item for item in everything if option.get("--state", "open") == "all" or item["state"] == "OPEN"]
        return json.dumps(listed[:int(option.get("--limit", "30"))])

    monkeypatch.setattr(dispatch.github, "gh_issue_list", gh_issue_list)

    states = dispatch.issue_states(["500", "501", "99999"])

    assert states == {"500": "CLOSED", "501": "OPEN"}


class _StopWaiting(Exception):
    pass


def test_main_waits_out_a_403_secondary_rate_limit_on_the_stall_check_issue_states_read_and_goes_on_issue_3582(
        monkeypatch, capsys, tmp_path):
    import os
    import subprocess
    dispatch = importlib.import_module("veri.dispatch")
    tdd = tmp_path / ".tdd" / "wt" / "7" / ".tdd"
    tdd.mkdir(parents=True)
    (tdd / "restart-pending").write_text("")
    events = tdd / "events.jsonl"
    events.write_text('{"event": "leaf-start"}\n')
    os.utime(events, (1000, 1000))
    lives = [["7"], []]
    ticks = [1000, 1000, 1000, 1003]
    waits = []
    reads = []

    def wait():
        waits.append(1)
        if len(waits) > 8:
            raise _StopWaiting

    def run(argv, *args, **kw):
        assert argv[:3] == ["gh", "issue", "list"], argv
        reads.append(argv)
        if len(reads) <= 2:
            return subprocess.CompletedProcess(
                argv, 1, "", "HTTP 403: You have exceeded a secondary rate limit. Please wait a few minutes "
                             "before you try again. (https://api.github.com/repos/o/r/issues)\n")
        return subprocess.CompletedProcess(argv, 0, json.dumps([{"number": 7, "state": "OPEN"}]), "")

    monkeypatch.setenv("VERI_DISPATCH_STALL", "2")
    monkeypatch.setattr(dispatch.os, "kill", lambda pid, sig: None)
    monkeypatch.setattr(dispatch.status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(dispatch.github.subprocess, "run", run)
    monkeypatch.setattr(dispatch.github.time, "sleep", lambda seconds: None)
    monkeypatch.setattr(dispatch, "clock", lambda: ticks.pop(0) if len(ticks) > 1 else ticks[0], raising=False)
    monkeypatch.setattr(dispatch, "live_conductors", lambda: lives.pop(0) if len(lives) > 1 else lives[0], raising=False)
    monkeypatch.setattr(dispatch, "queued_merges", lambda: [], raising=False)
    monkeypatch.setattr(dispatch, "solvable_issues", lambda: ["12"], raising=False)
    monkeypatch.setattr(dispatch, "launch", lambda issue: None, raising=False)
    monkeypatch.setattr(dispatch, "last_comment", lambda issue: "### 🔧 Working on it\n\nbody", raising=False)
    monkeypatch.setattr(dispatch, "wait", wait, raising=False)

    try:
        code = dispatch.main(["--target", "1"])
    except _StopWaiting:
        code = "looping"

    assert (code, capsys.readouterr().out) == (0, "stalled 7\n")
