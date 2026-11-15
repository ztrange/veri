"""Process-starting cases split from unit/test_invisible_work.py, which holds the small cases of the same module."""
import importlib
import os
import pathlib
import subprocess

import pytest


def run_git(repo, *args):
    done = subprocess.run(
        ["git", "-C", str(repo), "-c", "user.name=veri", "-c", "user.email=veri@example.test", *args],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, check=True)
    return done.stdout


def ref_state(clone, origin):
    return (run_git(clone, "for-each-ref", "--format=clone %(refname) %(objectname) %(symref)")
            + run_git(clone, "worktree", "list", "--porcelain")
            + run_git(origin, "for-each-ref", "--format=origin %(refname) %(objectname) %(symref)")
            + "origin HEAD " + run_git(origin, "symbolic-ref", "HEAD"))


def seed_origin(src, origin):
    subprocess.run(["git", "init", "-q", "-b", "main", str(src)], check=True)
    run_git(src, "commit", "-q", "--allow-empty", "-m", "initial")
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(origin)], check=True)
    run_git(src, "remote", "add", "origin", str(origin))
    run_git(src, "push", "-q", "-u", "origin", "main")


@pytest.mark.process("real git: a clone, its origin and a linked worktree, whose refs are read before and after the run")
def test_main_writes_to_no_ref_so_the_refs_of_the_clone_and_of_origin_are_byte_identical_after_a_run(
        run_cli, tmp_path):
    invisible_work = importlib.import_module("veri.invisible_work")
    src, origin, clone = tmp_path / "src", tmp_path / "origin.git", tmp_path / "clone"
    seed_origin(src, origin)
    for branch in ("chore/nobody-opened-a-pr", "tdd/4-supervised-leaves", "chore/deleted-on-origin"):
        run_git(src, "checkout", "-q", "-b", branch, "main")
        run_git(src, "commit", "-q", "--allow-empty", "-m", "chore: work with no PR")
        run_git(src, "push", "-q", "origin", branch)
    subprocess.run(["git", "clone", "-q", str(origin), str(clone)], check=True)
    run_git(clone, "branch", "-q", "tdd/4-supervised-leaves", "origin/tdd/4-supervised-leaves")
    run_git(clone, "tag", "-a", "-m", "v0.1", "v0.1", "origin/main")
    run_git(clone, "worktree", "add", "-q", "-b", "tdd/150-never-pushed", str(tmp_path / "wt-150"), "origin/main")
    run_git(tmp_path / "wt-150", "commit", "-q", "--allow-empty", "-m", "feat: a step nobody pushed (#150)")
    run_git(src, "push", "-q", "origin", "--delete", "chore/deleted-on-origin")
    run_git(src, "checkout", "-q", "-b", "chore/pushed-after-the-fetch", "main")
    run_git(src, "commit", "-q", "--allow-empty", "-m", "chore: work the clone has not fetched")
    run_git(src, "push", "-q", "origin", "chore/pushed-after-the-fetch")
    (tmp_path / "gh").mkdir()
    (tmp_path / "gh" / "issues.json").write_text("[]\n")
    (tmp_path / "gh" / "prs.json").write_text(
        '[{"headRefName": "tdd/4-supervised-leaves", "state": "MERGED", "body": "Closes #4"}]\n')

    before = ref_state(clone, origin)
    code, out, _ = run_cli(invisible_work, [], env={"VERI_GH_JSON": str(tmp_path / "gh")}, cwd=clone)
    after = ref_state(clone, origin)

    assert code == 0
    assert "chore/nobody-opened-a-pr" in out and "tdd/150-never-pushed" in out
    assert after == before


