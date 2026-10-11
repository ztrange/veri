"""The one reader of VERI_* tunables."""
import math

STOP_TIMEOUT_MAX = 2 ** 31 - 1


def stop_timeout(raw):
    value = float(raw)
    if not math.isfinite(value) or value <= 0 or value > STOP_TIMEOUT_MAX:
        raise ValueError
    return value
