"""refactor-owed.sh's owed-file append, render and list, run in-process."""
import os
import re
import sys

USAGE = ("refactor-owed: usage: refactor-owed.sh append <file> '<STEP>' < leaf-report.txt\n"
         "                      refactor-owed.sh render <file>\n"
         "                      refactor-owed.sh list <file>")


def candidate(cls):
    return re.compile(rf"^CANDIDATES:[ \t\n\r\f\v]*{cls}[ \t\n\r\f\v]*[|][ \t\n\r\f\v]*(.*)$")


STRUCTURAL = candidate("structural")
TEST_ONLY = candidate("test-only")
TEST_ONLY_MARK = "- test-only | "
TEST_FILE = re.compile(r"(^|/)tests/|\.test\.")


def all_tests(bounds):
    line = bounds.split("\n")[0]
    files = line.split(",")
    if files and files[-1] == "":
        files.pop()
    return bool(bounds) and all(TEST_FILE.search(f) for f in files)


def joined(lines):
    return "".join(f"{l}\n" for l in lines)


def bullets(transforms):
    return joined(f"- {t}" for t in transforms)


def refuse():
    print(USAGE, file=sys.stderr)
    return 2


def append(file, step, bounds):
    structural, test_only = [], []
    tests_bound = all_tests(bounds)
    stream = getattr(sys.stdin, "buffer", None)
    report = stream.read().decode(errors="surrogateescape") if stream else sys.stdin.read()
    for line in report.split("\n"):
        match = STRUCTURAL.match(line)
        if match and not tests_bound:
            structural.append(match.group(1))
        elif match or (match := TEST_ONLY.match(line)):
            test_only.append("test-only | " + match.group(1))
    owed = structural + test_only
    if owed:
        with open(file, "a", errors="surrogateescape") as out:
            out.write(f"### {step}\n" + bullets(owed))
    return 0


def emit(text):
    sys.stdout.buffer.write(text.encode(errors="surrogateescape"))


def owed_lines(file):
    lines = []
    if not os.path.isdir(file):
        with open(file, errors="surrogateescape") as owed:
            lines = owed.read().split("\n")
        if lines[-1] == "":
            lines.pop()
    return lines


def render(file):
    lines = owed_lines(file)
    kept, test_only = [], []
    for l in lines:
        if l.startswith(TEST_ONLY_MARK):
            test_only.append(l[len(TEST_ONLY_MARK):])
        else:
            kept.append(l)
    out = "## Refactor owed\n\n" + joined(kept)
    if test_only:
        out += ("\n### Test-only\n\n"
                "These change only files under tests/; the structural pass does not work them.\n\n"
                + bullets(test_only))
    emit(out)
    return 0


def list_owed(file):
    counts = {}
    for l in owed_lines(file):
        if l.startswith("- ") and not l.startswith(TEST_ONLY_MARK):
            counts[l[2:]] = counts.get(l[2:], 0) + 1
    listed = "\n".join(sorted(counts, key=counts.get, reverse=True)).rstrip("\n")
    if not listed:
        return 3
    emit(listed + "\n")
    return 0


def main(argv):
    verb, file, step, bounds = (list(argv) + ["", "", "", ""])[:4]
    if not verb or not file:
        return refuse()
    if verb == "append":
        return append(file, step, bounds)
    if verb in ("render", "list"):
        if not os.path.exists(file) or os.path.getsize(file) == 0:
            return 3
    if verb == "render":
        return render(file)
    if verb == "list":
        return list_owed(file)
    return refuse()
