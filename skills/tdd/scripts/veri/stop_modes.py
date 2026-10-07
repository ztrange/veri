"""The modes a stop request may name, shared by stop-requested.sh and stop-run.sh."""
STOP_MODES = ("at-ledger", "at-leaf", "now")


def stop_mode_known(mode):
    """True when `mode` is exactly one of STOP_MODES."""
    return mode in STOP_MODES


def modes_named():
    """STOP_MODES as a phrase: "at-ledger, at-leaf or now"."""
    return "{} or {}".format(" ".join(STOP_MODES[:-1]).replace(" ", ", "), STOP_MODES[-1])
