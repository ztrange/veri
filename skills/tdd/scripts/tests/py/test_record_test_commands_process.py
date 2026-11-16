"""Cases for record-test-commands.sh against real git: a bare origin, a clone of it, the pull request faked at gh."""
import importlib
import subprocess

import pytest

from conftest import SCRIPTS
from repo_builder import commit_all, git, new_repo

URL = "https://example.test/pull/1"


@pytest.fixture
def record():
    return importlib.import_module("veri.record_test_commands")


@pytest.fixture
def detect():
    return importlib.import_module("veri.detect_test_command")


@pytest.fixture(autouse=True)
def pulls(monkeypatch):
    """The pull requests opened, as (head, base, title, body); gh itself is never reached."""
    github = importlib.import_module("veri.github")
    opened = []

    def create(head, base, title, body):
        opened.append((head, base, title, body))
        return URL

    monkeypatch.setattr(github, "gh_pr_create", create, raising=False)
    return opened


def project(tmp_path, **files):
    """(origin, clone): a bare origin whose main holds <files> (a README when none), and a clone of it with an identity."""
    seed = new_repo(tmp_path / "seed")
    commit_all(seed, "initial", **(files or {"README.md": "hello\n"}))
    origin, work = tmp_path / "origin.git", tmp_path / "work"
    git(tmp_path, "clone", "-q", "--bare", str(seed), str(origin))
    git(tmp_path, "clone", "-q", str(origin), str(work))
    git(work, "config", "user.name", "veri")
    git(work, "config", "user.email", "veri@example.test")
    return origin, work


def declared(detect, origin, sha, tmp_path, tier):
    """What detect-test-command.sh --tier <tier> prints on the commit <sha> of <origin>."""
    tree = tmp_path / ("readback-" + tier.replace(" ", "-"))
    tree.mkdir(exist_ok=True)
    (tree / "CLAUDE.md").write_text(git(origin, "show", "%s:CLAUDE.md" % sha) + "\n")
    command = detect.resolved(tier, "", str(tree))
    return None if command is None else command.decode()


@pytest.mark.process("git clone, commit-tree and push to a bare origin")
def test_it_pushes_veri_install_one_commit_on_the_default_tip_changing_only_a_created_claude_md_that_declares_both_commands(
        tmp_path, run_cli, record, detect):
    origin, work = project(tmp_path)
    tip = git(origin, "rev-parse", "main")
    fast, full = "make unit", 'pytest -q "tests dir" | tee out.txt'

    code, out, err = run_cli(record, [fast, full], cwd=work)

    assert code == 0, err
    branch = git(origin, "rev-parse", "refs/heads/veri-install")
    assert git(origin, "rev-parse", branch + "^") == tip
    assert git(origin, "diff", "--name-status", tip, branch) == "A\tCLAUDE.md"
    assert declared(detect, origin, branch, tmp_path, "fast") == fast
    assert declared(detect, origin, branch, tmp_path, "all") == full


@pytest.mark.process("git clone, commit-tree and push to a bare origin")
def test_it_opens_the_pr_from_veri_install_against_the_default_branch_prints_its_url_and_leaves_the_checkout_as_it_was(
        tmp_path, run_cli, record, pulls):
    origin, work = project(tmp_path)
    git(work, "checkout", "-q", "-b", "mid-work")
    (work / "README.md").write_text("edited\n")
    (work / "staged.txt").write_text("staged\n")
    git(work, "add", "staged.txt")
    before = (git(work, "rev-parse", "--abbrev-ref", "HEAD"), git(work, "status", "--porcelain"),
              git(work, "diff"), git(work, "diff", "--cached"))

    code, out, err = run_cli(record, ["make unit", "make test"], cwd=work)

    assert (code, out) == (0, URL + "\n"), err
    assert [(head, base) for head, base, title, body in pulls] == [("veri-install", "main")]
    assert all(title and body for head, base, title, body in pulls)
    assert (git(work, "rev-parse", "--abbrev-ref", "HEAD"), git(work, "status", "--porcelain"),
            git(work, "diff"), git(work, "diff", "--cached")) == before


def branches(origin):
    return git(origin, "for-each-ref", "--format=%(refname)", "refs/heads").split()


@pytest.mark.process("git clone and fetch from a bare origin")
def test_a_default_tip_already_declaring_both_commands_exactly_is_exit_3_with_no_branch_or_pr(
        tmp_path, run_cli, record, pulls):
    origin, work = project(tmp_path, **{"CLAUDE.md": "# P\nveri: fast tests: `make unit`\nveri: all tests: make test\n"})

    code, out, err = run_cli(record, ["make unit", "make test"], cwd=work)

    assert (code, out, branches(origin), pulls) == (3, "", ["refs/heads/main"], [])


@pytest.mark.process("git clone, ls-remote and push to a bare origin")
def test_an_origin_already_holding_veri_install_is_exit_2_naming_it_with_nothing_written(tmp_path, run_cli, record, pulls):
    origin, work = project(tmp_path)
    git(origin, "branch", "veri-install", "main")
    before = git(origin, "rev-parse", "veri-install")

    code, out, err = run_cli(record, ["make unit", "make test"], cwd=work)

    assert (code, out, pulls) == (2, "", [])
    assert "veri-install" in err
    assert git(origin, "rev-parse", "veri-install") == before


@pytest.mark.process("record-test-commands.sh, the shim, started as a script")
def test_the_shim_execs_its_module_an_empty_command_through_it_is_exit_2_with_the_usage(tmp_path):
    done = subprocess.run([str(SCRIPTS / "record-test-commands.sh"), "", "make test"],
                          capture_output=True, text=True, cwd=str(tmp_path))

    assert (done.returncode, done.stdout) == (2, "")
    assert "usage: record-test-commands.sh" in done.stderr
