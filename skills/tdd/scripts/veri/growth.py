"""Context growth of a session, measured from its transcript records."""


def growth(records, baseline=0):
    context = None
    for record in records:
        usage = record.get("message", {}).get("usage")
        if usage:
            context = (
                usage["input_tokens"]
                + usage["cache_read_input_tokens"]
                + usage["cache_creation_input_tokens"]
            )
    if context is None:
        return None
    return context - baseline
