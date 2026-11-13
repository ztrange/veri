"""role-growth.sh's logic, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import glob
import json
import os
import sys

from full_tier_time import main_tree
import growth
import role_state

KNOBS = {"coord": "VERI_RESET_GROWTH_COORD"}
USAGE = "usage: role-growth.sh <coord|dev> [--lane <lane>]\n"


def _records(transcript):
    with open(transcript) as f:
        return [json.loads(l) for l in f if l.strip()]


def main(argv):
    lane = None
    if len(argv) == 3 and argv[1] == "--lane":
        lane = argv[2]
        argv = argv[:1]
    if len(argv) != 1 or argv[0] not in ("coord", "dev"):
        sys.stderr.write(USAGE)
        return 2
    session = os.environ["CLAUDE_CODE_SESSION_ID"]
    pattern = os.path.join(os.path.expanduser("~"), ".claude", "projects", "*", session + ".jsonl")
    found = glob.glob(pattern)
    if not found:
        sys.stderr.write("no transcript %s\n" % pattern)
        return 2
    transcript = found[0]
    path = role_state.state_path(main_tree(os.getcwd()), argv[0], lane)
    text = "session=%s\ntranscript=%s\n" % (session, transcript)
    fields = dict(l.split("=", 1) for l in (role_state.read(path) or "").splitlines() if "=" in l)
    recovered = fields.get("recovered-at")
    if "baseline-at" not in fields or (recovered and recovered > fields["baseline-at"]):
        context = growth.growth(_records(transcript), 0)
        if context is not None:
            text += "baseline=%d\nbaseline-at=%s\n" % (context, role_state.now())
    else:
        knob = int(os.environ.get(KNOBS.get(argv[0], ""), 70000))
        grown = growth.growth(_records(transcript), int(fields["baseline"]))
        if grown is not None and grown >= 2 * knob:
            print("context grew %d against the knob %d: reset now, even mid-task" % (grown, knob))
        elif grown is not None and grown >= 0.85 * knob:
            print("context grew %d against the knob %d: reset at the next quiet point" % (grown, knob))
    role_state.append(path, text)
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
