"""stop-reason.sh's report, run in-process.

Its first line: running | done <pr> | bailed <phase> <classification> | stopped <mode> | refused <check> |
killed-external <leaf> | usage-limit [<reset text>] | outage [<text>] | killed [<text>] | unknown [<text>].
"""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import sys

import entry
import event_log
import run_dir
import run_end
import tunables

USAGE = "usage: stop-reason.sh <issue>\n"


def killed_external(events):
    exits = [i for i, e in enumerate(events) if e.get("event") == "exit"]
    if not exits or events[exits[-1]].get("cause") != "killed-external":
        return ""
    for e in reversed(events[:exits[-1]]):
        if e.get("event") == "launch":
            return e.get("name", "")
    return ""


def main(argv):
    if len(argv) != 1:
        sys.stderr.write(USAGE)
        return 2
    # The empty main tree keeps the spelling relative to here: ".tdd/wt/<n>", as the messages print it.
    run = run_dir.worktree("", argv[0])
    if not os.path.isdir(run):
        sys.stderr.write("stop-reason.sh: no run for issue %s under .tdd/wt\n" % argv[0])
        return 2
    gap = tunables.get("VERI_SLEEP_GAP")
    if entry.whole_number(gap) is None:
        sys.stderr.write("stop-reason.sh: VERI_SLEEP_GAP must be a whole number >= 1, got %r\n" % gap)
        return 2
    log = event_log.path(run)
    if not os.path.isfile(log):
        sys.stderr.write("stop-reason.sh: no events log at %s\n" % log)
        return 2
    events = event_log.read_events(log)
    if not events:
        sys.stderr.write("stop-reason.sh: no events in %s\n" % log)
        return 2
    ended, cause, mark = run_end.run_end(run)
    conductor_log = run_end.conductor_log(run, argv[0])
    if not ended:
        sys.stdout.write("running\n")
    elif cause == "done":
        sys.stdout.write("done %s\n" % mark.get("pr"))
    elif cause == "bailed":
        sys.stdout.write("bailed %s %s\n" % (mark.get("phase"), mark.get("classification")))
    elif cause == "stopped":
        sys.stdout.write("stopped %s\n" % mark.get("mode"))
    elif cause == "refused":
        sys.stdout.write("refused %s\n" % mark.get("check"))
    elif leaf := killed_external(events):
        sys.stdout.write("killed-external %s\n" % leaf)
    elif not os.path.isfile(conductor_log):
        sys.stderr.write("stop-reason.sh: no conductor log at %s\n" % conductor_log)
        return 2
    else:
        text = (run_end.latest_result(conductor_log)[1] or {}).get("result", "")
        if cause == "usage-limit":
            text = text.partition(" resets ")[2]
        sys.stdout.write("%s %s\n" % (cause, text) if text else "%s\n" % cause)
    timed = [e for e in events if "ts" in e]
    for a, b in zip(timed, timed[1:], strict=False):
        if b["ts"] - a["ts"] > int(gap):
            sys.stdout.write("gap %s %s\n" % (a["ts"], b["ts"]))
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
