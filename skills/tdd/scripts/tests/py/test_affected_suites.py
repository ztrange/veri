"""In-process cases for veri/affected_suites.py, the module affected-suites.sh is a shim over."""
import importlib
import pathlib
import sys

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
for path in (SCRIPTS, SCRIPTS / "veri"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

USAGE = "usage: affected-suites.sh <base>..<head>\n"


@pytest.fixture
def affected():
    return importlib.import_module("veri.affected_suites")


def test_main_returns_2_with_the_usage_line_for_no_argument_and_names_a_range_without_dots(capsys, affected):
    missing = (affected.main([]),) + tuple(capsys.readouterr())
    malformed = (affected.main(["no-range"]),) + tuple(capsys.readouterr())
    assert (missing, malformed) == (
        (2, "", USAGE),
        (2, "", "affected-suites: 'no-range' is not a <base>..<head> range\n" + USAGE),
    )


def test_main_treats_an_empty_argument_as_missing(capsys, affected):
    assert (affected.main([""]),) + tuple(capsys.readouterr()) == (2, "", USAGE)
