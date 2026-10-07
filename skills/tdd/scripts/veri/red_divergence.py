"""red-divergence.sh's answer, read off a red leaf's report on stdin."""
import sys

from report import report_read

REASON = """The red leaf's prediction diverged from the failure it saw, so the test is the suspect.

PREDICTED_FAILURE: %s
FAIL_OUTPUT: %s
PREDICTION_NOTE: %s
"""
REASON_KEYS = ("PREDICTED_FAILURE", "FAIL_OUTPUT", "PREDICTION_NOTE")


def main(argv):
    report = sys.stdin.buffer.read().decode()
    fields = report_read(report, ("PREDICTION", *REASON_KEYS))
    prediction = fields.get("PREDICTION", "")
    if prediction[-1:] in (",", ";", ":", "."):
        prediction = prediction[:-1]
    if prediction == "MATCHED":
        return 3
    if prediction != "DIVERGED":
        return 2
    reason = REASON % tuple(fields.get(key, "") for key in REASON_KEYS)
    sys.stdout.buffer.write(reason.encode())
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
