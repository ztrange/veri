"""reset-cost.sh's logic, run in-process: what each recorded reset of a role cost, read from the files veri writes."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import json
import math
import os
import statistics
import sys
import time
from datetime import datetime

import event_log
import growth
import prices
import role_state
import run_dir
import tunables

USAGE = "usage: reset-cost.sh dev [--lane <lane>] | conductor <n>\n"


class Failure(Exception):
    pass


def _epoch(timestamp):
    return datetime.fromisoformat(timestamp.replace("Z", "+00:00")).timestamp()


def requests(records):
    """Each request once (by message id) that carries usage, in record order."""
    seen = set()
    found = []
    for record in records:
        message = record.get("message") or {}
        if not message.get("usage") or message.get("id") in seen:
            continue
        seen.add(message.get("id"))
        found.append(record)
    return found


def units(record):
    """The request's price in input-token units at its model's rates, None when the model has no price."""
    message = record["message"]
    model = prices.family(message.get("model") or "")
    if model is None:
        return None
    rates = prices.PRICES[model]
    usage = message["usage"]
    dollars = (usage.get("input_tokens", 0) * rates["input"] + usage.get("cache_read_input_tokens", 0) * rates["cache_read"]
               + usage.get("output_tokens", 0) * rates["output"]
               + sum(tokens * rates[rate] for rate, tokens in prices.cache_write_tokens(usage).items()))
    return dollars / rates["input"]


def cost(window):
    """The summed price of `window`'s requests, None when there is none or one is unpriced."""
    each = [units(r) for r in window]
    return None if not each or None in each else sum(each)


def per_request(window):
    """The mean context increase per request over `window`, by growth.growth; None under two requests."""
    if len(window) < 2:
        return None
    return growth.growth(window) / (len(window) - 1)


def cache_read_rate(measured):
    """The cache-read rate in input-token units of the model of the last priced request in `measured`, None when none is."""
    for record in reversed(measured):
        model = prices.family(record["message"].get("model") or "")
        if model:
            return prices.PRICES[model]["cache_read"] / prices.PRICES[model]["input"]
    return None


def _median(values):
    known = [v for v in values if v is not None]
    return statistics.median(known) if known else None


def _figure(value):
    return "unknown" if value is None else "%d" % round(value)


def _read_records(path):
    try:
        with open(path) as f:
            return [json.loads(line) for line in f if line.strip()]
    except (OSError, ValueError, UnicodeDecodeError):
        raise Failure("reset-cost.sh: unreadable transcript %s\n" % path)


def dev_resets(lines):
    """(reset-at, recovered-at or None, next reset-at or None) for each reset the state lines record."""
    resets = []
    for line in lines:
        key, _, value = line.partition("=")
        if key == "reset-at":
            resets.append([value, None])
        elif key == "recovered-at" and resets and resets[-1][1] is None:
            resets[-1][1] = value
    return [(at, recovered, resets[i + 1][0] if i + 1 < len(resets) else None)
            for i, (at, recovered) in enumerate(resets)]


def dev(lane):
    path = role_state.state_path(run_dir.main_tree_from_files(os.getcwd()), "dev", lane)
    lines = (role_state.read(path) or "").splitlines()
    resets = dev_resets(lines)
    if not resets:
        return None
    transcripts = list(dict.fromkeys(l.partition("=")[2] for l in lines if l.startswith("transcript=")))
    records = sorted((r for t in transcripts for r in requests(_read_records(t)) if r.get("timestamp")),
                     key=lambda r: _epoch(r["timestamp"]))
    rows = []
    measured = []
    for at, recovered, following in resets:
        start = role_state.epoch(at)
        end = role_state.epoch(following) if following else float("inf")
        k = g = None
        if recovered:
            back = role_state.epoch(recovered)
            after = [r for r in records if start < _epoch(r["timestamp"]) < end]
            upto = next((i for i, r in enumerate(after) if _epoch(r["timestamp"]) >= back), None)
            if upto is not None:
                k = cost(after[:upto + 1])
                measured += after[:upto + 1]
            g = per_request([r for r in after if _epoch(r["timestamp"]) >= back])
        rows.append((at, k, g))
    sources = "K and g from %s at the reset-at and recovered-at lines of %s" % (", ".join(transcripts) or "no transcript", path)
    return rows, measured, sources, "VERI_RESET_GROWTH_DEV", tunables.get("VERI_RESET_GROWTH_DEV")


def launches(lines):
    """Each launch's requests, a launch starting at each `system`/`init` record of a conductor log; lines that are not JSON are skipped."""
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
    return [timed for timed in ([r for r in requests(launch) if r.get("timestamp")] for launch in found) if timed]


def conductor(run):
    main = run_dir.main_tree_from_files(os.getcwd())
    restarts = event_log.events(run_dir.worktree(main, run), "conductor-restart", skip_unreadable=True)
    if not restarts:
        return None
    log = run_dir.main_file(main, "conductor-%s.log" % run)
    with open(log) as f:
        relaunches = launches(f)
    rows = []
    measured = []
    for restart in restarts:
        launch = next((l for l in relaunches if _epoch(l[0]["timestamp"]) >= restart["ts"]), None)
        at = time.strftime(role_state.STAMP, time.localtime(restart["ts"]))
        rows.append((at, cost(launch[:1]) if launch else None, per_request(launch) if launch else None))
        measured += (launch or [])[:1]
    sources = "K and g from %s at the conductor-restart events of %s" % (log, event_log.path(run_dir.worktree(main, run)))
    return rows, measured, sources, "VERI_RESET_GROWTH_CONDUCTOR", tunables.get("VERI_RESET_GROWTH_CONDUCTOR")


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
    if argv == ["dev"]:
        measures = dev(lane)
    elif len(argv) == 2 and argv[0] == "conductor" and lane is None:
        measures = conductor(argv[1])
    else:
        raise Failure(USAGE)
    if measures is None:
        return 3
    rows, measured, sources, knob, value = measures
    for at, k, g in rows:
        print("%s K=%s g=%s" % (at, _figure(k), _figure(g)))
    k = _median(row[1] for row in rows)
    g = _median(row[2] for row in rows)
    r = cache_read_rate(measured)
    best = None if None in (k, g, r) else math.sqrt(2 * k * g / r)
    print("median K=%s g=%s r=%s optimum=%s %s=%s" % (_figure(k), _figure(g), "unknown" if r is None else "%g" % r,
                                                     _figure(best), knob, value))
    print("source: %s; rates from veri/prices.py; %s from the environment or its default" % (sources, knob))
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
