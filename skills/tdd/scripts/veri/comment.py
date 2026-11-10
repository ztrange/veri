"""comment.sh's computation, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import contextlib
import io
import os
import sys

import event
import event_log
import github
import metrics as metrics_module
from ledger import ledger_path, ledger_steps

USAGE = "usage: comment.sh <issue> <kind> [--note-file <path>]"


def read_or_empty(path):
    try:
        with open(path) as f:
            return f.read()
    except FileNotFoundError:
        return ""


def with_note(body, note_file):
    if note_file:
        with open(note_file) as f:
            body += f"\n{f.read()}"
    return body


def post_done(issue):
    pr = None
    for e in event_log.read_events(".tdd/events.jsonl", skip_unreadable=True):
        if e.get("event") == "done":
            pr = e["pr"]
    if pr is None:
        print("comment.sh: no done event in .tdd/events.jsonl, so there is no pr-url to post", file=sys.stderr)
        return 2
    metrics = read_or_empty(f".tdd/issue-{issue}-metrics.md")
    if not metrics.startswith("### 📊 Metrics"):
        rendered = io.StringIO()
        with contextlib.redirect_stdout(rendered):
            code = metrics_module.main([issue])
        metrics = rendered.getvalue()
        if code != 0 or not metrics.startswith("### 📊 Metrics"):
            metrics = f"metrics could not be rendered: metrics.sh exited {code}"
    pinned = read_or_empty(f".tdd/issue-{issue}-skip-verify").strip()
    if pinned:
        metrics = f"{metrics.rstrip()}\n⚠️ Unverified phases: {pinned}\n"
    if os.path.isfile(".tdd/stop"):
        metrics = f"{metrics.rstrip()}\nA stop arrived after the last step, so the run finished rather than pausing.\n"
    url = github.gh_issue_comment(issue, f"### ✅ Done — {pr}\n\n{metrics}")
    return event.append("", {}, "comment", ["kind=done", f"url={url}"])


def post_red(issue, note_file=None):
    report = {}
    for line in read_or_empty(".tdd/develop-red.out").splitlines():
        key, sep, value = line.partition(": ")
        if sep:
            report[key] = value
    verdict = "prediction matched"
    if report.get("PREDICTION") == "DIVERGED":
        verdict = f"prediction diverged\n\n{report['PREDICTION_NOTE']}"
    body = (f"### 🔴 Red\n\nTest: {report['TEST_PATH']} :: {report['TARGET_TEST']}\n\n"
            f"Failing output: {report['FAIL_OUTPUT']}\n\n"
            f"PREDICTED_FAILURE: {report['PREDICTED_FAILURE']}\n\n{verdict}\n")
    url = github.gh_issue_comment(issue, with_note(body, note_file))
    return event.append("", {}, "comment", ["kind=red", f"url={url}"])


def post_verify_red(issue):
    reason = read_or_empty(".tdd/verify-red.reason")
    url = github.gh_issue_comment(issue, f"### 🔎 verify-red — PASS\n\n{reason}")
    return event.append("", {}, "comment", ["kind=verify-red", f"url={url}"])


def main(argv):
    if len(argv) == 2 and argv[1] == "verify-red":
        return post_verify_red(argv[0])
    if len(argv) == 2 and argv[1] == "red":
        return post_red(argv[0])
    if len(argv) == 4 and argv[1] == "red" and argv[2] == "--note-file":
        return post_red(argv[0], argv[3])
    if len(argv) == 2 and argv[1] == "done":
        return post_done(argv[0])
    if len(argv) < 2 or argv[1] != "step-done" or (len(argv) > 2 and (argv[2] != "--note-file" or len(argv) != 4)):
        print(USAGE, file=sys.stderr)
        return 2
    issue = argv[0]
    with open(ledger_path(".", issue)) as f:
        done = [r for r in ledger_steps(f.read()) if r[1] == "done"]
    body = f"### ✅ Step done\n\n{done[-1][6]}\n"
    url = github.gh_issue_comment(issue, with_note(body, argv[3] if len(argv) > 3 else None)).rstrip("\n")
    return event.append("", {}, "comment", ["kind=step-done", f"url={url}"])


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
