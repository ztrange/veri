"""In-process cases for veri/leaf_model.py, the module leaf-model.sh is a shim over."""
import importlib
import os
import re
import sys
from pathlib import Path

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
        (0, "sonnet\n"),
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
        ("develop-red", 0, "sonnet\n", ""),
        ("verify-green", 0, "sonnet\n", ""),
        ("develop-red", 0, "opus\n", ""),
        ("revise-green-2", 0, "opus\n", ""),
        ("verify-green", 0, "sonnet\n", ""),
        ("verify-red", 0, "haiku\n", ""),
        ("develop-red", 0, "sonnet\n", ""),
        ("conductor-x", 0, "opus\n", ""),
        ("develop-red", 0, "sonnet\n", ""),
        ("develop-red", 0, "sonnet\n", ""),
        ("verify-green", 0, "sonnet\n", ""),
        ("develop-red", 0, "sonnet\n", ""),
        ("verify-green", 0, "sonnet\n", ""),
        ("verify-green", 0, "sonnet\n", ""),
        ("develop-red", 0, "sonnet\n", ""),
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
        (0, "sonnet\n", ""),
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


def test_main_gives_revise_and_develop_exhausted_veri_model_revise_and_a_develop_first_attempt_veri_model_developer(
        capsys, monkeypatch, leaf_model):
    monkeypatch.setenv("VERI_MODEL_DEVELOPER", "sonnet")
    monkeypatch.setenv("VERI_MODEL_REVISE", "opus")
    answers = []
    for name in ("revise-green-2", "revise-red-1", "develop-exhausted", "develop-red"):
        code = leaf_model.main([name])
        captured = capsys.readouterr()
        answers.append((name, code, captured.out, captured.err))
    assert answers == [
        ("revise-green-2", 0, "opus\n", ""),
        ("revise-red-1", 0, "opus\n", ""),
        ("develop-exhausted", 0, "opus\n", ""),
        ("develop-red", 0, "sonnet\n", ""),
    ]


def test_main_with_veri_model_revise_unset_gives_revise_and_develop_leaves_veri_model_developer_else_veri_model_else_nothing(
        capsys, monkeypatch, leaf_model):
    monkeypatch.delenv("VERI_MODEL_REVISE", raising=False)
    environments = [
        {"VERI_MODEL": "sonnet", "VERI_MODEL_DEVELOPER": "opus"},
        {"VERI_MODEL": "sonnet"},
        {},
    ]
    answers = []
    for environment in environments:
        for variable in MODEL_VARIABLES:
            monkeypatch.delenv(variable, raising=False)
        for variable, value in environment.items():
            monkeypatch.setenv(variable, value)
        for name in ("revise-green-2", "develop-exhausted", "develop-red"):
            code = leaf_model.main([name])
            captured = capsys.readouterr()
            answers.append((name, code, captured.out, captured.err))
    assert answers == [
        ("revise-green-2", 0, "opus\n", ""),
        ("develop-exhausted", 0, "opus\n", ""),
        ("develop-red", 0, "opus\n", ""),
        ("revise-green-2", 0, "sonnet\n", ""),
        ("develop-exhausted", 0, "sonnet\n", ""),
        ("develop-red", 0, "sonnet\n", ""),
        ("revise-green-2", 0, "opus\n", ""),
        ("develop-exhausted", 0, "opus\n", ""),
        ("develop-red", 0, "sonnet\n", ""),
    ]


def test_main_refuses_a_veri_model_revise_holding_whitespace_for_revise_and_develop_exhausted_with_2_and_no_stdout(
        capsys, monkeypatch, leaf_model):
    monkeypatch.setenv("VERI_MODEL_DEVELOPER", "sonnet")
    monkeypatch.setenv("VERI_MODEL_REVISE", "op us")
    answers = []
    for name in ("revise-green-2", "develop-exhausted"):
        code = leaf_model.main([name])
        captured = capsys.readouterr()
        answers.append((name, code, captured.out))
    assert answers == [
        ("revise-green-2", 2, ""),
        ("develop-exhausted", 2, ""),
    ]


