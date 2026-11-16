"""In-process cases for veri/github_status.py, the module github-status.sh is a shim over.

Every case injects the fetch, the clock, the local timezone and the sleep: none touches the network or waits."""
import datetime
import importlib
import json

import pytest

NOW = datetime.datetime(2026, 11, 16, 12, 0, tzinfo=datetime.timezone.utc)
CST = datetime.timezone(datetime.timedelta(hours=-6))
DEFAULTS = ("Git Operations", "Pull Requests", "API Requests", "Issues", "Actions")


def incident(name, minutes_ago, *components, impact="minor"):
    opened = NOW - datetime.timedelta(minutes=minutes_ago)
    return {"name": name, "impact": impact, "created_at": opened.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "components": [{"name": c, "status": "degraded_performance"} for c in components]}


class Page:
    """The injected status page: what each read answers, and every URL it was asked for."""

    def __init__(self, monkeypatch):
        self.module = importlib.import_module("veri.github_status")
        self.calls = []
        self.answers = []
        monkeypatch.setattr(self.module, "fetch", self.fetch)
        monkeypatch.setattr(self.module, "now", lambda: NOW)
        monkeypatch.setattr(self.module, "local_zone", lambda: CST)

    def serve(self, *incidents, body=None, status=200, error=None):
        if body is None:
            body = json.dumps({"incidents": list(incidents)}).encode()
        self.answers.append((status, body, error))
        return self

    def fetch(self, url, timeout):
        self.calls.append((url, timeout))
        status, body, error = self.answers[min(len(self.calls), len(self.answers)) - 1]
        if error is not None:
            raise error
        return status, body


@pytest.fixture
def page(monkeypatch):
    return Page(monkeypatch)


def test_with_no_argument_it_reads_the_unresolved_feed_under_the_base_url_and_matches_the_five_default_components_only(
        page, run_cli):
    page.serve(*[incident("Down: " + c, 60, c) for c in DEFAULTS + ("Webhooks", "Copilot")])

    code, out, _ = run_cli(page.module, [], env={"VERI_GITHUB_STATUS_URL": "https://status.example"})

    assert code == 1
    assert page.calls[0][0] == "https://status.example/api/v2/incidents/unresolved.json"
    assert sorted(line.split("\t")[0] for line in out.splitlines()) == sorted("Down: " + c for c in DEFAULTS)


def test_with_component_arguments_it_matches_those_components_only(page, run_cli):
    page.serve(*[incident("Down: " + c, 60, c) for c in DEFAULTS + ("Webhooks", "Copilot")])

    code, out, _ = run_cli(page.module, ["Webhooks", "Copilot"])

    assert code == 1
    assert page.calls[0][0] == "https://www.githubstatus.com/api/v2/incidents/unresolved.json"
    assert sorted(line.split("\t")[0] for line in out.splitlines()) == ["Down: Copilot", "Down: Webhooks"]


def test_an_incident_opened_exactly_the_threshold_ago_counts_whatever_its_impact_and_status_and_one_a_minute_younger_does_not(
        page, run_cli):
    old = incident("Old enough", 45, "Actions", impact="none")
    old["components"][0]["status"] = "operational"
    page.serve(old, incident("A minute short", 44, "Actions", impact="critical"))

    code, out, _ = run_cli(page.module, [], env={"VERI_GITHUB_OUTAGE_MIN": "45"})

    assert code == 1
    assert [line.split("\t")[0] for line in out.splitlines()] == ["Old enough"]


def test_two_counting_incidents_exit_1_with_one_line_each_naming_it_its_matched_components_its_local_start_and_its_age(
        page, run_cli):
    page.serve(incident("Incident with Pull Requests", 61.5, "Pull Requests", "Copilot", "Actions"),
               incident("Git slow", 30, "Git Operations"))

    code, out, _ = run_cli(page.module, [])

    assert (code, out) == (1, "Incident with Pull Requests\tPull Requests, Actions\t2026-11-16 04:58\t61\n"
                              "Git slow\tGit Operations\t2026-11-16 05:30\t30\n")


