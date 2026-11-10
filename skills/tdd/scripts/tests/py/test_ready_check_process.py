"""Cases for ready-check.sh that start the real entry point."""
import os
import shutil
import re
import subprocess

import pytest

from conftest import SCRIPTS


@pytest.mark.process("ready-check.sh, a /bin/sh shim over veri/ready_check.py, run as a subprocess outside a git repository")
def test_issue_3055_ready_check_outside_a_git_repository_exits_2_with_a_usage_line_and_make_declares_its_caller(tmp_path):
    elsewhere = tmp_path / "not-a-repo"
    elsewhere.mkdir()
    env = {**os.environ, "GIT_CEILING_DIRECTORIES": str(tmp_path)}
    ran = subprocess.run([str(SCRIPTS / "ready-check.sh")], cwd=elsewhere, capture_output=True, text=True, env=env)
    makefile = (SCRIPTS.parent.parent.parent / "Makefile").read_text()

    assert ran.returncode == 2, (ran.returncode, ran.stdout, ran.stderr)
    assert "ready-check" in ran.stderr and "usage" in ran.stderr.lower()
    assert re.search(r"^ready-check:", makefile, re.M)


@pytest.mark.process("ready-check.sh, a /bin/sh shim over veri/ready_check.py, run as a subprocess inside a git repository")
def test_issue_3055_ready_check_with_two_positionals_or_an_unknown_option_exits_2_with_its_usage_line_and_no_stdout(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True, capture_output=True)
    for argv in (["one", "two"], ["--no-such-option"]):
        ran = subprocess.run([str(SCRIPTS / "ready-check.sh"), *argv], cwd=repo, capture_output=True, text=True)

        assert ran.returncode == 2, (argv, ran.returncode, ran.stdout, ran.stderr)
        assert "usage: ready-check.sh [repo-root]" in ran.stderr, (argv, ran.stderr)
        assert ran.stdout == "", (argv, ran.stdout)


def _git(repo, *argv):
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *argv], cwd=repo, check=True, capture_output=True)


def build_ready_repo(tmp_path):
    """A repo where every ready-check row holds, and an env whose PATH leads to a permissive gh stub."""
    repo = tmp_path / "ready-repo"
    (repo / ".github" / "workflows").mkdir(parents=True)
    (repo / "tests").mkdir()
    (repo / "CLAUDE.md").write_text("veri: fast tests: `make unit`\nveri: all tests: `make test`\n")
    (repo / ".gitignore").write_text(".tdd/\n")
    (repo / ".github" / "workflows" / "ci.yml").write_text(
        "name: ci\non:\n  pull_request:\n  push:\n    branches: [main]\njobs:\n  t:\n    runs-on: ubuntu-latest\n    steps:\n      - run: make test\n")
    (repo / "tests" / "test_one.py").write_text("def test_one():\n    assert True\n")
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=repo, check=True, capture_output=True)
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "init")
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    gh = bin_dir / "gh"
    gh.write_text('#!/bin/sh\ncase "$*" in\n  "auth status"*) exit 0 ;;\n  *label*) echo \'[{"name":"veri"}]\' ;;\n  *) echo \'{"permissions":{"push":true,"admin":true}}\' ;;\nesac\n')
    gh.chmod(0o755)
    env = {**os.environ, "PATH": f"{bin_dir}:{os.environ['PATH']}", "VERI_LABEL": "veri"}
    return repo, env


@pytest.mark.process("ready-check.sh, a /bin/sh shim over veri/ready_check.py, run as a subprocess inside a repository where every row holds")
def test_issue_3055_ready_check_exits_0_with_ready_as_its_last_line_where_every_row_holds(tmp_path):
    repo, env = build_ready_repo(tmp_path)
    ran = subprocess.run([str(SCRIPTS / "ready-check.sh")], cwd=repo, capture_output=True, text=True, env=env)
    lines = ran.stdout.splitlines()

    assert ran.returncode == 0, (ran.returncode, ran.stdout, ran.stderr)
    assert lines and lines[-1] == "ready", (ran.stdout, ran.stderr)


