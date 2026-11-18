"""Process-starting cases split from unit/test_affected_suites.py, which holds the small cases of the same module."""
import importlib
import os
import subprocess

import pytest

from conftest import ROOT, SCRIPTS
from repo_builder import commit_all, git, new_repo


@pytest.fixture
def affected():
    return importlib.import_module("veri.affected_suites")


def _install(fake_processes, fake_run):
    """Answers every git call through <fake_run>(args, **kwargs), which returns a CompletedProcess, and records it; the
    base commit is veri's own tree (`git cat-file -t <base>:skills/tdd/scripts/tests/py` is `tree`) when the working
    directory holds that directory, as the commit the case's tree stands for would."""
    def answer(line, **kwargs):
        args = fake.argvs[-1]
        if list(args[:3]) == ["git", "cat-file", "-t"]:
            own = args[3].endswith(":skills/tdd/scripts/tests/py") and os.path.isdir("skills/tdd/scripts/tests/py")
            return (0, b"tree\n", b"") if own else (128, b"", b"fatal: not a valid object name\n")
        done = fake_run(args, **kwargs)
        return done.returncode, done.stdout, done.stderr

    fake = fake_processes.answers({"git": answer})
    return fake


SCRIPTS_REL = "skills/tdd/scripts/"
SUITES = SCRIPTS_REL + "tests/"


def cli_git(touched, unresolvable=None, counted=()):
    def run(args, **kwargs):
        if list(args[:2]) == ["git", "rev-parse"]:
            bad = unresolvable is not None and unresolvable in args[-1]
            return subprocess.CompletedProcess(args, 1 if bad else 0, "" if bad else "abc\n", "")
        if list(args[:3]) == ["git", "diff", "--name-only"] and "--diff-filter=AD" in args:
            return subprocess.CompletedProcess(args, 0, "".join(f + "\n" for f in counted), "")
        if list(args[:3]) == ["git", "diff", "--name-only"]:
            return subprocess.CompletedProcess(args, 0, "".join(f + "\n" for f in touched), "")
        if list(args[:3]) == ["git", "diff", "-U0"]:
            return subprocess.CompletedProcess(args, 1, "", "")
        raise AssertionError("unexpected command: %r" % (args,))
    return run


def plant(root, files):
    for name, text in files.items():
        (root / name).parent.mkdir(parents=True, exist_ok=True)
        (root / name).write_text(text)


def pytest_plants(*names):
    return {SCRIPTS_REL + "tests/py/test_%s.py" % n: "def test_x(): pass\n" for n in names}


def pytest_paths(*names):
    return "".join(SUITES + "py/test_%s.py\n" % n for n in names)


