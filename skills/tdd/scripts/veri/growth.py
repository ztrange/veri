"""Context growth of a session, measured from its transcript records."""


def growth(records, baseline=None):
    context = None
    first = None
    seen = set()
    for record in records:
        if record.get("type") == "system" and record.get("subtype") == "init":
            first = None
        usage = record.get("message", {}).get("usage")
        if usage:
            msg_id = record["message"].get("id")
            if msg_id in seen:
                continue
            seen.add(msg_id)
            context = (
                usage["input_tokens"]
                + usage["cache_read_input_tokens"]
                + usage["cache_creation_input_tokens"]
            )
            if first is None:
                first = context
    if first is None:
        return None
    return context - (first if baseline is None else baseline)
