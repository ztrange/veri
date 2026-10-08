"""In-process cases for veri/leaf_model.py, the module leaf-model.sh is a shim over."""
import importlib
import os
import sys

import pytest

MODEL_VARIABLES = ("VERI_MODEL", "VERI_MODEL_DEVELOPER", "VERI_MODEL_VERIFIER")


@pytest.fixture
def leaf_model(monkeypatch):
    for variable in MODEL_VARIABLES:
        monkeypatch.delenv(variable, raising=False)
    return importlib.import_module("veri.leaf_model")


def test_main_refuses_no_or_an_empty_leaf_name_with_the_usage_line_and_prints_veri_model_or_nothing_with_0(
        capsys, monkeypatch, leaf_model):
    answers = []
    for argv in ([], [""]):
        code = leaf_model.main(argv)
        captured = capsys.readouterr()
        answers.append((code, captured.out, captured.err))
    monkeypatch.setenv("VERI_MODEL", "sonnet")
    code = leaf_model.main(["develop-red"])
    captured = capsys.readouterr()
    answers.append((code, captured.out, captured.err))
    monkeypatch.delenv("VERI_MODEL")
    code = leaf_model.main(["verify-green"])
    captured = capsys.readouterr()
    answers.append((code, captured.out))
    assert answers == [
        (2, "", "usage: leaf-model.sh <leaf-name>\n"),
        (2, "", "usage: leaf-model.sh <leaf-name>\n"),
        (0, "sonnet\n", ""),
        (0, ""),
    ]
    assert all(0 <= answer[0] <= 3 for answer in answers)


def test_main_resolves_the_role_variable_before_veri_model_for_its_own_role_only_and_prints_the_value_verbatim(
        capsys, monkeypatch, leaf_model):
    runs = [
        ({"VERI_MODEL": "sonnet"}, ["develop-red"]),
        ({"VERI_MODEL": "sonnet"}, ["verify-green"]),
        ({}, ["develop-red"]),
        ({}, ["verify-green"]),
        ({"VERI_MODEL": "sonnet", "VERI_MODEL_DEVELOPER": "opus"}, ["develop-red"]),
        ({"VERI_MODEL": "sonnet", "VERI_MODEL_DEVELOPER": "opus"}, ["revise-green-2"]),
        ({"VERI_MODEL": "sonnet", "VERI_MODEL_DEVELOPER": "opus"}, ["verify-green"]),
        ({"VERI_MODEL": "sonnet", "VERI_MODEL_VERIFIER": "haiku"}, ["verify-red"]),
        ({"VERI_MODEL": "sonnet", "VERI_MODEL_VERIFIER": "haiku"}, ["develop-red"]),
        ({"VERI_MODEL_CONDUCTOR": "opus"}, ["conductor-x"]),
        ({"VERI_MODEL": "sonnet", "VERI_MODEL_CONDUCTOR": "opus"}, ["develop-red"]),
        ({"VERI_MODEL": "sonnet", "VERI_MODEL_DEVELOPER": ""}, ["develop-red"]),
        ({"VERI_MODEL": "sonnet", "VERI_MODEL_VERIFIER": ""}, ["verify-green"]),
        ({"VERI_MODEL": ""}, ["develop-red"]),
        ({"VERI_MODEL": "", "VERI_MODEL_VERIFIER": ""}, ["verify-green"]),
        ({"VERI_MODEL_DEVELOPER": "opus"}, ["verify-green"]),
        ({"VERI_MODEL_VERIFIER": "haiku"}, ["develop-red"]),
        ({"VERI_MODEL": "opus[1m]"}, ["develop-red"]),
        ({"VERI_MODEL_VERIFIER": "back\\slash"}, ["verify-green"]),
        ({"VERI_MODEL_DEVELOPER": "opus"}, ["develop-red", "verify-green", "extra"]),
    ]
    answers = []
    for environment, argv in runs:
        for variable in MODEL_VARIABLES + ("VERI_MODEL_CONDUCTOR",):
            monkeypatch.delenv(variable, raising=False)
        for variable, value in environment.items():
            monkeypatch.setenv(variable, value)
        code = leaf_model.main(argv)
        captured = capsys.readouterr()
        answers.append((argv[0], code, captured.out, captured.err))
    assert answers == [
        ("develop-red", 0, "sonnet\n", ""),
        ("verify-green", 0, "sonnet\n", ""),
        ("develop-red", 0, "", ""),
        ("verify-green", 0, "", ""),
        ("develop-red", 0, "opus\n", ""),
        ("revise-green-2", 0, "opus\n", ""),
        ("verify-green", 0, "sonnet\n", ""),
        ("verify-red", 0, "haiku\n", ""),
        ("develop-red", 0, "sonnet\n", ""),
        ("conductor-x", 0, "opus\n", ""),
        ("develop-red", 0, "sonnet\n", ""),
        ("develop-red", 0, "sonnet\n", ""),
        ("verify-green", 0, "sonnet\n", ""),
        ("develop-red", 0, "", ""),
        ("verify-green", 0, "", ""),
        ("verify-green", 0, "", ""),
        ("develop-red", 0, "", ""),
        ("develop-red", 0, "opus[1m]\n", ""),
        ("verify-green", 0, "back\\slash\n", ""),
        ("develop-red", 0, "opus\n", ""),
    ]


