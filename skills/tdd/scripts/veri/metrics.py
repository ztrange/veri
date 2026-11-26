"""metrics.sh's report, rendered in-process, in two stages.

    fold(issue, events_path, ledger_path) -> Fold    what the report says: reads the event log, the ledger,
                                                     the conductor stream log, the transcripts and the
                                                     environment; computes every number; prints nothing
    layout(fold)                                     how it is printed: reads only the Fold
    render(...) is layout(fold(...)); report() captures it as text, main() is the CLI.

A Fold holds plain data. Tables are {key: {column: number}} dicts (phases, by_model, lost, steps; `total` is
one such row), columns named by PHASE_COLUMNS, STEP_COLUMNS, LOST_COLUMNS, COST_COLUMNS. Fields:
  header     issue, clocked, issue_wall, asleep, steps_done, planned, ended, cause, ending, lane, flaked,
             pinned, model_knobs, models
  tables     phases, leaves, by_model (+ by_model_shown), lost, steps (+ step_marks, step_walls), tier_runs,
             adjudications, switched_off, switched_off_by, total, green_rejects (+ green_reject_routes, green_reject_checks),
             launch_costs (+ launch_cost_missing), gradings, first_tries, revise_green, runs, stages, reject_outcomes, former
  refactor   passes (one dict per pass), structural (+ structural_marked, structural_inconsistency),
             refactor_totals
  conductor  conductor_counted, sessions, turn_rows (+ .families, .session_contexts, .estimated),
             conductor_spend, conductor_turns, conductor_model, conductor_priced, conductor_some_priced,
             conductor_estimated, conductor_by_phase, operator_sessions
  raw        marks (the event log)
A number that cannot be known is None; layout prints it as "unknown" or "?"."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import collections
import contextlib
import dataclasses
import datetime
import io
import json
import os
import re
import sys
import tempfile

import run_dir
import run_end
import run_pins
import run_records
import tunables
from event_log import read_events
from ledger import decode_ledger, ledger_steps
from prices import PRICES, cache_write_tokens, family

FAMILIES_TOTAL = "Total"
COMMENT_FAMILIES = [
    ("✅ Step done", "✅ Step done"),
    ("✅ Done", "✅ Done"),
    ("🔴 Red", "🔴 Red|🔎 verify-red"),
    ("🟢 Green", "🟢 Green"),
    ("🛠️ Refactor", "🛠️ Refactor"),
    ("🔎 verify-green", "🔎 verify-green(?! \\(revised\\))"),
    ("🔎 verify-refactor", "🔎 verify-refactor(?! \\(revised\\))"),
    ("🔎 verify-<phase> (revised)", "🔎 verify-[\\w-]+ \\(revised\\)"),
    ("🗺️ Plan", "🗺️ Plan"),
    ("🗺️ verify-plan", "🗺️ verify-plan"),
    ("▶️ Resuming", "▶️ Resuming"),
    ("⛔ Bailed", "⛔ Bailed"),
    ("⏹️ Stopped", "⏹️ Stopped"),
]

USAGE = "usage: metrics.sh <issue-number> [--json]"
JSON = "--json"
# the skip events counted on the "Verifiers switched off:" line beside refactor's own count
SWITCHED_OFF_EVENTS = {"verify-%s-skipped" % phase: phase for phase in ("branch", "diff", "green", "pin", "red")}


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

FIRST_TURN = [("first-turn cache creation", "first_turn_cache_creation_input_tokens"),
              ("first-turn cache read", "first_turn_cache_read_input_tokens"),
              ("first-turn input", "first_turn_input_tokens")]
LEAVES = "leaves"
LAUNCH_COLUMNS = [LEAVES] + [heading for heading, _ in FIRST_TURN]

REWORK_WALL, REWORK_COST = "rework wall s", "rework $"
WASTE_WALL, WASTE_COST = "waste wall s", "waste $"
LOST_COLUMNS = [REWORK_WALL, REWORK_COST, WASTE_WALL, WASTE_COST]

MONEY = {DOLLARS, REWORK_COST, WASTE_COST}

PHASE_COLUMNS = COUNTS + TIMES + COST_COLUMNS
STEP_COLUMNS = STEP_COUNTS + TIMES + COST_COLUMNS

ROLES = ("developer", "verifier", "adjudicator")

FIRST_TRY_KEYS = ("verified_steps", "first_try_pass", "revise_cycles")

UNNAMED = "unnamed"

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
        self.turns = []         # [epoch seconds or None, output tokens, dollars or None] per turn, for by_phase
        self.families = {name: [0, 0, 0.0] for name in [n for n, _ in COMMENT_FAMILIES] + [FAMILIES_TOTAL]}


def main_checkout_file(path, name):
    found = os.path.join(os.path.dirname(path), name)
    if not os.path.exists(found):
        found = os.path.join(os.path.dirname(path), "..", "..", "..", name)
    return found


def pin_roots(run="."):
    """Where a run's pin files may sit: the run's own `.tdd/`, then the main working tree's."""
    main = run_dir.main_of_worktree(os.path.abspath(run))
    return (run,) if main is None else (run, main)


def count_families(turn_rows, open_turn_rows, result_output):
    for names, model_family, own_tokens in open_turn_rows:
        output_tokens = own_tokens if result_output is None else result_output // len(open_turn_rows)
        for name in names + ([FAMILIES_TOTAL] if names else []):
            turn_rows.families[name][0] += 1
            turn_rows.families[name][1] += output_tokens
            if model_family:
                turn_rows.families[name][2] += output_tokens * PRICES[model_family]["output"] / 1e6
    open_turn_rows.clear()


def conductor_sessions(issue, path):
    """The conductor's sessions read off its stream log, and its turns as `TurnRows`. A session ends at its `result`
    record; one a `system` `init` record or the log's end finds without one (killed, or still going) is kept as an
    open session priced from its own turns' usage."""
    sessions = []
    turn_rows = TurnRows()
    seen_ids = {}
    opened = {}

    def start():
        opened.update(rows=[], turns=0, cost=0.0, priced=True, contexts=[], turns_of=[], families=[])

    def close_unended():
        count_families(turn_rows, opened["families"], None)
        turn_rows.turns += [[at, own, dollars if opened["priced"] else None] for at, own, dollars, _base in opened["turns_of"]]
        if opened["turns"]:
            sessions.append({"total_cost_usd": opened["cost"] if opened["priced"] else None,
                             "num_turns": opened["turns"], "open": True})
        if opened["contexts"]:
            turn_rows.session_contexts.append(opened["contexts"])
        start()

    start()
    with contextlib.suppress(OSError):
        with open(main_checkout_file(path, "conductor-%s.log" % issue)) as stream_log:
            for text in stream_log:
                with contextlib.suppress(ValueError):
                    record = json.loads(text)
                    if not isinstance(record, dict):
                        continue
                    if record.get("type") == "system" and record.get("subtype") == "init":
                        close_unended()
                    elif record.get("type") == "result":
                        shown_turns = len(opened["turns_of"])
                        counted_turns = record.get("num_turns")
                        # a session's turns: the more of those its result counts and those the log shows, so no
                        # turn by_phase attributes is missing from the per-run count
                        turns = max(counted_turns, shown_turns) if isinstance(counted_turns, int) else shown_turns
                        session = record if turns == counted_turns else dict(record, num_turns=turns)
                        woken = record.get("session_id")
                        if woken is not None and sessions and sessions[-1].get("session_id") == woken:
                            # a wake of the same session (#4599): its total is cumulative, its turns its own
                            earlier = sessions.pop()
                            session = dict(session, num_turns=turns + (earlier.get("num_turns") or 0))
                            if isinstance(record.get("total_cost_usd"), (int, float)) and \
                                    isinstance(earlier.get("total_cost_usd"), (int, float)):
                                record = dict(record, total_cost_usd=record["total_cost_usd"] - earlier["total_cost_usd"])
                        sessions.append(session)
                        count_families(turn_rows, opened["families"], (record.get("usage") or {}).get("output_tokens"))
                        total = record.get("total_cost_usd")
                        open_rows = opened["rows"]
                        if open_rows and opened["priced"] and total is not None:
                            share = (total - sum(base for _, base in open_rows)) / len(open_rows)
                            running, shown = 0.0, 0
                            for position, base in open_rows:
                                running += base + share
                                cents = round(running * 100) - shown
                                shown += cents
                                turn_rows[position][1] = "$%.2f" % (cents / 100)
                            turn_rows.estimated = True
                        turn_rows.turns += closed_turns(opened["turns_of"], record, opened["priced"])
                        if opened["contexts"]:
                            turn_rows.session_contexts.append(opened["contexts"])
                        start()
                        seen_ids = {key: kept for key, kept in seen_ids.items() if kept}
                    elif record.get("type") == "assistant":
                        message = record.get("message") or {}
                        usage = message.get("usage") or {}
                        calls = json.dumps([block.get("input") for block in message.get("content") or []
                                            if isinstance(block, dict) and block.get("type") == "tool_use"],
                                           ensure_ascii=False)
                        names = [name for name, pattern in COMMENT_FAMILIES if re.search(pattern, calls)]
                        if message.get("id") is not None:
                            earlier = seen_ids.get(message["id"])
                            flushed = not any(row[0] is earlier for row in opened["families"])
                            if earlier is not None and not (names and flushed and (not set(names) & set(earlier) or set(names) == set(earlier))):
                                added = [n for n in names if n not in earlier]
                                earlier.extend(added)
                                if flushed:
                                    count_families(turn_rows, [(added, None, 0)], None)
                                continue
                            seen_ids[message["id"]] = names
                        opened["turns"] += 1
                        model_name = message.get("model") or ""
                        model_family = family(model_name) or ("opus" if not model_name else None)
                        opened["families"].append((names, model_family, usage.get("output_tokens") or 0))
                        context = sum((usage.get(key) or 0) for key in CONTEXT_KEYS)
                        opened["contexts"].append(context)
                        own_output = usage.get("output_tokens") or 0
                        if model_family is None:
                            opened["turns_of"].append([moment(record.get("timestamp")), own_output, None, None])
                            opened["priced"] = False
                            turn_rows.append([str(len(turn_rows) + 1), "unpriced", str(context)])
                            continue
                        prices = PRICES[model_family]
                        output_dollars = (usage.get("output_tokens") or 0) * prices["output"] / 1e6
                        turn_dollars = usage_dollars(usage, prices)
                        opened["cost"] += turn_dollars
                        base_dollars = turn_dollars - output_dollars
                        opened["turns_of"].append([moment(record.get("timestamp")), own_output, turn_dollars, base_dollars])
                        opened["rows"].append((len(turn_rows), base_dollars))
                        turn_rows.append([str(len(turn_rows) + 1), "$%.2f" % base_dollars, str(context)])
        close_unended()
    return sessions, turn_rows


