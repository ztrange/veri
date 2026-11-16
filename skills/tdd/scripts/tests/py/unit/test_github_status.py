"""In-process cases for veri/github_status.py, the module github-status.sh is a shim over.

Every case injects the fetch, the clock, the local timezone and the sleep: none touches the network or waits."""
import datetime
import http.client
import importlib
import json
import socket
import urllib.error

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
        self.at = NOW
        self.read_at = []
        self.sleeps = []
        monkeypatch.setattr(self.module, "fetch", self.fetch)
        monkeypatch.setattr(self.module, "now", lambda: self.at)
        monkeypatch.setattr(self.module, "local_zone", lambda: CST)
        monkeypatch.setattr(self.module, "sleep", self.sleep, raising=False)

    def sleep(self, seconds):
        self.sleeps.append(seconds)
        if len(self.sleeps) > 50:
            raise AssertionError("waited past any deadline")
        self.at += datetime.timedelta(seconds=seconds)

    def serve(self, *incidents, body=None, status=200, error=None):
        if body is None:
            body = json.dumps({"incidents": list(incidents)}).encode()
        self.answers.append((status, body, error))
        return self

    def fetch(self, url, timeout):
        self.calls.append((url, timeout))
        self.read_at.append(self.at)
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


def test_wait_whose_reads_find_a_counting_incident_then_none_exits_0_after_the_read_that_found_none_sleeping_the_poll_between(
        page, run_cli):
    page.serve(incident("Incident with Pull Requests", 120, "Pull Requests")).serve()

    code, out, _ = run_cli(page.module, ["wait", "600"], env={"VERI_GITHUB_STATUS_POLL": "60"})

    assert (code, out) == (0, "up\n")
    assert len(page.calls) == 2
    assert page.sleeps == [60]


def test_wait_whose_reads_all_find_a_counting_incident_until_max_seconds_pass_exits_3_making_no_read_after_that_time(
        page, run_cli):
    page.serve(incident("Incident with Pull Requests", 120, "Pull Requests"))

    code, _, _ = run_cli(page.module, ["wait", "1000"])

    assert code == 3
    assert page.read_at == [NOW + datetime.timedelta(seconds=s) for s in (0, 300, 600, 900)]


def test_wait_never_sleeps_past_max_seconds_when_the_poll_is_longer_than_what_is_left(page, run_cli):
    page.serve(incident("Incident with Pull Requests", 120, "Pull Requests"))

    code, _, _ = run_cli(page.module, ["wait", "5"])

    assert code == 3
    assert page.sleeps == [5]


def test_wait_whose_reads_all_get_no_answer_until_max_seconds_pass_exits_2(page, run_cli):
    page.serve(status=503)

    code, out, err = run_cli(page.module, ["wait", "1000"])

    assert (code, out) == (2, "")
    assert "status 503" in err
    assert page.read_at == [NOW + datetime.timedelta(seconds=s) for s in (0, 300, 600, 900)]


def test_wait_retries_a_read_with_no_answer_at_the_next_poll_and_exits_0_after_a_third_read_finding_none(
        page, run_cli):
    page.serve(incident("Incident with Pull Requests", 120, "Pull Requests")).serve(status=502).serve()

    code, out, _ = run_cli(page.module, ["wait", "3600"])

    assert (code, out) == (0, "up\n")
    assert len(page.calls) == 3


def test_wait_matches_the_components_named_after_max_seconds_and_with_none_the_default_set(page, run_cli):
    page.serve(incident("Webhooks delayed", 120, "Webhooks"))

    assert run_cli(page.module, ["wait", "600", "Webhooks"])[0] == 3
    assert run_cli(page.module, ["wait", "600"])[:2] == (0, "up\n")


@pytest.mark.parametrize("argv", [["wait"], ["wait", "0"], ["wait", "-5"], ["wait", "abc"], ["wait", ""],
                                  ["wait", "Actions"]])
def test_wait_with_a_max_seconds_missing_or_not_a_positive_integer_exits_2_with_the_usage_before_any_read(
        page, run_cli, argv):
    page.serve(incident("Incident with Pull Requests", 120, "Pull Requests"))

    code, out, err = run_cli(page.module, argv)

    assert (code, out) == (2, "")
    assert "usage: github-status.sh" in err
    assert page.calls == []


@pytest.mark.parametrize("argv", [[], ["wait", "600"]], ids=["one-shot", "wait"])
@pytest.mark.parametrize("value", ["0", "-1", "abc", ""])
def test_a_poll_that_is_not_a_positive_integer_exits_2_naming_it_before_any_read(page, run_cli, argv, value):
    page.serve(incident("Incident with Pull Requests", 120, "Pull Requests"))

    code, out, err = run_cli(page.module, argv, env={"VERI_GITHUB_STATUS_POLL": value})

    assert (code, out) == (2, "")
    assert "VERI_GITHUB_STATUS_POLL" in err
    assert page.calls == []


