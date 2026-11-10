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


def post_and_record(issue, kind, body, strip_url=False):
    url = github.gh_issue_comment(issue, body)
    if strip_url:
        url = url.rstrip("\n")
    return event.append("", {}, "comment", [f"kind={kind}", f"url={url}"])


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
    return post_and_record(issue, "done", f"### ✅ Done — {pr}\n\n{metrics}")


def read_report(path):
    report = {}
    for line in read_or_empty(path).splitlines():
        key, sep, value = line.partition(": ")
        if sep:
            report[key] = value
    return report


def missing_line(path, key):
    print(f"comment.sh: {path} has no {key}: line", file=sys.stderr)
    return 2


def post_red(issue, note_file=None):
    red_out = ".tdd/develop-red.out"
    if not os.path.exists(red_out):
        print(f"comment.sh: {red_out} is missing", file=sys.stderr)
        return 2
    report = read_report(red_out)
    for key in ("TEST_PATH", "TARGET_TEST", "FAIL_OUTPUT", "PREDICTED_FAILURE"):
        if key not in report:
            return missing_line(red_out, key)
    verdict = "prediction matched"
    prediction = report.get("PREDICTION", "").partition(" ")[0]
    if prediction[-1:] in (",", "."):
        prediction = prediction[:-1]
    if prediction == "DIVERGED":
        if "PREDICTION_NOTE" not in report:
            return missing_line(red_out, "PREDICTION_NOTE")
        verdict = f"prediction diverged\n\n{report['PREDICTION_NOTE']}"
    body = (f"### 🔴 Red\n\nTest: {report['TEST_PATH']} :: {report['TARGET_TEST']}\n\n"
            f"Failing output: {report['FAIL_OUTPUT']}\n\n"
            f"PREDICTED_FAILURE: {report['PREDICTED_FAILURE']}\n\n{verdict}\n")
    return post_and_record(issue, "red", with_note(body, note_file))


def post_verify_red(issue):
    reason = read_or_empty(".tdd/verify-red.reason")
    verdict = "REJECT" if read_or_empty(".tdd/verdict-red.exit").strip() == "1" else "PASS"
    return post_and_record(issue, "verify-red", f"### 🔎 verify-red — {verdict}\n\n{reason}")


def post_green(issue):
    report = read_report(".tdd/develop-green.out")
    body = f"### 🟢 Green\n\nImplementation: {report['IMPL_PATH']}\n\nSuite: {report['SUITE']}\n"
    return post_and_record(issue, "green", body)


def main(argv):
    if len(argv) == 2 and argv[1] == "green":
        return post_green(argv[0])
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
    return post_and_record(issue, "step-done", with_note(body, argv[3] if len(argv) > 3 else None), strip_url=True)


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
