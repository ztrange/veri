"""Cases for which suites still read SKILL.md's `#### A ⟦phases: …⟧ step — each listed phase, a developer leaf then a blind verifier` subsection by its content."""
import pathlib
import sys

import pytest

import subsection_readers

TESTS_PY = pathlib.Path(__file__).resolve().parent
SKILL_MD = TESTS_PY.parents[2] / "SKILL.md"
PHASED_MD = SKILL_MD.with_name("PHASED.md")
PREFIX = "#### A `⟦phases: …⟧` step"
HEADING = "#### A `⟦phases: …⟧` step — each listed phase, a developer leaf then a blind verifier"

MARKERS = (
    "next-phase", "--phase-owed", "--phase <phase>", "production-frozen.sh", "no-product-caller.sh",
)

ALLOWED = {}


SPEC = subsection_readers.Subsection(HEADING, MARKERS, PREFIX)


def _subsection_and_rest():
    return subsection_readers.flat(PHASED_MD.read_text(encoding="utf-8")), subsection_readers.flat(SKILL_MD.read_text(encoding="utf-8"))


def _other_docs():
    return subsection_readers.other_docs(SKILL_MD, exclude=(PHASED_MD,))


def _readers(entry, subsection, rest, docs):
    return subsection_readers.readers(entry, subsection, rest, SPEC, docs)


def stray_cases(entries, allowed):
    subsection, rest = _subsection_and_rest()
    return subsection_readers.stray_cases(entries, allowed, SPEC, subsection, rest, TESTS_PY, __file__, _other_docs())


def lost_cases(entries, allowed):
    subsection, rest = _subsection_and_rest()
    return subsection_readers.lost_cases(entries, allowed, SPEC, subsection, rest, TESTS_PY, __file__, _other_docs())


@pytest.mark.tree_audit("every test file under skills/tdd/scripts/tests/py")
def test_every_remaining_case_reading_the_phases_step_subsection_by_its_content_is_on_the_mechanical_allow_list(tests_py_index):
    stray = stray_cases(tests_py_index, ALLOWED)
    assert stray == [], "cases read the phased-step subsection by content and are neither mechanical nor allow-listed:\n" + "\n".join(stray)
    lost = lost_cases(tests_py_index, ALLOWED)
    assert lost == [], "allow-listed entries no longer read the phased-step subsection:\n" + "\n".join(lost)


def test_2220_sweep_flags_a_case_reading_the_phases_step_subsection_until_it_is_on_the_allow_list(tmp_path, monkeypatch):
    from conftest import TestFile
    module = tmp_path / "test_synthetic_reader.py"
    module.write_text(
        'SKILL_MD = "SKILL.md"\n\n\n'
        'def test_reads_the_phases_step():\n'
        '    assert "--phase-owed" in SKILL_MD\n',
        encoding="utf-8")
    monkeypatch.setattr(sys.modules[__name__], "TESTS_PY", tmp_path)
    monkeypatch.setattr(sys.modules[__name__], "_other_docs", dict)
    entries = [TestFile(module)]
    key = "test_synthetic_reader.py::test_reads_the_phases_step"

    assert stray_cases(entries, {}) == [key]
    assert stray_cases(entries, {key: "mechanical: synthetic"}) == []
