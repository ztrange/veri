"""refactor-owed.sh's owed-file append, render and list, run in-process."""
import os
import re
import sys
from collections import Counter

USAGE = ("refactor-owed: usage: refactor-owed.sh append <file> '<STEP>' < leaf-report.txt\n"
         "                      refactor-owed.sh render <file>\n"
         "                      refactor-owed.sh list <file>")


def candidate(cls):
    return re.compile(rf"^CANDIDATES:[ \t\n\r\f\v]*{cls}[ \t\n\r\f\v]*[|][ \t\n\r\f\v]*(.*)$")


STRUCTURAL = candidate("structural")
TEST_ONLY = candidate("test-only")
OUT_OF_SCOPE = candidate("out-of-scope")
TEST_ONLY_PREFIX = "test-only | "
OUT_OF_SCOPE_PREFIX = "out-of-scope | "
TEST_ONLY_MARK = "- " + TEST_ONLY_PREFIX
OUT_OF_SCOPE_MARK = "- " + OUT_OF_SCOPE_PREFIX
APPLIED_MARK = "applied | "
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
            if match := pattern.match(line):
                group.append(prefix + match.group(1))
    owed = structural + test_only + out_of_scope
    return write(file, f"### {step}\n" + bullets(owed)) if owed else 0


def applied(file, transform, sha):
    return write(file, f"{APPLIED_MARK}{sha} | {transform}\n")


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


def out_of_scope_transforms(file):
    if not os.path.isfile(file):
        return []
    return [l[len(OUT_OF_SCOPE_MARK):] for l in owed_lines(file) if l.startswith(OUT_OF_SCOPE_MARK)]


def render(file):
    lines = owed_lines(file)
    kept, test_only, done = [], [], {}
    for l in lines:
        if l.startswith(APPLIED_MARK):
            sha, _, transform = l[len(APPLIED_MARK):].partition(" | ")
            done[transform] = sha
    for l in lines:
        if l.startswith((APPLIED_MARK, OUT_OF_SCOPE_MARK)) or (l.startswith("- ") and l[2:] in done):
            continue
        if l.startswith(TEST_ONLY_MARK):
            test_only.append(l[len(TEST_ONLY_MARK):])
        else:
            kept.append(l)
    out_of_scope = [t for t in out_of_scope_transforms(file) if OUT_OF_SCOPE_PREFIX + t not in done]
    kept = [l for l, after in zip(kept, kept[1:] + ["### "])
            if not (l.startswith("### ") and after.startswith("### "))]
    out ="## Refactor owed\n\n" + joined(kept)
    if test_only:
        out += ("\n### Test-only\n\n"
                "These change only files under tests/; the structural pass does not work them.\n\n"
                + bullets(test_only))
    if out_of_scope:
        out += "\n### Out-of-scope\n\n" + bullets(out_of_scope)
    if done:
        out += "\n### Applied\n\n" + bullets(f"{t} — {sha}" for t, sha in done.items())
    emit(out)
    return 0


def list_owed(file):
    counts = Counter(l[2:] for l in owed_lines(file)
                     if l.startswith("- ") and not l.startswith((TEST_ONLY_MARK, OUT_OF_SCOPE_MARK)))
    listed = "\n".join(t for t, _ in counts.most_common()).rstrip("\n")
    if not listed:
        return 3
    emit(listed + "\n")
    return 0


def main(argv):
    verb, file, *args = (list(argv) + ["", "", "", ""])[:4]
    if not verb or not file:
        return refuse()
    if verb == "append":
        step, bounds = args
        return append(file, step, bounds)
    if verb == "applied":
        transform, sha = args
        return applied(file, transform, sha)
    if verb in ("render", "list"):
        if not os.path.exists(file) or os.path.getsize(file) == 0:
            return 3
    if verb == "render":
        return render(file)
    if verb == "list":
        return list_owed(file)
    return refuse()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