@pytest.mark.process("ready-check.sh, a /bin/sh shim over veri/ready_check.py, run as a subprocess inside a repository whose fast tier resolves to nothing")
def test_issue_3055_ready_check_with_no_fast_tier_exits_1_with_a_fail_row_naming_the_claude_md_line_to_add(tmp_path):
    repo, env = build_ready_repo(tmp_path)
    (repo / "CLAUDE.md").write_text("veri: all tests: `make test`\n")
    _git(repo, "mv", "tests/test_one.py", "tests/one_test.py")
    _git(repo, "commit", "-q", "-am", "drop the fast tier line")
    resolved = subprocess.run([str(SCRIPTS / "detect-test-command.sh"), "--tier", "fast"], cwd=repo, capture_output=True, text=True, env=env)
    ran = subprocess.run([str(SCRIPTS / "ready-check.sh")], cwd=repo, capture_output=True, text=True, env=env)
    lines = ran.stdout.splitlines()

    assert resolved.returncode == 3, (resolved.returncode, resolved.stdout, resolved.stderr)
    assert ran.returncode == 1, (ran.returncode, ran.stdout, ran.stderr)
    assert any(l.startswith("fail") and "veri: fast tests:" in l for l in lines), (ran.stdout, ran.stderr)
    assert lines and lines[-1] == "not ready — 1 rows to fix", (ran.stdout, ran.stderr)


@pytest.mark.process("ready-check.sh, a /bin/sh shim over veri/ready_check.py, run as a subprocess inside a repository whose full tier resolves to nothing")
def test_issue_3055_ready_check_with_no_full_tier_exits_1_with_a_fail_row_naming_the_claude_md_line_to_add(tmp_path):
    repo, env = build_ready_repo(tmp_path)
    (repo / "CLAUDE.md").write_text("veri: fast tests: `make unit`\n")
    _git(repo, "mv", "tests/test_one.py", "tests/one_test.py")
    _git(repo, "commit", "-q", "-am", "drop the full tier line")
    resolved = subprocess.run([str(SCRIPTS / "detect-test-command.sh"), "--tier", "all"], cwd=repo, capture_output=True, text=True, env=env)
    ran = subprocess.run([str(SCRIPTS / "ready-check.sh")], cwd=repo, capture_output=True, text=True, env=env)
    lines = ran.stdout.splitlines()

    assert resolved.returncode == 3, (resolved.returncode, resolved.stdout, resolved.stderr)
    assert ran.returncode == 1, (ran.returncode, ran.stdout, ran.stderr)
    assert any(l.startswith("fail") and "veri: all tests:" in l for l in lines), (ran.stdout, ran.stderr)
    assert lines and lines[-1] == "not ready — 1 rows to fix", (ran.stdout, ran.stderr)


@pytest.mark.process("ready-check.sh, a /bin/sh shim over veri/ready_check.py, run as a subprocess inside a repository where no workflow triggers on pull_request")
def test_issue_3055_ready_check_with_no_pull_request_workflow_exits_1_with_a_fail_row_naming_its_fix(tmp_path):
    repo, env = build_ready_repo(tmp_path)
    env.pop("VERI_CI_ON_PR", None)
    (repo / ".github" / "workflows" / "ci.yml").write_text(
        "name: ci\non:\n  push:\n    branches: [main]\njobs:\n  t:\n    runs-on: ubuntu-latest\n    steps:\n      - run: make test\n")
    _git(repo, "commit", "-q", "-am", "ci on push only")
    ran = subprocess.run([str(SCRIPTS / "ready-check.sh")], cwd=repo, capture_output=True, text=True, env=env)
    lines = ran.stdout.splitlines()

    assert ran.returncode == 1, (ran.returncode, ran.stdout, ran.stderr)
    assert any(l.startswith("fail") and "pull_request" in l for l in lines), (ran.stdout, ran.stderr)
    assert lines and lines[-1] == "not ready — 1 rows to fix", (ran.stdout, ran.stderr)


