"""stop-reason.sh's report, run in-process."""
import json
import os
import sys


def main(argv):
    if len(argv) != 1:
        sys.stderr.write("usage: stop-reason.sh <issue>\n")
        return 2
    if not os.path.isdir(os.path.join(".tdd", "wt", argv[0])):
        sys.stderr.write("stop-reason.sh: no run for issue %s under .tdd/wt\n" % argv[0])
        return 2
    log = os.path.join(".tdd", "wt", argv[0], ".tdd", "events.jsonl")
    with open(log) as f:
        last = json.loads(f.read().splitlines()[-1])
    if last.get("event") == "done":
        sys.stdout.write("done %s\n" % last.get("pr"))
    elif last.get("event") == "bail":
        sys.stdout.write("bailed %s %s\n" % (last.get("phase"), last.get("classification")))
    elif last.get("event") == "stop":
        sys.stdout.write("stopped %s\n" % last.get("mode"))
    elif _live(os.path.join(os.path.dirname(log), "conductor.pid")):
        sys.stdout.write("running\n")
    else:
        sys.stdout.write(_usage_limit(argv[0]))
    return 0


def _live(pidfile):
    try:
        with open(pidfile) as f:
            os.kill(int(f.read()), 0)
    except (OSError, ValueError):
        return False
    return True


def _usage_limit(issue):
    with open(os.path.join(".tdd", "conductor-%s.log" % issue)) as f:
        results = [r for r in map(json.loads, f.read().splitlines()) if r.get("type") == "result"]
    text = results[-1].get("result", "")
    if "limit" not in text and not _rate_limited(issue):
        return "unknown %s\n" % text
    reset = text.partition(" resets ")[2]
    return "usage-limit %s\n" % reset if reset else "usage-limit\n"


def _rate_limited(issue):
    run = os.path.join(".tdd", "wt", issue, ".tdd")
    logs = sorted((os.path.join(run, n) for n in os.listdir(run) if n.endswith(".log")), key=os.path.getmtime)
    if not logs:
        return False
    with open(logs[-1]) as f:
        return any(json.loads(line).get("error") == "rate_limit" for line in f.read().splitlines())


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
