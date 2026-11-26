"""Process-starting cases split from unit/test_ensure_run_state_ignored.py, which holds the small cases of the same module."""
import importlib
import pathlib
import shutil
import subprocess

import pytest

from repo_builder import new_repo

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
GITIGNORE = SCRIPTS.parents[2] / ".gitignore"


@pytest.fixture
def ensure_run_state_ignored():
    return importlib.import_module("veri.ensure_run_state_ignored")


def git(repo, *args, **kwargs):
    return subprocess.run(["git", "-C", str(repo), "-c", "user.name=veri", "-c", "user.email=veri@example.test", *args],
                          capture_output=True, text=True, **kwargs)


def ignored(repo, name):
    return git(repo, "check-ignore", "-q", name).returncode


@pytest.mark.process("git: check-ignore over the .gitignore the script wrote in a real scratch repository")
def test_no_gitignore_creates_one_ignoring_the_run_log_but_not_the_ledger(tmp_path, run_cli, ensure_run_state_ignored):
    repo = new_repo(tmp_path / "fresh")

    run_cli(ensure_run_state_ignored, [str(repo)])

    assert (ignored(repo, ".tdd/develop-red.log"), ignored(repo, ".tdd/issue-7.md")) == (0, 1)


@pytest.mark.process("git: check-ignore over a .gitignore the script appended to in a real scratch repository")
def test_an_unrelated_gitignore_keeps_every_existing_line_and_reports_added(tmp_path, run_cli,
                                                                            ensure_run_state_ignored):
    repo = new_repo(tmp_path / "unrelated")
    (repo / ".gitignore").write_bytes(b"node_modules/\n*.log")

    code, out, err = run_cli(ensure_run_state_ignored, [str(repo)])

    assert (code, out) == (0, "added\n")
    assert (ignored(repo, "node_modules/x"), ignored(repo, "debug.log"), ignored(repo, ".tdd/develop-red.log"),
            ignored(repo, ".tdd/issue-7.md")) == (0, 0, 0, 1)


@pytest.mark.process("git: rev-parse in a real scratch repository whose .gitignore is veri's own")
def test_4338_a_gitignore_holding_the_4048_rule_block_reports_already_present_and_stays_byte_identical(
        tmp_path, run_cli, ensure_run_state_ignored):
    repo = new_repo(tmp_path / "holds-4048")
    (repo / ".gitignore").write_bytes(GITIGNORE.read_bytes())

    code, out, err = run_cli(ensure_run_state_ignored, [str(repo)])

    assert (code, out) == (0, "already present\n")
    assert (repo / ".gitignore").read_bytes() == GITIGNORE.read_bytes()


@pytest.mark.process("git: the caller's checkout and a linked worktree under .tdd/wt/1, both real")
def test_the_callers_checkout_stays_clean_while_the_worktree_holding_the_rule_exists(tmp_path, run_cli,
                                                                                      ensure_run_state_ignored):
    repo = new_repo(tmp_path / "caller")
    git(repo, "commit", "-q", "--allow-empty", "-m", "initial")
    git(repo, "worktree", "add", str(repo / ".tdd" / "wt" / "1"), "-b", "tdd/1")
    wt = repo / ".tdd" / "wt" / "1"

    run_cli(ensure_run_state_ignored, [str(wt)])
    git(wt, "add", ".gitignore")
    git(wt, "commit", "-q", "-m", "chore: ignore veri run state (#1)")

    assert (git(repo, "status", "--porcelain").stdout, wt.is_dir()) == ("", True)


@pytest.mark.process("git: check-ignore in a real worktree whose common directory also carries the rule")
def test_a_worktree_with_the_rule_in_info_exclude_too_still_ignores_the_run_log_and_not_the_ledger(
        tmp_path, run_cli, ensure_run_state_ignored):
    repo = new_repo(tmp_path / "caller")
    git(repo, "commit", "-q", "--allow-empty", "-m", "initial")
    git(repo, "worktree", "add", str(repo / ".tdd" / "wt" / "1"), "-b", "tdd/1")
    wt = repo / ".tdd" / "wt" / "1"

    run_cli(ensure_run_state_ignored, [str(wt)])
    git(wt, "add", ".gitignore")
    git(wt, "commit", "-q", "-m", "chore: ignore veri run state (#1)")

    assert (ignored(wt, ".tdd/develop-red.log"), ignored(wt, ".tdd/issue-1.md")) == (0, 1)


