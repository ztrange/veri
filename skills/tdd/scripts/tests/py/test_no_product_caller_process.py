"""Cases for no-product-caller.sh that start the real entry point against a real git repository."""
import subprocess

import pytest

from conftest import SCRIPTS

CHECK = SCRIPTS / "no-product-caller.sh"
HOOKS = "docs/hooks"


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), "-c", "user.name=veri", "-c", "user.email=veri@example.test", *args],
                          capture_output=True, text=True, check=True).stdout.strip()


def put(repo, path, content):
    target = repo / path
    target.parent.mkdir(parents=True, exist_ok=True)
    mode = "wb" if isinstance(content, bytes) else "w"
    with open(target, mode) as handle:
        handle.write(content)


def repo_with(tmp_path, files, commit=True):
    git(tmp_path, "init", "-q", "-b", "main")
    for path, content in files.items():
        put(tmp_path, path, content)
    if commit:
        git(tmp_path, "add", "-A")
        git(tmp_path, "commit", "-q", "-m", "feat: files")
    return tmp_path


def check(repo, name):
    ran = subprocess.run([str(CHECK), name], cwd=repo, capture_output=True, text=True)
    return ran.returncode, ran.stdout + ran.stderr


@pytest.mark.process("no-product-caller.sh run against a real git repository")
def test_no_product_caller_a_skill_md_line_names_the_sh_exit_1_printing_skill_md_line_5(tmp_path):
    repo = repo_with(tmp_path, {"skills/tdd/SKILL.md": "# tdd\n\nRun:\n\n    scripts/old-thing.sh <base-sha>\n"})

    code, out = check(repo, "old-thing.sh")

    assert code == 1
    assert "skills/tdd/SKILL.md:5" in out


@pytest.mark.process("no-product-caller.sh run against a real git repository")
def test_no_product_caller_a_line_in_the_other_product_files_exit_1_printing_each_file_line(tmp_path):
    repo = repo_with(tmp_path, {
        "skills/tdd/SKILL.md": "# tdd\n",
        "skills/tdd-fix/SKILL.md": "# tdd-fix\n\n    scripts/old-thing.sh\n",
        "skills/tdd-candidates/SKILL.md": "# tdd-candidates\nscripts/old-thing.sh\n",
        "Makefile": "test:\n\t@true\nold:\n\tscripts/old-thing.sh\n",
        f"{HOOKS}/reference-transaction": '#!/bin/sh\nscripts/old-thing.sh "$@"\n',
        "skills/tdd/scripts/veri/caller.py": 'import sys\n\n\nCALL = "old-thing.sh"\n',
    })

    code, out = check(repo, "old-thing.sh")

    assert code == 1
    for hit in ("skills/tdd-fix/SKILL.md:3", "skills/tdd-candidates/SKILL.md:2", "Makefile:4",
                f"{HOOKS}/reference-transaction:2", "skills/tdd/scripts/veri/caller.py:4"):
        assert hit in out


@pytest.mark.process("no-product-caller.sh run against a real git repository")
def test_no_product_caller_a_non_utf8_file_under_veri_exit_1_printing_its_file_line(tmp_path):
    repo = repo_with(tmp_path, {
        "skills/tdd/SKILL.md": "# tdd\n",
        "skills/tdd/scripts/veri/caller.dat": b"\xff\xfe\nold-thing.sh\n",
    }, commit=False)

    code, out = check(repo, "old-thing.sh")

    assert code == 1
    assert "skills/tdd/scripts/veri/caller.dat:2" in out


@pytest.mark.process("no-product-caller.sh run against a real git repository")
def test_no_product_caller_a_line_only_under_a_tests_directory_exit_0_printing_nothing(tmp_path):
    repo = repo_with(tmp_path, {
        "skills/tdd/SKILL.md": "# tdd\n",
        f"{HOOKS}/tests/reference-transaction.test.sh": '#!/bin/sh\nscripts/old-thing.sh "$@"\n',
        "skills/tdd/scripts/veri/tests/test_caller.py": 'import sys\n\n\nCALL = "old-thing.sh"\n',
    })

    assert check(repo, "old-thing.sh") == (0, "")


@pytest.mark.process("no-product-caller.sh run against a real git repository")
def test_no_product_caller_no_product_file_line_names_the_sh_exit_0_printing_nothing(tmp_path):
    repo = repo_with(tmp_path, {
        "skills/tdd/SKILL.md": "# tdd\n\n    scripts/new-thing.sh <base-sha>\n",
        "skills/tdd-fix/SKILL.md": "# tdd-fix\n\n    scripts/new-thing.sh\n",
        "skills/tdd-candidates/SKILL.md": "# tdd-candidates\nscripts/new-thing.sh\n",
        "Makefile": "test:\n\t@true\nnew:\n\tscripts/new-thing.sh\n",
        f"{HOOKS}/reference-transaction": '#!/bin/sh\nscripts/new-thing.sh "$@"\n',
        "skills/tdd/scripts/veri/caller.py": 'import sys\n\n\nCALL = "new-thing.sh"\n',
    })

    assert check(repo, "old-thing.sh") == (0, "")


@pytest.mark.process("no-product-caller.sh run against a real git repository")
def test_no_product_caller_module_function_named_by_a_product_line_exit_1_never_its_own_def(tmp_path):
    repo = repo_with(tmp_path, {
        "skills/tdd/SKILL.md": "# tdd\n",
        "skills/tdd/scripts/veri/old_mod.py": "import sys\n\n\ndef old_func(argv):\n    return 0\n",
        "skills/tdd/scripts/veri/caller.py": "import old_mod\n\n\ndef main(argv):\n    return old_mod.old_func(argv)\n",
    })

    code, out = check(repo, "old_mod.old_func")

    assert code == 1
    assert "skills/tdd/scripts/veri/caller.py:5" in out
    assert "skills/tdd/scripts/veri/old_mod.py" not in out


@pytest.mark.process("no-product-caller.sh run against a real git repository")
def test_no_product_caller_sh_named_in_its_own_module_and_another_file_prints_only_the_other(tmp_path):
    repo = repo_with(tmp_path, {
        "skills/tdd/SKILL.md": "# tdd\n",
        "skills/tdd/scripts/veri/old_thing.py": '"""old-thing.sh, run in-process."""\nimport sys\n\nUSAGE = "usage: old-thing.sh <base-sha>"\n',
        "skills/tdd/scripts/veri/caller.py": 'import sys\n\n\nCALL = "old-thing.sh"\n',
    })

    code, out = check(repo, "old-thing.sh")

    assert code == 1
    assert "skills/tdd/scripts/veri/caller.py:4" in out
    assert "skills/tdd/scripts/veri/old_thing.py" not in out


@pytest.mark.process("no-product-caller.sh run against a real git repository")
def test_no_product_caller_sh_named_only_by_pycache_and_pyc_files_exit_0_printing_nothing(tmp_path):
    repo = repo_with(tmp_path, {
        "skills/tdd/SKILL.md": "# tdd\n",
        "skills/tdd/scripts/veri/__pycache__/caller.cpython-312.pyc": b"\xff\xfe\nold-thing.sh\n",
        "skills/tdd/scripts/veri/stale.pyc": b"\xff\xfe\nold-thing.sh\n",
        "skills/tdd/scripts/veri/__pycache__/caller.txt": "old-thing.sh\n",
    }, commit=False)

    assert check(repo, "old-thing.sh") == (0, "")
