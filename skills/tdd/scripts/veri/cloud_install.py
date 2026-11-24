"""cloud-install.sh's computations, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import json
import os
import sys

import entry

SCRIPTS = os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), ".."))

USAGE = "usage: cloud-install.sh [repo-root]"


def main(argv):
    root = argv[0] if argv else os.getcwd()
    command = '[ "$CLAUDE_CODE_REMOTE" != true ] || ' + os.path.join(SCRIPTS, "cloud-setup.sh")
    settings = os.path.join(root, ".claude", "settings.json")
    data = {}
    if os.path.exists(settings):
        with open(settings) as text:
            try:
                data = json.load(text)
            except json.JSONDecodeError as exc:
                return entry.refuse("cloud-install: " + settings + ": not valid JSON: " + str(exc))
    groups = data.setdefault("hooks", {}).setdefault("SessionStart", [])
    if any(hook.get("command") == command for group in groups for hook in group.get("hooks", [])):
        print("already present in " + settings)
        return 0
    groups.append({"hooks": [{"type": "command", "command": command}]})
    os.makedirs(os.path.dirname(settings), exist_ok=True)
    with open(settings, "w") as out:
        out.write(json.dumps(data, indent=2) + "\n")
    print("added the cloud SessionStart hook to " + settings)
    return 0


if __name__ == "__main__":
    entry.run(main, sys.argv[1:])