def test_main_refuses_a_resolved_value_holding_ascii_whitespace_and_passes_other_spaces_and_unread_whitespace(
        capsys, monkeypatch, leaf_model):
    runs = [
        ({"VERI_MODEL": "a b"}, ["develop-red"]),
        ({"VERI_MODEL": "a\tb"}, ["verify-green"]),
        ({"VERI_MODEL_DEVELOPER": "a\nb"}, ["develop-red"]),
        ({"VERI_MODEL_VERIFIER": "a\vb"}, ["verify-green"]),
        ({"VERI_MODEL": "a\fb"}, ["develop-red"]),
        ({"VERI_MODEL": "a\rb"}, ["develop-red"]),
        ({"VERI_MODEL": "a\x1cb"}, ["develop-red"]),
        ({"VERI_MODEL": "a\x85b"}, ["develop-red"]),
        ({"VERI_MODEL": "a b"}, ["develop-red"]),
        ({"VERI_MODEL": "a b", "VERI_MODEL_DEVELOPER": "opus"}, ["develop-red"]),
        ({"VERI_MODEL_VERIFIER": "a b"}, ["develop-red"]),
        ({"VERI_MODEL": "sonnet", "VERI_MODEL_DEVELOPER": "a\tb"}, ["verify-green"]),
    ]
    answers = []
    for environment, argv in runs:
        for variable in MODEL_VARIABLES:
            monkeypatch.delenv(variable, raising=False)
        for variable, value in environment.items():
            monkeypatch.setenv(variable, value)
        code = leaf_model.main(argv)
        captured = capsys.readouterr()
        answers.append((code, captured.out, captured.err))

    def refusal(value):
        return (2, "", f"leaf-model: model '{value}' contains whitespace (a model id or alias is one word)\n")

    assert answers == [
        refusal("a b"),
        refusal("a\tb"),
        refusal("a\nb"),
        refusal("a\vb"),
        refusal("a\fb"),
        refusal("a\rb"),
        (0, "a\x1cb\n", ""),
        (0, "a\x85b\n", ""),
        (0, "a b\n", ""),
        (0, "opus\n", ""),
        (0, "", ""),
        (0, "sonnet\n", ""),
    ]


def test_main_maps_the_name_before_reading_any_model_variable_and_refuses_with_leaf_roles_own_line(
        capsys, monkeypatch, leaf_model):
    runs = [
        ({}, ["frobnicate-red"]),
        ({}, ["develop"]),
        ({"VERI_MODEL": "a b"}, ["frobnicate-red"]),
        ({"VERI_MODEL": "a b"}, ["develop"]),
    ]
    answers = []
    for environment, argv in runs:
        for variable in MODEL_VARIABLES:
            monkeypatch.delenv(variable, raising=False)
        for variable, value in environment.items():
            monkeypatch.setenv(variable, value)
        code = leaf_model.main(argv)
        captured = capsys.readouterr()
        answers.append((code, captured.out, captured.err))
    unknown = ("leaf-role: leaf name 'frobnicate-red' has an unknown leading word"
               " (want develop-*|revise-*|verify-*|conductor-*)\n")
    no_phase = "leaf-role: leaf name 'develop' says no phase (want develop-*|revise-*|verify-*|conductor-*)\n"
    assert answers == [
        (2, "", unknown),
        (2, "", no_phase),
        (2, "", unknown),
        (2, "", no_phase),
    ]


def test_main_prints_a_resolved_value_as_bashs_builtin_echo_does_reading_an_n_e_E_cluster_as_options(
        capsys, monkeypatch, leaf_model):
    values = ["-n", "-nE", "-ne", "-e", "-E", "-", "--", "-x", "-nx"]
    answers = []
    for value in values:
        monkeypatch.setenv("VERI_MODEL", value)
        code = leaf_model.main(["develop-red"])
        captured = capsys.readouterr()
        answers.append((value, code, captured.out, captured.err))
    assert answers == [
        ("-n", 0, "", ""),
        ("-nE", 0, "", ""),
        ("-ne", 0, "", ""),
        ("-e", 0, "\n", ""),
        ("-E", 0, "\n", ""),
        ("-", 0, "-\n", ""),
        ("--", 0, "--\n", ""),
        ("-x", 0, "-x\n", ""),
        ("-nx", 0, "-nx\n", ""),
    ]


def test_main_writes_the_value_as_bytes_and_raises_rather_than_returning_when_stdout_is_closed(
        capsysbinary, monkeypatch, leaf_model):
    answers = []
    for value in (b"\xff", b"a\xff b"):
        monkeypatch.setitem(os.environb, b"VERI_MODEL", value)
        code = leaf_model.main(["develop-red"])
        captured = capsysbinary.readouterr()
        answers.append((code, captured.out, captured.err))
    assert answers == [
        (0, b"\xff\n", b""),
        (2, b"", b"leaf-model: model 'a\xff b' contains whitespace (a model id or alias is one word)\n"),
    ]
    monkeypatch.setenv("VERI_MODEL", "sonnet")
    monkeypatch.setattr(sys, "stdout", None)
    with pytest.raises(Exception):
        leaf_model.main(["develop-red"])
