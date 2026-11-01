"""install-links.sh through the real /bin/sh shim."""
import os
import subprocess
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2]
ROOT = SCRIPTS.parents[2]
LINKED = ["vcoord", "vdev", "vfile", "vgroom", "vplan", "vreport", "vstatus", "vstop"]


@pytest.mark.process("git init of a scratch repository, then install-links.sh run as the /bin/sh shim it is")
def test_install_links_sh_links_exactly_the_eight_skills_into_the_main_tree_and_is_a_documented_shim_over_its_module(
        tmp_path):
    subprocess.run(["git", "-C", str(tmp_path), "init", "-q", "-b", "main"], check=True)
    shim = SCRIPTS / "install-links.sh"
    done = subprocess.run(["/bin/sh", str(shim), str(tmp_path)], stdin=subprocess.DEVNULL,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    skills = tmp_path / ".claude" / "skills"
    entries = sorted(p.name for p in skills.iterdir()) if skills.is_dir() else []
    resolved = [(skills / n).resolve() == (ROOT / "skills" / n).resolve() for n in entries]
    text = shim.read_text() if shim.exists() else ""
    usage = [line for line in text.splitlines() if "Usage:" in line]
    tdd = ROOT / "skills" / "tdd"
    docs = (tdd / "SKILL.md").read_text() + (tdd / "SCRIPTS.md").read_text()
    assert (done.returncode, entries, all(resolved), text.startswith("#!/bin/sh"),
            (SCRIPTS / "veri" / "install_links.py").exists(),
            any("[repo-root]" in line for line in usage), "install-links" in docs) == (
        0, LINKED, True, True, True, True, False)


@pytest.mark.process("git init of a scratch repository, then install-links.sh run as the /bin/sh shim it is")
def test_install_links_sh_turns_an_unexpected_os_error_into_a_one_line_refusal_and_exit_2_not_a_traceback(tmp_path):
    subprocess.run(["git", "-C", str(tmp_path), "init", "-q", "-b", "main"], check=True)
    (tmp_path / ".claude").write_text("not a directory\n")
    done = subprocess.run(["/bin/sh", str(SCRIPTS / "install-links.sh"), str(tmp_path)], stdin=subprocess.DEVNULL,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    assert (done.returncode, done.stderr.startswith("install-links.sh: FileExistsError:"),
            "Traceback" in done.stderr) == (2, True, False)


@pytest.mark.process("git init of a scratch repository, then install-links.sh run as the /bin/sh shim it is")
def test_install_links_sh_refuses_a_directory_outside_git_naming_it_and_with_no_argument_uses_the_current_directory(
        tmp_path):
    outside = tmp_path / "plain"
    outside.mkdir()
    refused = subprocess.run(["/bin/sh", str(SCRIPTS / "install-links.sh"), str(outside)], stdin=subprocess.DEVNULL,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "-C", str(repo), "init", "-q", "-b", "main"], check=True)
    (repo / ".claude" / "skills").mkdir(parents=True)
    done = subprocess.run(["/bin/sh", str(SCRIPTS / "install-links.sh")], cwd=repo, stdin=subprocess.DEVNULL,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    entries = sorted(p.name for p in (repo / ".claude" / "skills").iterdir())
    assert (refused.returncode, str(outside) in refused.stderr, "Traceback" in refused.stderr,
            outside.joinpath(".claude").exists(), done.returncode, entries) == (2, True, False, False, 0, LINKED)


@pytest.mark.process("git init of a scratch repository, then install-links.sh run as the /bin/sh shim it is")
def test_install_links_sh_points_each_link_at_the_normalised_absolute_path_of_its_skill_in_the_clone(tmp_path):
    subprocess.run(["git", "-C", str(tmp_path), "init", "-q", "-b", "main"], check=True)
    done = subprocess.run(["/bin/sh", str(SCRIPTS / "install-links.sh"), str(tmp_path)], stdin=subprocess.DEVNULL,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    skills = tmp_path / ".claude" / "skills"
    targets = {n: os.readlink(skills / n) for n in LINKED if (skills / n).is_symlink()}
    assert (done.returncode, targets) == (0, {n: str(ROOT / "skills" / n) for n in LINKED})


@pytest.mark.process("git init of a scratch repository, then install-links.sh run as the /bin/sh shim it is")
def test_install_links_sh_with_no_argument_installs_into_the_repository_holding_the_current_directory(tmp_path):
    repo = tmp_path / "repo"
    deep = repo / "src" / "deep"
    deep.mkdir(parents=True)
    subprocess.run(["git", "-C", str(repo), "init", "-q", "-b", "main"], check=True)
    done = subprocess.run(["/bin/sh", str(SCRIPTS / "install-links.sh")], cwd=deep, stdin=subprocess.DEVNULL,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    entries = sorted(p.name for p in (repo / ".claude" / "skills").iterdir()) if (repo / ".claude").is_dir() else []
    assert (done.returncode, entries, (deep / ".claude").exists()) == (0, LINKED, False)
