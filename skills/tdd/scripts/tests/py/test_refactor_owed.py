"""In-process cases for veri/refactor_owed.py, the module refactor-owed.sh is a shim over."""
import importlib
import io
import pathlib
import sys

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
for path in (SCRIPTS, SCRIPTS / "veri"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

USAGE = (
    "refactor-owed: usage: refactor-owed.sh append <file> '<STEP>' < leaf-report.txt\n"
    "                      refactor-owed.sh render <file>\n"
    "                      refactor-owed.sh list <file>\n"
)


@pytest.fixture
def refactor_owed():
    return importlib.import_module("veri.refactor_owed")


def test_main_refuses_a_missing_argument_or_unknown_verb_with_the_usage_text_and_answers_within_0_to_3(
        monkeypatch, capsys, tmp_path, refactor_owed):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "stdin", io.StringIO(""))

    for argv in ([], ["list"], ["", "f"], ["list", ""], ["bogus", "f"]):
        code = refactor_owed.main(argv)
        captured = capsys.readouterr()
        assert (argv, code, captured.out, captured.err) == (argv, 2, "", USAGE)
        assert (argv, sorted(p.name for p in tmp_path.iterdir())) == (argv, [])

    empty = tmp_path / "empty.md"
    empty.write_text("")
    for argv in (["list", str(tmp_path / "absent.md")], ["render", str(empty)]):
        code = refactor_owed.main(argv)
        captured = capsys.readouterr()
        assert (argv, code, captured.out) == (argv, 3, "")

    owed = tmp_path / "owed.md"
    monkeypatch.setattr(sys, "stdin", io.StringIO("CANDIDATES: structural | x\n"))
    code = refactor_owed.main(["append", str(owed), "S"])
    assert code == 0


def test_append_writes_a_test_only_line_under_the_step_as_test_only_candidate_answers_and_no_other_class_as_test_only(
        monkeypatch, tmp_path, refactor_owed):
    step = "append records a test-only candidate as test_only_candidate answers it"
    for line, transform in (
            ("CANDIDATES: test-only | fold the two fixtures into one", "fold the two fixtures into one"),
            ("CANDIDATES: structural | extract the parser", None),
            ("CANDIDATES: cosmetic | rename x to count", None),
            ("CANDIDATES: none", None)):
        owed = tmp_path / "owed.md"
        if owed.exists():
            owed.unlink()
        monkeypatch.setattr(sys, "stdin", io.StringIO(line + "\n"))
        code = refactor_owed.main(["append", str(owed), step])
        text = owed.read_text() if owed.exists() else ""
        assert (line, code) == (line, 0)
        if transform is None:
            assert (line, [l for l in text.splitlines() if l.startswith("- test-only | ")]) == (line, [])
            if not line.startswith("CANDIDATES: structural"):
                assert (line, owed.exists()) == (line, False)
        else:
            assert (line, text) == (line, f"### {step}\n- test-only | {transform}\n")


def test_append_counts_only_an_unindented_candidate_line_and_records_its_transform_after_the_bar_and_its_blanks(
        monkeypatch, tmp_path, refactor_owed):
    owed = tmp_path / "owed.md"
    report = ("CANDIDATES:structural|a\n"
              "  CANDIDATES: structural | b\n"
              "CANDIDATES: Structural | c\n"
              "CANDIDATES:   structural   |   e  \n"
              "CANDIDATES: structural | f | g\n"
              "CANDIDATES: structural |\n"
              "CANDIDATES: structural | h\r\n"
              "CANDIDATES: cosmetic | rename k\n"
              "junk line\n")
    monkeypatch.setattr(sys, "stdin", io.StringIO(report))
    code = refactor_owed.main(["append", str(owed), "S"])
    written = owed.read_bytes() if owed.exists() else b""
    assert (code, written) == (0, b"### S\n- a\n- e  \n- f | g\n- \n- h\r\n")


def test_append_writes_structural_before_test_only_and_appends_a_block_only_when_a_line_is_owed(
        monkeypatch, tmp_path, refactor_owed):
    owed = tmp_path / "owed.md"
    owed.write_bytes(b"prior\n")
    monkeypatch.setattr(sys, "stdin", io.StringIO("CANDIDATES: test-only | t1\n"
                                                  "CANDIDATES: structural | s1\n"
                                                  "CANDIDATES: test-only | t2\n"
                                                  "CANDIDATES: structural | s2"))
    code = refactor_owed.main(["append", str(owed), "", "src/a.sh", "tests/x"])
    assert (code, owed.read_bytes()) == (
        0, b"prior\n### \n- s1\n- s2\n- test-only | t1\n- test-only | t2\n")

    absent = tmp_path / "absent.md"
    monkeypatch.setattr(sys, "stdin", io.StringIO("CANDIDATES: cosmetic | rename k\njunk line\n"))
    code = refactor_owed.main(["append", str(absent), "S"])
    assert (code, absent.exists()) == (0, False)

    before = owed.read_bytes()
    monkeypatch.setattr(sys, "stdin", io.StringIO("CANDIDATES: cosmetic | rename k\njunk line\n"))
    code = refactor_owed.main(["append", str(owed), "S"])
    assert (code, owed.read_bytes()) == (0, before)


def test_append_with_no_step_argument_writes_the_block_under_an_empty_step_heading(
        monkeypatch, tmp_path, refactor_owed):
    owed = tmp_path / "owed.md"
    monkeypatch.setattr(sys, "stdin", io.StringIO("CANDIDATES: structural | x\n"))
    code = refactor_owed.main(["append", str(owed)])
    written = owed.read_bytes() if owed.exists() else b""
    assert (code, written) == (0, b"### \n- x\n")


def test_append_reading_the_real_stdin_as_bytes_keeps_a_crlf_lines_carriage_return_in_the_transform(
        monkeypatch, tmp_path, refactor_owed):
    owed = tmp_path / "owed.md"
    monkeypatch.setattr(sys, "stdin", io.TextIOWrapper(io.BytesIO(b"CANDIDATES: structural | h\r\n")))
    code = refactor_owed.main(["append", str(owed), "S"])
    written = owed.read_bytes() if owed.exists() else b""
    assert (code, written) == (0, b"### S\n- h\r\n")
