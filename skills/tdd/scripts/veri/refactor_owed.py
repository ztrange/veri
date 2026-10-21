"""refactor-owed.sh's owed-file append, render and list, run in-process."""
import os
import re
import sys
from collections import Counter

from candidates import CLASSES, candidate

USAGE = ("refactor-owed: usage: refactor-owed.sh append <file> '<STEP>' < leaf-report.txt\n"
         "                      refactor-owed.sh render <file>\n"
         "                      refactor-owed.sh list <file>")


STRUCTURAL, _, TEST_ONLY, OUT_OF_SCOPE = (candidate(cls) for cls in CLASSES)
TEST_ONLY_PREFIX = "test-only | "
OUT_OF_SCOPE_PREFIX = "out-of-scope | "
TEST_ONLY_MARK = "- " + TEST_ONLY_PREFIX
OUT_OF_SCOPE_MARK = "- " + OUT_OF_SCOPE_PREFIX
APPLIED_MARK = "applied | "
NOT_DONE_MARK = "not-done | "
SUBJECT_SEP = "\t"
NOT_DONE_REASONS = ("budget-spent", "no-predicate", "transform-rejected", "uncovered")
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


def write(file, text):
    try:
        with open(file, "a", errors="surrogateescape") as out:
            out.write(text)
    except OSError as error:
        print(f"refactor-owed.sh: {file}: {error.strerror}", file=sys.stderr)
        return 1
    return 0


def append(file, step, bounds):
    structural, test_only, out_of_scope = [], [], []
    tests_bound = all_tests(bounds)
    stream = getattr(sys.stdin, "buffer", None)
    report = stream.read().decode(errors="surrogateescape") if stream else sys.stdin.read()
    routes = ((STRUCTURAL, test_only if tests_bound else structural, TEST_ONLY_PREFIX if tests_bound else ""),
              (TEST_ONLY, test_only, TEST_ONLY_PREFIX),
              (OUT_OF_SCOPE, out_of_scope, OUT_OF_SCOPE_PREFIX))
    for line in report.split("\n"):
        for pattern, group, prefix in routes:
            if (match := pattern.match(line)) and match.group(1):
                group.append(prefix + match.group(1))
    owed = structural + test_only + out_of_scope
    return write(file, f"### {step}\n" + bullets(owed)) if owed else 0


def applied(file, transform, sha, subject=""):
    return write(file, f"{APPLIED_MARK}{sha} | {transform}{SUBJECT_SEP + subject if subject else ''}\n")


def not_done(file, candidate, reason):
    if reason not in NOT_DONE_REASONS:
        return refuse()
    return write(file, f"{NOT_DONE_MARK}{reason} | {candidate}\n")


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


def applied_records(lines):
    rows = (l[len(APPLIED_MARK):].partition(" | ") for l in lines if l.startswith(APPLIED_MARK))
    records = {}
    for sha, _, rest in rows:
        transform, _, subject = rest.partition(SUBJECT_SEP)
        records[transform] = f"{sha} {subject}" if subject else sha
    return records


def not_done_records(lines):
    return [l[len(NOT_DONE_MARK):].partition(" | ") for l in lines if l.startswith(NOT_DONE_MARK)]


def render(file):
    lines = owed_lines(file)
    kept, test_only, done = [], [], applied_records(lines)
    skipped = not_done_records(lines)
    skipped_transforms = {t for _, _, t in skipped}
    for l in lines:
        if l.startswith(NOT_DONE_MARK):
            continue
        if l.startswith(APPLIED_MARK) or (
                l.startswith("- ") and (l[2:] in done or l[2:] in skipped_transforms)):
            continue
        if l.startswith(OUT_OF_SCOPE_MARK):
            text = l[len(OUT_OF_SCOPE_MARK):]
            if text not in done and text not in skipped_transforms:
                kept.append("- " + text)
            continue
        if l.startswith(TEST_ONLY_MARK):
            test_only.append(l[len(TEST_ONLY_MARK):])
        else:
            kept.append(l)
    kept = [l for l, after in zip(kept, kept[1:] + ["### "])
            if not (l.startswith("### ") and after.startswith("### "))]
    sections = test_only or done or skipped
    if not (kept or sections or os.path.isdir(file)):
        return 0
    lead = "" if not kept and sections else "\n"
    out = "## Refactor owed\n" + lead + joined(kept)
    if test_only:
        out += ("\n### Test-only\n\n"
                "These change only files under tests/; the structural pass does not work them.\n\n"
                + bullets(test_only))
    if skipped:
        out += "\n### Not done\n\n" + bullets(f"{t} — {r}" for r, _, t in skipped)
    if done:
        out += "\n### Applied\n\n" + bullets(f"{t} — {sha}" for t, sha in done.items())
    emit(out)
    return 0


def structural_lines(file):
    if not os.path.exists(file) or os.path.getsize(file) == 0:
        return 3, []
    lines = owed_lines(file)
    done = applied_records(lines)
    skipped = {t for _, _, t in not_done_records(lines)}
    counts = Counter(l[2:].removeprefix(OUT_OF_SCOPE_PREFIX) for l in lines
                     if l.startswith("- ") and not l.startswith(TEST_ONLY_MARK)
                     and l[2:] not in done and l[2:] not in skipped
                     and l[2:].removeprefix(OUT_OF_SCOPE_PREFIX) not in done)
    listed = "\n".join(t for t, _ in counts.most_common()).rstrip("\n")
    return (0, listed.split("\n")) if listed else (3, [])


def list_owed(file):
    code, listed = structural_lines(file)
    if code == 0:
        emit(joined(listed))
    return code


def main(argv):
    verb, file, *args = (list(argv) + ["", "", "", "", ""])[:5]
    if not verb or not file:
        return refuse()
    if verb == "append":
        step, bounds = args[:2]
        return append(file, step, bounds)
    if verb == "applied":
        return applied(file, *args[:3])
    if verb == "not-done":
        return not_done(file, *args[:2])
    if verb in ("render", "list"):
        if not os.path.exists(file) or os.path.getsize(file) == 0:
            return 3
    if verb == "render":
        return render(file)
    if verb == "list":
        return list_owed(file)
    return refuse()


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
