"""extract-result.sh's record selection and passthrough, run in-process."""
import re
import sys

from leaf_log import result_records

REPORT_RE = re.compile(r"^[ \t]*(verdict|impl_path|split|test_path|suite):", re.I | re.M)


def main(argv):
    data = sys.stdin.read()
    result = None
    report = None
    for obj in result_records(data.splitlines()):
        if "result" in obj:
            result = obj["result"]
            if isinstance(result, str) and REPORT_RE.search(result):
                report = result
    if report is not None:
        result = report
    if result is None:
        sys.stdout.write(data)
    else:
        sys.stdout.write(result if result.endswith("\n") else result + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
