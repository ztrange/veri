"""build-adjudicate-prompt.sh's prompt builder, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import re
import sys

USAGE = "usage: build-adjudicate-prompt.sh <n> <cause> <exit-code> <stderr-file> <command…>"


def main(argv):
    if not argv:
        print(USAGE, file=sys.stderr)
        return 2
    n, cause, exit_code, stderr_file, *command = argv
    doc = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "ADJUDICATE.md")
    with open(doc) as f:
        eligible = dict(re.findall(r"^- `([^`]+)`:(.*)$", f.read(), re.M))
    if cause not in eligible:
        print(f"build-adjudicate-prompt.sh: cause not eligible: {cause}", file=sys.stderr)
        return 2
    routes = ", ".join(re.findall(r"`([^`]+)`", eligible[cause])) or eligible[cause].strip()
    with open(f".tdd/issue-{n}.md") as f:
        steps = [line.rstrip("\n") for line in f if line.startswith(("- [ ]", "- [x]"))]
    step = next((s for s in steps if s.startswith("- [ ]")), steps[-1])
    with open(stderr_file) as f:
        stderr = "".join(f.readlines()[-50:])
    print(
        f"Cause: {cause}\nCommand: {' '.join(command)}\nExit code: {exit_code}\nRoutes: {routes}\n"
        f"Stderr:\n{stderr}\nStep: {step}\n\n"
        "End with one final line: ADJUDICATION: retry|bail|route <token> — <reason>"
    )
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
