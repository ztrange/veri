"""metrics.sh's report, rendered in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import contextlib
import io
import json
import os
import sys
import run_end
import tunables

from event_log import read_events
from ledger import decode_ledger, ledger_path, ledger_steps
from prices import PRICES, cache_write_tokens, family

USAGE = "usage: metrics.sh <issue-number>"


COUNTS = ["attempts", "PASS", "REJECT", "kills"]

STEP_COUNTS = COUNTS + ["retries", "no-verdict"]

BUDGETS = ["revise", "refactor", "stopped"]

CROSSED = "crossed at"

SPLIT = "split"

CELL_MARKS = {"step-over-budget": (CROSSED, "spent"), "step-split": (SPLIT, "at")}
MARK_COLUMNS = [column for column, _ in CELL_MARKS.values()]

KIND = "kind"

TIMES = ["wall s", "API s"]
WALL, API = TIMES

COSTS = [("turns", "num_turns"),
         ("input", "input_tokens"),
         ("output", "output_tokens"),
         ("cache read", "cache_read_input_tokens"),
         ("cache creation", "cache_creation_input_tokens"),
         ("$", "total_cost_usd")]
COST_COLUMNS = [heading for heading, _ in COSTS]

DOLLARS = "$"

REWORK_WALL, REWORK_COST = "rework wall s", "rework $"
WASTE_WALL, WASTE_COST = "waste wall s", "waste $"
LOST_COLUMNS = [REWORK_WALL, REWORK_COST, WASTE_WALL, WASTE_COST]

MONEY = {DOLLARS, REWORK_COST, WASTE_COST}

UNKNOWN = "unknown"

NOT_APPLICABLE = "n/a"

UNBUDGETED_PHASES = {"cover", "transform", "diff"}


TURN_RATES = {"input_tokens": "input", "output_tokens": "output",
              "cache_read_input_tokens": "cache_read"}

CONTEXT_KEYS = ["input_tokens", "cache_read_input_tokens", "cache_creation_input_tokens"]


class TurnRows(list):
    estimated = False

    def __init__(self):
        super().__init__()
        self.session_contexts = []


def main_checkout_file(path, name):
    found = os.path.join(os.path.dirname(path), name)
    if not os.path.exists(found):
        found = os.path.join(os.path.dirname(path), "..", "..", "..", name)
    return found


def conductor_sessions(issue, path):
    sessions = []
    open_rows = []
    open_turns, open_cost, open_priced = 0, 0.0, True
    open_contexts = []
    turn_rows = TurnRows()
    seen_ids = set()
    with contextlib.suppress(OSError):
        with open(main_checkout_file(path, "conductor-%s.log" % issue)) as stream_log:
            for text in stream_log:
                with contextlib.suppress(ValueError):
                    record = json.loads(text)
                    if not isinstance(record, dict):
                        continue
                    if record.get("type") == "result":
                        sessions.append(record)
                        total = record.get("total_cost_usd")
                        if open_rows and open_priced and total is not None:
                            share = (total - sum(base for _, base in open_rows)) / len(open_rows)
                            running, shown = 0.0, 0
                            for position, base in open_rows:
                                running += base + share
                                cents = round(running * 100) - shown
                                shown += cents
                                turn_rows[position][1] = "$%.2f" % (cents / 100)
                            turn_rows.estimated = True
                        open_rows = []
                        open_turns, open_cost, open_priced = 0, 0.0, True
                        if open_contexts:
                            turn_rows.session_contexts.append(open_contexts)
                        open_contexts = []
                    elif record.get("type") == "assistant":
                        message = record.get("message") or {}
                        usage = message.get("usage") or {}
                        if message.get("id") is not None:
                            if message["id"] in seen_ids:
                                continue
                            seen_ids.add(message["id"])
                        open_turns += 1
                        context = sum((usage.get(key) or 0) for key in CONTEXT_KEYS)
                        open_contexts.append(context)
                        model_name = message.get("model") or ""
                        model_family = family(model_name) or ("opus" if not model_name else None)
                        if model_family is None:
                            open_priced = False
                            turn_rows.append([str(len(turn_rows) + 1), "unpriced", str(context)])
                            continue
                        prices = PRICES[model_family]
                        cache_write_dollars = sum(tokens * prices[rate] / 1e6
                                                  for rate, tokens in cache_write_tokens(usage).items())
                        output_dollars = (usage.get("output_tokens") or 0) * prices["output"] / 1e6
                        turn_dollars = sum((usage.get(key) or 0) * prices[rate] / 1e6
                                           for key, rate in TURN_RATES.items()) + cache_write_dollars
                        open_cost += turn_dollars
                        base_dollars = turn_dollars - output_dollars
                        open_rows.append((len(turn_rows), base_dollars))
                        turn_rows.append([str(len(turn_rows) + 1), "$%.2f" % base_dollars, str(context)])
        if open_turns:
            sessions.append({"total_cost_usd": open_cost if open_priced else None, "num_turns": open_turns, "open": True})
        if open_contexts:
            turn_rows.session_contexts.append(open_contexts)
    return sessions, turn_rows


def render(issue, path, ledger):
    def known(number):
        return UNKNOWN if number is None else "%d" % number

    def counted(total):
        return total or None

    def span(start, end):
        return None if start is None or end is None else end - start

    def reading(mark, clock):
        if mark is None or (clock == "awake" and not clocked):
            return None
        return mark.get(clock)

    def wall_and_awake_spans(start, end):
        return (span(reading(start, "ts"), reading(end, "ts")),
                span(reading(start, "awake"), reading(end, "awake")))

    def awake_span_or_wall(start, end):
        wall, awake = wall_and_awake_spans(start, end)
        return wall if awake is None or wall < awake else awake

    def planned_steps(path):
        try:
            with open(path, "rb") as f:
                text = decode_ledger(f.read())
        except OSError:
            return None, 0
        steps = ledger_steps(text)
        records = "".join("\t".join(record) + "\n" for record in steps)
        full_suite = sum(1 for record in steps if record[1] == "done" and record[2] == "full-suite")
        return counted(len(records.splitlines())), full_suite

    counts = {}
    steps = {}

    PHASE_COLUMNS = COUNTS + TIMES + COST_COLUMNS
    STEP_COLUMNS = STEP_COUNTS + TIMES + COST_COLUMNS

    lost = {}

    ROLES = ("developer", "verifier")
    by_model = {}

    spent = {}

    def step_mark(step):
        return spent.setdefault(step, {})

    passes = {}
    open_passes = {}

    def open_pass(step):
        return open_passes.setdefault(step, {"verdict": "", "revise": 0, WALL: 0, DOLLARS: 0.0})

    def settle_pass(step, current):
        if current["verdict"] == "PASS" and current.get("marked"):
            open_passes.pop(step)

    attempts_spent = {}

    rejected = []
    recovered = set()

    tier_runs = {}

    totals = {"total": dict.fromkeys(COST_COLUMNS, 0)}

    conductor_counted = False

    def row_in(table, key, columns):
        return table.setdefault(key, dict.fromkeys(columns, 0))

    def tally(table, key, columns, count):
        row_in(table, key, columns)[count] += 1

    def model_row(line):
        actor = line.get("actor")
        if actor not in ROLES:
            return None
        attempt = (line.get("step", ""), line.get("phase", ""), line.get("attempt", ""), actor)
        return row_in(by_model, (actor, models.get(attempt, "")), PHASE_COLUMNS)

    def rows_for(phase, step, line):
        rows = [r for r in [model_row(line)] if r is not None]
        if phase:
            rows.append(row_in(counts, phase, PHASE_COLUMNS))
        if step:
            rows.append(row_in(steps, step, STEP_COLUMNS))
        return rows

    def add_seconds(phase, step, line, column, seconds):
        for row_of in rows_for(phase, step, line):
            row_of[column] += seconds

    def attempt_in(phase, step, attempt):
        if not phase or not step:
            return None
        return attempts_spent.setdefault((step, phase, attempt), {WALL: 0, DOLLARS: 0.0})

    def add_cost(phase, step, line):
        rows = rows_for(phase, step, line) + [totals["total"]]
        for heading, field in COSTS:
            reported = line.get(field) or 0
            amount = float(reported) if heading in MONEY else int(reported)
            for row_of in rows:
                row_of[heading] += amount

    opening = None

    structural = None

    launched = {}

    marks = read_events(path)
    clocked = bool(marks) and all("awake" in mark for mark in marks if "ts" in mark)
    models = {(mark.get("step", ""), mark.get("phase", ""), mark.get("attempt", ""), mark.get("actor")):
              mark["model"] for mark in marks if mark.get("event") == "usage" and "model" in mark}

    for line in marks:
        event = line.get("event", "")
        step = line.get("step", "")
        phase = line.get("phase", "")
        ts = line.get("ts")
        if opening is None or event == "resume":
            opening = line
        if event == "structural-pass":
            structural = line
        if event in ("step-start", "step-done") and step:
            step_mark(step)[event] = line
            if event == "step-done":
                recovered.add(step)
            continue
        if event == "test-run":
            seconds = line.get("seconds")
            if seconds not in (None, ""):
                tier_runs.setdefault(line.get("tier") or UNKNOWN, []).append(str(seconds))
            continue
        if event == "pin" and step:
            recovered.add(step)
            step_mark(step)[KIND] = "pin"
        elif event == "verdict" and phase == "pin" and line.get("verdict") == "PASS" and step:
            step_mark(step).setdefault(KIND, "already-satisfied")
        attempt_no = line.get("attempt", "")
        attempt = attempt_in(phase, step, attempt_no)
        if event == "launch":
            launched[(step, phase, attempt_no)] = line
            step_mark(step).setdefault("leaf phases", set()).add(phase)
        if event == "exit":
            awake = span(reading(launched.get((step, phase, attempt_no)), "awake"),
                         reading(line, "awake"))
            seconds = int(awake if awake is not None else (line.get("secs") or 0))
            add_seconds(phase, step, line, "wall s", seconds)
            if attempt is not None:
                attempt[WALL] += seconds
            if phase == "refactor":
                open_pass(step)[WALL] += seconds
        elif event == "usage":
            add_seconds(phase, step, line, "API s",
                        int(line.get("duration_api_ms") or 0) // 1000)
            add_cost(phase, step, line)
            dollars = float(line.get("total_cost_usd") or 0)
            if attempt is not None:
                attempt[DOLLARS] += dollars
            if phase == "refactor":
                open_pass(step)[DOLLARS] += dollars
            if line.get("actor") == "conductor":
                conductor_counted = True
        elif event == "verdict" and line.get("verdict") == "REJECT" and attempt is not None:
            rejected.append((step, phase, attempt))
        if event == "verdict" and phase == "refactor":
            current = open_pass(step)
            current["verdict"] = line.get("verdict", "")
            settle_pass(step, current)
        if event == "verify-refactor-skipped" and step:
            open_pass(step)["verdict"] = "skipped"
        if event == "revise" and step:
            per_phase = step_mark(step).setdefault("revise phases", {})
            per_phase[phase] = (per_phase.get(phase, (0, ""))[0] + 1, line.get("budget", ""))
            if phase == "refactor":
                open_pass(step)["revise"] += 1
            continue
        if event == "reroute" and step and line.get("kind") == "repair":
            step_mark(step).setdefault("revise phases", {}).setdefault(phase, (0, line.get("budget", "")))
        if event == "refactor" and step:
            mark = step_mark(step)
            mark["transforms"] = line.get("transforms", "")
            mark["refactor"] = line.get("budget", "")
            mark["stopped"] = line.get("stopped", "")
            current = open_pass(step)
            passes[(step, line.get("pass", ""))] = (line, current)
            current["marked"] = True
            settle_pass(step, current)
            continue
        if event in CELL_MARKS and step:
            column, attribute = CELL_MARKS[event]
            step_mark(step)[column] = line.get(attribute, "")
            continue
        if event == "launch":
            count = "attempts"
        elif event == "verdict" and line.get("verdict") in ("PASS", "REJECT"):
            count = line["verdict"]
        elif event == "exit" and line.get("status") == "2":
            count = "kills"
        elif event == "retry":
            count = "retries"
        elif event == "relaunch" and line.get("cause") == "no-verdict":
            count = "no-verdict"
        else:
            continue
        if phase and count in COUNTS:
            tally(counts, phase, PHASE_COLUMNS, count)
        model = model_row(line) if count in COUNTS else None
        if model is not None:
            model[count] += 1
        if step:
            tally(steps, step, STEP_COLUMNS, count)

    for phase in counts:
        row_in(lost, phase, LOST_COLUMNS)

    def lose(phase, attempt, wall_column, cost_column):
        row_of = row_in(lost, phase, LOST_COLUMNS)
        row_of[wall_column] += attempt[WALL]
        row_of[cost_column] += attempt[DOLLARS]

    for step, phase, attempt in rejected:
        if step in recovered:
            lose(phase, attempt, REWORK_WALL, REWORK_COST)

    for (step, phase, _attempt_no), attempt in attempts_spent.items():
        if step not in recovered:
            lose(phase, attempt, WASTE_WALL, WASTE_COST)

    def row(cells):
        print("| " + " | ".join(cells) + " |")

    def figure(column, value):
        return "%.2f" % value if column in MONEY else "%d" % value

    def figures(row_counts, columns):
        return [figure(c, row_counts[c]) for c in columns]

    def refactor_spent(mark):
        return "%s/%s" % (mark["transforms"], mark.get("budget", "?"))

    def step_wall(mark):
        return known(awake_span_or_wall(mark.get("step-start"), mark.get("step-done")))

    def budget_cells(mark):
        phases = mark.get("revise phases", {})
        leaf_phases = mark.get("leaf phases")
        if leaf_phases and leaf_phases <= UNBUDGETED_PHASES and not phases and not mark.get("refactor"):
            return [NOT_APPLICABLE] * len(BUDGETS)
        named = len(phases) > 1
        revise = ", ".join(("%s " % phase if named else "") + "%d/%s" % (count, budget or "?")
                           for phase, (count, budget) in phases.items()) or UNKNOWN
        if mark.get("refactor"):
            refactor = "%s/%s" % (mark.get("transforms") or "?", mark["refactor"])
        else:
            refactor = UNKNOWN
        return [revise, refactor, mark.get("stopped") or UNKNOWN]

    def step_cells(step):
        mark = spent.get(step, {})
        return [step_wall(mark)] + budget_cells(mark) + [mark.get(column, "") for column in MARK_COLUMNS] + [mark.get(KIND, "full")]

    def heading_block(heading):
        print()
        print(heading)
        print()

    def table_head(heading, key_column, columns, aligns):
        heading_block(heading)
        row([key_column] + columns)
        row(["---"] + aligns)

    def section(heading, key_column, columns, table, text=None):
        headings, cells_for = text or ((), None)
        headings = list(headings)
        table_head(heading, key_column, columns + headings,
                   ["---:"] * len(columns) + ["---"] * len(headings))
        for key, row_counts in table.items():
            cells = [key] + figures(row_counts, columns)
            if heading == "#### Total" and total_estimated:
                at = columns.index(DOLLARS) + 1
                cells[at] += " (estimate)"
            row(cells + (cells_for(key) if cells_for else []))

    def tier_section(heading, key_column):
        width = max([len(runs) for runs in tier_runs.values()] or [0])
        table_head(heading, key_column,
                   ["run %d s" % (i + 1) for i in range(width)], ["---:"] * width)
        for tier, runs in tier_runs.items():
            row([tier] + runs + [""] * (width - len(runs)))

    ended, cause, ending = run_end.run_end(os.path.dirname(os.path.dirname(os.path.abspath(path))))
    ending = ending or None
    print("### 📊 Metrics — issue %s" % issue)
    print()
    wall_span, awake_span = wall_and_awake_spans(opening, ending)
    print("Wall time for the issue: %s s, from the last `resume`, or the first event of the log when "
          "there is none, to the mark that ended the run."
          % known(awake_span_or_wall(opening, ending)))
    if awake_span is not None and wall_span is not None:
        print("Seconds the machine was not running inside that span: %s s, excluded from it."
              % max(0, wall_span - awake_span))
    if not clocked:
        print("Every figure in this report is wall-clock: the log carries no awake-clock reading, "
              "so time the machine spent asleep is counted in them.")
    planned, full_suite = planned_steps(ledger)
    print("Steps done: %s of %s planned."
          % (known(counted(len(recovered) + full_suite)), known(planned)))
    if not ended:
        print("Outcome: none yet — the run is still going.")
    elif ending is None and cause == "usage-limit":
        print("Outcome: the run hit a usage limit.")
    elif ending is None and cause == "killed":
        print("Outcome: the run was killed — its conductor's latest launch left no result.")
    elif ending is None:
        print("Outcome: %s — the log carries no mark ending the run." % UNKNOWN)
    elif ending.get("event") == "done":
        print("Outcome: the run landed — its draft PR is %s."
              % (ending.get("pr") or UNKNOWN))
    elif ending.get("event") == "stop":
        print("Outcome: the run was stopped — mode %s, at %s."
              % (ending.get("mode") or UNKNOWN, ending.get("at") or UNKNOWN))
    else:
        print("Outcome: the run bailed — %s, a %s failure."
              % (ending.get("cause") or UNKNOWN, ending.get("classification") or UNKNOWN))
    print("Lane: %s" % (tunables.read("VERI_LABEL", "ready-for-agent", unless_empty="ready-for-agent")))
    sessions, turn_rows = [], []
    total_estimated = False
    if not conductor_counted:
        sessions, turn_rows = conductor_sessions(issue, path)
    if sessions:
        priced = not any(r.get("total_cost_usd", 0) is None for r in sessions)
        some_priced = any(r.get("total_cost_usd") is not None for r in sessions)
        print("Cost is every leaf of the run, and the conductor own spending." if priced else
              "Cost is every leaf of the run; the total row includes the priced sessions' conductor spending and leaves out the unpriced ones."
              if some_priced else
              "Cost is every leaf of the run; the total row excludes the conductor own spending, which is unpriced.")
        spend = sum(r.get("total_cost_usd") or 0 for r in sessions)
        totals["total"][DOLLARS] += spend
        model = ""
        with contextlib.suppress(OSError):
            with open(main_checkout_file(path, "issue-%s-conductor-model" % issue)) as recorded:
                model = recorded.read().strip()
        total_estimated = any(r.get("open") for r in sessions)
        print("Conductor own spending: %s over %d turns, in %d sessions%s%s."
              % ("$%.2f" % spend if priced else "unpriced",
                 sum(r.get("num_turns") or 0 for r in sessions), len(sessions),
                 ", on %s" % model if model else "",
                 " (estimate)" if total_estimated else ""))
        if total_estimated:
            print("The Conductor own spending figure is estimated: the output tokens of a session without a "
                  "result record are not yet known.")
        for contexts in turn_rows.session_contexts:
            print("Conductor context: first turn %d tokens, largest %d tokens" % (contexts[0], max(contexts)))
    else:
        print("Cost is every leaf of the run, and the conductor own %s."
              % ("closing accounting with them, which this log carries"
                 if conductor_counted else
                 "spending is not in it: this log carries no usage record of the conductor own"))
    if turn_rows:
        if turn_rows.estimated:
            print("The per-turn dollars are estimated: each turn's non-output usage priced, plus a share of the "
                  "result record's remaining cost.")
        table_head("#### Conductor per turn", "turn", ["dollars", "context"], ["---:", "---:"])
        for turn_row in turn_rows:
            row(turn_row)
    if models:
        print("Models requested: %s; models that answered: %s."
              % (", ".join("%s %s" % (knob, tunables.read(knob) or "unset")
                           for knob in ["VERI_MODEL", "VERI_MODEL_DEVELOPER", "VERI_MODEL_VERIFIER", "VERI_MODEL_REVISE"]),
                 ", ".join(sorted({m for answered in models.values() for m in answered.split(",") if m}))))
    section("#### By phase", "phase", PHASE_COLUMNS, counts)
    if models or any(mark.get("event") == "launch" and "model" in mark for mark in marks):
        table_head("#### By model", "role", ["model"] + PHASE_COLUMNS, ["---"] + ["---:"] * len(PHASE_COLUMNS))
        for (role, model), row_counts in by_model.items():
            row([role, model or "not recorded"] + figures(row_counts, PHASE_COLUMNS))
    section("#### Rework and waste, by phase", "phase", LOST_COLUMNS, lost)
    section("#### By step", "step", STEP_COUNTS + [API] + COST_COLUMNS, steps,
            ([WALL] + BUDGETS + MARK_COLUMNS + [KIND], step_cells))
    print()
    print("The figure comparable across runs is turns, the same measurement on any model; dollars "
          "are not comparable, the same measurement only at the same VERI_MODEL, "
          "VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.")
    if passes:
        table_head("#### By refactor pass", "step", ["pass", "refactor", "stopped", "verdict", "revise", WALL, DOLLARS],
                   ["---:", "---:", "---", "---", "---:", "---:", "---:"])
        for (step, index), (mark, spent_by) in passes.items():
            row([step, index, refactor_spent(mark), mark["stopped"],
                 spent_by["verdict"], str(spent_by["revise"])] + figures(spent_by, [WALL, DOLLARS]))
    if structural is None and ending is not None and ending.get("event") == "done":
        structural = {"stopped": "not marked"}
    if structural is not None:
        stopped = structural.get("stopped", "?")
        if "transforms" not in structural:
            heading_block("#### Structural pass")
            print("Stopped: %s" % stopped)
        else:
            table_head("#### Structural pass", "pass", ["refactor", "stopped"], ["---:", "---"])
            row(["issue", refactor_spent(structural), stopped])
        inconsistent = None
        if "stopped" not in structural:
            inconsistent = "the mark carries no stopped"
        elif "transforms" in structural:
            if "budget" not in structural:
                inconsistent = "transforms=%s without a budget" % structural["transforms"]
            elif structural["stopped"] == "budget-spent" and int(structural["transforms"]) < int(structural["budget"]):
                inconsistent = ("stopped=budget-spent, but transforms=%s is below budget=%s"
                                % (structural["transforms"], structural["budget"]))
            elif structural["stopped"] not in ("candidates-done", "budget-spent", "nothing-structural"):
                inconsistent = ("stopped=%s is not one of candidates-done, budget-spent, nothing-structural"
                                % structural["stopped"])
        if inconsistent is not None:
            print()
            print("Inconsistent mark: %s" % inconsistent)
    tier_section("#### Test-command seconds, by tier", "tier")
    section("#### Total", "run", COST_COLUMNS, totals)


def report(issue, events_path, ledger_path, stream=None):
    out = io.StringIO() if stream is None else stream
    with contextlib.redirect_stdout(out):
        render(issue, events_path, ledger_path)
    return out.getvalue() if stream is None else None


def main(argv):
    if not argv or not argv[0]:
        sys.stderr.write(USAGE + "\n")
        return 2
    issue = argv[0]
    report(issue, ".tdd/events.jsonl", ledger_path(".", issue), stream=sys.stdout)
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
