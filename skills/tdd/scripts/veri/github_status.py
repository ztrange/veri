"""github-status.sh: whether GitHub's status page has an incident on the components veri needs, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import datetime
import json
import sys
import urllib.request

import entry
import tunables

USAGE = "usage: github-status.sh [<component>…]"
FEED = "/api/v2/incidents/unresolved.json"
DEFAULT_COMPONENTS = ("Git Operations", "Pull Requests", "API Requests", "Issues", "Actions")


def fetch(url, timeout):
    """(status, body) of one GET of `url`."""
    with urllib.request.urlopen(url, timeout=timeout) as response:
        return response.status, response.read()


def now():
    return datetime.datetime.now(datetime.timezone.utc)


def local_zone():
    """The zone a start is printed in: None, the machine's own."""
    return None


def main(argv):
    components = tuple(argv) or DEFAULT_COMPONENTS
    _, body = fetch(tunables.get("VERI_GITHUB_STATUS_URL") + FEED, 15)
    threshold = datetime.timedelta(minutes=int(tunables.get("VERI_GITHUB_OUTAGE_MIN")))
    counting = []
    for incident in json.loads(body)["incidents"]:
        matched = [c["name"] for c in incident.get("components") or () if c["name"] in components]
        start = datetime.datetime.fromisoformat(incident["created_at"])
        age = now() - start
        if matched and age >= threshold:
            counting.append("\t".join((incident["name"], ", ".join(matched),
                                       start.astimezone(local_zone()).strftime("%Y-%m-%d %H:%M"),
                                       str(int(age.total_seconds() // 60)))))
    for line in counting:
        print(line)
    return 1 if counting else 0


if __name__ == "__main__":
    entry.run(main, sys.argv[1:])
