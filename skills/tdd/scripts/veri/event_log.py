"""The one per-line parse of a run's events.jsonl and the one dollar/token sum over its
`usage` events, which status.sh's run_activity and scope_totals both read through (#281)."""
import json

TOKEN_KINDS = ("input_tokens", "output_tokens", "cache_read_input_tokens",
               "cache_creation_input_tokens")


def read_events(path, skip_unreadable=False):
    """The log's events, one dict per non-blank line; skip_unreadable drops lines that
    are not a JSON object."""
    events = []
    with open(path) as f:
        for raw in f:
            if not raw.strip():
                continue
            try:
                event = json.loads(raw)
                if not isinstance(event, dict):
                    raise ValueError("not a JSON object: " + raw.strip())
            except ValueError:
                if skip_unreadable:
                    continue
                raise
            events.append(event)
    return events


def usage_totals(events):
    """(dollars, tokens) summed over the usage events."""
    dollars, tokens = 0.0, 0
    for line in events:
        if line.get("event") == "usage":
            dollars += float(line.get("total_cost_usd") or 0)
            tokens += sum(int(line.get(kind) or 0) for kind in TOKEN_KINDS)
    return dollars, tokens
