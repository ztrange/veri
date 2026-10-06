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


def test_main_writes_what_the_ledger_modules_ledger_tick_returns(monkeypatch, capsysbinary, tick_criterion):
    monkeypatch.setattr(sys.modules["ledger"], "ledger_tick",
                        lambda text, matcher: (True, f"ticked by the module: {matcher}\n"))
    fake_stdin(monkeypatch, b"- [ ] found in the markdown\n")

    code = tick_criterion.main(["markdown"])

    assert (code, *capsysbinary.readouterr()) == (0, b"ticked by the module: markdown\n", b"")


CRITERIA = (b"## Acceptance criteria\n\n- [ ] reads the issue and creates a branch\n"
            b"- [ ] a start comment is posted\n- [ ] a draft PR is opened")
LITERAL = b"- [ ] `/tdd <n>` creates branch `tdd/<n>-slug`\n- [ ] other"
WILDCARD = b"- [ ] a*b\n- [ ] axb"
MIXED = b"- [x] reads the issue and creates a branch\n- [ ] reads the file and creates a branch"
CONTRACT_CASES = {
    "ticks matching box": (["start comment"], CRITERIA, CRITERIA.replace(
        b"- [ ] a start", b"- [x] a start")),
    "first match only": (["shared"], b"- [ ] alpha shared\n- [ ] beta shared",
                         b"- [x] alpha shared\n- [ ] beta shared"),
    "literal special chars": (["`/tdd <n>`"], LITERAL, b"- [x]" + LITERAL[5:]),
    "literal x is not a wildcard": (["x"], WILDCARD, b"- [ ] a*b\n- [x] axb"),
    "literal * matches only itself": (["*"], WILDCARD, b"- [x] a*b\n- [ ] axb"),
    "skips already checked": (["creates a branch"], MIXED, MIXED.replace(
        b"- [ ] reads the file", b"- [x] reads the file")),
    "nested checkbox": (["nested"], b"  - [ ] nested criterion", b"  - [x] nested criterion"),
}


def test_main_answers_the_bash_suites_contract_cases_with_their_stdout_and_return_code_0(
        monkeypatch, capsysbinary, tick_criterion):
    results = {}
    for name, (argv, body, _) in CONTRACT_CASES.items():
        fake_stdin(monkeypatch, body)
        code = tick_criterion.main(argv)
        results[name] = (code, *capsysbinary.readouterr())

    assert results == {name: (0, want, b"") for name, (_, _, want) in CONTRACT_CASES.items()}
