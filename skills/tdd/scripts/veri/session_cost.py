"""session-cost.sh's computations, run in-process."""
import glob
import json
import os
import subprocess
import sys
from datetime import datetime

USAGE = "usage: session-cost.sh --since <ISO date> [--json] [<transcript.jsonl> ...]"

PRICES = {
    "opus": {
        "input": 15.00,
        "cache_read": 1.50,
        "cache_write_5m": 18.75,
        "cache_write_1h": 30.00,
        "output": 75.00,
    },
}

RAMP_FACTOR = 1.5

ROLES = (
    ("sdk-cli", "sdk-cli (leaf)"),
    (None,      "interactive"),
)


def fail(message):
    print("session-cost.sh: " + message, file=sys.stderr)
    return 2


def refuse(message=None):
    if message is not None:
        fail(message)
    print(USAGE, file=sys.stderr)
    return 2


def cache_write_tokens(usage):
    split = usage.get("cache_creation")
    if split:
        return {
            "cache_write_1h": split.get("ephemeral_1h_input_tokens", 0),
            "cache_write_5m": split.get("ephemeral_5m_input_tokens", 0),
        }
    return {"cache_write_5m": usage.get("cache_creation_input_tokens", 0)}


def one_rate(field, rate):
    return lambda usage: {rate: usage.get(field, 0)}


KINDS = (
    ("cache_read",  one_rate("cache_read_input_tokens", "cache_read"), "cache read"),
    ("cache_write", cache_write_tokens,                                "cache write"),
    ("output",      one_rate("output_tokens", "output"),               "output"),
    ("input",       one_rate("input_tokens", "input"),                 "input"),
)

BILLED = tuple(kind for kind, _, _ in KINDS)
CONTEXT = tuple(kind for kind in BILLED if kind != "output")


def model_id(obj):
    return obj["message"].get("model", "")


def weigh(usage, kinds):
    return sum(count
               for kind, read, _ in KINDS if kind in kinds
               for count in read(usage).values())


def family(model):
    for key in PRICES:
        if key in model:
            return key
    return None


def local_date(stamp):
    moment = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
    return moment.astimezone().date().isoformat()


def usage_records(path, since):
    seen = set()
    for line in open(path):
        s = line.strip()
        if not s.startswith("{"):
            continue
        try:
            obj = json.loads(s)
        except ValueError:
            continue
        if not isinstance(obj, dict):
            continue
        usage = obj.get("message", {}).get("usage")
        stamp = obj.get("timestamp")
        if not usage or not stamp:
            continue
        if local_date(stamp) < since:
            continue
        request = obj.get("requestId")
        if request is not None:
            if request in seen:
                continue
            seen.add(request)
        yield obj


def totals(records):
    tokens = {kind: {} for kind, _, _ in KINDS}
    for obj in records:
        usage = obj["message"]["usage"]
        for kind, read, _ in KINDS:
            for rate, count in read(usage).items():
                tokens[kind][rate] = tokens[kind].get(rate, 0) + count
    return tokens


def unpriced(records):
    rows = {}
    for obj in records:
        model = model_id(obj)
        if family(model):
            continue
        rows[model] = rows.get(model, 0) + weigh(obj["message"]["usage"], BILLED)
    return rows


def context(usage):
    return weigh(usage, CONTEXT)


def verdict(requests, preamble, total):
    floor = requests * preamble
    return "un-cleared ramp" if floor and total > floor * RAMP_FACTOR else ""


def sessions(records):
    rows = {}
    for obj in records:
        weight = context(obj["message"]["usage"])
        row = rows.setdefault(obj.get("sessionId", ""),
                              {"requests": 0, "preamble": weight, "final": 0, "total": 0,
                               "harness": obj.get("entrypoint", "")})
        row["requests"] += 1
        row["final"] = weight
        row["total"] += weight
    return {key: dict(row, verdict=verdict(row["requests"], row["preamble"], row["total"]))
            for key, row in rows.items()}


