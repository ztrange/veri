"""In-process cases for veri/grade_prose.py, the module grade-prose.sh is a shim over."""
import importlib
import subprocess

import pytest


@pytest.fixture
def grade_prose():
    return importlib.import_module("veri.grade_prose")


def test_a_grader_conf_model_value_that_names_no_version_makes_grade_prose_exit_2_before_anything_is_launched(
        tmp_path, monkeypatch, run_cli, grade_prose):
    (tmp_path / "skills" / "tdd" / "scripts").mkdir(parents=True)
    (tmp_path / "skills" / "tdd" / "grader.conf").write_text("model=sonnet\n")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n")
    launched = []
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    monkeypatch.setattr(subprocess, "run", lambda argv, *a, **k: launched.append(argv)
                        or subprocess.CompletedProcess(argv, 0, b"", b""))

    code, out, err = run_cli(grade_prose, ["REQUIREMENTS.md", "unit.md"], cwd=tmp_path)

    assert (code, launched) == (2, []), (code, launched, err)