def moment(stamp):
    """An ISO `timestamp` as epoch seconds, a zoneless one read as UTC; None when it is missing or unreadable."""
    try:
        at = datetime.datetime.fromisoformat(stamp)
    except (TypeError, ValueError):
        return None
    return (at if at.tzinfo else at.replace(tzinfo=datetime.timezone.utc)).timestamp()


def closed_turns(seen, result, priced):
    """[at, output tokens, dollars] per turn of a session its `result` record closes: `seen` holds each turn the log
    showed as [at, own output tokens, dollars, non-output dollars]. A turn's output is the result's output split evenly,
    the last turn taking the remainder (its own when the result carries none) and its dollars its non-output usage plus an even share of the rest of the
    result's cost, None when the session carries no price. A turn the result counts but no record showed is untimed,
    with no output or cost of its own (both shared over the turns shown), or all of them when none was shown."""
    total, output = result.get("total_cost_usd"), (result.get("usage") or {}).get("output_tokens")
    priced = priced and isinstance(total, (int, float))
    share = (total - sum(base for *_, base in seen)) / len(seen) if priced and seen else 0.0
    turns = [[at, own if output is None else output // len(seen), base + share if priced else None]
             for at, own, _dollars, base in seen]
    if turns and output is not None:
        turns[-1][1] += output % len(seen)
    unseen = result.get("num_turns") if isinstance(result.get("num_turns"), int) else 0
    for extra in range(unseen - len(seen)):
        alone = not seen and not extra
        turns.append([None, (output or 0) if alone else 0, (total if alone else 0.0) if priced else None])
    return turns


def leaf_and_stage_windows(marks):
    """(start, end, key) per ended window of the journal (PRD 035.6, D10): a leaf's `launch` to its `exit`, paired by
    the leaf's `name`, or by step, phase, attempt and actor when the exit names none, keyed by leaf kind; a stage's
    `stage-start` to its `stage-end`, keyed by stage. A window with no end (a killed leaf or stage) is none."""
    windows, leaves, stages = [], [], {}
    for line in marks:
        event, at = line.get("event"), line.get("ts")
        if not isinstance(at, (int, float)):
            continue
        context = tuple(line.get(key, "") for key in ("step", "phase", "attempt", "actor"))
        if event == "launch":
            leaves.append((at, line.get("name") or "", context))
        elif event == "exit":
            name = line.get("name") or ""
            match = next((opened for opened in reversed(leaves)
                          if (opened[1] == name if name else opened[2] == context)), None)
            if match is not None:
                leaves.remove(match)
                windows.append((match[0], at, re.sub(r"-[0-9]+$", "", match[1]) if match[1] else UNNAMED))
        elif event == "stage-start" and line.get("stage"):
            stages[line["stage"]] = at
        elif event == "stage-end" and line.get("stage") in stages:
            windows.append((stages.pop(line["stage"]), at, line["stage"]))
    return windows


BY_PHASE_KEYS = ("turns", "output_tokens", "cost_usd")


def conductor_by_phase(marks, turns):
    """The conductor's turns per window (D10): each timed turn under the innermost window holding its time (the
    latest to start), else `between`; an untimed one under `untimed`. An entry's cost is None when any of its turns
    carries no price."""
    windows = leaf_and_stage_windows(marks)
    by_phase = {}
    for at, output, dollars in turns:
        holding = [window for window in windows if at is not None and window[0] <= at <= window[1]]
        key = "untimed" if at is None else max(holding, key=lambda w: (w[0], -w[1]))[2] if holding else "between"
        entry = by_phase.setdefault(key, {"turns": 0, "output_tokens": 0, "cost_usd": 0.0})
        entry["turns"] += 1
        entry["output_tokens"] += output
        entry["cost_usd"] = None if dollars is None or entry["cost_usd"] is None else entry["cost_usd"] + dollars
    return by_phase


def span(start, end):
    """Seconds from `start` to `end`; None when either is missing."""
    return None if start is None or end is None else end - start


def counted(total):
    """`total`, or None when it is zero: a count of nothing is unknown, not 0."""
    return total or None


def reading(mark, clock, clocked):
    """The `clock` ("ts" or "awake") reading of an event mark; None when the mark is missing or, for
    "awake", when the log carries no awake clock (`clocked` is False)."""
    if mark is None or (clock == "awake" and not clocked):
        return None
    return mark.get(clock)


def wall_and_awake_spans(start, end, clocked):
    """(wall seconds, awake seconds) between two event marks, each None when it cannot be read."""
    return (span(reading(start, "ts", clocked), reading(end, "ts", clocked)),
            span(reading(start, "awake", clocked), reading(end, "awake", clocked)))


def awake_span_or_wall(start, end, clocked):
    """Seconds between two event marks on the awake clock, or on the wall clock when that is shorter
    or the awake clock is unreadable; None when neither can be read."""
    wall, awake = wall_and_awake_spans(start, end, clocked)
    return wall if awake is None or wall < awake else awake


def planned_steps(path):
    """(number of steps the ledger at `path` plans, or None; number of ticked full-suite lines; number of done steps not still refactor pending)."""
    try:
        with open(path, "rb") as f:
            text = decode_ledger(f.read())
    except OSError:
        return None, 0, 0
    steps = ledger_steps(text)
    records = "".join("\t".join(record) + "\n" for record in steps)
    full_suite = sum(1 for record in steps if record.state == "done" and record.kind == "full-suite")
    done = sum(1 for record in steps if record.state == "done" and record.pending == "0")
    return counted(len(records.splitlines())), full_suite, done


class _Tally:
    """The event log's tables, accumulated one event at a time by `take`; `fold` reads them off."""

    def __init__(self, models, clocked):
        self.models = models
        self.clocked = clocked
        self.counts = {}
        self.steps = {}
        self.by_model = {}
        self.spent = {}
        self.passes = {}
        self.open_passes = {}
        self.attempts_spent = {}
        self.rejected = []
        self.recovered = set()
        self.tier_runs = {}
        self.total = dict.fromkeys(COST_COLUMNS, 0)
        self.conductor_counted = False
        self.switched_off = 0
        self.switched_off_by = {}
        self.adjudications = {}
        self.opening = None
        self.structural = None
        self.launched = {}
        self.green_rejects = []
        self.launch_costs = {}
        self.launch_cost_missing = 0
        self.gradings = {"count": 0, "PASS": 0, "REJECT": 0, DOLLARS: 0.0, "efforts": set()}
        self.first_verdicts = {}
        self.leaves = {}
        self.launch_names = {}
        self.revise_cycles = collections.Counter()

    def step_mark(self, step):
        return self.spent.setdefault(step, {})

    def open_pass(self, step):
        return self.open_passes.setdefault(step, {"verdict": "", "revise": 0, WALL: 0, DOLLARS: 0.0})

    def settle_pass(self, step, current):
        if current["verdict"] == "PASS" and current.get("marked"):
            self.open_passes.pop(step)

    @staticmethod
    def row_in(table, key, columns):
        return table.setdefault(key, dict.fromkeys(columns, 0))

    def tally(self, table, key, columns, count):
        self.row_in(table, key, columns)[count] += 1

    def model_row(self, line):
        actor = line.get("actor")
        if actor not in ROLES:
            return None
        attempt = (line.get("step", ""), line.get("phase", ""), line.get("attempt", ""), actor)
        return self.row_in(self.by_model, (actor, self.models.get(attempt, "")), PHASE_COLUMNS)

    def leaf_kind(self, line):
        """The kind of the leaf a line is about: its own `name`, else the name of the `launch` sharing its step, phase,
        attempt and actor, less a trailing -<digits>; "unnamed" when neither names one."""
        name = line.get("name") or self.launch_names.get(
            (line.get("step", ""), line.get("phase", ""), line.get("attempt", ""), line.get("actor")))
        return re.sub(r"-[0-9]+$", "", name) if name else UNNAMED

    def rows_for(self, phase, step, line):
        rows = [r for r in [self.model_row(line)] if r is not None]
        if phase:
            rows.append(self.row_in(self.counts, phase, PHASE_COLUMNS))
            rows.append(self.row_in(self.leaves, self.leaf_kind(line), PHASE_COLUMNS))
        if step:
            rows.append(self.row_in(self.steps, step, STEP_COLUMNS))
        return rows

    def add_seconds(self, phase, step, line, column, seconds):
        for row_of in self.rows_for(phase, step, line):
            row_of[column] += seconds

    def attempt_in(self, phase, step, attempt):
        if not phase or not step:
            return None
        return self.attempts_spent.setdefault((step, phase, attempt), {WALL: 0, DOLLARS: 0.0})

    def add_cost(self, phase, step, line):
        rows = self.rows_for(phase, step, line) + [self.total]
        for heading, field in COSTS:
            reported = line.get(field) or 0
            amount = float(reported) if heading in MONEY else int(reported)
            for row_of in rows:
                row_of[heading] += amount

    def route_green_rejects(self, event, step, line):
        """Give each green REJECT still without a route the one this event is: a `reroute` of its step
        (its kind), a `revise` of its step, or any `bail`."""
        for each in self.green_rejects:
            if each[2] is not None:
                continue
            if event == "reroute" and step == each[0]:
                each[2] = line.get("kind", "")
            elif event == "revise" and step == each[0]:
                each[2] = "revise"
            elif event == "bail":
                each[2] = "bail"

    def take(self, line):
        """Fold one event of the log into the tables."""
        event = line.get("event", "")
        step = line.get("step", "")
        phase = line.get("phase", "")
        self.route_green_rejects(event, step, line)
        if event == "verdict" and phase and step and line.get("verdict") in ("PASS", "REJECT"):
            self.first_verdicts.setdefault((phase, step), line["verdict"])
        if event == "revise" and phase:
            self.revise_cycles[phase] += 1
        if self.opening is None or event == "resume":
            self.opening = line
        if event == "structural-pass":
            self.structural = line
        if event in ("step-start", "step-done") and step:
            self.step_mark(step)[event] = line
            if event == "step-done":
                self.recovered.add(step)
            return
        if event == "test-run":
            seconds = line.get("seconds")
            if seconds not in (None, ""):
                self.tier_runs.setdefault(line.get("tier") or UNKNOWN, []).append(str(seconds))
            return
        if event == "pin" and step:
            self.recovered.add(step)
            self.step_mark(step)[KIND] = "pin"
        elif event == "verdict" and phase == "pin" and line.get("verdict") == "PASS" and step:
            self.step_mark(step).setdefault(KIND, "already-satisfied")
        attempt_no = line.get("attempt", "")
        attempt = self.attempt_in(phase, step, attempt_no)
        if event == "launch":
            self.launched[(step, phase, attempt_no)] = line
            self.launch_names[(step, phase, attempt_no, line.get("actor"))] = line.get("name", "")
            self.step_mark(step).setdefault("leaf phases", set()).add(phase)
        if event == "exit":
            awake = span(reading(self.launched.get((step, phase, attempt_no)), "awake", self.clocked),
                         reading(line, "awake", self.clocked))
            seconds = int(awake if awake is not None else (line.get("secs") or 0))
            self.add_seconds(phase, step, line, "wall s", seconds)
            if attempt is not None:
                attempt[WALL] += seconds
            if phase == "refactor":
                self.open_pass(step)[WALL] += seconds
        elif event == "usage":
            self.add_seconds(phase, step, line, "API s",
                             int(line.get("duration_api_ms") or 0) // 1000)
            self.add_cost(phase, step, line)
            dollars = float(line.get("total_cost_usd") or 0)
            if attempt is not None:
                attempt[DOLLARS] += dollars
            if phase == "refactor":
                self.open_pass(step)[DOLLARS] += dollars
            if line.get("actor") == "conductor":
                self.conductor_counted = True
            elif all(field in line for _, field in FIRST_TURN):
                launch = self.row_in(self.launch_costs, (line.get("actor", ""), line.get("model", "")), LAUNCH_COLUMNS)
                launch[LEAVES] += 1
                for heading, field in FIRST_TURN:
                    launch[heading] += int(line[field])
            else:
                self.launch_cost_missing += 1
        elif event == "verdict" and line.get("verdict") == "REJECT" and attempt is not None:
            self.rejected.append((step, phase, attempt))
        if event == "verdict" and phase == "green" and line.get("verdict") == "REJECT":
            self.green_rejects.append([step, attempt_no, None, line.get("check", ""), line.get("reason")])
        if event == "verdict" and phase == "refactor":
            current = self.open_pass(step)
            current["verdict"] = line.get("verdict", "")
            self.settle_pass(step, current)
        if event == "verify-refactor-skipped" and step:
            self.open_pass(step)["verdict"] = "skipped"
            if line.get("reason") == "switched-off":
                self.switched_off += 1
        skipped = SWITCHED_OFF_EVENTS.get(event)
        if skipped and line.get("reason") == "switched-off":
            self.switched_off_by[skipped] = self.switched_off_by.get(skipped, 0) + 1
        if event == "grading":
            gradings = self.gradings
            gradings["count"] += 1
            if line.get("verdict") in ("PASS", "REJECT"):
                gradings[line["verdict"]] += 1
            gradings[DOLLARS] += float(line.get("cost_usd") or 0)
            if line.get("effort"):
                gradings["efforts"].add(line["effort"])
        if event == "adjudicated":
            outcome = line.get("outcome")
            self.adjudications[outcome] = self.adjudications.get(outcome, 0) + 1
        if event == "revise" and step:
            per_phase = self.step_mark(step).setdefault("revise phases", {})
            per_phase[phase] = (per_phase.get(phase, (0, ""))[0] + 1, line.get("budget", ""))
            if phase == "refactor":
                self.open_pass(step)["revise"] += 1
            return
        if event == "reroute" and step and line.get("kind") == "repair":
            self.step_mark(step).setdefault("revise phases", {}).setdefault(phase, (0, line.get("budget", "")))
        if event == "refactor" and step:
            mark = self.step_mark(step)
            mark["transforms"] = line.get("transforms", "")
            mark["refactor"] = line.get("budget", "")
            mark["stopped"] = line.get("stopped", "")
            current = self.open_pass(step)
            self.passes[(step, line.get("pass", ""))] = (line, current)
            current["marked"] = True
            self.settle_pass(step, current)
            return
        if event in CELL_MARKS and step:
            column, attribute = CELL_MARKS[event]
            self.step_mark(step)[column] = line.get(attribute, "")
            return
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
            return
        if phase and count in COUNTS:
            self.tally(self.counts, phase, PHASE_COLUMNS, count)
            self.tally(self.leaves, self.leaf_kind(line), PHASE_COLUMNS, count)
        model = self.model_row(line) if count in COUNTS else None
        if model is not None:
            model[count] += 1
        if step:
            self.tally(self.steps, step, STEP_COLUMNS, count)

    def first_tries(self):
        """Per phase: the steps with a PASS or REJECT verdict of it, those whose first such verdict was PASS, and its
        `revise` events."""
        tries = {}
        for (phase, _step), word in self.first_verdicts.items():
            counts = tries.setdefault(phase, dict.fromkeys(FIRST_TRY_KEYS, 0))
            counts["verified_steps"] += 1
            counts["first_try_pass"] += word == "PASS"
        for phase, cycles in self.revise_cycles.items():
            tries.setdefault(phase, dict.fromkeys(FIRST_TRY_KEYS, 0))["revise_cycles"] = cycles
        return tries

    def lost(self):
        """Per phase, the wall seconds and dollars of rejected attempts of steps that later finished (rework)
        and of every attempt of steps that never did (waste)."""
        lost = {}
        for phase in self.counts:
            self.row_in(lost, phase, LOST_COLUMNS)

        def lose(phase, attempt, wall_column, cost_column):
            row_of = self.row_in(lost, phase, LOST_COLUMNS)
            row_of[wall_column] += attempt[WALL]
            row_of[cost_column] += attempt[DOLLARS]

        for step, phase, attempt in self.rejected:
            if step in self.recovered:
                lose(phase, attempt, REWORK_WALL, REWORK_COST)
        for (step, phase, _attempt_no), attempt in self.attempts_spent.items():
            if step not in self.recovered:
                lose(phase, attempt, WASTE_WALL, WASTE_COST)
        return lost


def structural_inconsistency(structural):
    """What is self-contradictory in the structural-pass mark (a dict), or None when nothing is."""
    if "stopped" not in structural:
        return "the mark carries no stopped"
    if "transforms" in structural:
        if "budget" not in structural:
            return "transforms=%s without a budget" % structural["transforms"]
        if structural["stopped"] == "budget-spent" and int(structural["transforms"]) < int(structural["budget"]):
            return ("stopped=budget-spent, but transforms=%s is below budget=%s"
                    % (structural["transforms"], structural["budget"]))
        if structural["stopped"] not in ("candidates-done", "budget-spent", "nothing-structural"):
            return ("stopped=%s is not one of candidates-done, budget-spent, nothing-structural"
                    % structural["stopped"])
    return None


def refactor_total(label, marks):
    """(label, passes, transforms landed or None, passes that landed nothing or None, [(stop reason, passes)])
    over refactor marks; the two counts are None when a mark's transforms is not a number."""
    moved = [mark.get("transforms", "") for mark in marks]
    reasons = {}
    for mark in marks:
        reasons[mark["stopped"]] = reasons.get(mark["stopped"], 0) + 1
    numeric = all(count.isdigit() for count in moved)
    return (label, len(marks), sum(map(int, moved)) if numeric else None,
            moved.count("0") if numeric else None, sorted(reasons.items()))


def refactor_totals(passes, structural, structural_marked):
    """One `refactor_total` per step that had a refactor pass, then one for the issue (the structural pass
    counted when it was marked); [] when no pass and no structural mark exists."""
    if not (passes or structural_marked):
        return []
    by_step = {}
    for each in passes:
        by_step.setdefault(each["step"], []).append(each["mark"])
    every = [mark for marks in by_step.values() for mark in marks]
    rows = [refactor_total(step, marks) for step, marks in by_step.items()]
    if structural_marked:
        every = every + [dict(structural, transforms=structural.get("transforms", ""))]
    return rows + [refactor_total("issue", every)]


@dataclasses.dataclass
class Fold:
    """What the report says, as plain data; `layout` prints it and reads nothing else."""
    issue: str
    marks: list                 # every event of the log, each reworded step named by its latest text (reworded)
    clocked: bool               # whether every timed event carries an awake-clock reading
    models: dict                # (step, phase, attempt, actor) -> the model(s) that answered
    phases: dict                # phase -> {PHASE_COLUMNS: number}
    leaves: dict                # leaf kind (launch name less a trailing -<digits>, or "unnamed") -> {PHASE_COLUMNS: number}
    by_model: dict              # (role, model) -> {PHASE_COLUMNS: number}
    lost: dict                  # phase -> {LOST_COLUMNS: number}
    steps: dict                 # step -> {STEP_COLUMNS: number}
    step_marks: dict            # step -> the marks its events left (budgets, kind, start/done events)
    passes: list                # one dict per refactor pass: step, pass, mark, verdict, revise, wall, dollars
    tier_runs: dict             # test tier -> [seconds as text, in run order]
    adjudications: dict         # outcome -> count
    switched_off: int           # refactor verifiers switched off
    switched_off_by: dict       # phase -> verifiers switched off, every phase but refactor
    conductor_counted: bool     # whether the log carries the conductor's own usage event
    total: dict                 # {COST_COLUMNS: number}, leaves only until the conductor is added
    total_includes_conductor: bool   # the conductor's spend is in `total`: its usage event, or a priced session
    structural: object          # the structural-pass event, else {"stopped": "not marked"} for a landed run, else None
    by_model_shown: bool        # a model answered, or a launch named one
    ended: bool                 # whether the run is over (run_end's answer)
    cause: object               # why it ended without an ending mark: "usage-limit", "killed" or None
    ending: object              # the mark that ended the run (done, stop or bail event), or None
    bails: list                 # every bail event in log order, as {cause, classification, phase, step}; a key the
                                # event lacks is None
    issue_wall: object          # seconds from the opening mark to the ending, or None
    asleep: object              # seconds of that span the machine was not running, or None
    steps_done: object          # steps recovered plus ticked full-suite lines, or the ledger's done steps when
                                # more, or None when zero
    planned: object             # steps the ledger plans, or None
    lane: str                   # the label the run was opted in by
    flaked: list                # files named by suite-flake events
    pinned: str                 # the phases whose verifiers the run skipped (VERI_SKIP_VERIFY, pinned)
    model_knobs: dict           # VERI_MODEL* knob -> its value, and VERI_EFFORT_VERIFIER -> the launch events' efforts; falsy when unset
    sessions: list              # the conductor's sessions (result records, a trailing open one); [] when its usage
                                # event is in the log or its stream log is missing
    turn_rows: list             # the conductor's turns as [number, dollars text, context text], with .estimated,
                                # .session_contexts (tokens per turn, per session) and .families (comment family
                                # -> [turns, output tokens, dollars])
    conductor_spend: float      # dollars over every session, already added into `total`
    conductor_turns: int
    conductor_model: str        # the conductor model the launcher recorded, "" when none
    conductor_priced: bool      # every session carries a price
    conductor_some_priced: bool
    conductor_estimated: bool   # some session has no result record yet
    operator_sessions: list     # (label, turns, cache tokens read, dollars) per dev transcript found
    step_walls: dict            # step -> seconds between its start and done marks, or None
    structural_marked: bool     # the structural-pass event carries a stopped
    structural_inconsistency: object   # what contradicts itself in the structural mark, or None
    refactor_totals: list       # refactor_total rows: each step with a pass, then the issue
    green_rejects: list         # (step, attempt, route, check, reason) per green REJECT verdict, in log order
    green_reject_routes: list   # (route, count) over green_rejects, by count descending, then route
    green_reject_checks: list   # (check, count) over green_rejects, by check ascending, then ("unnamed", count)
    launch_costs: dict          # (actor, model) -> {LAUNCH_COLUMNS: tokens}, leaf usage events with first-turn fields
    launch_cost_missing: int    # leaf usage events without the first-turn fields
    gradings: dict              # the grading events: count, PASS, REJECT, $ (summed cost_usd), efforts (a set)
    first_tries: dict           # phase -> {FIRST_TRY_KEYS: count}: steps with a PASS or REJECT verdict of the phase, those
                                # whose first such verdict was PASS, and the phase's revise events
    revise_green: dict          # answering model -> {leaves, PASS, REJECT}: revise-green leaves, and the first green
                                # verdict of the same step after each
    runs: list                  # one dict per run of the issue, in order: index, ended, cause, wall_seconds,
                                # awake_seconds, sessions, leaves, cost_usd (runs_of)
    stages: dict                # stage -> {STAGE_KEYS: number}, for each stage the journal marked (stages_of)
    conductor_by_phase: object  # window -> {BY_PHASE_KEYS}, the conductor's turns per phase; None when no session was read
    reject_outcomes: list       # (phase, step, outcome) per REJECT verdict, in log order (reject_outcomes)
    former: dict                # step's latest text -> its earlier texts in order, for each reworded step (reworded)


def is_revise_green(name):
    return name == "revise-green" or name.startswith("revise-green-")


def revise_green_outcomes(marks, models):
    """Per model that answered a revise-green leaf: its leaves, and the PASS and REJECT counts of the first green
    `verdict` event of the same step after each."""
    outcomes = {}
    for at, mark in enumerate(marks):
        if mark.get("event") != "launch" or not is_revise_green(str(mark.get("name", ""))):
            continue
        key = (mark.get("step", ""), mark.get("phase", ""), mark.get("attempt", ""), mark.get("actor"))
        counts = outcomes.setdefault(models.get(key) or "not recorded", {"leaves": 0, "PASS": 0, "REJECT": 0})
        counts["leaves"] += 1
        verdict = next((later.get("verdict") for later in marks[at + 1:] if later.get("event") == "verdict"
                        and later.get("phase") == "green" and later.get("step", "") == key[0]), None)
        if verdict in ("PASS", "REJECT"):
            counts[verdict] += 1
    return outcomes


def launched_efforts(marks):
    """The efforts the run's verifier leaves were launched at, as their `launch` events record them: sorted, joined by
    commas, empty when none carries one; an effort that is not a string is skipped."""
    return ",".join(sorted({mark["effort"] for mark in marks if mark.get("event") == "launch"
                            and isinstance(mark.get("effort"), str) and mark["effort"]}))


RUN_ENDINGS = ("done", "bail", "stop")
CUT = "metrics-cut"


def cut_as_done(marks):
    """(the journal, None), or, when a `metrics-cut` line stands (no later done, bail, stop, preflight-refused, resume
    or step-added line follows it), (the journal with that line read as a `done` line, that line) (#4332): the report
    committed before the PR is readied ends where the cut was written, while the `done` mark waits for CI's green
    verdict."""
    cut = run_end.standing_mark(marks, (*run_end.MARKS, CUT))
    if cut.get("event") != CUT:
        return marks, None
    done = dict(cut, event="done")
    return [done if line is cut else line for line in marks], done


def runs_of(marks):
    """The journal split into runs (PRD 035.4b, D11): the first line opens run 1, a `done`, `bail` or `stop` line ends
    the run it is in and the next line opens the next, so a restart's `conductor-start` continues its run. Per run: its
    ending line's event and a bail's cause, its first-to-ending wall and awake seconds (None while open, or when a clock
    reading is missing), its `conductor-start` lines, and the `launch` and `usage` lines naming a phase, the ones the
    leaf tables count, so the runs sum to the issue's leaf totals."""
    runs, current = [], None
    for line in marks:
        if current is None:
            current = {"first": line, "ending": None, "sessions": 0, "leaves": 0, "cost_usd": 0.0}
            runs.append(current)
        event, phase = line.get("event"), line.get("phase")
        current["sessions"] += event == "conductor-start"
        current["leaves"] += bool(event == "launch" and phase)
        if event == "usage" and phase:
            current["cost_usd"] += float(line.get("total_cost_usd") or 0)
        if event in RUN_ENDINGS:
            current["ending"] = line
            current = None
    shaped = []
    for index, run in enumerate(runs, 1):
        first, ending = run["first"], run["ending"] or {}
        shaped.append({"index": index, "ended": ending.get("event"),
                       "cause": ending.get("cause") if ending.get("event") == "bail" else None,
                       "wall_seconds": span(first.get("ts"), ending.get("ts")),
                       "awake_seconds": span(first.get("awake"), ending.get("awake")),
                       "sessions": run["sessions"], "leaves": run["leaves"], "cost_usd": run["cost_usd"]})
    return shaped


STAGE_ENDS = {"0": "ok", "1": "failed", "2": "no_answer", "3": "nothing"}
STAGE_KEYS = ("runs", "ok", "failed", "no_answer", "nothing", "unended", "wall_seconds")


def stages_of(marks):
    """Per stage a journal marked (PRD 035.5a, D13): its `stage-start` lines (`runs`), its `stage-end` lines by exit code
    (`ok`, `failed`, `no_answer`, `nothing` for 0 to 3, any other status `no_answer`), its starts with no end of that stage before its next start
    or the journal's end (`unended`: killed), and its ends' seconds summed. A stage no line names is absent, never
    zero; a line naming no stage is skipped."""
    stages, open_starts = {}, {}
    for line in marks:
        event, name = line.get("event"), line.get("stage")
        if event not in ("stage-start", "stage-end") or not isinstance(name, str) or not name:
            continue
        counts = stages.setdefault(name, dict.fromkeys(STAGE_KEYS, 0))
        if event == "stage-start":
            counts["runs"] += 1
            counts["unended"] += open_starts.get(name, False)
            open_starts[name] = True
            continue
        open_starts[name] = False
        # a status outside the four exit codes (a line written before event.stage folded it) is no answer, as 2 is
        counts[STAGE_ENDS.get(line.get("status"), "no_answer")] += 1
        counts["wall_seconds"] += whole(line.get("secs")) or 0
    for name, unended in open_starts.items():
        stages[name]["unended"] += unended
    return stages


def reworded(marks):
    """The journal with every step a `step-reworded` line renamed, transitively, named by its latest text (PRD 035.4c,
    MS3), and {latest text: [its earlier texts, in order]}; a journal with no such line comes back as it is, with {}.
    A rewording back to an earlier text makes that text the latest again, never one of its own former texts; two steps
    reworded to one text are one step from then on, its former texts the target's then the source's."""
    chains = {}
    for line in marks:
        if line.get("event") == "step-reworded" and line.get("from") and line.get("to"):
            chain, target = chains.get(line["from"]) or [line["from"]], chains.get(line["to"])
            if target is not None and target is not chain:
                chain = [text for text in target if text != line["to"]] + [text for text in chain if text not in target]
            elif line["to"] in chain:
                chain.remove(line["to"])
            chain.append(line["to"])
            for text in chain:
                chains[text] = chain
    if not chains:
        return marks, {}
    renamed = [dict(line, step=chains[line["step"]][-1]) if line.get("step") in chains else line for line in marks]
    return renamed, {chain[-1]: chain[:-1] for chain in chains.values()}


REJECT_OUTCOMES = ("caught", "flipped", "overturned", "unresolved", "pending", "untracked")


def reject_outcome(reject, later):
    """What one REJECT `verdict` line led to (PRD 035.3a, D12), read off the lines after it: overturned when a
    `revise-impossible` bail of its step comes before its paired PASS (the first later PASS of its step and phase);
    else caught, flipped or untracked by the paired PASS's `tree`; else unresolved when any bail follows, pending
    when none does."""
    step, phase, bailed = reject.get("step", ""), reject.get("phase", ""), False
    for line in later:
        event = line.get("event")
        if event == "bail":
            if line.get("cause") == "revise-impossible" and line.get("step", "") == step:
                return "overturned"
            bailed = True
        elif (event == "verdict" and line.get("verdict") == "PASS" and line.get("step", "") == step
              and line.get("phase", "") == phase):
            if not reject.get("tree") or not line.get("tree"):
                return "untracked"
            return "flipped" if line["tree"] == reject["tree"] else "caught"
    return "unresolved" if bailed else "pending"


def reject_outcomes(marks):
    """(phase, step, outcome) per REJECT `verdict` line, in journal order; a `malformed` verdict is not one."""
    return [(line.get("phase", ""), line.get("step", ""), reject_outcome(line, marks[at + 1:]))
            for at, line in enumerate(marks) if line.get("event") == "verdict" and line.get("verdict") == "REJECT"]


def rejects_json(outcomes, wanted):
    """The six outcome counts over `outcomes` whose (phase, step) `wanted` accepts."""
    counts = dict.fromkeys(REJECT_OUTCOMES, 0)
    for phase, step, said in outcomes:
        if wanted(phase, step):
            counts[said] += 1
    return counts


BESIDE = "the run whose .tdd/ holds the journal"


def fold(issue, path, ledger, run=BESIDE, cut=False):
    """Read the journal at `path` (and the ledger and files beside it) into a `Fold`; prints nothing. `run` is the run
    directory whose end, conductor stream log and pins are read: by default the one whose `.tdd/` holds `path`; None
    reads the journal alone (the ledger too may be None), whose run has ended only when a mark ends it (else `ended`
    is None: not known) and whose conductor spend is not known. `cut` reads a standing `metrics-cut` line as the
    run's `done` (cut_as_done): the markdown report takes it, the JSON figures never do."""
    if run is BESIDE:
        run, beside, roots = os.path.dirname(os.path.dirname(os.path.abspath(path))), path, pin_roots()
    elif run is not None:
        beside, roots = run_dir.run_file(run, "events.jsonl"), pin_roots(run)
    marks, former = reworded(read_events(path))
    marks, cut = cut_as_done(marks) if cut else (marks, None)
    clocked = bool(marks) and all("awake" in mark for mark in marks if "ts" in mark)
    models = {(mark.get("step", ""), mark.get("phase", ""), mark.get("attempt", ""), mark.get("actor")):
              mark["model"] for mark in marks if mark.get("event") == "usage" and "model" in mark}
    tally = _Tally(models, clocked)
    for line in marks:
        tally.take(line)
    passes = [{"step": step, "pass": index, "mark": mark, "verdict": spent_by["verdict"],
               "revise": spent_by["revise"], "wall": spent_by[WALL], "dollars": spent_by[DOLLARS]}
              for (step, index), (mark, spent_by) in tally.passes.items()]
    if run is None:
        ending = run_end.standing_mark(marks)
        ended, cause = (True, run_end.MARKS[ending["event"]]) if ending else (None, None)
    else:
        ended, cause, ending = run_end.run_end(run)
        if cut is not None and not ending:  # the run's own end is read off its events file, which a cut never ends
            ended, cause, ending = True, run_end.MARKS["done"], cut
    ending = ending or None
    wall_span, awake_span = wall_and_awake_spans(tally.opening, ending, clocked)
    planned, full_suite, ledger_done = planned_steps(ledger) if ledger is not None else (None, 0, 0)
    pinned = (run_pins.skip_verify(issue, *roots) or "") if run is not None else ""
    sessions, turn_rows = [], []
    if not tally.conductor_counted and run is not None:
        sessions, turn_rows = conductor_sessions(issue, beside)
    spend, model, estimated, priced, some_priced = 0.0, "", False, False, False
    if sessions:
        priced = not any(r.get("total_cost_usd", 0) is None for r in sessions)
        some_priced = any(r.get("total_cost_usd") is not None for r in sessions)
        spend = sum(r.get("total_cost_usd") or 0 for r in sessions)
        tally.total[DOLLARS] += spend
        model = run_pins.conductor_model(issue, *roots) or ""
        estimated = any(r.get("open") for r in sessions)
    transcripts = tunables.get("VERI_SESSION_TRANSCRIPTS")
    first_event = min((mark["ts"] for mark in marks if "ts" in mark), default=None)
    done_at = max((mark["ts"] for mark in marks if mark.get("event") == "done" and "ts" in mark), default=None)
    operator_sessions = []
    for label, command in (("Dev", "/vdev"),):
        found = session_spend(transcripts, command, first_event, done_at) if transcripts else None
        if found:
            operator_sessions.append((label,) + found)
    green_rejects = [(step, attempt, "none" if route is None else route, check, reason)
                     for step, attempt, route, check, reason in tally.green_rejects]
    routes = collections.Counter(route for _step, _attempt, route, _check, _reason in green_rejects)
    checks = collections.Counter(check for _step, _attempt, _route, check, _reason in green_rejects)
    structural = tally.structural
    structural_marked = structural is not None and "stopped" in structural
    if structural is None and ending is not None and ending.get("event") == "done":
        structural = {"stopped": "not marked"}
    return Fold(issue=issue, marks=marks,
                step_walls={step: awake_span_or_wall(tally.spent.get(step, {}).get("step-start"),
                                                     tally.spent.get(step, {}).get("step-done"), clocked)
                            for step in tally.steps},
                structural_marked=structural_marked,
                structural_inconsistency=None if structural is None else structural_inconsistency(structural),
                refactor_totals=refactor_totals(passes, structural, structural_marked), clocked=clocked, models=models,
                by_model_shown=bool(models) or any(mark.get("event") == "launch" and "model" in mark for mark in marks),
                ended=ended, cause=cause, ending=ending,
                bails=[{key: mark.get(key) for key in ("cause", "classification", "phase", "step")}
                       for mark in marks if mark.get("event") == "bail"],
                sessions=sessions, turn_rows=turn_rows, conductor_spend=spend,
                conductor_turns=sum(r.get("num_turns") or 0 for r in sessions), conductor_model=model,
                conductor_priced=priced, conductor_some_priced=some_priced, conductor_estimated=estimated,
                operator_sessions=operator_sessions,
                issue_wall=awake_span_or_wall(tally.opening, ending, clocked),
                asleep=None if awake_span is None or wall_span is None else max(0, wall_span - awake_span),
                steps_done=counted(max(len(tally.recovered) + full_suite, ledger_done)), planned=planned,
                lane=tunables.get("VERI_LABEL", unless_empty=True),
                flaked=[name for mark in marks if mark.get("event") == "suite-flake"
                        for name in str(mark.get("files", "")).split(",")],
                pinned=pinned,
                model_knobs=dict({knob: tunables.read(knob) for knob in
                                  ["VERI_MODEL", "VERI_MODEL_DEVELOPER", "VERI_MODEL_VERIFIER", "VERI_MODEL_REVISE",
                                   "VERI_MODEL_REVISE_GREEN"]},
                                 VERI_EFFORT_VERIFIER=launched_efforts(marks)),
                phases=tally.counts, leaves=tally.leaves, by_model=tally.by_model, lost=tally.lost(),
                steps=tally.steps, step_marks=tally.spent, passes=passes, tier_runs=tally.tier_runs,
                adjudications=tally.adjudications, switched_off=tally.switched_off,
                switched_off_by=tally.switched_off_by,
                conductor_counted=tally.conductor_counted, total=tally.total,
                total_includes_conductor=tally.conductor_counted or some_priced, structural=structural,
                green_rejects=green_rejects,
                green_reject_routes=sorted(routes.items(), key=lambda item: (-item[1], item[0])),
                green_reject_checks=sorted(item for item in checks.items() if item[0]) + [("unnamed", checks[""])],
                launch_costs=tally.launch_costs, launch_cost_missing=tally.launch_cost_missing,
                gradings=tally.gradings, first_tries=tally.first_tries(), revise_green=revise_green_outcomes(marks, models),
                runs=runs_of(marks), stages=stages_of(marks), reject_outcomes=reject_outcomes(marks),
                former=former, conductor_by_phase=conductor_by_phase(marks, turn_rows.turns) if sessions else None)


def known(number):
    """`number` as text, or "unknown" when it is None."""
    return UNKNOWN if number is None else "%d" % number


def row(cells):
    print("| " + " | ".join(cells) + " |")


def figure(column, value):
    return "%.2f" % value if column in MONEY else "%d" % value


def figures(row_counts, columns):
    return [figure(c, row_counts[c]) for c in columns]


def refactor_spent(mark):
    """"transforms/budget" of a refactor mark, "?" for a part it lacks."""
    return "%s/%s" % (mark.get("transforms", "?"), mark.get("budget", "?"))


def budget_cells(mark):
    """The revise, refactor and stopped cells of a step's row, from the budget marks its events left."""
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


def step_cells(f, step):
    """The text cells after the counts in a step's row: wall, budgets, crossing and split marks, kind."""
    mark = f.step_marks.get(step, {})
    return ([known(f.step_walls[step])] + budget_cells(mark) + [mark.get(column, "") for column in MARK_COLUMNS]
            + [mark.get(KIND, "full")])


def heading_block(heading):
    print()
    print(heading)
    print()


def table_head(heading, key_column, columns, aligns):
    heading_block(heading)
    row([key_column] + columns)
    row(["---"] + aligns)


def section(heading, key_column, columns, table, text=None, estimate=False):
    """A table of `columns` per key; `text` is ((extra headings), cells_for(key)); `estimate` marks the dollars."""
    headings, cells_for = text or ((), None)
    headings = list(headings)
    table_head(heading, key_column, columns + headings,
               ["---:"] * len(columns) + ["---"] * len(headings))
    for key, row_counts in table.items():
        cells = [key] + figures(row_counts, columns)
        if estimate:
            at = columns.index(DOLLARS) + 1
            cells[at] += " (estimate)"
        row(cells + (cells_for(key) if cells_for else []))


def tier_section(heading, key_column, tier_runs):
    width = max([len(runs) for runs in tier_runs.values()] or [0])
    table_head(heading, key_column,
               ["run %d s" % (i + 1) for i in range(width)], ["---:"] * width)
    for tier, runs in tier_runs.items():
        row([tier] + runs + [""] * (width - len(runs)))


def print_outcome(f):
    """The sentences that open the report: wall time, steps done, the outcome, the lane, flakes."""
    ending = f.ending
    print("### 📊 Metrics — issue %s" % f.issue)
    print()
    print("Wall time for the issue: %s s, from the last `resume`, or the first event of the log when "
          "there is none, to the mark that ended the run."
          % known(f.issue_wall))
    if f.asleep is not None:
        print("Seconds the machine was not running inside that span: %s s, excluded from it."
              % f.asleep)
    if not f.clocked:
        print("Every figure in this report is wall-clock: the log carries no awake-clock reading, "
              "so time the machine spent asleep is counted in them.")
    print("Steps done: %s of %s planned."
          % (known(f.steps_done), known(f.planned)))
    said = outcome(f)
    if said == "running":
        print("Outcome: none yet — the run is still going.")
    elif said == "usage-limit":
        print("Outcome: the run hit a usage limit.")
    elif said == "killed":
        print("Outcome: the run was killed — its conductor's latest launch left no result.")
    elif said == UNKNOWN:
        print("Outcome: %s — the log carries no mark ending the run." % UNKNOWN)
    elif said == "landed":
        print("Outcome: the run landed — its draft PR is %s."
              % (ending.get("pr") or UNKNOWN))
    elif said == "stopped":
        print("Outcome: the run was stopped — mode %s, at %s."
              % (ending.get("mode") or UNKNOWN, ending.get("at") or UNKNOWN))
    else:
        print("Outcome: the run bailed — %s, a %s failure."
              % (ending.get("cause") or UNKNOWN, ending.get("classification") or UNKNOWN))
    print("Lane: %s" % f.lane)
    if f.flaked:
        print("Suite flakes: %s." % ", ".join(f.flaked))


def print_conductor(f):
    """The sentences and tables about the conductor's own spending."""
    sessions, turn_rows = f.sessions, f.turn_rows
    if sessions:
        priced = f.conductor_priced
        print("Cost is every leaf of the run, and the conductor own spending." if priced else
              "Cost is every leaf of the run; the total row includes the priced sessions' conductor spending and leaves out the unpriced ones."
              if f.conductor_some_priced else
              "Cost is every leaf of the run; the total row excludes the conductor own spending, which is unpriced.")
        print("Conductor own spending: %s over %d turns, in %d sessions%s%s."
              % ("$%.2f" % f.conductor_spend if priced else "unpriced",
                 f.conductor_turns, len(sessions),
                 ", on %s" % f.conductor_model if f.conductor_model else "",
                 " (estimate)" if f.conductor_estimated else ""))
        if f.conductor_estimated:
            print("The Conductor own spending figure is estimated: the output tokens of a session without a "
                  "result record are not yet known.")
        for contexts in turn_rows.session_contexts:
            print("Conductor context: first turn %d tokens, largest %d tokens" % (contexts[0], max(contexts)))
    else:
        print("Cost is every leaf of the run, and the conductor own %s."
              % ("closing accounting with them, which this log carries"
                 if f.conductor_counted else
                 "spending is not in it: this log carries no usage record of the conductor own"))
    if turn_rows:
        if turn_rows.estimated:
            print("The per-turn dollars are estimated: each turn's non-output usage priced, plus a share of the "
                  "result record's remaining cost.")
        table_head("#### Conductor per turn", "turn", ["dollars", "context"], ["---:", "---:"])
        for turn_row in turn_rows:
            row(turn_row)
    if turn_rows:
        table_head("#### Conductor comments, by family", "family", ["turns", "output tokens", "dollars"], ["---:", "---:", "---:"])
        for name, (turns, tokens, dollars) in turn_rows.families.items():
            row([name, str(turns), str(tokens), "$%.2f" % dollars])
    if f.conductor_by_phase:
        table_head("#### Conductor by phase (estimated: each turn placed by its timestamp)", "phase",
                   ["turns", DOLLARS], ["---:", "---:"])
        for window, entry in f.conductor_by_phase.items():
            cost = entry["cost_usd"]
            row([window, "%d" % entry["turns"], UNKNOWN if cost is None else "%.2f" % cost])
        print()  # a line straight after a table would read as one more row of it


def print_reject_outcomes(f):
    """What each phase's REJECTs led to (PRD 035.7a, MD1): one row per phase with a REJECT, the figures `as_json` gives
    its `rejects`; nothing when the run has none."""
    rejected = [(phase, rejects_json(f.reject_outcomes, lambda of, _step, phase=phase: of == phase))
                for phase in f.phases]
    rejected = [(phase, counts) for phase, counts in rejected if any(counts.values())]
    if not rejected:
        return
    table_head("#### REJECT outcomes", "phase", ["REJECT", *REJECT_OUTCOMES], ["---:"] * (1 + len(REJECT_OUTCOMES)))
    for phase, counts in rejected:
        row([phase, "%d" % sum(counts.values())] + ["%d" % counts[said] for said in REJECT_OUTCOMES])


STAGE_HEADINGS = {"runs": "runs", "ok": "ok", "failed": "failed", "no_answer": "no answer", "nothing": "nothing",
                  "unended": "unended", "wall_seconds": WALL}


def print_stages(f):
    """Each stage the journal marked (PRD 035.7b, MD4), whatever its name: the figures `as_json` gives its `stages`
    entry; nothing when no stage is marked."""
    if not f.stages:
        return
    table_head("#### Stages", "stage", [STAGE_HEADINGS[key] for key in STAGE_KEYS], ["---:"] * len(STAGE_KEYS))
    for name, counts in f.stages.items():
        row([name] + ["%d" % counts[key] for key in STAGE_KEYS])


def layout(f):
    """Print the report for a `Fold`; reads nothing else."""
    print_outcome(f)
    print_conductor(f)
    if f.models:
        print("Models requested: %s; models that answered: %s."
              % (", ".join("%s %s" % (knob, value or "unset") for knob, value in f.model_knobs.items()),
                 ", ".join(sorted({m for answered in f.models.values() for m in answered.split(",") if m}))))
    if f.pinned:
        print("⚠️ Unverified phases: %s" % f.pinned)
    switched_off = sorted((phase, n) for phase, n in [*f.switched_off_by.items(), ("refactor", f.switched_off)] if n)
    if switched_off:
        print("Verifiers switched off: %s" % ", ".join("%s %d" % pair for pair in switched_off))
    for operator_session in f.operator_sessions:
        print("%s session: %d turns, %d cache tokens read, $%.2f" % operator_session)
    section("#### By phase", "phase", PHASE_COLUMNS, f.phases)
    print_reject_outcomes(f)
    if f.by_model_shown:
        table_head("#### By model", "role", ["model"] + PHASE_COLUMNS, ["---"] + ["---:"] * len(PHASE_COLUMNS))
        for (role, model), row_counts in f.by_model.items():
            row([role, model or "not recorded"] + figures(row_counts, PHASE_COLUMNS))
    if f.revise_green:
        table_head("#### Revise-green, by model", "model", ["leaves", "PASS", "REJECT"], ["---:"] * 3)
        for model, counts in sorted(f.revise_green.items()):
            row([model] + ["%d" % counts[column] for column in ("leaves", "PASS", "REJECT")])
    section("#### Rework and waste, by phase", "phase", LOST_COLUMNS, f.lost)
    section("#### By step", "step", STEP_COUNTS + [API] + COST_COLUMNS, f.steps,
            ([WALL] + BUDGETS + MARK_COLUMNS + [KIND], lambda step: step_cells(f, step)))
    if f.adjudications:
        print()
        print("Adjudications: " + ", ".join("%s %d" % (outcome, f.adjudications.get(outcome, 0))
                                         for outcome in ("retry", "bail", "route", "unparsed")))
    print()
    print("The figure comparable across runs is turns, the same measurement on any model; dollars "
          "are not comparable, the same measurement only at the same VERI_MODEL, "
          "VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER, VERI_MODEL_REVISE and VERI_MODEL_REVISE_GREEN.")
    if f.passes:
        table_head("#### By refactor pass", "step", ["pass", "refactor", "stopped", "verdict", "revise", WALL, DOLLARS],
                   ["---:", "---:", "---", "---", "---:", "---:", "---:"])
        for each in f.passes:
            mark = each["mark"]
            row([each["step"], each["pass"], refactor_spent(mark), mark["stopped"],
                 each["verdict"], str(each["revise"])] + ["%d" % each["wall"], "%.2f" % each["dollars"]])
    structural = f.structural
    if structural is not None:
        stopped = structural.get("stopped", "?")
        if "transforms" not in structural:
            heading_block("#### Structural pass")
            print("Stopped: %s" % stopped)
        else:
            table_head("#### Structural pass", "pass", ["refactor", "stopped"], ["---:", "---"])
            row(["issue", refactor_spent(structural), stopped])
        if f.structural_inconsistency is not None:
            print()
            print("Inconsistent mark: %s" % f.structural_inconsistency)
    if f.refactor_totals:
        table_head("#### Refactor totals", "step", ["passes", "transforms", "landed nothing", "stopped"],
                   ["---:", "---:", "---:", "---"])
        for label, passed, transforms, nothing, reasons in f.refactor_totals:
            row([label, str(passed), "?" if transforms is None else str(transforms),
                 "?" if nothing is None else str(nothing), ", ".join("%s %d" % item for item in reasons)])
    tier_section("#### Test-command seconds, by tier", "tier", f.tier_runs)
    print_stages(f)
    section("#### Total", "run", COST_COLUMNS, {"total": f.total}, estimate=f.conductor_estimated)
    print()
    print("Not counted: the CI wait after readying and `pr-finish.sh`, which run after this report is committed.")
    if f.green_rejects:
        table_head("#### Green rejects", "step", ["attempt", "route", "check", "reason"], ["---:", "---", "---:", "---"])
        for step, attempt, route, check, reason in f.green_rejects:
            row([step, attempt, route, check, UNKNOWN if reason is None else reason.replace("|", "\\|")])
    print()
    print("Green rejects by route: " + (", ".join("%s %d" % item for item in f.green_reject_routes) or "none"))
    if f.green_rejects:
        print("Green rejects by check: " + ", ".join("%s %d" % item for item in f.green_reject_checks))
    if f.launch_costs:
        table_head("#### Launch cost, by role", "role", ["model"] + LAUNCH_COLUMNS, ["---"] + ["---:"] * len(LAUNCH_COLUMNS))
        for (role, model), tokens in f.launch_costs.items():
            row([role, model] + figures(tokens, LAUNCH_COLUMNS))
        if f.launch_cost_missing:
            print()
            print("Leaf usage events without first-turn figures, not in the table: %d" % f.launch_cost_missing)
    gradings = f.gradings
    if gradings["count"]:
        print()
        print("Gradings: %d, PASS %d, REJECT %d, cost $%.2f, efforts %s"
              % (gradings["count"], gradings["PASS"], gradings["REJECT"], gradings[DOLLARS],
                 ", ".join(sorted(gradings["efforts"])) or UNKNOWN))


def render(issue, path, ledger):
    """Print the report of `issue`: the journal at `path` and the ledger at `ledger`, folded then laid out, a standing
    `metrics-cut` line read as the run's end (#4332)."""
    layout(fold(issue, path, ledger, cut=True))


def usage_dollars(usage, prices):
    return (sum((usage.get(key) or 0) * prices[rate] / 1e6 for key, rate in TURN_RATES.items())
            + sum(tokens * prices[rate] / 1e6 for rate, tokens in cache_write_tokens(usage).items()))


def session_spend(directory, command, since, until=None):
    for name in sorted(os.listdir(directory)):
        with open(os.path.join(directory, name)) as lines:
            rows = [json.loads(line) for line in lines]
        if not rows[0]["message"]["content"].startswith(command):
            continue
        turns, cache_read, dollars = 0, 0, 0.0
        seen = set()
        for row in rows:
            message = row["message"]
            usage = message.get("usage")
            if not usage:
                continue
            stamp = row.get("timestamp")
            if stamp:
                moment = datetime.datetime.fromisoformat(stamp).timestamp()
                if (since is not None and moment < since) or (until is not None and moment > until):
                    continue
            if message.get("id") is not None:
                if message["id"] in seen:
                    continue
                seen.add(message["id"])
            prices = PRICES[family(message["model"])]
            turns += 1
            cache_read += usage["cache_read_input_tokens"]
            dollars += usage_dollars(usage, prices)
        return turns, cache_read, dollars
    return None


def report(issue, events_path, ledger_path, stream=None):
    out = io.StringIO() if stream is None else stream
    with contextlib.redirect_stdout(out):
        render(issue, events_path, ledger_path)
    return out.getvalue() if stream is None else None


def rendered(issue):
    """The report of `issue` read from the working directory's `.tdd`; answer `(code, stdout, stderr)` as text.

    Code 0 with the report on stdout, or code 2 with the usage line on stderr when `issue` is
    empty. Prints nothing; a missing or unreadable file raises as `report` does. Built on `report`.
    """
    if not issue:
        return 2, "", USAGE + "\n"
    return 0, report(issue, ".tdd/events.jsonl", run_dir.ledger(".", issue)), ""


JSON_KEYS = {"attempts": "attempts", "PASS": "pass", "REJECT": "reject", "kills": "kills", WALL: "wall_seconds",
             API: "api_seconds", "retries": "retries", "no-verdict": "no_verdict",
             **{heading: field for heading, field in COSTS}, "turns": "turns", DOLLARS: "cost_usd"}


def json_row(row_counts, columns):
    """A table row's `columns` under their JSON key names."""
    return {JSON_KEYS[column]: row_counts[column] for column in columns}


def as_json(f):
    """The run's figures as one JSON-ready object, read off a `Fold` alone (PRD 035.1)."""
    done = f.ending if f.ending is not None and f.ending.get("event") == "done" else {}
    return {"run": {"issue": f.issue, "outcome": outcome(f), "wall_seconds": whole(done.get("wall_seconds")),
                    "awake_seconds": whole(done.get("awake_seconds")), "bails": f.bails},
            "runs": f.runs,
            "stages": f.stages,
            "phases": {phase: dict(json_row(row_counts, PHASE_COLUMNS),
                                   **f.first_tries.get(phase, dict.fromkeys(FIRST_TRY_KEYS, 0)),
                                   rejects=rejects_json(f.reject_outcomes, lambda of, _step: of == phase))
                       for phase, row_counts in f.phases.items()},
            "leaves": {kind: json_row(row_counts, PHASE_COLUMNS) for kind, row_counts in f.leaves.items()},
            # a step's wall is the markdown's: its start-to-done span, not its leaves' summed seconds
            "steps": [dict(json_row(row_counts, STEP_COLUMNS), text=step, wall_seconds=f.step_walls[step],
                           rejects=rejects_json(f.reject_outcomes, lambda _phase, of: of == step),
                           former=list(f.former.get(step, [])))
                      for step, row_counts in f.steps.items()],
            "conductor": conductor_json(f),
            "total": dict(json_row(f.total, COST_COLUMNS), includes_conductor=f.total_includes_conductor)}


def whole(text):
    """A mark's whole-number value as an int; None when the mark lacks it or it is not a whole number."""
    return int(text) if isinstance(text, str) and text.isdigit() else None


def outcome(f):
    """How the run ended, in the word the report's Outcome sentence says it: running, usage-limit, killed, unknown,
    landed, stopped or bailed."""
    if f.ended is None:
        return None
    if not f.ended:
        return "running"
    if f.ending is None:
        return f.cause if f.cause in ("usage-limit", "killed") else UNKNOWN
    return {"done": "landed", "stop": "stopped"}.get(f.ending.get("event"), "bailed")


def conductor_json(f):
    """The conductor's own spending over its sessions; `cost_usd` and `turns` are None when no session was read, and
    `cost_usd` also when none carries a price (a partial figure is the priced sessions' sum, `priced` "partial")."""
    priced = True if f.conductor_priced else "partial" if f.conductor_some_priced else False
    return {"cost_usd": f.conductor_spend if priced else None, "turns": f.conductor_turns if f.sessions else None,
            "sessions": len(f.sessions), "model": f.conductor_model or None, "estimated": f.conductor_estimated,
            "priced": priced, "by_phase": f.conductor_by_phase}


def print_json(issue, path, ledger):
    """Print `as_json` of the journal at `path` as one JSON object, nothing before it is whole."""
    sys.stdout.write(json.dumps(as_json(fold(issue, path, ledger)), indent=2) + "\n")


def publish(target, issue, journal, ledger, run):
    """Write `as_json` of the journal at `journal` (the ledger and run directory as `fold` takes them) to `target`:
    a temporary file beside it renamed over it, so a reader sees the old file or the new one, never part of one; the
    temporary file is removed when anything fails, and the error raised."""
    text = json.dumps(as_json(fold(issue, journal, ledger, run=run)), indent=2) + "\n"
    descriptor, temporary = tempfile.mkstemp(dir=os.path.dirname(target), prefix="." + os.path.basename(target) + ".")
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(text)
        os.replace(temporary, target)
    except BaseException:
        os.remove(temporary)
        raise


def main(argv):
    if not argv or argv[0] in ("", JSON) or argv[1:] not in ([], [JSON]):
        sys.stderr.write(USAGE + "\n")
        return 2
    issue = argv[0]
    write = print_json if argv[1:] == [JSON] else (lambda *where: report(*where, stream=sys.stdout))
    events = ".tdd/events.jsonl"
    carried = None if has_events(events, issue) else run_records.read(issue, "events.jsonl", ".")
    if not carried:
        write(issue, events, run_dir.ledger(".", issue))
        return 0
    with tempfile.TemporaryDirectory() as elsewhere:
        os.mkdir(os.path.join(elsewhere, ".tdd"))
        fetched = os.path.join(elsewhere, events)
        with open(fetched, "w", encoding="utf-8") as f:
            f.write(carried)
        write(issue, fetched, run_dir.ledger(".", issue))
    return 0


def has_events(path, issue):
    """Whether the journal at <path> holds an event of <issue>, or one naming no issue (an event written with no run
    context belongs to the run whose journal holds it); False when it is missing."""
    try:
        return any(str(mark.get("issue") or issue) == issue for mark in read_events(path, skip_unreadable=True))
    except FileNotFoundError:
        return False


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
