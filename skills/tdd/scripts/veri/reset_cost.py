"""reset-cost.sh's logic, run in-process: what each recorded reset of a role cost, read from the files veri writes."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import json
import math
import os
import re
import statistics
import sys
import time
from datetime import datetime

import entry
import event_log
import growth
import prices
import role_state
import run_dir
import tunables

USAGE = "usage: reset-cost.sh dev [--lane <lane>] | conductor <n>\n"
LANE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]*")
CONTEXT_KEYS = ("input_tokens", "cache_read_input_tokens", "cache_creation_input_tokens")


class Failure(Exception):
    pass


def _count(n, thing, things):
    return "%d %s" % (n, thing if n == 1 else things)


def _epoch(timestamp):
    """The epoch seconds of a transcript's ISO timestamp, None when it is not one."""
    if not isinstance(timestamp, str):
        return None
    try:
        return datetime.fromisoformat(timestamp.replace("Z", "+00:00")).timestamp()
    except ValueError:
        return None


def requests(records):
    """Each request once (by message id) that carries usage, in record order."""
    seen = set()
    found = []
    for record in records:
        message = record.get("message")
        if not isinstance(message, dict) or not message.get("usage") or message.get("id") in seen:
            continue
        seen.add(message.get("id"))
        found.append(record)
    return found


def timed(records):
    """(each request of `records` with a readable timestamp as (epoch, record), the count of those without one)."""
    found = []
    bad = 0
    for record in requests(records):
        moment = _epoch(record.get("timestamp"))
        if moment is None:
            bad += 1
        else:
            found.append((moment, record))
    return found, bad


def _count_ok(value):
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def sound(record):
    """Whether every token count the request's usage carries is a whole number >= 0, the three context counts present."""
    usage = record["message"]["usage"]
    if not isinstance(usage, dict) or not all(_count_ok(usage.get(key)) for key in CONTEXT_KEYS):
        return False
    if "output_tokens" in usage and not _count_ok(usage["output_tokens"]):
        return False
    split = usage.get("cache_creation")
    return not split or (isinstance(split, dict) and all(_count_ok(v) for v in split.values()))


def units(record):
    """The request's price in input-token units at its model's rates, None when the model has no price or a count is unsound."""
    message = record["message"]
    model = prices.family(message.get("model") or "") if isinstance(message.get("model") or "", str) else None
    if model is None or not sound(record):
        return None
    rates = prices.PRICES[model]
    usage = message["usage"]
    dollars = (usage["input_tokens"] * rates["input"] + usage["cache_read_input_tokens"] * rates["cache_read"]
               + usage.get("output_tokens", 0) * rates["output"]
               + sum(tokens * rates[rate] for rate, tokens in prices.cache_write_tokens(usage).items()))
    return dollars / rates["input"]


def cost(window):
    """The summed price of `window`'s requests, None when there is none or one is unpriced or unsound."""
    each = [units(r) for r in window]
    return None if not each or None in each else sum(each)


def per_request(window):
    """The mean context increase per request over `window`, by growth.growth; None under two requests,
    when a request is unsound, or when the context shrank."""
    if len(window) < 2 or not all(sound(r) for r in window):
        return None
    mean = growth.growth(window) / (len(window) - 1)
    return mean if mean >= 0 else None


def cache_read_rate(measured):
    """The cache-read rate in input-token units of the model of the last priced request in `measured`, None when none is."""
    for record in reversed(measured):
        model = record["message"].get("model")
        model = prices.family(model) if isinstance(model, str) else None
        if model:
            return prices.PRICES[model]["cache_read"] / prices.PRICES[model]["input"]
    return None


def _median(values):
    known = [v for v in values if v is not None]
    return statistics.median(known) if known else None


def _figure(value):
    return "unknown" if value is None else "%d" % round(value)


def _read_records(path):
    """(the transcript's JSON-object records, the count of its other non-blank lines); a file that cannot be read is a Failure."""
    try:
        with open(path) as f:
            lines = [line for line in f if line.strip()]
    except (OSError, UnicodeDecodeError):
        raise Failure("reset-cost.sh: unreadable transcript %s\n" % path)
    records = []
    for line in lines:
        try:
            record = json.loads(line)
        except ValueError:
            continue
        if isinstance(record, dict):
            records.append(record)
    return records, len(lines) - len(records)


def _stamp(path, number, key, value):
    try:
        return role_state.epoch(value)
    except (ValueError, OverflowError):
        raise Failure("reset-cost.sh: %s line %d: %s is not a local time stamp\n" % (path, number, key))


def dev_resets(path, lines):
    """[reset-at text, its epoch, recovered-at epoch or None] for each reset the state lines record, in file order;
    an unparseable stamp is a Failure naming the field and line, never its value."""
    resets = []
    for number, line in enumerate(lines, 1):
        key, _, value = line.partition("=")
        if key == "reset-at":
            resets.append([value, _stamp(path, number, key, value), None])
        elif key == "recovered-at" and resets and resets[-1][2] is None:
            resets[-1][2] = _stamp(path, number, key, value)
    return resets


