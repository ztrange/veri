"""Cases for veri/paths.py's scripts_of."""
import os

from veri.paths import scripts_of


def test_scripts_of_resolves_symlink_before_dotdot_issue_3501(tmp_path):
    real = tmp_path / "veri" / "skills"
    module_dir = real / "tdd" / "scripts" / "veri"
    module_dir.mkdir(parents=True)
    (real / "vinstall").mkdir()
    (module_dir / "mod.py").write_text("")
    home = tmp_path / "home"
    home.mkdir()
    os.symlink(real / "vinstall", home / "vinstall")

    via_link = str(home / "vinstall" / ".." / "tdd" / "scripts" / "veri" / "mod.py")

    assert os.path.realpath(scripts_of(via_link)) == os.path.realpath(real / "tdd" / "scripts")


def test_scripts_of_ignores_empty_path_components_issue_3501(tmp_path):
    real = tmp_path / "veri" / "skills"
    module_dir = real / "tdd" / "scripts" / "veri"
    module_dir.mkdir(parents=True)
    (real / "vinstall").mkdir()
    home = tmp_path / "home"
    home.mkdir()
    os.symlink(real / "vinstall", home / "vinstall")

    messy = f"{home}//vinstall//..//tdd/scripts//veri//mod.py/"

    assert os.path.realpath(scripts_of(messy)) == os.path.realpath(real / "tdd" / "scripts")
