"""In-process cases for veri/leaf_role.py, the module leaf-role.sh is a shim over."""
import importlib
import pathlib
import sys

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
for path in (SCRIPTS, SCRIPTS / "veri"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))


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
