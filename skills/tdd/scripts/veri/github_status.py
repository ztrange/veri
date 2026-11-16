"""github-status.sh: whether GitHub's status page has an incident on the components veri needs, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import datetime
import json
import sys
import time
import urllib.error
import urllib.request

import entry
import tunables

USAGE = ("usage: github-status.sh [<component>…]\n"
         "       github-status.sh wait <max-seconds> [<component>…]")
FEED = "/api/v2/incidents/unresolved.json"
DEFAULT_COMPONENTS = ("Git Operations", "Pull Requests", "API Requests", "Issues", "Actions")
COMPONENTS = ("Git Operations", "Webhooks", "API Requests", "Issues", "Pull Requests", "Actions", "Packages", "Pages",
              "Copilot", "Codespaces", "Copilot AI Model Providers")


class NoAnswer(Exception):
    """The status page gave no answer; its message names the cause."""


def fetch(url, timeout):
    """(status, body) of one GET of `url`; an HTTP error status is answered, not raised."""
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            return response.status, response.read()
    except urllib.error.HTTPError as error:
        return error.code, b""


sleep = time.sleep


def now():
    return datetime.datetime.now(datetime.timezone.utc)


def local_zone():
    """The zone a start is printed in: None, the machine's own."""
    return None


def incidents(timeout):
    """The feed's incidents, or NoAnswer naming why there is none."""
    url = tunables.get("VERI_GITHUB_STATUS_URL") + FEED
    try:
        status, body = fetch(url, timeout)
    except (OSError, ValueError) as error:
        raise NoAnswer("%s: no response within %d s (VERI_GITHUB_STATUS_TIMEOUT): %s" % (url, timeout, error))
    if status != 200:
        raise NoAnswer("%s: status %s" % (url, status))
    try:
        listed = json.loads(body)["incidents"]
    except (ValueError, TypeError, KeyError):
        listed = None
    if not isinstance(listed, list) or not all(isinstance(i, dict) for i in listed):
        raise NoAnswer("%s: the body is not the feed's JSON (no incidents list)" % url)
    return listed


def started(incident):
    """The incident's created_at as an aware datetime, or NoAnswer."""
    raw = incident.get("created_at")
    try:
        start = datetime.datetime.fromisoformat(raw)
    except (TypeError, ValueError):
        start = None
    if start is None or start.tzinfo is None:
        raise NoAnswer("incident %r: created_at %r cannot be parsed" % (incident.get("name"), raw))
    return start


def read(components, threshold, timeout):
    """(code, lines) of one read: 1 and a line per counting incident, else 0 and `up` or the young lines."""
    counting, young = [], []
    for incident in incidents(timeout):
        matched = [c.get("name") for c in incident.get("components") or () if c.get("name") in components]
        if not matched:
            continue
        start = started(incident)
        age = now() - start
        minutes = str(int(age.total_seconds() // 60))
        if age >= threshold:
            counting.append("\t".join((str(incident.get("name")), ", ".join(matched),
                                       start.astimezone(local_zone()).strftime("%Y-%m-%d %H:%M"), minutes)))
        else:
            young.append("young %s %s" % (minutes, incident.get("name")))
    return (1, counting) if counting else (0, young or ["up"])


def positive(name):
    """The tunable's value as an int of at least 1, or None."""
    return entry.whole_number(tunables.get(name), 1)


def no_answer(cause):
    """Report a read that got no answer; 2."""
    return entry.refuse("github-status.sh: no answer from GitHub's status page: %s" % cause)


def wait(read_once, max_seconds, poll):
    """(code, lines): 0 and the first read finding nothing counting; 3 and the last counting read's lines once
    `max_seconds` pass, with no read after; 2 and no lines when no read in that time got an answer.
    A read with no answer is reported and retried at the next poll."""
    deadline = now() + datetime.timedelta(seconds=max_seconds)
    answered = None
    while True:
        try:
            answered = read_once()
        except NoAnswer as cause:
            no_answer(cause)
        else:
            if answered[0] == 0:
                return answered
        sleep(poll)
        if now() >= deadline:
            if answered is None:
                return entry.refuse("github-status.sh: wait: no read got an answer in %s s" % max_seconds), []
            return 3, answered[1]


def main(argv):
    waiting = argv[:1] == ["wait"]
    if waiting:
        max_seconds = entry.whole_number(argv[1], 1) if len(argv) > 1 else None
        if max_seconds is None:
            return entry.refuse("github-status.sh: wait needs <max-seconds>, a positive integer", usage=USAGE)
        argv = argv[2:]
    components = tuple(argv) or DEFAULT_COMPONENTS
    knobs = {name: positive(name) for name in ("VERI_GITHUB_OUTAGE_MIN", "VERI_GITHUB_STATUS_TIMEOUT",
                                               "VERI_GITHUB_STATUS_POLL")}
    for name, value in knobs.items():
        if value is None:
            return entry.refuse("github-status.sh: %s=%r is not a positive integer" % (name, tunables.get(name)))
    for name in components:
        if name not in COMPONENTS:
            return entry.refuse("github-status.sh: %r is not a GitHub component; the components are: %s"
                                % (name, ", ".join(COMPONENTS)), usage=USAGE)
    threshold = datetime.timedelta(minutes=knobs["VERI_GITHUB_OUTAGE_MIN"])

    def read_once():
        return read(components, threshold, knobs["VERI_GITHUB_STATUS_TIMEOUT"])

    if waiting:
        code, lines = wait(read_once, max_seconds, knobs["VERI_GITHUB_STATUS_POLL"])
    else:
        try:
            code, lines = read_once()
        except NoAnswer as cause:
            return no_answer(cause)
    for line in lines:
        print(line)
    return code


if __name__ == "__main__":
    entry.run(main, sys.argv[1:])