def unpr_clone(tmp_path, branch, ahead):
    src, origin, clone = tmp_path / "src", tmp_path / "origin.git", tmp_path / "clone"
    seed_origin(src, origin)
    run_git(src, "checkout", "-q", "-b", branch)
    for i in range(1, ahead + 1):
        run_git(src, "commit", "-q", "--allow-empty", "-m", f"feat: step {i} of a run nobody can see (#71)")
    run_git(src, "push", "-q", "origin", branch)
    subprocess.run(["git", "clone", "-q", str(origin), str(clone)], check=True)
    gh = tmp_path / "gh"
    gh.mkdir()
    (gh / "issues.json").write_text(
        '[{"number": 71, "title": "report: version the commentary too", "labels": [], "body": "", "state": "OPEN"}]\n')
    (gh / "prs.json").write_text("[]\n")
    return clone, origin, gh


@pytest.mark.process("invisible-work.sh run through a symlink to the skill directory from a subdirectory of a real clone")
def test_main_prints_the_same_report_stderr_and_exit_code_through_a_symlink_to_the_skill_directory_from_a_subdirectory_as_in_place(
        run_cli, tmp_path):
    invisible_work = importlib.import_module("veri.invisible_work")
    local_only = "tdd/150-a-run-that-never-reached-origin"
    clone, _, gh = unpr_clone(tmp_path, "tdd/71-report-version-the-commentary-too", 2)
    run_git(clone, "checkout", "-q", "-b", local_only, "main")
    run_git(clone, "commit", "-q", "--allow-empty", "-m", "feat: a step nobody pushed (#150)")
    run_git(clone, "checkout", "-q", "main")
    (clone / "sub" / "dir").mkdir(parents=True)
    (tmp_path / "linked-skill").symlink_to(
        pathlib.Path(invisible_work.__file__).resolve().parents[2], target_is_directory=True)

    in_place = run_cli(invisible_work, [], env={"VERI_GH_JSON": str(gh)}, cwd=clone)
    linked = subprocess.run([str(tmp_path / "linked-skill" / "scripts" / "invisible-work.sh")],
                            cwd=clone / "sub" / "dir", env={**os.environ, "VERI_GH_JSON": str(gh)},
                            stdin=subprocess.DEVNULL, capture_output=True, text=True)

    assert in_place[0] == 0 and local_only in in_place[1]
    assert (linked.returncode, linked.stdout, linked.stderr) == in_place


@pytest.mark.process("real git: a clone whose refs/remotes/origin/HEAD is deleted, resolved from its origin")
def test_main_prints_the_same_report_and_exit_code_with_no_origin_head_ref_as_when_it_is_set(run_cli, tmp_path):
    invisible_work = importlib.import_module("veri.invisible_work")
    branch = "tdd/71-report-version-the-commentary-too"
    clone, _, gh = unpr_clone(tmp_path, branch, 3)

    set_code, set_out, set_err = run_cli(invisible_work, [], env={"VERI_GH_JSON": str(gh)}, cwd=clone)
    run_git(clone, "config", "remote.origin.followRemoteHEAD", "never")
    run_git(clone, "symbolic-ref", "--delete", "refs/remotes/origin/HEAD")
    unset_code, unset_out, unset_err = run_cli(invisible_work, [], env={"VERI_GH_JSON": str(gh)}, cwd=clone)

    assert (set_code, branch in set_out) == (0, True), set_err
    assert (unset_code, unset_out) == (set_code, set_out), unset_err


@pytest.mark.process("real git: a clone with no refs/remotes/origin/HEAD whose origin's HEAD is detached")
def test_main_exits_2_naming_refs_remotes_origin_head_when_neither_the_ref_nor_the_remote_names_a_default(
        run_cli, tmp_path):
    invisible_work = importlib.import_module("veri.invisible_work")
    clone, origin, gh = unpr_clone(tmp_path, "tdd/71-report-version-the-commentary-too", 1)
    run_git(clone, "config", "remote.origin.followRemoteHEAD", "never")
    run_git(clone, "symbolic-ref", "--delete", "refs/remotes/origin/HEAD")
    run_git(origin, "update-ref", "--no-deref", "HEAD", run_git(origin, "rev-parse", "refs/heads/main").strip())

    code, out, err = run_cli(invisible_work, [], env={"VERI_GH_JSON": str(gh)}, cwd=clone)

    assert code == 2, (out, err)
    assert "refs/remotes/origin/HEAD" in err
