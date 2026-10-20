"""skill-edit-guard.sh's entry point, run in-process."""
import os
import subprocess
import sys

USAGE = "usage: skill-edit-guard.sh <unit-file> <base-sha>"


def _git_lines(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True).stdout.split("\n")


def main(argv):
    if len(argv) != 2:
        print(USAGE, file=sys.stderr)
        return 2
    unit, base = argv
    allowed = {unit, os.path.join(os.path.dirname(unit), "REQUIREMENTS.md")}
    changed = _git_lines("diff", "--name-only", base) + _git_lines("ls-files", "--others", "--exclude-standard")
    others = [path for path in changed if path and path not in allowed]
    for path in others:
        print(path)
    return 1 if others else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
