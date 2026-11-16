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
