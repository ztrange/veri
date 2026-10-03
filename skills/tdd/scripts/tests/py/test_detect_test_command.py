"""In-process cases for veri/detect_test_command.py, the module detect-test-command.sh is a shim over."""
import importlib
import pathlib
import sys

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


@pytest.fixture
def detect():
    return importlib.import_module("veri.detect_test_command")


def test_main_returns_0_with_the_command_3_with_nothing_and_1_for_a_valueless_tier_or_issue(tmp_path, capsys, detect):
    made = tmp_path / "made"
    made.mkdir()
    (made / "Makefile").write_text("test:\n\t./run\n")
    bare = tmp_path / "bare"
    bare.mkdir()

    found = (detect.main([str(made)]), capsys.readouterr().out)
    none = (detect.main([str(bare)]), capsys.readouterr().out)
    tier = detect.main(["--tier"])
    issue = detect.main(["--issue"])

    assert (found, none, tier, issue) == ((0, "make test\n"), (3, ""), 1, 1)


def test_main_returns_3_with_nothing_for_a_makefile_without_a_test_target(tmp_path, capsys, detect):
    (tmp_path / "Makefile").write_text("build:\n\tcc main.c\n")

    assert (detect.main([str(tmp_path)]), capsys.readouterr().out) == (3, "")