def harness_label(harness):
    return harness or "conductor"


def bands(rows):
    groups = {}
    for row in rows.values():
        groups.setdefault(row["harness"], []).append(row["preamble"])
    banded = {}
    for harness, preambles in groups.items():
        preambles.sort()
        banded[harness] = (preambles[0], preambles[len(preambles) // 2], preambles[-1])
    return banded


def role(obj):
    return "sdk-cli" if obj.get("entrypoint") == "sdk-cli" else None


def costed(tokens, price):
    return {
        kind: sum(count * price[rate] for rate, count in tokens[kind].items()) / 1e6
        for kind, _, _ in KINDS
    }


def bill(tokens, price):
    return sum(costed(tokens, price).values())


def row(label, tally, amount):
    print("  %-14s %19s   $%.2f" % (label, tally, amount))


def parse_args(argv):
    since, as_json, transcripts = "", False, []
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg == "--since":
            if i + 1 >= len(argv) or not argv[i + 1]:
                return None
            since = argv[i + 1]
            i += 2
        elif arg == "--json":
            as_json = True
            i += 1
        else:
            transcripts.append(arg)
            i += 1
    if not since:
        return None
    return since, as_json, transcripts


def repo_root():
    try:
        done = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                              stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    except OSError:
        return ""
    return done.stdout.strip() if done.returncode == 0 else ""


def discover():
    root = repo_root()
    if not root:
        return None
    slug = os.path.realpath(root).replace("/", "-")
    projects = os.path.join(os.environ["HOME"], ".claude", "projects")
    found = []
    if not os.path.isdir(projects):
        return found
    for directory in sorted(glob.glob(glob.escape(os.path.join(projects, slug)) + "*/")):
        found.extend(path for path in sorted(glob.glob(glob.escape(directory) + "*.jsonl"))
                     if os.path.isfile(path))
    return found


def report(since, as_json, paths):
    records = [obj for path in paths for obj in usage_records(path, since)]

    priced = [obj for obj in records if family(model_id(obj))]
    tokens = totals(priced)

    if not priced:
        return fail("no known model in any transcript")
    price = PRICES[family(model_id(priced[0]))]

    cost = costed(tokens, price)

    if as_json:
        print(json.dumps({
            "since": since,
            "transcripts": len(paths),
            "cost": dict(cost, total=bill(tokens, price)),
        }, indent=2))
        return 0

    counted = {kind: sum(tokens[kind].values()) for kind, _, _ in KINDS}
    print("since %s  %d transcript(s)" % (since, len(paths)))
    for kind, _, label in KINDS:
        row(label, "%d tokens" % counted[kind], cost[kind])
    row("total", "", bill(tokens, price))
    for key, label in ROLES:
        theirs = totals(obj for obj in priced if role(obj) == key)
        row(label, "", bill(theirs, price))

    session_rows = sessions(records)
    print("  per session")
    for key, session in session_rows.items():
        print("    %s  %s  preamble %d  final %d  read %d  %s"
              % (key, harness_label(session["harness"]), session["preamble"],
                 session["final"], session["total"], session["verdict"]))

    print("  baselines by harness")
    for harness, (low, mid, high) in bands(session_rows).items():
        print("    %-14s min %d  median %d  max %d" % (harness_label(harness), low, mid, high))

    strangers = unpriced(records)
    if strangers:
        print("  not priced, no rate in the table for:")
        for model, count in strangers.items():
            print("    %s  %d tokens" % (model, count))
    return 0


def main(argv):
    parsed = parse_args(argv)
    if parsed is None:
        return refuse()
    since, as_json, transcripts = parsed
    if not transcripts:
        transcripts = discover()
        if transcripts is None:
            return fail("no transcript named, and not inside a git repository")
    if not transcripts:
        return fail("no transcripts found for this repository")
    for path in transcripts:
        if not os.path.isfile(path):
            return refuse("no such transcript: %s" % path)
    return report(since, as_json, transcripts)


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