@pytest.mark.process("ready-check.sh, a /bin/sh shim over veri/ready_check.py, run as a subprocess on a feature branch whose own tree has no pull_request workflow while the default branch's tip has one")
def test_issue_3055_ready_check_reads_the_pull_request_workflow_at_the_default_branch_tip_not_head(tmp_path):
    repo, env = build_ready_repo(tmp_path)
    env.pop("VERI_CI_ON_PR", None)
    _git(repo, "checkout", "-q", "-b", "feature")
    (repo / ".github" / "workflows" / "ci.yml").write_text(
        "name: ci\non:\n  push:\n    branches: [main]\njobs:\n  t:\n    runs-on: ubuntu-latest\n    steps:\n      - run: make test\n")
    _git(repo, "commit", "-q", "-am", "feature drops the pull_request trigger")
    ran = subprocess.run([str(SCRIPTS / "ready-check.sh")], cwd=repo, capture_output=True, text=True, env=env)
    lines = ran.stdout.splitlines()

    assert ran.returncode == 0, (ran.returncode, ran.stdout, ran.stderr)
    assert lines and lines[-1] == "ready", (ran.stdout, ran.stderr)


@pytest.mark.process("ready-check.sh, a /bin/sh shim over veri/ready_check.py, run as a subprocess in a repository whose origin/HEAD names a default branch other than main")
def test_issue_3055_ready_check_reads_the_pull_request_workflow_at_the_branch_origin_head_names(tmp_path):
    repo, env = build_ready_repo(tmp_path)
    env.pop("VERI_CI_ON_PR", None)
    _git(repo, "update-ref", "refs/remotes/origin/trunk", "HEAD")
    _git(repo, "symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/trunk")
    (repo / ".github" / "workflows" / "ci.yml").write_text(
        "name: ci\non:\n  push:\n    branches: [main]\njobs:\n  t:\n    runs-on: ubuntu-latest\n    steps:\n      - run: make test\n")
    _git(repo, "commit", "-q", "-am", "main drops the pull_request trigger")
    ran = subprocess.run([str(SCRIPTS / "ready-check.sh")], cwd=repo, capture_output=True, text=True, env=env)
    lines = ran.stdout.splitlines()

    assert ran.returncode == 0, (ran.returncode, ran.stdout, ran.stderr)
    assert lines and lines[-1] == "ready", (ran.stdout, ran.stderr)


@pytest.mark.process("ready-check.sh, a /bin/sh shim over veri/ready_check.py, run as a subprocess from a directory outside the repository it is pointed at")
def test_issue_3055_ready_check_given_a_repo_root_from_outside_it_checks_that_repository(tmp_path):
    repo, env = build_ready_repo(tmp_path)
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    env = {**env, "GIT_CEILING_DIRECTORIES": str(tmp_path)}
    ran = subprocess.run([str(SCRIPTS / "ready-check.sh"), str(repo)], cwd=elsewhere, capture_output=True, text=True, env=env)
    lines = ran.stdout.splitlines()

    assert ran.returncode == 0, (ran.returncode, ran.stdout, ran.stderr)
    assert lines and lines[-1] == "ready", (ran.stdout, ran.stderr)



@pytest.mark.process("ready-check.sh, a /bin/sh shim over veri/ready_check.py, run as a subprocess with no argument from a linked worktree whose tree lacks a row the main working tree holds")
def test_issue_3055_ready_check_with_no_argument_from_a_linked_worktree_checks_the_main_working_tree(tmp_path):
    repo, env = build_ready_repo(tmp_path)
    linked = tmp_path / "linked"
    _git(repo, "worktree", "add", "-q", "-b", "feature", str(linked))
    (linked / "CLAUDE.md").write_text("veri: all tests: `make test`\n")
    _git(linked, "mv", "tests/test_one.py", "tests/one_test.py")
    _git(linked, "commit", "-q", "-am", "drop the fast tier line")
    ran = subprocess.run([str(SCRIPTS / "ready-check.sh")], cwd=linked, capture_output=True, text=True, env=env)
    lines = ran.stdout.splitlines()

    assert ran.returncode == 0, (ran.returncode, ran.stdout, ran.stderr)
    assert lines and lines[-1] == "ready", (ran.stdout, ran.stderr)