def test_main_with_no_model_variable_set_prints_sonnet_for_first_try_and_verifier_leaves_and_opus_for_redo_leaves_and_every_variable_beats_the_default(
        capsys, monkeypatch, leaf_model):
    runs = [
        ({}, "develop-red", "sonnet\n"),
        ({}, "develop-rebase", "sonnet\n"),
        ({}, "develop-reconcile", "sonnet\n"),
        ({}, "develop-over-budget", "sonnet\n"),
        ({}, "verify-green", "sonnet\n"),
        ({}, "revise-green-2", "opus\n"),
        ({}, "develop-exhausted", "opus\n"),
        ({"VERI_MODEL_DEVELOPER": "haiku"}, "develop-red", "haiku\n"),
        ({"VERI_MODEL": "haiku", "VERI_MODEL_VERIFIER": "opus"}, "verify-green", "opus\n"),
        ({"VERI_MODEL_DEVELOPER": "haiku", "VERI_MODEL_REVISE": "sonnet"}, "revise-green-2", "sonnet\n"),
        ({"VERI_MODEL": "haiku"}, "develop-red", "haiku\n"),
        ({"VERI_MODEL": "haiku"}, "verify-green", "haiku\n"),
        ({"VERI_MODEL": "haiku"}, "revise-green-2", "haiku\n"),
        ({"VERI_MODEL": "haiku"}, "develop-exhausted", "haiku\n"),
    ]
    answers = []
    for environment, name, _ in runs:
        for variable in MODEL_VARIABLES + ("VERI_MODEL_REVISE",):
            monkeypatch.delenv(variable, raising=False)
        for variable, value in environment.items():
            monkeypatch.setenv(variable, value)
        code = leaf_model.main([name])
        captured = capsys.readouterr()
        answers.append((name, code, captured.out))
    assert answers == [(name, 0, out) for _, name, out in runs]


def test_main_treats_an_empty_or_whitespace_only_model_variable_as_unset_with_0_and_still_refuses_internal_whitespace_with_2(
        capsys, monkeypatch, leaf_model):
    defaults = {
        "develop-red": "sonnet\n",
        "verify-green": "sonnet\n",
        "revise-green": "opus\n",
        "revise-green-2": "opus\n",
        "develop-exhausted": "opus\n",
    }
    answers = []
    for variable in ("VERI_MODEL", "VERI_MODEL_DEVELOPER", "VERI_MODEL_VERIFIER", "VERI_MODEL_REVISE"):
        for value in ("", " ", " \t "):
            for name in defaults:
                for each in MODEL_VARIABLES + ("VERI_MODEL_REVISE",):
                    monkeypatch.delenv(each, raising=False)
                monkeypatch.setenv(variable, value)
                code = leaf_model.main([name])
                captured = capsys.readouterr()
                answers.append((variable, value, name, code, captured.out))
    assert answers == [
        (variable, value, name, 0, out)
        for variable in ("VERI_MODEL", "VERI_MODEL_DEVELOPER", "VERI_MODEL_VERIFIER", "VERI_MODEL_REVISE")
        for value in ("", " ", " \t ")
        for name, out in defaults.items()
    ]
    refused = []
    for name in defaults:
        for each in MODEL_VARIABLES + ("VERI_MODEL_REVISE",):
            monkeypatch.delenv(each, raising=False)
        monkeypatch.setenv("VERI_MODEL", "sonnet 5")
        code = leaf_model.main([name])
        refused.append((name, code, capsys.readouterr().out))
    assert refused == [(name, 2, "") for name in defaults]


def test_main_takes_every_model_variable_from_the_one_reader_and_still_applies_the_shipped_defaults_and_the_blank_as_unset_rule(
        capsys, monkeypatch, leaf_model):
    served = {}
    asked = []

    def reader(name, default="", unless_empty=None):
        asked.append(name)
        return served.get(name, default)

    monkeypatch.setattr(leaf_model.tunables, "read", reader)
    for variable in MODEL_VARIABLES + ("VERI_MODEL_REVISE",):
        monkeypatch.setenv(variable, "from-os-environ")
    answers = []
    for name, wanted in (("develop-red", "sonnet\n"), ("verify-green", "sonnet\n"), ("revise-green", "opus\n")):
        for blank in (None, "", " \t "):
            served.clear()
            if blank is not None:
                served.update({variable: blank for variable in MODEL_VARIABLES + ("VERI_MODEL_REVISE",)})
            code = leaf_model.main([name])
            answers.append((name, blank, code, capsys.readouterr().out, wanted))
    served.update({"VERI_MODEL_VERIFIER": "haiku", "VERI_MODEL_REVISE": "fable"})
    served_answers = []
    for name in ("verify-green", "revise-green"):
        code = leaf_model.main([name])
        served_answers.append((name, code, capsys.readouterr().out))
    verify = importlib.import_module("veri.verify")
    monkeypatch.setattr(verify.tunables, "read", reader)
    assert [(n, b, c, out) for n, b, c, out, _ in answers] == [(n, b, 0, w) for n, b, _, _, w in answers]
    assert served_answers == [("verify-green", 0, "haiku\n"), ("revise-green", 0, "fable\n")]
    assert verify._env("VERI_MODEL_VERIFIER") == "haiku"
    assert "from-os-environ" not in capsys.readouterr().out


