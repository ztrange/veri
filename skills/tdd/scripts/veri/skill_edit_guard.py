"""skill-edit-guard.sh's entry point, run in-process."""
import os
import re
import subprocess
import sys

LEDGER = re.compile(r"\.tdd/issue-\d+(-added)?\.md")
USAGE = "usage: skill-edit-guard.sh <unit-file> <base-sha> [<pin-file>...]"


def _git_lines(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True).stdout.split("\n")


def _git_ok(*args):
    return subprocess.run(["git", *args], capture_output=True).returncode == 0


def list_path(unit):
    return os.path.join(os.path.dirname(unit), "REQUIREMENTS.md")


def main(argv):
    if len(argv) < 2:
        print(USAGE, file=sys.stderr)
        return 2
    unit, base, *pins = argv
    if not _git_ok("rev-parse", "--verify", "--quiet", base + "^{commit}"):
        print(f"skill-edit-guard.sh: {base} is not a commit", file=sys.stderr)
        return 2
    at_base = _git_ok("cat-file", "-e", f"{base}:{unit}")
    if not at_base and not os.path.exists(unit):
        print(f"skill-edit-guard.sh: {unit} exists neither at {base} nor in the working tree", file=sys.stderr)
        return 2
    allowed = {unit, list_path(unit), *pins}
    changed = _git_lines("diff", "--name-only", "--no-renames", base) + _git_lines("ls-files", "--others", "--exclude-standard")
    others = [path for path in changed if path and path not in allowed and not LEDGER.fullmatch(path)]
    for path in others:
        print(path)
    return 1 if others else 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
