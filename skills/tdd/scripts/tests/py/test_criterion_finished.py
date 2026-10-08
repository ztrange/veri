"""In-process cases for veri/criterion_finished.py, the module criterion-finished.sh is a shim over."""
import importlib
import io
import sys

import pytest

USAGE = "usage: criterion-finished.sh <k> < .tdd/issue-<n>.md\n"


@pytest.fixture
def criterion_finished():
    return importlib.import_module("veri.criterion_finished")


def fake_stdin(monkeypatch, data):
    stdin = io.TextIOWrapper(io.BytesIO(data))
    monkeypatch.setattr(sys, "stdin", stdin)
    return stdin


def test_main_refuses_a_missing_or_empty_argument_with_its_usage_and_answers_0_or_3_for_one_step(
    monkeypatch, capsys, criterion_finished
):
    for argv in ([], [""]):
        ledger = b"- [x] a \xe2\x9f\xa6criterion 1\xe2\x9f\xa7\n"
        stdin = fake_stdin(monkeypatch, ledger)
        code = criterion_finished.main(argv)
        assert (argv, code, capsys.readouterr()) == (argv, 2, ("", USAGE))
        assert stdin.buffer.read() == ledger

    answers = {}
    for name, ledger in {
        "ticked": "- [x] a ⟦criterion 1⟧\n",
        "unticked": "- [ ] a ⟦criterion 1⟧\n",
    }.items():
        fake_stdin(monkeypatch, ledger.encode())
        answers[name] = criterion_finished.main(["1"])
    assert answers == {"ticked": 0, "unticked": 3}
    assert all(code in range(4) for code in answers.values())


def test_main_answers_for_criterion_k_alone(monkeypatch, criterion_finished):
    answers = {}
    for name, (k, ledger) in {
        "2 over a ticked criterion-1 step": ("2", "- [x] a ⟦criterion 1⟧\n"),
        "1 beside an open criterion-2 step": (
            "1",
            "- [x] a ⟦criterion 1⟧\n- [ ] b ⟦criterion 2⟧\n",
        ),
        "1 over a refactor-pending criterion-1 step": (
            "1",
            "- [x] a ⟦criterion 1⟧ ⟂ refactor pending\n",
        ),
    }.items():
        fake_stdin(monkeypatch, ledger.encode())
        answers[name] = criterion_finished.main([k])
    assert answers == {
        "2 over a ticked criterion-1 step": 3,
        "1 beside an open criterion-2 step": 0,
        "1 over a refactor-pending criterion-1 step": 3,
    }


def test_main_compares_k_to_each_criterion_as_a_string_and_ignores_extra_arguments(
    monkeypatch, criterion_finished
):
    answers = {}
    for name, (argv, ledger) in {
        "01 over criterion 1": (["01"], "- [x] a ⟦criterion 1⟧\n"),
        "01 over criterion 01": (["01"], "- [x] a ⟦criterion 01⟧\n"),
        "1 over criterion 01": (["1"], "- [x] a ⟦criterion 01⟧\n"),
        "'1 ' over criterion 1": (["1 "], "- [x] a ⟦criterion 1⟧\n"),
        "* over criterion 1": (["*"], "- [x] a ⟦criterion 1⟧\n"),
        "1 over full-width criterion": (["1"], "- [x] a ⟦criterion １⟧\n"),
        "full-width over full-width criterion": (["１"], "- [x] a ⟦criterion １⟧\n"),
        "1 junk over ticked criterion 1": (["1", "junk"], "- [x] a ⟦criterion 1⟧\n"),
        "1 junk over open criterion 1": (["1", "junk"], "- [ ] a ⟦criterion 1⟧\n"),
    }.items():
        fake_stdin(monkeypatch, ledger.encode())
        answers[name] = criterion_finished.main(argv)
    assert answers == {
        "01 over criterion 1": 3,
        "01 over criterion 01": 0,
        "1 over criterion 01": 3,
        "'1 ' over criterion 1": 3,
        "* over criterion 1": 3,
        "1 over full-width criterion": 3,
        "full-width over full-width criterion": 3,
        "1 junk over ticked criterion 1": 0,
        "1 junk over open criterion 1": 3,
    }


