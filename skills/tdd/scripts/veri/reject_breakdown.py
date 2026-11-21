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


def green_checks(text):
    """{check: REJECTs} off the report's `Green rejects by check:` line; `unnamed` is left unclassified."""
    for line in text.splitlines():
        if line.startswith("Green rejects by check:"):
            pairs = (item.split() for item in line.split(":", 1)[1].split(","))
            return {name: int(count) for name, count in pairs if name != "unnamed"}
    return {}

def monday(day):
    date = datetime.date.fromisoformat(day)
    return date - datetime.timedelta(days=date.weekday())


def main(argv):
    weeks = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0]))
    reasons = collections.defaultdict(collections.Counter)
    for line in sys.stdin.read().splitlines():
        day, path = line.split(" ", 1)
        with open(path) as handle:
            text = handle.read()
        week = weeks[monday(day)]
        for phase, (passes, rejects) in phase_verdicts(text).items():
            week[phase][0] += passes
            week[phase][1] += rejects
            classified = green_checks(text) if phase == "green" else {}
            for check, count in classified.items():
                reasons[monday(day)][(phase, f"check {check}")] += count
            if rejects - sum(classified.values()):
                reasons[monday(day)][(phase, "unclassified")] += rejects - sum(classified.values())
    for week, phases in sorted(weeks.items()):
        rejects = sum(r for _, r in phases.values())
        verifies = sum(p + r for p, r in phases.values())
        print(f"week {week}: REJECT per verify {100 * rejects / verifies:.1f}% ({rejects} of {verifies})")
        for phase, (passes, phase_rejects) in sorted(phases.items()):
            if passes + phase_rejects:
                print(f"  phase {phase}: {phase_rejects} of {passes + phase_rejects}")
        for (phase, reason), count in sorted(reasons[week].items()):
            print(f"  reason {phase} {reason}: {count}")
    return 0

if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
