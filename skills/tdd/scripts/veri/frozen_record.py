"""The check-earlier pass marker: its path, its writing and removal."""
import hashlib
import os
import subprocess
import sys
import tempfile

from entry import write


def step_key(step):
    return hashlib.sha256(os.fsencode(step)).hexdigest()[:16]


def record_path(step):
    return ".tdd/tests-frozen-%s.record" % step_key(step)


def recorded_cases(step):
    try:
        with open(record_path(step), encoding="utf-8", errors="replace") as handle:
            return {line[6:].strip() for line in handle.read().splitlines() if line.startswith("case: ")}
    except OSError:
        return set()


def body_digest(body):
    return hashlib.sha256(body.encode()).hexdigest()


def body_line(name, case, body):
    return "body: %s\t%s\t%s" % (name, case, body_digest(body))


def helpers_line(name, case, digest):
    return "helpers: %s\t%s\t%s" % (name, case, digest)


def format_line():
    return "format: 2\n"


def case_lines(name, case, body):
    return ["case: %s\n" % case, body_line(name, case, body) + "\n"]


def is_marked(records):
    return "format: 2" in records


def digest_entry(line):
    if not line.strip() or line.startswith(("case: ", "body: ", "helpers: ", "format: ")):
        return None
    return line.rstrip("\n").split("  ", 1)


def body_record(line):
    return line[6:].split("\t") if line.startswith("body: ") else None


def write_record(path, out, opener=open):
    try:
        with opener(path, "w", encoding="utf-8") as handle:
            handle.writelines(out)
    except OSError as error:
        write(sys.stderr, "tests-frozen.sh: the record %s could not be written: %s" % (path, error))
        return False
    return True


def helper_records(records):
    for record in records:
        if record.startswith("helpers: "):
            name, case, digest = record[9:].split("\t")
            yield (name, case), digest


def rewrite_records(earlier, rewrite, opener=open):
    for owner, path, records in earlier:
        out = []
        replaced = False
        for record in records:
            parsed = body_record(record)
            if parsed:
                record = rewrite(owner, record, *parsed)
                if record is None:
                    if out and out[-1].startswith("case: "):
                        out.pop()
                    replaced = True
                    continue
                replaced = "\nhelpers: " in record
            elif replaced and record.startswith("helpers: "):
                continue
            else:
                replaced = False
            out.append(record + "\n")
        if not write_record(path, out, opener):
            return False
    return True


def pass_marker_path(step):
    return ".tdd/check-earlier-%s.pass" % step_key(step)


def work_tree_hash():
    # An ignored .tdd/ is already left out by `add -A`, and naming it in an exclude
    # pathspec makes git refuse ("paths are ignored"), so the exclude is passed only
    # when .tdd is not ignored as a whole (#2230).
    ignored = subprocess.run(["git", "check-ignore", "-q", ".tdd"], stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL).returncode == 0
    with tempfile.TemporaryDirectory() as scratch:
        env = dict(os.environ, GIT_INDEX_FILE=os.path.join(scratch, "index"))
        added = subprocess.run(["git", "add", "-A", "--", "."] + ([] if ignored else [":(exclude).tdd"]), env=env,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        done = subprocess.run(["git", "write-tree"], env=env, stdout=subprocess.PIPE,
                              stderr=subprocess.DEVNULL)
    if added.returncode != 0 or done.returncode != 0:
        return ""
    return os.fsdecode(done.stdout).strip()


def write_pass_marker(step, tree):
    done = subprocess.run(["git", "rev-parse", "HEAD"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    if done.returncode != 0:
        return
    os.makedirs(".tdd", exist_ok=True)
    with open(pass_marker_path(step), "w", encoding="utf-8") as handle:
        handle.write("step: %s\nhead: %s\ntree: %s\n" % (step, os.fsdecode(done.stdout).strip(), tree))


def remove_pass_marker(step):
    try:
        os.remove(pass_marker_path(step))
    except OSError:
        pass


def pass_marker_current(text):
    try:
        with open(pass_marker_path(text), encoding="utf-8") as handle:
            lines = handle.read().splitlines()
    except OSError:
        return False
    done = subprocess.run(["git", "rev-parse", "HEAD"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    head = done.stdout.rstrip("\n") if done.returncode == 0 else None
    return (head is not None and f"step: {text}" in lines and f"head: {head}" in lines
            and f"tree: {work_tree_hash()}" in lines)