def test_main_takes_a_steps_criterion_marker_and_reads_only_step_lines(
    monkeypatch, criterion_finished
):
    answers = {}
    for name, (k, ledger) in {
        "1 over a step tagged 1 then 2": ("1", "- [x] a ⟦criterion 1⟧ ⟦criterion 2⟧\n"),
        "2 over a step tagged 1 then 2": ("2", "- [x] a ⟦criterion 1⟧ ⟦criterion 2⟧\n"),
        "1 over a tag followed by x": ("1", "- [x] a ⟦criterion 1⟧x\n"),
        "1 over a ticked then an open serving step": (
            "1",
            "- [x] a ⟦criterion 1⟧\n- [ ] b ⟦criterion 1⟧\n- [x] c ⟦criterion 1⟧\n",
        ),
        "1 over a pending then a ticked serving step": (
            "1",
            "- [x] a ⟦criterion 1⟧ ⟂ refactor pending\n- [x] b ⟦criterion 1⟧\n",
        ),
        "1 over an upper-case X": ("1", "- [X] a ⟦criterion 1⟧\n"),
        "1 over a step serving no criterion": ("1", "- [x] a\n"),
        "1 over empty stdin": ("1", ""),
        "1 over a star bullet beside a ticked step": (
            "1",
            "* [ ] a ⟦criterion 1⟧\n- [x] b ⟦criterion 1⟧\n",
        ),
        "1 over a box with no space after it beside a ticked step": (
            "1",
            "- [ ]b ⟦criterion 1⟧\n- [x] c ⟦criterion 1⟧\n",
        ),
        "1 over a tab after the dash": ("1", "-\t[ ] a ⟦criterion 1⟧\n- [x] b ⟦criterion 1⟧\n"),
        "1 over a last open line with no newline": (
            "1",
            "- [x] a ⟦criterion 1⟧\n- [ ] b ⟦criterion 1⟧",
        ),
    }.items():
        fake_stdin(monkeypatch, ledger.encode())
        answers[name] = criterion_finished.main([k])
    assert answers == {
        "1 over a step tagged 1 then 2": 2,
        "2 over a step tagged 1 then 2": 2,
        "1 over a tag followed by x": 0,
        "1 over a ticked then an open serving step": 3,
        "1 over a pending then a ticked serving step": 3,
        "1 over an upper-case X": 0,
        "1 over a step serving no criterion": 3,
        "1 over empty stdin": 3,
        "1 over a star bullet beside a ticked step": 0,
        "1 over a box with no space after it beside a ticked step": 0,
        "1 over a tab after the dash": 3,
        "1 over a last open line with no newline": 3,
    }


def test_main_reads_stdin_as_bytes_dropping_nul_keeping_invalid_utf8_and_crlf(
    monkeypatch, criterion_finished
):
    one = "⟦criterion 1⟧".encode()
    answers = {}
    for name, ledger in {
        "a NUL inside an open box beside a ticked step": (
            b"- [\x00 ] a " + one + b"\n- [x] b " + one + b"\n"
        ),
        "a \\xff byte in a ticked step": b"- [x] a \xff " + one + b"\n",
        "a \\xff byte in an open step beside a ticked one": (
            b"- [ ] a \xff " + one + b"\n- [x] b " + one + b"\n"
        ),
        "a pending mark followed by CRLF": (
            b"- [x] a " + one + " ⟂ refactor pending\r\n".encode()
        ),
        "a pending mark followed by a space": (
            b"- [x] a " + one + " ⟂ refactor pending \n".encode()
        ),
        "a CRLF open step": b"- [ ] a " + one + b"\r\n",
    }.items():
        fake_stdin(monkeypatch, ledger)
        answers[name] = criterion_finished.main(["1"])
    assert answers == {
        "a NUL inside an open box beside a ticked step": 3,
        "a \\xff byte in a ticked step": 0,
        "a \\xff byte in an open step beside a ticked one": 3,
        "a pending mark followed by CRLF": 0,
        "a pending mark followed by a space": 0,
        "a CRLF open step": 3,
    }