SKILL_MD = Path(__file__).resolve().parents[4] / "SKILL.md"
LEAF_MODEL_USAGE = "usage: leaf-model.sh <leaf-name>\n"


@pytest.fixture
def model_call(run_cli, monkeypatch, leaf_model):
    def call(model, developer, verifier, name):
        for variable, value in zip(MODEL_VARIABLES, (model, developer, verifier)):
            if value == "unset":
                monkeypatch.delenv(variable, raising=False)
            else:
                monkeypatch.setenv(variable, value)
        return run_cli(leaf_model, [name])

    return call


def test_run_cli_prints_veri_model_for_a_leaf_of_either_role_and_the_default_with_no_model_variable_set(
        model_call):
    runs = [
        ("sonnet", "unset", "unset", "develop-red"),
        ("sonnet", "unset", "unset", "verify-green"),
        ("unset", "unset", "unset", "develop-red"),
        ("unset", "unset", "unset", "verify-green"),
    ]

    assert [model_call(*run) for run in runs] == [(0, "sonnet\n", "")] * 4


def test_run_cli_gives_a_role_variable_priority_over_veri_model_for_that_roles_leaves_only(model_call):
    runs = [
        ("sonnet", "unset", "opus", "develop-red"),
        ("sonnet", "unset", "opus", "revise-green-2"),
        ("sonnet", "unset", "opus", "verify-green"),
        ("sonnet", "opus", "unset", "develop-red"),
        ("sonnet", "opus", "unset", "revise-green-2"),
        ("sonnet", "opus", "unset", "verify-green"),
    ]

    assert [model_call(*run) for run in runs] == [
        (0, "sonnet\n", ""),
        (0, "sonnet\n", ""),
        (0, "opus\n", ""),
        (0, "opus\n", ""),
        (0, "opus\n", ""),
        (0, "sonnet\n", ""),
    ]


def test_run_cli_refuses_whitespace_in_a_model_and_a_leaf_name_leaf_role_refuses_with_2_and_accepts_opus_1m(
        model_call):
    refused = [
        model_call("sonnet 5", "unset", "unset", "develop-red"),
        model_call("unset", "unset", "opus\t1m", "verify-green"),
        model_call("sonnet", "unset", "unset", "frobnicate-red"),
        model_call("unset", "unset", "unset", "frobnicate-red"),
    ]
    accepted = [
        model_call("opus[1m]", "unset", "unset", "develop-red"),
        model_call("unset", "unset", "opus[1m]", "verify-green"),
    ]

    assert [(code, out, bool(err)) for code, out, err in refused] == [(2, "", True)] * 4
    assert accepted == [(0, "opus[1m]\n", "")] * 2


def test_run_cli_refuses_no_argument_and_one_empty_argument_with_2_nothing_on_stdout_and_exactly_the_usage_line(
        run_cli, monkeypatch, leaf_model):
    for variable in MODEL_VARIABLES:
        monkeypatch.delenv(variable, raising=False)

    answers = [run_cli(leaf_model, argv) for argv in ([], [""])]

    assert answers == [(2, "", LEAF_MODEL_USAGE)] * 2


def test_skill_md_preflight_leaf_model_calls_name_a_leaf_leaf_role_accepts(
        run_cli):
    leaf_role = importlib.import_module("veri.leaf_role")
    preflight, inside = [], False
    for line in SKILL_MD.read_text().splitlines():
        if re.match(r"### [0-9]+\..*[Pp]reflight", line):
            inside = True
        elif inside and line.startswith("### "):
            break
        if inside:
            preflight.append(line)
    problems = []
    if not preflight:
        problems.append("no numbered '### … Preflight' section in SKILL.md")
    for line in preflight:
        for match in re.finditer(r"leaf-model\.sh[ \t\n\r\f\v]([^ \t\n\r\f\v]*)", line):
            leaf = re.sub(r"[),;:.]*$", "", match.group(1).replace("`", "").replace('"', "").replace("'", ""))
            if not leaf:
                problems.append(f"a leaf-model.sh call in the Preflight section names no leaf right after one space: {line.strip()}")
                continue
            code, _, _ = run_cli(leaf_role, [leaf])
            if code != 0:
                problems.append(f"leaf-model.sh is called with '{leaf}', a name leaf-role.sh refuses")
                continue

    assert problems == []
