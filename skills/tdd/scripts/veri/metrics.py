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
  tables     phases, by_model (+ by_model_shown), lost, steps (+ step_marks, step_walls), tier_runs,
             adjudications, switched_off, switched_off_by, total, green_rejects (+ green_reject_routes, green_reject_checks),
             launch_costs (+ launch_cost_missing), gradings, revise_green
  refactor   passes (one dict per pass), structural (+ structural_marked, structural_inconsistency),
             refactor_totals
  conductor  conductor_counted, sessions, turn_rows (+ .families, .session_contexts, .estimated),
             conductor_spend, conductor_turns, conductor_model, conductor_priced, conductor_some_priced,
             conductor_estimated, operator_sessions
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
import run_dir
import run_end
import run_pins
import run_records
import tempfile
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

USAGE = "usage: metrics.sh <issue-number>"
JSON = "--json"
# the skip events counted on the "Verifiers switched off:" line beside refactor's own count
SWITCHED_OFF_EVENTS = {"verify-%s-skipped" % phase: phase for phase in ("diff", "green", "pin", "red")}


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
        self.families = {name: [0, 0, 0.0] for name in [n for n, _ in COMMENT_FAMILIES] + [FAMILIES_TOTAL]}


def main_checkout_file(path, name):
    found = os.path.join(os.path.dirname(path), name)
    if not os.path.exists(found):
        found = os.path.join(os.path.dirname(path), "..", "..", "..", name)
    return found


def pin_roots():
    """Where a run's pin files may sit: the run's own `.tdd/`, then the main working tree's."""
    main = run_dir.main_of_worktree(os.getcwd())
    return (".",) if main is None else (".", main)


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
    sessions = []
    open_rows = []
    open_turns, open_cost, open_priced = 0, 0.0, True
    open_contexts = []
    turn_rows = TurnRows()
    seen_ids = {}
    open_turn_rows = []

    with contextlib.suppress(OSError):
        with open(main_checkout_file(path, "conductor-%s.log" % issue)) as stream_log:
            for text in stream_log:
                with contextlib.suppress(ValueError):
                    record = json.loads(text)
                    if not isinstance(record, dict):
                        continue
                    if record.get("type") == "result":
                        sessions.append(record)
                        count_families(turn_rows, open_turn_rows, (record.get("usage") or {}).get("output_tokens"))
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
                            flushed = not any(row[0] is earlier for row in open_turn_rows)
                            if earlier is not None and not (names and flushed and (not set(names) & set(earlier) or set(names) == set(earlier))):
                                added = [n for n in names if n not in earlier]
                                earlier.extend(added)
                                if flushed:
                                    count_families(turn_rows, [(added, None, 0)], None)
                                continue
                            seen_ids[message["id"]] = names
                        open_turns += 1
                        model_name = message.get("model") or ""
                        model_family = family(model_name) or ("opus" if not model_name else None)
                        open_turn_rows.append((names,
                                               model_family, usage.get("output_tokens") or 0))
                        context = sum((usage.get(key) or 0) for key in CONTEXT_KEYS)
                        open_contexts.append(context)
                        if model_family is None:
                            open_priced = False
                            turn_rows.append([str(len(turn_rows) + 1), "unpriced", str(context)])
                            continue
                        prices = PRICES[model_family]
                        output_dollars = (usage.get("output_tokens") or 0) * prices["output"] / 1e6
                        turn_dollars = usage_dollars(usage, prices)
                        open_cost += turn_dollars
                        base_dollars = turn_dollars - output_dollars
                        open_rows.append((len(turn_rows), base_dollars))
                        turn_rows.append([str(len(turn_rows) + 1), "$%.2f" % base_dollars, str(context)])
        count_families(turn_rows, open_turn_rows, None)
        if open_turns:
            sessions.append({"total_cost_usd": open_cost if open_priced else None, "num_turns": open_turns, "open": True})
        if open_contexts:
            turn_rows.session_contexts.append(open_contexts)
    return sessions, turn_rows


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
    """(number of steps the ledger at `path` plans, or None; number of ticked full-suite lines)."""
    try:
        with open(path, "rb") as f:
            text = decode_ledger(f.read())
    except OSError:
        return None, 0
    steps = ledger_steps(text)
    records = "".join("\t".join(record) + "\n" for record in steps)
    full_suite = sum(1 for record in steps if record.state == "done" and record.kind == "full-suite")
    return counted(len(records.splitlines())), full_suite


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

    def rows_for(self, phase, step, line):
        rows = [r for r in [self.model_row(line)] if r is not None]
        if phase:
            rows.append(self.row_in(self.counts, phase, PHASE_COLUMNS))
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
        model = self.model_row(line) if count in COUNTS else None
        if model is not None:
            model[count] += 1
        if step:
            self.tally(self.steps, step, STEP_COLUMNS, count)

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
    marks: list                 # every event of the log
    clocked: bool               # whether every timed event carries an awake-clock reading
    models: dict                # (step, phase, attempt, actor) -> the model(s) that answered
    phases: dict                # phase -> {PHASE_COLUMNS: number}
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
    structural: object          # the structural-pass event, else {"stopped": "not marked"} for a landed run, else None
    by_model_shown: bool        # a model answered, or a launch named one
    ended: bool                 # whether the run is over (run_end's answer)
    cause: object               # why it ended without an ending mark: "usage-limit", "killed" or None
    ending: object              # the mark that ended the run (done, stop or bail event), or None
    issue_wall: object          # seconds from the opening mark to the ending, or None
    asleep: object              # seconds of that span the machine was not running, or None
    steps_done: object          # steps recovered plus ticked full-suite lines, or None when zero
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
    operator_sessions: list     # (label, turns, cache tokens read, dollars) per coordinator / dev transcript found
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
    revise_green: dict          # answering model -> {leaves, PASS, REJECT}: revise-green leaves, and the first green
                                # verdict of the same step after each


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


