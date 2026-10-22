"""Cases for which suites still read SKILL.md's `#### Green — minimum implementation (developer leaf), then verify-green (blind)` subsection by its content."""
import ast
import pathlib
import re

import pytest

TESTS_PY = pathlib.Path(__file__).resolve().parent.parent
SKILL_MD = TESTS_PY.parents[2] / "SKILL.md"
PREFIX = "#### Green"
HEADING = "#### Green — minimum implementation (developer leaf), then verify-green (blind)"

MARKERS = (
    HEADING, "wrong-test-route.sh", "red-contradicted", "red-supersede",
)

ALLOWED = {
    "test_skill_leaf_launch.py": "parses the document's launch lines and runs the leaf-launch guard over them, Green's among them",
    "test_skill_leaf_env.py": "runs every launch line against a stub claude and checks what the leaf saw",
    "unit/test_skill_suite_runs.py::test_698_case_1_passes_on_a_skill_md_whose_green_section_and_refactor_loop_name_no_full_suite_run":
        "mutates a fixture copy and checks the helper; asserts nothing about Green's text",
    "unit/test_skill_suite_runs.py::test_991_doc_text_given_the_from_regex_5_starts_at_the_line_5_y_not_at_5x_y":
        "tests the doc_text helper on a scratch file",
    "unit/test_skill_tests_frozen.py::test_green_and_revising_handle_check_exit_2_as_a_system_failure_bail_never_a_reject":
        "asserts REVISE.md's sentence, not Green's",
    "unit/test_skill_tests_frozen.py::test_revising_routes_a_revise_green_wrong_test_report_through_wrong_test_route_never_a_report_missing_bail":
        "asserts REVISE.md's sentence, not Green's",
    "unit/test_skill_refactor_kind.py::test_skill_md_puts_mutation_parity_sh_s_report_into_the_pr_body_as_the_pairs_table_and_each_row_it_reports_owed_under_owed_by_a_human":
        "no CY row: document-wide; searches every mutation-parity.sh in the document",
    "unit/test_skill_event_files.py::test_every_line_sending_the_run_to_stopping_points_at_stopping_md_1716":
        "names the Green heading only to exclude it",
    "unit/test_skill_event_files.py::test_every_line_launching_the_reconcile_leaf_points_at_reconcile_md_1716":
        "names the Green heading only to exclude it",
    "unit/test_skill_event_files.py::test_every_line_sending_the_run_into_the_revise_loop_points_at_revise_md_1855":
        "names the Green heading only to exclude it",
    "unit/test_skill_tests_frozen.py::test_every_tests_frozen_record_and_check_names_the_record_by_path_over_the_step_text_and_red_defines_the_key":
        "names the Green heading only to exclude it",
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
    """The subsection's heading, or a prefix of it from `#### Green` on: a case slicing SKILL.md by it
    reads the subsection whatever it asserts, however short."""
    return literal.startswith(PREFIX) and HEADING.startswith(literal)


def _only_in_subsection(literal, subsection, rest):
    """A phrase a case could only have copied from the Green subsection: three or more words no
    other part of SKILL.md carries.
    One or two words read as script vocabulary or a case's own message, so neither counts."""
    flat = _flat(literal)
    return len(flat.split(" ")) >= 3 and flat in subsection and flat not in rest


def _readers(entry, subsection, rest):
    text = entry.text
    if "SKILL" not in text:
        return []
    tree = entry.tree
    own = [
        n for n in tree.body
        if isinstance(n, (ast.FunctionDef, ast.Assign))
    ]
    segments, literals, reads = {}, {}, {}
    for node in own:
        fragments = {id(v) for j in ast.walk(node) if isinstance(j, ast.JoinedStr) for v in j.values}
        strings = [c.value for c in ast.walk(node)
                   if isinstance(c, ast.Constant) and isinstance(c.value, str) and id(c) not in fragments]
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
        return any(m in source for m in MARKERS) or any(
            _names_the_heading(s) or _only_in_subsection(s, subsection, rest) for n in names for s in literals[n])

    return sorted(
        name for name in segments
        if name.startswith("test_")
        and reads_the_subsection(reach(name))
        and any(re.fullmatch(r"SKILL(?:_MD)?|skill_lines", i) for n in reach(name) for i in reads[n])
    )


@pytest.mark.tree_audit("every test file under skills/tdd/scripts/tests/py")
def test_every_remaining_case_reading_the_green_subsection_by_its_content_is_on_the_mechanical_allow_list(tests_py_index):
    subsection, rest = _subsection_and_rest()
    stray = []
    for entry in tests_py_index:
        path = entry.path
        if path == pathlib.Path(__file__).resolve():
            continue
        rel = str(path.relative_to(TESTS_PY))
        if rel in ALLOWED:
            continue
        stray += [f"{rel}::{name}" for name in _readers(entry, subsection, rest) if f"{rel}::{name}" not in ALLOWED
                  and f"{path.name}::{name}" not in ALLOWED]
    assert stray == [], "cases read the Green subsection by content and are neither mechanical nor allow-listed:\n" + "\n".join(stray)
