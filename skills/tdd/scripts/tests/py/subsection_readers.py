"""The engine behind the audits that name which test cases still read one SKILL.md subsection by its content.

Vocabulary, as these audits use it:

- subsection: the slice of SKILL.md from one `####` heading to the next heading of level 1 to 4 (the whole
  of another document, such as PHASED.md or DRAFT-PR.md, when the subsection lives in its own file). `rest` is
  everything else in SKILL.md.
- flat: a text with every run of whitespace collapsed to one space, so a line break in the document or in a
  literal never decides a match.
- reader: a test case that, directly or through the module-level functions and constants it mentions, both
  reaches SKILL.md (a name such as SKILL, SKILL_MD, skill_lines or skill_sections; with `Subsection.path_literal`,
  also a string literal that is a path ending in SKILL.md, which a fixture repo's synthetic SKILL.md would trip) and
  reads this subsection: it carries one of the spec's markers, names the heading (or a prefix of it from
  `Subsection.prefix` on), or carries a literal of three or more words that the subsection holds and no other
  part of SKILL.md does. One or two words read as script vocabulary or a case's own message, so neither counts.
  A case that names another skill document is judged against `rest` plus that document, since a phrase the
  other document also carries is not the subsection's alone (`docs`, off when empty).

An audit keeps its own data (heading, markers, allow-list) and its own case; this module owns detection.
Cases are found through the shared `tests_py_index` entries, never by walking the tree here.
"""
import dataclasses
import functools
import pathlib
import re

from tree_index import mentioned_names

SKILL_NAMES = r"SKILL(?:_MD)?|skill_lines|skill_sections"
# SKILL.md reached through a path literal, whatever the variable is called: `SCRIPTS.parent / "SKILL.md"`.
SKILL_PATH_LITERAL = re.compile(r"(?:.*/)?SKILL\.md")


@dataclasses.dataclass(frozen=True)
class Subsection:
    heading: str
    markers: tuple
    prefix: str = None  # a literal that starts with it and is a prefix of the heading names the heading
    heading_in_any_case: object = None  # a regex a literal may also match to name the heading
    source_names: str = SKILL_NAMES  # identifiers that mean the audited document is being read
    gate: tuple = ("SKILL",)  # a file whose text carries none of these is not looked at
    path_literal: object = None  # a regex a string literal may fullmatch to mean the document is read, name or no name


def flat(text):
    return " ".join(text.split())


def cut_subsection(text, heading):
    """(flat subsection, flat rest) of `text` cut at `heading`: up to the next heading of level 1 to 4."""
    start = text.index(heading)
    following = re.search(r"^#{1,4} ", text[start + len(heading):], re.M)
    stop = start + len(heading) + following.start() if following else len(text)
    return flat(text[start:stop]), flat(text[:start] + "\n" + text[stop:])


def other_docs(skill_md, exclude=()):
    """The sibling skill documents by file name, but SKILL.md and `exclude`."""
    return {d.name: d.read_text(encoding="utf-8") for d in skill_md.parent.glob("*.md") if d != skill_md and d not in exclude}


@functools.cache
def _held(rest, *also_read):
    return flat("\n".join([rest, *also_read]))


def names_the_heading(literal, spec):
    prefix = spec.prefix or spec.heading
    return (literal.startswith(prefix) and spec.heading.startswith(literal)) or bool(
        spec.heading_in_any_case and spec.heading_in_any_case.match(literal))


def only_in_subsection(literal, subsection, rest):
    f = flat(literal)
    return len(f.split(" ")) >= 3 and f in subsection and f not in rest


def readers(entry, subsection, rest, spec, docs=None):
    """The `test_*` cases of one index entry that read the subsection (see the module docstring), sorted."""
    text = entry.text
    if not any(word in text for word in spec.gate):
        return []
    docs = docs or {}
    definitions = entry.walk.definitions
    segments = {d.name: d.segment for d in definitions}
    literals = {d.name: d.strings + d.byte_strings for d in definitions}
    reads = {d.name: set(d.names) for d in definitions}
    calls = mentioned_names(segments)

    def reach(name):
        seen, todo = {name}, [name]
        while todo:
            for other in calls[todo.pop()] - seen:
                seen.add(other)
                todo.append(other)
        return seen

    def reads_the_subsection(names):
        source = "\n".join(segments[n] for n in names)
        also_read = [doc for name, doc in docs.items() if name in source]
        markers = [m for m in spec.markers if not any(m in doc for doc in also_read)]
        held_elsewhere = _held(rest, *also_read)
        return any(m in source for m in markers) or any(
            names_the_heading(s, spec) or only_in_subsection(s, subsection, held_elsewhere)
            for n in names for s in literals[n])

    def reaches_the_document(names):
        return (any(re.fullmatch(spec.source_names, i) for n in names for i in reads[n])
                or (spec.path_literal and any(spec.path_literal.fullmatch(s) for n in names for s in literals[n])))

    found = []
    for name in segments:
        if name.startswith("test_"):
            names = reach(name)
            if reads_the_subsection(names) and reaches_the_document(names):
                found.append(name)
    return sorted(found)


def stray_cases(entries, allowed, spec, subsection, rest, tests_py, own_path, docs=None):
    """`<path under tests_py>::<case>` of every reader in `entries` that `allowed` names neither as a whole file
    (keyed by the path under tests_py, never a bare file name) nor as a case (by either path form). `own_path`,
    the audit's own file, is skipped."""
    stray = []
    for entry in entries:
        path = entry.path
        if path == pathlib.Path(own_path).resolve():
            continue
        rel = str(path.relative_to(tests_py))
        if rel in allowed:
            continue
        stray += [f"{rel}::{name}" for name in readers(entry, subsection, rest, spec, docs)
                  if f"{rel}::{name}" not in allowed and f"{path.name}::{name}" not in allowed]
    return stray


def lost_cases(entries, allowed, spec, subsection, rest, tests_py, own_path, docs=None):
    """Each `allowed` entry, sorted, that `readers` no longer finds reading the subsection: a whole-file entry
    (keyed by the path under tests_py) none of whose cases reads it, a case entry (by either path form) that does
    not. An entry naming no file in `entries` is lost too. `own_path`, the audit's own file, is skipped."""
    found = set()
    for entry in entries:
        path = entry.path
        if path == pathlib.Path(own_path).resolve():
            continue
        rel = str(path.relative_to(tests_py))
        names = readers(entry, subsection, rest, spec, docs)
        if names:
            found.add(rel)
        found.update(f"{form}::{name}" for name in names for form in (rel, path.name))
    return sorted(key for key in allowed if key not in found)
