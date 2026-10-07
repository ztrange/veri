"""extract-result.sh's record selection and passthrough, run in-process."""
import re
import sys

from leaf_log import result_records

REPORT_RE = re.compile(r"^[ \t]*(verdict|impl_path|split|test_path|suite):", re.I | re.M)


def extract(data):
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
        return data
    return result if result.endswith("\n") else result + "\n"


def main(argv):
    sys.stdout.write(extract(sys.stdin.read()))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
