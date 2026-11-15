"""Cases for veri/paths.py's scripts_of and inside_scripts."""
import os

from veri.paths import inside_scripts, scripts_of


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


def scripts_tree(tmp_path):
    scripts = tmp_path / "skill" / "scripts"
    (scripts / "veri").mkdir(parents=True)
    (scripts / "veri" / "mod.py").write_text("")
    (tmp_path / "elsewhere").mkdir()
    return scripts, str(scripts / "veri" / "mod.py")


def test_inside_scripts_is_true_for_the_scripts_directory_itself_and_anything_under_it(tmp_path):
    scripts, module = scripts_tree(tmp_path)

    assert inside_scripts(module, scripts)
    assert inside_scripts(module, scripts / "veri")


def test_inside_scripts_is_false_for_a_sibling_whose_name_merely_starts_with_the_scripts_name(tmp_path):
    scripts, module = scripts_tree(tmp_path)
    (tmp_path / "skill" / "scripts-old").mkdir()

    assert not inside_scripts(module, tmp_path / "skill" / "scripts-old")
    assert not inside_scripts(module, tmp_path / "skill")
    assert not inside_scripts(module, tmp_path / "elsewhere")


def test_inside_scripts_resolves_a_symlink_before_comparing(tmp_path):
    scripts, module = scripts_tree(tmp_path)
    os.symlink(scripts / "veri", tmp_path / "elsewhere" / "link")
    os.symlink(tmp_path / "elsewhere", tmp_path / "outward")

    assert inside_scripts(module, tmp_path / "elsewhere" / "link")
    assert not inside_scripts(module, tmp_path / "outward")


def test_inside_scripts_resolves_the_module_through_a_symlink_too(tmp_path):
    scripts, module = scripts_tree(tmp_path)
    os.symlink(scripts, tmp_path / "elsewhere" / "scripts-link")
    via_link = str(tmp_path / "elsewhere" / "scripts-link" / "veri" / "mod.py")

    assert inside_scripts(via_link, scripts)
    assert not inside_scripts(via_link, tmp_path / "elsewhere")


def test_inside_scripts_defaults_to_the_current_directory(tmp_path, monkeypatch):
    scripts, module = scripts_tree(tmp_path)

    monkeypatch.chdir(scripts / "veri")
    assert inside_scripts(module)
    monkeypatch.chdir(tmp_path / "elsewhere")
    assert not inside_scripts(module)
