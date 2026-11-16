"""Cases for record-test-commands.sh against real git: a bare origin, a clone of it, the pull request faked at gh."""
import importlib

import pytest

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