@pytest.mark.process("ready-check.sh, a /bin/sh shim over veri/ready_check.py, run as a subprocess in a repository where no workflow triggers on pull_request but VERI_CI_ON_PR is set")
def test_issue_3055_ready_check_with_no_pull_request_workflow_but_veri_ci_on_pr_set_exits_0_with_the_row_ok(tmp_path):
    repo, env = build_ready_repo(tmp_path)
    env["VERI_CI_ON_PR"] = "1"
    (repo / ".github" / "workflows" / "ci.yml").write_text(
        "name: ci\non:\n  push:\n    branches: [main]\njobs:\n  t:\n    runs-on: ubuntu-latest\n    steps:\n      - run: make test\n")
    _git(repo, "commit", "-q", "-am", "ci on push only")
    ran = subprocess.run([str(SCRIPTS / "ready-check.sh")], cwd=repo, capture_output=True, text=True, env=env)
    lines = ran.stdout.splitlines()

    assert not any(l.startswith("fail") and "pull_request" in l for l in lines), (ran.stdout, ran.stderr)
    assert ran.returncode == 0, (ran.returncode, ran.stdout, ran.stderr)
    assert lines and lines[-1] == "ready", (ran.stdout, ran.stderr)


@pytest.mark.process("ready-check.sh, a /bin/sh shim over veri/ready_check.py, run as a subprocess in a repository where no workflow triggers on push to the default branch")
def test_issue_3055_ready_check_with_no_push_workflow_exits_1_with_a_fail_row_naming_its_fix(tmp_path):
    repo, env = build_ready_repo(tmp_path)
    (repo / ".github" / "workflows" / "ci.yml").write_text(
        "name: ci\non:\n  pull_request:\njobs:\n  t:\n    runs-on: ubuntu-latest\n    steps:\n      - run: make test\n")
    _git(repo, "commit", "-q", "-am", "ci on pull_request only")
    ran = subprocess.run([str(SCRIPTS / "ready-check.sh")], cwd=repo, capture_output=True, text=True, env=env)
    lines = ran.stdout.splitlines()

    assert ran.returncode == 1, (ran.returncode, ran.stdout, ran.stderr)
    assert any(l.startswith("fail") and "push" in l for l in lines), (ran.stdout, ran.stderr)
    assert lines and lines[-1] == "not ready — 1 rows to fix", (ran.stdout, ran.stderr)


@pytest.mark.process("ready-check.sh, a /bin/sh shim over veri/ready_check.py, run as a subprocess in a repository where no tracked file is a test file")
def test_issue_3055_ready_check_with_no_tracked_test_file_exits_1_with_a_fail_row_naming_its_fix(tmp_path):
    repo, env = build_ready_repo(tmp_path)
    _git(repo, "mv", "tests/test_one.py", "lib.py")
    _git(repo, "commit", "-q", "-am", "no test file left")
    ran = subprocess.run([str(SCRIPTS / "ready-check.sh")], cwd=repo, capture_output=True, text=True, env=env)
    lines = ran.stdout.splitlines()

    assert ran.returncode == 1, (ran.returncode, ran.stdout, ran.stderr)
    assert any(l.startswith("fail") and "test file" in l for l in lines), (ran.stdout, ran.stderr)
    assert lines and lines[-1] == "not ready — 1 rows to fix", (ran.stdout, ran.stderr)


@pytest.mark.process("ready-check.sh, a /bin/sh shim over veri/ready_check.py, run as a subprocess in a repository where .tdd/ is not ignored")
def test_issue_3055_ready_check_with_tdd_not_ignored_exits_1_with_a_fail_row_naming_its_fix(tmp_path):
    repo, env = build_ready_repo(tmp_path)
    (repo / ".gitignore").write_text("*.pyc\n")
    _git(repo, "commit", "-q", "-am", "stop ignoring .tdd")
    ran = subprocess.run([str(SCRIPTS / "ready-check.sh")], cwd=repo, capture_output=True, text=True, env=env)
    lines = ran.stdout.splitlines()

    assert ran.returncode == 1, (ran.returncode, ran.stdout, ran.stderr)
    assert any(l.startswith("fail") and ".tdd/" in l for l in lines), (ran.stdout, ran.stderr)
    assert lines and lines[-1] == "not ready — 1 rows to fix", (ran.stdout, ran.stderr)


