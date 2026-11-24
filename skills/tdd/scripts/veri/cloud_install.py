"""cloud-install.sh's computations, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import json
import os
import sys

SCRIPTS = os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), ".."))

USAGE = "usage: cloud-install.sh [repo-root]"


def main(argv):
    root = argv[0] if argv else os.getcwd()
    command = '[ "$CLAUDE_CODE_REMOTE" != true ] || ' + os.path.join(SCRIPTS, "cloud-setup.sh")
    settings = os.path.join(root, ".claude", "settings.json")
    os.makedirs(os.path.dirname(settings), exist_ok=True)
    data = {"hooks": {"SessionStart": [{"hooks": [{"type": "command", "command": command}]}]}}
    with open(settings, "w") as out:
        out.write(json.dumps(data, indent=2) + "\n")
    print("added the cloud SessionStart hook to " + settings)
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
