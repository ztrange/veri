"""The check-earlier pass marker: its path, its writing and removal."""
import hashlib
import os
import subprocess
import sys
import tempfile

from entry import write


def _step_key(step):
    return hashlib.sha256(os.fsencode(step)).hexdigest()[:16]


def _record_path(step):
    return ".tdd/tests-frozen-%s.record" % _step_key(step)


def recorded_cases(step):
    try:
        with open(_record_path(step), encoding="utf-8", errors="replace") as handle:
            return {l[6:].strip() for l in handle.read().splitlines() if l.startswith("case: ")}
    except OSError:
        return set()


def _body_digest(body):
    return hashlib.sha256(body.encode()).hexdigest()


def _body_line(name, case, body):
    return "body: %s\t%s\t%s" % (name, case, _body_digest(body))


def _body_record(line):
    return line[6:].split("\t") if line.startswith("body: ") else None


def _write_record(path, out, opener=open):
    try:
        with opener(path, "w", encoding="utf-8") as handle:
            handle.writelines(out)
    except OSError as error:
        write(sys.stderr, "tests-frozen.sh: the record %s could not be written: %s" % (path, error))
        return False
    return True


def _helper_records(records):
    for record in records:
        if record.startswith("helpers: "):
            name, case, digest = record[9:].split("\t")
            yield (name, case), digest


def _rewrite_records(earlier, rewrite, opener=open):
    for owner, path, records in earlier:
        out = []
        replaced = False
        for record in records:
            parsed = _body_record(record)
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
        if not _write_record(path, out, opener):
            return False
    return True


def _pass_marker_path(step):
    return ".tdd/check-earlier-%s.pass" % _step_key(step)


def _work_tree_hash():
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


def _write_pass_marker(step, tree):
    done = subprocess.run(["git", "rev-parse", "HEAD"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    if done.returncode != 0:
        return
    os.makedirs(".tdd", exist_ok=True)
    with open(_pass_marker_path(step), "w", encoding="utf-8") as handle:
        handle.write("step: %s\nhead: %s\ntree: %s\n" % (step, os.fsdecode(done.stdout).strip(), tree))


def _remove_pass_marker(step):
    try:
        os.remove(_pass_marker_path(step))
    except OSError:
        pass


def pass_marker_current(text):
    try:
        with open(_pass_marker_path(text), encoding="utf-8") as handle:
            lines = handle.read().splitlines()
    except OSError:
        return False
    done = subprocess.run(["git", "rev-parse", "HEAD"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    head = done.stdout.rstrip("\n") if done.returncode == 0 else None
    return (head is not None and f"step: {text}" in lines and f"head: {head}" in lines
            and f"tree: {_work_tree_hash()}" in lines)
