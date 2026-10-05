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