@pytest.mark.process("ready-check.sh, a /bin/sh shim over veri/ready_check.py, run as a subprocess where gh auth status exits non-zero")
def test_issue_3055_ready_check_with_gh_not_authenticated_exits_1_with_a_fail_row_naming_its_fix(tmp_path):
    repo, env = build_ready_repo(tmp_path)
    gh = tmp_path / "bin" / "gh"
    gh.write_text('#!/bin/sh\ncase "$*" in\n  "auth status"*) exit 1 ;;\n  *label*) echo \'[{"name":"veri"}]\' ;;\n  *) echo \'{"permissions":{"push":true,"admin":true}}\' ;;\nesac\n')
    ran = subprocess.run([str(SCRIPTS / "ready-check.sh")], cwd=repo, capture_output=True, text=True, env=env)
    lines = ran.stdout.splitlines()

    assert ran.returncode == 1, (ran.returncode, ran.stdout, ran.stderr)
    assert any(l.startswith("fail") and "gh auth login" in l for l in lines), (ran.stdout, ran.stderr)
    assert lines and lines[-1] == "not ready — 1 rows to fix", (ran.stdout, ran.stderr)


@pytest.mark.process("ready-check.sh, a /bin/sh shim over veri/ready_check.py, run as a subprocess where the gh account lacks push access")
def test_issue_3055_ready_check_with_no_push_access_exits_1_with_a_fail_row_naming_its_fix(tmp_path):
    repo, env = build_ready_repo(tmp_path)
    gh = tmp_path / "bin" / "gh"
    gh.write_text('#!/bin/sh\ncase "$*" in\n  "auth status"*) exit 0 ;;\n  *label*) echo \'[{"name":"veri"}]\' ;;\n  *) echo \'{"permissions":{"push":false,"admin":false}}\' ;;\nesac\n')
    ran = subprocess.run([str(SCRIPTS / "ready-check.sh")], cwd=repo, capture_output=True, text=True, env=env)
    lines = ran.stdout.splitlines()

    assert ran.returncode == 1, (ran.returncode, ran.stdout, ran.stderr)
    assert any(l.startswith("fail") and "push access" in l for l in lines), (ran.stdout, ran.stderr)
    assert lines and lines[-1] == "not ready — 1 rows to fix", (ran.stdout, ran.stderr)


@pytest.mark.process("ready-check.sh, a /bin/sh shim over veri/ready_check.py, run as a subprocess where gh's repo API output is unparseable or lacks permissions.push")
def test_issue_3055_ready_check_with_unusable_repo_api_output_fails_the_push_access_row_instead_of_crashing(tmp_path):
    for i, body in enumerate(("not json", "{}", "[]")):
        sub = tmp_path / str(i)
        sub.mkdir()
        repo, env = build_ready_repo(sub)
        gh = sub / "bin" / "gh"
        gh.write_text('#!/bin/sh\ncase "$*" in\n  "auth status"*) exit 0 ;;\n  *label*) echo \'[{"name":"veri"}]\' ;;\n  *) echo \'' + body + '\' ;;\nesac\n')
        ran = subprocess.run([str(SCRIPTS / "ready-check.sh")], cwd=repo, capture_output=True, text=True, env=env)
        lines = ran.stdout.splitlines()

        assert ran.returncode == 1, (body, ran.returncode, ran.stdout, ran.stderr)
        assert any(l.startswith("fail") and "push access" in l for l in lines), (body, ran.stdout, ran.stderr)
        assert lines and lines[-1] == "not ready — 1 rows to fix", (body, ran.stdout, ran.stderr)


@pytest.mark.process("ready-check.sh, a /bin/sh shim over veri/ready_check.py, run as a subprocess inside a repository where every row holds")
def test_issue_3055_ready_check_prints_an_ok_row_for_each_check_that_holds_before_the_last_line(tmp_path):
    repo, env = build_ready_repo(tmp_path)
    ran = subprocess.run([str(SCRIPTS / "ready-check.sh")], cwd=repo, capture_output=True, text=True, env=env)
    rows = ran.stdout.splitlines()[:-1]

    assert any(l.startswith("ok") for l in rows), (ran.stdout, ran.stderr)
    assert all(l.startswith(("ok", "fail")) for l in rows), (ran.stdout, ran.stderr)


