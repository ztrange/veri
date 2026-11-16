"""The grader's effort, set by an `effort=` line in grader.conf (PRD 024.10)."""
import importlib

import pytest


@pytest.fixture
def grade_prose():
    return importlib.import_module("veri.grade_prose")


def conf(tmp_path, monkeypatch, grade_prose, text):
    scripts = tmp_path / "skills" / "tdd" / "scripts"
    scripts.mkdir(parents=True, exist_ok=True)
    (tmp_path / "skills" / "tdd" / "grader.conf").write_text(text)
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(scripts))


def test_the_grader_model_is_the_model_lines_value_whether_an_effort_line_sits_above_or_below_it(
        tmp_path, monkeypatch, grade_prose):
    models = []
    for text in ("# c\neffort=low\nmodel=claude-x-4\n", "model=claude-x-4\neffort=low\n"):
        conf(tmp_path, monkeypatch, grade_prose, text)
        models.append(grade_prose.grader_model())

    assert models == ["claude-x-4", "claude-x-4"]
