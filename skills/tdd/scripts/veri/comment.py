"""comment.sh's computation, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import json
import os
import sys
import tempfile

import detect_test_command
import event
import event_log
import github
import metrics as metrics_module
import paths
import restart_marker
import run_dir
import run_pins
from ledger import handed_out, is_retired, ledger_steps
from report import report_values

USAGE = "usage: comment.sh <issue> <kind> [--note-file <path>] [--pr]  (kinds include bailed, stopped, revise <phase> <k>; --pr only with bailed)"


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
    with open(run_dir.ledger(".", issue)) as f:
        return ledger_steps(f.read())


def post_and_record(issue, kind, body, strip_url=False, target=None):
    url = github.gh_issue_comment(target or issue, github.published(body))
    if strip_url:
        url = url.rstrip("\n")
    return event.append("", {}, "comment", [f"kind={kind}", f"url={url}"])


def render_metrics(issue):
    code, rendered, err = metrics_module.rendered(issue)
    sys.stderr.write(err)
    return code, rendered


def post_done(issue):
    done = event_log.last(".", "done", skip_unreadable=True)
    pr = done["pr"] if done is not None else None
    if pr is None:
        print("comment.sh: no done event in .tdd/events.jsonl, so there is no pr-url to post", file=sys.stderr)
        return 2
    metrics = read_or_empty(run_dir.issue_file(".", issue, "-metrics.md"))
    if not metrics.startswith("### 📊 Metrics"):
        code, metrics = render_metrics(issue)
        if code != 0 or not metrics.startswith("### 📊 Metrics"):
            metrics = f"metrics could not be rendered: metrics.sh exited {code}"
    pinned = run_pins.skip_verify(issue, ".", unreadable_raises=True)
    if pinned:
        metrics = f"{metrics.rstrip()}\n⚠️ Unverified phases: {pinned}\n"
    if os.path.isfile(run_dir.run_file(".", "stop")):
        metrics = f"{metrics.rstrip()}\nA stop arrived after the last step, so the run finished rather than pausing.\n"
    return post_and_record(issue, "done", f"### ✅ Done — {pr}\n\n{metrics}")


def read_report(path, keys):
    """{key: value} of each key's last `KEY: value` line; a key with none is absent."""
    text = read_or_empty(path)
    found = {key: report_values(text, key, occurrence="last", splitlines=True) for key in keys}
    return {key: value for key, value in found.items() if value is not None}


def missing_line(path, key):
    print(f"comment.sh: {path} has no {key}: line", file=sys.stderr)
    return 2


def missing_file(path):
    print(f"comment.sh: {path} is missing", file=sys.stderr)
    return 2


def load_report(path, keys, optional=()):
    if not os.path.exists(path):
        return None, missing_file(path)
    report = read_report(path, keys + optional)
    for key in keys:
        if key not in report:
            return None, missing_line(path, key)
    return report, 0


def post_red(issue, note_file=None):
    red_out = ".tdd/develop-red.out"
    report, code = load_report(red_out, ("TEST_PATH", "TARGET_TEST", "FAIL_OUTPUT", "PREDICTED_FAILURE"),
                               ("PREDICTION", "PREDICTION_NOTE"))
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


SWITCHED_OFF = "SKIPPED (switched off)"


def verdict_file(phase):
    return read_or_empty(run_dir.run_file(".", f"verdict-{phase}.exit")).strip()


def verdict_reason(phase):
    if verdict_file(phase) == "skipped":
        return ""
    return read_or_empty(run_dir.run_file(".", f"verify-{phase}.reason"))


def verdict_word(phase):
    return {"1": "REJECT", "skipped": SWITCHED_OFF}.get(verdict_file(phase), "PASS")


def post_verify(issue, kind):
    phase = kind.removeprefix("verify-")
    reason = verdict_reason(phase)
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
    report = read_or_empty(refactor_out)
    transforms = report_values(report, "RESULT", splitlines=True)
    flagged = "".join(f"triangulation flagged: {flags}\n" for flags in report_values(report, "FLAGS", splitlines=True)
                      if flags.startswith(("overfit:", "overfit |")))
    if transforms == ["nothing left to tidy"]:
        content = "no refactor warranted\n"
    else:
        content = "".join(f"- {t}\n" for t in transforms)
    return post_and_record(issue, "refactor", with_note(f"### 🛠️ Refactor\n\n{content}{flagged}", note_file))


def post_revised(issue, phase):
    reason = verdict_reason(phase)
    verdict = SWITCHED_OFF if verdict_file(phase) == "skipped" else "PASS"
    return post_and_record(issue, "verify-revised", f"### 🔎 verify-{phase} (revised) — {verdict}\n\n{reason}")


def post_revise(issue, phase, attempt):
    """REVISE.md sub-step 2's mirror of attempt <attempt>: the rejection reason verbatim (PRD 038.9)."""
    import tunables
    budget = tunables.get("REVISE_BUDGET", unless_empty=True)
    return post_and_record(issue, "revise", f"### ♻️ Revise {phase} — attempt {attempt}/{budget}\n\n"
                           + read_or_empty(run_dir.run_file(".", f"verify-{phase}.reason")))


def post_pin(issue):
    """PIN.md's PASS mirror: the step just pinned, the last done one, and why it already holds."""
    done = [r for r in read_steps(issue) if r.state == "done"]
    reason = f"verify-pin — {SWITCHED_OFF}\n" if verdict_file("pin") == "skipped" else verdict_reason("pin")
    return post_and_record(issue, "pin", f"### 📌 Already satisfied — {done[-1].text}\n\n{reason}")


