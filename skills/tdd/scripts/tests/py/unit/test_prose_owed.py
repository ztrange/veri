"""prose_owed.main, called in-process through run_cli as `prose-owed.sh <repo-root>`."""
import importlib

import pytest

from conftest import INTERPRETER_VENV


@pytest.fixture
def run(run_cli):
    """prose_owed.main called through run_cli with empty stdin: (code, stdout, stderr)."""
    prose_owed = importlib.import_module("veri.prose_owed")
    return lambda *argv, env=None: run_cli(prose_owed, list(argv), env=env)


def test_a_tree_where_no_unit_has_a_requirements_list_prints_nothing_and_exits_0(run, tmp_path):
    (tmp_path / "skills" / "demo").mkdir(parents=True)
    (tmp_path / "skills" / "demo" / "SKILL.md").write_text("Some prose with no list.\n")

    code, out, err = run(str(tmp_path))

    assert (code, out) == (0, "")


def test_a_unit_with_a_requirements_list_and_no_graded_line_is_printed_and_the_exit_is_1(run, tmp_path):
    (tmp_path / "skills" / "demo").mkdir(parents=True)
    (tmp_path / "skills" / "demo" / "SKILL.md").write_text("The widget is blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## skills/demo/SKILL.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n")

    code, out, err = run(str(tmp_path))

    assert (code, out.split()) == (1, ["skills/demo/SKILL.md"]), err


def test_a_unit_whose_signature_differs_from_its_graded_line_is_printed_and_one_that_matches_is_not(run, tmp_path, monkeypatch):
    from veri import grade_prose

    requirements = "".join(
        "## skills/%s/SKILL.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n\n" % name
        for name in ("fresh", "stale"))
    (tmp_path / "REQUIREMENTS.md").write_text(requirements)
    for name in ("fresh", "stale"):
        (tmp_path / "skills" / name).mkdir(parents=True)
        (tmp_path / "skills" / name / "SKILL.md").write_text("The widget is blue.\n")
    monkeypatch.chdir(tmp_path)
    fresh = grade_prose.signature("REQUIREMENTS.md", "skills/fresh/SKILL.md")
    (tmp_path / "skills" / "fresh" / "GRADED").write_text("skills/fresh/SKILL.md %s 2026-01-01 g1\n" % fresh)
    (tmp_path / "skills" / "stale" / "GRADED").write_text("skills/stale/SKILL.md %s 2026-01-01 g2\n" % ("0" * 64))

    code, out, err = run(str(tmp_path))

    assert (code, out.split()) == (1, ["skills/stale/SKILL.md"]), err


def test_a_graded_line_whose_unit_no_longer_exists_is_printed_as_an_orphan_and_the_exit_is_1(run, tmp_path, monkeypatch):
    from veri import grade_prose

    (tmp_path / "skills" / "demo").mkdir(parents=True)
    (tmp_path / "skills" / "demo" / "SKILL.md").write_text("The widget is blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## skills/demo/SKILL.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n")
    monkeypatch.chdir(tmp_path)
    kept = grade_prose.signature("REQUIREMENTS.md", "skills/demo/SKILL.md")
    (tmp_path / "skills" / "demo" / "GRADED").write_text(
        "skills/demo/SKILL.md %s 2026-01-01 g1\nskills/demo/gone.md %s 2026-01-01 g2\n" % (kept, kept))

    code, out, err = run(str(tmp_path))

    lines = out.splitlines()
    assert (code, len(lines)) == (1, 1), err
    assert "skills/demo/gone.md" in lines[0] and "orphan" in lines[0]


def test_a_unit_named_in_the_requirements_file_with_no_list_and_no_graded_line_is_never_printed(run, tmp_path):
    (tmp_path / "skills" / "bare").mkdir(parents=True)
    (tmp_path / "skills" / "bare" / "SKILL.md").write_text("The widget is blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text("## skills/bare/SKILL.md\n\nNo list here yet.\n")

    code, out, err = run(str(tmp_path))

    assert (code, out) == (0, ""), err


def test_a_repo_root_that_does_not_exist_is_refused_with_exit_2_and_a_one_line_prose_owed_sh_message(run, tmp_path):
    code, out, err = run(str(tmp_path / "gone"), env={"HOME": str(tmp_path), "VERI_VENV": INTERPRETER_VENV})

    assert (code, err.startswith("prose-owed.sh: FileNotFoundError: "), err.count("\n")) == (2, True, 1), err
