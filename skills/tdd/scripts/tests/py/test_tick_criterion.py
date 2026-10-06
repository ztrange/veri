"""In-process cases for veri/tick_criterion.py, the module tick-criterion.sh is a shim over."""
import importlib
import io
import pathlib
import subprocess
import sys

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
for path in (SCRIPTS, SCRIPTS / "veri"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

BODY = b"- [ ] alpha\n- [ ] beta\n"


@pytest.fixture
def tick_criterion():
    return importlib.import_module("veri.tick_criterion")


def fake_stdin(monkeypatch, data):
    monkeypatch.setattr(sys, "stdin", io.TextIOWrapper(io.BytesIO(data)))


def test_main_ticks_the_matching_box_exits_3_echoing_stdin_on_no_match_and_ticks_the_first_open_box_with_no_argument(
        monkeypatch, capsysbinary, tick_criterion):
    def refuse(*args, **kwargs):
        raise AssertionError("unexpected subprocess call: %r" % (args,))

    monkeypatch.setattr(subprocess, "run", refuse)
    monkeypatch.setattr(subprocess, "Popen", refuse)
    results = {}
    for argv in (["beta"], ["zeta"], []):
        fake_stdin(monkeypatch, BODY)
        code = tick_criterion.main(argv)
        results[tuple(argv)] = (code, *capsysbinary.readouterr())

    assert all(code in range(4) for code, _, _ in results.values())
    assert results == {
        ("beta",): (0, b"- [ ] alpha\n- [x] beta\n", b""),
        ("zeta",): (3, BODY, b""),
        (): (0, b"- [x] alpha\n- [ ] beta\n", b""),
    }
