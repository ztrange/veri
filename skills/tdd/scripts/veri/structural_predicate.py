"""structural-predicate.sh's answer, read off a predicate leaf's report on stdin."""
import os
import subprocess
import sys

from report import report_read

USAGE = "usage: structural-predicate.sh <record>"
MISSING = "structural-predicate.sh: the report carries no PREDICATE: line"


def main(argv):
    if not argv or not argv[0]:
        sys.stderr.write(USAGE + "\n")
        return 2
    report = sys.stdin.buffer.read().decode("utf-8", "surrogateescape")
    fields = report_read(report, ["PREDICATE"], optional_space=True, terminated_only=True)
    if "PREDICATE" not in fields:
        sys.stderr.write(MISSING + "\n")
        return 2
    predicate = fields["PREDICATE"]
    if predicate == "NONE" or predicate.startswith(("NONE ", "NONE—", "NONE:")):
        return 3
    env = {key: value for key, value in os.environ.items() if key != "predicate"}
    try:
        status = subprocess.run(
            ["bash", "-c", predicate],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            env=env,
        ).returncode
    except (FileNotFoundError, PermissionError):
        status = 127
    if status == 0:
        return 1
    try:
        with open(argv[0], "wb") as record:
            record.write(predicate.encode("utf-8", "surrogateescape") + b"\n")
    except OSError as error:
        sys.stderr.write("structural-predicate.sh: %s: %s\n" % (argv[0], error.strerror))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
