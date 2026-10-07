"""detach-command.sh's start and wait, run in-process."""
import os
import sys

import detach

USAGE = "usage: detach-command.sh start <name> <cmd> [args…] | wait <name> [max-seconds]"


def _recorded(exit_file):
    if not os.path.isfile(exit_file):
        return None
    with open(exit_file) as handle:
        print(handle.read().rstrip("\n"))
    return 1


def _alive(pid_file):
    try:
        with open(pid_file) as handle:
            os.kill(int(handle.read()), 0)
    except OSError:
        return False
    return True


def _wait(exit_file, pid_file):
    code = _recorded(exit_file)
    if code is not None:
        return code
    if not _alive(pid_file):
        return 2
    return 3


def main(argv):
    if len(argv) < 2 or argv[0] not in ("start", "wait") or (argv[0] == "start" and len(argv) < 3):
        print(USAGE, file=sys.stderr)
        return 2
    mode, name, rest = argv[0], argv[1], argv[2:]
    exit_file, pid_file = f".tdd/{name}.exit", f".tdd/{name}.pid"
    if mode == "wait":
        return _wait(exit_file, pid_file)
    pid = detach.start(rest, None, None, None)
    with open(pid_file, "w") as handle:
        handle.write(f"{pid}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
