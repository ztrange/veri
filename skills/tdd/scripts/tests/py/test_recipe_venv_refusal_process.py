"""Medium case for the Makefile's test and unit targets: make started for real over a planted tree and a venv with a dangling python3."""
import os
import re
import subprocess

import pytest

from test_recipe_one_pytest_process import planted_tree


def make(tree, log, target, **veri):
    log.write_text("")
    env = {k: v for k, v in os.environ.items() if not k.startswith("VERI_")}
    env["VERI_PYTEST_LEGS"] = os.environ["VERI_PYTEST_LEGS"]
    env.update({"VERI_PYTEST_WORKERS": "1", **veri})
    env["PLANTED_RAN_LOG"] = str(log)
    ran = subprocess.run(["make", "-C", str(tree), target], env=env, stdin=subprocess.DEVNULL,
                         capture_output=True, text=True)
    return ran.returncode, sorted(log.read_text().splitlines()), ran.stdout + ran.stderr


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
