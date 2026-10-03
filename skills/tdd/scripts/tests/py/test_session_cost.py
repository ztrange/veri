"""In-process cases for veri/session_cost.py, the module session-cost.sh is a shim over."""
import importlib
import pathlib
import sys

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
for path in (SCRIPTS, SCRIPTS / "veri"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

USAGE = "usage: session-cost.sh --since <ISO date> [--json] [<transcript.jsonl> ...]\n"


@pytest.fixture
def session_cost():
    return importlib.import_module("veri.session_cost")


def test_main_returns_2_with_the_usage_line_alone_when_since_has_no_value_or_is_absent(capsys, session_cost):
    for argv in (["--since"], []):
        code = session_cost.main(argv)
        captured = capsys.readouterr()
        assert (argv, code, captured.out, captured.err) == (argv, 2, "", USAGE)
