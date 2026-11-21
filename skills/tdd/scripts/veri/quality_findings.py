"""test-quality.sh, run in-process: the test files a run's range touched (files), and the develop-test-quality leaf's
FINDING: lines, checked and recorded (record).

Named quality_findings, not test_quality: a module named test_*.py would read as a test file (case_reader.is_test_path).
"""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import sys

import entry
from case_reader import file_defines, is_test_path, strip_param_suffix
from git import GitFailed, out
from ledger import CRITERION_TAG, ledger_steps, multi_tag_refusal, read_ledger, trailing_markers
from report import report_values

USAGE = "usage: test-quality.sh files <branch-base> | anchor <ledger> | record <n> < <leaf-report>"
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
    """(code, text, skipped): the record's text from the findings refusal() accepts, and the refusals of the others,
    so one finding naming a helper does not drop the report (#4534); exit 2 when none survives."""
    values = report_values(report, "FINDING", strip=True)
    if not values:
        return 2, "the report has no FINDING: line", []
    if values == ["none"]:
        return 3, "", []
    judged = [(value, refusal(value)) for value in values]
    skipped = [refused for _, refused in judged if refused]
    kept = [value for value, refused in judged if not refused]
    if not kept:
        return 2, "; ".join(skipped), []
    return 0, "".join(" | ".join(field.strip() for field in value.split("|", 2)) + "\n" for value in kept), skipped


def files(base):
    """The test files `git diff --name-only <base>..HEAD` names that still exist, one per line; exit 3 for none."""
    try:
        named = out("diff", "--name-only", f"{base}..HEAD").splitlines()
    except GitFailed as failed:
        print(f"test-quality.sh: {failed}", file=sys.stderr)
        return 2
    found = [path for path in named if is_test_path(path) and os.path.isfile(path)]
    sys.stdout.write("".join(path + "\n" for path in found))
    return 0 if found else 3


def anchor(path):
    """The last done step add-ledger-step.sh can anchor a fix step on: one criterion tag, in a ledger it does not refuse
    (no step carries two). Exit 3 when there is none, so the findings stay unfixed with no bail."""
    try:
        records = ledger_steps(read_ledger(path))
    except OSError as error:
        print(f"test-quality.sh: {path}: {error.strerror}", file=sys.stderr)
        return 2
    refusal = multi_tag_refusal(records)
    if refusal:
        print(f"test-quality.sh: no anchor: {refusal}", file=sys.stderr)
        return 3
    done = [r.text for r in records if r.state == "done" and trailing_markers(r.text).count(CRITERION_TAG) == 1]
    if not done:
        print("test-quality.sh: no anchor: no done step carries one criterion tag", file=sys.stderr)
        return 3
    print(done[-1])
    return 0


def main(argv):
    if len(argv) == 2 and argv[0] == "anchor" and argv[1]:
        return anchor(argv[1])
    if len(argv) == 2 and argv[0] == "files" and argv[1]:
        return files(argv[1])
    if len(argv) != 2 or argv[0] != "record" or entry.whole_number(argv[1], 1) is None:
        print(USAGE, file=sys.stderr)
        return 2
    code, text, skipped = record(argv[1], sys.stdin.read())
    for refused in skipped:
        print(f"test-quality.sh: finding skipped: {refused}", file=sys.stderr)
    if code == 2:
        print(f"test-quality.sh: nothing recorded: {text}", file=sys.stderr)
        return 2
    path = os.path.join(".tdd", f"issue-{argv[1]}-test-quality")  # no .md: `!.tdd/issue-*.md` would re-admit it
    partial = path + ".partial"
    with open(partial, "w", encoding="utf-8") as out:
        out.write(text)
    os.replace(partial, path)
    return code


if __name__ == "__main__":
    entry.run(main, sys.argv[1:])
