"""wait-leaf.sh's wait for a detached leaf's completion file, run in-process."""
import os
import re
import subprocess
import sys

from pid_file import number_in, supervising

USAGE = "usage: wait-leaf.sh <name> [max-seconds]\n"


def recorded(exit_file):
    code = number_in(exit_file)
    if code is None:
        return None
    return int(code) if code in ("0", "1", "2", "3") else 2


def arithmetic(text):
    digits = text.removeprefix("-")
    sign = -1 if digits != text else 1
    try:
        if digits[:2] in ("0x", "0X"):
            return sign * int(digits[2:], 16)
        if digits.startswith("0"):
            return sign * int(digits, 8)
        return sign * int(digits)
    except ValueError:
        return None


def not_a_number(max_text):
    sys.stderr.write(f"wait-leaf.sh: max-seconds '{max_text}' is not a number\n")
    return 1


def clock():
    try:
        reading = subprocess.run(["date", "+%s"], stdout=subprocess.PIPE, text=True).stdout
    except FileNotFoundError:
        return None
    return int(reading) if reading.strip() else None


def main(argv):
    if not argv or argv[0] == "":
        sys.stderr.write(USAGE)
        return 2
    name = argv[0]
    max_text = argv[1] if len(argv) > 1 and argv[1] else "540"
    max_seconds = arithmetic(max_text)
    poll = os.environ.get("VERI_POLL") or "1"
    exit_file = f".tdd/{name}.exit"
    pid_file = f".tdd/{name}.pid"
    start = clock() or 0
    if max_seconds is None and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", max_text):
        return not_a_number(max_text)
    while True:
        code = recorded(exit_file)
        if code is not None:
            return code
        pid = number_in(pid_file)
        if pid is not None and not supervising(pid, name):
            code = recorded(exit_file)
            if code is not None:
                return code
            sys.stderr.write(f"wait-leaf.sh: supervisor for leaf '{name}' (pid {pid}) exited without recording a status\n")
            return 2
        now = clock()
        if max_seconds is None:
            return not_a_number(max_text)
        if now is not None and now >= start + max_seconds:
            return 3
        subprocess.run(["sleep", poll])


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
