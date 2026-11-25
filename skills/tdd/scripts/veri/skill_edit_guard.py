"""skill-edit-guard.sh's entry point, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import re
import subprocess
import sys

import requirements

LEDGER = re.compile(r"\.tdd/issue-\d+(-added|-pr-body)?\.md")
USAGE = "usage: skill-edit-guard.sh <unit-file> <base-sha> [<pin-file>...]"


def _git_lines(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True).stdout.split("\n")


def _git_ok(*args):
    return subprocess.run(["git", *args], capture_output=True).returncode == 0


class Refusal(Exception):
    """No answer could be had: the message is what skill-edit-guard.sh prints on stderr before exiting 2."""


def offending(unit, base, pins=()):
    """The paths changed since <base> (tracked diff, then untracked) beyond <unit>'s file (a `file#heading` unit's
    file is the part before `#`), its requirements list, <pins> and the run's ledger files. Raises Refusal when <base>
    is no commit or <unit>'s file exists nowhere."""
    if not _git_ok("rev-parse", "--verify", "--quiet", base + "^{commit}"):
        raise Refusal(f"skill-edit-guard.sh: {base} is not a commit")
    file = unit.partition("#")[0]
    at_base = _git_ok("cat-file", "-e", f"{base}:{file}")
    if not at_base and not os.path.exists(file):
        raise Refusal(f"skill-edit-guard.sh: {file} exists neither at {base} nor in the working tree")
    allowed = {file, requirements.list_path(unit), *pins}
    changed = _git_lines("diff", "--name-only", "--no-renames", base) + _git_lines("ls-files", "--others", "--exclude-standard")
    return [path for path in changed if path and path not in allowed and not LEDGER.fullmatch(path)]


def main(argv):
    if len(argv) < 2:
        print(USAGE, file=sys.stderr)
        return 2
    unit, base, *pins = argv
    try:
        others = offending(unit, base, pins)
    except Refusal as refusal:
        print(refusal, file=sys.stderr)
        return 2
    for path in others:
        print(path)
    return 1 if others else 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
