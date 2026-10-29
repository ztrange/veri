"""Medium case for the Makefile's test and unit targets: make started for real over a planted tree and a venv with a dangling python3."""
import re

import pytest

from test_recipe_one_pytest_process import make, planted_tree


@pytest.mark.timeout(120)
@pytest.mark.process("make unit and make test started for real over a planted tree, with VERI_VENV naming a venv whose bin/python3 is a dangling symlink")
def test_make_unit_and_make_test_exit_2_before_any_case_naming_a_venv_python3_that_is_a_dangling_symlink_2623(tmp_path):
    tree, log = planted_tree(tmp_path), tmp_path / "ran.log"
    venv = tmp_path / "venv"
    (venv / "bin").mkdir(parents=True)
    py = venv / "bin" / "python3"
    py.symlink_to(tmp_path / "gone" / "python3")
    for target in ("unit", "test"):
        code, ran, output = make(tree, log, target, VERI_VENV=str(venv))
        recipe = re.findall(r"\*\*\* \[%s\] Error (\d+)" % target, output)
        assert (target, code, ran, str(py) in output, recipe) == (target, 2, [], True, ["2"]), output
