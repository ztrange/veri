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


def names_prediction_file(argv):
    return bool(argv) and not argv[0].startswith("-")


def prediction_unwritten_before_run(argv):
    if not names_prediction_file(argv):
        return None
    if not os.path.exists(argv[0]):
        return f"{argv[0]} does not exist"
    if len(argv) > 1 and os.path.getmtime(argv[0]) > os.path.getmtime(argv[1]):
        return f"{argv[0]} is newer than the run output {argv[1]}"
    return None


def prediction_file_content(argv):
    if not names_prediction_file(argv):
        return None
    with open(argv[0], "rb") as handle:
        return handle.read().decode(errors="surrogateescape").strip()


def main(argv):
    unwritten = prediction_unwritten_before_run(argv)
    if unwritten:
        sys.stderr.write(f"prediction not written before the run: {unwritten}\n")
        return 1
    report = sys.stdin.buffer.read().decode(errors="surrogateescape")
    fields = report_read(report, ("PREDICTION", *REASON_KEYS))
    prediction = fields.get("PREDICTION", "").partition(" ")[0]
    if prediction[-1:] in (",", ";", ":", "."):
        prediction = prediction[:-1]
    content = prediction_file_content(argv)
    if content is not None:
        if prediction == "MATCHED" and not content:
            prediction = "DIVERGED"
            fields["PREDICTION_NOTE"] = f"the prediction file {argv[0]} is empty"
        fields["PREDICTED_FAILURE"] = content
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