@pytest.mark.process("a real sh shim run through a symlink to the skill directory, over real git")
def test_the_shim_run_through_a_symlink_to_the_skill_directory_answers_as_it_does_in_place(tmp_path):
    repo = new_repo(tmp_path / "repo")
    plant(repo, {SCRIPTS_REL + "tests/py/test_status.py": "def test_main(): pass\n"})
    base = commit_all(repo, "base")
    plant(repo, {SCRIPTS_REL + "tests/py/test_status.py": "def test_main(): assert False\n"})
    head = commit_all(repo, "head")
    link = tmp_path / "linked-skill"
    link.symlink_to(SCRIPTS.parent)

    def answer(shim):
        done = subprocess.run(["/bin/sh", str(shim), base + ".." + head], cwd=repo,
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        return done.returncode, done.stdout

    assert answer(link / "scripts/affected-suites.sh") == answer(SCRIPTS / "affected-suites.sh") == (
        0, SUITES + "py/test_status.py\n")


@pytest.mark.process("real git: the changed lines come from git diff -U0 between two commits")
@pytest.mark.parametrize("path", ["CLAUDE.md", "Makefile", "skills/merge/SKILL.md"])
def test_an_edit_inside_one_section_of_claude_md_makefile_or_a_skill_md_other_than_tdds_is_not_section_scoped(
        run_cli, affected, tmp_path, path):
    text = "# doc\n\n## Alpha\n\nalpha text%s\n\n## Beta\n\nbeta text\n"
    repo = new_repo(tmp_path)
    py = SCRIPTS_REL + "tests/py/unit/"
    plant(repo, {path: text % "",
                 py + "test_section_reader.py": 'def test_a():\n    section(doc, "## Alpha")\n',
                 py + "test_whole_reader.py": 'def test_a():\n    open("skills/tdd/SKILL.md").read()\n'})
    base = commit_all(repo, "base")
    plant(repo, {path: text % " 2"})
    commit_all(repo, "head")
    assert run_cli(affected, [base + "..HEAD"], cwd=repo) == (3, "", "")


def topic_range(run_cli, affected, repo):
    return run_cli(affected, ["main..HEAD"], cwd=repo)


@pytest.mark.process("real git: the merge base of main and topic decides which side a file belongs to")
def test_1138_a_suite_the_base_gained_after_the_branch_point_is_not_printed_only_the_branchs_own(
        run_cli, affected, tmp_path):
    repo = new_repo(tmp_path)
    plant(repo, {SCRIPTS_REL + "tests/py/test_a.py": "# a suite\n"})
    commit_all(repo, "base")
    git(repo, "checkout", "-q", "-b", "topic")
    plant(repo, {SCRIPTS_REL + "tests/py/test_a.py": "# a suite 2\n"})
    commit_all(repo, "head")
    git(repo, "checkout", "-q", "main")
    plant(repo, {SCRIPTS_REL + "tests/py/test_b.py": "# b suite\n"})
    commit_all(repo, "main gains a suite")
    git(repo, "checkout", "-q", "topic")
    assert topic_range(run_cli, affected, repo) == (0, SUITES + "py/test_a.py\n", "")


@pytest.mark.tree_audit("copies the real test_skill_*.py readers into a scratch tree")
def test_a_one_section_edit_to_the_real_skill_md_selects_the_pytest_files_that_read_that_section_2980(
        monkeypatch, capsys, affected, tmp_path, fake_processes):
    base = cli_git(["skills/tdd/SKILL.md"])
    skill_lines = (ROOT / "skills/tdd/SKILL.md").read_text().splitlines()
    in_draft_pr = skill_lines.index("### 4. Draft PR") + 3

    def run(args, **kwargs):
        if list(args[:3]) == ["git", "diff", "-U0"]:
            return subprocess.CompletedProcess(
                args, 0, "@@ -%d +%d @@\n-old\n+new\n" % (in_draft_pr, in_draft_pr), "")
        return base(args, **kwargs)

    _install(fake_processes, run)
    prefix = "skills/tdd/scripts/tests/py/"
    for name in ["skills/tdd/SKILL.md"] + [
            str(f.relative_to(ROOT)) for f in (ROOT / prefix).rglob("test_skill_*.py")]:
        plant(tmp_path, {name: (ROOT / name).read_text()})
    monkeypatch.chdir(tmp_path)
    code = affected.main(["base..head"])
    selected = capsys.readouterr().out.split()
    assert code == 0
    assert prefix + "unit/test_skill_draft_pr.py" in selected
    assert prefix + "unit/test_skill_sections.py" not in selected


@pytest.mark.process("real git: the merge base of main and topic decides which side a file belongs to")
def test_1138_a_non_suite_file_the_base_changed_or_deleted_after_the_branch_point_contributes_no_suite(
        run_cli, affected, tmp_path):
    repo = new_repo(tmp_path)
    plant(repo, {SCRIPTS_REL + "foo.sh": "foo\n", SCRIPTS_REL + "bar.sh": "bar\n",
                 SCRIPTS_REL + "prompts/p.md": "a prompt\n",
                 **pytest_plants("foo", "bar"), SUITES + "py/unit/test_build_develop_prompt.py": "# renders\n"})
    commit_all(repo, "base")
    git(repo, "checkout", "-q", "-b", "topic")
    plant(repo, {SCRIPTS_REL + "foo.sh": "foo 2\n"})
    commit_all(repo, "head")
    git(repo, "checkout", "-q", "main")
    plant(repo, {SCRIPTS_REL + "bar.sh": "bar 2\n"})
    (repo / SCRIPTS_REL / "prompts/p.md").unlink()
    commit_all(repo, "main changes a script and deletes a prompt")
    git(repo, "checkout", "-q", "topic")
    assert topic_range(run_cli, affected, repo) == (0, pytest_paths("foo"), "")
