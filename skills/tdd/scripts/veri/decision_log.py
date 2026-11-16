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


def read(main):
    """The records of <main>'s decision log, oldest first; [] when it has none."""
    try:
        with open(log_path(main)) as f:
            return [json.loads(line) for line in f if line.strip()]
    except FileNotFoundError:
        return []


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
    if argv[:1] != ["record"] or len(argv) != 5 or not all(a.strip() for a in argv[1:]):
        sys.stderr.write(USAGE)
        return 2
    record(*argv[1:])
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
