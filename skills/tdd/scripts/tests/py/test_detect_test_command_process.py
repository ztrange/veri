"""Process cases for detect-test-command.sh, the shim over veri/detect_test_command.py."""
import os
import subprocess

import pytest

from repo_builder import commit_all, git, new_repo

SHIM = os.path.realpath(os.path.join(os.path.dirname(__file__), "..", "..", "detect-test-command.sh"))


@pytest.mark.process("detect-test-command.sh started through a symlink to the skill directory, from another working directory")
def test_shim_run_through_a_symlink_and_from_another_directory_prints_the_same_command_and_exit_code_as_in_place(tmp_path):
    repo = tmp_path / "linked-repo"
    repo.mkdir()
    (repo / "Makefile").write_text("test:\n\techo hi\n")
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    skill = os.path.dirname(os.path.dirname(SHIM))
    os.symlink(skill, str(tmp_path / "linked-skill"))
    linked_shim = str(tmp_path / "linked-skill" / "scripts" / "detect-test-command.sh")

    in_place = subprocess.run([SHIM], capture_output=True, text=True, cwd=str(repo))
    linked = subprocess.run([linked_shim, str(repo)], capture_output=True, text=True, cwd=str(elsewhere))

    assert (in_place.returncode, in_place.stdout, in_place.stderr) == (0, "make test\n", "")
    assert (linked.returncode, linked.stdout, linked.stderr) == (0, "make test\n", "")


@pytest.mark.process("detect-test-command.sh --tier lint run through its shim, in a repo with and without a veri: lint: line")
def test_shim_tier_lint_prints_the_declared_lint_command_and_exits_3_printing_nothing_without_one_4122(tmp_path):
    declared, undeclared = tmp_path / "declared", tmp_path / "undeclared"
    for repo in (declared, undeclared):
        repo.mkdir()
        (repo / "Makefile").write_text("test:\n\ttrue\nlint:\n\ttrue\n")
    (declared / "CLAUDE.md").write_text("veri: lint: `make lint`\n")
    (undeclared / "CLAUDE.md").write_text("veri: all tests: `make test`\n")

    runs = {repo.name: subprocess.run([SHIM, "--tier", "lint", str(repo)], capture_output=True, text=True,
                                      stdin=subprocess.DEVNULL)
            for repo in (declared, undeclared)}

    assert {name: (run.returncode, run.stdout, run.stderr) for name, run in runs.items()} == {
        "declared": (0, "make lint\n", ""), "undeclared": (3, "", "")}


@pytest.mark.process("git init, commit and checkout run for real in a scratch repository, then detect-test-command.sh in it")
def test_at_a_commit_every_tier_is_decided_from_that_commits_files_never_the_working_trees_4263(tmp_path):
    repo = new_repo(tmp_path / "repo")
    inferred = commit_all(repo, "a Makefile only", **{"Makefile": "test:\n\ttrue\n", "tests__test_x.py": ""})
    declared = commit_all(repo, "a fast line", **{"CLAUDE.md": "veri: fast tests: pytest -q\n"})
    git(repo, "checkout", "-q", "-b", "feature")
    commit_all(repo, "the branch's own lines", **{"CLAUDE.md": "veri: fast tests: true\nveri: all tests: true\n",
                                                   "package.json": '{"scripts": {"test": "true"}}'})
    (repo / "Makefile").unlink()

    def detect(*args):
        done = subprocess.run([SHIM, *args, str(repo)], capture_output=True, text=True, cwd=repo)
        return done.returncode, done.stdout, done.stderr.count("\n")

    assert [detect("--tier", "fast", "--at", inferred), detect("--tier", "all", "--at", declared),
            detect("--tier", "fast", "--at", declared), detect("--tier", "fast", "--at", "0" * 40),
            detect("--tier", "fast", "--at", "")] == [
        (0, "make test\n", 0), (0, "make test\n", 0), (0, "pytest -q\n", 0), (2, "", 1), (2, "", 1)]


@pytest.mark.process("git init and commit run for real in a scratch repository, then detect-test-command.sh in it")
def test_at_a_commit_a_tests_directory_of_test_files_infers_unittest_only_when_that_commit_holds_one_4263(tmp_path):
    repo = new_repo(tmp_path / "repo")
    bare = commit_all(repo, "a readme", **{"README": "x\n", "tests__helper.py": "", "tests__test_dir.py__x": ""})
    held = commit_all(repo, "a test file", **{"tests__test_x.py": ""})
    (repo / "tests" / "test_x.py").unlink()

    def detect(commit):
        done = subprocess.run([SHIM, "--tier", "fast", "--at", commit, str(repo)], capture_output=True, text=True)
        return done.returncode, done.stdout

    assert [detect(bare), detect(held)] == [(3, ""), (0, "python3 -m unittest discover -q\n")]


@pytest.mark.process("git init, commit and rm run for real in a scratch repository, then detect-test-command.sh in it")
def test_at_a_commit_each_file_the_fast_tier_infers_from_is_read_from_that_commit_4263(tmp_path):
    repo = new_repo(tmp_path / "repo")
    holds = [({"CLAUDE.md": "veri: fast tests: pytest -q\n"}, "pytest -q"),
             ({"package.json": '{"scripts": {"test": "jest"}}'}, "npm test"),
             ({"package.json": '{"scripts": {"test": "jest"}}', "pnpm-lock.yaml": ""}, "pnpm test"),
             ({"package.json": '{"scripts": {"test": "jest"}}', "yarn.lock": ""}, "yarn test"),
             ({"Makefile": "test:\n\ttrue\n"}, "make test"), ({"pytest.ini": ""}, "pytest -q"),
             ({"pyproject.toml": "[tool.pytest.ini_options]\n"}, "pytest -q"),
             ({"setup.cfg": "[tool:pytest]\n"}, "pytest -q"), ({"go.mod": ""}, "go test ./..."),
             ({"Cargo.toml": ""}, "cargo test")]
    commits = []
    for files, _ in holds:
        git(repo, "rm", "-rqf", "--ignore-unmatch", ".")
        commits.append(commit_all(repo, "only " + " ".join(files), allow_empty=True, **files))
    git(repo, "rm", "-rqf", "--ignore-unmatch", ".")

    found = [subprocess.run([SHIM, "--tier", "fast", "--at", c, str(repo)], capture_output=True, text=True).stdout
             for c in commits]

    assert found == [command + "\n" for _, command in holds]
