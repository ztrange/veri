"""Cases for which suites still read SKILL.md's `#### A ⟦diff-checked⟧ step — develop-diff, then verify-diff (blind)` subsection by its content."""
import pathlib
import re

import pytest

TESTS_PY = pathlib.Path(__file__).resolve().parent.parent
SKILL_MD = TESTS_PY.parents[2] / "SKILL.md"
PREFIX = "#### A `⟦diff-checked⟧` step"
HEADING = "#### A `⟦diff-checked⟧` step — develop-diff, then verify-diff (blind)"

MARKERS = (
    HEADING, "verdict-diff", "<step-base-sha>", "revise-diff-<k>",
    "git log -1 --format=%H -- .tdd/issue-<n>.md",
)

ALLOWED = {
    "test_skill_leaf_launch.py": "parses the document's launch lines and runs the leaf-launch guard over them, the develop-diff and verdict-diff lines among them",
    "test_skill_leaf_env.py": "runs every launch line against a stub claude and checks what the leaf saw",
    "test_suite_reported_process.py": "runs suite-reported.sh, which the subsection calls",
    "test_build_develop_prompt_process.py": "runs build-develop-prompt.sh, which the subsection calls",
    "test_verify.py": "runs the verifier script the subsection calls",
    "test_prompt_test_tiers.py": "checks the tiers a rendered prompt names",
    "unit/test_build_develop_prompt.py": "unit cases of build-develop-prompt.sh",
    "unit/test_build_verify_prompt.py": "unit cases of build-verify-prompt.sh",
    "unit/test_ledger.py": "unit cases of the ledger helper",
    "unit/test_skill_verify_step.py": "no CY row: document-wide; verify.sh calls only",
    "unit/test_skill_stopping.py": "no CY row: document-wide stop-check cases",
    "unit/test_skill_event_files.py::test_every_line_sending_the_run_into_the_revise_loop_points_at_revise_md_1855":
        "no CY row: document-wide site list",
    "test_skill_leaf_env.py::test_907_the_revise_diff_prompt_line": "runs build-develop-prompt.sh revise diff from REVISE.md",
}


def _flat(text):
    return " ".join(text.split())


def _subsection_and_rest():
    text = SKILL_MD.read_text(encoding="utf-8")
    start = text.index(HEADING)
    following = re.search(r"^#{1,4} ", text[start + len(HEADING):], re.M)
    stop = start + len(HEADING) + following.start() if following else len(text)
    return _flat(text[start:stop]), _flat(text[:start] + "\n" + text[stop:])


def _names_the_heading(literal):
    """The subsection's heading, or a prefix of it from `#### A `⟦diff-checked⟧` step` on: a case slicing SKILL.md by it
    reads the subsection whatever it asserts, however short."""
    return literal.startswith(PREFIX) and HEADING.startswith(literal)


def _only_in_subsection(literal, subsection, rest):
    """A phrase a case could only have copied from the diff-checked subsection: three or more words no
    other part of SKILL.md, nor another skill document the case names, carries.
    One or two words read as script vocabulary or a case's own message, so neither counts."""
    flat = _flat(literal)
    return len(flat.split(" ")) >= 3 and flat in subsection and flat not in rest


def _other_docs():
    return {d.name: d.read_text(encoding="utf-8") for d in SKILL_MD.parent.glob("*.md") if d != SKILL_MD}


def _readers(entry, subsection, rest, docs):
    text = entry.text
    if "SKILL" not in text:
        return []
    definitions = entry.walk.definitions
    segments = {d.name: d.segment for d in definitions}
    literals = {d.name: d.strings for d in definitions}
    reads = {d.name: set(d.names) for d in definitions}
    calls = {
        name: {o for o in segments if o != name and re.search(r"\b%s\b" % re.escape(o), src)}
        for name, src in segments.items()
    }

    def reach(name):
        seen, todo = {name}, [name]
        while todo:
            for other in calls[todo.pop()] - seen:
                seen.add(other)
                todo.append(other)
        return seen

    def reads_the_subsection(names):
        source = "\n".join(segments[n] for n in names)
        also_read = [text for doc, text in docs.items() if doc in source]
        markers = [m for m in MARKERS if not any(m in text for text in also_read)]
        held_elsewhere = _flat("\n".join([rest, *also_read]))
        return any(m in source for m in markers) or any(
            _names_the_heading(s) or _only_in_subsection(s, subsection, held_elsewhere) for n in names for s in literals[n])

    return sorted(
        name for name in segments
        if name.startswith("test_")
        and reads_the_subsection(reach(name))
        and any(re.fullmatch(r"SKILL(?:_MD)?|skill_lines", i) for n in reach(name) for i in reads[n])
    )


@pytest.mark.tree_audit("every test file under skills/tdd/scripts/tests/py")
def test_every_remaining_case_reading_the_diff_checked_subsection_by_its_content_is_on_the_mechanical_allow_list(tests_py_index):
    subsection, rest = _subsection_and_rest()
    docs = _other_docs()
    stray = []
    for entry in tests_py_index:
        path = entry.path
        if path == pathlib.Path(__file__).resolve():
            continue
        rel = str(path.relative_to(TESTS_PY))
        if rel in ALLOWED:
            continue
        stray += [f"{rel}::{name}" for name in _readers(entry, subsection, rest, docs) if f"{rel}::{name}" not in ALLOWED
                  and f"{path.name}::{name}" not in ALLOWED]
    assert stray == [], "cases read the diff-checked subsection by content and are neither mechanical nor allow-listed:\n" + "\n".join(stray)
