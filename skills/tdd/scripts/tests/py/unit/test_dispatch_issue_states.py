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
