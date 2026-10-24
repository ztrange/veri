"""worktree-setup.sh's computations, run in-process."""
import os
import subprocess
import sys

import detect_test_command as detect

MARKER = b"veri: setup:"


def main(argv):
    if len(argv) != 1:
        sys.stderr.write("usage: worktree-setup.sh <n>\n")
        return 2
    if not os.path.isfile("CLAUDE.md"):
        return 3
    try:
        detect.answer_from_file("CLAUDE.md", MARKER)
    except detect.Answer as found:
        done = f".tdd/issue-{argv[0]}-setup-done"
        if os.path.exists(done):
            return 3
        command = found.command.decode()
        code = subprocess.run(command, shell=True).returncode
        if code == 0:
            os.makedirs(".tdd", exist_ok=True)
            open(done, "w").close()
            return 0
        sys.stderr.write(f"setup failed: {command} exit {code}\n")
        return 1
    return 3


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
