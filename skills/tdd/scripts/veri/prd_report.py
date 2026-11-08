"""report.sh's renderer, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import datetime
import json
import sys

USAGE = "usage: report.sh --report"


def main(argv):
    if argv == ["--report"]:
        with open(".tdd/report-cache.json") as f:
            fetched = json.load(f)["fetched_at"]
        then = datetime.datetime.strptime(fetched, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc)
        hours = int((datetime.datetime.now(datetime.timezone.utc) - then).total_seconds() // 3600)
        print("snapshot age: %d hours" % hours)
        return 0
    print(USAGE, file=sys.stderr)
    return 2


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
