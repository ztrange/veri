"""decision-log.sh's work, run in-process: the judge's decisions about no issue, one JSON line each in
`.tdd/decisions.jsonl` of the main working tree."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import datetime
import json
import os
import sys

import redaction
import run_dir

USAGE = "usage: decision-log.sh record <question> <decision> <rule> <by>\n"


def log_path(main=None):
    """`.tdd/decisions.jsonl` in the main working tree <main> (default: the one above the current directory)."""
    return run_dir.main_file(run_dir.main_tree_from_files(os.getcwd()) if main is None else main, "decisions.jsonl")


KEYS = ("question", "decision", "rule", "by", "at")
# Who may decide: an operator role (role-state.sh's roles), or the owner, whose own answer or override is recorded too.
BY = ("coord", "dev", "owner")


class Malformed(Exception):
    """A line of the decision log that is not a decision record: `where` is `<path>:<line number>`."""

    def __init__(self, where):
        super().__init__(where)
        self.where = where


def _record(text):
    """<text> parsed as a decision record (every key of KEYS a non-empty string, `at` an ISO-8601 time with an
    offset), else None."""
    try:
        record = json.loads(text)
    except ValueError:
        return None
    if not (isinstance(record, dict) and all(isinstance(record.get(key), str) and record[key].strip() for key in KEYS)
            and record["by"] in BY):
        return None
    try:
        at = datetime.datetime.fromisoformat(record["at"])
    except ValueError:
        return None
    return record if at.utcoffset() is not None else None


def read(main):
    """The records of <main>'s decision log, oldest first; [] when the file is missing. Raises Malformed for a
    line that is not a decision record, and OSError for a log that cannot be read: an unread record is never "no
    decision"."""
    path = log_path(main)
    try:
        with open(path) as f:
            lines = f.read().splitlines()
    except FileNotFoundError:
        return []
    records = []
    for number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        record = _record(line)
        if record is None:
            raise Malformed("%s:%d" % (path, number))
        records.append(record)
    return records


def epoch(record):
    """A record's `at` as epoch seconds."""
    return datetime.datetime.fromisoformat(record["at"]).timestamp()


def record(question, decision, rule, by):
    fields = {"question": question, "decision": decision, "rule": rule, "by": by}
    line = {**{key: redaction.redact(value) for key, value in fields.items()},
            "at": datetime.datetime.now().astimezone().isoformat(timespec="seconds")}
    path = log_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a") as f:
        f.write(json.dumps(line, ensure_ascii=False) + "\n")


def main(argv):
    if argv[:1] != ["record"] or len(argv) != 5 or not all(a.strip() for a in argv[1:]) or argv[4] not in BY:
        sys.stderr.write(USAGE)
        return 2
    record(*argv[1:])
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
