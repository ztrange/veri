"""role-growth.sh's logic, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import glob
import json
import os
import sys

from full_tier_time import main_tree
import growth
import role_state

USAGE = "usage: role-growth.sh <coord|dev> [--lane <lane>]\n"


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
        with open(transcript) as f:
            records = [json.loads(l) for l in f if l.strip()]
        context = growth.growth(records, 0)
        if context is not None:
            text += "baseline=%d\nbaseline-at=%s\n" % (context, role_state.now())
    role_state.append(path, text)
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
