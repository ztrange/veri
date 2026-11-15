"""The one module that knows a run's journal, `<run>/.tdd/events.jsonl`: where it is, how a
line parses, and which events of a kind it holds (#281).

Interface by run (the run directory; "." for the current run):
  path(run)                       the journal's path
  events(run, *kinds, ...)        the events of those kinds (all when none), in journal order
  last(run, kind, ...)            the last event of a kind, or None

Interface by path (a journal file already in hand):
  read_events, read_json_lines, append_bytes, usage_totals

A run with no journal has no events: `events` returns [] and `last` None. A journal that
exists but cannot be opened (a directory, no permission) raises OSError.
"""
import json
from pathlib import Path

try:
    from run_dir import run_file
except ImportError:
    from .run_dir import run_file
import json
from pathlib import Path

TOKEN_KINDS = ("input_tokens", "output_tokens", "cache_read_input_tokens",
               "cache_creation_input_tokens")


def read_events(path, skip_unreadable=False, mark_unreadable=False, errors="replace"):
    """The log's events, one dict per non-blank line; skip_unreadable drops lines that
    are not a JSON object, mark_unreadable keeps each as None."""
    events = []
    with open(path, encoding="utf-8", errors=errors) as f:
        for raw in f:
            if not raw.strip():
                continue
            try:
                event = json.loads(raw)
                if not isinstance(event, dict):
                    raise ValueError("not a JSON object: " + raw.strip())
            except ValueError as error:
                error.line = raw.rstrip("\n")
                if mark_unreadable:
                    events.append(None)
                    continue
                if skip_unreadable:
                    continue
                refusal = ValueError(f"{path}: {error}")
                refusal.line = error.line
                raise refusal from error
            events.append(event)
    return events


def path(run):
    """The path of `run`'s journal, whether or not it exists."""
    return run_file(run, "events.jsonl")


def events(run, *kinds, skip_unreadable=False, errors="replace"):
    """The events of `run`'s journal whose "event" is one of `kinds` (every event when no
    kind is given), in journal order; [] when the run has no journal. An unreadable line
    (not a JSON object) raises ValueError naming the journal, unless skip_unreadable drops
    it; errors="strict" makes an undecodable byte raise UnicodeDecodeError instead of
    becoming U+FFFD."""
    try:
        found = read_events(path(run), skip_unreadable=skip_unreadable, errors=errors)
    except FileNotFoundError:
        return []
    return [e for e in found if not kinds or e.get("event") in kinds]


def last(run, kind, **tolerance):
    """The last event of `kind` in `run`'s journal, or None when there is none or no
    journal. Takes `events`' skip_unreadable and errors; raises as `events` does."""
    found = events(run, kind, **tolerance)
    return found[-1] if found else None


def read_json_lines(path):
    """The log's JSON lines as text, each with its line ending kept; a line that is not
    valid UTF-8 or not JSON is dropped."""
    lines = []
    with open(path, "rb") as f:
        for raw in f:
            try:
                text = raw.decode("utf-8")
                json.loads(text)
            except ValueError:
                continue
            lines.append(text)
    return lines


def append_bytes(path, data):
    with open(path, "ab") as f:
        f.write(data)


def usage_totals(events):
    """(dollars, tokens) summed over the usage events."""
    dollars, tokens = 0.0, 0
    for line in events:
        if line.get("event") == "usage":
            dollars += float(line.get("total_cost_usd") or 0)
            tokens += sum(int(line.get(kind) or 0) for kind in TOKEN_KINDS)
    return dollars, tokens


def run_keeping_journal(run):
    journal = Path(".tdd/events.jsonl")
    before = journal.read_bytes() if journal.exists() else None
    ran = run()
    if before is not None and not journal.read_bytes().startswith(before):
        journal.write_bytes(before)
    return ran
