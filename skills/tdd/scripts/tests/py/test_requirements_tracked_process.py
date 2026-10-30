"""Cases for requirements.tracked, through prose-owed.sh in a real git repository."""
import subprocess
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2]


@pytest.mark.process("prose-owed.sh run as a script in a real git repository")
def test_2702_an_untracked_requirements_md_in_a_subdirectory_is_owed_nothing(tmp_path):
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True, stdin=subprocess.DEVNULL)
    (tmp_path / "skills" / "demo").mkdir(parents=True)
    (tmp_path / "skills" / "demo" / "SKILL.md").write_text("The widget is blue.\n")
    (tmp_path / "scratch").mkdir()
    (tmp_path / "scratch" / "REQUIREMENTS.md").write_text(
        "## skills/demo/SKILL.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n")

    ran = subprocess.run([str(SCRIPTS / "prose-owed.sh"), str(tmp_path)], stdin=subprocess.DEVNULL,
                         capture_output=True, text=True)

    assert (ran.returncode, ran.stdout) == (0, ""), ran.stderr


@pytest.mark.process("prose-owed.sh run as a script in a real git repository")
def test_2702_an_untracked_graded_in_a_subdirectory_orphans_nothing(tmp_path):
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True, stdin=subprocess.DEVNULL)
    (tmp_path / "scratch").mkdir()
    (tmp_path / "scratch" / "GRADED").write_text("skills/gone/SKILL.md %s 2026-01-01 g1\n" % ("0" * 64))

    ran = subprocess.run([str(SCRIPTS / "prose-owed.sh"), str(tmp_path)], stdin=subprocess.DEVNULL,
                         capture_output=True, text=True)

    assert (ran.returncode, ran.stdout) == (0, ""), ran.stderr


@pytest.mark.process("prose-owed.sh run as a script in a real git repository")
def test_2702_a_requirements_md_under_a_git_ignored_node_modules_is_owed_nothing(tmp_path):
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True, stdin=subprocess.DEVNULL)
    (tmp_path / ".gitignore").write_text("node_modules/\n")
    (tmp_path / "skills" / "demo").mkdir(parents=True)
    (tmp_path / "skills" / "demo" / "SKILL.md").write_text("The widget is blue.\n")
    (tmp_path / "node_modules" / "pkg").mkdir(parents=True)
    (tmp_path / "node_modules" / "pkg" / "REQUIREMENTS.md").write_text(
        "## skills/demo/SKILL.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n")

    ran = subprocess.run([str(SCRIPTS / "prose-owed.sh"), str(tmp_path)], stdin=subprocess.DEVNULL,
                         capture_output=True, text=True)

    assert (ran.returncode, ran.stdout) == (0, ""), ran.stderr


@pytest.mark.process("prose-owed.sh run as a script in a real git repository")
def test_2702_tracked_requirements_md_at_the_root_under_docs_adr_and_three_levels_deep_are_all_listed(tmp_path):
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True, stdin=subprocess.DEVNULL)
    lists = {"REQUIREMENTS.md": "skills/root/SKILL.md", "docs/adr/REQUIREMENTS.md": "skills/adr/SKILL.md",
             "a/b/c/REQUIREMENTS.md": "skills/deep/SKILL.md"}
    for list_path, unit in lists.items():
        (tmp_path / unit).parent.mkdir(parents=True)
        (tmp_path / unit).write_text("The widget is blue.\n")
        (tmp_path / list_path).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / list_path).write_text(
            "## %s\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n" % unit)
    subprocess.run(["git", "add", "-A"], cwd=tmp_path, check=True, stdin=subprocess.DEVNULL)

    ran = subprocess.run([str(SCRIPTS / "prose-owed.sh"), str(tmp_path)], stdin=subprocess.DEVNULL,
                         capture_output=True, text=True)

    assert (ran.returncode, sorted(ran.stdout.split())) == (1, sorted(lists.values())), ran.stderr


@pytest.mark.process("prose-owed.sh run as a script in a real git repository")
def test_2702_a_git_ls_files_failure_in_a_corrupt_index_exits_2_rather_than_an_empty_list(tmp_path):
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True, stdin=subprocess.DEVNULL)
    (tmp_path / "REQUIREMENTS.md").write_text("## skills/demo/SKILL.md\n")
    (tmp_path / ".git" / "index").write_bytes(b"not an index\n")

    ran = subprocess.run([str(SCRIPTS / "prose-owed.sh"), str(tmp_path)], stdin=subprocess.DEVNULL,
                         capture_output=True, text=True)

    assert (ran.returncode, ran.stdout) == (2, ""), ran.stderr
