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
    """The pull requests opened, as (head, base, title, body); gh itself is never reached. `opened.refusals` is how many
    next creates gh refuses; an opened one is listed as open from its head."""
    github = importlib.import_module("veri.github")

    class Opened(list):
        refusals = 0

    opened = Opened()

    def create(head, base, title, body):
        if opened.refusals:
            opened.refusals -= 1
            raise github.NoAnswer("", "HTTP 502: bad gateway\n")
        opened.append((head, base, title, body))
        return URL

    def listed(fields, state="open", head=None, limit=10000, repo=None):
        return [github.Pull(number=1, url=URL, html_url=URL, draft=False, head_ref=h, head_sha=None, body=b,
                            state="OPEN", labels=()) for h, _, _, b in opened if head in (None, h)]

    monkeypatch.setattr(github, "gh_pr_create", create, raising=False)
    monkeypatch.setattr(github, "open_pulls", listed)
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


@pytest.mark.process("git clone, commit-tree and push to a bare origin")
def test_one_file_puts_the_one_test_file_line_in_the_same_commit_and_the_detector_reads_it_back_exactly(
        tmp_path, run_cli, record, detect):
    origin, work = project(tmp_path)
    tip = git(origin, "rev-parse", "main")
    one = 'pytest -q "$1"'

    code, out, err = run_cli(record, ["--one-file", one, "make unit", "make test"], cwd=work)

    assert code == 0, err
    branch = git(origin, "rev-parse", "refs/heads/veri-install")
    assert git(origin, "rev-parse", branch + "^") == tip
    assert declared(detect, origin, branch, tmp_path, "one test file") == one
    assert (declared(detect, origin, branch, tmp_path, "fast"), declared(detect, origin, branch, tmp_path, "all")) == (
        "make unit", "make test")


@pytest.mark.process("git clone, commit-tree and push to a bare origin")
def test_with_one_file_exit_3_needs_the_tip_to_declare_it_too_else_the_branch_and_pr_are_made(tmp_path, run_cli, record, pulls):
    tiers = "veri: fast tests: make unit\nveri: all tests: make test\n"
    origin, work = project(tmp_path / "tiers-only", **{"CLAUDE.md": tiers})
    held_origin, held_work = project(tmp_path / "all-three", **{"CLAUDE.md": tiers + 'veri: one test file: pytest -q "$1"\n'})
    argv = ["--one-file", 'pytest -q "$1"', "make unit", "make test"]

    made = run_cli(record, argv, cwd=work)
    held = run_cli(record, argv, cwd=held_work)

    assert (made[0], held[:2]) == (0, (3, ""))
    assert (branches(origin), branches(held_origin)) == (["refs/heads/main", "refs/heads/veri-install"], ["refs/heads/main"])
    assert len(pulls) == 1


@pytest.mark.process("record-test-commands.sh, the shim, started as a script")
def test_the_shim_execs_its_module_an_empty_command_through_it_is_exit_2_with_the_usage(tmp_path):
    done = subprocess.run([str(SCRIPTS / "record-test-commands.sh"), "", "make test"],
                          capture_output=True, text=True, cwd=str(tmp_path))

    assert (done.returncode, done.stdout) == (2, "")
    assert "usage: record-test-commands.sh" in done.stderr


@pytest.mark.process("git clone and fetch from a bare origin")
@pytest.mark.parametrize("fast", ["make\nrm x", "echo veri: all tests: SUBSET", "echo veri: one test file: x", "   ",
                                  "  pytest  ", "`make unit`"])
def test_a_command_that_would_not_read_back_exactly_is_exit_2_naming_the_tier_with_nothing_pushed(
        tmp_path, run_cli, record, pulls, fast):
    origin, work = project(tmp_path)

    code, out, err = run_cli(record, [fast, "make test"], cwd=work)

    assert (code, out, branches(origin), pulls) == (2, "", ["refs/heads/main"], [])
    assert "veri: " in err and "read back" in err


