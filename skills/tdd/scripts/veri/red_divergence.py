"""red-divergence.sh's answer, read off a red leaf's report on stdin."""
import os
import sys

from report import report_read

REASON = """The red leaf's prediction diverged from the failure it saw, so the test is the suspect.

PREDICTED_FAILURE: %s
FAIL_OUTPUT: %s
PREDICTION_NOTE: %s
"""
REASON_KEYS = ("PREDICTED_FAILURE", "FAIL_OUTPUT", "PREDICTION_NOTE")


def main(argv):
    if argv and not argv[0].startswith("-") and (
        not os.path.exists(argv[0])
        or (len(argv) > 1 and os.path.getmtime(argv[0]) > os.path.getmtime(argv[1]))
    ):
        sys.stderr.write("prediction not written before the run\n")
        return 1
    report = sys.stdin.buffer.read().decode(errors="surrogateescape")
    fields = report_read(report, ("PREDICTION", *REASON_KEYS))
    prediction = fields.get("PREDICTION", "").partition(" ")[0]
    if prediction[-1:] in (",", ";", ":", "."):
        prediction = prediction[:-1]
    if prediction == "MATCHED":
        return 3
    if prediction != "DIVERGED":
        return 2
    reason = REASON % tuple(fields.get(key, "") for key in REASON_KEYS)
    sys.stdout.buffer.write(reason.encode(errors="surrogateescape"))
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
