"""Evaluates .github/workflows/ci.yml's concurrency expression over event payloads, without GitHub."""
import re
from pathlib import Path

CI = Path(__file__).resolve().parents[6] / ".github" / "workflows" / "ci.yml"


def evaluate(line_prefix, event_name, pull_request):
    line = next(l for l in CI.read_text().splitlines() if l.strip().startswith(line_prefix))
    expr = line.split(":", 1)[1].strip()
    match = re.search(r"\$\{\{(.*)\}\}", expr)
    expr = match.group(1).strip() if match else expr
    context = {"event_name": event_name, "event": {"pull_request": pull_request}}

    def lookup(match):
        value = context
        for part in match.group(0).split(".")[1:]:
            value = value.get(part) if isinstance(value, dict) else None
        return repr(value)

    expr = re.sub(r"github(?:\.\w+)+", lookup, expr)
    expr = expr.replace("&&", " and ").replace("||", " or ")
    expr = re.sub(r"!(?!=)", " not ", expr)
    return bool(eval(expr, {"__builtins__": {}}))


def cancel_in_progress(event_name, pull_request):
    return evaluate("cancel-in-progress:", event_name, pull_request)


def test_draft_payload_pull_request_event_cancels_no_in_progress_run_2564():
    draft_payload = {"number": 2548, "draft": True}
    assert cancel_in_progress("pull_request", draft_payload) is False


def test_non_draft_pull_request_event_still_cancels_in_progress_run_2564():
    ready_payload = {"number": 2548, "draft": False}
    assert cancel_in_progress("pull_request", ready_payload) is True


def test_gates_job_skips_for_draft_payload_pull_request_event_2564():
    draft_payload = {"number": 2548, "draft": True}
    assert evaluate("if:", "pull_request", draft_payload) is False
