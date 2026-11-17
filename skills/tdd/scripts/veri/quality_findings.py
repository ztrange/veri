"""test-quality.sh's record verb, run in-process: the develop-test-quality leaf's FINDING: lines, checked and recorded.

Named quality_findings, not test_quality: a module named test_*.py would read as a test file (case_reader.is_test_path).
"""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import sys

import entry
from case_reader import file_defines, strip_param_suffix
from report import report_values

USAGE = "usage: test-quality.sh record <n> < <leaf-report>"
KINDS = ("weak-assertion", "redundant", "implementation-coupled")


def refusal(value):
    """Why the FINDING: value cannot be recorded, or None when it names a kind, a case its file defines and a why."""
    fields = [field.strip() for field in value.split("|", 2)]
    if len(fields) < 3 or "::" not in fields[1] or not fields[2]:
        return f"names no <file>::<case> with a kind and a why: {value}"
    if fields[0] not in KINDS:
        return f"kind '{fields[0]}' is not one of {', '.join(KINDS)}: {value}"
    path, *classes, case = fields[1].split("::")
    if not (os.path.isfile(path) and file_defines(path, strip_param_suffix(case), tuple(classes))):
        return f"{path} does not define {fields[1]}"
    return None


def record(issue, report):
    values = report_values(report, "FINDING", strip=True)
    if not values:
        return 2, "the report has no FINDING: line"
    if values == ["none"]:
        return 3, ""
    for value in values:
        refused = refusal(value)
        if refused:
            return 2, refused
    return 0, "".join(" | ".join(field.strip() for field in value.split("|", 2)) + "\n" for value in values)


def main(argv):
    if len(argv) != 2 or argv[0] != "record" or entry.whole_number(argv[1], 1) is None:
        print(USAGE, file=sys.stderr)
        return 2
    code, text = record(argv[1], sys.stdin.read())
    if code == 2:
        print(f"test-quality.sh: nothing recorded: {text}", file=sys.stderr)
        return 2
    path = os.path.join(".tdd", f"issue-{argv[1]}-test-quality.md")
    partial = path + ".partial"
    with open(partial, "w", encoding="utf-8") as out:
        out.write(text)
    os.replace(partial, path)
    return code


if __name__ == "__main__":
    entry.run(main, sys.argv[1:])
