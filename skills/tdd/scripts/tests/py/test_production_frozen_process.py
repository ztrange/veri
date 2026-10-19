"""Cases for production-frozen.sh that start the real entry point against a real git repository."""
import subprocess

import pytest

from conftest import SCRIPTS

FROZEN = SCRIPTS / "production-frozen.sh"


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), "-c", "user.name=veri", "-c", "user.email=veri@example.test", *args],
                          capture_output=True, text=True, check=True).stdout.strip()


def commit_all(repo, message):
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", message)


def frozen(repo, base):
    ran = subprocess.run([str(FROZEN), base], cwd=repo, capture_output=True, text=True)
    return ran.returncode, ran.stdout + ran.stderr


@pytest.fixture
def repo(tmp_path):
    root = tmp_path / "frozen"
    root.mkdir()
    git(root, "init", "-q", "-b", "main")
    for name, text in {"src/widget.sh": "widget() { echo 1; }\n", "tests/widget.test.sh": "widget | grep 1\n",
                       "pkg/contests/entry.sh": "entry\n"}.items():
        (root / name).parent.mkdir(parents=True, exist_ok=True)
        (root / name).write_text(text)
    commit_all(root, "feat: widget")
    return root


@pytest.mark.process("production-frozen.sh run against a real git range")
def test_production_frozen_range_production_paths_changed_exit_1_naming_each_and_not_the_test_file(repo):
    base = git(repo, "rev-parse", "HEAD")
    (repo / "tests/widget.test.sh").write_text("widget | grep -F 1\n")
    (repo / "src/widget.sh").write_text('widget() { printf "1\\n"; }\n')
    commit_all(repo, "test: loosen the widget test, and change widget")
    (repo / "pkg/contests/entry.sh").write_text("entry two\n")
    commit_all(repo, "chore: touch entry")

    code, out = frozen(repo, base)

    assert code == 1
    assert "src/widget.sh" in out
    assert "pkg/contests/entry.sh" in out
    assert "tests/widget.test.sh" not in out


@pytest.mark.process("production-frozen.sh run against a real git range")
def test_production_frozen_range_only_test_files_changed_exit_0_printing_no_path(repo):
    base = git(repo, "rev-parse", "HEAD")
    (repo / "lib").mkdir()
    (repo / "tests/widget.test.sh").write_text("widget | grep -Fx 1\n")
    (repo / "lib/entry.test.sh").write_text("entry | grep two\n")
    commit_all(repo, "test: tighten the widget test, and test entry")

    assert frozen(repo, base) == (0, "")


@pytest.mark.process("production-frozen.sh run against a real git range")
def test_production_frozen_range_base_sha_does_not_resolve_to_a_commit_exit_2(repo):
    code, _ = frozen(repo, "0123456789abcdef0123456789abcdef01234567")

    assert code == 2