@pytest.mark.process("git clone, commit-tree and push to a bare origin")
@pytest.mark.parametrize("fast", ["make test ARGS=`date`", "echo $(pwd) done", "pytest -q | tee out", "echo \"a\" 'b'",
                                  "make unit \\", "echo " + "a" * 4995, 'pytest -q "$1"'])
def test_a_command_that_reads_back_exactly_is_recorded(tmp_path, run_cli, record, detect, fast):
    origin, work = project(tmp_path)

    code, out, err = run_cli(record, [fast, "make test"], cwd=work)

    assert code == 0, err
    assert declared(detect, origin, "veri-install", tmp_path, "fast") == fast


@pytest.mark.process("git clone, commit-tree and push to a bare origin")
def test_a_pr_refused_after_the_push_says_to_re_run_and_a_re_run_opens_it_leaving_the_branch_as_pushed(
        tmp_path, run_cli, record, pulls):
    origin, work = project(tmp_path)
    pulls.refusals = 1

    first = run_cli(record, ["make unit", "make test"], cwd=work)
    pushed = git(origin, "rev-parse", "veri-install")
    again = run_cli(record, ["make unit", "make test"], cwd=work)

    assert (first[0], first[1]) == (2, "")
    assert "re-run" in first[2]
    assert again[:2] == (0, URL + "\n"), again[2]
    assert git(origin, "rev-parse", "veri-install") == pushed
    assert [head for head, _, _, _ in pulls] == ["veri-install"]


@pytest.mark.process("git clone, commit-tree and push to a bare origin")
def test_a_re_run_with_the_pr_already_open_from_the_same_commit_is_exit_3(tmp_path, run_cli, record, pulls):
    origin, work = project(tmp_path)
    run_cli(record, ["make unit", "make test"], cwd=work)

    code, out, err = run_cli(record, ["make unit", "make test"], cwd=work)

    assert (code, out, len(pulls)) == (3, "", 1)


@pytest.mark.process("git clone, ls-remote and push to a bare origin")
def test_an_origin_veri_install_holding_other_commands_is_exit_2_saying_to_open_its_pr_or_delete_it(
        tmp_path, run_cli, record, pulls):
    origin, work = project(tmp_path)
    run_cli(record, ["make unit", "make test"], cwd=work)
    del pulls[:]

    code, out, err = run_cli(record, ["make unit", "make all"], cwd=work)

    assert (code, out, pulls) == (2, "", [])
    assert "open a pull request from it" in err and "delete" in err and "re-run" in err


@pytest.mark.process("git clone and fetch from a bare origin")
def test_a_claude_md_that_is_a_symlink_is_exit_2_not_a_regular_file_with_nothing_pushed(tmp_path, run_cli, record, pulls):
    seed = new_repo(tmp_path / "seed")
    (seed / "AGENTS.md").write_text("# Agents\n")
    (seed / "CLAUDE.md").symlink_to("AGENTS.md")
    commit_all(seed, "initial")
    origin, work = tmp_path / "origin.git", tmp_path / "work"
    git(tmp_path, "clone", "-q", "--bare", str(seed), str(origin))
    git(tmp_path, "clone", "-q", str(origin), str(work))

    code, out, err = run_cli(record, ["make unit", "make test"], cwd=work)

    assert (code, out, branches(origin), pulls) == (2, "", ["refs/heads/main"], [])
    assert "CLAUDE.md is not a regular file" in err


@pytest.mark.process("git clone, commit-tree and push to a bare origin")
def test_the_pr_body_names_the_one_test_file_line_only_when_one_file_adds_it(tmp_path, run_cli, record, pulls):
    _, with_one = project(tmp_path / "with")
    _, without = project(tmp_path / "without")

    run_cli(record, ["--one-file", 'pytest -q "$1"', "make unit", "make test"], cwd=with_one)
    run_cli(record, ["make unit", "make test"], cwd=without)

    assert ["veri: one test file:" in body for _, _, _, body in pulls] == [True, False]
