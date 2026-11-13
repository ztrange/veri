"""role-growth.sh's logic, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import glob
import json
import os
import sys

from full_tier_time import main_tree
import growth
import role_state
import tunables

KNOBS = {"coord": "VERI_RESET_GROWTH_COORD", "dev": "VERI_RESET_GROWTH_DEV"}
USAGE = "usage: role-growth.sh <coord|dev> [--lane <lane>]\n"


class Failure(Exception):
    pass


def _records(transcript):
    try:
        with open(transcript) as f:
            return [json.loads(l) for l in f if l.strip()]
    except json.JSONDecodeError:
        raise Failure("unreadable transcript %s\n" % transcript)


def _baseline(transcript):
    context = growth.growth(_records(transcript), 0)
    if context is None:
        return ""
    return "baseline=%d\nbaseline-at=%s\n" % (context, role_state.now())


def _growth_line(path, lines, fields, transcript, knob):
    grown = growth.growth(_records(transcript), int(fields["baseline"]))
    if grown is None or grown < 0.85 * knob:
        return ""
    reason = role_state.refusal(path, lines, role_state.now())
    if not reason:
        advice = "reset now, even mid-task" if grown >= 2 * knob else "reset at the next quiet point"
        print("context grew %d against the knob %d: %s" % (grown, knob, advice))
        return ""
    if fields.get("refused-at"):
        return ""
    print("%s: report it to the operator, do not retry" % reason)
    return "refused-at=%s\n" % role_state.now()


def main(argv):
    try:
        return _main(argv)
    except Failure as e:
        sys.stderr.write(str(e))
        return 2


def _main(argv):
    lane = None
    if len(argv) == 3 and argv[1] == "--lane":
        lane = argv[2]
        argv = argv[:1]
    if len(argv) != 1 or argv[0] not in KNOBS:
        raise Failure(USAGE)
    raw = tunables.read(KNOBS[argv[0]], "70000")
    if not raw.isdigit() or int(raw) < 1:
        raise Failure("%s must be a whole number of at least 1, got %r\n" % (KNOBS[argv[0]], raw))
    session = os.environ["CLAUDE_CODE_SESSION_ID"]
    pattern = os.path.join(os.path.expanduser("~"), ".claude", "projects", "*", session + ".jsonl")
    found = glob.glob(pattern)
    if not found:
        raise Failure("no transcript %s\n" % pattern)
    transcript = found[0]
    path = role_state.state_path(main_tree(os.getcwd()), argv[0], lane)
    text = "session=%s\ntranscript=%s\n" % (session, transcript)
    lines = (role_state.read(path) or "").splitlines()
    if any("=" not in l and not l.startswith(("decision ", "dropped-decision ", "message ", "override ", "timed-n ")) for l in lines):
        raise Failure("malformed state file %s\n" % path)
    fields = dict(l.split("=", 1) for l in lines if "=" in l)
    recovered = fields.get("recovered-at")
    if "baseline-at" not in fields or (recovered and recovered > fields["baseline-at"]):
        text += _baseline(transcript)
    else:
        text += _growth_line(path, lines, fields, transcript, int(raw))
    role_state.append(path, text)
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
