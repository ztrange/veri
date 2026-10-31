"""The price table and the helpers that read it."""

PRICES = {
    "opus": {
        "input": 15.00,
        "cache_read": 1.50,
        "cache_write_5m": 18.75,
        "cache_write_1h": 30.00,
        "output": 75.00,
    },
    "claude-opus-5-5": {
        "input": 4.00,
        "cache_read": 0.20,
        "cache_write_5m": 5.00,
        "cache_write_1h": 8.00,
        "output": 20.00,
    },
}


def cache_write_tokens(usage):
    split = usage.get("cache_creation")
    if split:
        return {
            "cache_write_1h": split.get("ephemeral_1h_input_tokens", 0),
            "cache_write_5m": split.get("ephemeral_5m_input_tokens", 0),
        }
    return {"cache_write_5m": usage.get("cache_creation_input_tokens", 0)}


def family(model):
    for key in sorted(PRICES, key=len, reverse=True):
        if key in model:
            return key
    return None