def fold(issue, path, ledger):
    """Read the journal at `path` (and the ledger and files beside it) into a `Fold`; prints nothing."""
    marks = read_events(path)
    clocked = bool(marks) and all("awake" in mark for mark in marks if "ts" in mark)
    models = {(mark.get("step", ""), mark.get("phase", ""), mark.get("attempt", ""), mark.get("actor")):
              mark["model"] for mark in marks if mark.get("event") == "usage" and "model" in mark}
    tally = _Tally(models, clocked)
    for line in marks:
        tally.take(line)
    passes = [{"step": step, "pass": index, "mark": mark, "verdict": spent_by["verdict"],
               "revise": spent_by["revise"], "wall": spent_by[WALL], "dollars": spent_by[DOLLARS]}
              for (step, index), (mark, spent_by) in tally.passes.items()]
    ended, cause, ending = run_end.run_end(os.path.dirname(os.path.dirname(os.path.abspath(path))))
    ending = ending or None
    wall_span, awake_span = wall_and_awake_spans(tally.opening, ending, clocked)
    planned, full_suite = planned_steps(ledger)
    pinned = run_pins.skip_verify(issue, *pin_roots()) or ""
    sessions, turn_rows = [], []
    if not tally.conductor_counted:
        sessions, turn_rows = conductor_sessions(issue, path)
    spend, model, estimated, priced, some_priced = 0.0, "", False, False, False
    if sessions:
        priced = not any(r.get("total_cost_usd", 0) is None for r in sessions)
        some_priced = any(r.get("total_cost_usd") is not None for r in sessions)
        spend = sum(r.get("total_cost_usd") or 0 for r in sessions)
        tally.total[DOLLARS] += spend
        model = run_pins.conductor_model(issue, *pin_roots()) or ""
        estimated = any(r.get("open") for r in sessions)
    transcripts = tunables.get("VERI_SESSION_TRANSCRIPTS")
    first_event = min((mark["ts"] for mark in marks if "ts" in mark), default=None)
    done_at = max((mark["ts"] for mark in marks if mark.get("event") == "done" and "ts" in mark), default=None)
    operator_sessions = []
    for label, command in (("Coordinator", "/vcoord"), ("Dev", "/vdev")):
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
                sessions=sessions, turn_rows=turn_rows, conductor_spend=spend,
                conductor_turns=sum(r.get("num_turns") or 0 for r in sessions), conductor_model=model,
                conductor_priced=priced, conductor_some_priced=some_priced, conductor_estimated=estimated,
                operator_sessions=operator_sessions,
                issue_wall=awake_span_or_wall(tally.opening, ending, clocked),
                asleep=None if awake_span is None or wall_span is None else max(0, wall_span - awake_span),
                steps_done=counted(len(tally.recovered) + full_suite), planned=planned,
                lane=tunables.get("VERI_LABEL", unless_empty=True),
                flaked=[name for mark in marks if mark.get("event") == "suite-flake"
                        for name in str(mark.get("files", "")).split(",")],
                pinned=pinned,
                model_knobs=dict({knob: tunables.read(knob) for knob in
                                  ["VERI_MODEL", "VERI_MODEL_DEVELOPER", "VERI_MODEL_VERIFIER", "VERI_MODEL_REVISE",
                                   "VERI_MODEL_REVISE_GREEN"]},
                                 VERI_EFFORT_VERIFIER=launched_efforts(marks)),
                phases=tally.counts, by_model=tally.by_model, lost=tally.lost(),
                steps=tally.steps, step_marks=tally.spent, passes=passes, tier_runs=tally.tier_runs,
                adjudications=tally.adjudications, switched_off=tally.switched_off,
                switched_off_by=tally.switched_off_by,
                conductor_counted=tally.conductor_counted, total=tally.total, structural=structural,
                green_rejects=green_rejects,
                green_reject_routes=sorted(routes.items(), key=lambda item: (-item[1], item[0])),
                green_reject_checks=sorted(item for item in checks.items() if item[0]) + [("unnamed", checks[""])],
                launch_costs=tally.launch_costs, launch_cost_missing=tally.launch_cost_missing,
                gradings=tally.gradings, revise_green=revise_green_outcomes(marks, models))


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
    if not f.ended:
        print("Outcome: none yet — the run is still going.")
    elif ending is None and f.cause == "usage-limit":
        print("Outcome: the run hit a usage limit.")
    elif ending is None and f.cause == "killed":
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
    section("#### Total", "run", COST_COLUMNS, {"total": f.total}, estimate=f.conductor_estimated)
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
    """Print the report of `issue`: the journal at `path` and the ledger at `ledger`, folded then laid out."""
    layout(fold(issue, path, ledger))


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
    return {"run": {}, "phases": {phase: json_row(row_counts, PHASE_COLUMNS) for phase, row_counts in f.phases.items()},
            "steps": [], "conductor": {}, "total": {}}


def print_json(issue, path, ledger):
    """Print `as_json` of the journal at `path` as one JSON object, nothing before it is whole."""
    sys.stdout.write(json.dumps(as_json(fold(issue, path, ledger)), indent=2) + "\n")


def main(argv):
    if not argv or not argv[0]:
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
