"""comment.sh's computation, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import contextlib
import io
import json
import os
import sys
import tempfile

import detect_test_command
import event
import event_log
import github
import metrics as metrics_module
from ledger import handed_out, ledger_path, ledger_steps

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


def read_steps(issue):
    with open(ledger_path(".", issue)) as f:
        return ledger_steps(f.read())


def post_and_record(issue, kind, body, strip_url=False, target=None):
    url = github.gh_issue_comment(target or issue, body)
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


def missing_file(path):
    print(f"comment.sh: {path} is missing", file=sys.stderr)
    return 2


def load_report(path, keys):
    if not os.path.exists(path):
        return None, missing_file(path)
    report = read_report(path)
    for key in keys:
        if key not in report:
            return None, missing_line(path, key)
    return report, 0


def post_red(issue, note_file=None):
    red_out = ".tdd/develop-red.out"
    report, code = load_report(red_out, ("TEST_PATH", "TARGET_TEST", "FAIL_OUTPUT", "PREDICTED_FAILURE"))
    if report is None:
        return code
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


def verdict_word(phase):
    return "REJECT" if read_or_empty(f".tdd/verdict-{phase}.exit").strip() == "1" else "PASS"


def post_verify(issue, kind):
    phase = kind.removeprefix("verify-")
    reason = read_or_empty(f".tdd/{kind}.reason")
    verdict = verdict_word(phase)
    return post_and_record(issue, kind, f"### 🔎 {kind} — {verdict}\n\n{reason}")


def post_green(issue, note_file=None):
    green_out = ".tdd/develop-green.out"
    report, code = load_report(green_out, ("IMPL_PATH", "SUITE"))
    if report is None:
        return code
    body = f"### 🟢 Green\n\nImplementation: {report['IMPL_PATH']}\n\nSuite: {report['SUITE']}\n"
    return post_and_record(issue, "green", with_note(body, note_file))


def post_refactor(issue, note_file=None):
    refactor_out = ".tdd/develop-refactor.out"
    if not os.path.exists(refactor_out):
        return missing_file(refactor_out)
    report = read_or_empty(refactor_out).splitlines()
    transforms = [line.removeprefix("RESULT: ") for line in report if line.startswith("RESULT: ")]
    flagged = "".join(f"triangulation flagged: {line.removeprefix('FLAGS: ')}\n"
                      for line in report if line.startswith(("FLAGS: overfit:", "FLAGS: overfit |")))
    if transforms == ["nothing left to tidy"]:
        content = "no refactor warranted\n"
    else:
        content = "".join(f"- {t}\n" for t in transforms)
    return post_and_record(issue, "refactor", with_note(f"### 🛠️ Refactor\n\n{content}{flagged}", note_file))


def post_revised(issue, phase):
    reason = read_or_empty(f".tdd/verify-{phase}.reason")
    return post_and_record(issue, "verify-revised", f"### 🔎 verify-{phase} (revised) — PASS\n\n{reason}")


def post_verify_skipped(issue):
    return post_and_record(issue, "verify-refactor", "### 🔎 verify-refactor — SKIPPED (nothing landed)")


def post_plan(issue):
    steps = read_steps(issue)
    with tempfile.TemporaryDirectory() as scratch:
        body_file = os.path.join(scratch, "body")
        with open(body_file, "w") as f:
            f.write(github.gh_issue_view(issue, "body"))
        command = detect_test_command.resolved("fast", body_file, ".")
    listed = "".join(f"- {r[6]}\n" for r in steps)
    return post_and_record(issue, "plan", f"### 🗺️ Plan\n\n{listed}\nTest command: {os.fsdecode(command)}\n")


def post_verify_plan(issue):
    reason = read_or_empty(".tdd/verify-plan.reason")
    verdict = verdict_word("plan")
    return post_and_record(issue, "verify-plan", f"### 🗺️ verify-plan — {verdict}\n\n{reason}")


def post_resuming(issue, note_file=None):
    steps = read_steps(issue)
    pending = next((r[6] for r in steps if handed_out(r)), None)
    heading = "### ▶️ Resuming\n" if pending is None else f"### ▶️ Resuming\n\n{pending}\n"
    return post_and_record(issue, "resuming", with_note(heading, note_file))


def current_branch():
    head = read_or_empty(".git/HEAD").strip()
    return head.removeprefix("ref: refs/heads/")


def run_pr_number():
    branch = current_branch()
    path = f"repos/{{owner}}/{{repo}}/pulls?head={{owner}}:{branch}"
    prs = json.loads(github.gh_api(path).stdout)
    if not prs:
        print(f"comment.sh: no PR has {branch} as its head", file=sys.stderr)
        return None
    return prs[0]["number"]


def last_event(name):
    found = None
    for e in event_log.read_events(".tdd/events.jsonl"):
        if e.get("event") == name:
            found = e
    if found is None:
        print(f"comment.sh: no {name} event in .tdd/events.jsonl", file=sys.stderr)
    return found


def post_bailed(issue, note_file, pr=False):
    bail = last_event("bail")
    if bail is None:
        return 2
    heading = f"### ⛔ Bailed — {bail['phase']} ({bail['classification']} failure)\n"
    target = run_pr_number() if pr else None
    if pr and target is None:
        return 2
    return post_and_record(issue, "bailed", with_note(heading, note_file), target=target)


def post_stopped(issue, note_file):
    stop = last_event("stop")
    if stop is None:
        return 2
    rendered = io.StringIO()
    with contextlib.redirect_stdout(rendered):
        metrics_module.main([issue])
    body = f"### ⏹️ Stopped — {stop['mode']}\n\n{rendered.getvalue()}\nat={stop['at']}\n"
    return post_and_record(issue, "stopped", with_note(body, note_file))


def main(argv):
    if len(argv) == 4 and argv[1] == "stopped" and argv[2] == "--note-file":
        return post_stopped(argv[0], argv[3])
    if len(argv) == 5 and argv[1:4] == ["bailed", "--pr", "--note-file"]:
        return post_bailed(argv[0], argv[4], pr=True)
    if len(argv) == 4 and argv[1] == "bailed" and argv[2] == "--note-file":
        return post_bailed(argv[0], argv[3])
    if argv[1:] == ["verify-plan"]:
        return post_verify_plan(argv[0])
    if argv[1:] == ["plan"]:
        return post_plan(argv[0])
    if argv[1:] == ["verify-refactor", "--skipped"]:
        return post_verify_skipped(argv[0])
    if len(argv) == 3 and argv[1] == "verify-revised":
        return post_revised(argv[0], argv[2])
    noted = {"green": post_green, "red": post_red, "refactor": post_refactor, "resuming": post_resuming}
    if len(argv) in (2, 4) and argv[1] in noted and (len(argv) == 2 or argv[2] == "--note-file"):
        return noted[argv[1]](argv[0], *argv[3:])
    if len(argv) == 2 and argv[1] in ("verify-red", "verify-green", "verify-refactor"):
        return post_verify(argv[0], argv[1])
    if len(argv) == 2 and argv[1] == "done":
        return post_done(argv[0])
    if len(argv) < 2 or argv[1] != "step-done" or (len(argv) > 2 and (argv[2] != "--note-file" or len(argv) != 4)):
        print(USAGE, file=sys.stderr)
        return 2
    issue = argv[0]
    done = [r for r in read_steps(issue) if r[1] == "done"]
    body = f"### ✅ Step done\n\n{done[-1][6]}\n"
    return post_and_record(issue, "step-done", with_note(body, argv[3] if len(argv) > 3 else None), strip_url=True)


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