@pytest.mark.process("ready-check.sh, a /bin/sh shim over veri/ready_check.py, run as a subprocess where the opt-in label is missing from the repository")
def test_issue_3055_ready_check_with_the_opt_in_label_missing_exits_1_with_a_fail_row_naming_its_fix(tmp_path):
    repo, env = build_ready_repo(tmp_path)
    gh = tmp_path / "bin" / "gh"
    gh.write_text('#!/bin/sh\ncase "$*" in\n  "auth status"*) exit 0 ;;\n  *label*) echo \'[]\' ;;\n  *) echo \'{"permissions":{"push":true,"admin":true}}\' ;;\nesac\n')
    ran = subprocess.run([str(SCRIPTS / "ready-check.sh")], cwd=repo, capture_output=True, text=True, env=env)
    lines = ran.stdout.splitlines()

    assert ran.returncode == 1, (ran.returncode, ran.stdout, ran.stderr)
    assert any(l.startswith("fail") and "label" in l and "veri" in l for l in lines), (ran.stdout, ran.stderr)
    assert lines and lines[-1] == "not ready — 1 rows to fix", (ran.stdout, ran.stderr)


@pytest.mark.process("ready-check.sh, a /bin/sh shim over veri/ready_check.py, run as a subprocess where two rows fail at once")
def test_issue_3055_ready_check_with_two_failing_rows_counts_both_in_its_last_line(tmp_path):
    repo, env = build_ready_repo(tmp_path)
    gh = tmp_path / "bin" / "gh"
    gh.write_text('#!/bin/sh\ncase "$*" in\n  "auth status"*) exit 1 ;;\n  *label*) echo \'[]\' ;;\n  *) echo \'{"permissions":{"push":true,"admin":true}}\' ;;\nesac\n')
    ran = subprocess.run([str(SCRIPTS / "ready-check.sh")], cwd=repo, capture_output=True, text=True, env=env)
    lines = ran.stdout.splitlines()

    assert ran.returncode == 1, (ran.returncode, ran.stdout, ran.stderr)
    assert sum(l.startswith("fail") for l in lines) == 2, (ran.stdout, ran.stderr)
    assert lines and lines[-1] == "not ready — 2 rows to fix", (ran.stdout, ran.stderr)


@pytest.mark.process("ready-check.sh, a /bin/sh shim over veri/ready_check.py, run as a subprocess where gh label list itself fails")
def test_issue_3055_ready_check_with_a_failing_gh_label_list_fails_the_label_row_instead_of_crashing(tmp_path):
    repo, env = build_ready_repo(tmp_path)
    gh = tmp_path / "bin" / "gh"
    gh.write_text('#!/bin/sh\ncase "$*" in\n  "auth status"*) exit 0 ;;\n  *label*) echo \'[{"name":"veri"}]\'; echo "boom" >&2; exit 1 ;;\n  *) echo \'{"permissions":{"push":true,"admin":true}}\' ;;\nesac\n')
    ran = subprocess.run([str(SCRIPTS / "ready-check.sh")], cwd=repo, capture_output=True, text=True, env=env)
    lines = ran.stdout.splitlines()

    assert ran.returncode == 1, (ran.returncode, ran.stdout, ran.stderr)
    assert "Traceback" not in ran.stderr, ran.stderr
    assert any(l.startswith("fail") and "label" in l and "veri" in l for l in lines), (ran.stdout, ran.stderr)
    assert lines and lines[-1] == "not ready — 1 rows to fix", (ran.stdout, ran.stderr)


@pytest.mark.process("ready-check.sh, a /bin/sh shim over veri/ready_check.py, run as a subprocess beside a detect-test-command.sh that exits 2")
@pytest.mark.tree_audit("symlinks every entry of the scripts directory but detect-test-command.sh into a scratch copy")
def test_issue_3055_ready_check_where_detect_test_command_exits_2_fails_the_tier_rows_saying_no_answer_was_obtained(tmp_path):
    repo, env = build_ready_repo(tmp_path)
    fake = tmp_path / "scripts"
    fake.mkdir()
    for entry in SCRIPTS.iterdir():
        if entry.name == "veri":
            shutil.copytree(entry, fake / "veri", ignore=shutil.ignore_patterns("__pycache__"))
        elif entry.name != "detect-test-command.sh":
            (fake / entry.name).symlink_to(entry)
    detect = fake / "detect-test-command.sh"
    detect.write_text("#!/bin/sh\nexit 2\n")
    detect.chmod(0o755)
    ran = subprocess.run([str(fake / "ready-check.sh")], cwd=repo, capture_output=True, text=True, env=env)
    lines = ran.stdout.splitlines()

    assert ran.returncode == 1, (ran.returncode, ran.stdout, ran.stderr)
    for tier in ("fast", "all"):
        assert any(l.startswith("fail") and f"{tier} tier" in l and "no answer was obtained" in l and "exit 2 from detect-test-command.sh" in l for l in lines), (tier, ran.stdout, ran.stderr)
    assert lines and lines[-1] == "not ready — 2 rows to fix", (ran.stdout, ran.stderr)


