"""Cases for which suites still read SKILL.md's `#### A ⟦phases: …⟧ step — each listed phase, a developer leaf then a blind verifier` subsection by its content."""
import ast
import pathlib
import re

import pytest

TESTS_PY = pathlib.Path(__file__).resolve().parent.parent
SKILL_MD = TESTS_PY.parents[2] / "SKILL.md"
PREFIX = "#### A `⟦phases: …⟧` step"
HEADING = "#### A `⟦phases: …⟧` step — each listed phase, a developer leaf then a blind verifier"

MARKERS = (
    HEADING, "next-phase", "--phase-owed", "--phase <phase>", "production-frozen.sh", "no-product-caller.sh",
)

ALLOWED = {
    "unit/test_skill_refactor_kind.py::test_skill_md_puts_mutation_parity_sh_s_report_into_the_pr_body_as_the_pairs_table_and_each_row_it_reports_owed_under_owed_by_a_human":
        "windows around every mutation-parity.sh in the document",
    "unit/test_skill_refactor_kind.py::test_skill_md_s_draft_pr_step_puts_the_conductor_s_mutation_parity_sh_report_into_the_pr_body_template_…":
        "windows around every mutation-parity.sh in the document",
    "unit/test_skill_stopping.py::test_each_phases_leaf_exit_2_branch_points_back_to_launching_a_leaf_where_stop_requested_is_asked_before_the_exit_2_is_read_as_killed_stuck":
        "its rows are verify-plan, Red, Green, Refactor loop and Revising",
    "unit/test_skill_event_files.py::test_every_line_sending_the_run_into_the_revise_loop_points_at_revise_md_1855":
        "document-wide site list",
    "unit/test_skill_suite_runs.py::test_skill_md_s_phase_sections_and_claude_md_say_which_leaves_run_the_full_suite":
        "reads Red, the Refactor loop and CLAUDE.md, not this subsection",
    "test_skill_leaf_launch.py": "launch lines are Launching a leaf instances",
    "test_skill_leaf_env.py": "launch lines are Launching a leaf instances",
    "test_ledger_steps.py": "script suite", "test_tick_ledger.py": "script suite", "test_next_unchecked.py": "script suite",
    "test_transform_touches_tests.py": "script suite", "test_production_frozen_process.py": "script suite",
    "test_no_product_caller_process.py": "script suite", "test_tests_frozen_process.py": "script suite",
    "test_suite_reported_process.py": "script suite", "test_prompt_test_tiers.py": "script suite",
    "test_build_develop_prompt.py": "script suite", "test_build_verify_prompt.py": "script suite",
    "test_metrics.py": "the phases fixtures",
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
    """The subsection's heading, or a prefix of it from `#### A `⟦phases: …⟧` step` on: a case slicing SKILL.md by it
    reads the subsection whatever it asserts, however short."""
    return literal.startswith(PREFIX) and HEADING.startswith(literal)


def _only_in_subsection(literal, subsection, rest):
    """A phrase a case could only have copied from the phased-step subsection: three or more words no
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
def test_every_remaining_case_reading_the_phases_step_subsection_by_its_content_is_on_the_mechanical_allow_list(tests_py_index):
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
    assert stray == [], "cases read the phased-step subsection by content and are neither mechanical nor allow-listed:\n" + "\n".join(stray)
