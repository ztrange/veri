"""reject-breakdown.sh: the verifier REJECT verdicts of a set of metrics reports, per week (#4568)."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import collections
import datetime
import sys


def phase_verdicts(text):
    """{phase: (PASS, REJECT)} off the report's `#### By phase` table."""
    lines = text.splitlines()
    start = lines.index("#### By phase")
    rows = []
    for line in lines[start + 1:]:
        if line.startswith("#### "):
            break
        if line.startswith("|"):
            rows.append([cell.strip() for cell in line.strip().strip("|").split("|")])
    header, body = rows[0], rows[2:]
    verdicts = {}
    for row in body:
        cells = dict(zip(header, row))
        verdicts[cells["phase"]] = (int(cells["PASS"]), int(cells["REJECT"]))
    return verdicts


def monday(day):
    date = datetime.date.fromisoformat(day)
    return date - datetime.timedelta(days=date.weekday())


def main(argv):
    weeks = collections.defaultdict(lambda: [0, 0])
    for line in sys.stdin.read().splitlines():
        day, path = line.split(" ", 1)
        with open(path) as handle:
            text = handle.read()
        week = weeks[monday(day)]
        for passes, rejects in phase_verdicts(text).values():
            week[0] += passes
            week[1] += rejects
    for week, (passes, rejects) in sorted(weeks.items()):
        verifies = passes + rejects
        print(f"week {week}: REJECT per verify {100 * rejects / verifies:.1f}% ({rejects} of {verifies})")
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
