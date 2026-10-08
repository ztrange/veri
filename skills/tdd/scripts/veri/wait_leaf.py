"""wait-leaf.sh's wait for a detached leaf's completion file, run in-process."""
import subprocess
import sys

from pid_file import number_in

USAGE = "usage: wait-leaf.sh <name> [max-seconds]\n"


def to_contract(code):
    return int(code) if code in ("0", "1", "2", "3") else 2


def clock():
    return int(subprocess.run(["date", "+%s"], stdout=subprocess.PIPE, text=True).stdout)


def main(argv):
    if not argv or argv[0] == "":
        sys.stderr.write(USAGE)
        return 2
    name = argv[0]
    max_seconds = int(argv[1]) if len(argv) > 1 and argv[1] else 540
    exit_file = f".tdd/{name}.exit"
    deadline = clock() + max_seconds
    while True:
        code = number_in(exit_file)
        if code is not None:
            return to_contract(code)
        if clock() >= deadline:
            return 3


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
