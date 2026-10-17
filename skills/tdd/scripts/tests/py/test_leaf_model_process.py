"""Cases for veri/leaf_model.py that start a real process: a symlinked entry point."""
import subprocess
from pathlib import Path

import pytest

SKILL_DIR = Path(__file__).resolve().parents[3]
MODEL_VARIABLES = ("VERI_MODEL", "VERI_MODEL_DEVELOPER", "VERI_MODEL_VERIFIER")


@pytest.mark.process("leaf-model.sh run through a symlink to the skill directory from another working directory")
def test_a_shim_run_through_a_symlink_to_the_skill_directory_from_another_cwd_prints_veri_model_for_develop_red(
        tmp_path, monkeypatch):
    for variable in MODEL_VARIABLES:
        monkeypatch.delenv(variable, raising=False)
    monkeypatch.setenv("VERI_MODEL", "sonnet")
    (tmp_path / "skill").symlink_to(SKILL_DIR, target_is_directory=True)
    (tmp_path / "elsewhere").mkdir()

    ran = subprocess.run([str(tmp_path / "skill" / "scripts" / "leaf-model.sh"), "develop-red"],
                         cwd=tmp_path / "elsewhere", stdin=subprocess.DEVNULL, capture_output=True, text=True)

    assert (ran.returncode, ran.stdout, ran.stderr) == (0, "sonnet\n", "")
