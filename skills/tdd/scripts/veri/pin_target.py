"""pin-target.sh, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import sys

USAGE = "usage: pin-target.sh <step-red-report> [<red-missing-report>…]"


def main(argv):
    if not argv:
        print(USAGE, file=sys.stderr)
        return 2
    import json
    from report import report_read
    text = open(argv[0], encoding="utf-8").read()
    for line in text.splitlines():
        try:
            record = json.loads(line)
        except ValueError:
            continue
        if isinstance(record, dict) and record.get("type") == "result" and isinstance(record.get("result"), str):
            text = record["result"]
    target = None
    for line in text.splitlines():
        target = report_read(line, ["TARGET_TEST"]).get("TARGET_TEST")
        if target is not None:
            break
    if target is not None:
        print(target.strip())
        return 0
    return 2


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
