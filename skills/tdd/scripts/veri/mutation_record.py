"""A run's mutation record, `.tdd/issue-<n>-mutations.md`: the mutation probes a verifier ran.

The one module that spells the record's name and its line format. A record is a run of entries,
each a set of fields `<name> <size>\\n<value>\\n` (size in characters) closed by a blank line; the
text fields old, new and context are stored base64-encoded under `<name>-b64`. mutation_probe
appends entries, pin_recheck reads and rewrites them, tick_ledger prunes them, supervise
snapshots and restores whole files, verify names the file a pin's verifier may append to."""
import base64
import glob
import os
import re

import run_dir

TEXT_FIELDS = ("old", "new", "context")
_NAME = re.compile(r"issue-\d+-mutations\.md")


class MalformedRecord(ValueError):
    """An entry's field header is not `<name> <size>`; `header` is that line."""

    def __init__(self, header):
        super().__init__(header)
        self.header = header


def path(run, issue):
    """`<run>/.tdd/issue-<issue>-mutations.md`. str, never raises."""
    return run_dir.issue_file(run, issue, "-mutations.md")


def of_ledger(ledger_path):
    """The record that sits beside a ledger file: `issue-<n>.md` becomes `issue-<n>-mutations.md`."""
    return re.sub(r"\.md$", "", ledger_path) + "-mutations.md"


def is_record(name):
    """True when the basename of `name` is `issue-<digits>-mutations.md`."""
    return _NAME.fullmatch(name.rsplit("/", 1)[-1]) is not None


def number(record_path):
    """The issue number (str) in a record's file name."""
    return record_path.rsplit("/", 1)[-1].removeprefix("issue-").removesuffix("-mutations.md")


def paths(run=""):
    """The records present in `<run>/.tdd/`, sorted; relative (`.tdd/...`) when `run` is empty."""
    return sorted(glob.glob(run_dir.run_file(run, "issue-*-mutations.md")))


def snapshot(run=""):
    """{path: bytes} of every record present, as paths() names them."""
    out = {}
    for record in paths(run):
        with open(record, "rb") as f:
            out[record] = f.read()
    return out


def format_record(fields):
    """The text of one entry: `fields` is (name, value) pairs or a dict's items; text fields get encoded."""
    out = ""
    for name, value in fields:
        if name in TEXT_FIELDS:
            name, value = name + "-b64", base64.b64encode(value.encode()).decode()
        out += f"{name} {len(value)}\n{value}\n"
    return out + "\n"


def append(record_path, fields):
    """Add one entry to the end of the record, creating it when absent."""
    with open(record_path, "a") as f:
        f.write(format_record(fields))


def chunks(text):
    """[(raw, fields)] per entry: `raw` is its exact text with the blank lines after it, `fields` the
    undecoded {name: value}. Leading blank lines come back as an entry of no fields. Raises MalformedRecord."""
    out, i = [], 0
    while i < len(text):
        start, fields = i, {}
        while i < len(text) and text[i] != "\n":
            end = text.index("\n", i)
            try:
                name, size = text[i:end].split()
                int(size)
            except ValueError:
                raise MalformedRecord(text[i:end])
            fields[name] = text[end + 1:end + 1 + int(size)]
            i = end + 2 + int(size)
        while i < len(text) and text[i] == "\n":
            i += 1
        out.append((text[start:i], fields))
    return out


def records(text):
    """[{name: value}] per entry, text fields decoded."""
    out = []
    for _, fields in chunks(text):
        if not fields:
            continue
        for name in TEXT_FIELDS:
            if name + "-b64" in fields:
                fields[name] = base64.b64decode(fields.pop(name + "-b64")).decode()
        out.append(fields)
    return out


def stale_pins(run, issue):
    """(file, first line of old) per unretired entry of the run's own mutation record whose old text its file, in the
    run's worktree, no longer holds; a missing record or mutated file adds nothing (pin-recheck names a missing file)."""
    try:
        with open(path(run, issue), encoding="utf-8") as f:
            entries = records(f.read())
    except FileNotFoundError:
        return []
    out = []
    for entry in entries:
        if "file" not in entry or "retired" in entry:
            continue
        try:
            with open(os.path.join(run, entry["file"]), encoding="utf-8") as f:
                held = f.read()
        except FileNotFoundError:
            continue
        old = entry.get("old", "")
        if old not in held:
            out.append((entry["file"], (old.strip().splitlines() or [""])[0].strip()))
    return out
