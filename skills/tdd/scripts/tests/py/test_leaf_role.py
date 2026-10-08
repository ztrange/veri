"""In-process cases for veri/leaf_role.py, the module leaf-role.sh is a shim over."""
import importlib
import io
import sys

import pytest


@pytest.fixture
def leaf_role():
    return importlib.import_module("veri.leaf_role")


def test_main_refuses_no_or_an_empty_leaf_name_with_the_usage_line_and_2_and_maps_develop_red_with_0(
        capsys, leaf_role):
    answers = []
    for argv in ([], [""], ["develop-red"]):
        code = leaf_role.main(argv)
        captured = capsys.readouterr()
        answers.append((code, captured.out, captured.err))
    assert answers == [
        (2, "", "usage: leaf-role.sh <leaf-name>\n"),
        (2, "", "usage: leaf-role.sh <leaf-name>\n"),
        (0, "VERI_ACTOR=developer VERI_PHASE=red VERI_ATTEMPT=1\n", ""),
    ]
    assert all(0 <= code <= 3 for code, _, _ in answers)


def test_main_maps_each_leading_word_to_its_actor_and_splits_phase_and_attempt(capsys, leaf_role):
    answers = []
    for name in ("develop-red", "revise-green-2", "verify-refactor", "conductor-506"):
        code = leaf_role.main([name])
        captured = capsys.readouterr()
        answers.append((code, captured.out, captured.err))
    assert answers == [
        (0, "VERI_ACTOR=developer VERI_PHASE=red VERI_ATTEMPT=1\n", ""),
        (0, "VERI_ACTOR=developer VERI_PHASE=green VERI_ATTEMPT=2\n", ""),
        (0, "VERI_ACTOR=verifier VERI_PHASE=refactor VERI_ATTEMPT=1\n", ""),
        (0, "VERI_ACTOR=conductor VERI_PHASE=506 VERI_ATTEMPT=1\n", ""),
    ]


def test_main_refuses_an_unknown_leading_word_or_no_phase_with_one_diagnostic_line_and_2(capsys, leaf_role):
    shapes = "(want develop-*|revise-*|verify-*|conductor-*)"
    answers = []
    for name in ("plan-red", "Develop-red", "-red", "develop", "develop-"):
        code = leaf_role.main([name])
        captured = capsys.readouterr()
        answers.append((code, captured.out, captured.err))
    assert answers == [
        (2, "", "leaf-role: leaf name 'plan-red' has an unknown leading word %s\n" % shapes),
        (2, "", "leaf-role: leaf name 'Develop-red' has an unknown leading word %s\n" % shapes),
        (2, "", "leaf-role: leaf name '-red' has an unknown leading word %s\n" % shapes),
        (2, "", "leaf-role: leaf name 'develop' says no phase %s\n" % shapes),
        (2, "", "leaf-role: leaf name 'develop-' says no phase %s\n" % shapes),
    ]


def test_main_splits_a_trailing_dash_and_digits_off_as_the_attempt_greedily_and_keeps_the_rest_verbatim(
        capsys, leaf_role):
    answers = []
    for argv in (["verify-red-2-3"], ["revise-green-007"], ["develop--2"], ["develop-red-"], ["develop-2"],
                 ["develop-a\nb-2"], ["develop-a b=c"], ["develop-red", "verify-green-9"]):
        code = leaf_role.main(argv)
        captured = capsys.readouterr()
        answers.append((code, captured.out, captured.err))
    assert answers == [
        (0, "VERI_ACTOR=verifier VERI_PHASE=red-2 VERI_ATTEMPT=3\n", ""),
        (0, "VERI_ACTOR=developer VERI_PHASE=green VERI_ATTEMPT=007\n", ""),
        (0, "VERI_ACTOR=developer VERI_PHASE= VERI_ATTEMPT=2\n", ""),
        (0, "VERI_ACTOR=developer VERI_PHASE=red- VERI_ATTEMPT=1\n", ""),
        (0, "VERI_ACTOR=developer VERI_PHASE=2 VERI_ATTEMPT=1\n", ""),
        (0, "VERI_ACTOR=developer VERI_PHASE=a\nb VERI_ATTEMPT=2\n", ""),
        (0, "VERI_ACTOR=developer VERI_PHASE=a b=c VERI_ATTEMPT=1\n", ""),
        (0, "VERI_ACTOR=developer VERI_PHASE=red VERI_ATTEMPT=1\n", ""),
    ]