@pytest.mark.process("ready-check.sh, a /bin/sh shim over veri/ready_check.py, run as a subprocess where preflight's bash check finds a bash older than 5")
def test_issue_3055_ready_check_with_bash_older_than_5_exits_1_with_a_fail_row_naming_its_fix(tmp_path):
    repo, env = build_ready_repo(tmp_path)
    env["VERI_BASH_MAJOR"] = "4"
    ran = subprocess.run([str(SCRIPTS / "ready-check.sh")], cwd=repo, capture_output=True, text=True, env=env)
    lines = ran.stdout.splitlines()

    assert ran.returncode == 1, (ran.returncode, ran.stdout, ran.stderr)
    assert any(l.startswith("fail") and "bash" in l for l in lines), (ran.stdout, ran.stderr)
    assert lines and lines[-1] == "not ready — 1 rows to fix", (ran.stdout, ran.stderr)


@pytest.mark.process("ready-check.sh, a /bin/sh shim over veri/ready_check.py, run as a subprocess where preflight's Python check finds a Python below the floor")
def test_issue_3055_ready_check_with_python_below_the_floor_exits_1_with_a_fail_row_naming_its_fix(tmp_path):
    repo, env = build_ready_repo(tmp_path)
    env["VERI_PYTHON_VERSION"] = "3.8.0"
    ran = subprocess.run([str(SCRIPTS / "ready-check.sh")], cwd=repo, capture_output=True, text=True, env=env)
    lines = ran.stdout.splitlines()

    assert ran.returncode == 1, (ran.returncode, ran.stdout, ran.stderr)
    assert any(l.startswith("fail") and "Python" in l for l in lines), (ran.stdout, ran.stderr)
    assert lines and lines[-1] == "not ready — 1 rows to fix", (ran.stdout, ran.stderr)


def _repo_state(repo):
    def out(*argv):
        return subprocess.run(["git", *argv], cwd=repo, check=True, capture_output=True, text=True).stdout
    files = sorted(str(p.relative_to(repo)) for p in repo.rglob("*") if ".git" not in p.relative_to(repo).parts[:1])
    contents = {f: (repo / f).read_bytes() for f in files if (repo / f).is_file()}
    return {"status": out("status", "--porcelain", "--ignored"), "index": out("ls-files", "-s"),
            "refs": out("for-each-ref"), "head": out("rev-parse", "HEAD"), "files": files, "contents": contents,
            "config": (repo / ".git" / "config").read_bytes()}


@pytest.mark.process("ready-check.sh, a /bin/sh shim over veri/ready_check.py, run as a subprocess with a recording gh stub inside a repository where every row holds")
def test_issue_3055_ready_check_where_every_row_holds_leaves_tree_index_and_refs_unchanged_and_makes_no_writing_gh_call(tmp_path):
    repo, env = build_ready_repo(tmp_path)
    log = tmp_path / "gh.log"
    gh = tmp_path / "bin" / "gh"
    gh.write_text('#!/bin/sh\necho "$*" >> "' + str(log) + '"\ncase "$*" in\n  "auth status"*) exit 0 ;;\n  *label*) echo \'[{"name":"veri"}]\' ;;\n  *) echo \'{"permissions":{"push":true,"admin":true}}\' ;;\nesac\n')
    before = _repo_state(repo)
    ran = subprocess.run([str(SCRIPTS / "ready-check.sh")], cwd=repo, capture_output=True, text=True, env=env)
    after = _repo_state(repo)
    calls = log.read_text().splitlines() if log.exists() else []

    assert ran.returncode == 0, (ran.returncode, ran.stdout, ran.stderr)
    assert calls, "ready-check made no gh call, so the recording stub saw nothing to judge"
    assert after == before
    writes = [c for c in calls if re.search(r"label (create|edit|delete|add|remove)|--method|(^| )-X( |$)|--add-label|--remove-label|(^| )-[fF]( |$)|--(raw-)?field|--input", c)]
    assert writes == [], writes


