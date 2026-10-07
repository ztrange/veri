"""red-divergence.sh's answer, read off a red leaf's report on stdin."""
import sys

from report import report_read

REASON = """The red leaf's prediction diverged from the failure it saw, so the test is the suspect.

PREDICTED_FAILURE: %s
FAIL_OUTPUT: %s
PREDICTION_NOTE: %s
"""


def main(argv):
    report = sys.stdin.buffer.read().decode()
    fields = report_read(report, ("PREDICTION", "PREDICTED_FAILURE", "FAIL_OUTPUT", "PREDICTION_NOTE"))
    prediction = fields.get("PREDICTION", "")
    if prediction == "MATCHED":
        return 3
    if prediction != "DIVERGED":
        return 2
    reason = REASON % (fields["PREDICTED_FAILURE"], fields["FAIL_OUTPUT"], fields["PREDICTION_NOTE"])
    sys.stdout.buffer.write(reason.encode())
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
