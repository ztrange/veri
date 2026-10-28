"""Evaluates .github/workflows/ci.yml's concurrency expression over event payloads, without GitHub."""
import re
from pathlib import Path

CI = Path(__file__).resolve().parents[6] / ".github" / "workflows" / "ci.yml"


def cancel_in_progress(event_name, pull_request):
    line = next(l for l in CI.read_text().splitlines() if l.strip().startswith("cancel-in-progress:"))
    expr = re.search(r"\$\{\{(.*)\}\}", line).group(1).strip()
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


def test_draft_payload_pull_request_event_cancels_no_in_progress_run_2564():
    draft_payload = {"number": 2548, "draft": True}
    assert cancel_in_progress("pull_request", draft_payload) is False
