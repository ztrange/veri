"""How skills/tdd/SKILL.md's preflight checks launchability, budgets, GitHub, the worktree baseline and the conductor.pid lock, read as text."""
import functools
import pathlib
import re
import sys
import warnings

import pytest

SKILL = pathlib.Path(__file__).resolve().parents[3].parent / "SKILL.md"

PREFLIGHT_MD = SKILL.with_name("PREFLIGHT.md")
PREFLIGHT = "## 0. Preflight — baseline checks (bail before any cycle)"
SKILL_PREFLIGHT = "#" + PREFLIGHT


TESTS_DIR = pathlib.Path(__file__).resolve().parent
MECHANICAL_READERS = (
    "test_1420_skill_md_s_preflight_discard",
    "test_1967_preflight_step_3_resumed_run_block_is_one_resume_clean_sh_call",
    "skill_md_preflight_leaf_model_calls_name_a_leaf",
    "test_a_gh_auth_status_call_planted_in_skill_md_is_named_as_file_line",
    "test_issue_2375_a_resumed_run_with_a_marker_an_earlier_run_left",
    "test_issue_2375_a_second_conflict_after_the_runs_own_rebase",
    "test_an_edit_to_a_skill_doc_prints_exactly_the_pytest_file_mentioning_it_without_widening",
    "test_every_remaining_case_that_reads_skill_md_s_preflight_section",
    "test_2220_sweep_flags_a_case_reading_the_preflight_section",
    "test_2220_sweep_flags_a_case_reading_a_phrase_only_the_preflight_section",
)
NAMES_PREFLIGHT = re.compile(r"^PREFLIGHT$|#+ .*[Pp]reflight|#+ 0\.|Preflight —")


def plain(text):
    return "\n".join(" ".join(line.replace("`", "").replace("*", "").split()).lower() for line in text.splitlines())


def preflight_and_rest():
    lines = SKILL.read_text().splitlines()
    held = [i for i, line in enumerate(lines) if line == SKILL_PREFLIGHT]
    if held:
        end = next(i for i in range(held[0] + 1, len(lines)) if re.match(r"#{1,3} ", lines[i]))
        lines = lines[:held[0]] + lines[end:]
    preflight, rest = plain(PREFLIGHT_MD.read_text()), plain("\n".join(lines))
    flat = lambda text: " " + " ".join(text.split()) + " "  # padded, so ^ and $ never match a section edge
    return (preflight, flat(preflight)), (rest, flat(rest))


@functools.cache
def only_in_preflight(value, preflight, rest):
    """preflight and rest are each (line by line, all whitespace flattened): a phrase that wraps a line in SKILL.md
    matches only the flattened form, a ^-anchored item pattern only the line-by-line one."""
    if NAMES_PREFLIGHT.search(value):
        return True
    probe = " ".join(value.split())
    if len(probe.split(" ")) < 3:
        return False
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            pattern = re.compile(probe, re.I | re.M)
    except re.error:
        pattern = None
    for inside, outside in zip(preflight, rest, strict=True):
        if plain(probe) in inside and plain(probe) not in outside:
            return True
        if pattern and pattern.search(inside) and not pattern.search(outside):
            return True
    return False


STRING_ASSIGNMENT = re.compile(r"\w+\s*=\s*[rRbBuU]*['\"]")


def preflight_readers(walk, preflight, rest):
    defs = {d.name: d for d in walk.definitions if d.segment.startswith("def ")}
    consts = {d.name: d.literals[0] for d in walk.definitions
              if not d.names and len(d.literals) == 1 and STRING_ASSIGNMENT.match(d.segment)}

    def reads(fn, seen):
        if fn.name in seen:
            return False
        seen.add(fn.name)
        for name in fn.names:
            if NAMES_PREFLIGHT.search(name):
                return True
            if name in consts and only_in_preflight(consts[name], preflight, rest):
                return True
            if name in defs and reads(defs[name], seen):
                return True
        return any(only_in_preflight(value, preflight, rest) for value in fn.constants)

    return [name for name, fn in defs.items() if name.startswith("test_") and reads(fn, set())]


def stray_cases(entries, allowed):
    preflight, rest = preflight_and_rest()
    strays = []
    for entry in entries:
        path = entry.path
        if "SKILL" not in entry.text:
            continue
        for name in preflight_readers(entry.walk, preflight, rest):
            if not any(key in name for key in allowed):
                strays.append(f"{path.relative_to(TESTS_DIR)}::{name}")
    return strays


@pytest.mark.tree_audit("every test module under tests/py, parsed for the cases that read SKILL.md's Preflight section")
def test_every_remaining_case_that_reads_skill_md_s_preflight_section_is_a_named_mechanical_fact_case(tests_py_index):
    strays = stray_cases(tests_py_index, MECHANICAL_READERS)
    assert strays == [], f"cases read the Preflight section but are not on the mechanical-fact allow-list: {strays}"


def test_2220_sweep_flags_a_case_reading_the_preflight_section_until_it_is_on_the_allow_list(tmp_path, monkeypatch):
    from conftest import TestFile
    module = tmp_path / "test_synthetic_reader.py"
    module.write_text(
        'SKILL_MD = "SKILL.md"\n\n\n'
        'def test_reads_the_preflight_section():\n'
        '    assert PREFLIGHT in SKILL_MD\n',
        encoding="utf-8")
    monkeypatch.setattr(sys.modules[__name__], "TESTS_DIR", tmp_path)
    entries = [TestFile(module)]
    key = "test_synthetic_reader.py::test_reads_the_preflight_section"

    assert stray_cases(entries, []) == [key]
    assert stray_cases(entries, ["test_reads_the_preflight_section"]) == []


def test_2220_sweep_flags_a_case_reading_a_phrase_only_the_preflight_section_holds_until_it_is_on_the_allow_list(
        tmp_path, monkeypatch):
    from conftest import TestFile
    (preflight, _), (rest, _) = preflight_and_rest()
    phrase = next(
        line for line in preflight.splitlines()
        if len(line.split()) >= 4 and not re.search(r"['\"\\{}]", line) and line not in rest
        and not NAMES_PREFLIGHT.search(line))
    module = tmp_path / "test_synthetic_reader.py"
    module.write_text(
        'SKILL_MD = "SKILL.md"\n\n\n'
        'def test_reads_a_preflight_phrase():\n'
        '    assert "%s" in SKILL_MD\n' % phrase,
        encoding="utf-8")
    monkeypatch.setattr(sys.modules[__name__], "TESTS_DIR", tmp_path)
    entries = [TestFile(module)]
    key = "test_synthetic_reader.py::test_reads_a_preflight_phrase"

    assert stray_cases(entries, []) == [key]
    assert stray_cases(entries, ["test_reads_a_preflight_phrase"]) == []