@pytest.mark.process("git: rev-parse run for real outside any repository, its own diagnostic on stderr")
def test_not_a_git_repository_exits_2_prints_nothing_on_stdout_and_lets_gits_own_diagnostic_through(
        tmp_path, monkeypatch, run_cli, ensure_run_state_ignored):
    target = tmp_path / "not-a-repo"
    target.mkdir()
    monkeypatch.setenv("GIT_CEILING_DIRECTORIES", str(tmp_path))
    want = subprocess.run(["git", "-C", str(target), "rev-parse", "--git-common-dir"], capture_output=True,
                          text=True).stderr

    code, out, err = run_cli(ensure_run_state_ignored, [str(target)])

    assert want != ""
    assert (code, out, err) == (2, "", want)


@pytest.mark.process("ensure-run-state-ignored.sh run as a real process through a symlink to the skill directory")
def test_a_run_through_a_symlink_to_the_skill_directory_from_another_directory_answers_as_in_place(tmp_path):
    (tmp_path / "linked-skill").symlink_to(SCRIPTS.parent, target_is_directory=True)
    in_place = new_repo(tmp_path / "in-place")
    linked = new_repo(tmp_path / "linked")

    ran_in_place = subprocess.run([str(SCRIPTS / "ensure-run-state-ignored.sh")], cwd=in_place,
                                  capture_output=True, text=True)
    ran_linked = subprocess.run([str(tmp_path / "linked-skill" / "scripts" / "ensure-run-state-ignored.sh")],
                                cwd=linked, capture_output=True, text=True)

    assert (ran_in_place.returncode, ran_in_place.stdout, ran_in_place.stderr) == (0, "added\n", "")
    assert (ran_linked.returncode, ran_linked.stdout, ran_linked.stderr) == (0, "added\n", "")
    assert (linked / ".gitignore").read_bytes() == (in_place / ".gitignore").read_bytes()


@pytest.mark.process("a mutated ensure-run-state-ignored.sh run as a real process from its own directory beside a decoy repository")
@pytest.mark.tree_audit("copies the skill's veri/ module directory into a decoy tree")
def test_1158_a_shim_that_drops_its_root_argument_and_runs_from_its_own_directory_writes_nothing_outside_the_scratch_repository(
        tmp_path):
    repo = new_repo(tmp_path / "pinned-scratch")
    decoy = new_repo(tmp_path / "decoy")
    exclude_before = (decoy / ".git" / "info" / "exclude").read_bytes()
    mutant = decoy / "skills" / "tdd" / "scripts"
    mutant.mkdir(parents=True)
    shutil.copytree(SCRIPTS / "veri", mutant / "veri", ignore=shutil.ignore_patterns("__pycache__"))
    lines = []
    for line in (SCRIPTS / "ensure-run-state-ignored.sh").read_text().splitlines():
        if line.startswith(("exec python3", '. "$(dirname "$0")/lib/shim-python.sh"', 'exec "$py"')):
            if not any(line == 'cd "$(dirname "$0")"' for line in lines):
                lines.append('cd "$(dirname "$0")"')
            line = line.replace(' "$@"', "")
        lines.append(line)
    if (SCRIPTS / "lib" / "shim-python.sh").is_file():
        (mutant / "lib").mkdir()
        shutil.copy(SCRIPTS / "lib" / "shim-python.sh", mutant / "lib" / "shim-python.sh")
        shutil.copy(SCRIPTS / "lib" / "venv-python.sh", mutant / "lib" / "venv-python.sh")
    (mutant / "ensure-run-state-ignored.sh").write_text("\n".join(lines) + "\n")
    (mutant / "ensure-run-state-ignored.sh").chmod(0o755)

    ran = subprocess.run([str(mutant / "ensure-run-state-ignored.sh"), str(repo)], capture_output=True, text=True)

    assert not (decoy / ".gitignore").exists()
    assert not (mutant / ".gitignore").exists()
    assert (decoy / ".git" / "info" / "exclude").read_bytes() == exclude_before
    if ran.returncode == 0:
        assert ignored(repo, ".tdd/develop-red.log") == 0
    else:
        assert not (repo / ".gitignore").exists()