def dev(lane):
    path = role_state.state_path(run_dir.main_tree_from_files(os.getcwd()), "dev", lane)
    lines = (role_state.read(path) or "").splitlines()
    resets = dev_resets(path, lines)
    if not resets:
        return None
    transcripts = list(dict.fromkeys(l.partition("=")[2] for l in lines if l.startswith("transcript=")))
    read = [_read_records(t) for t in transcripts]
    skipped = sum(n for _, n in read)
    found = [timed(records) for records, _ in read]
    bad = sum(n for _, n in found)
    records = sorted((pair for pairs, _ in found for pair in pairs), key=lambda pair: pair[0])
    rows = []
    measured = []
    for i, (at, start, back) in enumerate(resets):
        following = resets[i + 1][1] if i + 1 < len(resets) else float("inf")
        in_order = following > start and (i == 0 or start > resets[i - 1][1]) and back is not None and back >= start
        k = g = None
        if in_order:
            after = [(moment, r) for moment, r in records if start < moment < following]
            upto = next((j for j, (moment, _) in enumerate(after) if moment >= back), None)
            if upto is not None:
                k = cost([r for _, r in after[:upto + 1]])
                if k is not None:
                    measured += [r for _, r in after[:upto + 1]]
            g = per_request([r for moment, r in after if moment >= back])
        rows.append((at, k, g))
    sources = ("K and g from %s at the reset-at and recovered-at lines of %s, %s that are not a JSON object skipped, %s skipped"
               % (", ".join(transcripts) or "no transcript", path,
                  _count(skipped, "transcript line", "transcript lines"),
                  _count(bad, "request with an unreadable timestamp", "requests with an unreadable timestamp")))
    return rows, measured, sources, "VERI_RESET_GROWTH_DEV", _knob("VERI_RESET_GROWTH_DEV")


def launches(lines):
    """(each launch's timed requests, a launch starting at each `system`/`init` record of a conductor log, and the count
    of requests without a readable timestamp); lines that are not a JSON object are skipped."""
    found = [[]]
    for line in lines:
        try:
            record = json.loads(line)
        except ValueError:
            continue
        if not isinstance(record, dict):
            continue
        if record.get("type") == "system" and record.get("subtype") == "init":
            found.append([])
        else:
            found[-1].append(record)
    each = [timed(launch) for launch in found]
    return [pairs for pairs, _ in each if pairs], sum(n for _, n in each)


def conductor(run):
    main = run_dir.main_tree_from_files(os.getcwd())
    journal = event_log.path(run_dir.worktree(main, run))
    restarts = event_log.events(run_dir.worktree(main, run), "conductor-restart", skip_unreadable=True)
    if not restarts:
        return None
    for i, restart in enumerate(restarts, 1):
        ts = restart.get("ts")
        if not (isinstance(ts, (int, float)) and not isinstance(ts, bool) and 0 <= ts < 2 ** 40):
            raise Failure("reset-cost.sh: %s: conductor-restart event %d: ts is not a time\n" % (journal, i))
    log = run_dir.main_file(main, "conductor-%s.log" % run)
    try:
        with open(log) as f:
            relaunches, bad = launches(f)
    except (OSError, UnicodeDecodeError):
        raise Failure("reset-cost.sh: unreadable conductor log %s\n" % log)
    rows = []
    measured = []
    for restart in restarts:
        launch = next(([r for _, r in pairs] for pairs in relaunches if pairs[0][0] >= restart["ts"]), None)
        at = time.strftime(role_state.STAMP, time.localtime(restart["ts"]))
        k = cost(launch[:1]) if launch else None
        rows.append((at, k, per_request(launch) if launch else None))
        if k is not None:
            measured += launch[:1]
    sources = "K and g from %s at the conductor-restart events of %s, %s skipped" % (
        log, journal, _count(bad, "request with an unreadable timestamp", "requests with an unreadable timestamp"))
    return rows, measured, sources, "VERI_RESET_GROWTH_CONDUCTOR", _knob("VERI_RESET_GROWTH_CONDUCTOR")


def _knob(name):
    """The growth knob's value; a bad one is a Failure naming it, before anything is read or printed."""
    value, bad = tunables.resolve(name)
    if bad:
        raise Failure("reset-cost.sh: %s must be %s, got '%s'\n" % (name, bad[1], bad[0]))
    return value


def main(argv):
    try:
        return _main(argv)
    except Failure as e:
        sys.stderr.write(str(e))
        return 2


def _main(argv):
    lane = None
    if argv[1:2] == ["--lane"] and len(argv) == 3:
        lane = argv[2]
        argv = argv[:1]
    if lane is not None and not LANE.fullmatch(lane):
        raise Failure(USAGE)
    if argv == ["dev"]:
        _knob("VERI_RESET_GROWTH_DEV")
        measures = dev(lane)
    elif len(argv) == 2 and argv[0] == "conductor" and lane is None and entry.whole_number(argv[1]) is not None:
        _knob("VERI_RESET_GROWTH_CONDUCTOR")
        measures = conductor(argv[1])
    else:
        raise Failure(USAGE)
    if measures is None:
        return 3
    rows, measured, sources, knob, value = measures
    out = ["%s K=%s g=%s" % (at, _figure(k), _figure(g)) for at, k, g in rows]
    k = _median(row[1] for row in rows)
    g = _median(row[2] for row in rows)
    r = cache_read_rate(measured)
    partial = sum(1 for _, rk, rg in rows if rk is None or rg is None)
    best = None if partial or None in (k, g, r) else math.sqrt(2 * k * g / r)
    out.append("median K=%s g=%s r=%s optimum=%s %s=%s" % (_figure(k), _figure(g), "unknown" if r is None else "%g" % r,
                                                           _figure(best), knob, value))
    why = "; optimum unknown: %d of %d resets has an unknown K or g" % (partial, len(rows)) if partial else ""
    out.append("source: %s; rates from veri/prices.py; %s from the environment or its default%s" % (sources, knob, why))
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    entry.run(main, sys.argv[1:])