def malformed_components():
    bad = incident("Incident with Pull Requests", 120)
    bad["components"] = ["Pull Requests"]
    return {"body": json.dumps({"incidents": [bad]}).encode()}


@pytest.mark.parametrize("failed", [
    {"error": http.client.IncompleteRead(b"{")},
    {"error": http.client.BadStatusLine("garbage")},
    malformed_components(),
    {"body": b"[" * 200000},
], ids=["incomplete-read", "bad-status-line", "component-not-an-object", "nested-too-deep"])
def test_wait_retries_every_kind_of_failed_read_at_the_next_poll_and_exits_0_when_a_later_read_finds_none(
        page, run_cli, failed):
    page.serve(incident("Incident with Pull Requests", 120, "Pull Requests")).serve(**failed).serve()

    code, out, err = run_cli(page.module, ["wait", "3600"])

    assert (code, out) == (0, "up\n")
    assert len(page.calls) == 3
    assert "no answer from GitHub's status page" in err


def test_wait_whose_reads_never_answered_ends_with_one_line_saying_no_read_got_an_answer_in_max_seconds(page, run_cli):
    page.serve(error=ConnectionRefusedError(61, "Connection refused"))

    code, out, err = run_cli(page.module, ["wait", "600"])

    assert (code, out) == (2, "")
    assert err.splitlines()[-1] == "github-status.sh: wait: no read got an answer in 600 s"


@pytest.mark.parametrize("error, cause", [
    (urllib.error.URLError(ConnectionRefusedError(61, "Connection refused")), "Connection refused"),
    (urllib.error.URLError(socket.gaierror(8, "nodename nor servname provided")), "nodename nor servname provided"),
], ids=["refused", "dns"])
def test_a_fetch_failing_other_than_by_timeout_names_its_cause_and_not_a_timeout(page, run_cli, error, cause):
    page.serve(error=error)

    code, out, err = run_cli(page.module, [])

    assert (code, out) == (2, "")
    assert cause in err
    assert "no response within" not in err


def test_a_timeout_wrapped_by_urllib_is_still_named_as_no_response_within_the_timeout(page, run_cli):
    page.serve(error=urllib.error.URLError(TimeoutError("timed out")))

    code, _, err = run_cli(page.module, [], env={"VERI_GITHUB_STATUS_TIMEOUT": "9"})

    assert code == 2
    assert "no response within 9 s (VERI_GITHUB_STATUS_TIMEOUT)" in err


class Oversized:
    """A response whose body is larger than any feed: it answers whatever amount is asked, up to 2 MiB."""

    status = 200

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def read(self, amount=None):
        size = 2 * 1024 * 1024
        return b"x" * (size if amount is None or amount < 0 else min(amount, size))


def test_a_body_larger_than_the_cap_is_no_answer_and_never_read_whole(monkeypatch, run_cli):
    import urllib.request

    monkeypatch.setattr(urllib.request, "urlopen", lambda url, timeout: Oversized())
    module = importlib.import_module("veri.github_status")

    code, out, err = run_cli(module, [])

    assert (code, out) == (2, "")
    assert "larger than %d bytes" % module.MAX_BODY in err


@pytest.mark.parametrize("url", ["file:///etc/passwd", "ftp://status.example", "status.example"])
def test_a_status_url_whose_scheme_is_not_http_or_https_exits_2_naming_it_before_any_fetch(page, run_cli, url):
    page.serve()

    code, out, err = run_cli(page.module, [], env={"VERI_GITHUB_STATUS_URL": url})

    assert (code, out) == (2, "")
    assert "VERI_GITHUB_STATUS_URL" in err
    assert page.calls == []


def test_a_name_holding_tabs_or_newlines_prints_on_one_line_with_whitespace_collapsed_and_a_missing_one_as_unnamed(
        page, run_cli):
    forged = incident("Slow\tPRs\nFake incident\tActions", 61, "Pull Requests")
    unnamed = incident(None, 45, "Actions")
    del unnamed["name"]
    young = incident("Young\n\tone", 5, "Issues")
    page.serve(forged, unnamed)

    code, out, _ = run_cli(page.module, [])

    assert (code, out) == (1, "Slow PRs Fake incident Actions\tPull Requests\t2026-11-16 04:59\t61\n"
                              "(unnamed)\tActions\t2026-11-16 05:15\t45\n")
    page.serve(young)
    assert run_cli(page.module, [])[:2] == (0, "young 5 Young one\n")
