"""transform-touches-tests.sh's range check, run in-process."""
import re
import subprocess
import sys

USAGE = "usage: transform-touches-tests.sh <base-sha>"
TEST_FILE = re.compile(rb"(^|/)tests/|\.test\.")


def refuse(message=None):
    if message:
        print(message, file=sys.stderr)
    print(USAGE, file=sys.stderr)
    return 2


def main(argv):
    base = argv[0] if argv else ""
    if not base:
        return refuse()
    check = subprocess.run(["git", "rev-parse", "--verify", "--quiet", f"{base}^{{commit}}"],
                           stdout=subprocess.DEVNULL)
    if check.returncode != 0:
        return refuse(f"transform-touches-tests.sh: base-sha does not resolve to a commit: {base}")
    log = subprocess.run(["git", "log", "--format=", "--name-only", f"{base}..HEAD"],
                         stdout=subprocess.PIPE)
    if log.returncode != 0:
        return 2
    matched = b"".join(line + b"\n" for line in log.stdout.split(b"\n") if TEST_FILE.search(line))
    touched = subprocess.run(["sort", "-u"], input=matched, stdout=subprocess.PIPE).stdout.rstrip(b"\n")
    if not touched:
        return 0
    touched = touched.decode()
    print(f"transform changed a test file: {touched}")
    return 1


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
