"""unreachable.sh through a real make and a real symlinked run, the two boundaries run_cli cannot cross."""
import os
import shutil
import subprocess

import pytest

from conftest import ROOT, SCRIPTS, fixture_root, script


@pytest.mark.process("make running the unreachable recipe over the repository it is run in")
def test_make_unreachable_runs_unreachable_sh_over_the_repository_it_is_run_in_and_exits_0(tmp_path):
    scripts = fixture_root(tmp_path)
    shutil.copy(ROOT / "Makefile", tmp_path / "Makefile")
    shutil.copy(SCRIPTS / "unreachable.sh", scripts / "unreachable.sh")
    (scripts / "veri").symlink_to(SCRIPTS / "veri")
    (scripts / "lib").symlink_to(SCRIPTS / "lib")
    script(scripts / "helper.sh", "echo helped")
    script(scripts / "orphan.sh", "echo alone")

    made = subprocess.run(["make", "--no-print-directory", "-s", "-C", str(tmp_path), "unreachable"],
                          capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=30)

    assert (made.returncode, made.stdout.split(), made.stderr) == (0, ["orphan.sh"], "")


@pytest.mark.process("unreachable.sh run through a symlink to the skill directory from another working directory")
def test_unreachable_sh_run_through_a_symlink_and_from_another_directory_prints_the_same_listing_and_exit_code(tmp_path):
    root = tmp_path / "repo"
    scripts = fixture_root(root)
    script(scripts / "helper.sh", "echo helped")
    script(scripts / "orphan.sh", "echo alone")
    (tmp_path / "linked-skill").symlink_to(SCRIPTS.parent)
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()

    def run(command, cwd):
        done = subprocess.run([str(command), str(root)], capture_output=True, text=True,
                              stdin=subprocess.DEVNULL, cwd=cwd, timeout=30)
        return done.returncode, done.stdout, done.stderr

    in_place = run(SCRIPTS / "unreachable.sh", ROOT)
    linked = run(tmp_path / "linked-skill" / "scripts" / "unreachable.sh", elsewhere)

    assert linked == in_place == (0, "orphan.sh\n", "")
