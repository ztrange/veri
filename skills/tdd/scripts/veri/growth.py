"""Context growth of a session, measured from its transcript records."""


def growth(records, baseline=0):
    context = None
    seen = set()
    for record in records:
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
    if context is None:
        return None
    return context - baseline
