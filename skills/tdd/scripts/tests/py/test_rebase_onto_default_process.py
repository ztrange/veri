"""Cases for rebase-onto-default.sh that start a real process."""
import os
import subprocess
import sys

import pytest

from conftest import SCRIPTS


@pytest.mark.process("rebase-onto-default.sh run for real, in a directory that is no git repository")
def test_rebase_onto_default_sh_forwards_the_modules_exit_code_as_its_own(tmp_path):
    ran = subprocess.run([str(SCRIPTS / "rebase-onto-default.sh")], cwd=tmp_path, capture_output=True, text=True,
                         env={"PATH": os.path.dirname(sys.executable) + ":/usr/bin:/bin",
                              "PYTHONDONTWRITEBYTECODE": "1", "GIT_CEILING_DIRECTORIES": str(tmp_path.parent)})

    assert (ran.returncode, ran.stdout) == (2, "")
    assert ran.stderr.endswith("rebase-onto-default: refs/remotes/origin/HEAD is not set — no default branch to rebase onto\n")


def _git(repo, *argv):
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *argv], cwd=repo, check=True,
                          capture_output=True, text=True).stdout.strip()


def _diverged(tmp_path, main_lines, branch_lines, branch_other=None):
    """A clone whose branch and origin's default both edit GRADED after a shared base."""
    origin, clone = tmp_path / "origin", tmp_path / "clone"
    origin.mkdir()
    _git(origin, "init", "-q", "-b", "main")
    (origin / "GRADED").write_text("a sig-a\nz sig-z\n")
    _git(origin, "add", "-A")
    _git(origin, "commit", "-q", "-m", "base")
    _git(tmp_path, "clone", "-q", str(origin), str(clone))
    (origin / "GRADED").write_text(main_lines)
    _git(origin, "add", "-A")
    _git(origin, "commit", "-q", "-m", "main signs")
    _git(clone, "checkout", "-q", "-b", "work")
    (clone / "GRADED").write_text(branch_lines)
    if branch_other:
        (clone / branch_other[0]).write_text(branch_other[1])
    _git(clone, "add", "-A")
    _git(clone, "commit", "-q", "-m", "branch signs")
    return origin, clone


MAIN_SIGNS = "a sig-a\nm sig-m\nz sig-z\n"
BRANCH_SIGNS = "a sig-a2\nb sig-b\nz sig-z\n"


@pytest.mark.process("rebase-onto-default.sh's module run over a real clone whose GRADED conflicts with origin")
def test_2706_a_conflict_confined_to_graded_is_unioned_by_unit_and_the_rebase_finishes(tmp_path, run_cli, monkeypatch):
    import importlib
    rebase = importlib.import_module("veri.rebase_onto_default")
    origin, clone = _diverged(tmp_path, MAIN_SIGNS, BRANCH_SIGNS)
    onto = _git(origin, "rev-parse", "HEAD")

    code, out, err = run_cli(rebase, [], cwd=clone)

    lines = (clone / "GRADED").read_text().splitlines()
    assert (code, out.splitlines()[1], sorted(lines)) == (0, onto, ["a sig-a2", "b sig-b", "m sig-m", "z sig-z"])
    assert len(_git(clone, "log", "--format=%H", onto + "..HEAD").split()) == 1


@pytest.mark.process("rebase-onto-default.sh's module run over a real clone conflicting in GRADED and another file")
def test_2706_a_conflict_touching_another_path_still_answers_1_and_aborts(tmp_path, run_cli):
    import importlib
    rebase = importlib.import_module("veri.rebase_onto_default")
    origin, clone = _diverged(tmp_path, MAIN_SIGNS, BRANCH_SIGNS)
    (origin / "other").write_text("main\n")
    _git(origin, "add", "-A")
    _git(origin, "commit", "-q", "-m", "main other")
    (clone / "other").write_text("branch\n")
    _git(clone, "add", "-A")
    _git(clone, "commit", "-q", "-m", "branch other")

    code, out, _ = run_cli(rebase, [], cwd=clone)

    assert (code, out) == (1, "other\n")
    assert _git(clone, "status", "--porcelain") == ""


@pytest.mark.process("graded-only-conflict.sh's module run over a real clone")
@pytest.mark.parametrize("other, want", ((None, 0), (("other", 1), 1)), ids=("graded-only", "another-path"))
def test_2706_graded_only_conflict_answers_whether_every_conflicting_path_is_a_graded_file(tmp_path, run_cli, other, want):
    import importlib
    graded_only = importlib.import_module("veri.graded_only_conflict")
    origin, clone = _diverged(tmp_path, MAIN_SIGNS, BRANCH_SIGNS)
    if other:
        (origin / "other").write_text("main\n")
        _git(origin, "add", "-A")
        _git(origin, "commit", "-q", "-m", "main other")
        (clone / "other").write_text("branch\n")
        _git(clone, "add", "-A")
        _git(clone, "commit", "-q", "-m", "branch other")
    _git(clone, "fetch", "-q", "origin")

    assert run_cli(graded_only, [], cwd=clone)[0] == want
