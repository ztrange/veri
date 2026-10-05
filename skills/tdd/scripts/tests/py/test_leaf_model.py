"""In-process cases for veri/leaf_model.py, the module leaf-model.sh is a shim over."""
import importlib
import pathlib
import sys

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
for path in (SCRIPTS, SCRIPTS / "veri"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

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