def post_retire(issue):
    """PIN.md's REJECT mirror once pin-reject-route.sh retired a step: the last retired step, and the verifier's reason."""
    retired = [r for r in read_steps(issue) if r.state == "done" and is_retired(r.text)]
    return post_and_record(issue, "retire", f"### 🪦 Retired — {retired[-1].text}\n\n{verdict_reason('pin')}")


def post_verify_skipped(issue):
    return post_and_record(issue, "verify-refactor", "### 🔎 verify-refactor — SKIPPED (nothing landed)")


def post_plan(issue):
    steps = read_steps(issue)
    with tempfile.TemporaryDirectory() as scratch:
        body_file = os.path.join(scratch, "body")
        with open(body_file, "w") as f:
            f.write(github.gh_issue_view(issue, "body"))
        command = detect_test_command.resolved("fast", body_file, ".")
    if command is None:
        print("comment.sh: no fast-tier command found", file=sys.stderr)
        return 2
    listed = "".join(f"- {r.text}\n" for r in steps)
    return post_and_record(issue, "plan", f"### 🗺️ Plan\n\n{listed}\nTest command: {os.fsdecode(command)}\n")


def post_verify_plan(issue):
    reason = read_or_empty(run_dir.run_file(".", "verify-plan.reason"))
    verdict = verdict_word("plan")
    return post_and_record(issue, "verify-plan", f"### 🗺️ verify-plan — {verdict}\n\n{reason}")


def post_resuming(issue, note_file=None):
    steps = read_steps(issue)
    pending = next((r.text for r in steps if handed_out(r)), None)
    heading = "### ▶️ Resuming\n" if pending is None else f"### ▶️ Resuming\n\n{pending}\n"
    return post_and_record(issue, "resuming", with_note(heading, note_file))


def current_branch():
    git_dir = ".git"
    if os.path.isfile(".git"):
        pointer = read_or_empty(".git").strip()
        git_dir = pointer.removeprefix("gitdir:").strip()
    head = read_or_empty(os.path.join(git_dir, "HEAD")).strip()
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
    return event_log.last(".", name)


def event_before_last(name):
    before = None
    previous = None
    for e in event_log.read_events(".tdd/events.jsonl"):
        if e.get("event") == name:
            before = previous
        previous = e
    return before


def post_bailed(issue, note_file, pr=False):
    bail = last_event("bail")
    if bail is None:
        print("comment.sh: no bail event in .tdd/events.jsonl", file=sys.stderr)
        return 2
    heading = f"### ⛔ Bailed — {bail['phase']} ({bail['classification']} failure)\n"
    target = run_pr_number() if pr else None
    if pr and target is None:
        return 2
    return post_and_record(issue, "bailed", with_note(heading, note_file), target=target)


def restart_pending():
    # An empty, non-digit or unreadable marker counts as dead: SCRIPTS.md's comment entry.
    return restart_marker.in_flight(".", unreadable=False)


def post_stopped(issue, note_file=None):
    stop = last_event("stop")
    if stop is None:
        print("comment.sh: no stop event in .tdd/events.jsonl", file=sys.stderr)
        return 2
    code, rendered = render_metrics(issue)
    metrics = rendered if code == 0 else f"metrics could not be rendered: metrics.sh exited {code}\n"
    body = f"### ⏹️ Stopped — {stop['mode']}\n\n{metrics}\nat={stop['at']}\n"
    before = event_before_last("stop")
    if before is not None and before.get("event") == "push-rejected":
        body += f"push=rejected sha={before['remote_sha']}\n"
    if restart_pending():
        body += "The conductor is being restarted for context growth.\n"
    else:
        scripts = paths.resolved_scripts_of(__file__)
        body += f"branch={current_branch()}\nworktree={os.getcwd()}\n{scripts}/run-conductor.sh {issue}\n"
    return post_and_record(issue, "stopped", with_note(body, note_file))


def main(argv):
    if len(argv) == 5 and argv[1:4] == ["bailed", "--pr", "--note-file"]:
        return post_bailed(argv[0], argv[4], pr=True)
    if len(argv) == 4 and argv[1] == "bailed" and argv[2] == "--note-file":
        return post_bailed(argv[0], argv[3])
    if argv[1:] == ["verify-plan"]:
        return post_verify_plan(argv[0])
    if argv[1:] == ["pin"]:
        return post_pin(argv[0])
    if argv[1:] == ["retire"]:
        return post_retire(argv[0])
    if argv[1:] == ["plan"]:
        return post_plan(argv[0])
    if argv[1:] == ["verify-refactor", "--skipped"]:
        return post_verify_skipped(argv[0])
    if len(argv) == 4 and argv[1] == "revise":
        return post_revise(argv[0], argv[2], argv[3])
    if len(argv) == 3 and argv[1] == "verify-revised":
        return post_revised(argv[0], argv[2])
    noted = {"green": post_green, "red": post_red, "refactor": post_refactor, "resuming": post_resuming,
             "stopped": post_stopped}
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
    done = [r for r in read_steps(issue) if r.state == "done"]
    body = f"### ✅ Step done\n\n{done[-1].text}\n"
    return post_and_record(issue, "step-done", with_note(body, argv[3] if len(argv) > 3 else None), strip_url=True)


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