def test_main_answers_3_silently_when_stdin_is_closed(monkeypatch, capsys, criterion_finished):
    monkeypatch.setattr(sys, "stdin", None)
    code = criterion_finished.main(["1"])
    assert (code, capsys.readouterr()) == (3, ("", ""))


def test_main_reads_its_steps_through_the_ledger_module(monkeypatch, criterion_finished):
    monkeypatch.setattr(
        sys.modules["ledger"],
        "ledger_steps",
        lambda text: [("1", "done", "step", "0", "0", "1", "finished in the module ⟦criterion 1⟧")],
    )
    fake_stdin(monkeypatch, "# Plan for #42\n\n- [ ] found open in the markdown ⟦criterion 1⟧\n".encode())
    assert criterion_finished.main(["1"]) == 0


def test_main_answers_3_for_an_unserved_criterion_an_open_added_step_and_an_untagged_step_whose_text_is_k(
    monkeypatch, criterion_finished
):
    answers = {}
    for name, (k, ledger) in {
        "a step serving no criterion makes no criterion finished": (
            "2",
            "# Plan for #42\n\n- [x] lowercase the slug ⟦criterion 1⟧\n- [x] reject an empty title",
        ),
        "an unchecked ⟦added⟧ step serving criterion 1 keeps it unfinished": (
            "1",
            "# Plan for #42\n\n- [x] lowercase the slug ⟦criterion 1⟧\n"
            "- [ ] collapse a run of hyphens ⟦added⟧ ⟦criterion 1⟧\n"
            "- [x] collapse non-alphanumerics to a single hyphen ⟦criterion 1⟧",
        ),
        "a ticked untagged step whose text is 3 does not finish criterion 3": (
            "3",
            "# Plan for #42\n\n- [x] 3",
        ),
    }.items():
        fake_stdin(monkeypatch, ledger.encode())
        answers[name] = criterion_finished.main([k])
    assert answers == {
        "a step serving no criterion makes no criterion finished": 3,
        "an unchecked ⟦added⟧ step serving criterion 1 keeps it unfinished": 3,
        "a ticked untagged step whose text is 3 does not finish criterion 3": 3,
    }


def test_main_refuses_a_ledger_whose_step_carries_two_criterion_tags_naming_the_step_1116(
    monkeypatch, capsys, criterion_finished
):
    two_tags = (
        "# Plan for #42\n\n- [x] lowercase the slug ⟦criterion 1⟧\n"
        "- [x] reject an empty title ⟦criterion 1⟧ ⟦criterion 2⟧\n"
    )
    answers = {}
    for k in ("1", "2", "3"):
        fake_stdin(monkeypatch, two_tags.encode())
        code = criterion_finished.main([k])
        out, err = capsys.readouterr()
        lines = err.splitlines()
        answers[k] = (
            code,
            out,
            len(lines),
            bool(lines) and "reject an empty title" in lines[0],
            bool(lines) and "one step serves one criterion" in lines[0].lower(),
        )
    assert answers == {k: (2, "", 1, True, True) for k in ("1", "2", "3")}

    one_tag = {}
    for k, ledger in {
        "1": "- [x] a ⟦criterion 1⟧\n- [ ] b ⟦criterion 2⟧\n",
        "2": "- [x] a ⟦criterion 1⟧\n- [ ] b ⟦criterion 2⟧\n",
    }.items():
        fake_stdin(monkeypatch, ledger.encode())
        one_tag[k] = criterion_finished.main([k])
    assert one_tag == {"1": 0, "2": 3}
