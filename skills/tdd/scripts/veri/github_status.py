"""github-status.sh: whether GitHub's status page has an incident on the components veri needs, run in-process.

One read is bounded by VERI_GITHUB_STATUS_TIMEOUT per socket operation (connect, and each receive) and by MAX_BODY
bytes; its total time is not bounded: urllib has no whole-request deadline, and a server trickling bytes inside each
timeout could stretch it. Bounding the total would need a thread or a process, which this module does not start."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import datetime
import http.client
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

import entry
import tunables

USAGE = ("usage: github-status.sh [<component>…]\n"
         "       github-status.sh wait <max-seconds> [<component>…]   (<max-seconds>: 1 to 86400)")
FEED = "/api/v2/incidents/unresolved.json"
MAX_BODY = 1024 * 1024
MAX_WAIT = 86400
DEFAULT_COMPONENTS = ("Git Operations", "Pull Requests", "API Requests", "Issues", "Actions")
COMPONENTS = ("Git Operations", "Webhooks", "API Requests", "Issues", "Pull Requests", "Actions", "Packages", "Pages",
              "Copilot", "Codespaces", "Copilot AI Model Providers")


class NoAnswer(Exception):
    """The status page gave no answer; its message names the cause."""


def fetch(url, timeout):
    """(status, body) of one GET of `url`; an HTTP error status is answered, not raised."""
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            return response.status, response.read(MAX_BODY + 1)
    except urllib.error.HTTPError as error:
        return error.code, b""


sleep = time.sleep
monotonic = time.monotonic


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
    except (OSError, ValueError, http.client.HTTPException) as error:
        reason = getattr(error, "reason", error)
        if isinstance(reason, TimeoutError):
            raise NoAnswer("%s: no response within %d s (VERI_GITHUB_STATUS_TIMEOUT): %s" % (url, timeout, reason))
        raise NoAnswer("%s: no response: %s: %s" % (url, type(reason).__name__, reason))
    if status != 200:
        raise NoAnswer("%s: status %s" % (url, status))
    if len(body) > MAX_BODY:
        raise NoAnswer("%s: the body is larger than %d bytes" % (url, MAX_BODY))
    try:
        listed = json.loads(body)["incidents"]
    except (ValueError, TypeError, KeyError, RecursionError):
        listed = None
    if not isinstance(listed, list) or not all(well_formed(i) for i in listed):
        raise NoAnswer("%s: the body is not the feed's JSON (no incidents list of incident objects)" % url)
    return listed


def well_formed(incident):
    """Whether an incident is an object whose `components`, when present, is a list of objects whose `name`, when
    present, is a string."""
    if not isinstance(incident, dict):
        return False
    components = incident.get("components")
    return components is None or isinstance(components, list) and all(
        isinstance(c, dict) and isinstance(c.get("name", ""), str) for c in components)


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


def one_line(name):
    """A name as printed: its whitespace (tabs and newlines included) collapsed to single spaces; `(unnamed)` when
    missing or blank, so no name can split a line or forge another."""
    return " ".join(str(name).split()) if name is not None and str(name).strip() else "(unnamed)"


def judged(incident, components, threshold):
    """(counting, line) for an incident naming one of `components`, else None."""
    matched = list(dict.fromkeys(one_line(c.get("name")) for c in incident.get("components") or ()
                                 if c.get("name") in components))
    if not matched:
        return None
    start = started(incident)
    age = max(now() - start, datetime.timedelta(0))
    minutes = str(int(age.total_seconds() // 60))
    if age >= threshold:
        return True, "\t".join((one_line(incident.get("name")), ", ".join(matched),
                                 start.astimezone(local_zone()).strftime("%Y-%m-%d %H:%M"), minutes))
    return False, "young %s %s" % (minutes, one_line(incident.get("name")))


def read(components, threshold, timeout):
    """(code, lines) of one read: 1 and a line per counting incident, else 0 and `up` or the young lines.

    Any error the feed's data raises while it is judged (an out-of-range date, a missing key) is a NoAnswer, so a
    `wait` retries it; only the interpreter's own failures (MemoryError) propagate."""
    counting, young = {}, {}
    for index, incident in enumerate(incidents(timeout)):
        try:
            key = json.dumps(incident["id"], sort_keys=True) if incident.get("id") is not None else index
            verdict = judged(incident, components, threshold)
        except (ArithmeticError, LookupError, TypeError, ValueError, AttributeError) as error:
            raise NoAnswer("incident %r (created_at %r): %s: %s" % (incident.get("name"), incident.get("created_at"),
                                                                    type(error).__name__, error))
        if verdict is not None:
            (counting if verdict[0] else young).setdefault(key, verdict[1])
    return (1, list(counting.values())) if counting else (0, list(young.values()) or ["up"])


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
    deadline = monotonic() + max_seconds
    answered = None
    while True:
        try:
            answered = read_once()
        except NoAnswer as cause:
            no_answer(cause)
        else:
            if answered[0] == 0:
                return answered
        sleep(min(poll, max(0, deadline - monotonic())))
        if monotonic() >= deadline:
            if answered is None:
                return entry.refuse("github-status.sh: wait: no read got an answer in %s s" % max_seconds), []
            return 3, answered[1]


def main(argv):
    waiting = argv[:1] == ["wait"]
    if waiting:
        max_seconds = entry.whole_number(argv[1], 1) if len(argv) > 1 else None
        if max_seconds is None or max_seconds > MAX_WAIT:
            return entry.refuse("github-status.sh: wait needs <max-seconds>, a whole number from 1 to %d" % MAX_WAIT,
                                usage=USAGE)
        argv = argv[2:]
    components = tuple(argv) or DEFAULT_COMPONENTS
    knobs = {name: positive(name) for name in ("VERI_GITHUB_OUTAGE_MIN", "VERI_GITHUB_STATUS_TIMEOUT",
                                               "VERI_GITHUB_STATUS_POLL")}
    for name, value in knobs.items():
        if value is None:
            return entry.refuse("github-status.sh: %s=%r is not a positive integer" % (name, tunables.get(name)))
    base = tunables.get("VERI_GITHUB_STATUS_URL")
    if urllib.parse.urlsplit(base).scheme not in ("http", "https"):
        return entry.refuse("github-status.sh: VERI_GITHUB_STATUS_URL=%r is not an http or https URL" % base)
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
