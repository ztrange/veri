"""stop-reason.sh's report, run in-process."""
import os
import sys

import event_log
import run_end
import tunables


def main(argv):
    if len(argv) != 1:
        sys.stderr.write("usage: stop-reason.sh <issue>\n")
        return 2
    if not os.path.isdir(os.path.join(".tdd", "wt", argv[0])):
        sys.stderr.write("stop-reason.sh: no run for issue %s under .tdd/wt\n" % argv[0])
        return 2
    gap = tunables.read("VERI_SLEEP_GAP", "900")
    if not (gap.isascii() and gap.isdigit() and int(gap) >= 1):
        sys.stderr.write("stop-reason.sh: VERI_SLEEP_GAP must be a whole number >= 1, got %r\n" % gap)
        return 2
    log = os.path.join(".tdd", "wt", argv[0], ".tdd", "events.jsonl")
    if not os.path.isfile(log):
        sys.stderr.write("stop-reason.sh: no events log at %s\n" % log)
        return 2
    events = event_log.read_events(log)
    if not events:
        sys.stderr.write("stop-reason.sh: no events in %s\n" % log)
        return 2
    run_dir = os.path.join(".tdd", "wt", argv[0])
    ended, cause, mark = run_end.run_end(run_dir)
    conductor_log = run_end.conductor_log(run_dir, argv[0])
    if not ended:
        sys.stdout.write("running\n")
    elif cause == "done":
        sys.stdout.write("done %s\n" % mark.get("pr"))
    elif cause == "bailed":
        sys.stdout.write("bailed %s %s\n" % (mark.get("phase"), mark.get("classification")))
    elif cause == "stopped":
        sys.stdout.write("stopped %s\n" % mark.get("mode"))
    elif not os.path.isfile(conductor_log):
        sys.stderr.write("stop-reason.sh: no conductor log at %s\n" % conductor_log)
        return 2
    else:
        text = (run_end.latest_result(conductor_log)[1] or {}).get("result", "")
        if cause == "usage-limit":
            text = text.partition(" resets ")[2]
        sys.stdout.write("%s %s\n" % (cause, text) if text else "%s\n" % cause)
    for a, b in zip(events, events[1:]):
        if b["ts"] - a["ts"] > int(gap):
            sys.stdout.write("gap %s %s\n" % (a["ts"], b["ts"]))
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
