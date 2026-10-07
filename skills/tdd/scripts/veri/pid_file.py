"""lib/number-in.sh's number_in and lib/pid-file.sh's live_conductor and supervising, run in-process."""


def number_in(file):
    with open(file, "rb") as f:
        return f.readline().rstrip(b"\n").strip(b" \t").decode()
