"""The one per-line parse of a run's events.jsonl and the one dollar/token sum over its
`usage` events, which status.sh's run_activity and scope_totals both read through (#281)."""
import json

TOKEN_KINDS = ("input_tokens", "output_tokens", "cache_read_input_tokens",
               "cache_creation_input_tokens")


def read_events(path):
    """The log's events, one dict per non-blank line."""
    with open(path) as f:
        return [json.loads(raw) for raw in f if raw.strip()]


def usage_totals(events):
    """(dollars, tokens) summed over the usage events."""
    dollars, tokens = 0.0, 0
    for line in events:
        if line.get("event") == "usage":
            dollars += float(line.get("total_cost_usd") or 0)
            tokens += sum(int(line.get(kind) or 0) for kind in TOKEN_KINDS)
    return dollars, tokens
