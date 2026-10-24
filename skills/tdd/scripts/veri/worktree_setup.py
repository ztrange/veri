"""worktree-setup.sh's computations, run in-process."""
import subprocess
import sys

import detect_test_command as detect

MARKER = b"veri: setup:"


def main(argv):
    if len(argv) != 1:
        sys.stderr.write("usage: worktree-setup.sh <n>\n")
        return 2
    try:
        detect.answer_from_file("CLAUDE.md", MARKER)
    except detect.Answer as found:
        return subprocess.run(found.command.decode(), shell=True).returncode
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
