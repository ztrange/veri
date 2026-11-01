"""install-links.sh through the real /bin/sh shim."""
import os
import shutil
import subprocess
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2]
ROOT = SCRIPTS.parents[2]
LINKED = ["vcoord", "vdev", "vfile", "vgroom", "vplan", "vreport", "vstatus", "vstop"]


def _clone(tmp_path):
    """A scratch git repository holding a copy of the scripts and the eight skill directories."""
    clone = (tmp_path / "clone").resolve()
    scripts = clone / "skills" / "tdd" / "scripts"
    scripts.mkdir(parents=True)
    ignore = shutil.ignore_patterns("__pycache__", "tests")
    for part in ("lib", "veri"):
        shutil.copytree(SCRIPTS / part, scripts / part, ignore=ignore)
    shutil.copy(SCRIPTS / "install-links.sh", scripts)
    for name in LINKED:
        (clone / "skills" / name).mkdir()
    subprocess.run(["git", "-C", str(clone), "init", "-q", "-b", "main"], check=True)
    return clone, scripts / "install-links.sh"


@pytest.mark.process("git init of a scratch repository, then install-links.sh run as the /bin/sh shim it is")
@pytest.mark.tree_audit("copies the scripts lib and veri directories into a scratch clone")
def test_install_links_sh_links_exactly_the_eight_skills_into_the_main_tree_and_is_a_documented_shim_over_its_module(
        tmp_path):
    clone, shim = _clone(tmp_path)
    done = subprocess.run(["/bin/sh", str(shim), str(clone)], stdin=subprocess.DEVNULL,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    skills = clone / ".claude" / "skills"
    entries = sorted(p.name for p in skills.iterdir()) if skills.is_dir() else []
    resolved = [(skills / n).resolve() == (clone / "skills" / n).resolve() for n in entries]
    text = shim.read_text() if shim.exists() else ""
    usage = [line for line in text.splitlines() if "Usage:" in line]
    tdd = ROOT / "skills" / "tdd"
    docs = (tdd / "SKILL.md").read_text() + (tdd / "SCRIPTS.md").read_text()
    assert (done.returncode, entries, all(resolved), text.startswith("#!/bin/sh"),
            (shim.parent / "veri" / "install_links.py").exists(),
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
@pytest.mark.tree_audit("copies the scripts lib and veri directories into a scratch clone")
def test_install_links_sh_points_each_link_at_the_normalised_absolute_path_of_its_skill_in_the_clone(tmp_path):
    clone, shim = _clone(tmp_path)
    done = subprocess.run(["/bin/sh", str(shim), str(clone)], stdin=subprocess.DEVNULL,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    skills = clone / ".claude" / "skills"
    targets = {n: os.readlink(skills / n) for n in LINKED if (skills / n).is_symlink()}
    assert (done.returncode, targets) == (0, {n: str(clone / "skills" / n) for n in LINKED})


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


@pytest.mark.process("git init, commit and worktree add on a scratch clone, then install-links.sh run from the worktree")
@pytest.mark.tree_audit("copies the scripts lib and veri directories into a scratch clone")
def test_install_links_sh_run_from_a_linked_worktree_of_veri_links_each_skill_under_the_main_clone(tmp_path):
    clone, _ = _clone(tmp_path)
    for name in LINKED:
        (clone / "skills" / name / "SKILL.md").write_text(name + "\n")
    git = ["git", "-C", str(clone), "-c", "user.name=t", "-c", "user.email=t@t"]
    subprocess.run(git + ["add", "-A"], check=True)
    subprocess.run(git + ["commit", "-q", "-m", "scripts"], check=True)
    wt = (tmp_path / "wt").resolve()
    subprocess.run(git + ["worktree", "add", "-q", "--detach", str(wt)], check=True)
    shim = wt / "skills" / "tdd" / "scripts" / "install-links.sh"
    done = subprocess.run(["/bin/sh", str(shim)], cwd=wt, stdin=subprocess.DEVNULL,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    skills = clone / ".claude" / "skills"
    targets = {n: os.readlink(skills / n) for n in LINKED if (skills / n).is_symlink()}
    assert (done.returncode, targets) == (0, {n: str(clone / "skills" / n) for n in LINKED})


@pytest.mark.process("git init of a scratch repository, then install-links.sh run as the /bin/sh shim it is")
@pytest.mark.tree_audit("copies the scripts lib and veri directories into a scratch clone")
def test_install_links_sh_link_lets_the_filesystem_resolve_dotdot_to_the_unlinked_tdd_and_vmerge_skills(tmp_path):
    clone, shim = _clone(tmp_path)
    (clone / "skills" / "vmerge").mkdir()
    (clone / "skills" / "vmerge" / "SKILL.md").write_text("vmerge\n")
    done = subprocess.run(["/bin/sh", str(shim), str(clone)], stdin=subprocess.DEVNULL,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    skills = clone / ".claude" / "skills"
    base = str(skills / "vcoord")
    scripts = os.stat(base + "/../tdd/scripts/")
    merge = os.stat(base + "/../vmerge/SKILL.md")
    assert (done.returncode, (skills / "tdd").exists(), (skills / "vmerge").exists(),
            os.path.samestat(scripts, os.stat(clone / "skills" / "tdd" / "scripts")),
            os.path.samestat(merge, os.stat(clone / "skills" / "vmerge" / "SKILL.md"))) == (0, False, False, True, True)


@pytest.mark.process("git init, commit and worktree add on a scratch project, then install-links.sh run against the worktree")
@pytest.mark.tree_audit("copies the scripts lib and veri directories into a scratch clone")
def test_install_links_sh_run_against_a_linked_worktree_of_a_project_installs_into_its_main_tree_and_nothing_in_the_worktree(
        tmp_path):
    _, shim = _clone(tmp_path)
    project = (tmp_path / "project").resolve()
    project.mkdir()
    git = ["git", "-C", str(project), "-c", "user.name=t", "-c", "user.email=t@t"]
    subprocess.run(git + ["init", "-q", "-b", "main"], check=True)
    subprocess.run(git + ["commit", "-q", "--allow-empty", "-m", "init"], check=True)
    wt = (tmp_path / "project-wt").resolve()
    subprocess.run(git + ["worktree", "add", "-q", "--detach", str(wt)], check=True)
    done = subprocess.run(["/bin/sh", str(shim), str(wt)], cwd=wt, stdin=subprocess.DEVNULL,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    skills = project / ".claude" / "skills"
    entries = sorted(p.name for p in skills.iterdir()) if skills.is_dir() else []
    assert (done.returncode, entries, (wt / ".claude").exists()) == (0, LINKED, False)


@pytest.mark.process("git init, commit and status on a scratch project, then install-links.sh run against it")
@pytest.mark.tree_audit("copies the scripts lib and veri directories into a scratch clone")
def test_install_links_sh_lists_each_link_once_in_the_common_dir_exclude_file_and_leaves_git_status_clean(tmp_path):
    _, shim = _clone(tmp_path)
    project = (tmp_path / "project").resolve()
    project.mkdir()
    git = ["git", "-C", str(project), "-c", "user.name=t", "-c", "user.email=t@t"]
    subprocess.run(git + ["init", "-q", "-b", "main"], check=True)
    subprocess.run(git + ["commit", "-q", "--allow-empty", "-m", "init"], check=True)
    done = subprocess.run(["/bin/sh", str(shim), str(project)], stdin=subprocess.DEVNULL,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    exclude = project / ".git" / "info" / "exclude"
    lines = exclude.read_text().splitlines() if exclude.exists() else []
    listed = {n: sum(1 for line in lines if line.strip().strip("/") == ".claude/skills/" + n) for n in LINKED}
    status = subprocess.run(git + ["status", "--porcelain"], stdout=subprocess.PIPE, text=True, check=True)
    assert (done.returncode, listed, status.stdout) == (0, {n: 1 for n in LINKED}, "")


@pytest.mark.process("git init and commit on a scratch project, then install-links.sh run against it")
@pytest.mark.tree_audit("copies the scripts lib and veri directories into a scratch clone")
def test_install_links_sh_does_not_list_again_a_link_path_the_exclude_file_already_holds(tmp_path):
    _, shim = _clone(tmp_path)
    project = (tmp_path / "project").resolve()
    project.mkdir()
    git = ["git", "-C", str(project), "-c", "user.name=t", "-c", "user.email=t@t"]
    subprocess.run(git + ["init", "-q", "-b", "main"], check=True)
    exclude = project / ".git" / "info" / "exclude"
    exclude.parent.mkdir(exist_ok=True)
    with exclude.open("a") as out:
        out.write("/.claude/skills/vdev\n")
    done = subprocess.run(["/bin/sh", str(shim), str(project)], stdin=subprocess.DEVNULL,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    lines = [line.strip().strip("/") for line in exclude.read_text().splitlines()]
    listed = {n: lines.count(".claude/skills/" + n) for n in LINKED}
    assert (done.returncode, listed) == (0, {n: 1 for n in LINKED})


@pytest.mark.process("git init and commit on a scratch project, then install-links.sh run twice against it")
@pytest.mark.tree_audit("copies the scripts lib and veri directories into a scratch clone")
def test_install_links_sh_second_run_changes_no_link_and_not_the_exclude_file_and_exits_0(tmp_path):
    _, shim = _clone(tmp_path)
    project = (tmp_path / "project").resolve()
    project.mkdir()
    git = ["git", "-C", str(project), "-c", "user.name=t", "-c", "user.email=t@t"]
    subprocess.run(git + ["init", "-q", "-b", "main"], check=True)
    skills = project / ".claude" / "skills"
    exclude = project / ".git" / "info" / "exclude"

    def run():
        return subprocess.run(["/bin/sh", str(shim), str(project)], stdin=subprocess.DEVNULL,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    def snapshot():
        links = {n: os.readlink(skills / n) for n in LINKED if (skills / n).is_symlink()}
        return links, exclude.read_bytes() if exclude.exists() else b""

    first = run()
    before = snapshot()
    second = run()
    assert (first.returncode, second.returncode, snapshot() == before, second.stderr) == (0, 0, True, "")


@pytest.mark.process("git init on a scratch project, then install-links.sh run against it holding a dangling veri link")
@pytest.mark.tree_audit("copies the scripts lib and veri directories into a scratch clone")
def test_install_links_sh_repairs_a_dangling_veri_link_so_it_resolves_again_under_the_veri_main_clone(tmp_path):
    clone, shim = _clone(tmp_path)
    project = (tmp_path / "project").resolve()
    project.mkdir()
    subprocess.run(["git", "-C", str(project), "init", "-q", "-b", "main"], check=True)
    skills = project / ".claude" / "skills"
    skills.mkdir(parents=True)
    os.symlink(clone / "skills" / "vdev-renamed-away", skills / "vdev")
    done = subprocess.run(["/bin/sh", str(shim), str(project)], stdin=subprocess.DEVNULL,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    repaired = os.readlink(skills / "vdev") if (skills / "vdev").is_symlink() else None
    assert (done.returncode, repaired, (skills / "vdev").exists()) == (0, str(clone / "skills" / "vdev"), True)


@pytest.mark.process("git init on a scratch project, then install-links.sh run against it holding a plain file at the last link path")
@pytest.mark.tree_audit("copies the scripts lib and veri directories into a scratch clone")
def test_install_links_sh_leaves_a_non_veri_path_untouched_and_exits_2_naming_it_with_no_link_created(tmp_path):
    _, shim = _clone(tmp_path)
    project = (tmp_path / "project").resolve()
    project.mkdir()
    subprocess.run(["git", "-C", str(project), "init", "-q", "-b", "main"], check=True)
    skills = project / ".claude" / "skills"
    skills.mkdir(parents=True)
    (skills / LINKED[-1]).write_text("mine\n")
    done = subprocess.run(["/bin/sh", str(shim), str(project)], stdin=subprocess.DEVNULL,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    entries = sorted(p.name for p in skills.iterdir())
    kept = (skills / LINKED[-1]).read_text() if (skills / LINKED[-1]).is_file() else None
    assert (done.returncode, str(skills / LINKED[-1]) in done.stderr, entries, kept) == (
        2, True, [LINKED[-1]], "mine\n")


@pytest.mark.process("git init on a scratch project, then install-links.sh run against it holding symlinks elsewhere")
@pytest.mark.tree_audit("copies the scripts lib and veri directories into a scratch clone")
def test_install_links_sh_leaves_a_symlink_elsewhere_untouched_and_exits_2_naming_it_with_no_link_created(tmp_path):
    _, shim = _clone(tmp_path)
    project = (tmp_path / "project").resolve()
    project.mkdir()
    subprocess.run(["git", "-C", str(project), "init", "-q", "-b", "main"], check=True)
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    skills = project / ".claude" / "skills"
    skills.mkdir(parents=True)
    (skills / LINKED[0]).symlink_to(elsewhere)
    (skills / LINKED[-1]).symlink_to(tmp_path / "nowhere")
    done = subprocess.run(["/bin/sh", str(shim), str(project)], stdin=subprocess.DEVNULL,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    entries = {p.name: os.readlink(p) for p in skills.iterdir()}
    assert (done.returncode, str(skills / LINKED[0]) in done.stderr, entries) == (
        2, True, {LINKED[0]: str(elsewhere), LINKED[-1]: str(tmp_path / "nowhere")})


@pytest.mark.process("git init on a scratch project, then install-links.sh run against it holding one dangling symlink elsewhere")
@pytest.mark.tree_audit("copies the scripts lib and veri directories into a scratch clone")
def test_install_links_sh_leaves_a_lone_dangling_symlink_elsewhere_untouched_and_exits_2_naming_it(tmp_path):
    _, shim = _clone(tmp_path)
    project = (tmp_path / "project").resolve()
    project.mkdir()
    subprocess.run(["git", "-C", str(project), "init", "-q", "-b", "main"], check=True)
    skills = project / ".claude" / "skills"
    skills.mkdir(parents=True)
    (skills / LINKED[-1]).symlink_to(tmp_path / "nowhere")
    done = subprocess.run(["/bin/sh", str(shim), str(project)], stdin=subprocess.DEVNULL,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    entries = {p.name: os.readlink(p) for p in skills.iterdir()}
    assert (done.returncode, str(skills / LINKED[-1]) in done.stderr, entries) == (
        2, True, {LINKED[-1]: str(tmp_path / "nowhere")})


@pytest.mark.process("git, asked by install-links.sh for the common directory of a plain directory outside any repository")
def test_install_links_sh_run_from_outside_a_git_repository_exits_2_and_creates_nothing(tmp_path):
    plain = tmp_path / "plain"
    plain.mkdir()
    done = subprocess.run(["/bin/sh", str(SCRIPTS / "install-links.sh")], cwd=plain, stdin=subprocess.DEVNULL,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    assert (done.returncode, sorted(p.name for p in tmp_path.rglob("*")), "Traceback" in done.stderr) == (
        2, ["plain"], False)


@pytest.mark.process("git init --template= on a scratch project, then install-links.sh run against it")
@pytest.mark.tree_audit("copies the scripts lib and veri directories into a scratch clone")
def test_install_links_sh_in_a_repo_with_no_git_info_directory_creates_it_and_lists_the_eight_links_2830(tmp_path):
    _, shim = _clone(tmp_path)
    project = (tmp_path / "project").resolve()
    project.mkdir()
    subprocess.run(["git", "-C", str(project), "init", "-q", "-b", "main", "--template="], check=True)
    assert not (project / ".git" / "info").exists()
    done = subprocess.run(["/bin/sh", str(shim), str(project)], stdin=subprocess.DEVNULL,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    exclude = project / ".git" / "info" / "exclude"
    lines = exclude.read_text().splitlines() if exclude.exists() else []
    skills = project / ".claude" / "skills"
    links = sorted(p.name for p in skills.iterdir() if p.is_symlink()) if skills.is_dir() else []
    assert (done.returncode, sorted(lines), links) == (
        0, sorted("/.claude/skills/" + n for n in LINKED), sorted(LINKED))
