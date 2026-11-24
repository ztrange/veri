"""parse-adjudication.sh's answer reader, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import re
import sys

from report import report_values

USAGE = "usage: parse-adjudication.sh <leaf-output>"


def section(title):
    """The text of ADJUDICATE.md's `### <title>` section, up to the next `###` heading; "" when it has none."""
    with open(os.path.join(os.path.dirname(__file__), "..", "..", "ADJUDICATE.md")) as f:
        doc = f.read()
    match = re.search(r"^### " + re.escape(title) + r"\n(.*?)(?=^### |\Z)", doc, re.M | re.S)
    return match.group(1) if match else ""


def waivable_rule(cause):
    """The rule id ADJUDICATE.md's *Waivable rules* names for bail cause `cause`, or None when it names none."""
    for rule, named in re.findall(r"^- `([^`]+)`: `([^`]+)`", section("Waivable rules"), re.M):
        if named == cause:
            return rule
    return None


def parse(path, cause=None):
    """Read the leaf output file at `path`; answer `(outcome, reason)` of its last ADJUDICATION: line.

    Answers None when no answer exists: the file is missing, holds no such line, or the
    outcome is neither `retry`, `bail`, `deviate` nor `route <listed route>`, a route being listed
    when ADJUDICATE.md's *Eligible causes* lists it for `cause` (for any cause when `cause` is None).
    `deviate` is read for any cause; whether the cause may deviate is `waivable_rule`'s answer,
    which `adjudicate.sh record` asks. Prints nothing.
    """
    try:
        with open(path) as f:
            answer = report_values(f.read(), "ADJUDICATION", occurrence="last", space="kept", splitlines=True)
    except FileNotFoundError:
        return None
    if answer is None:
        return None
    outcome, _, reason = answer.strip().partition(" — ")
    kind, _, token = outcome.partition(" ")
    eligible = [t for c, t in re.findall(r"^- `([^`]+)`:(.*)$", section("Eligible causes"), re.M) if cause in (None, c)]
    listed_route = kind == "route" and any(token in re.findall(r"`([^`]+)`", t) for t in eligible)
    if not listed_route and outcome not in ("retry", "bail", "deviate"):
        return None
    return outcome, reason


def main(argv):
    if not argv:
        print(USAGE, file=sys.stderr)
        return 2
    parsed = parse(argv[0])
    if parsed is None:
        return 2
    print(parsed[0])
    print(parsed[1])
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
