"""Cases for which suites still read SKILL.md's `#### Refactor loop — one leaf applies the step's transforms, then verify-refactor (blind, once)` subsection by its content."""
import ast
import pathlib
import re

import pytest

TESTS_PY = pathlib.Path(__file__).resolve().parent
SKILL_MD = TESTS_PY.parents[2] / "SKILL.md"
PREFIX = "#### Refactor loop"
HEADING = "#### Refactor loop — one leaf applies the step's transforms, then verify-refactor (blind, once)"

MARKERS = (
    HEADING, ".tdd/develop-refactor.out", "refactor-triage.sh", "verify-refactor.log", "nothing left to tidy",
    "uncovered-spec", "beyond-spec", "overfit",
)

ALLOWED = {
    "unit/test_skill_refactor_footer.py::test_skill_md_refactor_section_names_exactly_the_report_lines_the_built_refactor_prompt_asks_the_leaf_for":
        "mechanical: two-sided RESULT:/CANDIDATES:/FLAGS: label parity with the built refactor prompt",
    "unit/test_skill_suite_runs.py::test_skill_md_names_no_full_suite_run_inside_a_step_s_cycle":
        "document-wide absence over Red to Draft PR; the Draft PR slice owns it",
    "unit/test_skill_suite_runs.py::test_1300_skill_md_runs_suite_reported_sh_only_after_a_leaf_whose_prompt_asks_for_a_suite_line_never_after_the_refactor_leaf_or_a_revise_of_red_green_or_refactor":
        "absence assertion; the prose states nothing about it",
    "test_skill_leaf_env.py": "launch lines are Launching a leaf instances",
}

# A heading named in any case, as a regex or a plain string: `(?i)^#{4}\s+refactor\s+loop`, `#### refactor loop`,
# `refactor loop`. Optional anchors, inline flags, `#` runs and whitespace may lead; `refactor` then `loop` must follow.
HEADING_IN_ANY_CASE = re.compile(
    r"(?:\(\?[a-zA-Z]+\)|\^|\\A|\\?#|\[#\]|\{\d+(?:,\d*)?\}|[+*?]|\s|\\s)*"
    r"refactor(?:\s|\\s|[+*.]|\[ \])+loop",
    re.I)

# SKILL.md reached through a path literal, whatever the variable is called: `SCRIPTS.parent / "SKILL.md"`.
SKILL_PATH_LITERAL = re.compile(r"(?:.*/)?SKILL\.md")


def _flat(text):
    return " ".join(text.split())


def _subsection_and_rest():
    text = SKILL_MD.read_text(encoding="utf-8")
    start = text.index(HEADING)
    following = re.search(r"^#{1,4} ", text[start + len(HEADING):], re.M)
    stop = start + len(HEADING) + following.start() if following else len(text)
    return _flat(text[start:stop]), _flat(text[:start] + "\n" + text[stop:])


def _names_the_heading(literal):
    """The subsection's heading, or a prefix of it from `#### Refactor loop` on, in any case and as a regex too: a
    case slicing SKILL.md by it reads the subsection whatever it asserts, however short."""
    return (literal.startswith(PREFIX) and HEADING.startswith(literal)) or bool(HEADING_IN_ANY_CASE.match(literal))


def _only_in_subsection(literal, subsection, rest):
    """A phrase a case could only have copied from the Refactor loop subsection: three or more words no
    other part of SKILL.md, nor another skill document the case names, carries.
    One or two words read as script vocabulary or a case's own message, so neither counts."""
    flat = _flat(literal)
    return len(flat.split(" ")) >= 3 and flat in subsection and flat not in rest


def _other_docs():
    return {d.name: d.read_text(encoding="utf-8") for d in SKILL_MD.parent.glob("*.md") if d != SKILL_MD}


def _readers(path, subsection, rest, docs):
    text = path.read_text(encoding="utf-8")
    if "SKILL" not in text:
        return []
    tree = ast.parse(text)
    own = [
        n for n in tree.body
        if isinstance(n, (ast.FunctionDef, ast.Assign))
    ]
    segments, literals, reads = {}, {}, {}
    for node in own:
        fragments = {id(v) for j in ast.walk(node) if isinstance(j, ast.JoinedStr) for v in j.values}
        strings = [c.value if isinstance(c.value, str) else c.value.decode("utf-8", "replace") for c in ast.walk(node)
                   if isinstance(c, ast.Constant) and isinstance(c.value, (str, bytes)) and id(c) not in fragments]
        names = {n.id for n in ast.walk(node) if isinstance(n, ast.Name)}
        if isinstance(node, ast.FunctionDef):
            segments[node.name] = ast.get_source_segment(text, node)
            literals[node.name] = strings
            reads[node.name] = names
        else:
            for target in node.targets:
                if isinstance(target, ast.Name):
                    segments[target.id] = ast.get_source_segment(text, node.value)
                    literals[target.id] = strings
                    reads[target.id] = names
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
        and (any(re.fullmatch(r"SKILL(?:_MD)?|skill_lines", i) for n in reach(name) for i in reads[n])
             or any(SKILL_PATH_LITERAL.fullmatch(s) for n in reach(name) for s in literals[n]))
    )


@pytest.mark.tree_audit("every test file under skills/tdd/scripts/tests/py")
def test_every_remaining_case_reading_the_refactor_loop_subsection_by_its_content_is_on_the_mechanical_allow_list():
    subsection, rest = _subsection_and_rest()
    docs = _other_docs()
    stray = []
    for path in sorted(TESTS_PY.rglob("test_*.py")):
        if path == pathlib.Path(__file__).resolve():
            continue
        rel = str(path.relative_to(TESTS_PY))
        if rel in ALLOWED:  # a whole-file entry: keyed by the path under tests/py, never a bare file name
            continue
        stray += [f"{rel}::{name}" for name in _readers(path, subsection, rest, docs) if f"{rel}::{name}" not in ALLOWED
                  and f"{path.name}::{name}" not in ALLOWED]
    assert stray == [], "cases read the Refactor loop subsection by content and are neither mechanical nor allow-listed:\n" + "\n".join(stray)