def test_no_incident_naming_a_component_exits_0_printing_up(page, run_cli):
    page.serve(incident("Copilot down", 120, "Copilot"))

    assert run_cli(page.module, [])[:2] == (0, "up\n")


def test_only_incidents_younger_than_the_threshold_exit_0_printing_a_young_line_each_and_no_up(page, run_cli):
    page.serve(incident("Slow PRs", 12.5, "Pull Requests"), incident("Copilot down", 120, "Copilot"),
               incident("Slow issues", 5, "Issues"))

    assert run_cli(page.module, [])[:2] == (0, "young 12 Slow PRs\nyoung 5 Slow issues\n")


def test_an_incident_with_empty_or_absent_components_never_counts_however_old(page, run_cli):
    absent = incident("Something somewhere", 600)
    del absent["components"]
    page.serve(incident("Unnamed trouble", 600), absent)

    assert run_cli(page.module, [])[:2] == (0, "up\n")


def unparseable_start():
    bad = incident("Incident with Pull Requests", 120, "Pull Requests")
    bad["created_at"] = "this morning"
    return {"body": json.dumps({"incidents": [bad]}).encode()}


@pytest.mark.parametrize("answer, cause", [
    ({"error": TimeoutError("timed out")}, "no response within 7 s (VERI_GITHUB_STATUS_TIMEOUT)"),
    ({"status": 503}, "status 503"),
    ({"body": b"<html>unicorn</html>"}, "not the feed's JSON"),
    ({"body": b'{"page": {}}'}, "not the feed's JSON"),
    (unparseable_start(), "created_at 'this morning'"),
], ids=["no-response", "status-503", "not-json", "no-incidents-list", "bad-created-at"])
def test_no_answer_from_the_status_page_exits_2_naming_the_cause_and_never_0_or_1(page, run_cli, answer, cause):
    page.serve(incident("Incident with Pull Requests", 120, "Pull Requests"), **answer)

    code, out, err = run_cli(page.module, [], env={"VERI_GITHUB_STATUS_TIMEOUT": "7"})

    assert (code, out) == (2, "")
    assert cause in err
    assert page.calls[0][1] == 7


@pytest.mark.parametrize("name", ["VERI_GITHUB_OUTAGE_MIN", "VERI_GITHUB_STATUS_TIMEOUT"])
@pytest.mark.parametrize("value", ["0", "-1", "abc", ""])
def test_a_threshold_or_timeout_that_is_not_a_positive_integer_exits_2_naming_it_before_any_fetch(
        page, run_cli, name, value):
    page.serve(incident("Incident with Pull Requests", 120, "Pull Requests"))

    code, out, err = run_cli(page.module, [], env={name: value})

    assert (code, out) == (2, "")
    assert name in err
    assert page.calls == []


def test_a_component_argument_that_is_not_one_of_githubs_names_exits_2_naming_it_and_listing_them_before_any_fetch(
        page, run_cli):
    page.serve()

    code, out, err = run_cli(page.module, ["Actions", "pull requests"])

    assert (code, out) == (2, "")
    assert "'pull requests'" in err
    for name in ("Git Operations", "Webhooks", "API Requests", "Issues", "Pull Requests", "Actions", "Packages",
                 "Pages", "Copilot", "Codespaces", "Copilot AI Model Providers"):
        assert name in err
    assert page.calls == []


def test_the_real_fetch_answers_an_http_error_status_rather_than_raising_it(monkeypatch):
    import urllib.error
    import urllib.request

    def refused(url, timeout):
        raise urllib.error.HTTPError(url, 503, "Service Unavailable", {}, None)

    monkeypatch.setattr(urllib.request, "urlopen", refused)
    module = importlib.import_module("veri.github_status")

    assert module.fetch("https://status.example/feed", 3) == (503, b"")
