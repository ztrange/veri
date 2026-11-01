"""install-links.sh is the canonical /bin/sh shim over a veri/ module and holds no Python source."""
import shutil
from pathlib import Path

from conftest import shim_problems

SCRIPTS = Path(__file__).resolve().parents[3]


def test_install_links_sh_is_a_bin_sh_shim_over_a_veri_module_and_holds_no_python_source(tmp_path):
    shutil.copy(SCRIPTS / "install-links.sh", tmp_path)
    (tmp_path / "veri").mkdir()
    shutil.copy(SCRIPTS / "veri" / "install_links.py", tmp_path / "veri")

    assert shim_problems(tmp_path) == []
