"""Cases of `subsection_readers` over planted indexes, never the real test tree."""
import subsection_readers
from conftest import TestFile

HEADING = "#### Planted step"
SPEC = subsection_readers.Subsection(HEADING, ("planted-marker.sh",))
SUBSECTION, REST = subsection_readers.cut_subsection(
    "# Doc\n\nintro\n\n#### Planted step\n\nrun planted-marker.sh\n\n#### Other\n\nelse\n", HEADING)

READER = (
    'SKILL_MD = "SKILL.md"\n\n\n'
    'def test_reads():\n'
    '    assert "planted-marker.sh" in SKILL_MD\n\n\n'
    'def test_also_reads():\n'
    '    assert "planted-marker.sh" in SKILL_MD\n')


def _index(tmp_path, files):
    for name, text in files.items():
        (tmp_path / name).write_text(text, encoding="utf-8")
    return [TestFile(tmp_path / name) for name in files]


def _lost(entries, allowed, tmp_path):
    return subsection_readers.lost_cases(entries, allowed, SPEC, SUBSECTION, REST, tmp_path, tmp_path / "test_audit.py")


def test_lost_cases_names_an_allowed_entry_whose_reading_line_was_removed_and_every_allowed_entry_when_no_case_reads(tmp_path):
    allowed = {"test_a.py::test_reads": "planted", "test_a.py::test_also_reads": "planted", "test_b.py": "planted"}
    reading = _index(tmp_path, {"test_a.py": READER, "test_b.py": READER})
    assert _lost(reading, allowed, tmp_path) == []

    one_line_gone = _index(tmp_path, {"test_a.py": READER.replace('    assert "planted-marker.sh" in SKILL_MD\n\n\n', '    pass\n\n\n', 1),
                                      "test_b.py": READER})
    assert _lost(one_line_gone, allowed, tmp_path) == ["test_a.py::test_reads"]

    no_reader = _index(tmp_path, {"test_a.py": READER.replace("planted-marker.sh", "x"), "test_b.py": "def test_x():\n    pass\n"})
    assert _lost(no_reader, allowed, tmp_path) == sorted(allowed)