@pytest.mark.process("ready-check.sh, a /bin/sh shim over veri/ready_check.py, run as a subprocess in a repository whose .gitignore ignores .tdd/* and re-includes the ledger")
def test_issue_3172_ready_check_with_tdd_contents_ignored_and_the_ledger_re_included_exits_0_with_the_tdd_row_ok(tmp_path):
    repo, env = build_ready_repo(tmp_path)
    (repo / ".gitignore").write_text(".tdd/*\n!.tdd/issue-*.md\n.tdd/issue-*-spec.md\n")
    (repo / ".tdd").mkdir()
    (repo / ".tdd" / "issue-1.md").write_text("- [ ] step\n")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "ignore the contents of .tdd, commit the ledger")
    ran = subprocess.run([str(SCRIPTS / "ready-check.sh")], cwd=repo, capture_output=True, text=True, env=env)
    lines = ran.stdout.splitlines()

    assert ran.returncode == 0, (ran.returncode, ran.stdout, ran.stderr)
    assert not any(l.startswith("fail") and ".tdd/" in l for l in lines), (ran.stdout, ran.stderr)
    assert lines and lines[-1] == "ready", (ran.stdout, ran.stderr)


@pytest.mark.process("ready-check.sh, a /bin/sh shim over veri/ready_check.py, run as a subprocess in a repository labelled ready-for-agent with VERI_LABEL unset")
def test_issue_3173_ready_check_with_veri_label_unset_prints_an_ok_label_row_naming_ready_for_agent(tmp_path):
    repo, env = build_ready_repo(tmp_path)
    env.pop("VERI_LABEL")
    gh = tmp_path / "bin" / "gh"
    gh.write_text(gh.read_text().replace('"name":"veri"', '"name":"ready-for-agent"'))
    ran = subprocess.run([str(SCRIPTS / "ready-check.sh")], cwd=repo, capture_output=True, text=True, env=env)
    lines = ran.stdout.splitlines()

    assert "ok    label ready-for-agent" in lines, (ran.returncode, ran.stdout, ran.stderr)


@pytest.mark.process("ready-check.sh, a /bin/sh shim over veri/ready_check.py, run as a subprocess in a repository without the ready-for-agent label and with VERI_LABEL unset")
def test_issue_3173_ready_check_with_veri_label_unset_and_ready_for_agent_missing_prints_a_fail_label_row_naming_it(tmp_path):
    repo, env = build_ready_repo(tmp_path)
    env.pop("VERI_LABEL")
    ran = subprocess.run([str(SCRIPTS / "ready-check.sh")], cwd=repo, capture_output=True, text=True, env=env)
    lines = ran.stdout.splitlines()

    assert ran.returncode == 1, (ran.returncode, ran.stdout, ran.stderr)
    assert any(l.startswith("fail") and "label ready-for-agent" in l and "`ready-for-agent`" in l for l in lines), (ran.stdout, ran.stderr)


@pytest.mark.process("ready-check.sh, a /bin/sh shim over veri/ready_check.py, run as a subprocess with VERI_LABEL set but empty")
def test_issue_3173_ready_check_with_veri_label_set_but_empty_prints_a_fail_label_row_saying_to_name_a_label_or_unset_it(tmp_path):
    repo, env = build_ready_repo(tmp_path)
    env["VERI_LABEL"] = ""
    ran = subprocess.run([str(SCRIPTS / "ready-check.sh")], cwd=repo, capture_output=True, text=True, env=env)
    label_rows = [l for l in ran.stdout.splitlines() if l.startswith("fail") and "label" in l]

    assert label_rows and all("VERI_LABEL" in l and "create the ``" not in l for l in label_rows), (ran.returncode, ran.stdout, ran.stderr)
