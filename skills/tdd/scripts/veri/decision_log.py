"""decision-log.sh's work, run in-process: the judge's decisions about no issue, one JSON line each in
`.tdd/decisions.jsonl` of the main working tree."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import datetime
import json
import os
import sys

import run_dir

USAGE = "usage: decision-log.sh record <question> <decision> <rule> <by>\n"


def log_path():
    """`.tdd/decisions.jsonl` in the main working tree."""
    return run_dir.main_file(run_dir.main_tree_from_files(os.getcwd()), "decisions.jsonl")


def record(question, decision, rule, by):
    line = {"question": question, "decision": decision, "rule": rule, "by": by,
            "at": datetime.datetime.now().astimezone().isoformat(timespec="seconds")}
    path = log_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a") as f:
        f.write(json.dumps(line, ensure_ascii=False) + "\n")


def main(argv):
    if argv[:1] != ["record"]:
        sys.stderr.write(USAGE)
        return 2
    record(*argv[1:])
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
