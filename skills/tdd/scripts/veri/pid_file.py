"""lib/number-in.sh's number_in and lib/pid-file.sh's live_conductor and supervising, run in-process."""

import re


def number_in(file):
    with open(file, "rb") as f:
        n = f.readline().rstrip(b"\n").strip(b" \t")
    return n.decode() if re.fullmatch(rb"[0-9]+", n) else None