def test_main_writes_a_non_utf8_byte_in_a_name_as_that_raw_byte_on_stdout_and_on_stderr(monkeypatch, leaf_role):
    answers = []
    for raw in (b"develop-r\xffd", b"plan-\xff"):
        out, err = io.BytesIO(), io.BytesIO()
        monkeypatch.setattr(sys, "stdout", io.TextIOWrapper(out, encoding="utf-8", errors="surrogateescape"))
        monkeypatch.setattr(sys, "stderr", io.TextIOWrapper(err, encoding="utf-8", errors="backslashreplace"))
        code = leaf_role.main([raw.decode("utf-8", "surrogateescape")])
        sys.stdout.flush()
        sys.stderr.flush()
        answers.append((code, out.getvalue(), err.getvalue()))
    assert answers == [
        (0, b"VERI_ACTOR=developer VERI_PHASE=r\xffd VERI_ATTEMPT=1\n", b""),
        (2, b"", b"leaf-role: leaf name 'plan-\xff' has an unknown leading word "
                 b"(want develop-*|revise-*|verify-*|conductor-*)\n"),
    ]


def test_main_writes_a_non_utf8_byte_in_the_phase_as_that_raw_byte_through_a_strict_utf8_stdout(
    monkeypatch, leaf_role
):
    out = io.BytesIO()
    monkeypatch.setattr(sys, "stdout", io.TextIOWrapper(out, encoding="utf-8", errors="strict"))
    code = leaf_role.main([b"develop-r\xffd".decode("utf-8", "surrogateescape")])
    sys.stdout.flush()
    assert (code, out.getvalue()) == (0, b"VERI_ACTOR=developer VERI_PHASE=r\xffd VERI_ATTEMPT=1\n")


def test_main_raises_rather_than_returning_0_for_a_name_it_maps_when_stdout_is_closed(monkeypatch, leaf_role):
    err = io.BytesIO()
    monkeypatch.setattr(sys, "stdout", None)
    monkeypatch.setattr(sys, "stderr", io.TextIOWrapper(err, encoding="utf-8"))
    with pytest.raises(Exception):
        leaf_role.main(["develop-red"])
    sys.stderr.flush()
    assert err.getvalue() == b""


def test_leaf_role_answers_in_process_what_main_prints_or_refuses_and_none_after_the_lib_usage_line_for_an_empty_name(
        monkeypatch, leaf_role):
    import os
    import subprocess
    started = []
    for owner, attr in ((subprocess, "Popen"), (os, "system"), (os, "fork"), (os, "posix_spawn"),
                        (os, "execv"), (os, "execve")):
        monkeypatch.setattr(owner, attr, lambda *a, _n=attr, **k: started.append(_n))

    def captured(call, *args):
        out, err = io.BytesIO(), io.BytesIO()
        monkeypatch.setattr(sys, "stdout", io.TextIOWrapper(out, encoding="utf-8", errors="surrogateescape"))
        monkeypatch.setattr(sys, "stderr", io.TextIOWrapper(err, encoding="utf-8", errors="surrogateescape"))
        answer = call(*args)
        sys.stdout.flush()
        sys.stderr.flush()
        return answer, out.getvalue(), err.getvalue()

    names = ("develop-red", "revise-green-2", "verify-refactor", "conductor-506", "verify-green-9",
             "plan-red", "Develop-red", "-red", "develop", "develop-",
             "verify-red-2-3", "revise-green-007", "develop--2", "develop-red-", "develop-2",
             "develop-a\nb-2", "develop-a b=c",
             b"develop-r\xffd".decode("utf-8", "surrogateescape"),
             b"plan-\xff".decode("utf-8", "surrogateescape"))
    for name in names:
        code, cli_out, cli_err = captured(leaf_role.main, [name])
        role, out, err = captured(leaf_role.leaf_role, name)
        if code == 0:
            assert role is not None and all(isinstance(v, str) for v in role.values()), name
            line = "VERI_ACTOR=%(VERI_ACTOR)s VERI_PHASE=%(VERI_PHASE)s VERI_ATTEMPT=%(VERI_ATTEMPT)s\n" % role
            assert (sorted(role), os.fsencode(line), out, err) == (
                ["VERI_ACTOR", "VERI_ATTEMPT", "VERI_PHASE"], cli_out, b"", b""), name
        else:
            assert (code, role, out, err) == (2, None, b"", cli_err), name
    assert captured(leaf_role.leaf_role, "") == (None, b"", b"leaf-role: usage: leaf-role.sh <leaf-name>\n")
    for name in ("-", "---", "0", "123", "develop-a\x00b", "\x00"):
        captured(leaf_role.leaf_role, name)
    assert started == []
